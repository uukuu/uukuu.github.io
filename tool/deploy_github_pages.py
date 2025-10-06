#!/usr/bin/env python3
"""
deploy_github_pages.py

按顺序执行：
  1. fix_md_math.py (转换/修正数学格式)
  2. replace_square_to_dollar.py
  3. fix_backslashes_in_math.py （对所有 md 文件）
  4. hugo --minify 构建站点到 public/
  5. （可选）将 public/ 强制推送到远程 gh-pages 分支（需要传入 --push）

默认只执行前 1-4 步（安全），避免未经授权地强制覆盖远程分支。

用法示例：
  python deploy_github_pages.py        # 运行修复并构建，不推送
  python deploy_github_pages.py --push # 在构建后把 public/ 推送到 origin gh-pages（会覆盖远程）
"""
from pathlib import Path
import subprocess
import sys
import shutil
import argparse


def run(cmd, cwd=None, check=True):
    print('>>>', ' '.join(cmd), '  (cwd=', cwd, ')')
    return subprocess.run(cmd, cwd=cwd, check=check)


def run_python_script(script: Path, args: list):
    cmd = [sys.executable, str(script)] + args
    return run(cmd, cwd=str(script.parent))


def get_origin_url(root: Path):
    try:
        p = subprocess.run(['git', 'config', '--get', 'remote.origin.url'], cwd=str(root), capture_output=True, text=True, check=False)
        url = p.stdout.strip()
        return url
    except Exception:
        return ''


def push_public_to_gh_pages(root: Path, branch='gh-pages'):
    public = root / 'public'
    if not public.exists():
        print('public/ directory not found. Build first.')
        return 2

    origin = get_origin_url(root)
    if not origin:
        print('Could not determine origin URL for repository. Is this a git repository with remote "origin"?')
        return 3

    # Initialize git in public/ and push to branch
    print('Preparing to push public/ to', origin, branch)

    # If public/.git exists, remove it to avoid accidental metadata reuse
    gitdir = public / '.git'
    if gitdir.exists():
        print('Removing existing .git in public/ to ensure clean deploy')
        shutil.rmtree(gitdir)

    run(['git', 'init'], cwd=str(public))
    run(['git', 'checkout', '-B', branch], cwd=str(public))
    run(['git', 'add', '--all'], cwd=str(public))
    # Use a consistent commit message
    run(['git', 'commit', '-m', 'Deploy site: automated deploy by deploy_github_pages.py'], cwd=str(public))
    run(['git', 'remote', 'add', 'origin', origin], cwd=str(public))
    # Force push the branch
    print('Pushing to origin', branch, '(this will force-update remote branch)')
    run(['git', 'push', '-f', 'origin', f'HEAD:{branch}'], cwd=str(public))
    print('Push complete')
    return 0


def main():
    p = argparse.ArgumentParser(description='Run math fixes, build Hugo, and optionally push public/ to gh-pages')
    p.add_argument('--push', action='store_true', help='After building, push public/ to origin gh-pages (force).')
    p.add_argument('--dry-run', action='store_true', help='Run pre-build scripts in dry-run/preview mode; do not write changes or push.')
    args = p.parse_args()

    tool_dir = Path(__file__).parent.resolve()
    root = tool_dir.parent.resolve()

    ok = True

    # 1) fix_md_math.py
    script = tool_dir / 'fix_md_math.py'
    if script.exists():
        print('\n==> Running fix_md_math.py')
        try:
            args_list = ['--root', str(root)]
            if args.dry_run:
                args_list.append('--dry-run')
            run_python_script(script, args_list)
        except subprocess.CalledProcessError as e:
            print('fix_md_math.py failed', e)
            ok = False
    else:
        print('Missing', script)
        ok = False

    # 2) replace_square_to_dollar.py
    script = tool_dir / 'replace_square_to_dollar.py'
    if script.exists():
        print('\n==> Running replace_square_to_dollar.py')
        try:
            args_list = ['--root', str(root)]
            if args.dry_run:
                args_list.append('--dry-run')
            run_python_script(script, args_list)
        except subprocess.CalledProcessError as e:
            print('replace_square_to_dollar.py failed', e)
            ok = False
    else:
        print('Missing', script)
        ok = False

    # 3) fix_backslashes_in_math.py on all md files
    script = tool_dir / 'fix_backslashes_in_math.py'
    if script.exists():
        print('\n==> Running fix_backslashes_in_math.py on all md files')
        # get list of md files
        md_files = list(root.rglob('*.md'))
        for f in md_files:
            try:
                cmd = [sys.executable, str(script), str(f)]
                if args.dry_run:
                    cmd.append('--dry-run')
                run(cmd, cwd=str(tool_dir))
            except subprocess.CalledProcessError as e:
                print('fix_backslashes_in_math failed for', f, e)
                ok = False
    else:
        print('Missing', script)
        ok = False

    if not ok:
        print('\nOne or more pre-build steps failed. Aborting build.')
        sys.exit(1)

    # 4) Hugo build
    print('\n==> Running Hugo build')
    if shutil.which('hugo') is None:
        print('hugo not found in PATH. Please install Hugo and try again.')
        sys.exit(2)
    try:
        run(['hugo', '--minify'], cwd=str(root))
    except subprocess.CalledProcessError as e:
        print('Hugo build failed', e)
        sys.exit(3)

    # 5) Optionally push
    if args.push:
        rc = push_public_to_gh_pages(root)
        sys.exit(rc)

    print('\nBuild completed. public/ is ready. To push to GitHub Pages, run with --push')


if __name__ == '__main__':
    main()
