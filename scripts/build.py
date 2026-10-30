#!/usr/bin/env python3
"""Generate complete Codex/Claude/Cursor packages from one public source."""
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
ICON = 'assets/icon.png'  # Each profile's render of icons/ship.svg (scripts/icons.py).


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


def build(url, output, source=SOURCE, *, name=None, display_name=None, icon=None):
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
    # Codex reads a root plugin.json before .codex-plugin/plugin.json and loads no MCP servers from it (0.162), so the
    # portable manifest stays the source only and each host gets its native manifest.
    (plugin / 'plugin.json').unlink()
    shutil.copyfile(ROOT / 'LICENSE', plugin / 'LICENSE')
    (plugin / ICON).parent.mkdir()
    shutil.copyfile(icon or ROOT / 'icons' / f'{name}.png', plugin / ICON)
    # One server per package: each connection to the authorized MCP is its own crew device, and it serves the start
    # tools (bootstrap, get_guide) once signed in, so the anonymous /public/mcp stays server-side.
    write(plugin / 'mcp.json', {
        '$schema': 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json',
        'mcpServers': {
            name: {'type': 'streamable-http', 'url': url,
                   'extensions': {'com.openai': {'auth': {'type': 'oauth', 'client': {'mode': 'dcr'}}}}},
        },
    })
    write(plugin / '.mcp.json', {'mcpServers': {name: {'type': 'http', 'url': url}}})
    common = {k: manifest[k] for k in ('name', 'version', 'description', 'author', 'homepage', 'repository', 'license', 'keywords')}
    openai = manifest['extensions']['com.openai']
    write(plugin / '.codex-plugin/plugin.json', {
        **common, 'skills': './skills/', 'mcpServers': './.mcp.json',
        'interface': {**openai['interface'], 'composerIcon': './' + ICON, 'logo': './' + ICON},
        'extensions': {'com.openai': {'onboardingSkill': openai['onboardingSkill']}},
    })
    # Claude Code ignores icon; Anthropic's directory reads it for the listing.
    write(plugin / '.claude-plugin/plugin.json', {**common, 'icon': './' + ICON})
    write(plugin / '.cursor-plugin/plugin.json', {**common, 'displayName': openai['interface']['displayName'], 'logo': ICON})
    write(output / '.agents/plugins/marketplace.json', {
        'name': 'actionfleet', 'interface': {'displayName': 'Actionfleet Plugins'},
        'plugins': [{'name': name, 'source': {'source': 'local', 'path': './plugins/actionfleet'},
                     'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}, 'category': 'Productivity'}],
    })
    write(output / '.claude-plugin/marketplace.json', {
        'name': 'actionfleet', 'owner': {'name': 'Actionfleet'},
        'description': 'Actionfleet harness setup and durable task coordination.',
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
