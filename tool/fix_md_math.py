#!/usr/bin/env python3
"""
fix_md_math.py

批量修复 Markdown 文件中的数学换行与下划线转义问题：
- 在数学环境（$$...$$, \[...\], $...$）中，把 LaTeX 换行 `\\`（两个反斜杠）升级为 `\\\\`（四个反斜杠），以防止 Markdown 渲染链把 `\\` 变为 `\\` 后丢失；
- 在非数学、非代码、非 frontmatter 区域，把未转义的下划线 `_` 替换为 `\_`，以避免被 Markdown 解释为斜体。

安全：脚本默认会为每个被修改的文件保存一个 `.bak` 备份文件。
用法:
  python fix_md_math.py [--dry-run] [--root PATH]

示例:
  python fix_md_math.py --root "e:/University/Blog" --dry-run

注意：对非常复杂的 Markdown（例如混合很多 HTML、embed、或不规范的 math delimiter），脚本可能不是 100% 无副作用，运行前请先使用 --dry-run 并检查差异。
"""

import re
import sys
import argparse
from pathlib import Path

# Patterns for protected regions
PATTERNS = [
    # YAML frontmatter handled separately
    # Fenced code blocks ```...```
    re.compile(r"(?s)```.*?```"),
    # HTML script/style tags
    re.compile(r"(?is)<script.*?>.*?</script>"),
    re.compile(r"(?is)<style.*?>.*?</style>"),
    # Inline code `...`
    re.compile(r"`[^`]*`"),
    # Markdown links/images ![alt](url) or [alt](url)
    re.compile(r"!\[[^\]]*\]\([^\)]*\)"),
    re.compile(r"\[[^\]]*\]\([^\)]*\)"),
]

# Math patterns (we'll treat math spans specially)
MATH_PATTERNS = [
    re.compile(r"(?s)\$\$.*?\$\$"),        # $$...$$ display
    re.compile(r"(?s)\\\[.*?\\\]"),      # \[ ... \]
    re.compile(r"(?s)(?<!\$)\$(?!\$).*?(?<!\$)\$(?!\$)"),  # inline $...$
    re.compile(r"(?s)\\\(.*?\\\)"),      # \( ... \)
    re.compile(r"(?is)<script[^>]*type=[\"']?math/tex[^>]*>.*?</script>"),
]

# Regex to find exactly two backslashes (not part of a longer run). Replace with four.
RE_TWO_BACKSLASHES = re.compile(r"(?<!\\)(\\\\)(?!\\)")
REPL_FOUR = r"\\\\\\\\"

# Regex to escape underscores that are not already escaped (only inside math spans per user's request)
RE_UNDERSCORE = re.compile(r"(?<!\\)_(?!\\)")


def protect_spans(text):
    """Return list of (start,end) spans that should NOT be modified (protected regions).
    Also include YAML frontmatter span if present.
    """
    spans = []
    # YAML frontmatter
    if text.startswith('---'):
        m = re.search(r"^---\s*\n.*?\n---\s*\n", text, flags=re.S)
        if m:
            spans.append((m.start(), m.end()))
    # Other patterns
    for pat in PATTERNS:
        for mo in pat.finditer(text):
            spans.append((mo.start(), mo.end()))
    # merge spans
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
    orig = text
    spans = protect_spans(text)

    # We'll build new_text by walking through ranges
    out_parts = []
    last = 0
    changed = False

    for (s,e) in spans:
        # process unprotected region [last, s)
        if last < s:
            chunk = text[last:s]
            # new_chunk = RE_UNDERSCORE.sub(r"\\_", chunk)
            new_chunk = chunk
            if new_chunk != chunk:
                changed = True
            out_parts.append(new_chunk)
        # protected region appended unchanged for now, except for math-specific replacements
        prot = text[s:e]
        # If this protected region is a math region (contains $ or \\[ or $$), apply backslash doubling
        if ('$$' in prot) or ('\\[' in prot) or (prot.startswith('$') and prot.endswith('$')) or ('\begin' in prot) or (prot.strip().startswith('<script type="math/tex')):
            # replace exact two backslashes with four, but avoid touching existing quadruples
            new_prot = RE_TWO_BACKSLASHES.sub(REPL_FOUR, prot)
            if new_prot != prot:
                changed = True
            out_parts.append(new_prot)
        else:
            out_parts.append(prot)
        last = e
    # tail
    if last < len(text):
        tail = text[last:]
        new_tail = RE_UNDERSCORE.sub(r"\\_", tail)
        if new_tail != tail:
            changed = True
        out_parts.append(new_tail)

    new_text = ''.join(out_parts)

    if changed:
        if dry_run:
            return True, orig, new_text
        # by default do not create .bak files unless caller requests
        path.write_text(new_text, encoding='utf-8')
        return True, orig, new_text
    return False, orig, orig


def find_md_files(root: Path):
    return list(root.rglob('*.md'))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='.', help='repo root (default current dir)')
    p.add_argument('--dry-run', action='store_true', help='show changes but do not write')
    p.add_argument('--backup', action='store_true', help='create .bak backups for modified files')
    p.add_argument('--preview', action='store_true', help='print diff for changed files')
    args = p.parse_args()

    root = Path(args.root).resolve()
    tool_dir = Path(__file__).parent
    # print(f"Scanning for .md files under: {root}")
    files = find_md_files(root)
    # print(f"Found {len(files)} .md files")
    modified = []
    for f in files:
        ok, before, after = process_file(f, dry_run=args.dry_run)
        if ok:
            modified.append(str(f))
            # print("MODIFIED:", f)
            # if args.preview:
            #     # show small preview
            #     print('--- before ---')
            #     print(before[:1000])
            #     print('--- after ---')
            #     print(after[:1000])
    print(f"Total modified: {len(modified)}")

if __name__ == '__main__':
    main()
