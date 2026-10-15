---
name: coordinate
description: Use when the user asks to fan out independent work, delegate across connected harnesses, collect results, or coordinate an ad hoc fleet. Keep execution in real receiving harnesses.
---

# Coordinate independent work

Use the connected Fleet MCP and current schemas. Start with the work-task fast
path; avoid a separate planning ceremony for a small task. Fleet is the task
ledger. GitHub issues, labels, Projects and callback review loops are unnecessary.

1. Split only where work can actually proceed independently. Keep shared-file
   changes with one writer. Use `parent_task` to group work. A parent link does
   not block children. Add dependencies only for required inputs.
2. Advertise real models/capabilities on each authenticated connection. Put
   all-required capability tags in `required_capabilities`; put acceptable model
   alternatives in `required_models` when the server exposes these fields.
   Do not infer model/subscription availability from a connection name.
3. Open independent tasks with stable request/command IDs using
   `submit_task_commands` if advertised (at most 16, up to 8 server operations
   concurrently). Results are per task; partial success has no global rollback.
   Never batch dependent writes to the same task. Inspect each result and retry
   uncertain commands unchanged.
4. Deliver work through a real supported native worker path. If no launcher/resume
   adapter is configured, a running worker must discover and claim it through MCP.
   Report queued/pickup-needed with one concrete next action. Never invent a
   launch API or call task creation dispatch. Get a real delivery/claim receipt.
5. Use `get_task_group` for up to 16 known child IDs to collect summaries and
   report evidence together. It returns per-task watermarks, not a global snapshot.
   React to changes; avoid repeated unchanged history/schema dumps.
6. If an aggregator may consume unverified results, explicitly choose
   `dependency_policy="reported"`; default dependencies require verified results.
   Reported fan-in does not approve children. Keep final human acceptance separate.
   Include failed, cancelled, stopped, unverified and missing children honestly.

Native parallel execution needs actual available workers/capacity. Fleet's batch
API parallelizes coordination/storage calls; it does not pool subscriptions or
prove simultaneous model execution. Each task retains its own claim, lease, STOP
and idempotency. Preserve user scope and other writers. Report useful throughput
and end-to-end milestones, not just tool-call counts or summed concurrent times.
