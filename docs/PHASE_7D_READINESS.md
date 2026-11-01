# Phase 7D — readiness

**READY WITH CAVEATS** for development playtesting. Modern construction is fixed without changing Historical AXIS; long-horizon economic balance and every regional event are not certified.

## Playable candidate

`C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.6.0 - Phase 7D Progression.scn`

SHA-256: `8eb114a0a4b4ea95363b810bfc815c0b30998e254399ff0d0dad8574e8456ec9`

Use **GS v4/schema 4** with the unchanged AXIS **0.6.0** GRF (SHA-256 `023099757b94573f33e0c8380804cdbe80d3155b914d5441f98e89e55c9d8b84`). Initial map: **617 towns, 542 industries, 64 cargos, 15 identical GRF references, seven-tile trains, calendar 1830/economy 1800**. All initial map planes, town/industry records, settings and industry storage match Phase 7C.

From the repository on this development PC:

```powershell
& 'C:/Users/Kladd/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' scripts/lifecycle_phase7d_launch.py
```

Add `--verify-only` or `--editor` as needed. The launcher checks the scenario, engine, unchanged GRF, GS/policy files and isolated assets. Exact paths/hashes are in `docs/research/phase7d_candidate_delivery.json`; the profile is `newgrfs/axis-historical-progression/.work/runtime/phase7d-editor-1793492909485253100`. Do not use an unrelated profile, substitute GRFs into an ongoing save, or deploy the 1984 test snapshot as the campaign.

## Verified and conditional

- **Modern sequence constructed:** depot, junkyard, recovery and plastics on a small map and in **two real Europe regions**, Rhine and Lille. Zero house demolition by production siting; all native callbacks remain enabled. Depot RCYC generation observed; other inputs/outputs confirmed from the native definitions/API.
- **Europe fixture:** nine new industries, **551 total**, all 542 original identities and 617 towns retained. It also built a food-processing event. Normal opening dates were compressed to 1985 for this test; it is not a paid transport or continuous Europe economy experiment.
- **Regional policy:** 32 conditional expansion/replacement events plus the unchanged three scheduled coal events, four-mine policy and one-mill retirement. Britain, Rhine/Ruhr, Polish lands, France/Benelux, Italy, Iberia and Scandinavia are represented with proposed regional dates.
- **Timeline:** continuous-calendar small-map attempt reached 2026 through one save/reload, with 11 successful and 17 cancelled events in the earlier 28-event fixture; no duplicate openings. The final four Lille additions/revised Rhine windows are Europe-smoke-tested, not full-timeline-tested. See the per-event CSV rather than assuming all 32 built.
- **Safety:** five-year default-off/no-unplanned-opening guard; targeted original-mine authorization check; final candidate startup and autosave-root guard; five focused tests. **Nine engine invocations including two corrected compile failures**, not a repeated broad regression matrix.

## Remaining work, in priority order

1. **MINOR for development playtest / MAJOR before economic certification:** operate RCYC→recovery→PLAS→plastics→MNSP deliveries with period-appropriate future vehicles. Construction and a producing depot do not establish delivered revenue, throughput or profitability. Test the parallel SCMT branch and EAF input supply too.
2. **MINOR:** review cancelled and untested regional events. Native town population, house proximity, growth and occupied sites legitimately constrain openings. Silesian modern facilities remain conditional; no town was artificially enlarged. The default is bounded cancellation, not demolition or silent relocation.
3. **MINOR:** play a human save/rejoin session with Kladdey, Squirrel and Toni. This phase did not repeat dedicated/multiplayer tests or the paid Galician route already proven in 7C. No three-human success is claimed.
4. **OPTIONAL / later validation:** a final-policy small-map run or selected future Europe snapshots when those regions become relevant. Do not rerun the entire earlier test matrix. Broad unrelated Python dependency/geography failures were not revisited.

No critical starting-map or modern native-construction blocker remains in the tested regions. The initial candidate is separate and playable; previous scenarios/assets/saves and historical reports are preserved. Normal policy does not award industries or cash to a company, change vehicle prices, or silently migrate old saves.

Read [implementation and exact evidence limits](PHASE_7D_IMPLEMENTATION.md), [test receipts](research/phase7d_test_receipts.json), [event coverage](research/phase7d_event_coverage.csv) and [preservation](research/phase7d_preservation.json). Raw logs are local; generated binaries are not committed. Changes are committed locally only; pushing or merging requires a separate instruction.
