# Action Fleet plugins

Install **Action Fleet Dev** to connect Codex, Claude Code or Cursor to the same
durable coordination service. Work runs in your harness. Fleet records Ships,
claims, progress and independent delivery outputs; installation does not launch
a stopped chat or pool subscription allowances.

**The MCP is the integration; this plugin is optional.** Any host that takes MCP
servers gets everything from the MCP alone: its instructions, tool descriptions,
bootstrap's `tool_guide` and `get_guide` (`start`, `work`, `coordinate`). The plugin
packages that connection so a host can switch it on and off, with thin skills that
defer to the server. Keep them in sync:

- The setup skill passes this plugin's version to `bootstrap` (`plugin_version`);
  `plugin.status` is `outdated` when the server needs a newer plugin. Agents then
  follow the server and ask the user to update.
- CI's endpoints job reads the live public catalog and fails when a skill names a
  tool the server lacks or the server needs a newer plugin than this one.
  `server-tools.json` is the offline snapshot the unit tests use; refresh it when
  the server's tools change.

## Stable connections

| Package | Stable MCP URL | Availability |
| --- | --- | --- |
| Action Fleet Dev (`actionfleet-dev`) | `https://af-platform-api-nzjgusc4sq-uw.a.run.app/mcp` | Active dev; native Codex, Claude and Cursor cloud task loops reported |
| Action Fleet (`actionfleet`) | `https://af-platform-api-qk3fflod5q-uw.a.run.app/mcp` | Prepared production profile; unavailable until OAuth activation and acceptance |

These are the untagged Cloud Run **service** URLs. Their traffic moves to each
environment's promoted revision; an existing connection receives that revision
without changing its URL. Do not install `pr-*---` or `sha-*---` revision URLs as
permanent connections. Production promotion remains separate from main's dev
rollout. The production service URL is inventory-confirmed, but that alone does
not mean its MCP/OAuth service is active.

Existing **Actionfleet Dev** connections using the dev URL already receive server
updates. Keep them while testing plugin installation; avoid duplicate task claims
from two connections. Complete browser OAuth using the intended Fleet account.
No bearer tokens, client secrets or request headers are needed for normal DCR
setup. Public onboarding lives at the same origin's `/public/mcp`; authorized
work lives at `/mcp`.

## Install

The Git marketplace is **actionfleetai/actionfleet-plugin**, tracking **main**.
It contains OpenAI, Claude and Cursor catalogs and complete packages with bundled
MCP definitions and shared skills. Public directory review/listing is a separate
step; this repository does not imply vendor approval.

### Codex

For clients supporting Git marketplaces:

```sh
codex plugin marketplace add actionfleetai/actionfleet-plugin --ref main
```

Then install **Action Fleet Dev** from the app's Plugins directory under the
Action Fleet marketplace. For managed hosted workspaces, an administrator can
import `https://github.com/actionfleetai/actionfleet-plugin` through the workspace
plugin marketplace settings. Availability varies by surface and workspace policy.
Local CLI installation does not install a plugin into a Codex cloud chat. Until
that host's package import is available, keep the hosted custom MCP connection at
the stable dev URL and select it in the cloud chat.

### Claude Code

```sh
claude plugin marketplace add actionfleetai/actionfleet-plugin
claude plugin install actionfleet-dev@actionfleet
```

Enable **auto-update** for the Action Fleet marketplace in `/plugin` →
Marketplaces. Third-party marketplaces default to auto-update off. Install and
authenticate through your browser; inspect `/mcp` if a bundled server needs consent.

Claude Code **cloud** does not inherit a plugin installed on your local computer.
For the cloud-first path, add **Action Fleet Dev** at
[Claude connectors](https://claude.ai/customize/connectors) with the dev URL:
**Sign in now**, **Register automatically**, no custom headers. Use the same
Fleet login as your other harness. Connector availability and packaged skill
availability are separate; use your organization's supported cloud plugin
distribution when available. A successful Claude chat connector is not yet proof
of Claude Code cloud tool execution.

### Cursor

For a team marketplace, open Dashboard → **Plugins & MCPs** → Team Marketplaces →
**Add Marketplace** → **Import from Repo** and enter
`https://github.com/actionfleetai/actionfleet-plugin`. Review/add **Action Fleet
Dev**, save access settings, and install it from Cursor's plugin UI. Enable
**Auto Refresh** for the GitHub import; the Cursor GitHub App needs access to this
public repository. Refresh the marketplace manually if that option is unavailable.
Cursor batches automatic re-indexing to at most once every ten minutes; use
**Refresh** when testing a just-pushed package.
Cloud Agents must also have the MCP/connector available in their own environment.

For the standalone cloud path, open [Cursor Agents](https://cursor.com/agents),
use its **MCP dropdown** to add a custom **HTTP** server with the stable dev URL,
and complete OAuth with your Fleet login. Shared servers can also be configured
under **Team MCP Servers** in Dashboard → Plugins & MCPs. The dev
server must allow `https://www.cursor.com/agents/mcp/oauth/callback`. Desktop's
`http://localhost:8787/callback` is covered by the configured localhost callback
with an ephemeral port. No static OAuth client or bearer secret is required.

The package includes the portable `plugin.json`/`mcp.json` and native
`.cursor-plugin/plugin.json`; both use the same skills. No CLI-only install step
is presented as proof that a Cursor cloud agent is connected.

## What updates, and when

| Layer | Update path | Check |
| --- | --- | --- |
| Server behavior | Deploy/promote behind the stable environment URL | `bootstrap` → `deployment.source_sha` |
| MCP tool schemas | Host refresh/reconnect or new session; rediscover after deployment changes | Tool discovery (`get_tags`, `search`, `get_schema`) |
| Plugin and server in sync | Plugin release at or above the server's `plugin_minimum` | `bootstrap(plugin_version=…)` → `plugin.status`; CI endpoints job |
| Bundled skills/manifests | Versioned Git marketplace/plugin update | Installed plugin version and `skills/setup/references/installation.json` |
| Account access | Browser OAuth consent and normal token refresh | Required bootstrap checks and server-bound worker/scope |

For Codex, refresh the repo snapshot with `codex plugin marketplace upgrade
actionfleet` and apply the plugin update in the supported app UI; hosted imports
use their workspace sync controls. For Claude Code, use `claude plugin update
actionfleet-dev@actionfleet`, then `/reload-plugins` or a new session. Refreshing a
marketplace listing alone does not guarantee installed skills changed. Cursor's
team Auto Refresh updates the indexed package; use its update/reload controls and
confirm the installed version before claiming the session uses new skills.

Do not recreate OAuth connections for ordinary deployments. A future custom
domain migration must deliberately preserve/change the OAuth issuer, resource
audience and registrations together; a redirect or DNS alias alone is not a
tested OAuth migration. Current service URLs remain stable throughout that work.

## Use the tools

Run `setup` once per new session/reconnect to bootstrap with this plugin's version.
`work-task` and `coordinate` are short forms of the server's `get_guide` topics
`work` and `coordinate`: crew, checkpoint and report Ships; open Convoys, delegate
to a child Ship and message related Ships through tunnels. Where a skill and the
server differ, the server wins. Preserve claim/STOP checks and human verification of
an exact report. GitHub is source/CI, not Fleet's coordination queue. Normal chat
questions do not need a Ship.

Bootstrap with the actual harness **before the first claim**, including
`cursor-cloud` for Cursor Cloud Agents. If a connection's harness label is wrong,
rerun bootstrap from that same harness with the correct name; recreating OAuth
is unnecessary. The worker identity belongs to the authenticated connection;
harness/version/session labels are client observations. Historical task reports
retain the labels recorded when those events happened.

## Build, verify and release

`plugins/actionfleet/` is the only skill source. `profiles.json` declares the
environment endpoints and availability. Generate the tracked `packages/` and
three root marketplace catalogs after edits:

```sh
python3 scripts/catalog.py
python3 -m unittest discover -s tests
python3 scripts/catalog.py --check
python3 scripts/catalog.py --archives /tmp/actionfleet-release
```

Never hand-edit generated packages. Before a package release, run
`python3 scripts/release_version.py bump` after fetching/rebasing main. It updates
`release.json`, the canonical manifest and generated packages together. Releases
use the **Los Angeles date plus build**, matching the mobile date convention:
`2026.10.15 (1)` is plugin version `2026.1015.1` (`year.monthday.build`). Build 2
is `2026.1015.2`; October 16 build 1 is `2026.1016.1`. January 5 uses `2026.105.1`
without a leading zero, preserving valid semantic version ordering. The plugin's
counter is independent of each mobile app's store counter. `+build` metadata is
not used for ordering because semantic version comparisons ignore it.

Same-day releases increment the build; a new Los Angeles date starts at build 1.
The saved identity is used throughout CI, even across midnight. Fetch/rebase
before allocating; conflicting releases must allocate another build, never
overwrite an existing tag. CI checks date/version consistency, generated drift, package
isolation and reproducibility, validates the real packages/catalog with Claude's
CLI, and anonymously probes each configured endpoint. Active profiles must pass
discovery/issuer/resource/PKCE/auth-challenge checks. Inactive production failures
remain visible in the endpoint artifact and do not block dev publication. These
checks do not register OAuth clients, consent, read private data or modify tasks.

On main, passing checks publish an immutable versioned prerelease with active
package ZIPs and `SHA256SUMS`. Existing versions cannot be overwritten with changed
package contents. Git marketplace consumers track main; pinned tags/ZIPs stay
pinned until deliberately updated. Production is excluded from Claude/Cursor's
installable catalogs and marked `NOT_AVAILABLE` in OpenAI's catalog until its
profile is activated. Prepared production files are for operator review.

To activate production, first verify production Firebase/account scope, OAuth
issuer/resource, intended callback allowlist, durable storage and native harness
canary through the separate production rollout. Then set `installable: true`,
allocate a new date/build release, regenerate and publish. No dev account identifiers,
tokens, task IDs or callbacks are automatically copied into production.

Sources: [OpenAI packaging](https://developers.openai.com/plugins/build/plugins),
[OpenAI workspace marketplace sync](https://help.openai.com/en/articles/20001504-importing-and-syncing-plugin-marketplaces-from-github),
[Claude plugin installation/updates](https://code.claude.com/docs/en/discover-plugins),
[Cursor plugins](https://cursor.com/docs/plugins) and
[Cursor manifest reference](https://cursor.com/docs/reference/plugins).

Licensed under the [MIT License](LICENSE).
