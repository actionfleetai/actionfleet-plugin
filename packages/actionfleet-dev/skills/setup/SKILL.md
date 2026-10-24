---
name: setup
description: Use when connecting this harness to Actionfleet or after a reconnect. Connects the MCP, bootstraps with this plugin's version and hands over to the server's own guides.
---

# Connect to Actionfleet

The Actionfleet MCP is the whole integration. This plugin only packages its connection so a host
can switch it on and off. The server's tools, their descriptions, bootstrap's `tool_guide` and
`get_guide` are the source of truth; wherever this skill and the server differ, follow the server.

1. Use this package's MCP connection. Its `-setup` connection is public onboarding and needs no
   account. When authorized tools are missing, finish sign-in and consent in the browser. Never
   ask for or paste passwords, tokens or secrets.
2. Read `references/installation.json` beside this skill: its `plugin_version` is this plugin's
   version. Call `bootstrap` once with the real harness (`claude-code`, `claude-code-cloud`,
   `codex-cloud`, `codex`, `cursor` or `cursor-cloud`), its version or `unknown`, a stable session
   id, only the models and capabilities this session really has, and `plugin_version`.
3. Read `plugin.status`. `current`: carry on. `outdated`: tell the user to update the Actionfleet
   plugin (see the plugin README's update controls) and follow the server's guides meanwhile.
   `unrecognized` or `not_reported`: follow the server's guides.
4. Resolve `required` checks one at a time and wait for the user where they must act; optional
   checks do not block work. Bootstrap's `recovery` lists Ships this connection still holds.
5. Read `get_guide` with topic `start`, then `work` before working a Ship and `coordinate` before
   fanning out work or messaging another Ship's crew.

A saved connection does not start a stopped chat, and installing this plugin dispatches nothing.
