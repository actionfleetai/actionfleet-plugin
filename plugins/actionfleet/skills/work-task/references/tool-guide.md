# Principal tools (discover the deployed schema)

| Intent | Tool | Use |
| --- | --- | --- |
| Setup/reconnect | `bootstrap_harness` | Once; real harness/version/session and advertised models/capabilities. Read required checks, recovery and tool guide. |
| Payload schema | `get_protocol_schema` | Discover once for this deployment, before constructing commands. |
| Pick up work | `list_tasks` | Small eligible inbox; `my_claims` for recovery; follow cursors. |
| Inspect/guard | `get_task` | Current claim/head/STOP/acceptance before shared writes. |
| Claim/checkpoint/result | `submit_task_command` | Stable command ID; holder proof; current `if_head` where required. |
| Independent fan-out | `submit_task_commands` | Only if advertised; max 16 independent commands, per-task results. |
| Result fan-in | `get_task_group` | Only if advertised; max 16 known children, per-task watermarks, no acceptance implied. |
| Investigate/recover | `get_task_changesets` | Bounded task-local history when needed, not every poll. |
| Diagnose runtime | `get_runtime_status` | Only for a concrete connection/runtime problem; not a setup ritual or provider quota source. |

Code Mode uses `await call_tool(name, params)` inside `execute`. Batch related
reads; writes still need current authority. Return compact useful output. Do not
assume tool availability from this static guide; fallback to current single-task
tools if bulk tools are absent. An MCP connection supplies task coordination,
not native process launch or interruption. Never ask for secrets in chat.
