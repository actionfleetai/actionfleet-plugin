#!/usr/bin/env python3
"""The tools the public skills name, for checks against the server's catalog (server-tools.json and the live public bootstrap)."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'plugins/actionfleet'
SNAPSHOT = ROOT / 'server-tools.json'
# actionfleet/1 tools removed without aliases. A skill naming one sends agents to a tool that does not exist.
REMOVED = ('bootstrap_harness', 'get_protocol_schema', 'get_ship_identity', 'submit_ship_command', 'submit_ship_commands',
           'submit_task_command', 'submit_task_commands', 'get_ship_group', 'get_task_group', 'get_ship_changesets',
           'get_task_changesets', 'register_changeset', 'record_changeset_output', 'get_changeset_outputs', 'get_ship_outputs',
           'get_task_outputs', 'list_tasks', 'get_task', 'list_games', 'get_game_download_links', 'get_billing_status')
# A backticked name starting with one of these reads as a tool; argument names that start the same way are listed apart.
TOOL_WORDS = {'add', 'block', 'bootstrap', 'crew', 'dispatch', 'get', 'list', 'new', 'pause', 'read', 'record', 'register',
              'release', 'report', 'request', 'send', 'set', 'stop', 'submit', 'update', 'whoami'}
NOT_TOOLS = {'request_id', 'report_id'}
# Code Mode's own discovery tools: every Code Mode server has them, so the Fleet catalog does not list them.
CODE_MODE = {'get_tags', 'search', 'get_schema', 'execute'}


def texts(source=SOURCE):
    return {p.relative_to(source).as_posix(): p.read_text() for p in sorted(source.rglob('*.md'))}


def named_tools(text):
    """Tool names a text sends an agent to: `name(...)` calls and backticked tool-like names."""
    called = set(re.findall(r'`([a-z]+(?:_[a-z]+)+)\(', text))
    named = {n for n in re.findall(r'`([a-z]+(?:_[a-z]+)*)`', text) if n.split('_')[0] in TOOL_WORDS}
    return (called | named) - NOT_TOOLS


def skill_tools(source=SOURCE):
    """Fleet tools the skills name (Code Mode's discovery tools aside)."""
    return set().union(*(named_tools(text) for text in texts(source).values())) - CODE_MODE


def removed_named(source=SOURCE):
    return sorted({name for text in texts(source).values() for name in REMOVED if re.search(rf'\b{name}\b', text)})


def snapshot(path=SNAPSHOT):
    data = json.loads(path.read_text())
    if data.get('protocol') != 'actionfleet/2' or not data.get('tools') or not data.get('plugin_minimum'):
        raise ValueError('server-tools.json needs protocol actionfleet/2, tools and plugin_minimum.')
    return data


def version(value):
    """`2026.1024.1` -> (2026, 1024, 1); None for anything else."""
    match = re.fullmatch(r'(\d{4})\.(\d{3,4})\.(\d+)', value or '')
    return tuple(int(part) for part in match.groups()) if match else None


if __name__ == '__main__':
    print(json.dumps({'skill_tools': sorted(skill_tools()), 'removed_named': removed_named()}, indent=2))
