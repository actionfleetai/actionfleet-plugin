import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import catalog


class CatalogTests(unittest.TestCase):
    def test_profiles_isolate_connections_and_catalog_availability(self):
        files = catalog.generated()
        for p in catalog.profiles():
            root = 'packages/' + p['name'] + '/'
            portable = json.loads(files[root + 'mcp.json'])['mcpServers']
            claude = json.loads(files[root + '.mcp.json'])['mcpServers']
            self.assertEqual(set(portable), {p['name']})
            self.assertEqual(set(claude), {p['name']})
            self.assertEqual(portable[p['name']]['url'], p['mcp_url'])
            self.assertEqual(claude[p['name']]['url'], p['mcp_url'])
            for path in ('.codex-plugin/plugin.json', '.claude-plugin/plugin.json', '.cursor-plugin/plugin.json'):
                self.assertEqual(json.loads(files[root + path])['name'], p['name'])
            # Codex reads a root plugin.json first and loads no MCP servers from it.
            self.assertNotIn(root + 'plugin.json', files)
            codex = json.loads(files[root + '.codex-plugin/plugin.json'])
            self.assertEqual((codex['skills'], codex['mcpServers']), ('./skills/', './.mcp.json'))
            self.assertEqual(codex['interface']['displayName'], p['display_name'])
            self.assertIn(root + codex['extensions']['com.openai']['onboardingSkill'][2:], files)
            self.assertEqual(json.loads(files[root + 'skills/setup/references/installation.json'])['channel'], p['channel'])
            for skill in ('setup', 'work-task', 'coordinate'):
                self.assertEqual(files[root + f'skills/{skill}/SKILL.md'],
                                 (ROOT / f'plugins/actionfleet/skills/{skill}/SKILL.md').read_bytes())
            self.assertEqual(files[root + 'assets/icon.png'], (ROOT / 'icons' / (p['name'] + '.png')).read_bytes())
        self.assertNotEqual(files['packages/actionfleet-dev/assets/icon.png'], files['packages/actionfleet/assets/icon.png'])
        openai = json.loads(files[catalog.CATALOGS[0]])['plugins']
        self.assertEqual([p['policy']['installation'] for p in openai], ['AVAILABLE', 'NOT_AVAILABLE'])
        for path in catalog.CATALOGS[1:]:
            self.assertEqual([p['name'] for p in json.loads(files[path])['plugins']], ['actionfleet-dev'])

    def test_checked_in_files_match_source_and_reject_drift(self):
        catalog.sync(check=True)
        with tempfile.TemporaryDirectory() as tmp, patch.object(catalog, 'ROOT', Path(tmp)):
            catalog.sync()
            catalog.sync(check=True)
            skill = Path(tmp) / 'packages/actionfleet-dev/skills/setup/SKILL.md'
            skill.write_text('stale instructions')
            with self.assertRaisesRegex(ValueError, 'stale'):
                catalog.sync(check=True)
            skill.unlink()
            skill.symlink_to(ROOT / 'README.md')
            with self.assertRaisesRegex(ValueError, 'symlink'):
                catalog.sync()

    def test_no_tagged_secret_or_shared_profile_endpoints(self):
        for url in ('https://sha-abc---api.example.com/mcp',
                    'https://api.example.com/mcp?token=secret',
                    'http://api.example.com/mcp'):
            rows = json.loads((ROOT / 'profiles.json').read_text())
            rows['profiles'][0]['mcp_url'] = url
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'profiles.json'
                path.write_text(json.dumps(rows))
                with self.assertRaises(ValueError):
                    catalog.profiles(path)
        for background in (None, 'blue', '#1f7cf2cc', '#1F7CF2'):
            rows = json.loads((ROOT / 'profiles.json').read_text())
            rows['profiles'][0]['icon_background'] = background
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'profiles.json'
                path.write_text(json.dumps(rows))
                with self.subTest(background=background), self.assertRaises(ValueError):
                    catalog.profiles(path)
        rows['profiles'][0]['mcp_url'] = rows['profiles'][1]['mcp_url']
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'profiles.json'
            path.write_text(json.dumps(rows))
            with self.assertRaises(ValueError):
                catalog.profiles(path)

    def test_release_archives_are_reproducible_and_only_active_profiles(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = [Path(tmp) / n for n in ('a', 'b')]
            catalog.archives(a)
            catalog.archives(b)
            self.assertEqual((a / 'SHA256SUMS').read_bytes(), (b / 'SHA256SUMS').read_bytes())
            self.assertEqual(len(list(a.glob('*.zip'))), 1)
            self.assertEqual(list(a.glob('*.zip'))[0].read_bytes(), list(b.glob('*.zip'))[0].read_bytes())
