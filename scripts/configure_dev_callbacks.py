#!/usr/bin/env python3
"""Append known harness callbacks to the existing DEV variable, with backup/readback.

Uses the caller's gh authentication. Does not configure production or deploy.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import urlsplit

VARIABLE = 'ACTIONFLEET_CONFIG_DEV'
RESOURCE = 'repos/actionfleetai/fleet/actions/variables/' + VARIABLE
CALLBACKS = {
    'cursor': ['https://www.cursor.com/agents/mcp/oauth/callback', 'http://localhost/callback'],
    'claude': ['https://claude.ai/api/mcp/auth_callback', 'http://localhost/callback'],
}
DEV_ORIGIN = 'https://af-platform-api-nzjgusc4sq-uw.a.run.app'


def updated(raw, harness):
    original = json.loads(raw)
    if not isinstance(original, dict) or original.get('ACTIONFLEET_MCP_ENABLED') != 'true':
        raise ValueError('Expected an existing active development configuration.')
    if original.get('ACTIONFLEET_API_URL') != DEV_ORIGIN:
        raise ValueError('Refusing to edit a different issuer or environment.')
    value = json.loads(original['ACTIONFLEET_OAUTH_REDIRECT_URIS'])
    if not isinstance(value, list) or not value or any(not isinstance(v, str) for v in value):
        raise ValueError('Expected the existing callback list encoded as a JSON string.')
    for uri in value:
        parsed = urlsplit(uri)
        _ = parsed.port
        if (any(c.isspace() for c in uri) or not parsed.hostname or parsed.username or parsed.password
                or parsed.fragment or parsed.scheme not in {'https', 'http'}
                or parsed.scheme == 'http' and parsed.hostname not in {'localhost', '127.0.0.1', '::1'}):
            raise ValueError('Existing callback configuration is invalid; inspect manually.')
    callbacks = value + [v for v in CALLBACKS[harness] if v not in value]
    result = {**original, 'ACTIONFLEET_OAUTH_REDIRECT_URIS': json.dumps(callbacks)}
    if {k: v for k, v in result.items() if k != 'ACTIONFLEET_OAUTH_REDIRECT_URIS'} != {
            k: v for k, v in original.items() if k != 'ACTIONFLEET_OAUTH_REDIRECT_URIS'}:
        raise ValueError('Unexpected configuration change.')
    return result, callbacks == value


def gh(*args, body=None):
    run = subprocess.run(['gh', *args], input=body, text=True, capture_output=True, check=False)
    if run.returncode:
        raise RuntimeError('GitHub request failed; check gh authentication and repository Variables access. No credential output is printed.')
    return run.stdout


def configure(harness):
    raw = json.loads(gh('api', RESOURCE))['value']
    result, unchanged = updated(raw, harness)
    backup_dir = Path(tempfile.mkdtemp(prefix='actionfleet-dev-callbacks-'))
    backup = backup_dir / 'ACTIONFLEET_CONFIG_DEV.json'
    with backup.open('x', opener=lambda path, flags: os.open(path, flags, 0o600)) as file:
        file.write(raw)
    print('Backup: ' + str(backup))
    if not unchanged:
        if json.loads(gh('api', RESOURCE))['value'] != raw:
            raise RuntimeError('Configuration changed concurrently; no write made. Inspect and rerun.')
        gh('api', '--method', 'PATCH', RESOURCE, '--input', '-',
           body=json.dumps({'name': VARIABLE, 'value': json.dumps(result)}))
    readback = json.loads(json.loads(gh('api', RESOURCE))['value'])
    if readback != result:
        raise RuntimeError('Readback differs; keep the backup and inspect before deployment.')
    print('VERIFIED: ' + harness + ' dev callbacks configured; ready for dev-only deployment.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--harness', choices=sorted(CALLBACKS), required=True)
    args = parser.parse_args()
    try:
        configure(args.harness)
    except (ValueError, KeyError, TypeError, RuntimeError, OSError) as error:
        parser.exit(1, str(error) + '\n')
