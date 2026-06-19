#!/usr/bin/env python3
"""
Post-production pipeline v2 — correct timing:
  - Each segment target = max(voice_duration + 0.4, 5.875)
  - Video: tpad to target
  - Voice: apad to target
  - Subtitle timed to actual voice duration within each target window
"""
import os
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/Zhuanz/Documents/Minimax Code Projects/Minimax Video Master/cloisonne_drama")
FFMPEG = "/opt/homebrew/Cellar/ffmpeg-full/8.1.1/bin/ffmpeg"
FFPROBE = "/opt/homebrew/Cellar/ffmpeg-full/8.1.1/bin/ffprobe"

def run(cmd):
    print(f"[run] {cmd[:180]}{'...' if len(cmd)>180 else ''}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print("STDERR:", r.stderr[-1500:])
        sys.exit(f"FAILED: {cmd[:120]}")
    return r

def ffprobe_dur(fp):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(fp)], capture_output=True, text=True)
    return float(r.stdout.strip())

# === Step 1: probe voice + clip durations ===
voice_dur = {i: ffprobe_dur(ROOT / "audio" / f"voice_{i:02d}.mp3") for i in range(1, 9)}
clip_dur = {i: ffprobe_dur(ROOT / "clips" / f"clip_{i:02d}.mp4") for i in range(1, 9)}
print("Voice:", {k: round(v, 2) for k, v in voice_dur.items()})
print("Clip :", {k: round(v, 2) for k, v in clip_dur.items()})

# === Step 2: compute per-segment targets ===
# target = max(clip_dur, voice_dur + 0.4)
# ensures video ≥ voice + 0.4 OR video ≥ orig (whichever is bigger)
target = {}
for i in range(1, 9):
    target[i] = max(clip_dur[i], voice_dur[i] + 0.4)
print("Target:", {k: round(v, 2) for k, v in target.items()})
total = sum(target.values())
print(f"Total target: {total:.2f}s")

# === Step 3: clean and prep output dirs ===
import glob
for d in ["clips_padded", "audio_padded"]:
    p = ROOT / d
    p.mkdir(exist_ok=True)
    for f in glob.glob(str(p / "*.mp4")) + glob.glob(str(p / "*.mp3")):
        os.remove(f)

# === Step 4: pad each video to target ===
print("\n[Pad videos]")
for i in range(1, 9):
    src = ROOT / "clips" / f"clip_{i:02d}.mp4"
    dst = ROOT / "clips_padded" / f"clip_{i:02d}.mp4"
    extra = target[i] - clip_dur[i]
    if extra > 0.05:
        cmd = (
            f'{FFMPEG} -y -i "{src}" '
            f'-vf "tpad=stop_mode=clone:stop_duration={extra:.3f},setpts=PTS-STARTPTS" '
            f'-c:v libx264 -preset fast -crf 18 -an "{dst}"'
        )
        run(cmd)
    else:
        # no padding needed, just re-encode for consistency
        cmd = f'{FFMPEG} -y -i "{src}" -c:v libx264 -preset fast -crf 18 -an "{dst}"'
        run(cmd)
    actual = ffprobe_dur(dst)
    print(f"  clip_{i:02d}: target {target[i]:.2f}s → actual {actual:.2f}s")

# === Step 5: pad each voice to target (apad silence) ===
print("\n[Pad voices with apad silence]")
for i in range(1, 9):
    src = ROOT / "audio" / f"voice_{i:02d}.mp3"
    dst = ROOT / "audio_padded" / f"voice_{i:02d}.mp3"
    extra = target[i] - voice_dur[i]
    if extra > 0.05:
        cmd = (
            f'{FFMPEG} -y -i "{src}" '
            f'-af "apad=pad_dur={extra:.3f},atrim=0:{target[i]:.3f}" '
            f'-c:a libmp3lame -b:a 128k "{dst}"'
        )
    else:
        cmd = f'{FFMPEG} -y -i "{src}" -c:a libmp3lame -b:a 128k "{dst}"'
    run(cmd)
    actual = ffprobe_dur(dst)
    print(f"  voice_{i:02d}: target {target[i]:.2f}s → actual {actual:.2f}s")

# === Step 6: concat padded videos ===
print("\n[Concat videos]")
vlist = ROOT / "clips_padded" / "filelist.txt"
with open(vlist, "w") as f:
    for i in range(1, 9):
        f.write(f"file '{(ROOT / 'clips_padded' / f'clip_{i:02d}.mp4')}'\n")
raw_video = ROOT / "raw_video.mp4"
if raw_video.exists():
    raw_video.unlink()
run(f'{FFMPEG} -y -f concat -safe 0 -i "{vlist}" -c copy "{raw_video}"')
print(f"  raw_video: {ffprobe_dur(raw_video):.3f}s")

# === Step 7: concat padded voices ===
print("\n[Concat voices]")
alist = ROOT / "audio_padded" / "filelist.txt"
with open(alist, "w") as f:
    for i in range(1, 9):
        f.write(f"file '{(ROOT / 'audio_padded' / f'voice_{i:02d}.mp3')}'\n")
voice_all = ROOT / "audio" / "voice_all.mp3"
if voice_all.exists():
    voice_all.unlink()
run(f'{FFMPEG} -y -f concat -safe 0 -i "{alist}" -c copy "{voice_all}"')
print(f"  voice_all: {ffprobe_dur(voice_all):.3f}s")

# === Step 8: mix voice + BGM ===
print("\n[Mix voice + BGM]")
mixed = ROOT / "audio" / "mixed.m4a"
if mixed.exists():
    mixed.unlink()
run(
    f'{FFMPEG} -y -i "{voice_all}" -stream_loop -1 -i "{ROOT}/bgm/bgm.mp3" '
    f'-filter_complex "[1:a]volume=0.20[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=0[mix]" '
    f'-map "[mix]" -c:a aac -b:a 192k "{mixed}"'
)
print(f"  mixed: {ffprobe_dur(mixed):.3f}s")

# === Step 9: attach audio to video (explicit -t) ===
print("\n[Attach audio + explicit -t]")
va = ROOT / "video_with_audio.mp4"
if va.exists():
    va.unlink()
run(
    f'{FFMPEG} -y -i "{raw_video}" -i "{mixed}" '
    f'-map 0:v -map 1:a -c:v copy -c:a copy -t {total:.3f} -shortest "{va}"'
)
print(f"  video_with_audio: {ffprobe_dur(va):.3f}s")

# === Step 10: build .ass subtitle file ===
print("\n[Build .ass subtitle]")
narrations = [
    "他，便是这门古老技艺的传承人，\n数十年如一日，守护着掐丝珐琅的火与色。",
    "一张宣纸，几笔墨痕，\n是作品的灵魂起点。",
    "匠人将紫铜片锤打成器形，\n作品的骨架便由此铸就。",
    "细如发丝的扁铜丝，\n在指尖弯折成画的经脉。",
    "矿物釉料被一一填入丝间，\n恰如点染丹青。",
    "入窑七百度的锤炼，\n釉与丝相融相生。",
    "砂石一遍遍地打磨，\n器面方能光可鉴人。",
    "镀金之后，丝如金线，釉如宝石。\n掐丝珐琅，至此方成大器。",
]

def ts(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t - h*3600 - m*60
    return f"{h:d}:{m:02d}:{s:05.2f}"

events = []
cur = 0.0
for i, narr in enumerate(narrations, 1):
    start = cur + 0.15
    end = cur + voice_dur[i] + 0.05
    events.append((start, end, narr))
    cur += target[i]
print("Subtitle events:")
for s, e, t in events:
    print(f"  {ts(s)} --> {ts(e)}: {t.split(chr(10))[0]}")

ass_header = """[Script Info]
Title: Cloisonne Drama Subs
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,STKaiti,40,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,1,2,40,40,160,134

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

ass_path = ROOT / "subtitles.ass"
with open(ass_path, "w", encoding="utf-8") as f:
    f.write(ass_header)
    for s, e, text in events:
        f.write(f"Dialogue: 0,{ts(s)},{ts(e)},Default,,0,0,0,,{text}\n")
print(f"  saved: {ass_path}")

# === Step 11: burn subtitles ===
print("\n[Burn subtitles]")
final = ROOT / "cloisonne_drama.mp4"
if final.exists():
    final.unlink()
run(
    f'{FFMPEG} -y -i "{va}" -vf "ass={ass_path}" '
    f'-c:v libx264 -preset slow -crf 20 -c:a copy -t {total:.3f} "{final}"'
)
print(f"\n✓ FINAL: {final} ({ffprobe_dur(final):.3f}s)")
print(f"  size: {os.path.getsize(final)/1024/1024:.1f} MB")
print("DONE")
