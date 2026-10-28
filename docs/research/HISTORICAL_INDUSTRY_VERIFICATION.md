# Investigation verification record

2026-10-28. Baseline repository commit `046877e`.

| Check | Result |
|---|---|
| JGRPP source pin | `jgrpp-0.73.4` resolves to `cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8`; inspected actual C++ headers and command implementations. |
| AXIS source pin | Release commit `11c8353ccf7444b143e57080b1aa2b5e38839a23`, explicitly checked out instead of current HEAD. |
| Upstream distinction | OpenTTD 15.0 headers also expose BuildIndustry, ResolveNewGRFID, SetControlFlags, NO_CLOSURE and SetProductionLevel; these are not unique JGRPP APIs. |
| Metadata extraction | Executed `scripts/extract_axis_industry_matrix.py` with bundled Python. 91 enabled Classic industry types, 64 cargo slots. |
| Metadata invariants | 91 unique local IDs; coal_mine local ID 0; matrix table covers exactly the extracted identifiers. |
| Python syntax | `python -m py_compile scripts/extract_axis_industry_matrix.py` passed. |
| Probe static API-symbol audit | All 20 distinct qualified method names in main.nut were found in the corresponding pinned headers. The industry-type class is exposed to game API. List constructors/iteration were inspected in their headers. |
| Registration review | Required info methods, `default_value` setting field and API `16` support checked against `script_info.cpp`, `script_info_docs.hpp` and `game_info.hpp`. |
| Whitespace and change scope | `git diff --check`; only research documents, extractor, isolated probe, ignore rules and documentation-index additions intended. Existing scenarios, NewGRFs and map data untouched. |

Extracted JSON SHA256:
`c1d8357ac01f927089d993c5b5ac6188f28c801163d607986d498cae101948d0`.

The source extractor uses the original AXIS model methods and inherited economy
overrides. Only `chameleon.PageTemplateLoader` and unused messaging utilities
are stubbed; no rendering/build is attempted. This is executable source metadata
extraction, not verification that the user's installed GRF matches that source.
Upstream checkouts are local ignored research inputs, not vendored dependencies.

**Not tested:** Squirrel parsing/compilation, GameScript registration/loading in
JGRPP, construction, output volumes, editor persistence, settings interaction in
a running game, save/reload, multiplayer determinism or long-campaign performance.
Header-symbol checks cannot establish correct Squirrel syntax, argument binding
or runtime behavior. No successful build or completed in-game proof is claimed.

Reproducible next test protocol is in the
[probe README](../../prototypes/historical_industry_poc/README.md).
