#!/usr/bin/env python3
"""Los Angeles date/build releases, encoded as ordered three-field plugin versions."""
import argparse
from datetime import date, datetime, timezone
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ZONE = 'America/Los_Angeles'


def identity(value):
    day = date.fromisoformat(value['date'])
    number = value['build']
    if (day.isoformat() != value['date'] or type(number) is not int or number < 1
            or value.get('timezone') != ZONE):
        raise ValueError('Use an ISO release date, positive integer build and Los Angeles timezone.')
    return {**value, 'version': f'{day.year}.{day.month * 100 + day.day}.{number}',
            'label': f'{day.year}.{day.month}.{day.day} ({number})'}


def read_release(path=ROOT / 'release.json'):
    return identity(json.loads(path.read_text()))


def next_release(value, now=None):
    old = identity(value)
    now = datetime.now(timezone.utc) if now is None else now
    if now.tzinfo is None:
        raise ValueError('Release clock must have an explicit timezone.')
    day = now.astimezone(ZoneInfo(ZONE)).date()
    previous = date.fromisoformat(old['date'])
    if day < previous:
        raise ValueError('Release date cannot move backwards. Fetch/rebase main and check the clock.')
    return {'date': day.isoformat(), 'build': old['build'] + 1 if day == previous else 1, 'timezone': ZONE}


def bump():
    path = ROOT / 'release.json'
    value = next_release(json.loads(path.read_text()))
    manifest_path = ROOT / 'plugins/actionfleet/plugin.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['version'] = identity(value)['version']
    path.write_text(json.dumps(value, indent=2) + '\n')
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    from catalog import sync
    sync()
    return identity(value)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['info', 'bump'], nargs='?', default='info')
    parser.add_argument('--field', choices=['version', 'label'])
    args = parser.parse_args()
    result = bump() if args.command == 'bump' else read_release()
    print(result[args.field] if args.field else json.dumps(result, indent=2))
