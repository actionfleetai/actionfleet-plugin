---
name: session-titles
description: Prefixes this chat's title with where it runs (💻 local, ☁️ cloud) and its Actionfleet Ship ref, using a script for the format. Use right after Actionfleet bootstrap, and right after this session crews or opens a Ship it will work. Not for renaming a Ship or another session.
---

# Session titles

Titles this chat `<place> <ref> <rest>`, for example `☁️ SHIP-7 Opt-in skills`. `scripts/title.py` owns the
format; this card gathers its facts and applies its answer.

## Facts

| Fact | Source (only) | If unknown |
| --- | --- | --- |
| harness | the `harness` this session passed to `bootstrap` | SKIPPED |
| ship | `head.ship.ref` of the Ship this chat crewed or opened with `crew=true`, or the person's words | leave `--ship` out |
| convoy | the parent's `head.ship.ref` (`get_ship` on `snapshot.parent_ship`), only when this chat works several Ships under it | leave `--convoy` out |
| title | this chat's current title | leave `--title` out |
| objective | the Ship's objective | leave `--objective` out |

## Rules

Place, ref and rest: `python3 <this skill's folder>/scripts/title.py --rules` prints them.

| If the host is | Then the title tool is |
| --- | --- |
| claude.ai/code | `set_session_title`, with this session's id from `get_session` |
| Cursor Cloud Agents | `rename-chat` |
| Codex CLI | `set_thread_title`, without `threadId` |
| Otherwise | none, so SKIPPED |

## Procedure

1. After `bootstrap`, and again after crewing or opening the Ship, run
   `python3 <this skill's folder>/scripts/title.py --harness <harness> --ship <ref> --convoy <ref> --title "<title>" --objective "<objective>"`,
   leaving out each flag whose fact is unknown.
2. Set this chat's title to the script's output with the title tool. Rename only this chat.

Reporting, releasing or a STOP doesn't change the title.

## Faults

| Symptom | Action | Tell |
| --- | --- | --- |
| the script exits 2 (no harness, or not a Ship ref) | don't retitle | nobody |
| `python3` is missing | read `scripts/title.py` and apply its rules by hand | nobody |
| the title tool refuses or errors | don't retry | nobody |

## Exits

- DONE: the host shows the script's title.
- SKIPPED: no title tool, harness unknown, or the script refused. Say nothing; don't ask the person to rename the chat.

## Tests

- Fires: a cloud session crews SHIP-7 → `☁️ SHIP-7 <rest>`.
- Doesn't fire: "rename SHIP-7" (the Ship's title, not the chat's).
- False branch: Claude Code CLI, no title tool → title unchanged, no message.
- Rules: `python3 <this skill's folder>/scripts/title.py --test` runs the script's examples.
