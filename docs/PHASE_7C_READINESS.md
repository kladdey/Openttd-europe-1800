# Phase 7C — readiness

**READY WITH CAVEATS** for a limited multiplayer playtest. A separate playable, historically paced scenario is delivered. This is not approval of a fully validated 1830–2025 industrial schedule.

## Candidate and launch

Scenario:

`C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.6.0 - Historical Expansion.scn`

SHA-256: `3064ea27afd485a59a3a4c71d30ee8c96d28968ecdf31aa2b056fb537924dbda`

GRF:

`newgrfs/axis-historical-expansion/dist/axis-historical-europe-0.6.0-expansion-candidate.grf`

SHA-256: `023099757b94573f33e0c8380804cdbe80d3155b914d5441f98e89e55c9d8b84`

Isolated profile:

`newgrfs/axis-historical-expansion/.work/runtime/expansion-editor-1793478730979671100`

From the repository, launch with:

```powershell
& 'C:/Users/Kladd/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' scripts/lifecycle_phase7c_launch.py
```

Add `--verify-only` to check hashes, or `--editor` to inspect the scenario. The launcher uses stock JGRPP 0.73.4 with `-X -x`, the isolated configuration/assets and GS v3. The normal OpenTTD profile is not configured to supply this candidate. Do not open it through a different profile and accept missing/substitute assets. Machine-readable paths/checksums/15 identities are in `docs/research/phase7c_candidate_delivery.json`.

## What is delivered

- Initial snapshot: **617 towns, 542 industries, 64 cargos, 96 registered industry types, 15 GRFs, seven-tile train limit**, preserved terrain/waterways/settings/parameters.
- **10 new opening events**, spanning five era bands, plus the unchanged three scheduled mine events and unchanged four-mine policy.
- **One narrowly enrolled processor transition**: old Krakow-area mill, warning 1885 / earliest retirement 1895, conditional on a nearby live successor and local cargo endpoints. No generic factory closure mechanism or unlimited service subsidy.
- Real Europe early opening, complete paid grain/food chain, physical warned processor closure and nearby successor; later Europe steel/sheet opening wave; deterministic save/reload/replay; dedicated restore; 36 final engine invocations and 75 passing focused tests.
- Source/build scripts, persistent GS, policy/chain data, raw receipts, preservation checks, candidate launcher and four Phase 7C reports committed locally. Prior scenarios and binaries remain available. No push/merge is part of this phase.

## Caveats and minimum next work

| Priority | Issue | Evidence / next action |
|---|---|---|
| MAJOR for a claimed complete late-century schedule; not an 1830 opening blocker | Modern recovery package is incomplete | Native junkyard siting failed in the small-map run; dependent recovery/plastics events cancelled safely. Before relying on the 1985 wave, validate house-adjacent clear sites in a disposable future Europe snapshot and run an RCYC→PLAS→MNSP delivery chain. Do not relax terrain/player-asset safeguards simply to force a pass. |
| MINOR for this pilot | Future regional routes and replacement siting | Only the early grain/food route was paid in Europe. Later workshops/slag/depot were construction-tested on the small map. Town/player growth may occupy the historically paced sites; the 1887 replacement can defer, so the old mill must then remain open. Monitor the ledger, not just calendar dates. |
| MINOR / inherited | Byproducts and resource coverage | No 1830 EOIL consumer; no scheduled future SCMT consumer in this slice. Compatibility graphs are conditional projections, not transport/production proof. Keep these visible and design a later reviewed consumer wave rather than invent conversions. |
| MINOR / inherited | Service attribution | Mine service extension uses public transported counters; actual paid fixture evidence does not make that metric resistant to pickup/dump gaming. Factory extensions are disabled. Monitor competitive abuse before expanding service incentives. |
| OPTIONAL before an extended campaign; required before calling multiplayer validated | Three-client join/reconnect | Dedicated server restore passed with no humans. Kladdey, Squirrel and Toni must test identical assets, synchronized news, save/rejoin and event visibility. |
| Separate repository maintenance | Broad Python suite is not green | 199-test discovery has missing SciPy and earlier coastline/path-snapshot failures. The 75 relevant tests pass; no unrelated geography files were rewritten. |

No critical initial-map or early lifecycle blocker was observed. The minimum next step is a short human session using the normal candidate, followed by a separately labelled compressed-transition test if the players want to inspect the warning/closure without waiting decades. Do not deploy the compressed policy as the campaign.

## First human session

1. Kladdey hosts a **new game** from the pinned scenario/profile. Squirrel and Toni use identical client GRFs, especially this local 0.6 candidate; verify the server's 15 identities. Preserve the existing normal campaign saves.
2. Enter three companies with normal starting conditions. Try distinct regions/strategies without gifts or scripted ownership. Confirm the 1830 public Galician expansion notice appears for every company; nobody receives exclusive rights or cash.
3. Save, disconnect/rejoin and restart the server from that save. Confirm one persistent scheduler, unchanged event status and no duplicate announcement/opening. Build competing approaches near a candidate district; no existing road/station/town should be removed to force a site.
4. During normal progression, inspect the 1835 mill opportunity and build an actual grain-to-food service. Record loaded units, accepted delivery income, running/infrastructure expense and all three players' observations; the automated positive samples are not a multiplayer profitability guarantee.
5. In a **separate disposable accelerated fixture**, verify all clients receive the multi-year warning, successor appears before retirement, old industry disappears once, and player vehicles/stations/orders survive. Compare server logs after save/rejoin. Do not transplant that fixture's dates or save into the normal campaign.
6. Keep later steel, slag and recycling operation as explicit follow-up tests. A safely cancelled event is a limitation to review, not evidence that the complete late economy works.

Exact event dates, receipts, failures and confidence are in [engine validation](PHASE_7C_ENGINE_VALIDATION.md), with historical assumptions in [policy](PHASE_7C_HISTORICAL_EXPANSION_POLICY.md) and reproduction/migration rules in [implementation](PHASE_7C_IMPLEMENTATION.md).
