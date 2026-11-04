import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build
import catalog
from release_version import read_release

sys.dont_write_bytecode = True  # Loading the add-on's script must not leave __pycache__ in its reviewed source.
spec = importlib.util.spec_from_file_location('check_card', ROOT / 'plugins/skill-cards/skills/skill-cards/scripts/check_card.py')
check_card = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_card)


class AddonTests(unittest.TestCase):
    """Opt-in add-ons are skills-only plugins: installing one is the opt-in, and none carries an MCP server."""

    def test_addons_are_skills_only_with_release_version(self):
        files = catalog.generated()
        version = read_release()['version']
        for name in build.ADDONS:
            root = f'packages/{name}/'
            package = {path[len(root):] for path in files if path.startswith(root)}
            self.assertFalse(package & {'mcp.json', '.mcp.json', 'plugin.json'}, name)
            codex = json.loads(files[root + '.codex-plugin/plugin.json'])
            self.assertNotIn('mcpServers', codex)
            self.assertNotIn('extensions', codex)
            self.assertEqual(codex['skills'], './skills/')
            for path in ('.codex-plugin/plugin.json', '.claude-plugin/plugin.json', '.cursor-plugin/plugin.json'):
                manifest = json.loads(files[root + path])
                self.assertEqual((manifest['name'], manifest['version']), (name, version))
            for path in build.ADDONS[name] - {'plugin.json'}:
                self.assertEqual(files[root + path], (ROOT / 'plugins' / name / path).read_bytes())
            self.assertEqual(files[root + build.ICON], build.ADDON_ICON.read_bytes())

    def test_addon_skills_pass_their_card_check(self):
        for name in build.ADDONS:
            for skill in sorted((ROOT / 'plugins' / name / 'skills').iterdir()):
                self.assertEqual(check_card.check(skill), ([], []), skill.name)

    def test_addon_scripts_pass_their_own_examples(self):
        scripts = [ROOT / 'plugins' / name / path for name, files in build.ADDONS.items() for path in sorted(files)
                   if path.endswith('.py') and "'--test'" in (ROOT / 'plugins' / name / path).read_text()]
        self.assertTrue(scripts)
        for script in scripts:
            run = subprocess.run([sys.executable, '-I', str(script), '--test'], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, f'{script.name}: {run.stdout}{run.stderr}')

    def test_session_title_script_refuses_what_is_not_a_ship_ref(self):
        script = ROOT / 'plugins/session-titles/skills/session-titles/scripts/title.py'
        run = lambda *args: subprocess.run([sys.executable, '-I', str(script), *args], capture_output=True, text=True)
        self.assertEqual(run('--harness', 'codex-cloud', '--ship', 'SHIP-12', '--title', '💻 SHIP-3 Fix login').stdout,
                         '☁️ SHIP-12 Fix login\n')
        for args in (['--harness', 'codex', '--ship', 'shp_abc123'], ['--ship', 'SHIP-12']):
            refused = run(*args)
            self.assertEqual((refused.returncode, refused.stdout), (2, ''), args)
            self.assertIn('refused:', refused.stderr)

    def test_addon_source_rejects_unreviewed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'skill-cards'
            shutil.copytree(ROOT / 'plugins/skill-cards', source)
            build.addon('skill-cards', source)
            (source / 'skills/skill-cards/.env').write_text('not a real secret')
            with self.assertRaises(ValueError):
                build.addon('skill-cards', source)
        with self.assertRaises(ValueError):
            build.addon('not-an-addon')

    def test_card_check_catches_spec_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / 'Bad_Name'
            skill.mkdir()
            (skill / 'SKILL.md').write_text('---\nname: Bad_Name\ndescription: Does things.\n---\n\nSee [it](references/missing.md).\n')
            errors, warnings = check_card.check(skill)
            self.assertTrue(any(e.startswith('name:') for e in errors))
            self.assertTrue(any('missing' in e for e in errors))
            self.assertTrue(any('Use when' in w for w in warnings))
