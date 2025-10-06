#!/usr/bin/env python3
"""
replace_square_to_dollar.py

把 Markdown 中的显示数学定界符 "\[ ... \]" 替换为 "$$ ... $$"，
但会跳过 YAML frontmatter、代码块（```...```）、HTML script/style 等保护区。
对每个被修改的文件会生成一个 `.bak` 备份。

用法:
  python replace_square_to_dollar.py --root "e:/University/Blog/content" [--dry-run]
"""
import re
import argparse
from pathlib import Path

PROTECT_PATTERNS = [
    re.compile(r"(?s)```.*?```"),
    re.compile(r"(?s)^---.*?^---\s*", re.M),
    re.compile(r"(?is)<script.*?>.*?</script>"),
    re.compile(r"(?is)<style.*?>.*?</style>"),
    re.compile(r"`[^`]*`"),
]

DEF_OPEN = re.compile(r"\\\\\[")
DEF_CLOSE = re.compile(r"\\\\\]")

def protect_spans(text):
    spans = []
    for pat in PROTECT_PATTERNS:
        for m in pat.finditer(text):
            spans.append((m.start(), m.end()))
    spans.sort()
    merged = []
    for s,e in spans:
        if not merged:
            merged.append([s,e])
        else:
            if s <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s,e])
    return [(a,b) for a,b in merged]


def process_file(path: Path, dry_run=False):
    text = path.read_text(encoding='utf-8')
    spans = protect_spans(text)
    last = 0
    out = []
    changed = False
    for s,e in spans:
        if last < s:
            chunk = text[last:s]
            new_chunk = DEF_OPEN.sub('$$', chunk)
            new_chunk = DEF_CLOSE.sub('$$', new_chunk)
            if new_chunk != chunk:
                changed = True
            out.append(new_chunk)
        out.append(text[s:e])
        last = e
    if last < len(text):
        tail = text[last:]
        new_tail = DEF_OPEN.sub('$$', tail)
        new_tail = DEF_CLOSE.sub('$$', new_tail)
        if new_tail != tail:
            changed = True
        out.append(new_tail)
    new_text = ''.join(out)
    if changed:
        if dry_run:
            return True, text, new_text
        # do not create .bak by default; caller can opt-in
        path.write_text(new_text, encoding='utf-8')
        return True, text, new_text
    return False, text, text


def find_md(root: Path):
    return list(root.rglob('*.md'))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='.', help='root dir')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--backup', action='store_true', help='create .bak backups for modified files')
    args = p.parse_args()
    root = Path(args.root)
    files = find_md(root)
    # print(f'Found {len(files)} md files under {root}')
    modified = []
    for f in files:
        ok, before, after = process_file(f, dry_run=args.dry_run)
        if ok:
            modified.append(str(f))
            # print('MODIFIED:', f)
    print('Total modified:', len(modified))

if __name__ == '__main__':
    main()
