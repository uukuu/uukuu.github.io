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
import os
import uuid
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


def get_current_branch(root: Path) -> str:
    try:
        p = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=str(root), capture_output=True, text=True, check=False)
        return p.stdout.strip()
    except Exception:
        return ''


def normalize_public_case(public: Path, dry_run: bool = False):
    """Normalize all file and directory names under `public` to lowercase.

    This walks the tree, detects any paths that would collide when lowercased
    and then renames items bottom-up using a temporary name to ensure Git and
    the filesystem notice case-only changes on case-insensitive systems.
    """
    print('Normalizing case of files under', public)
    # Collect all existing entries (files and directories)
    entries = [p for p in public.rglob('*') if p.exists()]
    # Map relative path -> lowercased relative path
    rel_map = {}
    for p in entries:
        rel = p.relative_to(public)
        rel_map[rel] = Path(str(rel).lower())

    # Detect collisions: two different rel paths mapping to same lowercased path
    lower_map = {}
    for rel, lower in rel_map.items():
        lower_map.setdefault(str(lower), []).append(rel)
    collisions = {k: v for k, v in lower_map.items() if len(v) > 1}
    if collisions:
        print('ERROR: Case-normalization would cause collisions:')
        for k, srcs in collisions.items():
            print('  ->', k, ' <- ', ', '.join(map(str, srcs)))
        raise RuntimeError('Case-normalization collisions detected; aborting')

    # Sort by path depth (deepest first) so we rename children before parents
    sorted_rels = sorted(rel_map.keys(), key=lambda r: len(r.parts), reverse=True)

    for rel in sorted_rels:
        cur = public / rel
        desired = public / rel_map[rel]
        # Skip if already the same string (no case change needed)
        if str(rel) == str(rel_map[rel]):
            continue

        print(f'Case-fix: {cur} -> {desired}')
        if dry_run:
            continue

        parent = cur.parent
        # create unique temporary name to avoid collisions on case-insensitive FS
        tmp_name = rel.name + '__CASEFIX__' + uuid.uuid4().hex
        tmp = parent / tmp_name

        # Ensure destination parent exists
        desired.parent.mkdir(parents=True, exist_ok=True)

        # Perform rename via temporary name
        os.rename(str(cur), str(tmp))
        os.rename(str(tmp), str(desired))

    print('Case normalization finished')


def push_source_to_branch(root: Path, branch: str = 'blog-hugo-v2', auto_commit: bool = False, dry_run: bool = False) -> int:
    """Push current HEAD (source tree) to a remote branch (force-with-lease).

    This pushes the repository's current HEAD to `origin:branch` without
    checking out or modifying the working copy. It uses --force-with-lease to
    reduce accidental overwrites.
    """
    origin = get_origin_url(root)
    if not origin:
        print('Could not determine origin URL for repository. Is this a git repository with remote "origin"?')
        return 3

    cur = get_current_branch(root)
    if not cur:
        print('Could not determine current branch (git rev-parse failed).')
        return 4

    # If requested, auto-commit any working tree changes before pushing source
    # if auto_commit:
    p = subprocess.run(['git', 'status', '--porcelain'], cwd=str(root), capture_output=True, text=True)
    if p.stdout.strip():
        print('Auto-commit enabled: detected uncommitted changes:')
        print(p.stdout)
        if dry_run:
            print('Dry-run: would run: git add -A && git commit -m "Auto commit before deploy"')
        else:
            print('Staging all changes and creating auto-commit')
            run(['git', 'add', '-A'], cwd=str(root))
            try:
                run(['git', 'commit', '-m', 'Auto commit before deploy'], cwd=str(root))
            except subprocess.CalledProcessError:
                print('Auto-commit failed (maybe no changes to commit after staging)')
    else:
        print('Auto-commit enabled: no changes detected')

    print(f'Pushing source (HEAD -> {branch}) to origin using --force-with-lease (from branch: {cur})')
    try:
        # push current HEAD to target branch on origin using safer force
        run(['git', 'push', '--force-with-lease', 'origin', f'HEAD:{branch}'], cwd=str(root))
    except subprocess.CalledProcessError as e:
        print('Failed to push source to', branch, e)
        return 5
    print('Source push complete')
    return 0




def push_public_to_gh_pages(root: Path, branch='gh-pages', incremental: bool = False, dry_run: bool = False):
    public = root / 'public'
    if not public.exists():
        print('public/ directory not found. Build first.')
        return 2

    origin = get_origin_url(root)
    if not origin:
        print('Could not determine origin URL for repository. Is this a git repository with remote "origin"?')
        return 3

    # Prepare for deploy
    print('Preparing to push public/ to', origin, branch)
    gitdir = public / '.git'

    if incremental:
        # Attempt incremental deploy: preserve or create a git repo in public/ and only push changes.
        if gitdir.exists():
            print('Using existing git repository in public/ for incremental deploy')
            run(['git', 'add', '--all'], cwd=str(public))
            p = subprocess.run(['git', 'status', '--porcelain'], cwd=str(public), capture_output=True, text=True)
            if not p.stdout.strip():
                print('No changes detected in public/. Nothing to push.')
                return 0
            run(['git', 'commit', '-m', 'Deploy site: automated incremental deploy'], cwd=str(public))
            print('Pushing incremental changes to origin', branch)
            run(['git', 'push', 'origin', f'HEAD:{branch}'], cwd=str(public))
            print('Incremental push complete')
            return 0
        else:
            print('Initializing git in public/ for incremental deploy')
            run(['git', 'init'], cwd=str(public))
            run(['git', 'remote', 'add', 'origin', origin], cwd=str(public))
            p = subprocess.run(['git', 'ls-remote', '--heads', 'origin', branch], cwd=str(public), capture_output=True)
            if p.returncode == 0 and p.stdout.strip():
                run(['git', 'fetch', 'origin', branch], cwd=str(public))
                run(['git', 'checkout', '-B', branch, f'origin/{branch}'], cwd=str(public))
            else:
                run(['git', 'checkout', '-B', branch], cwd=str(public))
                # Normalize path case before staging
                normalize_public_case(public, dry_run=dry_run)
                run(['git', 'add', '--all'], cwd=str(public))
            p = subprocess.run(['git', 'status', '--porcelain'], cwd=str(public), capture_output=True, text=True)
            if not p.stdout.strip():
                print('No changes detected in public/. Nothing to push.')
                return 0
            run(['git', 'commit', '-m', 'Deploy site: automated incremental deploy'], cwd=str(public))
            run(['git', 'push', '--force-with-lease', 'origin', f'HEAD:{branch}'], cwd=str(public))
            print('Initial incremental push complete')
            return 0

    # Non-incremental (legacy) behavior: fresh deploy by re-initializing repo in public/
    if gitdir.exists():
        print('Removing existing .git in public/ to ensure clean deploy')
        shutil.rmtree(gitdir)

    run(['git', 'init'], cwd=str(public))
    run(['git', 'checkout', '-B', branch], cwd=str(public))
    # Normalize path case before staging
    normalize_public_case(public, dry_run=dry_run)
    run(['git', 'add', '--all'], cwd=str(public))
    run(['git', 'commit', '-m', 'Deploy site: automated deploy by deploy_github_pages.py'], cwd=str(public))
    run(['git', 'remote', 'add', 'origin', origin], cwd=str(public))
    print('Pushing to origin', branch, '(this will force-update remote branch)')
    run(['git', 'push', '-f', 'origin', f'HEAD:{branch}'], cwd=str(public))
    print('Push complete')
    return 0


def main():
    p = argparse.ArgumentParser(description='Run math fixes, build Hugo, and optionally push public/ to gh-pages')
    p.add_argument('--push', action='store_true', help='After building, push public/ to origin gh-pages (force).')
    p.add_argument('--incremental', action='store_true', help='When used with --push, attempt an incremental deploy that preserves public/.git and only pushes changes.')
    p.add_argument('--auto-commit', action='store_true', help='Automatically stage and commit local changes before pushing source to blog-hugo-v2')
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
        rc = push_public_to_gh_pages(root, incremental=args.incremental, dry_run=args.dry_run)
        if rc != 0:
            print('Push of public/ failed, aborting source push.')
            sys.exit(rc)

        # Also push the repository source to blog-hugo-v2 branch
        src_rc = push_source_to_branch(root, branch='blog-hugo-v2', auto_commit=args.auto_commit, dry_run=args.dry_run)
        if src_rc != 0:
            print('Source push failed with code', src_rc)
            sys.exit(src_rc)

        sys.exit(0)

    print('\nBuild completed. public/ is ready. To push to GitHub Pages, run with --push')


if __name__ == '__main__':
    main()
