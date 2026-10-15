from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build', ROOT / 'scripts/build.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PackageTests(unittest.TestCase):
    def test_complete_packages_share_skills_and_endpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = module.build('https://mcp.example.com/mcp', Path(tmp) / 'release')
            root = archive.parent
            plugin = root / 'plugins/actionfleet'
            portable = json.loads((plugin / 'mcp.json').read_text())
            claude = json.loads((plugin / '.mcp.json').read_text())
            self.assertEqual(portable['mcpServers']['actionfleet']['url'], claude['mcpServers']['actionfleet']['url'])
            self.assertEqual(portable['mcpServers']['actionfleet']['type'], 'streamable-http')
            self.assertEqual(claude['mcpServers']['actionfleet']['type'], 'http')
            self.assertEqual(portable['mcpServers']['actionfleet-setup']['url'], 'https://mcp.example.com/public/mcp')
            self.assertEqual(portable['mcpServers']['actionfleet']['extensions']['com.openai']['auth']['type'], 'oauth')
            self.assertEqual(portable['mcpServers']['actionfleet-setup']['extensions']['com.openai']['auth']['type'], 'none')
            for path in ['.agents/plugins/marketplace.json', '.claude-plugin/marketplace.json']:
                self.assertEqual(json.loads((root / path).read_text())['plugins'][0]['name'], 'actionfleet')
            with zipfile.ZipFile(archive) as z:
                names = z.namelist()
                self.assertIn('actionfleet/mcp.json', names)
                self.assertIn('actionfleet/skills/setup/SKILL.md', names)
                self.assertFalse(any('/.git/' in n or n.endswith('.env') for n in names))
            with self.assertRaises(ValueError):
                module.build('https://mcp.example.com/mcp', root)

    def test_archives_are_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            archives = [module.build('https://mcp.example.com/mcp', Path(tmp) / n) for n in ('a', 'b')]
            self.assertEqual(*(sha256(a.read_bytes()).hexdigest() for a in archives))

    def test_rejects_secret_bearing_and_non_https_endpoints(self):
        for value in ['http://mcp.example.com/mcp', 'https://user:secret@example.com/mcp',
                      'https://example.com/mcp?token=secret', 'https://example.com/mcp#secret',
                      'https://example.com/not-mcp', 'https://example.com:invalid/mcp']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                module.endpoint(value)

    def test_source_does_not_package_unreviewed_files(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'source'
            shutil.copytree(module.SOURCE, source)
            (source / '.env').write_text('not a real secret')
            with self.assertRaises(ValueError):
                module.build('https://mcp.example.com/mcp', Path(tmp) / 'release', source)
