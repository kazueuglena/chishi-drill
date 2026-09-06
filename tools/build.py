#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""data/qa.json を src/template.html に埋め込んで、単一ファイルの index.html を作る。
   外部リクエストなしで動くので、GitHub Pages でもローカルの file:// でも同じように使える。"""
import json, pathlib, sys

root = pathlib.Path(__file__).resolve().parent.parent
data = json.loads((root / "data" / "qa.json").read_text(encoding="utf-8"))
tpl  = (root / "src" / "template.html").read_text(encoding="utf-8")

# JSON中の </script> がHTMLを壊さないようにエスケープしておく
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

marker = "/*__DATA__*/"
if marker not in tpl:
    sys.exit("テンプレートに埋め込み位置マーカーがない")
out = tpl.replace(marker, blob)

(root / "index.html").write_text(out, encoding="utf-8")

# Claudeのアーティファクト用: doctype/head/body の外枠を外し、PWA関連の参照を落とした版も作る
import re
head = re.search(r"<head>(.*?)</head>", out, re.S).group(1)
body = re.search(r"<body>(.*?)</body>", out, re.S).group(1)
for pat in (r'\s*<link rel="manifest"[^>]*>', r'\s*<link rel="(apple-touch-icon|icon)"[^>]*>',
            r'\s*<meta name="(apple-mobile-web-app|theme-color)[^>]*>',
            r"\s*<meta charset[^>]*>", r'\s*<meta name="viewport"[^>]*>'):
    head = re.sub(pat, "", head)
body = re.sub(r"if \('serviceWorker' in navigator.*?\n\}\n", "", body, flags=re.S)
(root / "artifact.html").write_text(head.strip() + "\n" + body.strip() + "\n", encoding="utf-8")

n = sum(len(s["items"]) for r in data["regions"] for s in r["sections"])
print(f"index.html を書き出した: {n}問 / {len(data['regions'])}地域 / {len(out)/1024:.0f} KB")
