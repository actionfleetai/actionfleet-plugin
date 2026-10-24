import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from probe_endpoints import probe
from skills import skill_tools, snapshot

PROFILE = {'channel': 'dev', 'mcp_url': 'https://dev.example.com/mcp', 'installable': True}


def responses(issuer='https://dev.example.com', private_status=401, tools=None, minimum=None):
    known = snapshot()
    catalog = {'protocol': 'actionfleet/2', 'tools': known['tools'] if tools is None else tools,
               'guides': known['guides'], 'plugin_minimum': minimum or known['plugin_minimum']}

    def fetch(url, payload=None):
        if url.endswith('/oauth-authorization-server'):
            return {'status': 200, 'json': {'issuer': issuer,
                'authorization_endpoint': issuer + '/authorize', 'token_endpoint': issuer + '/token',
                'registration_endpoint': issuer + '/register', 'code_challenge_methods_supported': ['S256']}}
        if '/oauth-protected-resource/' in url:
            return {'status': 200, 'json': {'resource': PROFILE['mcp_url'], 'authorization_servers': [issuer]}}
        if url.endswith('/public/mcp'):
            assert payload['params']['arguments']['plugin_version']  # The probe reports this plugin's version.
            return {'status': 200, 'json': {'result': {'structuredContent': {'catalog': catalog}}}}
        return {'status': private_status, 'challenge': 'Bearer resource_metadata="https://dev.example.com/.well-known/oauth-protected-resource/mcp"'}
    return fetch


class EndpointContractTests(unittest.TestCase):
    def test_rejects_cross_environment_discovery_and_anonymous_private_access(self):
        self.assertTrue(probe(PROFILE, responses())['anonymous_contract_ready'])
        self.assertFalse(probe(PROFILE, responses('https://prod.example.com'))['anonymous_contract_ready'])
        self.assertFalse(probe(PROFILE, responses(private_status=200))['anonymous_contract_ready'])

    def test_fails_when_the_live_server_lacks_a_skill_tool_or_needs_a_newer_plugin(self):
        ready = probe(PROFILE, responses())
        self.assertTrue(ready['catalog']['snapshot_current'])
        self.assertEqual(ready['catalog']['missing_tools'], [])
        gone = sorted(skill_tools())[0]
        missing = probe(PROFILE, responses(tools=[t for t in snapshot()['tools'] if t != gone]))
        self.assertFalse(missing['anonymous_contract_ready'])
        self.assertEqual(missing['catalog']['missing_tools'], [gone])
        newer = probe(PROFILE, responses(minimum='2999.101.1'))
        self.assertFalse(newer['checks']['plugin_meets_server_minimum'])
        self.assertFalse(newer['anonymous_contract_ready'])
        # A server that only adds tools still passes; the snapshot just needs a refresh.
        added = probe(PROFILE, responses(tools=snapshot()['tools'] + ['new_tool']))
        self.assertTrue(added['anonymous_contract_ready'])
        self.assertFalse(added['catalog']['snapshot_current'])

    def test_unconfigured_profile_has_explicit_failure_without_claiming_native_acceptance(self):
        result = probe({'channel': 'prod', 'mcp_url': 'https://prod.example.com/mcp', 'installable': False},
                       lambda *args: {'status': 404})
        self.assertFalse(result['anonymous_contract_ready'])
        self.assertFalse(result['native_consent_tested'])
        self.assertEqual(result['http']['authorization'], 404)
