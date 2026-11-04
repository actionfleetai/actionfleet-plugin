#!/usr/bin/env python3
"""Compute this chat's Actionfleet title, `<place> <emoji> <ref> <type>: <rest>`.

Rules, first match wins in each:
  place  --harness ends in -cloud -> ☁️  | otherwise -> 💻
  ref    --convoy given -> convoy        | --ship given -> ship | otherwise -> none
  emoji  --emoji given and a ref -> the emoji before the ref (its fleet's second name: 🚀 AFP-161) | otherwise -> none
  rest   --title without leading 💻/☁️, fleet emoji and Ship refs | if empty -> the first words of --objective | otherwise -> none
  type   --type given -> `<type>: ` before rest, replacing an earlier `type(scope)!: ` | otherwise -> rest as it is

Types are Conventional Commits types, by what the chat's main change does for the people who use it:
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

Refuses with exit 2, printing why, when --harness is empty, a ref isn't a Ship ref such as SHIP-7, --type isn't one of
these types or --emoji isn't one emoji-like symbol: it never builds or guesses one. Pass --convoy only when this chat works several Ships under that parent.

>>> title('claude-code-cloud', ship='SHIP-7', current='☁️ Opt-in skills for ActionFleet')
'☁️ SHIP-7 Opt-in skills for ActionFleet'
>>> title('claude-code', ship='SHIP-12', current='💻 SHIP-9 Fix login')
'💻 SHIP-12 Fix login'
>>> title('codex-cloud', ship='SHIP-14', convoy='SHIP-12', current='Port the shop')
'☁️ SHIP-12 Port the shop'
>>> title('cursor', current='☁️☁️ SHIP-3')
'💻'
>>> title('claude-code-cloud', ship='SHIP-7', objective='Publish the opt-in skill-cards add-on in the actionfleet-plugin GitHub marketplace')
'☁️ SHIP-7 Publish the opt-in skill-cards add-on in the actionfleet-plugin'
>>> title('claude-code-cloud', ship='SHIP-7', current='☁️ SHIP-7 Opt-in skills', type='feat')
'☁️ SHIP-7 feat: Opt-in skills'
>>> title('codex', ship='SHIP-9', current='💻 SHIP-9 feat(web): Ship list paging', type='fix')
'💻 SHIP-9 fix: Ship list paging'
>>> title('claude-code', ship='SHIP-9', current='💻 SHIP-9 feat: Ship list paging')
'💻 SHIP-9 feat: Ship list paging'
>>> title('claude-code', ship='AFP-161', emoji='🚀', current='💻 AFP-161 Login loop', type='fix')
'💻 🚀 AFP-161 fix: Login loop'
>>> title('codex-cloud', ship='AFP-161', emoji='🛸', current='☁️ 🚀 AFP-161 fix: Login loop')
'☁️ 🛸 AFP-161 fix: Login loop'
>>> title('claude-code', emoji='🚀', current='Notes')
'💻 Notes'
>>> title('claude-code', ship='AFP-1', emoji='AFP')
Traceback (most recent call last):
ValueError: not an emoji: 'AFP'
>>> title('claude-code', ship='SHIP-9', type='feature')
Traceback (most recent call last):
ValueError: not a commit type: 'feature'
>>> title('claude-code', ship='shp_abc123')
Traceback (most recent call last):
ValueError: not a Ship ref: 'shp_abc123'
>>> title('', ship='SHIP-7')
Traceback (most recent call last):
ValueError: no harness: pass the harness this session gave bootstrap
"""
import argparse
import re
import sys

CLOUD, LOCAL = '☁️', '💻'
REF = re.compile(r'[A-Z][A-Z0-9]{0,9}-[1-9][0-9]*')
EMOJI = re.compile(r'[^\x00-\x7f\s]{1,16}')  # One emoji-like symbol: a fleet's second name for its key.
PREFIX = re.compile(rf'^(?:\s*(?:{CLOUD}|☁|{LOCAL}|{REF.pattern}|{EMOJI.pattern}(?=\s+{REF.pattern}))(?=\s|$|{CLOUD}|☁|{LOCAL}))+\s*')
OBJECTIVE_WORDS = 8
TYPES = ('feat', 'fix', 'perf', 'refactor', 'docs', 'test', 'build', 'ci', 'style', 'chore', 'revert')
TYPED = re.compile(rf'^(?:{"|".join(TYPES)})(?:\([^()]*\))?!?:\s+')


def ship_ref(value):
    if value is not None and not REF.fullmatch(value):
        raise ValueError(f'not a Ship ref: {value!r}')
    return value


def title(harness, ship=None, convoy=None, current='', objective='', type=None, emoji=None):
    if not harness:
        raise ValueError('no harness: pass the harness this session gave bootstrap')
    if type is not None and type not in TYPES:
        raise ValueError(f'not a commit type: {type!r}')
    if emoji is not None and not EMOJI.fullmatch(emoji):
        raise ValueError(f'not an emoji: {emoji!r}')
    place = CLOUD if harness.endswith('-cloud') else LOCAL
    ref = ship_ref(convoy) or ship_ref(ship)
    rest = PREFIX.sub('', current or '').strip()
    if type:
        rest = TYPED.sub('', rest)
    rest = rest or ' '.join((objective or '').split()[:OBJECTIVE_WORDS])
    if type and rest:
        rest = f'{type}: {rest}'
    return ' '.join(part for part in (place, emoji if ref else None, ref, rest) if part)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--harness', default='', help="the harness this session gave bootstrap, e.g. claude-code-cloud")
    parser.add_argument('--ship', help="the Ship this chat crewed, as its ref (SHIP-7)")
    parser.add_argument('--convoy', help="the parent's ref, only when this chat works several Ships under it")
    parser.add_argument('--title', default='', help="this chat's current title")
    parser.add_argument('--objective', default='', help="the Ship's objective, used when the title is empty")
    parser.add_argument('--type', help="the commit type of this chat's main change, one of the types in --rules")
    parser.add_argument('--emoji', help="the shown Ship's fleet emoji (head.ship.emoji), when its fleet has one")
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
    try:
        print(title(args.harness, args.ship, args.convoy, args.title, args.objective, args.type, args.emoji))
    except ValueError as error:
        print(f'refused: {error}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
