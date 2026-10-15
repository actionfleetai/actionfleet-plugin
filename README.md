# Action Fleet Plugin

Public installation resources for connecting an AI harness to Action Fleet:
guided setup skills, the MCP connection package, and vendor compatibility
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

The MCP has distinct public onboarding and account-authorized surfaces. Public
onboarding can link to signup/signin and explain the connection process; private
task access requires OAuth and the applicable server-side authorization. Missing
setup should lead to a concrete next action, never a request to paste passwords,
provider keys or access tokens into chat.

Phase 1 validates Codex cloud. A second Codex subscription is Phase 2. Cursor is
Phase 3. Claude packaging is prepared for compatibility testing; it does not
establish a validated Claude execution harness or combine subscription allowances.

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
