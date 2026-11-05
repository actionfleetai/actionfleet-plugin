# Actionfleet plugins

Install **Actionfleet Dev** to connect Codex or Cursor to the same durable
coordination service; Claude connects through one claude.ai connector instead
([Claude Code](#claude-code)). Work runs in your harness. Fleet records Ships,
claims, progress and independent delivery outputs; installation does not launch
a stopped chat or pool subscription allowances. The same marketplace offers
[opt-in skills](#opt-in-skills): `extras`, a plugin that holds skills only, for Claude too.

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
| Actionfleet Dev (`actionfleet-dev`) | `https://api.actionfleet.dev/mcp` | Active dev; native Codex, Claude and Cursor cloud task loops reported |
| Actionfleet (`actionfleet`) | `https://api.actionfleet.ai/mcp` | Prepared production profile; not installable until native harness acceptance |

These are the API's branded hosts. Their traffic moves to each environment's
promoted revision; an existing connection receives that revision without changing
its URL. Connections made on the earlier Cloud Run service URLs keep working (the
server lists them as aliases); reinstall or reconnect on the branded host when
convenient. Do not install `pr-*---` or `sha-*---` revision URLs as permanent
connections. Production promotion remains separate from main's dev rollout; a
production endpoint that answers discovery is not by itself an accepted harness
profile.

Existing **Actionfleet Dev** connections using the dev URL already receive server
updates. Use one connection per host: the plugin's server and a hand-added server
or claude.ai connector to the same address are separate crew devices that could
each claim Ships, so remove the one you do not use. Complete browser OAuth using the intended Fleet account.
No bearer tokens, client secrets or request headers are needed for normal DCR
setup. Each package carries one server, the authorized `/mcp`, which serves the
start tools (`bootstrap`, `get_guide`) once signed in. The same origin's
anonymous `/public/mcp` is not packaged; the endpoint checks below use it.

## Install

The Git marketplace is **actionfleetai/actionfleet-plugin**, tracking **main**.
It contains OpenAI, Claude and Cursor catalogs and complete packages with bundled
MCP definitions and shared skills. Public directory review/listing is a separate
step; this repository does not imply vendor approval.

### Codex

```sh
codex plugin marketplace add actionfleetai/actionfleet-plugin && codex plugin add actionfleet-dev@actionfleet && codex mcp login actionfleet-dev
```

Each command is safe to run again. `codex mcp login` opens the browser: approve with
your Fleet account, then start a new Codex session. Its first Actionfleet request
bootstraps; ask it to *set up this harness for Actionfleet* to have the onboarding
skill report the required checks now. Or install **Actionfleet Dev** from the app's
Plugins directory under the Actionfleet marketplace and approve the sign-in it offers.
`codex mcp login` registers `http://127.0.0.1:<port>/callback`, so the
server must allow `http://127.0.0.1/callback` (`scripts/configure_dev_callbacks.py
--harness codex` adds it to dev's list; deploy dev afterwards).

Each package carries a native `.codex-plugin/plugin.json`: Codex reads a root
`plugin.json` first and loads no MCP servers from it, so packages ship none. For
managed hosted workspaces, an administrator can import
`https://github.com/actionfleetai/actionfleet-plugin` through the workspace plugin
marketplace settings. Availability varies by surface and workspace policy.
Local CLI installation does not install a plugin into a Codex cloud chat. Until
that host's package import is available, keep the hosted custom MCP connection at
the stable dev URL and select it in the cloud chat.

### Claude Code

Connect Claude with one claude.ai connector. Claude's desktop app, the `claude` CLI
and claude.ai/code cloud sessions all load it, so one connection covers local and
cloud. Open the prefilled
[Add Actionfleet Dev to Claude](https://claude.ai/customize/connectors?modal=add-custom-connector&connectorName=Actionfleet%20Dev&connectorUrl=https%3A%2F%2Fapi.actionfleet.dev%2Fmcp)
link, or in Fleet choose Crew › Add crew › **Claude** › **Add to Claude**. Keep
**Sign in now** and **Register automatically**, add no request headers, then
**Connect** and approve with the same Fleet account as your other harnesses. A
session bootstraps on its first Actionfleet request; a connected connector is not
by itself proof that a cloud session ran Actionfleet tools, so check bootstrap from
that session.

**Don't also install this plugin in Claude.** Its server is a second connection to
the same address beside the connector, so Claude becomes a second crew device that
can claim Ships on its own, and a plugin installed on one computer never reaches
cloud sessions. Use the plugin only where Claude Code is not signed in to claude.ai
(connectors load only with a claude.ai login), instead of the connector:

```sh
claude plugin marketplace add actionfleetai/actionfleet-plugin && claude plugin install actionfleet-dev@actionfleet
```

Then, in a new session, open `/mcp`, choose `plugin:actionfleet-dev:actionfleet-dev`
and **Authenticate** in the browser (in a session that was already open, run
`/reload-plugins` first). `/actionfleet-dev:setup` reports the required checks on
demand. Turn on auto-update for the Actionfleet marketplace: third-party
marketplaces default to off ([updates and auto-update](#updates-and-auto-update)).

A repository prepared through the server's `get_guide("setup")` keeps its `.mcp.json`
entry for the GitHub Copilot app and lists it in `disabledMcpjsonServers` in
`.claude/settings.json`, so opening it in Claude Code adds nothing beside the
connector.

### Cursor

For a team marketplace, open Dashboard → **Plugins & MCPs** → Team Marketplaces →
**Add Marketplace** → **Import from Repo** and enter
`https://github.com/actionfleetai/actionfleet-plugin`. Review/add **Actionfleet
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

Without the plugin, Crew › Connections › **Connect harness** on the Fleet site has
**Add to Cursor** and **Install in VS Code** links that add the MCP alone.

The package includes the portable `mcp.json` and native
`.cursor-plugin/plugin.json`; every host uses the same skills. No CLI-only install step
is presented as proof that a Cursor cloud agent is connected.

## Opt-in skills

`extras` is one plugin in this marketplace that holds skills only. It carries no MCP
server, so it is safe beside the claude.ai connector or the Actionfleet plugin and
never becomes another crew device. Nothing installs it for you: installing it is the
opt-in, and uninstalling it opts out. Only each skill's description loads at the start
of a session; a skill's body loads when it is used, and its script runs without being
read into context.

| Skill | What it does |
| --- | --- |
| `skill-cards` | Writes and tightens agent skills: a description that fires on the right request, a few numbered steps, Python scripts for rules a program can decide, and its `check_card.py` for spec errors and bloat. |
| `session-titles` | Prefixes an Actionfleet chat's title with where it runs (💻 local, ☁️ cloud), its Ship ref (after its fleet's emoji, when it has one) and, once the work is known, its commit type, such as `☁️ 🚀 SHIP-12 fix: Login loop`. Its `title.py` owns the format. |
| `commit-messages` | Writes and checks commit messages as [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) (`type(scope)!: summary`, body, trailers), following each repository's own identity and trailer policy. Its `commit.py` owns the format and the types, and also runs as a commit-msg hook. |

Each line installs from this GitHub repository and works whether or not the
marketplace was added before; the update step brings an older copy up to date.

```sh
claude plugin marketplace add actionfleetai/actionfleet-plugin; claude plugin marketplace update actionfleet && claude plugin install extras@actionfleet
```

```sh
codex plugin marketplace add actionfleetai/actionfleet-plugin; codex plugin marketplace upgrade actionfleet && codex plugin add extras@actionfleet
```

```sh
copilot plugin marketplace add actionfleetai/actionfleet-plugin && copilot plugin install extras@actionfleet
```

In an open Claude Code session, run `/reload-plugins`; the skills are
`/extras:skill-cards`, `/extras:session-titles` and `/extras:commit-messages`. The plugin
stays on the version you installed until the marketplace refreshes
([updates and auto-update](#updates-and-auto-update)). Before November 2026 these were
three plugins; Claude reports each as "not found in marketplace" until it is removed
(`uninstall` takes one plugin at a time):

```sh
for p in skill-cards session-titles commit-messages; do claude plugin uninstall $p@actionfleet; done
```

Codex: the same loop with `codex plugin remove $p@actionfleet`.

If Claude says the marketplace's source doesn't match its `extraKnownMarketplaces`
entry, add it from the source that entry lists, or change the entry to
`{"source": "github", "repo": "actionfleetai/actionfleet-plugin"}`. In Cursor, install
**Actionfleet Extras** from the imported team marketplace; an admin who sets it to
**Default Off** leaves each member to opt in. Without a team marketplace, copy
`packages/extras` into `~/.cursor/plugins/local/extras` as a real folder and reload the
window. GitHub Copilot in VS Code reads marketplaces from `chat.plugins.marketplaces`
(with `chat.plugins.enabled`); that path is not yet checked. A plugin installed on one
computer doesn't reach claude.ai/code cloud sessions or Codex cloud tasks. An
organization can turn `extras` on for every claude.ai/code session through claude.ai's
managed Claude Code settings, but that enables it for everyone, so it is no longer
opt-in.

## What updates, and when

| Layer | Update path | Check |
| --- | --- | --- |
| Server behavior | Deploy/promote behind the stable environment URL | `bootstrap` → `deployment.source_sha` |
| MCP tool schemas | Host refresh/reconnect or new session; rediscover after deployment changes | Tool discovery (`get_tags`, `search`, `get_schema`) |
| Plugin and server in sync | Plugin release at or above the server's `plugin_minimum` | `bootstrap(plugin_version=…)` → `plugin.status`; CI endpoints job |
| Bundled skills/manifests | Versioned Git marketplace/plugin update | Installed plugin version and `skills/setup/references/installation.json` |
| Account access | Browser OAuth consent and normal token refresh | Required bootstrap checks and server-bound worker/scope |

Claude Code and Codex: see [updates and auto-update](#updates-and-auto-update).
Hosted Codex imports use their workspace sync controls. Claude's connector has no
plugin to update. Cursor's
team Auto Refresh updates the indexed package; use its update/reload controls and
confirm the installed version before claiming the session uses new skills.

### Updates and auto-update

Claude Code updates a plugin only after it refreshes its copy of the marketplace, and
it leaves auto-update off for third-party marketplaces such as this one. Until then
`/plugin` shows the version you installed, with **Update** greyed out, even after a
newer release. To update now:

```sh
claude plugin marketplace update actionfleet && claude plugin update extras@actionfleet
```

Then run `/reload-plugins` or start a new session. To keep plugins current, turn on
auto-update once in `/plugin` → **Marketplaces** → **actionfleet** → **Enable
auto-update**, or declare it in settings: `~/.claude/settings.json` for you, or a
repository's `.claude/settings.json` for everyone who opens that repository.

```json
{
  "extraKnownMarketplaces": {
    "actionfleet": {
      "source": { "source": "github", "repo": "actionfleetai/actionfleet-plugin" },
      "autoUpdate": true
    }
  }
}
```

Claude Code then refreshes the marketplace and the plugins installed from it at
startup; an update applies after `/reload-plugins` or a restart.

Codex refreshes every configured Git marketplace in the background when it starts and
reinstalls the plugins installed from it; there is no setting to turn on (checked in
Codex CLI 0.166). Start a new session to be sure it loaded an update. To update now:

```sh
codex plugin marketplace upgrade actionfleet
```

`codex plugin marketplace add` declares the marketplace in `~/.codex/config.toml`. A
repository's `.codex/config.toml` declares it for everyone who opens that repository,
once they trust the project (Codex skips an untrusted project's `.codex/`):

```toml
[marketplaces.actionfleet]
source_type = "git"
source = "https://github.com/actionfleetai/actionfleet-plugin.git"
```

Declaring the marketplace installs nothing in either host, so `extras` stays opt-in. Each
plugin keeps the version of the release where it last changed, so a plugin can show an
older version than the newest release; each release's notes list the plugins it changed.

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

`plugins/actionfleet/` is the core plugin's skill source; `plugins/extras/` is the
opt-in skills', with its reviewed files listed in `ADDONS` in `scripts/build.py`.
Each plugin keeps the version of the release where its package last changed, so hosts
offer an update only for plugins that changed. `profiles.json` declares the
environment endpoints and availability. Generate the tracked `packages/` and
three root marketplace catalogs after edits:

```sh
python3 scripts/catalog.py
python3 -m unittest discover -s tests
python3 scripts/catalog.py --check
python3 scripts/catalog.py --archives /tmp/actionfleet-release
```

Each profile's icon is Actionfleet's single ship (`icons/ship.svg`, the site's app
icon) on that profile's opaque `icon_background`: navy for Actionfleet and the
brand's blue wing (`#1f7cf2`) for Actionfleet Dev, so the two read apart. After
changing the art or a color, run `python3 scripts/icons.py` (needs `rsvg-convert`)
to render `icons/<name>.png` at 512 px; the tests check each PNG's size and
background. Packages carry it as `assets/icon.png`, named by Codex's
`interface.logo` and `composerIcon`, Cursor's `logo` and Claude's `icon` (read by
Anthropic's directory listing; Claude Code ignores it).

`python3 scripts/check_codex_package.py` asks a real Codex (`codex app-server`,
throwaway `CODEX_HOME`, no sign-in) what it loads from each package and fails
unless its one MCP server, the three skills, the onboarding skill and its icon appear, and
unless `extras` loads its skills and icon with no MCP server; CI runs
it with a pinned Codex. Never hand-edit generated packages.

Commit subjects are Conventional Commits (the `commit-messages` skill in `extras`;
`git config core.hooksPath .githooks` checks each one as you commit). To land, run
`python3 scripts/land.py`: it rebases on main, checks commits not yet pushed anywhere,
allocates a release only when a package changed (`release_version.py bump` sets that
release's version on the changed plugins alone and regenerates packages), runs the
checks, and repeats if main moves. It pushes nothing; push main when it prints `ready`.
CI refuses package changes on main without a release (`release_version.py check`) and
publishes the release with notes generated from commit subjects by
[git-cliff](https://git-cliff.org) (`cliff.toml`). Releases
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
