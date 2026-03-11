# Issues

## Current Findings

1. Resolved: `get_top()` now validates `callmode` instead of relying on possibly unbound locals.
2. Resolved: squad member display now matches players against the current squad correctly.
3. Resolved: `is_vip_for_less_than_xh()` has a corrected docstring.
4. Resolved: VIP-award eligibility is now explicit instead of inferred from `second_data`.
5. Resolved: score-to-minutes conversion now uses `SCORE_PER_MINUTE`.
6. Resolved: match-end Discord posts now stop when the message is only `"No stats yet"`.
7. Resolved: score multipliers are normalized consistently through `normalized_ratio()`.
8. Resolved: CRCON settings are loaded lazily instead of at import time.
9. Resolved: ranking helpers now include type hints.
10. Resolved: match status is fetched once and reused across rankings.
11. Resolved: message and webhook delivery failures are logged instead of silently ignored.
12. Resolved: `stats_on_match_end()` now reuses the existing server number.
13. Resolved: Discord webhook config is validated before use.
14. Resolved: VIP time formatting is computed at runtime for the current language.
15. Resolved: Discord server config lookup is range-checked.
16. Resolved: the repository now includes an initial `unittest` test suite under `tests/`.
17. Resolved: plugin configuration can now be supplied through environment variables instead of editing constants directly.
18. Remaining follow-up: extend tests beyond pure helpers into mocked `Rcon` flows such as match-end VIP awarding and Discord posting.

## Priority Order

1. Extend automated coverage around CRCON-facing flows.
2. Consider a dedicated config object instead of module-level variables.
3. Consider splitting the single plugin file into config, ranking, and integration sections.
