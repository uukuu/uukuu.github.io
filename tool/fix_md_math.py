#!/usr/bin/env python3
"""
fix_md_math.py

批量修复 Markdown 文件中的数学换行与下划线转义问题：
- 在数学环境（$$...$$, \[...\], $...$）中，把 LaTeX 换行 `\\`（两个反斜杠）升级为 `\\\\`（四个反斜杠），以防止 Markdown 渲染链把 `\\` 变为 `\\` 后丢失；
- 在非数学、非代码、非 frontmatter 区域，把已被转义的下划线 `\_` 还原为 `_`（Revert escaping）。

安全：脚本默认会为每个被修改的文件保存一个 `.bak` 备份文件。
用法:
  python fix_md_math.py [--dry-run] [--root PATH]

示例:
  python fix_md_math.py --root "e:/University/Blog" --dry-run
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

# Math patterns (treated as protected spans to avoid messing up internal underscores)
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
    
    # Check all patterns (Code, HTML, Links AND Math)
    # We include MATH_PATTERNS here so that math blocks are 'protected' 
    # from the underscore un-escaping logic, but we will apply the 
    # backslash fixing logic to them specifically in process_file.
    for pat in PATTERNS + MATH_PATTERNS:
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
    try:
        text = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        print(f"Skipping binary or non-utf8 file: {path}")
        return False, None, None

    orig = text
    spans = protect_spans(text)

    # We'll build new_text by walking through ranges
    out_parts = []
    last = 0
    changed = False

    for (s,e) in spans:
        # 1. Process unprotected region [last, s) (Normal Text)
        if last < s:
            chunk = text[last:s]
            # Logic: Convert escaped underscores `\_` back to `_`
            new_chunk = chunk.replace(r"\_", "_")
            
            if new_chunk != chunk:
                changed = True
            out_parts.append(new_chunk)
            
        # 2. Process protected region [s, e) (Code, Math, Links, etc.)
        prot = text[s:e]
        
        # Check if this protected region is a Math region
        is_math = (
            ('$$' in prot) or 
            ('\\[' in prot) or 
            (prot.startswith('$') and prot.endswith('$')) or 
            (prot.startswith('\\(') and prot.endswith('\\)')) or 
            ('\\begin' in prot) or 
            (prot.strip().startswith('<script type="math/tex'))
        )

        if is_math:
            # Apply backslash doubling for Math
            new_prot = RE_TWO_BACKSLASHES.sub(REPL_FOUR, prot)
            if new_prot != prot:
                changed = True
            out_parts.append(new_prot)
        else:
            # Other protected regions (code blocks, links) are left alone
            out_parts.append(prot)
            
        last = e

    # tail
    if last < len(text):
        tail = text[last:]
        # Logic: Convert escaped underscores `\_` back to `_`
        new_tail = tail.replace(r"\_", "_")
        
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
    
    print(f"Scanning for .md files under: {root}")
    files = find_md_files(root)
    print(f"Found {len(files)} .md files")
    
    modified = []
    for f in files:
        if args.backup and not args.dry_run:
            # Create simple backup before reading/writing
            bak_path = f.with_suffix('.md.bak')
            if not bak_path.exists():
                try:
                    bak_path.write_bytes(f.read_bytes())
                except Exception as e:
                    print(f"Failed to backup {f}: {e}")

        ok, before, after = process_file(f, dry_run=args.dry_run)
        if ok:
            modified.append(str(f))
            print(f"MODIFIED: {f}")
            if args.preview:
                print('--- before ---')
                print(before[-500:] if len(before)>500 else before)
                print('--- after ---')
                print(after[-500:] if len(after)>500 else after)
                print('-'*20)
                
    print(f"Total modified: {len(modified)}")

if __name__ == '__main__':
    main()