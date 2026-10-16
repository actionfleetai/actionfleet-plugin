#!/usr/bin/env python3
"""Generate complete portable/OpenAI/Claude packages from one public source."""
import argparse
import json
from pathlib import Path
import shutil
from urllib.parse import urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'plugins/actionfleet'
FILES = {'plugin.json', 'skills/setup/SKILL.md', 'skills/work-task/SKILL.md',
         'skills/coordinate/SKILL.md', 'skills/work-task/references/tool-guide.md'}


def endpoint(value):
    parsed = urlsplit(value)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment or parsed.path.rstrip('/') != '/mcp'):
        raise ValueError('Supply the verified HTTPS /mcp endpoint without credentials or query parameters.')
    _ = parsed.port  # Reject malformed ports.
    return value.rstrip('/')


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def build(url, output, source=SOURCE, *, name=None, display_name=None):
    url = endpoint(url)
    actual = {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
    if actual != FILES or any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('Plugin source must contain only the reviewed public manifest and skills, with no symlinks.')
    output = Path(output)
    if output.exists():
        raise ValueError('Choose a new output directory; existing files are never replaced.')
    manifest = json.loads((source / 'plugin.json').read_text())
    if name:
        if name not in {'actionfleet', 'actionfleet-dev'}:
            raise ValueError('Unknown plugin identity.')
        manifest['name'] = name
    name = manifest['name']
    if display_name:
        manifest['extensions']['com.openai']['interface']['displayName'] = display_name
    plugin = output / 'plugins/actionfleet'
    shutil.copytree(source, plugin)
    write(plugin / 'plugin.json', manifest)
    shutil.copyfile(ROOT / 'LICENSE', plugin / 'LICENSE')
    public_url = url[:-4] + '/public/mcp'
    write(plugin / 'mcp.json', {
        '$schema': 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json',
        'mcpServers': {
            name + '-setup': {'type': 'streamable-http', 'url': public_url,
                                 'extensions': {'com.openai': {'auth': {'type': 'none'}}}},
            name: {'type': 'streamable-http', 'url': url,
                            'extensions': {'com.openai': {'auth': {'type': 'oauth', 'client': {'mode': 'dcr'}}}}},
        },
    })
    write(plugin / '.mcp.json', {'mcpServers': {
        name + '-setup': {'type': 'http', 'url': public_url},
        name: {'type': 'http', 'url': url},
    }})
    write(plugin / '.claude-plugin/plugin.json', {k: manifest[k] for k in
          ('name', 'version', 'description', 'author', 'homepage', 'repository', 'license', 'keywords')})
    write(plugin / '.cursor-plugin/plugin.json', {
        **{k: manifest[k] for k in ('name', 'version', 'description', 'author', 'homepage', 'repository', 'license', 'keywords')},
        'displayName': display_name or manifest['extensions']['com.openai']['interface']['displayName'],
    })
    write(output / '.agents/plugins/marketplace.json', {
        'name': 'actionfleet', 'interface': {'displayName': 'Action Fleet Plugins'},
        'plugins': [{'name': name, 'source': {'source': 'local', 'path': './plugins/actionfleet'},
                     'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}, 'category': 'Productivity'}],
    })
    write(output / '.claude-plugin/marketplace.json', {
        'name': 'actionfleet', 'owner': {'name': 'Action Fleet'},
        'description': 'Action Fleet harness setup and durable task coordination.',
        'plugins': [{'name': name, 'source': './plugins/actionfleet', 'description': manifest['description']}],
    })
    archive = output / f"{name}-{manifest['version']}.zip"
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for file in sorted(p for p in plugin.rglob('*') if p.is_file()):
            info = zipfile.ZipInfo('actionfleet/' + file.relative_to(plugin).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, file.read_bytes())
    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mcp-url', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        print(build(args.mcp_url, args.output))
    except (ValueError, OSError) as error:
        parser.exit(1, 'Package build refused; verify endpoint, reviewed source and a fresh output directory.\n')
