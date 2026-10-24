# Tools (the server decides)

A map, not a contract: the deployed server's tools and their descriptions decide, and
`get_guide` (`start`, `work`, `coordinate`) serves the full guides. This plugin's CI checks every
tool named here against the live server's public catalog.

| Need | Tools |
| --- | --- |
| Connect | `bootstrap`, `whoami`, `get_guide` |
| Find and read Ships | `list_ships`, `get_ship`, `get_ship_actions`, `get_convoy` |
| Open Ships | `new_ship`, `new_ships` |
| Hold a Ship | `crew_ship`, `update_ship`, `report_ship`, `release_ship`, `block_ship` |
| Relate and stop | `set_blocked_by`, `stop_ship` |
| Talk to related Ships | `send_tunnel`, `read_tunnel` |
| Deliver | `register_ship_payload`, `record_ship_port_result`, `get_ship_payload`, `list_ship_payloads` |
| Cloud crews and budgets | `dispatch_convoy`, `get_convoy_dispatch`, `get_ship_budget`, `request_ship_budget` |

`bootstrap`, `whoami`, `list_services` and `get_guide` are called directly. Find the rest with
`search` and `get_schema`, and run them in `execute` with `await call_tool(name, params)`.
