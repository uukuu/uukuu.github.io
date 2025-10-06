#!/usr/bin/env python3
"""
fix_backslashes_in_math.py

针对单个 Markdown 文件：仅在数学区域（$$...$$, \[...\], \(...\), $...$, <script type="math/tex">）中
将恰好两个反斜杠 "\\" 替换为四个 "\\\\"，并保证幂等性（已是四个的不变）。
生成备份 .bak

用法:
  python fix_backslashes_in_math.py <file.md>
"""
import re
import sys
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('file', help='markdown file to process')
parser.add_argument('--dry-run', action='store_true', help='do not write changes; only report')
parser.add_argument('--backup', action='store_true', help='create .bak backup for the file')
args = parser.parse_args()

p = Path(args.file)
if not p.exists():
    print('File not found:', p)
    sys.exit(2)

text = p.read_text(encoding='utf-8')
# patterns for math spans
math_pats = [
    re.compile(r'(?s)\$\$.*?\$\$'),
    re.compile(r'(?s)\\\\\[.*?\\\\\]'),
    re.compile(r'(?s)\\\\\(.*?\\\\\)'),
    re.compile(r"(?s)(?<!\$)\$(?!\$).*?(?<!\$)\$(?!\$)"),
    re.compile(r"(?is)<script[^>]*type=[\'\"]?math/tex[^>]*>.*?</script>"),
]
# match positions
spans = []
for pat in math_pats:
    for m in pat.finditer(text):
        spans.append((m.start(), m.end()))
spans.sort()
# merge spans
merged = []
for s,e in spans:
    if not merged:
        merged.append([s,e])
    else:
        if s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s,e])

if not merged:
    print('No math spans found in', p)
    sys.exit(0)

RE_TWO = re.compile(r'(?<!\\)(\\\\)(?!\\)')
repl = r'\\\\\\\\'

out_parts = []
last = 0
changed = False
for s,e in merged:
    if last < s:
        out_parts.append(text[last:s])
    chunk = text[s:e]
    new_chunk = RE_TWO.sub(repl, chunk)
    if new_chunk != chunk:
        changed = True
    out_parts.append(new_chunk)
    last = e
if last < len(text):
    out_parts.append(text[last:])
new_text = ''.join(out_parts)
if changed:
    if args.dry_run:
        print('Would update', p)
        sys.exit(0)
    if args.backup:
        bak = p.with_suffix(p.suffix + '.bak')
        bak.write_text(text, encoding='utf-8')
        print('Updated', p, 'backup at', bak)
    p.write_text(new_text, encoding='utf-8')
    print('Updated', p)
else:
    print('No changes needed (no exact double-backslashes in math spans).')

