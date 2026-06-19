# Minimax Video Master

中国传统文化短视频 AI 生产工作流 / Chinese Cultural Heritage Short-Video AI Production Workflow

> 基于 matrix MCP（MiniMax）的 AI 生成 + ffmpeg-full 后期合成的端到端流水线
> End-to-end pipeline: matrix MCP (MiniMax) AI generation + ffmpeg-full post-composition

---

## 这是什么 / What is this

8 个独立的短视频项目，每个项目走同样的三段式流水线：

8 independent short-video projects, all following the same 3-stage pipeline:

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│ 1. 规划   │ →  │ 2. 生成   │ →  │ 3. 合成   │
│ Planning │    │Generation│    │ Compose  │
└──────────┘    └──────────┘    └──────────┘
   .md / .json     matrix MCP     ffmpeg + PIL
   storyboard      (TTS/图/视频/   + ass 字幕
                    音乐)
```

| 阶段 Stage | 工具 Tool | 输入 Input | 输出 Output |
|------------|-----------|-----------|------------|
| 1. 规划 Planning | 人工 / AI 对话 | 主题 | `analysis/*.md` · `storyboard/*.md` · `tts_request.json` · `image_request.json` · `bgm_request.json` |
| 2. 生成 Generation | matrix MCP | Stage 1 的 request JSON | `audio/*.mp3` · `images/*.png` · `clips/*.mp4` · `bgm/*.mp3` |
| 3. 合成 Compose | `ffmpeg-full` + Python/PIL | Stage 2 的素材 | 最终 `.mp4` 视频 |

> **注意 / Note**：本仓库**只包含 Stage 1（规划）和 Stage 3（合成）的代码**。Stage 2 生成的媒体文件（mp4/mp3/png）通过 `.gitignore` 排除——它们是 2GB+ 的可再生产物，不是工作流本身。
>
> This repo only ships **Stage 1 (planning) and Stage 3 (composition) code**. Stage 2 media (mp4/mp3/png) is excluded by `.gitignore` — it's 2GB+ of regenerable artifacts, not the workflow itself.

---

## 项目清单 / Project Index

| # | 项目 Project | 主题 Theme | 风格 Style | 关键脚本 Key script |
|---|-------------|-----------|-----------|-------------------|
| 1 | `cloisonne_drama/` | 掐丝珐琅 8 镜头写实短剧 | 写实纪实 / Realistic | `post_production.py` |
| 2 | `cloisonne_ink/` | 掐丝珐琅水墨版（脚本） | 水墨 / Ink | `script_outline.md`（仅规划） |
| 3 | `cloisonne_plate/` | 掐丝珐琅盘子单口短片 | 综合 / Mixed | `build_v2.py`（PIL 烧字幕） |
| 4 | `dragon_nine_sons/` | 龙生九子 + 红印章叠字 | 国风 / Chinese | `add_text_v3.sh`（ffmpeg drawtext） |
| 5 | `shen_shou_drama/` | 中国神兽水墨短片 | 水墨 / Ink | `compose.py` |
| 6 | `sui_yang_podcast/` | 隋炀帝 · 播客横版 1920×1080 | 知识科普 / Docu | `scripts/build_video.py` + `scripts/build_subtitles.py` |
| 7 | `sui_yang_short/` | 隋炀帝 · 竖版 1080×1920 | 短视频 / Vertical | `scripts/build_short.py` + `scripts/build_subtitles.py` |
| 8 | `suxiu_embroidery/` | 苏绣 8 镜头写实短剧 | 写实纪实 / Realistic | （无独立 build 脚本，复用 cloisonne_drama 模式） |

---

## 新终端使用流程 / How to use on a fresh terminal

### 1. 准备环境 / Setup environment

```bash
# macOS (Apple Silicon) — ffmpeg-full 是关键（带 libass，能烧 ASS 字幕）
brew install ffmpeg-full

# Python 3.11+，需要 PIL（仅 cloisonne_plate 用）
python3 -m pip install --user Pillow

# 配置 matrix MCP（MiniMax）的认证
# Config matrix MCP (MiniMax) auth — see your org's docs
```

> ⚠️ 仓库里所有 `.py` 脚本里写死了 `FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"`。换机器后要么建这个路径的软链，要么改脚本里的常量。强烈建议用 `brew install ffmpeg-full` 安装到默认位置。
>
> ⚠️ All `.py` scripts hardcode `FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"`. Either keep the install path or edit the constant. `brew install ffmpeg-full` installs to the expected location.

### 2. 跑一个项目 / Run a project

以 `sui_yang_podcast/` 为例（最完整的样板）：

```bash
cd sui_yang_podcast

# Stage 1: 已经有规划文档（analysis / storyboard / tts_request.json）
ls scripts/
#   tts_request.json        ← 喂给 matrix TTS
#   build_subtitles.py      ← 生成 SRT + ASS
#   build_video.py          ← 最终合成
#   image_request.json      ← 喂给 matrix 生图（Stage 2 用）

# Stage 2: 在新终端上用 matrix MCP 重新生成素材
#   - TTS → audio/tts_01.mp3 ... tts_07.mp3
#   - 生图 → images/01_cover.png ... 06_pic5_yangguang_portrait.png
#   - BGM → bgm/bgm_main.mp3
# 这些文件没在本仓库里（被 .gitignore 排除），但 .json 请求文件告诉你怎么重新生成

# Stage 3: 生成字幕 + 最终合成
python3 scripts/build_subtitles.py
python3 scripts/build_video.py
# → output/sui_yang_podcast_final.mp4
```

### 3. 8 个项目的差异 / Per-project quirks

| 项目 | 关键差异 Key difference |
|------|---------------------|
| `sui_yang_podcast` | 横版 1920×1080, 7 段 TTS, 6 张配图, 280s. 一遍合成。 |
| `sui_yang_short` | 竖版 1080×1920, 6 段 TTS, 6 张配图, 90s. TTS 间插静音做节奏。 |
| `cloisonne_drama` | 8 个 AI 视频片段 (5.875s/段), tpad+apad 对齐, 烧 ASS 字幕。 |
| `shen_shou_drama` | 类似 cloisonne_drama 但加 13s 黑场补到 60s, BGM 用 `stream_loop -1`。 |
| `dragon_nine_sons` | 静态图 + ffmpeg drawtext 叠标题印章, **不烧字幕**。 |
| `cloisonne_plate` | 7 段, **用 PIL 烧字幕** (不用 ffmpeg ass filter)。 |
| `cloisonne_ink` | **仅规划**, 无合成脚本。 |
| `suxiu_embroidery` | 与 cloisonne_drama 同结构, 8 段 5.875s, 写实纪实风。 |

---

## 目录约定 / Directory convention

每个子项目根目录一般有：

```
<project>/
├── analysis/              ← Stage 1: 剧本分析 (script_analysis.md, asset_list.md)
├── storyboard/            ← Stage 1: 分镜脚本 (storyboard.md, scene_index.json)
├── scripts/               ← Stage 3: 合成脚本 (build_*.py, *.json)
├── subtitles/             ← Stage 3 输出: SRT + ASS
├── subtitles.ass/.srt     ← 顶层字幕 (部分项目)
├── audio/                 ← Stage 2 输出: TTS mp3 (被 gitignore)
├── images/                ← Stage 2 输出: AI 生图 (被 gitignore)
├── clips/                 ← Stage 2 输出: AI 视频片段 (被 gitignore)
├── bgm/                   ← Stage 2 输出: BGM (被 gitignore)
├── output/                ← Stage 3 最终输出 (被 gitignore)
└── *.py / *.sh            ← 合成入口
```

---

## 关键技术细节 / Key technical details

1. **ffmpeg-full 必备** — macOS 自带 ffmpeg 没有 libass，烧 ASS 字幕会爆。Homebrew 装 `ffmpeg-full`。
2. **concat demuxer 不要用 filter** — `-f concat -safe 0 -i filelist.txt -c copy` 保持原时长；filter 形式的 `concat=n=N` 会重编码缩水。
3. **5.875s 是 matrix 视频的固定时长** — Stage 2 出来的视频片段几乎都是 5.875s 一段，Stage 3 脚本里硬编码这个值。
4. **ASS 字幕淡入淡出** — `Dialogue` 行的 `Style` 后面用 `\fad(400,400)` 之类的转义，加 `\an2` 居中。
5. **BGM loop** — `ffmpeg -stream_loop -1 -i bgm.mp3 -t <total_sec> ...` 循环 BGM 到视频总长。
6. **ass filter 坑** — 项目路径含空格（"Minimax Code Projects"）时，ffmpeg filter 解析器会再炸一次。新终端建议把仓库 clone 到无空格路径。

---

## 给 AI Agent 的指引 / For AI agents

如果你的下一个会话要在这个仓库里工作，请读 [`AGENTS.md`](./AGENTS.md)。

If your next session will work in this repo, read [`AGENTS.md`](./AGENTS.md).

---

## 许可 / License

本仓库是个人/团队的工作流模板，对外公开方便跨终端复用。媒体资产（生成的视频/图片/音频）归 matrix MCP / MiniMax 平台与原作者所有，请勿用作商业用途。
This repo is a personal/team workflow template, public for cross-terminal reuse. The media assets (generated video/image/audio) belong to the matrix MCP / MiniMax platform and original authors — do not use commercially.
