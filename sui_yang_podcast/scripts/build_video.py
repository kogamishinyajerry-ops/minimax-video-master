#!/usr/bin/env python3
"""
Build the Sui Yang podcast video.

Pipeline:
  1) Concat the 7 TTS mp3s with 3s opening silence + 2s tail silence -> tts_full.mp3
  2) Concat the 6 image blocks (cover 3s + 5 配图s with their segment durations)
     into a slideshow video (no audio) using ffmpeg concat demuxer -> slides.mp4
  3) One-pass final render: mix TTS audio + looped BGM, burn ASS subs onto the
     slideshow video -> final.mp4

Durations are computed dynamically via ffprobe — no hardcoded TTS lengths.
Only the image→TTS-segment mapping is hardcoded (which配图 covers which segments).
"""
import subprocess
from pathlib import Path

PROJ = Path("/Users/Zhuanz/Documents/Minimax Code Projects/Minimax Video Master/sui_yang_podcast")
FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"

# --- Config: image→TTS-segment mapping (business logic, not magic numbers) ---
# Each slide is (image file, list of TTS segment indices it covers).
# - Cover image gets a fixed 3s intro (no TTS).
# - 配图① covers TTS segments [1, 2] (Hook + transition).
# - 配图⑤ covers TTS segments [6, 7] (历史叙事 + CTA).
# - Other 配图s cover exactly one TTS segment each.
# Duration for each slide = sum of its TTS segments' actual ffprobe durations.
COVER_DURATION = 3.0  # opening cover, matches ASS layer 1 title window
SLIDES_SPEC = [
    ("01_cover.png",                    None),        # fixed COVER_DURATION
    ("02_pic1_canal_ancient.png",       [1, 2]),
    ("03_pic2_canal_map.png",           [3]),
    ("04_pic3_gongyuan.png",            [4]),
    ("05_pic4_uprising.png",            [5]),
    ("06_pic5_yangguang_portrait.png",  [6, 7]),
]
TTS_COUNT = 7  # tts_01.mp3 .. tts_07.mp3

BGM = PROJ / "bgm" / "bgm_main.mp3"
ASS = PROJ / "subtitles" / "script.ass"
OUT_FINAL = PROJ / "output" / "sui_yang_podcast_final.mp4"
SLIDES_MP4 = PROJ / "output" / "_slides_raw.mp4"
TTS_FULL = PROJ / "output" / "_tts_full.mp3"

OPEN_SILENCE = 3.0  # matches the cover window
TAIL_SILENCE = 2.0  # after the last TTS, fade-out grace period
BGM_FADE_OUT_BEFORE_END = 3.0  # BGM fades out in the last N seconds

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


def probe_duration(path: Path) -> float:
    """Return media duration in seconds (float)."""
    r = run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)])
    return float(r.stdout.strip())


def tts_path(i: int) -> Path:
    return PROJ / "audio" / f"tts_{i:02d}.mp3"


def build_tts_full(tts_durations: list[float]) -> float:
    """Concat TTS files with opening/tail silence. Returns total duration."""
    inputs = []
    filt_parts = []
    idx = 0
    # opening silence
    inputs += ["-f", "lavfi", "-t", str(OPEN_SILENCE), "-i", "anullsrc=r=44100:cl=stereo"]
    filt_parts.append(f"[{idx}:a]")
    idx += 1
    # TTS segments
    for i in range(1, TTS_COUNT + 1):
        inputs += ["-i", str(tts_path(i))]
        filt_parts.append(f"[{idx}:a]")
        idx += 1
    # tail silence
    inputs += ["-f", "lavfi", "-t", str(TAIL_SILENCE), "-i", "anullsrc=r=44100:cl=stereo"]
    filt_parts.append(f"[{idx}:a]")

    concat_filter = "".join(filt_parts) + f"concat=n={len(filt_parts)}:v=0:a=1[out]"
    cmd = [FFMPEG, "-y", *inputs,
           "-filter_complex", concat_filter,
           "-map", "[out]",
           "-c:a", "libmp3lame", "-b:a", "192k",
           str(TTS_FULL)]
    run(cmd)
    total = probe_duration(TTS_FULL)
    expected = OPEN_SILENCE + sum(tts_durations) + TAIL_SILENCE
    print(f"tts_full duration: {total:.3f}s ({expected:.3f}s expected)")
    return total


def build_slides(slides: list[tuple[Path, float]]) -> float:
    """Build a 1920x1080 30fps slideshow mp4 with hard cuts (no audio)."""
    list_file = PROJ / "scripts" / "_slide_filelist.txt"
    lines = []
    total_dur = 0.0
    for img, dur in slides:
        lines.append(f"file '{img}'")
        lines.append(f"duration {dur}")
        total_dur += dur
    # concat demuxer needs the last image repeated without duration to mark end
    lines.append(f"file '{slides[-1][0]}'")
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
    actual = probe_duration(SLIDES_MP4)
    print(f"slides duration: {actual:.3f}s ({total_dur:.2f}s expected)")
    return actual


def build_final(total_video_dur: float):
    """One-pass final: slideshow video + (TTS audio * looped BGM) + ASS subs."""
    bgm_fade_out_start = max(0.0, total_video_dur - BGM_FADE_OUT_BEFORE_END)
    cmd = [
        FFMPEG, "-y",
        "-i", str(SLIDES_MP4),
        "-i", str(TTS_FULL),
        "-stream_loop", "-1", "-i", str(BGM),
        "-filter_complex",
            f"[1:a]volume=1.0[tts];"
            f"[2:a]volume=0.18,afade=t=in:st=0:d=2,"
            f"afade=t=out:st={bgm_fade_out_start:.3f}:d=3[bgm];"
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


def main():
    OUT_FINAL.parent.mkdir(parents=True, exist_ok=True)

    # --- Step 0: probe all TTS durations ---
    print("=== Step 0: probe TTS durations ===")
    tts_durations: list[float] = []
    for i in range(1, TTS_COUNT + 1):
        d = probe_duration(tts_path(i))
        tts_durations.append(d)
        print(f"  tts_{i:02d}.mp3: {d:.3f}s")
    # segment i (1-based) → tts_durations[i-1]

    # --- Step 1: concat TTS ---
    print("\n=== Step 1: concat TTS with opening/tail silence ===")
    build_tts_full(tts_durations)

    # --- Step 2: build slideshow ---
    # Resolve each slide's duration from the TTS durations it covers.
    print("\n=== Step 2: build image slideshow ===")
    slides: list[tuple[Path, float]] = []
    for img_name, seg_indices in SLIDES_SPEC:
        if seg_indices is None:
            dur = COVER_DURATION
        else:
            dur = sum(tts_durations[i - 1] for i in seg_indices)
        slides.append((PROJ / "images" / img_name, dur))
        print(f"  {img_name}: {dur:.3f}s" + (f" (segments {seg_indices})" if seg_indices else " (cover)"))
    slides_dur = build_slides(slides)

    # --- Step 3: final render ---
    print("\n=== Step 3: final render with audio mix + ASS burn-in ===")
    build_final(slides_dur)

    print(f"\nDONE: {OUT_FINAL}")


if __name__ == "__main__":
    main()
