---
name: setup
description: Use when connecting this harness to Actionfleet, right after installing this plugin, or after a reconnect. Signs in, bootstraps with this plugin's version and hands over to the server's own guides.
---

# Connect to Actionfleet

The Actionfleet MCP is the whole integration. This plugin only packages its connection so a host
can switch it on and off. The server's tools, their descriptions, bootstrap's `tool_guide` and
`get_guide` are the source of truth; wherever this skill and the server differ, follow the server.

1. Read `references/installation.json` beside this skill: `name` is this plugin's MCP server,
   `mcp_url` its address and `plugin_version` this plugin's version. It is the plugin's only server.
2. Find that server's tools. When the authorized tools (`bootstrap`, `whoami`) are missing, the
   person signs in once in the browser with their Actionfleet account:
   - Claude Code: `/mcp`, choose `plugin:<name>:<name>`, then Authenticate.
   - Codex: approve the sign-in Codex offers for this plugin, or run `codex mcp login <name>`.
   - Elsewhere: the host's MCP or connector settings.
   Then reload or start a new session if the tools still do not appear. Never ask for or paste
   passwords, tokens or secrets.
3. One connection per host. If this session also has another Actionfleet connection to the same
   address (added by hand or a claude.ai connector), use one, and tell the person they can remove
   the other: each connection is its own crew device and could claim Ships separately.
4. Once signed in, call that server's `bootstrap` once with the real harness (`claude-code`, `claude-code-cloud`, `codex-cloud`,
   `codex`, `cursor` or `cursor-cloud`), its version or `unknown`, a stable session id, only the
   models and capabilities this session really has, and `plugin_version`.
5. Read `plugin.status`. `current`: carry on. `outdated`: tell the person to update the Actionfleet
   plugin (see the plugin README's update controls) and follow the server's guides meanwhile.
   `unrecognized` or `not_reported`: follow the server's guides.
6. Resolve `required` checks one at a time and wait for the person where they must act; optional
   checks do not block work. Bootstrap's `recovery` lists Ships this connection still holds.
7. Read `get_guide` with topic `start`, then `work` before working a Ship and `coordinate` before
   fanning out work or messaging another Ship's crew. Report the required checks and the crew
   member bootstrap names, then stop: do not take a Ship unless asked.

A saved connection does not start a stopped chat, and installing this plugin dispatches nothing.
