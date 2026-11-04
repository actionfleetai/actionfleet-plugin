from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import doctest
import release_version
from release_version import identity, next_release, order, parse, ZONE


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

    def test_versions_parse_back_to_their_release_and_order_by_date(self):
        for day, build in (('2026-01-05', 2), ('2026-11-03', 1), ('2026-12-31', 9)):
            value = identity(self.value(day, build))
            self.assertEqual(parse(value['version']), value)
        self.assertLess(order('2026.1231.9'), order('2027.101.1'))
        self.assertLess(order('2026.1103.1'), order('2026.1103.2'))
        for bad in ('2026.0105.1', '2026.1301.1', '2026.230.1', '2026.105.0', 'v2026.105.1', '1.2.3'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                parse(bad)

    def test_changed_plugins_examples(self):
        self.assertEqual(doctest.testmod(release_version).failed, 0)
