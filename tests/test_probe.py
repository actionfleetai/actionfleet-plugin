import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from probe_endpoints import probe


class EndpointContractTests(unittest.TestCase):
    def test_rejects_cross_environment_discovery_and_anonymous_private_access(self):
        profile = {'channel': 'dev', 'mcp_url': 'https://dev.example.com/mcp', 'installable': True}
        def responses(issuer, private_status):
            def fetch(url, payload=None):
                if url.endswith('/oauth-authorization-server'):
                    return {'status': 200, 'json': {'issuer': issuer,
                        'authorization_endpoint': issuer + '/authorize', 'token_endpoint': issuer + '/token',
                        'registration_endpoint': issuer + '/register', 'code_challenge_methods_supported': ['S256']}}
                if '/oauth-protected-resource/' in url:
                    return {'status': 200, 'json': {'resource': profile['mcp_url'], 'authorization_servers': [issuer]}}
                return {'status': private_status, 'challenge': 'Bearer resource_metadata="https://dev.example.com/.well-known/oauth-protected-resource/mcp"'}
            return fetch
        self.assertTrue(probe(profile, responses('https://dev.example.com', 401))['anonymous_contract_ready'])
        self.assertFalse(probe(profile, responses('https://prod.example.com', 401))['anonymous_contract_ready'])
        self.assertFalse(probe(profile, responses('https://dev.example.com', 200))['anonymous_contract_ready'])

    def test_unconfigured_profile_has_explicit_failure_without_claiming_native_acceptance(self):
        result = probe({'channel': 'prod', 'mcp_url': 'https://prod.example.com/mcp', 'installable': False},
                       lambda *args: {'status': 404})
        self.assertFalse(result['anonymous_contract_ready'])
        self.assertFalse(result['native_consent_tested'])
        self.assertEqual(result['http']['authorization'], 404)
