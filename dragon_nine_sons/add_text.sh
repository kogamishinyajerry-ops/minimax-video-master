#!/bin/bash
# 给 9 张神兽图叠书法字（用 ffmpeg drawtext 100% 准确）

FONT="/System/Library/AssetsV2/com_apple_MobileAsset_Font8/88d6cc32a907955efa1d014207889413890573be.asset/AssetData/Kaiti.ttc"
cd "/Users/Zhuanz/Documents/Minimax Code Projects/Minimax Video Master/dragon_nine_sons"

# 1: 长子·囚牛
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_01_qiuniu.png \
  -vf "drawtext=text='长子·囚牛':fontfile=${FONT}:fontsize=72:fontcolor=white:x=(w-text_w)/2:y=80:box=1:boxcolor=black@0.55:boxborderw=18,drawtext=text='qiuniu':fontfile=${FONT}:fontsize=42:fontcolor=0xFFD700:x=(w-text_w)/2:y=190,drawtext=text='性好音律 · 琴头之饰':fontfile=${FONT}:fontsize=42:fontcolor=white:x=(w-text_w)/2:y=1260:box=1:boxcolor=black@0.55:boxborderw=14,drawbox=x=30:y=1280:w=130:h=130:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT}:fontsize=88:fontcolor=white:x=30+65-text_w/2:y=1280+65-text_h/2" \
  characters/character_01_qiuniu.png 2>&1 | tail -1

# 2: 次子·睚眦
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_02_yazi.png \
  -vf "drawtext=text='次子·睚眦':fontfile=${FONT}:fontsize=72:fontcolor=white:x=(w-text_w)/2:y=80:box=1:boxcolor=black@0.55:boxborderw=18,drawtext=text='yazi':fontfile=${FONT}:fontsize=42:fontcolor=0xFFD700:x=(w-text_w)/2:y=190,drawtext=text='嗜杀好斗 · 刀剑之饰':fontfile=${FONT}:fontsize=42:fontcolor=white:x=(w-text_w)/2:y=1260:box=1:boxcolor=black@0.55:boxborderw=14,drawbox=x=30:y=1280:w=130:h=130:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT}:fontsize=88:fontcolor=white:x=30+65-text_w/2:y=1280+65-text_h/2" \
  characters/character_02_yazi.png 2>&1 | tail -1

# 3: 三子·嘲风
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_03_chaofeng.png \
  -vf "drawtext=text='三子·嘲风':fontfile=${FONT}:fontsize=72:fontcolor=white:x=(w-text_w)/2:y=80:box=1:boxcolor=black@0.55:boxborderw=18,drawtext=text='chaofeng':fontfile=${FONT}:fontsize=42:fontcolor=0xFFD700:x=(w-text_w)/2:y=190,drawtext=text='喜登高远 · 殿角之饰':fontfile=${FONT}:fontsize=42:fontcolor=white:x=(w-text_w)/2:y=1260:box=1:boxcolor=black@0.55:boxborderw=14,drawbox=x=30:y=1280:w=130:h=130:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT}:fontsize=88:fontcolor=white:x=30+65-text_w/2:y=1280+65-text_h/2" \
  characters/character_03_chaofeng.png 2>&1 | tail -1

# 4: 四子·蒲牢
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_04_pulao.png \
  -vf "drawtext=text='四子·蒲牢':fontfile=${FONT}:fontsize=72:fontcolor=white:x=(w-text_w)/2:y=80:box=1:boxcolor=black@0.55:boxborderw=18,drawtext=text='pulao':fontfile=${FONT}:fontsize=42:fontcolor=0xFFD700:x=(w-text_w)/2:y=190,drawtext=text='性好鸣叫 · 洪钟之饰':fontfile=${FONT}:fontsize=42:fontcolor=white:x=(w-text_w)/2:y=1260:box=1:boxcolor=black@0.55:boxborderw=14,drawbox=x=30:y=1280:w=130:h=130:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT}:fontsize=88:fontcolor=white:x=30+65-text_w/2:y=1280+65-text_h/2" \
  characters/character_04_pulao.png 2>&1 | tail -1

# 5: 五子·狻猊
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_05_suanni.png \
  -vf "drawtext=text='五子·狻猊':fontfile=${FONT}:fontsize=72:fontcolor=white:x=(w-text_w)/2:y=80:box=1:boxcolor=black@0.55:boxborderw=18,drawtext=text='suanni':fontfile=${FONT}:fontsize=42:fontcolor=0xFFD700:x=(w-text_w)/2:y=190,drawtext=text='喜静好坐 · 香炉之饰':fontfile=${FONT}:fontsize=42:fontcolor=white:x=(w-text_w)/2:y=1260:box=1:boxcolor=black@0.55:boxborderw=14,drawbox=x=30:y=1280:w=130:h=130:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT}:fontsize=88:fontcolor=white:x=30+65-text_w/2:y=1280+65-text_h/2" \
  characters/character_05_suanni.png 2>&1 | tail -1

# 6: 六子·霸下
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_06_baxia.png \
  -vf "drawtext=text='六子·霸下':fontfile=${FONT}:fontsize=72:fontcolor=white:x=(w-text_w)/2:y=80:box=1:boxcolor=black@0.55:boxborderw=18,drawtext=text='baxia':fontfile=${FONT}:fontsize=42:fontcolor=0xFFD700:x=(w-text_w)/2:y=190,drawtext=text='力大负重 · 石碑之基':fontfile=${FONT}:fontsize=42:fontcolor=white:x=(w-text_w)/2:y=1260:box=1:boxcolor=black@0.55:boxborderw=14,drawbox=x=30:y=1280:w=130:h=130:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT}:fontsize=88:fontcolor=white:x=30+65-text_w/2:y=1280+65-text_h/2" \
  characters/character_06_baxia.png 2>&1 | tail -1

# 7: 七子·狴犴
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_07_bian.png \
  -vf "drawtext=text='七子·狴犴':fontfile=${FONT}:fontsize=72:fontcolor=white:x=(w-text_w)/2:y=80:box=1:boxcolor=black@0.55:boxborderw=18,drawtext=text='bian':fontfile=${FONT}:fontsize=42:fontcolor=0xFFD700:x=(w-text_w)/2:y=190,drawtext=text='明察秋毫 · 律门之守':fontfile=${FONT}:fontsize=42:fontcolor=white:x=(w-text_w)/2:y=1260:box=1:boxcolor=black@0.55:boxborderw=14,drawbox=x=30:y=1280:w=130:h=130:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT}:fontsize=88:fontcolor=white:x=30+65-text_w/2:y=1280+65-text_h/2" \
  characters/character_07_bian.png 2>&1 | tail -1

# 8: 八子·负屃
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_08_fuxi.png \
  -vf "drawtext=text='八子·负屃':fontfile=${FONT}:fontsize=72:fontcolor=white:x=(w-text_w)/2:y=80:box=1:boxcolor=black@0.55:boxborderw=18,drawtext=text='fuxi':fontfile=${FONT}:fontsize=42:fontcolor=0xFFD700:x=(w-text_w)/2:y=190,drawtext=text='雅好文采 · 碑文之伴':fontfile=${FONT}:fontsize=42:fontcolor=white:x=(w-text_w)/2:y=1260:box=1:boxcolor=black@0.55:boxborderw=14,drawbox=x=30:y=1280:w=130:h=130:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT}:fontsize=88:fontcolor=white:x=30+65-text_w/2:y=1280+65-text_h/2" \
  characters/character_08_fuxi.png 2>&1 | tail -1

# 9: 九子·螭吻
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i raw/clean_09_chiwen.png \
  -vf "drawtext=text='九子·螭吻':fontfile=${FONT}:fontsize=72:fontcolor=white:x=(w-text_w)/2:y=80:box=1:boxcolor=black@0.55:boxborderw=18,drawtext=text='chiwen':fontfile=${FONT}:fontsize=42:fontcolor=0xFFD700:x=(w-text_w)/2:y=190,drawtext=text='喷浪降雨 · 屋脊之守':fontfile=${FONT}:fontsize=42:fontcolor=white:x=(w-text_w)/2:y=1260:box=1:boxcolor=black@0.55:boxborderw=14,drawbox=x=30:y=1280:w=130:h=130:color=red@0.92:t=fill,drawtext=text='龍':fontfile=${FONT}:fontsize=88:fontcolor=white:x=30+65-text_w/2:y=1280+65-text_h/2" \
  characters/character_09_chiwen.png 2>&1 | tail -1

ls -la characters/
