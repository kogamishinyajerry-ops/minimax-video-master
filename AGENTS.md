# AGENTS.md

> 给新终端的 AI 编程助手（Codex / OpenCode / Cursor / Claude Code …）读的项目说明。
> Read this first if you are an AI coding agent working in this repo.

## 项目性质 / What this repo is

**这不是一个"代码项目"**——它是一个**短视频生产工作流的代码骨架**。8 个子项目每个走相同的三段式：

1. **规划 (Planning)** — `analysis/*.md`, `storyboard/*.md`, `scripts/*.json` 描述要做什么
2. **生成 (Generation)** — 用 matrix MCP（MiniMax）调 AI 生 TTS / 生图 / 生视频 / 生 BGM。**本仓库没有这部分的代码**——通过 `.json` 请求 + MCP CLI 调用实现
3. **合成 (Composition)** — `*.py` / `*.sh` 脚本用 ffmpeg-full 把 Stage 2 素材拼成最终视频

媒体产物（mp4 / mp3 / png）**不在 git 里**——它们是 Stage 2/3 的输出，不是工作流本身。新终端需要**重新生成**或**从别处复制**。

## 跑通一个项目的最小步骤 / Minimal steps to run a project

```bash
# 假设要跑 sui_yang_podcast
cd sui_yang_podcast

# 1. 用 matrix MCP 跑 tts_request.json → audio/tts_01..07.mp3
#    用 matrix 生图（image_request.json 或类似）→ images/*.png
#    用 matrix 生 BGM → bgm/bgm_main.mp3
# （具体调用看 matrix MCP 工具说明 / 平台文档）

# 2. 跑合成脚本
python3 scripts/build_subtitles.py
python3 scripts/build_video.py
# → output/sui_yang_podcast_final.mp4
```

## 关键约定 / Key conventions

### 文件路径硬编码
每个 `.py` 里 `PROJ = Path("/Users/Zhuanz/Documents/Minimax Code Projects/Minimax Video Master/<project>")` 写死了 macOS 路径。**新终端必须改这个路径**或者把仓库放到同一路径。

> 提示：在 `sui_yang_podcast/scripts/build_video.py` 顶部、`cloisonne_drama/post_production.py` 第 15-17 行等位置都有。改之前先 `grep -rn "PROJ = Path" --include="*.py"` 一下。

### ffmpeg 路径硬编码
```python
FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
```
- macOS：`brew install ffmpeg-full` 装到这个路径
- Linux：自己编译带 `--enable-libass` 的 ffmpeg

### 字体硬编码（drawtext 场景）
`dragon_nine_sons/add_text_v3.sh` 用了 `Xingkai.ttc`（macOS 系统字体）。Linux 终端要换成可用中文字体（如 `Noto Serif CJK SC`）。

## 8 个子项目的合成入口 / Build entry per project

| 项目 | 入口 | 关键依赖 |
|------|------|---------|
| `cloisonne_drama` | `python3 post_production.py` | `audio/voice_01..08.mp3` + `clips/clip_01..08.mp4` + `bgm/bgm.mp3` |
| `cloisonne_ink` | ⚠️ 无合成脚本 — 仅规划 | — |
| `cloisonne_plate` | `python3 build_v2.py` | `output/videos/scene_01..07.mp4` + `output/audio/v2/voice_01..07.mp3` + `cloisonne_ink/output/bgm.mp3` |
| `dragon_nine_sons` | `bash add_text_v3.sh` | `raw/clean_01..09_*.png` → `characters/*.png` |
| `shen_shou_drama` | `python3 compose.py` | `output/clips/*.mp4` + `output/audio/*.mp3` + `output/music/bgm.mp3` |
| `sui_yang_podcast` | `python3 scripts/build_subtitles.py` → `python3 scripts/build_video.py` | `audio/tts_01..07.mp3` + `images/01_cover.png ... 06_pic5_*.png` + `bgm/bgm_main.mp3` |
| `sui_yang_short` | `python3 scripts/build_subtitles.py` → `python3 scripts/build_short.py` | `audio/tts_01..06.mp3` + `images/01_cover.png ... 06_yangguang.png` + `bgm/bgm_short.mp3` |
| `suxiu_embroidery` | ⚠️ 无独立 build 脚本 — 仿照 cloisonne_drama 模式写 | — |

## 已知坑（来自实战）/ Known gotchas

1. **macOS ffmpeg 默认不带 libass** — 必须 `brew install ffmpeg-full`，否则 `ass` filter 不存在
2. **项目路径含空格** — ffmpeg filter 解析器对空格敏感，建议 clone 到无空格路径
3. **`-shortest` 会裁视频** — 当音频比视频短时会反向裁视频。用 `-t <total>` 显式指定总长
4. **`concat` filter 会重编码缩水** — 用 `concat demuxer` (`-f concat -safe 0 -i filelist.txt -c copy`) 保持原时长
5. **5.875s 是 matrix 视频固定时长** — 几乎所有分镜脚本都假设 5.875s/段
6. **Python 默认 LF + 无 BOM** — 不影响 Python 自身，但写 `.bat` 时记得转 CRLF（这个仓库没有 .bat，跳过）

## 你的任务是什么？ / What's your task?

接到任务前先确认：
- [ ] 用户想跑**已有的项目** → 看上方"跑通一个项目的最小步骤"
- [ ] 用户想做**新项目** → 模仿 `sui_yang_podcast/` 的结构：先写 `analysis/script_analysis.md` → 再写 `storyboard/storyboard.md` → 再写 `scripts/tts_request.json` + `image_request.json` + `bgm_request.json` → 调 matrix MCP 生成素材 → 最后写 `scripts/build_*.py` 合成
- [ ] 用户想**改 bug** → 看对应的 `*.py` 顶部 `PROJ` / `FFMPEG` 路径是否匹配本地环境
- [ ] 用户想**改风格** → 改 `subtitles.ass` / `script.ass` 的 Style 行（STKaiti 字号、颜色、位置）

## 不要做 / Do NOT

- ❌ 不要把 Stage 2 生成的 mp4/mp3/png 提交到 git — `.gitignore` 已经排除，但如果你用 `git add -f` 强制加，会污染仓库
- ❌ 不要修改 `*.json` 请求文件中的 prompt 不告诉用户 — 这是 Stage 2 的输入，改了会影响再生产
- ❌ 不要在没有本地 ffmpeg-full 的环境跑合成脚本 — 必爆
- ❌ 不要把 `subtitles.ass` 当文本改 — 它是 ASS 字幕格式，特殊字符（`{`、`}`、`\N`）有语法意义
