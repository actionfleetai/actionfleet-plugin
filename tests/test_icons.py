from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import icons
from catalog import profiles


class IconTests(unittest.TestCase):
    """Each profile ships the brand's single ship on its own opaque background."""

    def test_committed_icons_match_their_profiles(self):
        self.assertEqual(icons.check(), [])
        for p in profiles():
            width, height, rows = icons.pixels(icons.icon_path(p['name']))
            self.assertEqual(rows[0][0][3], 0)  # Rounded corner, like the site's app icon.
            self.assertEqual(rows[height // 2][width // 2], (10, 14, 26, 255))  # The ship's navy visor.

    def test_only_the_background_changes(self):
        art = icons.ART.read_text()
        self.assertEqual(icons.svg('#0a0e1a'), art)
        dev = icons.svg('#1f7cf2')
        self.assertNotEqual(dev, art)
        self.assertEqual(dev.replace('#1f7cf2', '#0a0e1a'), art)
