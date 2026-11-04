#!/usr/bin/env python3
"""Check skill folders against the Agent Skills spec and the card format.

Usage: check_card.py <skill folder | folder of skills | SKILL.md>...
Errors break the spec and exit 1; warnings are card advice and exit 0.
"""
import re
import sys
from pathlib import Path

NAME = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
TAG = re.compile(r'<[A-Za-z/][^<>]*>')
CODE = re.compile(r'`[^`]*`')
LINK = re.compile(r'\]\(([^)#\s]+)\)')
PATH = re.compile(r'`((?:references|scripts|assets)/[^`\s]+)`')
WHEN = re.compile(r'\buse (when|whenever|for|after|before|right|only|to)\b', re.I)


def unquote(value):
    return value[1:-1] if len(value) > 1 and value[0] == value[-1] and value[0] in '"\'' else value


def frontmatter(text):
    """Top-level keys of simple YAML frontmatter, folding indented continuation lines; None when absent."""
    if not text.startswith('---\n'):
        return None, text
    end = text.find('\n---', 3)
    if end < 0:
        return None, text
    fields, key = {}, None
    for line in text[4:end].splitlines():
        match = re.match(r'^([A-Za-z][\w-]*):\s*(.*)$', line)
        if match:
            key, value = match.group(1), match.group(2).strip()
            fields[key] = '' if value in ('>', '|', '>-', '|-') else unquote(value)
        elif key and line[:1] in (' ', '\t'):
            fields[key] = (fields[key] + ' ' + line.strip()).strip()
    return fields, text[end + 4:].lstrip('\n')


def local(text):
    """Relative file links and backticked skill paths in text, without URLs."""
    found = LINK.findall(text) + PATH.findall(text)
    return sorted({t for t in found if '://' not in t and not t.startswith('mailto:')})


def section(body, title):
    match = re.search(rf'^##\s+{re.escape(title)}\s*$(.*?)(?=^##\s|\Z)', body, re.M | re.S)
    return match.group(1) if match else ''


def tables(text):
    """Each run of table rows as a list of first cells, separator rows dropped."""
    found, rows = [], []
    for line in text.splitlines() + ['']:
        if line.lstrip().startswith('|'):
            cell = line.strip().strip('|').split('|')[0].strip()
            if not re.fullmatch(r':?-{3,}:?', cell):
                rows.append(cell)
        elif rows:
            found.append(rows)
            rows = []
    return found


def prose(body):
    """The body without fenced blocks or code spans, for placeholder checks."""
    return CODE.sub('', re.sub(r'^```.*?^```', '', body, flags=re.M | re.S))


def check(folder):
    errors, warnings = [], []
    text = (folder / 'SKILL.md').read_text(encoding='utf-8')
    fields, body = frontmatter(text)
    if fields is None:
        return ['SKILL.md must start with --- frontmatter ---'], []

    name = fields.get('name', '')
    if not name:
        errors.append('name: missing')
    elif len(name) > 64 or not NAME.match(name):
        errors.append(f'name: {name!r} must be 1-64 lowercase letters, digits and single hyphens')
    elif name != folder.resolve().name:
        errors.append(f'name: {name!r} must match its folder, {folder.resolve().name!r}')
    if re.search('anthropic|claude', name):
        warnings.append('name: Claude reserves "anthropic" and "claude"')

    description = fields.get('description', '')
    if not description:
        errors.append('description: missing')
    else:
        if len(description) > 1024:
            errors.append(f'description: {len(description)} characters; the limit is 1024')
        if TAG.search(CODE.sub('', description)):
            errors.append('description: remove <tags> and unfilled placeholders')
        if not WHEN.search(description):
            warnings.append('description: say when to use it ("Use when ...")')
        if re.search(r"\b(I|I'm|I'll|[Yy]ou|[Yy]our)\b", description):
            warnings.append('description: write in the third person')
    if 'compatibility' in fields and not 1 <= len(fields['compatibility']) <= 500:
        errors.append('compatibility: must be 1-500 characters')

    lines = body.splitlines()
    if len(lines) > 500:
        errors.append(f'body: {len(lines)} lines; the limit is 500')
    elif len(lines) > 100:
        warnings.append(f'body: {len(lines)} lines; move detail to references/')
    for target in local(body):
        path = folder / target
        if not path.exists():
            errors.append(f'{target}: linked but missing')
        elif folder.resolve() not in path.resolve().parents:
            warnings.append(f'{target}: outside the skill folder, so it won\'t travel with the skill')
        elif path.suffix == '.md' and local(path.read_text(encoding='utf-8')):
            warnings.append(f'{target}: links further files; keep references one level deep')

    if re.search(r'^##\s+Tests\s*$', body, re.M):
        warnings.append('Tests: keep test prompts out of SKILL.md; the body loads on every use')
    facts = section(body, 'Facts')
    if facts and not ('Source' in facts and 'If unknown' in facts):
        warnings.append('Facts: give each fact a Source and an If unknown column')
    for rows in tables(section(body, 'Rules')):
        if not rows[-1].lower().startswith('otherwise'):
            warnings.append(f'Rules: the table starting "{rows[0]}" has no Otherwise row')
    if TAG.search(prose(body)):
        warnings.append('body: unfilled <placeholder> outside code')
    for line in lines:
        if re.match(r'\s*(WARNING|CAUTION):.*\b\d+\.\s', line):
            warnings.append(f'"{line.strip()[:40]}...": keep steps out of WARNING and CAUTION')
        elif re.match(r'\s*NOTE:', line):
            warnings.append(f'"{line.strip()[:40]}...": cut the NOTE or make it a rule')
    return errors, warnings


def folders(arg):
    path = Path(arg).expanduser()
    if path.name == 'SKILL.md':
        return [path.parent]
    if (path / 'SKILL.md').is_file():
        return [path]
    return sorted(child for child in path.iterdir() if (child / 'SKILL.md').is_file()) if path.is_dir() else []


def main(args):
    if not args:
        print(__doc__.strip())
        return 2
    failed = False
    for arg in args:
        found = folders(arg)
        if not found:
            print(f'{arg}: no SKILL.md here')
            failed = True
        for folder in found:
            errors, warnings = check(folder)
            failed |= bool(errors)
            print(f'{folder.name}: {"FAIL" if errors else "OK"} ({len(errors)} errors, {len(warnings)} warnings)')
            for message in errors:
                print(f'  error: {message}')
            for message in warnings:
                print(f'  warning: {message}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
