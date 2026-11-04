# Why cards look like this

The shape borrows from Navy maintenance and casualty-control cards, which a trained crew member runs
without asking, and adapts them for agents.

| Navy | Card |
| --- | --- |
| Maintenance Requirement Card: who does what, when, how and with what | description (what, when), Facts (with what), Procedure (how) |
| Periodicity or situational requirement | the trigger in the description |
| Tag-out and equipment guide lists: what must be true first | Facts, each with its only source |
| WARNING (people), then CAUTION (equipment), then NOTE, placed before the step and never holding steps | `WARNING:` for irreversible or outward-facing actions, `CAUTION:` for wrong or wasted output, before the step. No NOTE: a line that changes nothing is cut |
| Casualty control: symptoms, then controlling and restoring actions | Faults: symptom, action, who to tell |
| A card crossed off when done, circled and rescheduled when not | Exits: DONE, SKIPPED, BLOCKED |

What agents need that a crew member doesn't:

- **A source for every fact.** An agent fills gaps with plausible guesses, so each fact names where it
  comes from and what happens when it's unknown.
- **An Otherwise row.** Every rule ends in a default, so no state is undefined.
- **Tests first.** Three prompts written before the card show whether the description fires.
- **A small budget.** Hosts load every description at start and the body on use, so each line costs
  context in every session.

## Sources

- Agent Skills specification: https://agentskills.io/specification (frontmatter limits, folders,
  body under 500 lines and about 5,000 tokens, references one level deep, `skills-ref validate`).
- Skill authoring best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
  (only add what the agent lacks, third-person descriptions, degrees of freedom, evaluation first).
- NAVSEAINST 4790.8 (ships' maintenance and material management, MRC format):
  https://www.navsea.navy.mil/Portals/103/Documents/NAVINST/04790.008D.pdf
- Engineering Operational Sequencing System overview:
  https://engineeringtraining.tpub.com/14079/css/Engineering-Operational-Sequencing-System-Eoss-105.htm
- WARNING, CAUTION and NOTE order and placement, MIL-STD-38784:
  https://technicalmanualspecsstandards.emilspec.com/MIL-STD-38784/page31.html
