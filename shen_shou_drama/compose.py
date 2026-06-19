#!/usr/bin/env python3
"""
中国神兽水墨风视频后期合成脚本
- 拼接 8 个视频片段(concat demuxer,保持原时长)
- 对齐 8 段配音到每段 5.875s(短了补静音,长了切)
- 混合视频 + 配音 + BGM
- 加 13s 黑场补到 60s
- 烧录 ASS 字幕
"""
import os
import subprocess
import json

# 用 ffmpeg-full(带 libass,ass filter 正常工作)
FFMPEG = "/opt/homebrew/Cellar/ffmpeg-full/8.1.1/bin/ffmpeg"
FFPROBE = "/opt/homebrew/Cellar/ffmpeg-full/8.1.1/bin/ffprobe"

BASE = "/Users/Zhuanz/Documents/Minimax Code Projects/Minimax Video Master/shen_shou_drama/output"
CLIPS = f"{BASE}/clips"
AUDIO = f"{BASE}/audio"
MUSIC = f"{BASE}/music"
FINAL = f"{BASE}/final"
SUBS = f"{BASE}/subtitles"

CLIP_DURATION = 5.875  # matrix 视频固定 5.875s
NUM_CLIPS = 8
TARGET_TOTAL = 60.0
BGM_VOLUME = 0.25  # BGM 音量,0.25 不压过旁白

# 时间轴 (start, end) for each clip
def clip_start(i):
    return i * CLIP_DURATION

def clip_end(i):
    return (i + 1) * CLIP_DURATION

# 字幕定义 - 短句,1-2 行
# 每个字幕时间窗从 clip 中部开始,持续 ~4s,避开段边界
SUBTITLES = [
    # (start, end, text)
    (0.5, 5.5, "天地玄黄\\N宇宙洪荒"),
    (6.4, 11.0, "青龙镇东\\N应春属木"),
    (12.3, 17.0, "白虎在西\\N应秋属金"),
    (18.2, 23.0, "朱雀翔南\\N应夏属火"),
    (24.1, 29.0, "玄武镇北\\N应冬属水"),
    (30.0, 35.0, "麒麟居中\\N德瑞呈祥"),
    (36.0, 40.5, "金木水火土\\N五行相生"),
    (42.0, 46.5, "万古流芳"),
    (49.0, 58.5, "中国神兽\\N镇守四方"),
]


def make_ass_subtitle():
    """生成 ASS 字幕文件(STKaiti 楷体,水墨风)"""
    os.makedirs(SUBS, exist_ok=True)
    ass_path = f"{SUBS}/subtitles.ass"

    # ASS 头部 - STKaiti 楷体,白色,大号
    ass = """[Script Info]
Title: ShenShou Ink Style
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,STKaiti,68,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,3,2,80,80,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def to_ass_time(t):
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = t % 60
        cs = int((s - int(s)) * 100)
        return f"{h:d}:{m:02d}:{int(s):02d}.{cs:02d}"

    for start, end, text in SUBTITLES:
        line = f"Dialogue: 0,{to_ass_time(start)},{to_ass_time(end)},Default,,0,0,0,,{text}"
        ass += line + "\n"

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass)
    print(f"[OK] ASS subtitle: {ass_path}")
    return ass_path


def pad_voice():
    """给每段 voice padding 到 5.875s,生成 padded_voice_XX.mp3"""
    for i in range(1, NUM_CLIPS + 1):
        src = f"{AUDIO}/voice_{i:02d}.mp3"
        dst = f"{AUDIO}/padded_voice_{i:02d}.mp3"
        # 用 ffmpeg 强制 5.875s: 不够补静音, 多了切到 5.875s
        cmd = [
            FFMPEG, "-y", "-i", src,
            "-af", f"apad=pad_dur=10,atrim=0:{CLIP_DURATION},asetpts=PTS-STARTPTS",
            "-ar", "44100", "-ac", "2", "-c:a", "libmp3lame", "-b:a", "192k",
            dst
        ]
        subprocess.run(cmd, capture_output=True, check=False)
        # 验证时长
        out = subprocess.run(
            [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst],
            capture_output=True, text=True
        )
        print(f"[OK] padded_voice_{i:02d}.mp3: {out.stdout.strip()}s")


def concat_videos():
    """用 concat demuxer 拼接 8 个 clip(保持原时长不重编码)"""
    filelist = f"{BASE}/video_filelist.txt"
    with open(filelist, "w") as f:
        for i in range(1, NUM_CLIPS + 1):
            f.write(f"file 'clips/clip_{i:02d}_*.mp4'\n")
    # 实际匹配文件名
    import glob
    with open(filelist, "w") as f:
        for i in range(1, NUM_CLIPS + 1):
            matches = glob.glob(f"{CLIPS}/clip_{i:02d}_*.mp4")
            if matches:
                fname = os.path.basename(matches[0])
                f.write(f"file 'clips/{fname}'\n")

    out = f"{BASE}/concatenated.mp4"
    cmd = [
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", filelist,
        "-c", "copy",
        out
    ]
    subprocess.run(cmd, capture_output=True, check=False)
    out_dur = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
        capture_output=True, text=True
    )
    print(f"[OK] concatenated.mp4: {out_dur.stdout.strip()}s")
    return out


def concat_voices():
    """拼接 8 段 padded voice"""
    filelist = f"{BASE}/voice_filelist.txt"
    with open(filelist, "w") as f:
        for i in range(1, NUM_CLIPS + 1):
            f.write(f"file 'audio/padded_voice_{i:02d}.mp3'\n")

    out = f"{BASE}/voiceover.mp3"
    cmd = [
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", filelist,
        "-c", "copy",
        out
    ]
    subprocess.run(cmd, capture_output=True, check=False)
    out_dur = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
        capture_output=True, text=True
    )
    print(f"[OK] voiceover.mp3: {out_dur.stdout.strip()}s")
    return out


def compose_final(voiceover, ass_path):
    """合成最终视频: 视频+配音+BGM+字幕+黑场补到 60s"""
    bgm = f"{MUSIC}/bgm.mp3"
    # 输出文件
    out_raw = f"{FINAL}/final_raw.mp4"

    # 步骤 1: 拼接 BGM(循环)到 60s,然后混合配音
    # 用 filter_complex: [1:a] = voiceover, [0:a] = BGM
    # voiceover 时长 47s, BGM loop 到 60s
    # final duration 60s(用 -t 60)

    # 用 concat filter 把视频和 13s 黑场合成 60s 视频
    # 然后混合配音和 BGM,烧录字幕
    black = f"{BASE}/black_13s.mp4"
    # 生成 13s 黑场
    cmd_black = [
        FFMPEG, "-y", "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=13:r=24",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        black
    ]
    subprocess.run(cmd_black, capture_output=True, check=False)
    print(f"[OK] black_13s.mp4 created")

    # 用 concat demuxer 拼接视频+黑场
    final_filelist = f"{BASE}/final_filelist.txt"
    with open(final_filelist, "w") as f:
        f.write(f"file 'concatenated.mp4'\n")
        f.write(f"file 'black_13s.mp4'\n")
    video_60 = f"{BASE}/video_60s.mp4"
    cmd_concat = [
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", final_filelist,
        "-c", "copy",
        "-t", str(TARGET_TOTAL),
        video_60
    ]
    subprocess.run(cmd_concat, capture_output=True, check=False)
    out_dur = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video_60],
        capture_output=True, text=True
    )
    print(f"[OK] video_60s.mp4: {out_dur.stdout.strip()}s")

    # 步骤 2: 把 voiceover 拼接到 60s(末尾加静音)
    voiceover_60 = f"{BASE}/voiceover_60s.mp3"
    cmd_voice = [
        FFMPEG, "-y", "-i", voiceover,
        "-af", f"apad=pad_dur=20,atrim=0:{TARGET_TOTAL},asetpts=PTS-STARTPTS",
        "-ar", "44100", "-ac", "2", "-c:a", "libmp3lame", "-b:a", "192k",
        voiceover_60
    ]
    subprocess.run(cmd_voice, capture_output=True, check=False)
    print(f"[OK] voiceover_60s.mp3 created")

    # 步骤 3: BGM 循环到 60s
    bgm_60 = f"{BASE}/bgm_60s.mp3"
    cmd_bgm = [
        FFMPEG, "-y", "-stream_loop", "-1", "-i", bgm,
        "-t", str(TARGET_TOTAL),
        "-af", f"volume={BGM_VOLUME},afade=t=in:st=0:d=1,afade=t=out:st={TARGET_TOTAL-2}:d=2",
        "-ar", "44100", "-ac", "2", "-c:a", "libmp3lame", "-b:a", "192k",
        bgm_60
    ]
    subprocess.run(cmd_bgm, capture_output=True, check=False)
    print(f"[OK] bgm_60s.mp3 created")

    # 步骤 4: 混合 voiceover + BGM,烧字幕,输出最终
    final = f"{FINAL}/shenshou_ink_60s.mp4"
    # 关键:ffmpeg 8.x 解析 ass filter 有 bug,改用 filter_complex 形式
    import shutil
    short_ass = f"{BASE}/subs.ass"
    shutil.copy(ass_path, short_ass)
    cmd_final = [
        FFMPEG, "-y",
        "-i", video_60,
        "-i", voiceover_60,
        "-i", bgm_60,
        "-filter_complex",
        f"[0:v]ass=subs.ass[v];[1:a][2:a]amix=inputs=2:duration=first:dropout_transition=0[aout]",
        "-map", "[v]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-t", str(TARGET_TOTAL),
        final
    ]
    res = subprocess.run(cmd_final, capture_output=True, text=True, cwd=BASE)
    if res.returncode != 0:
        print(f"[ERROR] final composition failed:")
        print(res.stderr[-2000:])
    else:
        out_dur = subprocess.run(
            [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", final],
            capture_output=True, text=True
        )
        print(f"[OK] FINAL: {final}, {out_dur.stdout.strip()}s")

    return final


if __name__ == "__main__":
    os.makedirs(FINAL, exist_ok=True)
    print("=== Step 1: Make ASS subtitle ===")
    ass = make_ass_subtitle()

    print("=== Step 2: Pad voices to 5.875s ===")
    pad_voice()

    print("=== Step 3: Concat videos ===")
    concat_videos()

    print("=== Step 4: Concat voices ===")
    voiceover = concat_voices()

    print("=== Step 5: Compose final video ===")
    compose_final(voiceover, ass)

    print("\n=== DONE ===")
