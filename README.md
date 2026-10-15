# Action Fleet Plugin

Public installation resources for connecting an AI harness to Action Fleet:
guided setup, task execution and parallel coordination skills, the MCP connection package, and vendor compatibility
manifests. Work runs in the user's harness; Action Fleet coordinates durable
tasks through its authenticated MCP service.

This is an authoring scaffold. A verified MCP endpoint and real host acceptance
are required before publishing an installable release. No functioning server URL
or marketplace approval is implied by this repository.

## Package layout

`plugins/actionfleet/` is the canonical portable plugin and skill source. The
OpenAI extension declares the setup skill. The build creates the portable
`mcp.json`, Claude's `.mcp.json` and `.claude-plugin/plugin.json`, plus both
marketplace catalogs from that source. Skills are shared rather than forked.
Generated packages declare both public onboarding (`/public/mcp`, no application
authentication) and authorized work (`/mcp`, OAuth discovery and DCR). Host support
for onboarding before the private connection completes must be tested; public
onboarding can also be connected separately during account setup.

No account credentials, infrastructure secrets, customer data, backend source,
or privileged execution hooks belong in this repository. Installation does not
grant account access: the user connects through browser OAuth consent.

## Build a release candidate

Run the checks, then supply the actual verified HTTPS MCP URL:

```sh
python3 -m unittest discover -s tests
python3 scripts/build.py --mcp-url "$ACTIONFLEET_MCP_URL" --output /tmp/actionfleet-release
```

The build refuses credential-bearing URLs, endpoint query parameters, an existing
output directory, symlinks, and unexpected source files. It produces a complete
MCP-enabled plugin, marketplace catalogs, and a deterministic plugin ZIP. It does
not connect accounts, install dependencies, grant permissions, publish a release,
or submit anything to a vendor directory.

Validate the generated artifacts in actual hosts. In Claude Code:

```sh
claude plugin validate /tmp/actionfleet-release/plugins/actionfleet --strict
claude plugin validate /tmp/actionfleet-release --strict
```

For supported OpenAI clients, use the generated repo marketplace or import the
complete package through the supported workspace/private-plugin flow. Codex cloud
connection/installation is separate from editing local CLI configuration. A public
GitHub repository or custom marketplace is separate from an approved public
directory listing.

## User onboarding

The intended user experience is **Install Action Fleet Plugin**, then run setup.
The bundled skill discovers `bootstrap_harness`, supplies the actual harness name
and observed version, and guides the user through required setup. Optional
capabilities remain visible without blocking the basic task profile.

The work skill targets `actionfleet/1` and reads exact command data schemas
through `get_protocol_schema`. It covers connection-bound claim recovery,
guarded waiting/report/release, cooperative STOP and human verification of an
exact report/artifact. Check bootstrap protocol and deployment provenance before
using it. Updating this authoring source does not establish live/native release
acceptance or upgrade a running server.

The MCP has distinct public onboarding and account-authorized surfaces. Public
onboarding can link to signup/signin and explain the connection process; private
task access requires OAuth and the applicable server-side authorization. Missing
setup should lead to a concrete next action, never a request to paste passwords,
provider keys or access tokens into chat.

The skills cover Codex and Cursor through the same discovered task protocol.
Actual host installation, execution and native launch/resume must be tested
separately. Claude packaging remains compatibility preparation. No package pools
subscription allowances or supplies a launcher merely by being installed.

Use `setup` for connection/readiness, `work-task` for execution/recovery, and
`coordinate` for independent fan-out/fan-in. Each skill has a specific trigger;
ordinary chat questions do not require a coordination ceremony. The compact
tool guide and bootstrap tool guide expose the main tools without repeated
full discovery. Fleet owns task state; GitHub remains optional code/CI evidence.

For Fleet source edits, all harnesses follow the same
[mainline and delivery guide](https://github.com/actionfleetai/fleet/blob/main/docs/harness-mainline-workflow.md):
checkpoint, fetch/rebase, affected checks, freshness check, guarded push, source
registration and independent delivery receipts. The plugin points to the
repository's canonical instructions rather than inventing a second source policy.

## Release acceptance

- Confirm public onboarding, OAuth discovery, consent, revocation and account isolation.
- Confirm the plugin installs and invokes its setup skill in each supported host.
- Complete a native Codex cloud task through the deployed MCP and record the version.
- Test missing required setup, optional omissions, denied access and stale revisions.
- Keep release contents and the verified endpoint reproducible; publish explicit support status.
- Publish versioned tags/packages only after the complete MCP-enabled package passes.

Sources: [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins),
[OpenAI connection testing](https://developers.openai.com/plugins/deploy/connect-chatgpt),
[Claude manifest reference](https://code.claude.com/docs/en/plugins-reference), and
[Claude marketplaces](https://code.claude.com/docs/en/plugin-marketplaces).

Licensed under the [MIT License](LICENSE).
