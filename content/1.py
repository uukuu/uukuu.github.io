#!/usr/bin/env python3
"""
restore_underscores.py

功能：
遍历指定目录下的所有 .md 文件，将误转义的下划线 `\_` 恢复为 `_`。
为了安全起见，脚本会自动跳过 YAML 头信息、代码块、行内代码和 HTML 标签，
只处理普通文本区域。

用法:
  python restore_underscores.py --root "你的文件夹路径"
  python restore_underscores.py --root "." --dry-run (仅预览不修改)
"""

import re
import argparse
from pathlib import Path

# 定义需要“保护”不被修改的区域的正则表达式
PROTECTED_PATTERNS = [
    # 1. YAML Frontmatter (文件开头的元数据)
    re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL | re.MULTILINE),
    # 2. 代码块 (Fenced code blocks) ``` ... ```
    re.compile(r"(?s)```.*?```"),
    # 3. 行内代码 (Inline code) ` ... `
    re.compile(r"`[^`]*`"),
    # 4. HTML 标签 (Script/Style/Img etc)
    re.compile(r"(?is)<[^>]+>"),
    # 5. LaTeX 数学公式 (可选，视情况而定，这里默认保护以防破坏公式内的转义)
]

def get_protected_spans(text):
    """
    分析文本，返回所有“受保护区域”的起止位置列表 [(start, end), ...]
    """
    spans = []
    for pat in PROTECTED_PATTERNS:
        for mo in pat.finditer(text):
            spans.append((mo.start(), mo.end()))
    
    # 对区间进行排序并合并重叠区间
    spans.sort()
    merged = []
    for s, e in spans:
        if not merged:
            merged.append([s, e])
        else:
            if s <= merged[-1][1]:
                # 如果当前区间与前一个有重叠或连接，合并
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s, e])
    return [(a, b) for a, b in merged]

def process_file(path: Path, dry_run=False, make_backup=True):
    try:
        text = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        print(f"[跳过] 无法读取非 UTF-8 文件: {path.name}")
        return False

    orig_text = text
    spans = get_protected_spans(text)
    
    output_parts = []
    last_pos = 0
    changed = False

    # 遍历所有受保护的区间，处理区间之间的“普通文本”
    for start, end in spans:
        # 1. 处理受保护区间之前的普通文本 (last_pos -> start)
        if last_pos < start:
            chunk = text[last_pos:start]
            # 执行核心替换逻辑：\_ -> _
            new_chunk = chunk.replace(r"\_", "_")
            if new_chunk != chunk:
                changed = True
            output_parts.append(new_chunk)
        
        # 2. 追加受保护的内容原样不动 (start -> end)
        output_parts.append(text[start:end])
        last_pos = end

    # 3. 处理最后剩余的文本
    if last_pos < len(text):
        tail = text[last_pos:]
        new_tail = tail.replace(r"\_", "_")
        if new_tail != tail:
            changed = True
        output_parts.append(new_tail)

    final_text = "".join(output_parts)

    if changed:
        print(f"[修改] {path}")
        if not dry_run:
            # 创建备份
            if make_backup:
                bak_path = path.with_suffix('.md.bak')
                if not bak_path.exists():
                    bak_path.write_bytes(path.read_bytes())
            
            # 写入文件
            path.write_text(final_text, encoding='utf-8')
        return True
    else:
        return False

def main():
    parser = argparse.ArgumentParser(description="递归将 Markdown 文件中的 \\_ 替换回 _")
    parser.add_argument('--root', default='.', help='要遍历的根目录 (默认为当前目录)')
    parser.add_argument('--dry-run', action='store_true', help='仅预览将要修改的文件，不实际写入')
    parser.add_argument('--no-backup', action='store_true', help='禁用 .bak 文件备份')
    
    args = parser.parse_args()
    root_dir = Path(args.root).resolve()

    print(f"正在扫描目录: {root_dir}")
    print("正在寻找 .md 文件并处理...\n")

    md_files = list(root_dir.rglob("*.md"))
    modified_count = 0

    for f in md_files:
        if f.name.endswith('.bak'): 
            continue # 跳过备份文件
        
        is_modified = process_file(f, dry_run=args.dry_run, make_backup=not args.no_backup)
        if is_modified:
            modified_count += 1

    print("-" * 30)
    if args.dry_run:
        print(f"预览结束。将有 {modified_count} 个文件被修改。")
    else:
        print(f"处理完成。共修改了 {modified_count} 个文件。")

if __name__ == "__main__":
    main()