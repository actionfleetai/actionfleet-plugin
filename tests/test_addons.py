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
from release_version import order, plugin_version, read_release

sys.dont_write_bytecode = True  # Loading the add-on's script must not leave __pycache__ in its reviewed source.
spec = importlib.util.spec_from_file_location('check_card', ROOT / 'plugins/extras/skills/skill-cards/scripts/check_card.py')
check_card = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_card)


def script(path):
    spec = importlib.util.spec_from_file_location(Path(path).stem, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


commit = script('plugins/extras/skills/commit-messages/scripts/commit.py')
title = script('plugins/extras/skills/session-titles/scripts/title.py')


class AddonTests(unittest.TestCase):
    """Opt-in add-ons are skills-only plugins: installing one is the opt-in, and none carries an MCP server."""

    def test_addons_are_skills_only_with_their_own_release_version(self):
        files = catalog.generated()
        newest = order(read_release()['version'])
        for name in build.ADDONS:
            version = plugin_version(name)
            self.assertLessEqual(order(version), newest)
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
        script = ROOT / 'plugins/extras/skills/session-titles/scripts/title.py'
        run = lambda *args: subprocess.run([sys.executable, '-I', str(script), *args], capture_output=True, text=True)
        self.assertEqual(run('--harness', 'codex-cloud', '--ship', 'SHIP-12', '--title', '💻 SHIP-3 Fix login').stdout,
                         '☁️ SHIP-12 Fix login\n')
        for args in (['--harness', 'codex', '--ship', 'shp_abc123'], ['--ship', 'SHIP-12']):
            refused = run(*args)
            self.assertEqual((refused.returncode, refused.stdout), (2, ''), args)
            self.assertIn('refused:', refused.stderr)

    def test_titles_and_commits_share_one_type_list(self):
        self.assertEqual(title.TYPES, commit.TYPES)
        types = lambda module: [line for line in module.__doc__.splitlines() if line.split()[:1] and line.split()[0] in commit.TYPES]
        self.assertEqual(types(title), types(commit))
        self.assertEqual(len(types(commit)), len(commit.TYPES))

    def test_commit_check_refuses_a_bad_message_file_and_passes_a_good_one(self):
        script = ROOT / 'plugins/extras/skills/commit-messages/scripts/commit.py'
        with tempfile.TemporaryDirectory() as tmp:
            message = Path(tmp) / 'COMMIT_EDITMSG'
            for text, code in (('feat(catalog): list add-on versions\n\n# Please enter the commit message\n', 0),
                               ('Add add-on versions\n', 2), ('fix: keep refs\n\nShip: SHIP-7\n', 2)):
                message.write_text(text)
                run = subprocess.run([sys.executable, '-I', str(script), 'check', '--public', '--message-file', str(message)],
                                     capture_output=True, text=True)
                self.assertEqual(run.returncode, code, run.stderr)

    def test_addon_source_rejects_unreviewed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'extras'
            shutil.copytree(ROOT / 'plugins/extras', source)
            build.addon('extras', source)
            (source / 'skills/skill-cards/.env').write_text('not a real secret')
            with self.assertRaises(ValueError):
                build.addon('extras', source)
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
            (skill / 'SKILL.md').write_text('---\nname: Bad_Name\ndescription: Does things. Use when asked.\n---\n\n## Tests\n')
            self.assertTrue(any(w.startswith('Tests:') for w in check_card.check(skill)[1]))
