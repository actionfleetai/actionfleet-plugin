---
name: commit-messages
description: Writes and checks commit messages as Conventional Commits (`type(scope)!: summary`, body, trailers), using a script for the format. Use when committing, amending an unpushed commit, or naming a pull request, and when a commit-msg hook or landing check refuses a subject. Not for release notes, which are generated from these subjects.
---

# Commit messages

Writes one commit message per change: `type(scope)!: summary`, then an optional body and trailers.
`scripts/commit.py` owns the format and the types; this card picks the facts and applies its answer.

## Facts

| Fact | Source (only) | If unknown |
| --- | --- | --- |
| change: what the commit does for the people who use it | the staged diff (`git diff --staged`) | nothing staged: SKIPPED |
| type | the change, matched to a type in `commit.py --rules` | the change mixes types: split it |
| scope | the repository's own scopes (its AGENTS.md or commit guide); otherwise the one area the diff touches | leave `--scope` out |
| breaking | the change removes or changes something people rely on | not breaking |
| policy: identity, trailers, public or private | the repository's AGENTS.md, CLAUDE.md or contributing guide | its Git config identity, no trailers |
| ship | `head.ship.ref` of the Ship this session holds | no Ship trailer |

## Rules

First match wins in each table.

| If the staged change | Then |
| --- | --- |
| mixes unrelated changes | one commit per change |
| Otherwise | one commit |

| If the repository | Then trailers are |
| --- | --- |
| is public | its policy's trailers, never `Ship:`: refs are private |
| asks for `Ship:` | its policy's trailers, then `Ship: <ref>` |
| Otherwise | its policy's trailers |

| If a change to an installed skill, card or prompt | Then its type is |
| --- | --- |
| adds or changes what an agent does | `feat` or `fix`, never `docs` |
| Otherwise | the type from `commit.py --rules` |

## Procedure

1. Read the staged diff and pick the type, scope and a summary: imperative, what changes for people, not how.
2. Run `python3 <this skill's folder>/scripts/commit.py format --type <type> --scope <scope> --summary "<summary>"`,
   adding `--breaking` when it breaks something and leaving out an unknown scope. Use its output as the subject.
3. Add a body only when the why isn't in the diff, after a blank line. For a breaking change, end with
   `BREAKING CHANGE: <what people must do>`. Put trailers last, as the policy names them.
4. Commit with the repository's identity. Credit an assisting agent in a trailer, never as the author.
5. Run `python3 <this skill's folder>/scripts/commit.py check --range "HEAD --not --remotes"`, adding `--public` for a
   public repository, and fix what it refuses.
   CAUTION: a commit already pushed is published history.
6. Fix a pushed commit with a new commit, never by amending or rebasing it.

A pull request's title is the subject its commit would have.

## Faults

| Symptom | Action | Tell |
| --- | --- | --- |
| the script exits 2 | fix each reason it prints and run it again | nobody |
| the subject is over 72 characters | shorten the summary, then drop the scope | nobody |
| a hook refuses a commit already pushed | leave it; fix forward | the person |
| `python3` is missing | read `scripts/commit.py` and apply its rules by hand | nobody |

## Exits

- DONE: `check` passes; report the subject.
- SKIPPED: nothing staged.

## Tests

- Fires: "commit this fix to the catalog check" → `fix(catalog): <summary>`, and `check` passes.
- Doesn't fire: "what changed in the last release?"
- False branch: a public repository whose policy asks for `Ship:` → no Ship trailer.
- Rules: `python3 <this skill's folder>/scripts/commit.py --test` runs the script's examples.
