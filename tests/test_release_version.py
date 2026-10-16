from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from release_version import identity, next_release, ZONE


class ReleaseIdentityTests(unittest.TestCase):
    def value(self, day, build=1):
        return {'date': day, 'build': build, 'timezone': ZONE}

    def test_same_day_updates_and_calendar_boundaries_sort_in_release_order(self):
        cases = [('2026-01-05', 1), ('2026-01-05', 2), ('2026-01-31', 1),
                 ('2026-02-01', 1), ('2026-10-15', 1), ('2026-10-15', 12),
                 ('2026-10-16', 1), ('2026-12-31', 1), ('2027-01-01', 1)]
        versions = [tuple(map(int, identity(self.value(d, b))['version'].split('.'))) for d, b in cases]
        self.assertEqual(versions, sorted(set(versions)))
        self.assertEqual(identity(self.value('2026-10-15'))['label'], '2026.10.15 (1)')
        self.assertEqual(identity(self.value('2026-01-05'))['version'], '2026.105.1')

    def test_los_angeles_date_and_daily_build_reset_survive_utc_midnight(self):
        current = self.value('2026-10-15', 7)
        self.assertEqual(next_release(current, datetime(2026, 10, 16, 0, 30, tzinfo=timezone.utc)),
                         self.value('2026-10-15', 8))
        self.assertEqual(next_release(current, datetime(2026, 10, 16, 7, 0, tzinfo=timezone.utc)),
                         self.value('2026-10-16', 1))
        self.assertEqual(next_release(self.value('2026-12-31', 4), datetime(2027, 1, 1, 8, tzinfo=timezone.utc)),
                         self.value('2027-01-01', 1))

    def test_no_clock_rollback_or_invalid_counter(self):
        with self.assertRaises(ValueError):
            next_release(self.value('2026-10-16'), datetime(2026, 10, 16, 0, tzinfo=timezone.utc))
        for build in (True, 0, -1, '2'):
            with self.subTest(build=build), self.assertRaises(ValueError):
                identity(self.value('2026-10-15', build))
