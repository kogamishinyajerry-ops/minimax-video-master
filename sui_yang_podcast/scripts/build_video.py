#!/usr/bin/env python3
"""
Build the Sui Yang podcast video.

Pipeline:
  1) Concat the 7 TTS mp3s with 3s opening silence + 2s tail silence -> tts_full.mp3
  2) Concat the 6 image blocks (cover 3s + 5 配图s with their segment durations)
     into a slideshow video (no audio) using ffmpeg concat demuxer -> slides.mp4
  3) One-pass final render: mix TTS audio + looped BGM, burn ASS subs onto the
     slideshow video -> final.mp4
"""
import subprocess
import json
from pathlib import Path

PROJ = Path("/Users/Zhuanz/Documents/Minimax Code Projects/Minimax Video Master/sui_yang_podcast")
FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"

# (image path, duration_sec)
# 3s opening cover (with title text overlay from ASS layer 1)
# then 5 image blocks covering 7 TTS segments
# 配图① covers segment 1+2 (Hook+transition)
# 配图⑤ covers segment 6+7 (历史叙事+CTA)
SLIDES = [
    (PROJ / "images" / "01_cover.png", 3.0),
    (PROJ / "images" / "02_pic1_canal_ancient.png", 24.624 + 22.932),
    (PROJ / "images" / "03_pic2_canal_map.png", 47.916),
    (PROJ / "images" / "04_pic3_gongyuan.png", 51.732),
    (PROJ / "images" / "05_pic4_uprising.png", 54.900),
    (PROJ / "images" / "06_pic5_yangguang_portrait.png", 52.200 + 22.284),
]
TTS_FILES = [
    PROJ / "audio" / f"tts_0{i}.mp3" for i in range(1, 8)
]
BGM = PROJ / "bgm" / "bgm_main.mp3"
ASS = PROJ / "subtitles" / "script.ass"
OUT_FINAL = PROJ / "output" / "sui_yang_podcast_final.mp4"
SLIDES_MP4 = PROJ / "output" / "_slides_raw.mp4"
TTS_FULL = PROJ / "output" / "_tts_full.mp3"

OPEN_SILENCE = 3.0  # matches the 3s cover
TAIL_SILENCE = 2.0  # after the last TTS, fade-out grace period

VIDEO_W, VIDEO_H = 1920, 1080
FPS = 30


def run(cmd, **kw):
    print(f"$ {' '.join(str(x) for x in cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("STDOUT:", r.stdout)
        print("STDERR:", r.stderr)
        raise SystemExit(f"Command failed: {r.returncode}")
    return r


def build_tts_full():
    """Concat 7 TTS files with opening and tail silence."""
    inputs = []
    filt_parts = []
    idx = 0
    # 3s opening silence
    inputs += ["-f", "lavfi", "-t", str(OPEN_SILENCE), "-i", "anullsrc=r=44100:cl=stereo"]
    filt_parts.append(f"[{idx}:a]")
    idx += 1
    # 7 TTS segments
    tts_indices = []
    for f in TTS_FILES:
        inputs += ["-i", str(f)]
        filt_parts.append(f"[{idx}:a]")
        tts_indices.append(idx)
        idx += 1
    # 2s tail silence
    inputs += ["-f", "lavfi", "-t", str(TAIL_SILENCE), "-i", "anullsrc=r=44100:cl=stereo"]
    filt_parts.append(f"[{idx}:a]")
    idx += 1

    concat_filter = "".join(filt_parts) + f"concat=n={len(filt_parts)}:v=0:a=1[out]"
    cmd = [FFMPEG, "-y", *inputs,
           "-filter_complex", concat_filter,
           "-map", "[out]",
           "-c:a", "libmp3lame", "-b:a", "192k",
           str(TTS_FULL)]
    run(cmd)
    # probe
    r = run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(TTS_FULL)])
    print(f"tts_full duration: {r.stdout.strip()}s")


def build_slides():
    """Build a 1920x1080 30fps slideshow mp4 with hard cuts (no audio)."""
    list_file = PROJ / "scripts" / "_slide_filelist.txt"
    lines = []
    total_dur = 0
    for img, dur in SLIDES:
        lines.append(f"file '{img}'")
        lines.append(f"duration {dur}")
        total_dur += dur
    # concat demuxer needs the last image repeated without duration to mark end,
    # otherwise ffmpeg will hang/loop. We add a final "file" line.
    lines.append(f"file '{SLIDES[-1][0]}'")
    list_file.write_text("\n".join(lines), encoding="utf-8")

    # total frames = total_dur * FPS
    total_frames = int(total_dur * FPS)
    cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-vf", f"scale={VIDEO_W}:{VIDEO_H}:force_original_aspect_ratio=increase,"
               f"crop={VIDEO_W}:{VIDEO_H},setsar=1,format=yuv420p",
        "-r", str(FPS),
        "-frames:v", str(total_frames),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-an",
        str(SLIDES_MP4),
    ]
    run(cmd)
    r = run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(SLIDES_MP4)])
    print(f"slides duration: {r.stdout.strip()}s ({total_dur:.2f}s expected)")


def build_final():
    """One-pass final: slideshow video + (TTS audio * looped BGM) + ASS subs."""
    cmd = [
        FFMPEG, "-y",
        "-i", str(SLIDES_MP4),
        "-i", str(TTS_FULL),
        "-stream_loop", "-1", "-i", str(BGM),
        "-filter_complex",
            f"[1:a]volume=1.0[tts];"
            f"[2:a]volume=0.18,afade=t=in:st=0:d=2,afade=t=out:st=275:d=3[bgm];"
            f"[tts][bgm]amix=inputs=2:duration=first:dropout_transition=0[mix]",
        "-map", "0:v",
        "-map", "[mix]",
        "-vf", f"ass={ASS}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-movflags", "+faststart",
        str(OUT_FINAL),
    ]
    run(cmd)
    r = run([FFPROBE, "-v", "error", "-show_entries",
             "format=duration:stream=codec_type,codec_name,width,height",
             "-of", "default=noprint_wrappers=1", str(OUT_FINAL)])
    print(f"final video info:\n{r.stdout}")


if __name__ == "__main__":
    OUT_FINAL.parent.mkdir(parents=True, exist_ok=True)
    print("=== Step 1: concat TTS with opening/tail silence ===")
    build_tts_full()
    print("\n=== Step 2: build image slideshow ===")
    build_slides()
    print("\n=== Step 3: final render with audio mix + ASS burn-in ===")
    build_final()
    print(f"\nDONE: {OUT_FINAL}")
