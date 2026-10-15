---
name: work-task
description: Carry an authorized Action Fleet task through ownership, checkpoints, durable waits and evidence using the connected harness.
---

# Work on an Action Fleet task

Run setup first when the connection or readiness is unknown. Discover the current
task tool schemas; follow the server's protocol version and the user's scope.
Fetch the task, latest revision, owner, holds, STOP and acceptance before work.

Claim only eligible authorized work. Preserve stable task, session and command
identities. Use expected revisions and the returned execution fence for owned
writes. Another writer's work requires an accepted handoff. A lease timeout,
silent chat or disconnected process does not transfer ownership.

Perform implementation in this harness with its normal repository permissions.
Report meaningful checkpoints and exact source/artifact references. Keep tool
results separate from independently verified acceptance. On uncertain delivery,
query the current task and reuse the original command ID; do not duplicate work.

Save waits with a reason and next action. Register a real supported continuation
when needed; otherwise report the explicit resume step. Never claim that saving
a wait, adding a comment or installing this plugin wakes a stopped cloud agent.

On STOP, stop choosing new writes, checkpoint safely, report any in-flight or
uncertain effects and acknowledge the specific STOP. Acknowledgment must reflect
the actual process state, and cannot undo an already completed external effect.

Report a result with relevant evidence and unresolved limitations. Preserve the
distinction between result reported, accepted outcome, source landed and released.
This skill does not grant additional execution, monetary or release authority.
