import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from configure_dev_callbacks import DEV_ORIGIN, updated


class CallbackTests(unittest.TestCase):
    def test_append_preserves_other_fields_and_existing_callbacks_and_is_idempotent(self):
        old = {'ACTIONFLEET_MCP_ENABLED': 'true', 'ACTIONFLEET_API_URL': DEV_ORIGIN,
               'ACTIONFLEET_WEB_URL': 'https://af-platform-web-nzjgusc4sq-uw.a.run.app',
               'FLEET_PROTOCOL_ENABLED': 'true', 'secret_references': {'opaque': 'preserved'},
               'ACTIONFLEET_OAUTH_REDIRECT_URIS': json.dumps([
                   'https://chatgpt.com/connector_platform_oauth_redirect',
                   'https://claude.ai/api/mcp/auth_callback', 'http://localhost/callback'])}
        result, unchanged = updated(json.dumps(old), 'cursor')
        self.assertFalse(unchanged)
        self.assertEqual(json.loads(result['ACTIONFLEET_OAUTH_REDIRECT_URIS']),
                         json.loads(old['ACTIONFLEET_OAUTH_REDIRECT_URIS']) +
                         ['https://www.cursor.com/agents/mcp/oauth/callback'])
        for key in old.keys() - {'ACTIONFLEET_OAUTH_REDIRECT_URIS'}:
            self.assertEqual(old[key], result[key])
        again, unchanged = updated(json.dumps(result), 'cursor')
        self.assertTrue(unchanged)
        self.assertEqual(again, result)

    def test_refuses_other_environment_and_malformed_callbacks(self):
        for origin, callbacks in [('https://api.actionfleet.ai', '["http://localhost/callback"]'),
                                  (DEV_ORIGIN, '[]'), (DEV_ORIGIN, '["https://user:secret@example.com/callback"]')]:
            with self.subTest(origin=origin, callbacks=callbacks), self.assertRaises(ValueError):
                updated(json.dumps({'ACTIONFLEET_MCP_ENABLED': 'true', 'ACTIONFLEET_API_URL': origin,
                                    'ACTIONFLEET_OAUTH_REDIRECT_URIS': callbacks}), 'cursor')
