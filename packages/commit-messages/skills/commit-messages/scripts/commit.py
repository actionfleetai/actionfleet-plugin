#!/usr/bin/env python3
"""Check and format commit messages: Conventional Commits 1.0.0 subjects, `type(scope)!: summary`.

Rules, every one must hold:
  type     one of the types below, lowercase
  scope    optional, in parentheses: lowercase words joined by - / . or _, such as catalog or games/hexa-colony
  !        before the colon when the change breaks something people rely on, or a `BREAKING CHANGE:` footer
  summary  after `: `; starts lowercase, with a digit or with an acronym (`MCP`), not a capital word (`Add`); no
           trailing period
  header   at most 72 characters
  body     after one blank line, when there is one
  Ship     a `Ship:` trailer holds one Ship ref such as SHIP-7; --public refuses it, because refs are private
Git's own `Merge ...` and `Revert "..."` subjects pass. Squash `fixup!` and `squash!` commits before checking.

Types, by what the change does for the people who use it:
  feat      adds or changes a capability
  fix       corrects a defect
  perf      makes it faster or cheaper, with the same behavior
  refactor  restructures code, with the same behavior
  docs      documentation only
  test      tests only
  build     build, packaging or dependencies
  ci        CI configuration
  style     formatting only
  chore     anything else, such as a release
  revert    undoes an earlier commit

>>> problems('feat(skill-cards): add a commit rule')
[]
>>> problems('fix(api): MCP tools return the Ship ref')
[]
>>> problems('Add a commit rule')
['not `type(scope)!: summary`']
>>> problems('feat: Add a commit rule')
['summary starts with a capital word: write `add`']
>>> problems('feature: add x')
["unknown type 'feature': use build, chore, ci, docs, feat, fix, perf, refactor, revert, style or test"]
>>> problems('docs(Plugin): trim the README.')
["scope 'Plugin': lowercase words joined by - / . or _", 'summary ends with a period']
>>> problems('feat!: drop the v1 protocol\\n\\nBREAKING CHANGE: reconnect with actionfleet/2')
[]
>>> problems('fix: keep titles\\nno blank line')
['no blank line after the subject']
>>> problems('fix: keep titles\\n\\nShip: shp_abc123')
["Ship trailer isn't a Ship ref: 'shp_abc123'"]
>>> problems('fix: keep titles\\n\\nShip: SHIP-7', public=True)
['Ship trailer in a public repository: refs are private']
>>> problems('Merge branch main into topic')
[]
>>> problems('fixup! feat: add x')
['squash fixup! and squash! commits first']
>>> header('feat', 'add commit types to titles', scope='session-titles')
'feat(session-titles): add commit types to titles'
>>> header('fix', 'Keep the ref')
Traceback (most recent call last):
ValueError: summary starts with a capital word: write `keep`
"""
import argparse
import re
import subprocess
import sys

TYPES = ('feat', 'fix', 'perf', 'refactor', 'docs', 'test', 'build', 'ci', 'style', 'chore', 'revert')
HEADER = re.compile(r'^(?P<type>[A-Za-z]+)(?:\((?P<scope>[^()]*)\))?(?P<bang>!)?: (?P<summary>\S.*)$')
SCOPE = re.compile(r'[a-z0-9]+(?:[-/._][a-z0-9]+)*')
CAPITAL = re.compile(r'[A-Z][a-z]')
REF = re.compile(r'[A-Z][A-Z0-9]{0,9}-[1-9][0-9]*')
MAX_HEADER = 72


def subject_problems(subject):
    if subject.startswith(('fixup! ', 'squash! ', 'amend! ')):
        return ['squash fixup! and squash! commits first']
    if subject.startswith(('Merge ', 'Revert "')):
        return []
    match = HEADER.match(subject)
    if not match:
        return ['not `type(scope)!: summary`']
    found = []
    if match['type'] not in TYPES:
        found.append(f"unknown type {match['type']!r}: use {', '.join(sorted(TYPES)[:-1])} or {sorted(TYPES)[-1]}")
    if match['scope'] is not None and not SCOPE.fullmatch(match['scope']):
        found.append(f"scope {match['scope']!r}: lowercase words joined by - / . or _")
    summary = match['summary']
    if CAPITAL.match(summary):
        found.append(f'summary starts with a capital word: write `{summary.split()[0].lower()}`')
    if summary.endswith('.'):
        found.append('summary ends with a period')
    if len(subject) > MAX_HEADER:
        found.append(f'header is {len(subject)} characters; keep it to {MAX_HEADER}')
    return found


def problems(message, public=False):
    lines = message.strip('\n').split('\n')
    found = subject_problems(lines[0].strip())
    if len(lines) > 1 and lines[1].strip():
        found.append('no blank line after the subject')
    for line in lines[1:]:
        key, _, value = line.partition(':')
        if key == 'Ship':
            if public:
                found.append('Ship trailer in a public repository: refs are private')
            elif not REF.fullmatch(value.strip()):
                found.append(f"Ship trailer isn't a Ship ref: {value.strip()!r}")
        elif key.strip().lower() in ('breaking change', 'breaking-change') and key not in ('BREAKING CHANGE', 'BREAKING-CHANGE'):
            found.append('write the footer as `BREAKING CHANGE:`')
    return found


def header(type_, summary, scope=None, breaking=False):
    value = f"{type_}{f'({scope})' if scope else ''}{'!' if breaking else ''}: {summary.strip()}"
    found = subject_problems(value)
    if found:
        raise ValueError('; '.join(found))
    return value


def from_file(path):
    """A commit-msg hook's message: Git's comment lines and everything below its scissors line removed."""
    kept = []
    for line in open(path, encoding='utf-8').read().split('\n'):
        if line.startswith('# ') and '>8' in line:
            break
        if not line.startswith('#'):
            kept.append(line)
    return '\n'.join(kept)


def from_range(rev_range):
    out = subprocess.run(['git', 'log', '--no-merges', '--format=%h%x00%B%x1e', *rev_range.split()],
                         capture_output=True, text=True, check=True).stdout
    return [tuple(entry.strip('\n').split('\0', 1)) for entry in out.split('\x1e') if entry.strip()]


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('command', nargs='?', choices=['check', 'format'])
    parser.add_argument('--range', help="check: git log's revisions, such as origin/main..HEAD or 'HEAD --not --remotes'")
    parser.add_argument('--message-file', help="check: a commit-msg hook's message file")
    parser.add_argument('--message', help='check: one message')
    parser.add_argument('--public', action='store_true', help='check: the repository is public, so refuse Ship trailers')
    parser.add_argument('--type', help='format: the type')
    parser.add_argument('--scope', help='format: the scope, if any')
    parser.add_argument('--breaking', action='store_true', help='format: mark the header with !')
    parser.add_argument('--summary', default='', help='format: the summary')
    parser.add_argument('--rules', action='store_true', help='print the rules and exit')
    parser.add_argument('--test', action='store_true', help='run the examples and exit')
    args = parser.parse_args(argv)
    if args.rules:
        print(__doc__.split('\n>>>')[0].strip())
        return 0
    if args.test:
        import doctest
        failed, tried = doctest.testmod(sys.modules[__name__])
        print(f'{tried - failed}/{tried} examples pass')
        return 1 if failed else 0
    if args.command == 'format':
        try:
            print(header(args.type or '', args.summary, args.scope, args.breaking))
        except ValueError as error:
            print(f'refused: {error}', file=sys.stderr)
            return 2
        return 0
    if args.command != 'check' or sum(x is not None for x in (args.range, args.message_file, args.message)) != 1:
        parser.error('use check with one of --range, --message-file or --message, or format, --rules or --test')
    if args.range:
        try:
            commits = from_range(args.range)
        except subprocess.CalledProcessError as error:
            print(f'refused: git log {args.range}: {error.stderr.strip()}', file=sys.stderr)
            return 2
    else:
        commits = [('message', from_file(args.message_file) if args.message_file else args.message)]
    failed = 0
    for name, message in commits:
        found = problems(message, public=args.public)
        if found:
            failed += 1
            print(f"refused: {name} {message.split(chr(10))[0][:60]}: {'; '.join(found)}", file=sys.stderr)
    print(f'{len(commits) - failed}/{len(commits)} commit messages pass')
    return 2 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
