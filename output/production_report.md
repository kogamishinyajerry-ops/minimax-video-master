# 中华神兽水墨介绍视频 · 制作报告

## 基本信息
- **短剧名称**:中华神兽 · 千古之韵(Chinese Mythical Beasts · Shuimo Style)
- **总时长**:70.5 秒
- **分辨率**:1376 × 768(16:9 横版)
- **帧率**:24 fps
- **编码**:H.264 High Profile / AAC 192kbps
- **文件大小**:35.3 MB
- **分镜数量**:12

## 结构
- **开篇**(Scene_01):墨韵生辉,标题"中华神兽 · 千古之韵"
- **五兽依次登场**(Scene_02-11):每只神兽 2 个分镜(动态出场 + 近景特写)
  - 青龙 · 东方木(S02-S03)
  - 白虎 · 西方金(S04-S05)
  - 朱雀 · 南方火(S06-S07)
  - 玄武 · 北方水(S08-S09)
  - 麒麟 · 中央土(S10-S11)
- **收尾**(Scene_12):五山远景 + 主题"中华神兽 · 永耀古今"

## 素材清单
- **神兽参考图**:5 张(青龙/白虎/朱雀/玄武/麒麟)
- **场景参考图**:7 张(东方云海/西方山岭/南方火海/北方玄海/中央祥云/开篇墨场/收尾群峰)
- **分镜首帧**:12 张
- **分镜视频片段**:12 个
- **BGM**:1 首(古风水墨 · 73.3 秒循环匹配)

## 后期处理
- **拼接方式**:concat demuxer(`-c copy` 不重编码,保持原始时长 5.875s/段)
- **字幕**:ASS 格式,主标题(STKaiti 72pt)+ 副标题(STKaiti 40pt),含 0.4s 淡入淡出
- **BGM**:`/opt/homebrew/opt/ffmpeg-full` 编译版(libass + libharfbuzz 支持)
- **音视频混合**:BGM 音量 0.25,末尾 2.5s 淡出,总时长 `-t 70.5` 强制

## 视觉风格
- 核心:Chinese ink wash painting / shuimo
- 调色板:水墨五色(焦浓重淡清)+ 神兽本色点缀
- 关键技巧:飞白、晕染、留白、虚实相生
- 神兽以写意笔触呈现,非写实 CGI

## 输出文件
| 文件 | 用途 | 大小 |
|------|------|------|
| `output/final_drama.mp4` | **最终视频(带字幕+BGM)** | 35.3 MB |
| `output/final_with_subs.mp4` | 视频+字幕(无 BGM) | 34.7 MB |
| `output/final_raw.mp4` | 纯拼接视频 | 27.3 MB |
| `output/subtitles.ass` | 字幕源文件 | - |
| `output/audio/bgm.mp3` | BGM 源文件 | 1.2 MB |

## 制作时间
- **开始**:2026-06-08 13:24
- **完成**:2026-06-08 14:04
- **总耗时**:约 40 分钟

## 关键发现 / 经验沉淀
1. **ffmpeg 默认 build 不带 libass** — macOS homebrew 装的 ffmpeg 8.1.1 默认没有 `--enable-libass`,ass/subtitles filter 都不存在。需要装 `ffmpeg-full` (keg-only) 才能烧字幕。
2. **ass filter 路径不能有空格** — 项目路径含 `Minimax Code Projects` 空格,ffmpeg filter 解析器对空格敏感,需用符号链接到无空格路径再调用。
3. **concat demuxer + `-c copy` 保持原时长** — 5.875s × 12 = 70.5s 精确无损。如果用 concat filter 重编码会缩水到 45s 左右。
4. **视频生成 prompt 要短** — matrix 视频生成对 prompt 长度敏感,1-2 句 1 个核心动作最稳。
