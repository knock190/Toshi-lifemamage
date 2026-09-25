#!/usr/bin/env python3
"""グラフのページ（board.html）にデータを入れて、公開用の HTML を作る。

使い方: python3 departments/data/build_board.py <data.json> <出力先.html>
data.json は board.html の <script id="board-data"> と同じ形。
出力先は Git に入れない場所（スクラッチ）にする。データは Git に貯めない（2026-09-25 としやす決定）。
"""
import json, sys, pathlib, re

src = pathlib.Path(__file__).with_name('board.html').read_text(encoding='utf-8')
data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
payload = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
out, n = re.subn(r'(<script type="application/json" id="board-data">).*?(</script>)',
                 lambda m: m.group(1) + payload + m.group(2), src, count=1, flags=re.S)
if n != 1:
    sys.exit('board-data が見つかりません')
pathlib.Path(sys.argv[2]).write_text(out, encoding='utf-8')
print('ok', sys.argv[2])
