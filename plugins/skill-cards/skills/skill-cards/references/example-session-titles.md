---
name: session-titles
description: Prefixes this chat's title with where it runs (💻 local, ☁️ cloud) and its Actionfleet Ship ref. Use right after Actionfleet bootstrap, and right after this session crews or opens a Ship it will work. Not for renaming a Ship or another session.
---

# Session titles

Titles this chat `<place> <ref> <rest>`, for example `☁️ SHIP-12 Fix login redirect`.

## Facts

| Fact | Source (only) | If unknown |
| --- | --- | --- |
| harness | the `harness` this session passed to `bootstrap` | SKIPPED |
| ship | `head.ship.ref` of the Ship this chat crewed or opened with `crew=true`, or the person's words | no ref |
| parent | that Ship's `snapshot.parent_ship` | no parent |
| rest | the current title without a leading 💻/☁️ and `SHIP-n` | a few words from the Ship's objective |

## Rules

First match wins in each table.

| If | Then place is |
| --- | --- |
| harness ends in `-cloud` | ☁️ |
| Otherwise | 💻 |

| If | Then ref is |
| --- | --- |
| the chat works several Ships under one parent | parent |
| ship is known | ship |
| Otherwise | none, and the title is `<place> <rest>` |

| If the host is | Then the title tool is |
| --- | --- |
| claude.ai/code | `set_session_title`, with this session's id from `get_session` |
| Cursor Cloud Agents | `rename-chat` |
| Codex CLI | `set_thread_title`, without `threadId` |
| Otherwise | none |

## Procedure

1. After `bootstrap`, set this chat's title to `<place> <rest>`.
2. After crewing or opening the Ship, set it to `<place> <ref> <rest>`.

Reporting, releasing or a STOP doesn't change the title. Never build or guess a ref, and rename only
this chat.

## Faults

| Symptom | Action | Tell |
| --- | --- | --- |
| the title tool refuses or errors | don't retry | nobody |

## Exits

- DONE: the host shows the new title.
- SKIPPED: no title tool, or harness unknown. Say nothing; don't ask the person to rename the chat.

## Tests

- Fires: a cloud session crews SHIP-12 → `☁️ SHIP-12 <rest>`.
- Doesn't fire: "rename SHIP-12" (the Ship's title, not the chat's).
- False branch: Claude Code CLI, no title tool → title unchanged, no message.
