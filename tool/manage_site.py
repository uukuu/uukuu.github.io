#!/usr/bin/env python3
"""
manage_site.py

工具脚本：在项目根下运行数学格式修复脚本（现有的 fix_md_math.py、replace_square_to_dollar.py、fix_backslashes_in_math.py），
并可启动 Hugo 本地服务以便预览。

用法示例：
  python manage_site.py --root "e:\\University\\Blog" --fix-all --dry-run
  python manage_site.py --root . --start-hugo --port 1313 --bind 0.0.0.0

脚本会默认调用当前 Python 解释器运行子脚本（保持环境一致）。
"""
from pathlib import Path
import subprocess
import sys
import shutil
import os
import socket


def run_python_script(script: Path, args: list):
    cmd = [sys.executable, str(script)] + args
    print("\n>>> ", " ".join(cmd))
    try:
        completed = subprocess.run(cmd, check=False)
        return completed.returncode == 0
    except FileNotFoundError:
        print(f"Python script not found: {script}")
        return False


def start_hugo_server(root: Path, port: int = 1313, bind: str = 'localhost', drafts: bool = True, disable_fast_render: bool = True):
    if shutil.which('hugo') is None:
        print('hugo not found in PATH. Please install Hugo or add it to PATH.')
        return 2
    cmd = ['hugo', 'server', f'--bind={bind}', f'--port={port}']
    if drafts:
        cmd.append('-D')
    if disable_fast_render:
        cmd.append('--disableFastRender')

    print('\n>>> Starting Hugo server in foreground (press Ctrl+C to stop)')
    print('>>> Command:', ' '.join(cmd))
    # Run Hugo server in the specified root
    try:
        p = subprocess.Popen(cmd, cwd=str(root))
        p.wait()
        return p.returncode
    except KeyboardInterrupt:
        print('\nHugo server interrupted by user')
        try:
            p.terminate()
        except Exception:
            pass
        return 0


def find_md_files(root: Path):
    return list(root.rglob('*.md'))


def main():
    """No-arg workflow: run all math fixes across project root, then start Hugo server.

    This script intentionally omits CLI parameters to keep usage simple. It assumes
    the project root is the parent directory of the `tool/` folder.
    """
    tool_dir = Path(__file__).parent.resolve()
    root = tool_dir.parent.resolve()
    print('Project root:', root)

    ok = True

    # 1) fix_md_math.py
    script = tool_dir / 'fix_md_math.py'
    if script.exists():
        print('\n==> Running fix_md_math.py across project')
        cmd_args = ['--root', str(root)]
        ok = run_python_script(script, cmd_args) and ok
    else:
        print('Missing script:', script)
        ok = False

    # 2) replace_square_to_dollar.py
    script = tool_dir / 'replace_square_to_dollar.py'
    if script.exists():
        print('\n==> Running replace_square_to_dollar.py across project')
        cmd_args = ['--root', str(root)]
        ok = run_python_script(script, cmd_args) and ok
    else:
        print('Missing script:', script)
        ok = False

    # 3) fix_backslashes_in_math.py on all md files
    script = tool_dir / 'fix_backslashes_in_math.py'
    if script.exists():
        files = find_md_files(root)
        print(f"\n==> Found {len(files)} .md files, running backslash fixer on each")
        for f in files:
            ok = run_python_script(script, [str(f)]) and ok
    else:
        print('Missing script:', script)
        ok = False

    # 4) start hugo server (choose an available port starting from 1313)
    print('\n==> Starting Hugo server (will run in foreground, Ctrl+C to stop)')
    def find_free_port(start=1313, end=1400):
        for p in range(start, end + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    s.bind(('127.0.0.1', p))
                    return p
                except OSError:
                    continue
        return None

    port = find_free_port(1313, 1400)
    if port is None:
        print('No free port found in range 1313-1400; aborting Hugo start.')
        sys.exit(1)
    print(f'Chosen free port: {port}')
    rc = start_hugo_server(root, port=port, bind='127.0.0.1', drafts=True)
    if rc != 0:
        print('\nHugo exited with code', rc)
        sys.exit(rc)

    if ok:
        print('\nAll steps completed successfully.')
    else:
        print('\nOne or more processing steps failed. See logs above.')


if __name__ == '__main__':
    main()
