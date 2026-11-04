#!/usr/bin/env python3
"""Los Angeles date/build releases, encoded as ordered three-field plugin versions.

release.json names the newest release. Each plugin keeps the version of the release where its package last changed,
so a host offers an update only for plugins that changed. `bump` allocates a release only when a package changed since
the commit that set release.json, and `check` refuses packages that changed without one.
"""
import argparse
from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
import subprocess
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ZONE = 'America/Los_Angeles'
# What hosts install: the generated packages and the three marketplace catalogs.
SERVED = ('packages', '.agents/plugins/marketplace.json', '.claude-plugin/marketplace.json',
          '.cursor-plugin/marketplace.json')
VERSION = re.compile(r'(\d{4})\.([1-9]\d{2,3})\.([1-9]\d*)')


def identity(value):
    day = date.fromisoformat(value['date'])
    number = value['build']
    if (day.isoformat() != value['date'] or type(number) is not int or number < 1
            or value.get('timezone') != ZONE):
        raise ValueError('Use an ISO release date, positive integer build and Los Angeles timezone.')
    return {**value, 'version': f'{day.year}.{day.month * 100 + day.day}.{number}',
            'label': f'{day.year}.{day.month}.{day.day} ({number})'}


def parse(version):
    """The release identity a version names: 2026.105.2 is 5 January 2026, build 2."""
    match = VERSION.fullmatch(version)
    if not match:
        raise ValueError(f'Not a date/build version: {version!r}.')
    year, middle, build = map(int, match.groups())
    try:
        found = identity({'date': date(year, middle // 100, middle % 100).isoformat(), 'build': build, 'timezone': ZONE})
    except ValueError:
        raise ValueError(f'Not a date/build version: {version!r}.') from None
    return found


def order(version):
    return tuple(int(part) for part in parse(version)['version'].split('.'))


def read_release(path=ROOT / 'release.json'):
    return identity(json.loads(path.read_text()))


def plugin_version(name='actionfleet', root=ROOT):
    return json.loads((root / 'plugins' / name / 'plugin.json').read_text())['version']


def next_release(value, now=None):
    old = identity(value)
    now = datetime.now(timezone.utc) if now is None else now
    if now.tzinfo is None:
        raise ValueError('Release clock must have an explicit timezone.')
    day = now.astimezone(ZoneInfo(ZONE)).date()
    previous = date.fromisoformat(old['date'])
    if day < previous:
        raise ValueError('Release date cannot move backwards. Fetch/rebase main and check the clock.')
    return {'date': day.isoformat(), 'build': old['build'] + 1 if day == previous else 1, 'timezone': ZONE}


def packages():
    """Each plugin's generated packages: the core plugin builds one per profile, each add-on one."""
    from build import ADDONS
    from catalog import profiles
    return {'actionfleet': [p['name'] for p in profiles()], **{name: [name] for name in ADDONS}}


def changed(old, new, names):
    """The plugins whose package files differ between two {path: bytes} maps, in `names` order.

    >>> changed({'packages/a/x': b'1', 'packages/b/x': b'1'}, {'packages/a/x': b'2', 'packages/b/x': b'1'},
    ...         {'core': ['a'], 'b': ['b']})
    ['core']
    >>> changed({}, {'packages/c/x': b'1'}, {'c': ['c']})
    ['c']
    """
    def package(files, name):
        return {path: data for path, data in files.items() if path.startswith(f'packages/{name}/')}
    return [plugin for plugin, names_ in names.items() if any(package(old, n) != package(new, n) for n in names_)]


def git(*args, data=None):
    return subprocess.run(['git', '-C', str(ROOT), *args], input=data, capture_output=True, check=True).stdout


def files_at(commit):
    """The served files at a commit, as {path: bytes}."""
    names = [n for n in git('ls-tree', '-r', '-z', '--name-only', commit, '--', *SERVED).decode().split('\0') if n]
    out = git('cat-file', '--batch', data=''.join(f'{commit}:{name}\n' for name in names).encode())
    files, at = {}, 0
    for name in names:
        end = out.index(b'\n', at)
        size = int(out[at:end].split()[2])
        files[name] = out[end + 1:end + 1 + size]
        at = end + 2 + size
    return files


def release_commits():
    """The commits that set release.json, newest first."""
    return git('log', '--format=%H', '--', 'release.json').decode().split()


def bump(now=None):
    """Allocate the next release for the plugins whose packages changed; None when none did."""
    from catalog import generated, sync
    current = {path: data for path, data in generated().items() if path.startswith('packages/')}
    plugins = changed(files_at(release_commits()[0]), current, packages())
    if not plugins:
        return None
    path = ROOT / 'release.json'
    value = next_release(json.loads(path.read_text()), now)
    path.write_text(json.dumps(value, indent=2) + '\n')
    version = identity(value)['version']
    for name in plugins:
        manifest_path = ROOT / 'plugins' / name / 'plugin.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['version'] = version
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    sync()
    return {**identity(value), 'plugins': plugins}


def check():
    """The release HEAD serves and the plugins it updates; refuses a package that changed without a release."""
    commits = release_commits()
    head = git('rev-parse', 'HEAD').decode().strip()
    release = identity(json.loads(git('show', 'HEAD:release.json')))
    served = files_at('HEAD')
    if commits[0] != head and files_at(commits[0]) != served:
        raise ValueError(f"Packages changed after release {release['version']} without a new one; run scripts/land.py.")
    previous = commits[1] if len(commits) > 1 else None
    if previous:
        before = identity(json.loads(git('show', f'{previous}:release.json')))
        if order(release['version']) <= order(before['version']):
            raise ValueError(f"Release {release['version']} must be newer than {before['version']}.")
    plugins = changed(files_at(previous) if previous else {}, served, packages())
    if not plugins:
        raise ValueError(f"Release {release['version']} changes no package; drop its release.json change.")
    stale = [name for name in plugins if plugin_version(name) != release['version']]
    if stale:
        raise ValueError(f"Changed plugins must carry release {release['version']}: {', '.join(stale)}.")
    return release, plugins


def notes(release, plugins):
    """The release's plugin table, for its notes."""
    names = ['actionfleet', *[name for name in packages() if name != 'actionfleet']]
    rows = [f"| {name} | {plugin_version(name)} | {'updated' if name in plugins else 'unchanged'} |" for name in names]
    return '\n'.join(['| Plugin | Version | In this release |', '| --- | --- | --- |', *rows])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('command', choices=['info', 'bump', 'check'], nargs='?', default='info')
    parser.add_argument('--field', choices=['version', 'label'])
    parser.add_argument('--notes', action='store_true', help='check: print the plugin table for release notes')
    args = parser.parse_args()
    try:
        if args.command == 'bump':
            result = bump()
            print(json.dumps(result, indent=2) if result else 'No package changed since the last release; nothing to release.')
        elif args.command == 'check':
            release, plugins = check()
            print(notes(release, plugins) if args.notes else
                  f"Release {release['version']}: " + (', '.join(plugins) + ' updated' if plugins else 'no package changes since it'))
        else:
            result = read_release()
            print(result[args.field] if args.field else json.dumps(result, indent=2))
    except (ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'refused: {error}\n')
