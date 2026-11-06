import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from catalog import profiles
from release_version import read_release
from skills import CODE_MODE, START, mentioned, named_tools, removed_named, skill_tools, snapshot, texts, version


class SkillTests(unittest.TestCase):
    """The plugin stays thin and in sync: the MCP is the integration, and the server's guides win."""

    def test_skills_name_only_tools_the_server_serves(self):
        tools = set(snapshot()['tools'])
        self.assertTrue(skill_tools())
        self.assertEqual(skill_tools() - tools, set(), 'A skill names a tool the server does not serve; refresh server-tools.json or the skill.')
        self.assertEqual(skill_tools() - set(snapshot()['listed']), set(), 'A skill calls a tool a session does not list directly.')
        self.assertEqual(removed_named(), [], 'A skill names a removed actionfleet/1 tool.')
        self.assertEqual(named_tools('Call `get_task(...)` then `list_tasks` with `request_id`.'), {'get_task', 'list_tasks'})
        self.assertTrue(CODE_MODE.isdisjoint(tools))

    def test_skills_name_only_the_start_tools_and_leave_the_rest_to_the_guides(self):
        self.assertEqual(skill_tools(), START, 'Skills name only bootstrap and get_guide; the server\'s guides name the rest.')
        self.assertEqual(set(mentioned(snapshot()['tools'])) - START, set(), 'A skill mentions another server tool.')
        self.assertEqual(mentioned(['get_guide', 'list_ships']), ['get_guide'])

    def test_every_skill_defers_to_the_server(self):
        guides = set(snapshot()['guides'])
        for name, text in texts().items():
            if name.endswith('SKILL.md'):
                self.assertIn('`bootstrap`', text, name)
                self.assertIn('plugin_version', text, name)
                topics = set(re.findall(r"`get_guide\('([a-z]+)'\)`", text))
                self.assertTrue(topics, name)
                self.assertEqual(topics - guides, set(), name)
        setup = (ROOT / 'plugins/actionfleet/skills/setup/SKILL.md').read_text()
        for needed in ('plugin_version', 'references/installation.json', 'outdated', 'source of truth'):
            self.assertIn(needed, setup)

    def test_the_other_skills_find_the_plugin_version_where_packages_put_it(self):
        for profile in profiles():
            for skill in ('work-task', 'coordinate'):
                folder = ROOT / 'packages' / profile['name'] / 'skills' / skill
                self.assertIn('../setup/references/installation.json', (folder / 'SKILL.md').read_text())
                self.assertTrue((folder / '../setup/references/installation.json').resolve().is_file(), folder)

    def test_this_release_meets_the_server_minimum_it_was_written_for(self):
        manifest = json.loads((ROOT / 'plugins/actionfleet/plugin.json').read_text())['version']
        self.assertGreaterEqual(version(manifest), version(snapshot()['plugin_minimum']))
        self.assertLessEqual(version(manifest), version(read_release()['version']))
        self.assertEqual(version('2026.101.3'), (2026, 101, 3))
        self.assertIsNone(version('v1'))
