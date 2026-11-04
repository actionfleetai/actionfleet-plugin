---
name: skill-cards
description: Writes and revises agent skills (SKILL.md) so they are short, fire on the right request and run the same way every time. Use when creating, refactoring, reviewing or tightening a skill, SOP or runbook for Claude Code, Codex or Cursor. Not for listing or installing skills.
---

# Skill cards

A capable agent reads the skill: write only what it can't know or infer, and each rule once. Most
skills are a description and a few numbered steps.

1. Get the purpose (the outcome, one sentence); ask once if the person hasn't said it. When revising,
   read the skill's files first and keep every command, name and rule it needs.
2. Write the description: `<What it does, third person>. Use when <the person's words>. Not for <near
   miss>.` At most 1024 characters, no `<tags>`.
3. Write the steps: numbered, one action each, verb first, exact commands where exactness matters.
   State each rule once, where it applies: on the line before an irreversible or outward-facing step
   (delete, push, publish, spend, message people), put `WARNING:` and the check that must pass first.
4. Move each rule a program can decide (a format, a date, a count, a parse) into a stdlib Python script
   in `scripts/`: inputs as flags, the answer on stdout, exit 2 with why when it refuses, and `--test`
   with its examples. The skill runs it instead of restating the rule; only its output enters context.
   Titles, commit subjects and release notes follow Conventional Commits.
5. Add a part only when the steps can't carry it:
   - facts the steps use, each with its only source and what to do when it's unknown, when a guess
     would be wrong;
   - a rules table ending in `Otherwise`, when a choice has three or more branches;
   - how it ends (done with what evidence, blocked on whom), when the last step doesn't show it.
6. Cut every line that doesn't change what the agent does: background, reminders to be careful,
   restated rules, a failure note that repeats a step. Keep the body under 100 lines, since it loads on
   every use; move rarely needed detail to `references/`, one level deep.
7. Run `python3 <this skill's folder>/scripts/check_card.py <skill folder>` and fix what it reports.
8. Try three prompts in a fresh session, kept out of the skill: one that should fire it, a near miss
   that shouldn't, and one that takes its main rule's other branch.

Put a skill for one repository in `<repo>/.agents/skills/<name>`, symlinked from
`<repo>/.claude/skills/<name>`; otherwise in `~/.agents/skills/<name>`, symlinked from
`~/.claude/skills/<name>`. Only when the person wants it run by name alone, add
`disable-model-invocation: true` (Claude Code, Cursor) and `agents/openai.yaml` with
`policy: {allow_implicit_invocation: false}` (Codex).

Why it looks like this, and sources: `references/sources.md` (read only when asked).
