#!/usr/bin/env python3
"""Build tracked, reproducible marketplaces; never install or authenticate a host."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import zipfile

from build import ROOT, build, endpoint

CATALOGS = ('.agents/plugins/marketplace.json', '.claude-plugin/marketplace.json',
            '.cursor-plugin/marketplace.json')


def profiles(path=ROOT / 'profiles.json'):
    data = json.loads(path.read_text())
    rows = data['profiles']
    if data.get('schema_version') != 1 or len(rows) != 2:
        raise ValueError('Expected explicit dev and prod profiles.')
    for channel, name in [('dev', 'actionfleet-dev'), ('prod', 'actionfleet')]:
        found = [p for p in rows if p['channel'] == channel]
        if len(found) != 1 or found[0]['name'] != name or type(found[0]['installable']) is not bool:
            raise ValueError('Profile identities and availability must be explicit.')
    if len({endpoint(p['mcp_url']) for p in rows}) != 2:
        raise ValueError('Dev and production must use different origins.')
    if len({p['mcp_url'].rsplit('/', 1)[0] for p in rows}) != 2:
        raise ValueError('Dev and production must use different origins.')
    for p in rows:
        if '---' in p['mcp_url'] or p['protocol'] != 'actionfleet/1':
            raise ValueError('Use stable service endpoints and an explicit supported protocol.')
    return rows


def encoded(value):
    return (json.dumps(value, indent=2) + '\n').encode()


def generated(rows=None):
    rows = profiles() if rows is None else rows
    files = {}
    entries = []
    for p in rows:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / 'package'
            build(p['mcp_url'], package, name=p['name'], display_name=p['display_name'])
            root = package / 'plugins/actionfleet'
            meta = {**p, 'plugin_version': json.loads((root / 'plugin.json').read_text())['version']}
            files[f"packages/{p['name']}/skills/setup/references/installation.json"] = encoded(meta)
            for file in sorted(root.rglob('*')):
                if file.is_file():
                    files[f"packages/{p['name']}/{file.relative_to(root).as_posix()}"] = file.read_bytes()
        entries.append({'name': p['name'], 'source': './packages/' + p['name'],
                        'description': 'Action Fleet task coordination: ' + p['display_name'],
                        'version': meta['plugin_version']})
    files[CATALOGS[0]] = encoded({
        'name': 'actionfleet', 'interface': {'displayName': 'Action Fleet Plugins'},
        'plugins': [{'name': e['name'], 'source': {'source': 'local', 'path': e['source']},
                     'policy': {'installation': 'AVAILABLE' if p['installable'] else 'NOT_AVAILABLE',
                                'authentication': 'ON_INSTALL'}, 'category': 'Productivity'}
                    for p, e in zip(rows, entries)],
    })
    active = [e for p, e in zip(rows, entries) if p['installable']]
    common = {'name': 'actionfleet', 'owner': {'name': 'Action Fleet'},
              'description': 'Action Fleet harness setup and durable task coordination.', 'plugins': active}
    files[CATALOGS[1]] = encoded(common)
    files[CATALOGS[2]] = encoded(common)
    return files


def sync(check=False):
    files = generated()
    for name in files:
        path = ROOT / name
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
            raise ValueError('Generated paths must not be symlinks.')
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'packages').rglob('*') if p.is_file()}
    expected = set(files) - set(CATALOGS)
    if actual - expected:
        raise ValueError('Unexpected generated package files; inspect and remove explicitly.')
    stale = [name for name, data in files.items()
             if not (ROOT / name).is_file() or (ROOT / name).read_bytes() != data]
    if check:
        if stale:
            raise ValueError('Generated marketplace is stale: ' + ', '.join(stale))
    else:
        for name, data in files.items():
            path = ROOT / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    return files


def archives(output):
    files = sync(check=True)
    output.mkdir(parents=True, exist_ok=False)
    sums = []
    for p in profiles():
        if not p['installable']:
            continue
        prefix = f"packages/{p['name']}/"
        version = json.loads(files[prefix + 'plugin.json'])['version']
        path = output / f"{p['name']}-{version}.zip"
        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for name, data in sorted(files.items()):
                if name.startswith(prefix):
                    info = zipfile.ZipInfo(p['name'] + '/' + name[len(prefix):], date_time=(1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    z.writestr(info, data)
        sums.append(sha256(path.read_bytes()).hexdigest() + '  ' + path.name)
    (output / 'SHA256SUMS').write_text('\n'.join(sums) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--archives', type=Path)
    args = parser.parse_args()
    sync(check=args.check or args.archives is not None)
    if args.archives:
        archives(args.archives)
