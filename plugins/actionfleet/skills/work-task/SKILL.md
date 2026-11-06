---
name: work-task
description: Use when asked to pick up, do, resume, stop or report an Actionfleet Ship (a tracked task). The server's work guide has the steps.
---

# Work on a Ship

The Actionfleet server says how to work a Ship, and that changes with its tools, so this skill
points to the server instead of repeating it.

1. Not bootstrapped in this session yet? Call `bootstrap` first, passing `plugin_version` from
   `../setup/references/installation.json` (this plugin's setup skill has the steps). If its answer
   says this plugin is outdated, tell the person to update the Actionfleet plugin.
2. Read `get_guide('work')` and follow it. It comes from the server, so it names the tools this
   session has. Where it differs from this plugin, an older note or memory, follow the server.
3. Follow the target repository's source and commit identity policy. Never replace the user's Git
   identity with an agent's to satisfy a hook or a Verified badge.

Name Ships to people by their Ship id (SHIP-12). A person verifies a reported Ship; never verify
your own work.
