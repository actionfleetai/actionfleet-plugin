#!/usr/bin/env python3
"""Bounded anonymous endpoint contracts. No registration, consent or Ship writes.

Besides OAuth discovery, the public onboarding bootstrap returns the server's tool catalog: an installable
profile fails when the live server lacks a tool the skills name or needs a newer plugin than this one."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import build_opener, HTTPRedirectHandler, Request

from catalog import profiles
from release_version import read_release
from skills import skill_tools, snapshot, version as parse_version


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def read(url, payload=None):
    headers = {'Accept': 'application/json, text/event-stream',
               'User-Agent': 'actionfleet-plugin-endpoint-check/1'}
    data = None if payload is None else json.dumps(payload).encode()
    if data is not None:
        headers['Content-Type'] = 'application/json'
    try:
        with build_opener(NoRedirect).open(Request(url, data=data, headers=headers), timeout=12) as response:
            raw = response.read(128 * 1024 + 1)
            if len(raw) > 128 * 1024:
                return {'status': response.status, 'error': 'response_too_large'}
            try:
                body = json.loads(raw)
            except (ValueError, UnicodeError):
                body = None
            return {'status': response.status, 'json': body,
                    'challenge': response.headers.get('WWW-Authenticate', '')}
    except HTTPError as error:
        return {'status': error.code, 'challenge': error.headers.get('WWW-Authenticate', '')}
    except (OSError, URLError):
        return {'status': None, 'error': 'network_or_tls_unavailable'}


def probe(profile, fetch=read, *, plugin_version=None, needed=None, known=None):
    origin = profile['mcp_url'][:-4]
    plugin_version = plugin_version or read_release()['version']
    needed = skill_tools() if needed is None else needed
    known = snapshot() if known is None else known
    auth = fetch(origin + '/.well-known/oauth-authorization-server')
    resource = fetch(origin + '/.well-known/oauth-protected-resource/mcp')
    protected = fetch(profile['mcp_url'], {
        'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {'protocolVersion': '2025-03-26', 'capabilities': {},
                   'clientInfo': {'name': 'actionfleet-endpoint-check', 'version': '1'}},
    })
    public = fetch(origin + '/public/mcp', {
        'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call',
        'params': {'name': 'bootstrap', 'arguments': {'harness': 'unknown', 'version': 'endpoint-check',
                                                      'session_id': 'plugin-endpoint-check', 'plugin_version': plugin_version}},
    })
    meta = auth.get('json') or {}
    res = resource.get('json') or {}
    result = (public.get('json') or {}).get('result') or {}
    live = (result.get('structuredContent') or {}).get('catalog') or {}
    tools = set(live.get('tools') or [])
    minimum = parse_version(live.get('plugin_minimum'))
    checks = {
        'oauth_discovery': auth['status'] == 200 and str(meta.get('issuer', '')).rstrip('/') == origin,
        'oauth_endpoints': all(str(meta.get(k, '')).startswith(origin + '/') for k in
                               ('authorization_endpoint', 'token_endpoint', 'registration_endpoint')),
        'pkce_s256': 'S256' in meta.get('code_challenge_methods_supported', []),
        'protected_resource': resource['status'] == 200 and res.get('resource') == profile['mcp_url']
                              and [str(s).rstrip('/') for s in res.get('authorization_servers', [])] == [origin],
        'private_requires_oauth': protected['status'] == 401 and
                                  'resource_metadata=' in protected.get('challenge', ''),
        'catalog_has_skill_tools': bool(tools) and set(needed) <= tools,
        'plugin_meets_server_minimum': minimum is not None and parse_version(plugin_version) >= minimum,
    }
    return {'channel': profile['channel'], 'endpoint': profile['mcp_url'],
            'installable': profile['installable'], 'anonymous_contract_ready': all(checks.values()),
            'checks': checks, 'http': {'authorization': auth['status'],
                                     'resource': resource['status'], 'private': protected['status'], 'public': public['status']},
            'catalog': {'plugin_version': plugin_version, 'plugin_minimum': live.get('plugin_minimum'),
                        'missing_tools': sorted(set(needed) - tools),
                        # Informational: refresh server-tools.json when the server's tools change.
                        'snapshot_current': sorted(tools) == sorted(known['tools']) and live.get('plugin_minimum') == known['plugin_minimum']},
            'native_consent_tested': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(probe, profiles()))
    args.output.write_text(json.dumps({'results': results}, indent=2) + '\n')
    print(json.dumps({'results': results}, indent=2))
    raise SystemExit(1 if any(p['installable'] and not p['anonymous_contract_ready'] for p in results) else 0)
