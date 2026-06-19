#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v2 完整合成流水线：
1. 每段 video tpad 到目标时长 + audio apad 到目标时长
2. PIL 在每帧烧字幕
3. concat 所有段
4. 合成 voice + BGM
"""
import os, subprocess, json, math, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/Zhuanz/Documents/Minimax Code Projects/Minimax Video Master/cloisonne_plate")
VIDEOS = ROOT / "output/videos"
AUDIO = ROOT / "output/audio/v2"
BGM_SRC = Path("/Users/Zhuanz/Documents/Minimax Code Projects/Minimax Video Master/cloisonne_ink/output/bgm.mp3")
TEMP = ROOT / "output/temp"
OUT = ROOT / "output"

CLIPS = [
    (1, "在京城的一隅，有一位掐丝珐琅匠人。数十年来，他只做一件事\n——把金丝与釉料，化作凝固的火焰"),
    (2, "一器之始是画稿。今日他要做的，\n是一只圆盘，饰以缠枝莲纹"),
    (3, "继而制胎，以锤击紫铜成器之骨；\n再以极细铜丝弯折成缠枝莲的轮廓，粘于胎上——\n掐丝，是最见功力的工序"),
    (4, "点蓝。将矿物研磨的各色釉料，\n填入铜丝围成的格中。蓝如宝石，绿若翡翠"),
    (5, "入窑烧制。八百度的炉火，\n令釉料与铜丝紧紧相拥。\n这件器物，需七十二道工序，反复入窑，反复点蓝"),
    (6, "出窑后以砂石打磨，令表面平如镜；\n终以镀金，将金液敷于铜丝之上，\n金线夺目，器物方成"),
    (7, "掐丝珐琅，是凝固的火焰，是凝固的时光。\n匠人说：每完成一件器物，便多活了一世"),
]

FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_SIZE = 44
FPS = 24
FADE_IN = 0.3
FADE_OUT = 0.3

def run(cmd, **kw):
    print(">>>", " ".join(str(c) for c in cmd[:6]), "...")
    return subprocess.run(cmd, check=True, capture_output=True, **kw)

def get_duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ]).decode().strip()
    return float(out)

def pad_video(src, dst, target_dur):
    """tpad 重复末帧延长 video 到 target_dur"""
    cur = get_duration(src)
    pad = max(0, target_dur - cur)
    if pad < 0.01:
        shutil.copy2(src, dst)
        return
    run([
        "ffmpeg", "-y", "-i", str(src),
        "-vf", f"tpad=stop_mode=clone:stop_duration={pad:.3f}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        str(dst)
    ])

def pad_audio(src, dst, target_dur):
    """apad 静音延长 audio 到 target_dur"""
    cur = get_duration(src)
    pad = target_dur - cur
    if pad > 0.05:
        run([
            "ffmpeg", "-y", "-i", str(src),
            "-af", f"apad=pad_dur={pad:.3f}",
            "-ar", "44100",
            "-c:a", "pcm_s16le",
            str(dst)
        ])
    elif pad < -0.05:
        run([
            "ffmpeg", "-y", "-i", str(src),
            "-t", f"{target_dur:.3f}",
            "-ar", "44100",
            "-c:a", "pcm_s16le",
            str(dst)
        ])
    else:
        run([
            "ffmpeg", "-y", "-i", str(src),
            "-ar", "44100",
            "-c:a", "pcm_s16le",
            str(dst)
        ])

def burn_subtitle(scene_id, video_in, subtitle, dst):
    """提取帧 → PIL烧字幕 → 重新编码"""
    frames_dir = TEMP / f"frames_s{scene_id:02d}"
    frames_dir.mkdir(exist_ok=True)
    for f in frames_dir.glob("*.png"):
        f.unlink()
    
    run([
        "ffmpeg", "-y", "-i", str(video_in),
        "-vf", f"fps={FPS}",
        str(frames_dir / "frame_%05d.png")
    ])
    
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    frame_files = sorted(frames_dir.glob("*.png"))
    total = len(frame_files)
    fade_in_f = int(FADE_IN * FPS)
    fade_out_f = int(FADE_OUT * FPS)
    
    lines = subtitle.split("\n")
    line_h = FONT_SIZE + 12
    
    for fi, ff in enumerate(frame_files):
        img = Image.open(ff).convert("RGBA")
        W, H = img.size
        
        # alpha 因子
        if fi < fade_in_f:
            af = fi / max(1, fade_in_f)
        elif fi > total - fade_out_f:
            af = max(0, (total - fi) / max(1, fade_out_f))
        else:
            af = 1.0
        
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        total_text_h = line_h * len(lines)
        y_start = H - 80 - total_text_h
        
        for li, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = (W - tw) // 2
            y = y_start + li * line_h
            
            # 描边（圆形）
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    if dx*dx + dy*dy <= 9:
                        draw.text((x+dx, y+dy), line, font=font, fill=(0, 0, 0, int(220 * af)))
            
            # 白色文字
            draw.text((x, y), line, font=font, fill=(255, 255, 255, int(255 * af)))
        
        # 半透明黑色背景条（增强可读性）
        bg_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bg_draw = ImageDraw.Draw(bg_overlay)
        bg_y = y_start - 8
        bg_h = total_text_h + 16
        # 渐变黑底（中央更黑）
        for i in range(bg_h):
            alpha = int(120 * af * (1 - abs(i - bg_h/2) / (bg_h/2)))
            bg_draw.line([(0, bg_y+i), (W, bg_y+i)], fill=(0, 0, 0, alpha))
        img = Image.alpha_composite(img, bg_overlay)
        
        # 叠加字幕
        img = Image.alpha_composite(img, overlay)
        img.convert("RGB").save(ff, optimize=True)
    
    # 编码
    run([
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%05d.png"),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        str(dst)
    ])

def process_scene(scene_id, subtitle, force=False):
    video_in = VIDEOS / f"scene_0{scene_id}.mp4"
    voice_in = AUDIO / f"voice_0{scene_id}.mp3"
    
    clip_out = TEMP / f"clip_0{scene_id}.mp4"
    if clip_out.exists() and not force:
        d = get_duration(clip_out)
        print(f"\n=== S{scene_id}: SKIP (exists, {d:.3f}s) ===")
        return clip_out
    
    v_dur = get_duration(video_in)
    a_dur = get_duration(voice_in)
    target = max(v_dur, a_dur) + 0.5
    
    print(f"\n=== S{scene_id}: video={v_dur:.3f}s voice={a_dur:.3f}s target={target:.3f}s ===")
    
    video_long = TEMP / f"scene_0{scene_id}_long.mp4"
    voice_long = TEMP / f"voice_0{scene_id}_long.wav"
    video_sub = TEMP / f"scene_0{scene_id}_sub.mp4"
    
    pad_video(video_in, video_long, target)
    pad_audio(voice_in, voice_long, target)
    burn_subtitle(scene_id, video_long, subtitle, video_sub)
    
    # 合并烧字幕视频 + 长音频
    run([
        "ffmpeg", "-y",
        "-i", str(video_sub),
        "-i", str(voice_long),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "128k",
        "-ar", "44100",
        "-shortest",
        str(clip_out)
    ])
    
    final_dur = get_duration(clip_out)
    print(f"S{scene_id} -> {clip_out.name} (final {final_dur:.3f}s)")
    return clip_out

def main():
    TEMP.mkdir(parents=True, exist_ok=True)
    clips = []
    for sid, sub in CLIPS:
        clips.append(process_scene(sid, sub))
    
    # concat 所有段
    filelist = TEMP / "filelist.txt"
    with open(filelist, "w") as f:
        for c in clips:
            f.write(f"file '{c.absolute()}'\n")
    
    concat_out = TEMP / "concat.mp4"
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(filelist),
        "-c", "copy",
        str(concat_out)
    ])
    
    # 加 BGM（loop 到视频长 + 音量降到 0.2）
    total_dur = get_duration(concat_out)
    print(f"\nConcat total: {total_dur:.3f}s")
    
    # BGM 处理：loop 到 total_dur，音量 0.20
    bgm_loop = TEMP / "bgm_looped.wav"
    bgm_dur = get_duration(BGM_SRC)
    loops = math.ceil(total_dur / bgm_dur)
    run([
        "ffmpeg", "-y", "-i", str(BGM_SRC),
        "-filter_complex", f"[0:a]aloop=loop={loops-1}:size=1e9,atrim=0:{total_dur:.3f},volume=0.20[bgm]",
        "-map", "[bgm]",
        "-ar", "44100",
        "-c:a", "pcm_s16le",
        str(bgm_loop)
    ])
    
    # 混合 voice (concat.mp4) + bgm
    final = OUT / "cloisonne_plate_final.mp4"
    run([
        "ffmpeg", "-y",
        "-i", str(concat_out),
        "-i", str(bgm_loop),
        "-filter_complex", "[1:a]volume=0.20[bgm];[0:a][bgm]amix=inputs=2:duration=shortest:dropout_transition=0[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-ar", "44100",
        "-shortest",
        str(final)
    ])
    
    final_dur = get_duration(final)
    print(f"\n*** FINAL OUTPUT: {final} ({final_dur:.3f}s) ***")

if __name__ == "__main__":
    main()