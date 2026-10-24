import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from release_version import read_release
from skills import CODE_MODE, named_tools, removed_named, skill_tools, snapshot, texts, version


class SkillTests(unittest.TestCase):
    """The plugin stays thin and in sync: the MCP is the integration, and the server's guides win."""

    def test_skills_name_only_tools_the_server_serves(self):
        tools = set(snapshot()['tools'])
        self.assertTrue(skill_tools())
        self.assertEqual(skill_tools() - tools, set(), 'A skill names a tool the server does not serve; refresh server-tools.json or the skill.')
        self.assertEqual(removed_named(), [], 'A skill names a removed actionfleet/1 tool.')
        self.assertEqual(named_tools('Call `get_task(...)` then `list_tasks` with `request_id`.'), {'get_task', 'list_tasks'})
        self.assertTrue(CODE_MODE.isdisjoint(tools))

    def test_every_skill_defers_to_the_server(self):
        for name, text in texts().items():
            if name.endswith('SKILL.md'):
                self.assertIn('get_guide', text, name)
        setup = (ROOT / 'plugins/actionfleet/skills/setup/SKILL.md').read_text()
        for needed in ('plugin_version', 'references/installation.json', 'plugin.status', 'source of truth'):
            self.assertIn(needed, setup)

    def test_this_release_meets_the_server_minimum_it_was_written_for(self):
        release = read_release()['version']
        manifest = json.loads((ROOT / 'plugins/actionfleet/plugin.json').read_text())['version']
        self.assertEqual(release, manifest)
        self.assertGreaterEqual(version(release), version(snapshot()['plugin_minimum']))
        self.assertEqual(version('2026.101.3'), (2026, 101, 3))
        self.assertIsNone(version('v1'))
