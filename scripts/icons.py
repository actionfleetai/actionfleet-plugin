#!/usr/bin/env python3
"""Render each profile's plugin icon: Actionfleet's single ship (icons/ship.svg, the site's app icon) on the
profile's opaque icon_background. Rendering needs rsvg-convert; --check needs only the committed PNGs."""
import argparse
from pathlib import Path
import struct
import subprocess
import tempfile
import zlib

from catalog import profiles

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'icons/ship.svg'
BACKGROUND = '<rect width="32" height="32" rx="8" fill="#0a0e1a"/>'
SIZE = 512


def icon_path(name, root=ROOT):
    return root / 'icons' / f'{name}.png'


def svg(background):
    art = ART.read_text()
    if art.count(BACKGROUND) != 1:
        raise ValueError('icons/ship.svg must keep its one 32px rounded background square.')
    return art.replace(BACKGROUND, BACKGROUND.replace('#0a0e1a', background))


def render(rsvg='rsvg-convert'):
    for p in profiles():
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'icon.svg'
            source.write_text(svg(p['icon_background']))
            subprocess.run([rsvg, '-w', str(SIZE), '-h', str(SIZE), str(source), '-o', str(icon_path(p['name']))],
                           check=True)


def pixels(path):
    """Width, height and RGBA rows of an 8-bit, non-interlaced RGB or RGBA PNG."""
    data = Path(path).read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'{path} is not a PNG.')
    chunks, at = {}, 8
    while at < len(data):
        length, kind = struct.unpack('>I4s', data[at:at + 8])
        chunks[kind] = chunks.get(kind, b'') + data[at + 8:at + 8 + length]
        at += 12 + length
    width, height, depth, color, _, _, interlace = struct.unpack('>IIBBBBB', chunks[b'IHDR'])
    if depth != 8 or color not in (2, 6) or interlace:
        raise ValueError(f'{path} must be an 8-bit, non-interlaced RGB or RGBA PNG.')
    step = 4 if color == 6 else 3
    raw, stride, rows, previous = zlib.decompress(chunks[b'IDAT']), width * step, [], bytearray(width * step)
    for y in range(height):
        kind, line = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for x in range(stride):
            a = line[x - step] if x >= step else 0
            b, c = previous[x], previous[x - step] if x >= step else 0
            p = a + b - c
            paeth = a if abs(p - a) <= abs(p - b) and abs(p - a) <= abs(p - c) else b if abs(p - b) <= abs(p - c) else c
            line[x] = (line[x] + (0, a, b, (a + b) // 2, paeth)[kind]) & 0xFF
        rows.append([tuple(line[i:i + step]) + ((255,) if step == 3 else ()) for i in range(0, stride, step)])
        previous = line
    return width, height, rows


def check(root=ROOT):
    """Each profile has a square PNG whose background is its icon_background, and no two profiles share one."""
    found = []
    for p in profiles():
        width, height, rows = pixels(icon_path(p['name'], root))
        expected = tuple(bytes.fromhex(p['icon_background'][1:])) + (255,)
        if (width, height) != (SIZE, SIZE):
            found.append(f"{p['name']}: icon is {width}x{height}, expected {SIZE}x{SIZE}")
        elif rows[SIZE // 64][SIZE // 2] != expected:  # Above the ship's nose, inside the rounded square.
            found.append(f"{p['name']}: icon background is not {p['icon_background']}; run scripts/icons.py")
    if len({p['icon_background'].lower() for p in profiles()}) != len(profiles()):
        found.append('Each profile needs its own icon_background.')
    return found


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if not args.check:
        render()
    if found := check():
        parser.exit(1, '\n'.join(found) + '\n')
