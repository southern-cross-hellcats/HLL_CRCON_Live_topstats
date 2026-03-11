# Issues

## Current Findings

1. `get_top()` can reference `server_status` before assignment if `callmode` is not exactly `"chat"` or `"matchend"`.
2. Squad member display is broken in `get_top()` because the member lookup compares squad data against `unit_name` instead of the squad `name`.
3. `is_vip_for_less_than_xh()` has a contradictory docstring that does not match the real behavior.
4. VIP exclusion for ratio and killrate rankings is encoded indirectly via `second_data != "kills"`, which is brittle and unclear.
5. `killrate()` depends on a hard-coded `20` score-to-minutes conversion with no explanation or validation.
6. `stats_on_match_end()` can still post a Discord embed when the rendered message is just `"No stats yet"`.
7. `real_offdef()` treats `OFFENSEDEFENSE_RATIO == 0` as a special case even though the surrounding configuration comments make the scoring behavior ambiguous.
8. The module loads `RconServerSettingsUserConfig` at import time and silently swallows failures.
9. `get_top()` leaves `sortkey` untyped even though the module otherwise uses type hints.
10. `stats_gather()` calls `get_top()` repeatedly, and each match-end `get_top()` call fetches `rcon.get_status()` again, causing redundant remote calls.
11. `message_all_players()` swallows all exceptions, making delivery failures invisible.
12. `stats_on_match_end()` calls `get_server_number()` twice instead of reusing the earlier result.
13. `SERVER_CONFIG` accepts placeholder Discord webhook URLs with no validation or friendly configuration error.
14. `LOCAL_TIME_FORMAT` is computed at import time from `LANG`, which couples formatting to module initialization.
15. `stats_on_match_end()` indexes `SERVER_CONFIG` without checking that the current server number is in range.
16. The repository has no automated tests: no `tests/` directory, no test modules, and no configured test runner.

## Priority Order

1. Fix correctness bugs that affect runtime output or can crash the plugin.
2. Reduce repeated remote calls and weak configuration handling.
3. Add automated tests around score formatting and CRCON interaction boundaries.
