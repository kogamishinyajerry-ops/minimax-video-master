#!/usr/bin/env python3
"""
Build ASS subtitle for the 90s vertical Sui Yang short.

Layout: 1080x1920 (9:16 vertical).
Two styles:
  - Default: 60pt, 22 chars/line max, bottom-center, 字幕 实际正文
  - BigText: 110pt, 2-8 chars, mid-screen emphasis flash (大字弹幕)
  - TitleBig: 130pt, opening title card

Timeline (cumulative t in seconds):
  0.00-3.00   cover head (silent, title card via TitleBig)
  3.00-8.07   TTS_01 (intro)            + Default 字幕
  8.07-12.50  interlude 1 (大字弹幕)       + BigText
 12.50-19.64  TTS_02 (运河)              + Default
 19.64-24.00  interlude 2                + BigText
 24.00-31.51  TTS_03 (科举)              + Default
 31.51-36.00  interlude 3                + BigText
 36.00-44.86  TTS_04 (太急)              + Default
 44.86-49.00  interlude 4                + BigText
 49.00-56.40  TTS_05 (史官)              + Default
 56.40-61.00  interlude 5                + BigText
 61.00-68.88  TTS_06 (CTA)               + Default
 68.88-90.00  tail (3 大字收尾)             + BigText
"""
import re
from pathlib import Path
from datetime import timedelta

PROJ = Path("/Users/Zhuanz/Documents/Minimax Code Projects/Minimax Video Master/sui_yang_short")

# (segment_index, tts_text, duration_sec, start_time)
# start_time is when this segment's audio begins in the full track.
SEGMENTS = [
    (1, "杨广,被骂了,一千四百年的暴君。可今天,我要给他翻案。", 5.07, 3.00),
    (2, "他修了一条运河,北京到杭州,两千多公里,唐宋明清,一千多年,都靠它吃饭。", 7.14, 12.50),
    (3, "他还搞了科举,让平民能靠读书当官。这套制度,用了一千三百年,直到清朝才废。", 7.51, 24.00),
    (4, "可他为什么亡了?一个字,急。修运河、征高句丽、建东都,所有大事十几年里全干完了,民夫死绝。", 8.86, 36.00),
    (5, "他被骂成昏君,有多少是真的?唐朝写的史书,把前朝皇帝,写得越坏越好。", 7.40, 49.00),
    (6, "他不是圣人,也不是昏君,是急功近利的改革家,一个输给了时间的人。评论区,给他打个分。", 7.88, 61.00),
]

# Interlude 大字弹幕 (start_time, end_time, text)
INTERLUDES = [
    (8.07, 12.50, "一条运河\\N养活中国 1400 年"),
    (19.64, 24.00, "科举\\N让平民翻身"),
    (31.51, 36.00, "一个字\\N急"),
    (44.86, 49.00, "历史\\N由胜利者写"),
    (56.40, 61.00, "急功近利\\N的改革家"),
]

# Tail 收尾大字 (start_time, end_time, text)
TAIL_BIG = [
    (68.88, 75.50, "评论\\N给他打个分"),
    (75.50, 83.00, "关注\\N下期更狠"),
    (83.00, 90.00, "隋炀帝\\N翻案系列"),
]

# Opening title card (层 1, large)
OPENING_TITLE = (0.0, 3.0, "被骂 1400 年\\N的暴君 隋炀帝")


def split_subtitle(text: str, max_chars: int = 22) -> list[str]:
    """Split TTS text into displayable chunks <= max_chars Chinese chars.

    First pass: split on 。！？  then on 、，；, then greedily re-pack.
    (Same logic as the horizontal version — 22 chars fits comfortably
    in 1080 vertical width at 60pt with margin 60.)
    """
    sents = [p.strip() for p in re.split(r"(?<=[。！？])", text) if p.strip()]
    clause_pat = re.compile(r"(?<=[、,，;；])")
    chunks: list[str] = []
    for sent in sents:
        if len(sent) <= max_chars:
            chunks.append(sent)
            continue
        subs = [p.strip() for p in clause_pat.split(sent) if p.strip()]
        cur = ""
        for sp in subs:
            if not cur:
                cur = sp
            elif len(cur) + len(sp) <= max_chars:
                cur += sp
            else:
                chunks.append(cur)
                cur = sp
        if cur:
            chunks.append(cur)
    return chunks


def fmt_ass_ts(t_sec: float) -> str:
    td = timedelta(seconds=max(0.0, t_sec))
    total_cs = int(td.total_seconds() * 100)
    h, rem = divmod(total_cs, 3600 * 100)
    m, rem = divmod(rem, 60 * 100)
    s, cs = divmod(rem, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def main():
    ass_lines: list[str] = []
    srt_lines: list[str] = []

    # Build Default dialogue lines for each TTS segment
    srt_idx = 1
    for seg_idx, text, duration, seg_start in SEGMENTS:
        sents = split_subtitle(text)
        weights = [max(1, len(s)) for s in sents]
        total_w = sum(weights)
        seg_t = seg_start
        for s, w in zip(sents, weights):
            dur = duration * (w / total_w)
            start = seg_t
            end = seg_t + dur
            end_padded = end - 0.05 if (end - start) > 0.4 else end
            ass_lines.append(
                f"Dialogue: 0,{fmt_ass_ts(start)},{fmt_ass_ts(end_padded)},Default,,0,0,0,,{s}"
            )
            seg_t = end

    # Interlude 大字弹幕 (layer 2, BigText)
    for start, end, text in INTERLUDES:
        ass_lines.append(
            f"Dialogue: 2,{fmt_ass_ts(start)},{fmt_ass_ts(end)},BigText,,0,0,0,,{text}"
        )

    # Tail 收尾 (layer 2, BigText)
    for start, end, text in TAIL_BIG:
        ass_lines.append(
            f"Dialogue: 2,{fmt_ass_ts(start)},{fmt_ass_ts(end)},BigText,,0,0,0,,{text}"
        )

    # Opening title card (layer 1, TitleBig)
    s, e, t = OPENING_TITLE
    opening = f"Dialogue: 1,{fmt_ass_ts(s)},{fmt_ass_ts(e)},TitleBig,,0,0,0,,{t}"

    # ASS header
    ass_header = """[Script Info]
Title: Sui Yang Emperor Yang Guang - 90s Short (Vertical 9:16)
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,STHeiti SC,60,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,60,60,220,1
Style: BigText,STHeiti SC,110,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,5,80,80,0,1
Style: TitleBig,STHeiti SC,130,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8,3,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    ass_full = ass_header + opening + "\n" + "\n".join(ass_lines) + "\n"

    ass_path = PROJ / "subtitles" / "script.ass"
    ass_path.parent.mkdir(parents=True, exist_ok=True)
    ass_path.write_text(ass_full, encoding="utf-8")

    print(f"Generated ASS -> {ass_path}")
    print(f"  Default 字幕 chunks: {sum(len(split_subtitle(t)) for _, t, _, _ in SEGMENTS)}")
    print(f"  Interlude 大字弹幕: {len(INTERLUDES)}")
    print(f"  Tail 收尾大字: {len(TAIL_BIG)}")
    print(f"  Total ASS lines: {2 + len(ass_lines)}")


if __name__ == "__main__":
    main()
