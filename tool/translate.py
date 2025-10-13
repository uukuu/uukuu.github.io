# -*- coding: utf-8 -*-
import re
from pathlib import Path

# Load input
in_path = Path("/mnt/data/1.txt")
text = in_path.read_text(encoding="utf-8")

def strip_leading_indents(s: str) -> str:
    # Remove leading spaces/tabs on each line but keep blank lines
    return "\n".join([re.sub(r"^[ \t]+", "", line) for line in s.splitlines()])

def replace_braces_escapes(s: str) -> str:
    # Replace \{ -> \lbrace  and  \} -> \rbrace, and add a space after each
    # Use negative lookbehind to avoid double-replacing if already done.
    s = re.sub(r"\\\{", r"\\lbrace ", s)
    s = re.sub(r"\\\}", r"\\rbrace ", s)
    return s

def replace_sets_and_symbols(s: str) -> str:
    # \R \N \C \Q
    s = re.sub(r"\\R\b", r"\\mathbb{R}", s)
    s = re.sub(r"\\N\b", r"\\mathbb{N}", s)
    s = re.sub(r"\\C\b", r"\\mathbb{C}", s)
    s = re.sub(r"\\Q\b", r"\\mathbb{Q}", s)
    # \td, \ti
    s = re.sub(r"\\td\b", r"\\text{d}", s)
    s = re.sub(r"\\ti\b", r"\\text{i}", s)
    # \mst
    s = re.sub(r"\\mst\b", r"\\text{s.t.}", s)
    return s

def replace_problem_headers(s: str) -> str:
    # \problem[<id>]Title  ->  ## <id>\nTitle
    def _repl(m):
        ident = m.group("id").strip()
        rest = m.group("rest")
        # ensure following content starts on new line
        if rest and not rest.startswith("\n"):
            rest = "\n" + rest
        return f"## {ident}{rest}"
    pattern = re.compile(r"\\problem\[(?P<id>[^\]]+)\](?P<rest>.*)")
    # Replace per-line to avoid greediness across paragraphs
    lines = s.splitlines()
    out_lines = []
    for line in lines:
        if "\\problem" in line:
            line = re.sub(pattern, _repl, line)
        out_lines.append(line)
    return "\n".join(out_lines)

def replace_norm(s: str) -> str:
    # \norm{X} -> \Vert X \Vert
    s = re.sub(r"\\norm\{([^{}]+)\}", r"\\Vert \1 \\Vert", s)
    # \norm\alpha  or \norm \cdot  -> capture control sequence or token
    s = re.sub(r"\\norm\s*(\\[A-Za-z]+|[^{}\s]+)", r"\\Vert \1 \\Vert", s)
    return s

def replace_mint(s: str) -> str:
    # \mint[low]^up  -> \displaystyle\int_{low}^{up}
    # allow spaces, optional braces on up
    s = re.sub(
        r"\\mint\[\s*([^\]]+?)\s*\]\s*\^\s*(?:\{([^}]+)\}|([^\s\}]+))",
        lambda m: "\\displaystyle\\int_{%s}^{%s}" % (m.group(1), (m.group(2) or m.group(3))),
        s
    )
    return s

def replace_proof_solution_with_admonition(s: str) -> str:
    # Insert <!--more--> before the first begin{proof} or begin{solution}
    first_match = re.search(r"\\begin\{(?:proof|solution)\}", s)
    if first_match:
        idx = first_match.start()
        s = s[:idx] + "<!--more-->\n" + s[idx:]
    # Replace begin/end
    s = re.sub(r"\\begin\{proof\}", r'{{< admonition note "答案" false >}}', s)
    s = re.sub(r"\\end\{proof\}", r"{{< /admonition >}}", s)
    s = re.sub(r"\\begin\{solution\}", r'{{< admonition note "答案" false >}}', s)
    s = re.sub(r"\\end\{solution\}", r"{{< /admonition >}}", s)
    return s

def replace_lstlisting(s: str) -> str:
    # \begin{lstlisting} ... \end{lstlisting} => ```cpp ... ```
    s = re.sub(r"\\begin\{lstlisting\}", "```cpp", s)
    s = re.sub(r"\\end\{lstlisting\}", "```", s)
    return s

def replace_itemize(s: str) -> str:
    # Convert itemize blocks to markdown lists
    def _block(m):
        content = m.group(1)
        # Convert \item lines to "- " with preserved text; handle nesting by leaving indentation under markdown
        lines = content.splitlines()
        out = []
        for line in lines:
            line_stripped = re.sub(r"^[ \t]+", "", line)
            if re.match(r"\\item\b", line_stripped):
                # remove \item
                line_after = re.sub(r"^\\item\b[ \t]*", "", line_stripped)
                out.append(f"- {line_after}")
            else:
                if line_stripped.strip() == "":
                    out.append("")
                else:
                    # continuation lines: indent by two spaces
                    out.append(f"  {line_stripped}")
        return "\n".join(out)
    s = re.sub(r"\\begin\{itemize\}(.*?)\\end\{itemize\}", _block, s, flags=re.DOTALL)
    return s

def remove_label_tags(s: str) -> str:
    return re.sub(r"\\label\{[^}]*\}", "", s)

def replace_figures(s: str) -> str:
    # Convert figure environments to markdown images and ignore latex-specific options
    def _repl(figm):
        inner = figm.group(1)
        # find includegraphics path
        m = re.search(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", inner)
        if not m:
            return ""
        path = m.group(1)
        # unify to URL starting with figures/...
        # If path already starts with 'figures/', keep tail; otherwise, leave as-is
        if "figures/" in path:
            idx = path.find("figures/")
            tail = path[idx+len("figures/"):]
            url = f"https://blog.nan2inf.com/figures/{tail}"
        else:
            # Fallback: use as-is after last slash
            url = f"https://blog.nan2inf.com/{path.lstrip('/')}"
        return f"![]({url})"
    s = re.sub(r"\\begin\{figure\}.*?\}(.*?)\\end\{figure\}", _repl, s, flags=re.DOTALL)
    return s

def to_markdown(s: str) -> str:
    s = strip_leading_indents(s)
    s = replace_braces_escapes(s)
    s = replace_problem_headers(s)
    s = replace_proof_solution_with_admonition(s)
    s = replace_lstlisting(s)
    s = replace_itemize(s)
    s = replace_figures(s)
    s = remove_label_tags(s)
    s = replace_sets_and_symbols(s)
    s = replace_norm(s)
    s = replace_mint(s)
    return s

md = to_markdown(text)

out_path = Path("/mnt/data/1_converted.md")
out_path.write_text(md, encoding="utf-8")

# Basic scan for non-default LaTeX-like commands not handled here
known_cmds = {
    "newpage","section","problem","begin","end","align*","includegraphics","centering",
    "mathbb","text","lbrace","rbrace","sup","leqslant","sqrt","max",
    "displaystyle","int","proof","solution","itemize","item","label","H"
}
# find commands
cmds = set(re.findall(r"\\([A-Za-z]+)\b", text))
unknown = sorted([c for c in cmds if c not in known_cmds])

print("Converted markdown written to:", out_path.as_posix())
print("Potential non-standard commands found:", ", ".join(unknown) if unknown else "None")

