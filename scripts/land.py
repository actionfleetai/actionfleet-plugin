#!/usr/bin/env python3
"""Prepare this branch to land on main: rebase, check new commit messages, release what changed, run the checks.

It pushes nothing. When it prints `ready`, recheck the Ship's claim and STOP, then `git push origin HEAD:main`; CI
publishes the release. A release commit is added only when a package changed, and is redone if main moves.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COMMIT = ROOT / 'plugins/commit-messages/skills/commit-messages/scripts/commit.py'
RELEASED = ['release.json', 'plugins', 'packages', '.agents/plugins', '.claude-plugin', '.cursor-plugin']
PASSES = 3


def run(*args, capture=False):
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=capture)
    if result.returncode:
        raise SystemExit(f"refused: {' '.join(args[:3])} failed" + (f': {result.stderr.strip()}' if capture else ''))
    return result.stdout.strip() if capture else None


def head(ref='HEAD'):
    return run('git', 'rev-parse', ref, capture=True)


def main():
    if run('git', 'status', '--porcelain', capture=True):
        raise SystemExit('refused: commit or stash your changes first')
    for attempt in range(1, PASSES + 1):
        run('git', 'fetch', '--quiet', 'origin', 'main')
        if subprocess.run(['git', 'rebase', '--quiet', 'origin/main'], cwd=ROOT).returncode:
            subprocess.run(['git', 'rebase', '--abort'], cwd=ROOT)
            raise SystemExit('refused: the rebase onto origin/main conflicts; resolve it, then run land.py again')
        base = head('origin/main')
        # Commits already on a remote branch are published; fix those forward instead of rewording them.
        run(sys.executable, '-I', str(COMMIT), 'check', '--public', '--range', 'HEAD --not --remotes')
        bumped = run(sys.executable, 'scripts/release_version.py', 'bump', capture=True)
        released = None
        if bumped.startswith('{'):
            release = json.loads(bumped)
            run('git', 'add', '--all', '--', *RELEASED)
            run('git', 'commit', '--quiet', '-m', f"chore(release): v{release['version']}",
                '-m', 'Updates ' + ', '.join(release['plugins']) + '.')
            released = head()
            print(f"release {release['version']}: {', '.join(release['plugins'])}")
        else:
            print(bumped)
        run(sys.executable, '-m', 'unittest', 'discover', '-q', '-s', 'tests')
        run(sys.executable, 'scripts/catalog.py', '--check')
        run(sys.executable, 'scripts/release_version.py', 'check')
        if shutil.which('claude'):
            for target in [*sorted(str(p) for p in (ROOT / 'packages').iterdir()), '.']:
                run('claude', 'plugin', 'validate', target, '--strict', capture=True)
        else:
            print('note: `claude` is not installed; CI runs strict plugin validation')
        if shutil.which('codex'):
            run(sys.executable, 'scripts/check_codex_package.py', capture=True)
        else:
            print('note: `codex` is not installed; CI runs the Codex package check')
        run('git', 'fetch', '--quiet', 'origin', 'main')
        if head('origin/main') == base:
            print(f'ready: {head()[:12]} on {base[:12]}. Recheck the claim and STOP, then: git push origin HEAD:main')
            return 0
        print(f'main moved during pass {attempt}; preparing again')
        if released and head() == released:
            run('git', 'reset', '--quiet', '--hard', 'HEAD~1')
    raise SystemExit(f'refused: main kept moving for {PASSES} passes; run land.py again')


if __name__ == '__main__':
    sys.exit(main())
