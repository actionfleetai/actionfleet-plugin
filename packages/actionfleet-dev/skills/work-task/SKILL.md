---
name: work-task
description: Use when asked to pick up, implement, resume, stop, or report an Action Fleet task. Coordinate through the connected MCP while work runs in this harness.
---

# Work on a Fleet task

Use Fleet when the user asks to coordinate or execute a tracked task. Ordinary
questions and tiny local edits do not need invented task hierarchies or duplicate
GitHub records. Fleet owns task state; GitHub is optional source/CI evidence.
Do not create issue mirrors, Project cards, task labels or callback comments.

## Fast path

1. If setup is unknown or reconnecting, use the setup skill. Bootstrap once,
   recover current claims, and discover the current tool/payload schemas once.
   Read the server's `tool_guide`; do not repeatedly rediscover unchanged schemas.
2. For assigned work, `get_task`. For pickup, `list_tasks(mode="inbox", limit=5)`.
   Follow pagination while `has_more`; retain the cursor. Read acceptance,
   requirements, dependency policy, claim and STOP. Claim only authorized work
   this connection can perform, using `submit_task_command(kind="claim")`.
3. Work in an isolated attempt workspace. Preserve the returned claim ID/current
   head. Before shared writes, check live claim/STOP. Send progress at meaningful
   milestones or when renewal is needed; avoid narrating every tool call.
4. Report exact evidence/artifact with the current claim and `if_head`. A report
   releases the claim. Human verification is separate; never self-verify.

Batch related native calls in one Code Mode `execute` block when supported.
Return only relevant IDs, state, blockers and next action; avoid dumping histories.
For independent fan-out/fan-in, use the coordinate skill and the server's bounded
batch/group tools if advertised. See [the compact tool guide](references/tool-guide.md).

## Source integration and delivery

Follow the target repository's source policy. For `actionfleetai/fleet`, use the
[canonical harness workflow](https://github.com/actionfleetai/fleet/blob/main/docs/harness-mainline-workflow.md):
local checkpoint commit, fetch main, rebase if needed, affected checks, fetch again
and repeat when main advances. `node scripts/mainline.mjs prepare` bounds that
loop to three passes. Enable the repository's pre-push hook without replacing
other hooks; recheck live Fleet claim/STOP before a normal direct-main push.
Validate the final rebased source; never reuse a check from an earlier source or
force-push through a race. Other repositories need their own explicit policy.

Use the human author/committer identity specified by the user or target repository
for agent-prepared commits. Credit the actual assisting agent/model with an
optional documented `Co-authored-by` trailer, or an `Agent-Harness` trailer without
inventing a provider email. Keep that attribution secondary; a harness Stop hook
or an Unverified badge is not a reason to replace the user's identity with an
agent/bot. Signing verification is independent of authorship: preserve signing
settings, inspect the actual reason, and report a key/setup blocker accurately.
Preserve other contributors' authorship and published history. Correct a user's
unpublished commit only within their authorized scope, then revalidate its new SHA.

Discover `register_changeset`, `get_task_outputs`, `get_changeset_outputs` and
`record_changeset_output` when delivery is in scope. Register the exact repository,
full commit, target and requested lanes while claimed. Registration does not land
source or launch a build. Read authenticated CI receipts; manual evidence stays
harness-reported. Return the dev link when ready while iOS/Android proceed
independently. Upload receipt, store processing and human acceptance are distinct.
Do not rebuild or reupload a successful lane just to retry its receipt publisher.

## Recovery and authority

OAuth determines the worker. Session names do not isolate identities or prove a
subscription/model entitlement. Advertise real models/capabilities during setup;
client-reported availability is not provider-verified execution. A claim ID is an
attempt ID, not a secret. Another writer needs an explicit handoff.

Use stable command IDs and retain entire submitted commands, including timestamps.
Retry uncertain writes unchanged; inspect their current returned head before the
next action. Reconcile external effects before repeating them. Recover with
`list_tasks(mode="my_claims")` and task-local changeset cursors.

A waiting reason does not pause a lease or register a wake. Use actual harness
continuations; otherwise give the concrete resume step. Fleet's MCP connection
alone cannot launch a stopped native chat. Never report dispatched/running based
only on a saved connection, task creation or client-reported capability.

On STOP, cease new work, stop owned external work where supported, reconcile
in-flight effects and acknowledge using guarded `release(reason="stopped")`.
Do not claim process cleanup without evidence. Expiry revokes authority but does
not prove an external process stopped.

Finish only requested endpoints. Candidate build, source integration, deployment,
store receipt and processing are different milestones. Do not keep an icon/source
task open following unrelated deployments. Use existing focused checks; broad CI
can overlap candidate preparation. Preserve required review and release authority.
Report measured usage only; omit unknown costs, token balances and reset times.
