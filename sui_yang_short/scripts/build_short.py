#!/usr/bin/env python3
"""
Build the 90s vertical Sui Yang short.

Pipeline:
  1) Concat 6 TTS mp3s with proper inter-segment silence -> tts_full.mp3
  2) Concat 6 image blocks (image 06 covers the tail) into a vertical
     slideshow (1080x1920, 30fps) using ffmpeg concat demuxer -> slides.mp4
  3) One-pass final: mix TTS + looped BGM, burn ASS subs onto slideshow
"""
import subprocess
from pathlib import Path

PROJ = Path("/Users/Zhuanz/Documents/Minimax Code Projects/Minimax Video Master/sui_yang_short")
FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"

# Timeline (cumulative t in seconds, image name, duration_sec):
#   0.00-8.07   01_cover          8.07  (head 3s silent + tts_01 5.07s)
#   8.07-19.64  02_canal         11.57  (interlude 4.43s + tts_02 7.14s)
#  19.64-31.51  03_keju          11.87  (interlude 4.36s + tts_03 7.51s)
#  31.51-44.86  04_uprising      13.35  (interlude 4.49s + tts_04 8.86s)
#  44.86-56.40  05_tang_scribe   11.54  (interlude 4.14s + tts_05 7.40s)
#  56.40-90.00  06_yangguang     33.60  (interlude 4.60s + tts_06 7.88s + tail 21.12s)
SLIDES = [
    (PROJ / "images" / "01_cover.png",        8.07),
    (PROJ / "images" / "02_canal.png",       11.57),
    (PROJ / "images" / "03_keju.png",        11.87),
    (PROJ / "images" / "04_uprising.png",    13.35),
    (PROJ / "images" / "05_tang_scribe.png", 11.54),
    (PROJ / "images" / "06_yangguang.png",   33.60),
]

TTS_FILES = [PROJ / "audio" / f"tts_0{i}.mp3" for i in range(1, 7)]
BGM = PROJ / "bgm" / "bgm_short.mp3"
ASS = PROJ / "subtitles" / "script.ass"

OUT_FINAL = PROJ / "output" / "sui_yang_short_final.mp4"
SLIDES_MP4 = PROJ / "output" / "_slides_raw.mp4"
TTS_FULL = PROJ / "output" / "_tts_full.mp3"

# TTS segment start times (must match build_subtitles.py SEGMENTS)
TTS_START_TIMES = [3.00, 12.50, 24.00, 36.00, 49.00, 61.00]
# TTS segment durations
TTS_DURATIONS = [5.07, 7.14, 7.51, 8.86, 7.40, 7.88]
# Head silence and tail silence
HEAD_SILENCE = 3.0
TAIL_SILENCE = 21.12  # 90 - 68.88

VIDEO_W, VIDEO_H = 1080, 1920
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
    """Concat 6 TTS files with proper inter-segment silence + head/tail silence."""
    inputs = []
    filt_parts = []
    idx = 0
    # Head silence (3s)
    inputs += ["-f", "lavfi", "-t", str(HEAD_SILENCE), "-i", "anullsrc=r=44100:cl=stereo"]
    filt_parts.append(f"[{idx}:a]")
    idx += 1
    # 6 TTS segments with silence between
    for i, f in enumerate(TTS_FILES):
        inputs += ["-i", str(f)]
        filt_parts.append(f"[{idx}:a]")
        idx += 1
        # Add silence after this segment if it's not the last
        if i < len(TTS_FILES) - 1:
            gap = TTS_START_TIMES[i + 1] - TTS_START_TIMES[i] - TTS_DURATIONS[i]
            if gap > 0:
                inputs += ["-f", "lavfi", "-t", f"{gap:.3f}", "-i", "anullsrc=r=44100:cl=stereo"]
                filt_parts.append(f"[{idx}:a]")
                idx += 1
    # Tail silence
    inputs += ["-f", "lavfi", "-t", f"{TAIL_SILENCE:.3f}", "-i", "anullsrc=r=44100:cl=stereo"]
    filt_parts.append(f"[{idx}:a]")
    idx += 1

    concat_filter = "".join(filt_parts) + f"concat=n={len(filt_parts)}:v=0:a=1[out]"
    cmd = [FFMPEG, "-y", *inputs,
           "-filter_complex", concat_filter,
           "-map", "[out]",
           "-c:a", "libmp3lame", "-b:a", "192k",
           str(TTS_FULL)]
    run(cmd)
    r = run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(TTS_FULL)])
    print(f"tts_full duration: {r.stdout.strip()}s")


def build_slides():
    """Build a 1080x1920 30fps vertical slideshow mp4 with hard cuts (no audio)."""
    list_file = PROJ / "scripts" / "_slide_filelist.txt"
    lines = []
    total_dur = 0
    for img, dur in SLIDES:
        lines.append(f"file '{img}'")
        lines.append(f"duration {dur}")
        total_dur += dur
    # concat demuxer quirk: last file must be repeated
    lines.append(f"file '{SLIDES[-1][0]}'")
    list_file.write_text("\n".join(lines), encoding="utf-8")

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
    total = HEAD_SILENCE + sum(TTS_DURATIONS) + TAIL_SILENCE
    # also include inter-segment gaps
    gaps = sum(TTS_START_TIMES[i + 1] - TTS_START_TIMES[i] - TTS_DURATIONS[i]
               for i in range(len(TTS_DURATIONS) - 1))
    total = HEAD_SILENCE + sum(TTS_DURATIONS) + gaps + TAIL_SILENCE
    # fade out at total - 2s
    fade_out_start = total - 2.0

    cmd = [
        FFMPEG, "-y",
        "-i", str(SLIDES_MP4),
        "-i", str(TTS_FULL),
        "-stream_loop", "-1", "-i", str(BGM),
        "-filter_complex",
            f"[1:a]volume=1.0[tts];"
            f"[2:a]volume=0.20,afade=t=in:st=0:d=1.5,afade=t=out:st={fade_out_start:.2f}:d=2.0[bgm];"
            f"[tts][bgm]amix=inputs=2:duration=first:dropout_transition=0[mix]",
        "-map", "0:v",
        "-map", "[mix]",
        "-vf", f"ass={ASS}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-t", f"{total:.3f}",
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
    print("=== Step 1: concat TTS with proper timing ===")
    build_tts_full()
    print("\n=== Step 2: build vertical 1080x1920 slideshow ===")
    build_slides()
    print("\n=== Step 3: final render with audio mix + ASS burn-in ===")
    build_final()
    print(f"\nDONE: {OUT_FINAL}")
