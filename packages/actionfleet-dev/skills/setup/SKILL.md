---
name: setup
description: Use when connecting this harness to Actionfleet, right after installing this plugin, or after a reconnect. Signs in, bootstraps with this plugin's version and hands over to the server's own guides.
---

# Connect to Actionfleet

The Actionfleet MCP is the whole integration. This plugin only packages its connection so a host
can switch it on and off. The server's tools, their descriptions and its guides (`get_guide`) are
the source of truth. This plugin names only `bootstrap` and `get_guide`, so it stays right when the
server's other tools change; wherever it and the server differ, follow the server.

1. Read `references/installation.json` beside this skill: `name` is this plugin's MCP server,
   `mcp_url` its address and `plugin_version` this plugin's version. It is the plugin's only server.
2. Find that server's tools. When its `bootstrap` is missing, the person signs in once in the
   browser with their Actionfleet account:
   - Claude Code: `/mcp`, choose `plugin:<name>:<name>`, then Authenticate.
   - Codex: approve the sign-in Codex offers for this plugin, or run `codex mcp login <name>`.
   - Elsewhere: the host's MCP or connector settings.
   Then reload or start a new session if the tools still do not appear. Never ask for or paste
   passwords, tokens or secrets.
3. One connection per host. If this session also has another Actionfleet connection to the same
   address (added by hand or a claude.ai connector), use one, and tell the person they can remove
   the other: each connection is its own crew device and could claim Ships separately.
4. Call that server's `bootstrap` once, as its description says, with the real harness this
   session runs in (such as `claude-code`, `claude-code-cloud`, `codex`, `codex-cloud`, `cursor` or
   `cursor-cloud`), only the models and capabilities this session really has, and `plugin_version`
   from step 1.
5. Bootstrap's answer says whether this plugin matches the server. If it says the plugin is
   outdated, tell the person to update the Actionfleet plugin (the plugin README's update controls)
   and, until they do, follow the server's guides and tool descriptions, not this plugin's skills.
6. Read `get_guide('start')` and follow it: it explains bootstrap's answer, the checks to resolve
   first and the other guides. Report what is required and who must act, then stop: do not take a
   Ship unless asked.

A saved connection does not start a stopped chat, and installing this plugin dispatches nothing.
