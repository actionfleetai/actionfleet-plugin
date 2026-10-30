#!/usr/bin/env python3
"""Ask a real Codex what it loads from each package: its one MCP server, skills, the onboarding skill and its icon.
Installs into a throwaway CODEX_HOME only; never signs in or connects to a server."""
import argparse
import json
import os
from pathlib import Path
import select
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from catalog import profiles  # noqa: E402


def read_plugins(names, codex='codex', root=ROOT, install=(), timeout=60):
    """plugin/read for each name, through `codex app-server`'s JSON-RPC on stdio. Codex reports an onboarding skill
    only for an installed plugin, so the names in install are installed first."""
    with tempfile.TemporaryDirectory() as home:
        env = {**os.environ, 'CODEX_HOME': home}
        for command in [['plugin', 'marketplace', 'add', str(root)]] + [['plugin', 'add', name + '@actionfleet'] for name in install]:
            subprocess.run([codex, *command], env=env, cwd=home, check=True, capture_output=True, timeout=timeout)
        server = subprocess.Popen([codex, 'app-server'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, text=True, cwd=home, env=env)
        try:
            def call(id, method, params):
                server.stdin.write(json.dumps({'jsonrpc': '2.0', 'id': id, 'method': method, 'params': params}) + '\n')
                server.stdin.flush()
                end = time.time() + timeout
                while (left := end - time.time()) > 0 and select.select([server.stdout], [], [], left)[0]:
                    line = server.stdout.readline()
                    if not line:
                        break
                    message = json.loads(line)
                    if message.get('id') == id:
                        if 'error' in message:
                            raise ValueError(f"{method}: {message['error'].get('message')}")
                        return message['result']
                raise TimeoutError(f'{method}: no answer from codex app-server')

            call(0, 'initialize', {'clientInfo': {'name': 'actionfleet-plugin-check', 'version': '0'}})
            marketplace = str(Path(root) / '.agents/plugins/marketplace.json')
            return {name: call(i, 'plugin/read', {'marketplacePath': marketplace, 'pluginName': name})['plugin']
                    for i, name in enumerate(names, start=1)}
        finally:
            server.kill()


def problems(name, plugin, installed=True):
    found = []
    servers = set(plugin.get('mcpServers') or [])
    if servers != {name}:
        found.append(f'{name}: Codex loads MCP servers {sorted(servers)}, expected {[name]}')
    if installed and (plugin.get('onboardingSkill') or {}).get('name') != name + ':setup':
        found.append(f'{name}: Codex has no {name}:setup onboarding skill')
    skills = {s['name'] for s in plugin.get('skills') or []}
    for skill in ('setup', 'work-task', 'coordinate'):
        if f'{name}:{skill}' not in skills:
            found.append(f'{name}: Codex does not load skill {skill}')
    interface = (plugin.get('summary') or {}).get('interface') or {}
    for key in ('logo', 'composerIcon'):
        if not str(interface.get(key) or '').endswith(f'/packages/{name}/assets/icon.png'):
            found.append(f'{name}: Codex resolves no {key} to the package icon')
    return found


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex', default='codex', help='Codex CLI command (default: codex on PATH)')
    args = parser.parse_args()
    names = [p['name'] for p in profiles()]
    installable = [p['name'] for p in profiles() if p['installable']]
    plugins = read_plugins(names, args.codex, install=installable)
    found = [line for name in names for line in problems(name, plugins[name], name in installable)]
    for name in names:
        print(f"{name}: MCP {sorted(plugins[name].get('mcpServers') or [])}, "
              f"onboarding {(plugins[name].get('onboardingSkill') or {}).get('name')}")
    if found:
        parser.exit(1, '\n'.join(found) + '\n')
