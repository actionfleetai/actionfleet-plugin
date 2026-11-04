---
name: skill-cards
description: Writes and revises agent skills (SKILL.md) as short, testable cards with a trigger, facts and their sources, decision rules, numbered steps, faults and exits. Use when creating, refactoring, reviewing or tightening a skill, SOP or runbook for Claude Code, Codex or Cursor.
---

# Skill cards

A card tells a capable agent who runs it, when, with what, how, and how it ends. Write only what the
agent can't already know or infer. Blank card: `assets/card.md`. Worked examples: the `session-titles`
and `commit-messages` add-ons in the same marketplace, cards that run a script.

## Facts

| Fact | Source (only) | If unknown |
| --- | --- | --- |
| purpose: the outcome, one sentence | the person | ask once; BLOCKED until answered |
| trigger: the request or moment that starts it | the person, or the purpose | propose one and confirm |
| current text, when revising | the skill's files | new skill |

## Rules

First match wins in each table.

| If the trigger is | Then |
| --- | --- |
| something the person asks for | the description carries it |
| Otherwise (a moment in the agent's own work: a tool returned, a session started) | descriptions fire unreliably there: put a one-line instruction where the moment happens (that tool's result, a hook), keep the card as the how, and tell the person |

| If a step is | Then write |
| --- | --- |
| a rule over facts the agent already holds (format, parse, validate, compute) | a stdlib Python script in `scripts/`: facts as flags, the answer on stdout, exit 2 with why when it refuses, and `--rules` and `--test` (its examples). The card names the facts, runs it and applies the answer |
| writing a title, commit subject, pull request title or release note | Conventional Commits, `type(scope)!: summary`, with the type from the spec's list and checked by the script |
| fragile or exact (a command, a format, an API) | the exact command or format |
| Otherwise | the intent and its limit, not a script |

| If the skill | Then install it in |
| --- | --- |
| is one of Actionfleet's opt-in skills | `plugins/<name>/skills/<name>` in `actionfleetai/actionfleet-plugin`, listed in `ADDONS` in its build script; skills only, never an MCP server |
| uses one repository's files or scripts | `<repo>/.agents/skills/<name>`, symlinked from `<repo>/.claude/skills/<name>` |
| Otherwise | `~/.agents/skills/<name>`, symlinked from `~/.claude/skills/<name>` |

| If the skill should run | Then add |
| --- | --- |
| only when called by name | `disable-model-invocation: true` (Claude Code, Cursor) and `agents/openai.yaml` with `policy: {allow_implicit_invocation: false}` (Codex) |
| Otherwise | nothing |

## Procedure

1. Write the three Tests first: a prompt that fires it, a near miss that must not, and the false
   branch of its main rule.
2. Write the description: `<What it does, third person>. Use when <trigger>. Not for <near miss>.`
   Use the words the person would say. At most 1024 characters, no `<tags>`.
3. Fill Facts: every fact the rules read, its only source, and what happens when it's unknown.
   "Don't guess" becomes an If unknown branch.
4. Fill Rules as tables over the facts. First match wins; end each table with `Otherwise`. Move each
   rule a script can decide into one, and keep in the card only what needs judgment or the host.
5. Fill Procedure: one numbered action per step, verb first. Put `WARNING:` (irreversible or
   outward-facing: delete, push, publish, spend, message people) or `CAUTION:` (wrong or wasted
   output) on the line before the step it guards, never with steps inside it.
6. Fill Faults (observable symptom, action, who to tell) and Exits (DONE with evidence, SKIPPED,
   BLOCKED with who can fix). Every path ends in one exit.
7. Cut every line that doesn't change what the agent does. One rule in one place, the same word for
   the same thing. Keep the body under 100 lines; move detail to `references/`, one level deep.
8. Run `python3 <this skill's folder>/scripts/check_card.py <skill folder>`, fix, and repeat until
   it reports no errors. Then try the three Tests in a fresh session.

## Faults

| Symptom | Action | Tell |
| --- | --- | --- |
| a Test fires when it shouldn't | add the near miss to `Not for` | nobody |
| a Test doesn't fire | add the person's trigger words to the description | nobody |
| a script's `--test` fails | fix the script or its examples before the card | nobody |
| `python3` is missing | read the script and apply it by hand | the person |

## Exits

- DONE: no checker errors, Tests behave as written; report the path and the card's one-line purpose.
- BLOCKED: purpose unknown; the person.

## Tests

- Fires: "make a skill that titles my chats with the Ship id" → a card whose title format, with a commit type, is
  a script.
- Doesn't fire: "what skills do I have installed?"
- False branch: the trigger is "after crew_ship returns" → the card, plus advice to put the
  instruction in that tool's result.

Why it looks like this, and sources: `references/sources.md` (read only when asked).
