#!/bin/bash
# v3 叠字：印章放大到 200x200 + 字体大小 130pt 居中

FONT_XK="/System/Library/AssetsV2/com_apple_MobileAsset_Font8/13b8ce423f920875b28b551f9406bf1014e0a656.asset/AssetData/Xingkai.ttc"
cd "/Users/Zhuanz/Documents/Minimax Code Projects/Minimax Video Master/dragon_nine_sons"

# 印章位置：左下角 (x=40, y=1240)，尺寸 200x200，字 130pt 居中
SEAL_X=40
SEAL_Y=1220
SEAL_SIZE=200

# 1
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_01_qiuniu.png \
  -vf "drawtext=text='长子·囚牛':fontfile=${FONT_XK}:fontsize=80:fontcolor=white:x=(w-text_w)/2:y=70:box=1:boxcolor=black@0.65:boxborderw=20,drawtext=text='qiuniu':fontfile=${FONT_XK}:fontsize=46:fontcolor=0xFFD700:x=(w-text_w)/2:y=200,drawtext=text='性好音律 · 琴头之饰':fontfile=${FONT_XK}:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=1200:box=1:boxcolor=black@0.65:boxborderw=16,drawbox=x=${SEAL_X}:y=${SEAL_Y}:w=${SEAL_SIZE}:h=${SEAL_SIZE}:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT_XK}:fontsize=130:fontcolor=white:x=${SEAL_X}+100-text_w/2:y=${SEAL_Y}+100-text_h/2" \
  characters/character_01_qiuniu.png 2>&1 | tail -1

# 2
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_02_yazi.png \
  -vf "drawtext=text='次子·睚眦':fontfile=${FONT_XK}:fontsize=80:fontcolor=white:x=(w-text_w)/2:y=70:box=1:boxcolor=black@0.65:boxborderw=20,drawtext=text='yazi':fontfile=${FONT_XK}:fontsize=46:fontcolor=0xFFD700:x=(w-text_w)/2:y=200,drawtext=text='嗜杀好斗 · 刀剑之饰':fontfile=${FONT_XK}:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=1200:box=1:boxcolor=black@0.65:boxborderw=16,drawbox=x=${SEAL_X}:y=${SEAL_Y}:w=${SEAL_SIZE}:h=${SEAL_SIZE}:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT_XK}:fontsize=130:fontcolor=white:x=${SEAL_X}+100-text_w/2:y=${SEAL_Y}+100-text_h/2" \
  characters/character_02_yazi.png 2>&1 | tail -1

# 3
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_03_chaofeng.png \
  -vf "drawtext=text='三子·嘲风':fontfile=${FONT_XK}:fontsize=80:fontcolor=white:x=(w-text_w)/2:y=70:box=1:boxcolor=black@0.65:boxborderw=20,drawtext=text='chaofeng':fontfile=${FONT_XK}:fontsize=46:fontcolor=0xFFD700:x=(w-text_w)/2:y=200,drawtext=text='喜登高远 · 殿角之饰':fontfile=${FONT_XK}:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=1200:box=1:boxcolor=black@0.65:boxborderw=16,drawbox=x=${SEAL_X}:y=${SEAL_Y}:w=${SEAL_SIZE}:h=${SEAL_SIZE}:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT_XK}:fontsize=130:fontcolor=white:x=${SEAL_X}+100-text_w/2:y=${SEAL_Y}+100-text_h/2" \
  characters/character_03_chaofeng.png 2>&1 | tail -1

# 4
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_04_pulao.png \
  -vf "drawtext=text='四子·蒲牢':fontfile=${FONT_XK}:fontsize=80:fontcolor=white:x=(w-text_w)/2:y=70:box=1:boxcolor=black@0.65:boxborderw=20,drawtext=text='pulao':fontfile=${FONT_XK}:fontsize=46:fontcolor=0xFFD700:x=(w-text_w)/2:y=200,drawtext=text='性好鸣叫 · 洪钟之饰':fontfile=${FONT_XK}:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=1200:box=1:boxcolor=black@0.65:boxborderw=16,drawbox=x=${SEAL_X}:y=${SEAL_Y}:w=${SEAL_SIZE}:h=${SEAL_SIZE}:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT_XK}:fontsize=130:fontcolor=white:x=${SEAL_X}+100-text_w/2:y=${SEAL_Y}+100-text_h/2" \
  characters/character_04_pulao.png 2>&1 | tail -1

# 5
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_05_suanni.png \
  -vf "drawtext=text='五子·狻猊':fontfile=${FONT_XK}:fontsize=80:fontcolor=white:x=(w-text_w)/2:y=70:box=1:boxcolor=black@0.65:boxborderw=20,drawtext=text='suanni':fontfile=${FONT_XK}:fontsize=46:fontcolor=0xFFD700:x=(w-text_w)/2:y=200,drawtext=text='喜静好坐 · 香炉之饰':fontfile=${FONT_XK}:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=1200:box=1:boxcolor=black@0.65:boxborderw=16,drawbox=x=${SEAL_X}:y=${SEAL_Y}:w=${SEAL_SIZE}:h=${SEAL_SIZE}:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT_XK}:fontsize=130:fontcolor=white:x=${SEAL_X}+100-text_w/2:y=${SEAL_Y}+100-text_h/2" \
  characters/character_05_suanni.png 2>&1 | tail -1

# 6
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_06_baxia.png \
  -vf "drawtext=text='六子·霸下':fontfile=${FONT_XK}:fontsize=80:fontcolor=white:x=(w-text_w)/2:y=70:box=1:boxcolor=black@0.65:boxborderw=20,drawtext=text='baxia':fontfile=${FONT_XK}:fontsize=46:fontcolor=0xFFD700:x=(w-text_w)/2:y=200,drawtext=text='力大负重 · 石碑之基':fontfile=${FONT_XK}:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=1200:box=1:boxcolor=black@0.65:boxborderw=16,drawbox=x=${SEAL_X}:y=${SEAL_Y}:w=${SEAL_SIZE}:h=${SEAL_SIZE}:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT_XK}:fontsize=130:fontcolor=white:x=${SEAL_X}+100-text_w/2:y=${SEAL_Y}+100-text_h/2" \
  characters/character_06_baxia.png 2>&1 | tail -1

# 7
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_07_bian.png \
  -vf "drawtext=text='七子·狴犴':fontfile=${FONT_XK}:fontsize=80:fontcolor=white:x=(w-text_w)/2:y=70:box=1:boxcolor=black@0.65:boxborderw=20,drawtext=text='bian':fontfile=${FONT_XK}:fontsize=46:fontcolor=0xFFD700:x=(w-text_w)/2:y=200,drawtext=text='明察秋毫 · 律门之守':fontfile=${FONT_XK}:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=1200:box=1:boxcolor=black@0.65:boxborderw=16,drawbox=x=${SEAL_X}:y=${SEAL_Y}:w=${SEAL_SIZE}:h=${SEAL_SIZE}:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT_XK}:fontsize=130:fontcolor=white:x=${SEAL_X}+100-text_w/2:y=${SEAL_Y}+100-text_h/2" \
  characters/character_07_bian.png 2>&1 | tail -1

# 8
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_08_fuxi.png \
  -vf "drawtext=text='八子·负屃':fontfile=${FONT_XK}:fontsize=80:fontcolor=white:x=(w-text_w)/2:y=70:box=1:boxcolor=black@0.65:boxborderw=20,drawtext=text='fuxi':fontfile=${FONT_XK}:fontsize=46:fontcolor=0xFFD700:x=(w-text_w)/2:y=200,drawtext=text='雅好文采 · 碑文之伴':fontfile=${FONT_XK}:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=1200:box=1:boxcolor=black@0.65:boxborderw=16,drawbox=x=${SEAL_X}:y=${SEAL_Y}:w=${SEAL_SIZE}:h=${SEAL_SIZE}:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT_XK}:fontsize=130:fontcolor=white:x=${SEAL_X}+100-text_w/2:y=${SEAL_Y}+100-text_h/2" \
  characters/character_08_fuxi.png 2>&1 | tail -1

# 9
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_09_chiwen.png \
  -vf "drawtext=text='九子·螭吻':fontfile=${FONT_XK}:fontsize=80:fontcolor=white:x=(w-text_w)/2:y=70:box=1:boxcolor=black@0.65:boxborderw=20,drawtext=text='chiwen':fontfile=${FONT_XK}:fontsize=46:fontcolor=0xFFD700:x=(w-text_w)/2:y=200,drawtext=text='喷浪降雨 · 屋脊之守':fontfile=${FONT_XK}:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=1200:box=1:boxcolor=black@0.65:boxborderw=16,drawbox=x=${SEAL_X}:y=${SEAL_Y}:w=${SEAL_SIZE}:h=${SEAL_SIZE}:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT_XK}:fontsize=130:fontcolor=white:x=${SEAL_X}+100-text_w/2:y=${SEAL_Y}+100-text_h/2" \
  characters/character_09_chiwen.png 2>&1 | tail -1

ls -la characters/
