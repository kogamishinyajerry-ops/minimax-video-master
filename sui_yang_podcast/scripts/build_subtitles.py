#!/usr/bin/env python3
"""
Build SRT + ASS subtitle for the Sui Yang podcast video.

Each TTS segment is one visual. Within a segment, sentences are split
and time-stamped proportionally based on character count.

Output:
  - subtitles/script.srt     (SRT for sanity check)
  - subtitles/script.ass     (ASS with style: bottom-center, large font, fade in/out)
"""
import re
from pathlib import Path
from datetime import timedelta

PROJ = Path("/Users/Zhuanz/Documents/Minimax Code Projects/Minimax Video Master/sui_yang_podcast")

# (segment_index, tts_text, duration_sec)
# Order matches the TTS request order.
SEGMENTS = [
    (1, "公元六一八年，一个皇帝在扬州被自己的禁卫军用一条白绫勒死。\n他死后，接管天下的唐朝给他定了一个字的谥号——炀。\n这个字什么意思？去礼远众曰炀，翻译成大白话就是：荒淫无道、众叛亲离。\n一个字，把他钉在了昏君的耻辱柱上，一钉就是一千四百年。", 26.388),
    (2, "可是有件事很多人不知道：今天连接北京和杭州、至今还在通航、南水北调工程还在用它河道的京杭大运河，主干就是这个昏君挖出来的。\n那么问题来了——一个真正的昏君，怎么会留下一条恩泽中国一千多年的工程？\n今天这篇，我想给杨广翻个案。", 23.220),
    (3, "第一件事：那条一千四百年后还在用的运河。\n杨广一上台，就干了件惊天动地的大工程：开凿大运河。\n他把北边到涿郡（今天的北京）、南边到余杭（今天的杭州）的一条条旧河道，用洛阳当中心，硬生生连成了一条贯通南北、全长两千多公里的水上大动脉。\n这条河有多重要？在没有铁路和高速公路的古代，它第一次把中国的北方政治中心和南方经济粮仓，用一条高速水路连了起来。\n之后唐朝的繁荣、宋朝的富庶、明清的漕运，全都靠它吃饭。\n换句话说，杨广花了自己一朝的命，修了一条养活后面一千多年的路。", 47.556),
    (4, "第二件事：他给平民一条逆天改命的路。\n如果说运河是看得见的功劳，那第二件事，影响更深远——他设立了进士科，正式开启了科举制度。\n在杨广之前，当官靠什么？靠出身、靠门第。\n你爹是世家大族，你天生就是官；你是农民的儿子，读再多书也没用。\n社会的上升通道，被几个大家族死死焊住。\n而科举的意思是：不管你爹是谁，考试考得好，你就能当官。\n这在当时是石破天惊的。\n它第一次给了底层平民一条凭本事改命的路，这套制度一直用到了清朝末年，整整影响了中国一千三百年。\n我们今天说的知识改变命运，根子就在这里。", 50.508),
    (5, "那他到底输在哪？——不是坏，是太急。\n讲到这你可能想问：这么牛，那他怎么还亡国了？\n问题就出在这两个字：太急。\n修运河、营建东都洛阳、三次大规模征讨高句丽……这些事单拎出来，每一件都是雄主才敢干的大手笔。\n可杨广把它们全堆在了十几年里，一起干。\n修运河，几百万民夫累死在工地上；征高句丽，百万大军三次惨败，尸骨堆成山。\n整个国家像一台被踩到红线的发动机，被他在十几年里榨干了最后一滴油。\n于是民怨沸腾，天下大乱，隋朝二世而亡。\n他不是不知道这些事该做，他是太想在自己手里把它们全做完。\n——这不是昏，这是一个改革者最致命的傲慢。", 53.028),
    (6, "最后一个问题：那他为什么被骂成暴君？\n这里有个很多人忽略的真相：历史是胜利者写的。\n推翻隋朝、坐上龙椅的是唐朝。\n一个新王朝要证明自己取代前朝是天经地义，最好的办法是什么？就是把前朝最后那个皇帝，写得越坏越好。\n所以你今天在史书里看到的那个荒淫、残暴、一无是处的杨广，有几分是真的，有几分是唐朝人需要他是这样的？\n我不是要给杨广洗白成圣人——他确实残暴、确实把百姓往死里用。\n但把一个做了运河、立了科举的改革者，简单粗暴地骂成昏君，这本身就是对历史的偷懒。\n他真正的标签应该是四个字：急功近利。\n一个输给了时间的改革家。", 52.020),
    (7, "你怎么看？\n如果给你一个机会评价杨广，你会给他打几分？\n你觉得他是被冤枉的改革家，还是罪有应得的暴君？\n评论区聊聊，我看看有多少人敢跟史书对着干。\n下一期被冤枉的帝王系列，我们聊另一个被骂惨的人——商鞅。\n关注我，下期不迷路。", 22.176),
]


def split_sentences(text: str, max_chars: int = 22) -> list[str]:
    """Split text into displayable chunks, each <= max_chars Chinese chars.

    Rules:
      1. Honor explicit \\n in source — each line treated as one paragraph.
      2. Within a paragraph, first split on 。！？  (sentence ends).
      3. If a resulting sentence is still > max_chars, split further on
         clause punctuation 、 , ， ; ； ——  and greedily re-pack into
         chunks of <= max_chars so each subtitle line fits in 1920px width.
    """
    raw_lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    chunks: list[str] = []
    clause_pat = re.compile(r"(?<=[、,，;；——])")

    for line in raw_lines:
        # First pass: split on sentence-end punctuation
        sents = [p.strip() for p in re.split(r"(?<=[。！？])", line) if p.strip()]
        for sent in sents:
            if len(sent) <= max_chars:
                chunks.append(sent)
                continue
            # Second pass: split long sentence on clause punctuation
            subs = [p.strip() for p in clause_pat.split(sent) if p.strip()]
            cur = ""
            for sp in subs:
                if not cur:
                    cur = sp
                elif len(cur) + len(sp) <= max_chars:
                    cur = cur + sp
                else:
                    chunks.append(cur)
                    cur = sp
            if cur:
                chunks.append(cur)
    return chunks


def fmt_ts(t_sec: float) -> str:
    """Format seconds as SRT timestamp HH:MM:SS,mmm"""
    td = timedelta(seconds=max(0.0, t_sec))
    total_ms = int(td.total_seconds() * 1000)
    h, rem = divmod(total_ms, 3600 * 1000)
    m, rem = divmod(rem, 60 * 1000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def fmt_ass_ts(t_sec: float) -> str:
    """Format seconds as ASS timestamp H:MM:SS.cc (centiseconds)"""
    td = timedelta(seconds=max(0.0, t_sec))
    total_cs = int(td.total_seconds() * 100)
    h, rem = divmod(total_cs, 3600 * 100)
    m, rem = divmod(rem, 60 * 100)
    s, cs = divmod(rem, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def main():
    srt_lines = []
    ass_lines = []
    cursor = 0.0  # seconds, running time within the full video audio track

    srt_idx = 1
    for seg_idx, text, duration in SEGMENTS:
        sents = split_sentences(text)
        # weight by character count, with a tiny minimum so a single-char line still gets visible time
        weights = [max(1, len(s)) for s in sents]
        total_w = sum(weights)
        seg_t = cursor
        for s, w in zip(sents, weights):
            dur = duration * (w / total_w)
            start = seg_t
            end = seg_t + dur
            # Tiny padding inside the segment so the line clears before next appears
            start_with_pad = start
            end_with_pad = end - 0.05 if (end - start) > 0.4 else end
            srt_lines.append(f"{srt_idx}\n{fmt_ts(start_with_pad)} --> {fmt_ts(end_with_pad)}\n{s}\n")
            ass_lines.append(
                f"Dialogue: 0,{fmt_ass_ts(start_with_pad)},{fmt_ass_ts(end_with_pad)},Default,,0,0,0,,{s}"
            )
            srt_idx += 1
            seg_t = end
        cursor += duration

    # Open the cover title slot: we add a 3s opening title card before segment 1
    # Shift everything by 3s
    OPEN_OFFSET = 3.0
    srt_lines = []
    ass_lines = []
    cursor = OPEN_OFFSET
    srt_idx = 1
    for seg_idx, text, duration in SEGMENTS:
        sents = split_sentences(text)
        weights = [max(1, len(s)) for s in sents]
        total_w = sum(weights)
        seg_t = cursor
        for s, w in zip(sents, weights):
            dur = duration * (w / total_w)
            start = seg_t
            end = seg_t + dur
            start_with_pad = start
            end_with_pad = end - 0.05 if (end - start) > 0.4 else end
            srt_lines.append(f"{srt_idx}\n{fmt_ts(start_with_pad)} --> {fmt_ts(end_with_pad)}\n{s}\n")
            ass_lines.append(
                f"Dialogue: 0,{fmt_ass_ts(start_with_pad)},{fmt_ass_ts(end_with_pad)},Default,,0,0,0,,{s}"
            )
            srt_idx += 1
            seg_t = end
        cursor += duration

    # ---- Build ASS header + body ----
    ass_header = """[Script Info]
Title: Sui Yang Emperor Yang Guang - Podcast Video
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,STHeiti SC,60,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,1,2,80,80,90,1
Style: TitleBig,STHeiti SC,96,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,80,80,100,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    # Opening title card: 主推标题, 0 -> 3s
    opening = (
        f"Dialogue: 1,0:00:00.00,{fmt_ass_ts(OPEN_OFFSET)},TitleBig,,0,0,0,,被骂了1400年的暴君隋炀帝\\N他做的两件事\\N却养活了之后整个中国"
    )

    ass_full = ass_header + opening + "\n" + "\n".join(ass_lines) + "\n"

    srt_path = PROJ / "subtitles" / "script.srt"
    ass_path = PROJ / "subtitles" / "script.ass"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
    ass_path.write_text(ass_full, encoding="utf-8")

    total_dur = OPEN_OFFSET + sum(d for _, _, d in SEGMENTS)
    print(f"Generated {len(srt_lines)} SRT lines, {len(ass_lines)} ASS dialogue lines")
    print(f"Total video duration: {total_dur:.2f}s = {total_dur/60:.2f} min")
    print(f"SRT: {srt_path}")
    print(f"ASS: {ass_path}")


if __name__ == "__main__":
    main()
