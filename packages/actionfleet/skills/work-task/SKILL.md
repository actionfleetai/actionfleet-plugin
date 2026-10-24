---
name: work-task
description: Use when asked to pick up, do, resume, stop or report an Actionfleet Ship (a tracked task). The server's work guide has the steps; this is the short form.
---

# Work on a Ship

Call `get_guide` with topic `work` and follow it: it comes from the server, so it matches the
tools this session has. The short form:

- Find or read the Ship with `list_ships(mode='inbox', limit=5)` or `get_ship`, crew it with
  `crew_ship`, and state the source scope (local iteration, checkpoint, pull request or mainline)
  in the first `update_ship`. Checkpoint with `update_ship`; it renews the lease.
- Finish with `report_ship`: evidence and, for code, the exact repository and commit. It releases
  the claim. A person verifies; never verify your own work.
- Cannot do it? `block_ship` with the blocker. Waiting on another Ship? `set_blocked_by`. On STOP,
  stop external work, then `release_ship` with reason `stopped`.
- `get_ship`, `crew_ship` and `update_ship` carry `tunnels` when a related Ship's crew wrote to
  this Ship; read them with `read_tunnel`.
- Follow the target repository's source and commit identity policy. Never replace the user's Git
  identity with an agent's to satisfy a hook or a Verified badge.

Name Ships to people by their Ship id (SHIP-12). If a tool named here is missing, this plugin is
out of date: say so and follow the server.
