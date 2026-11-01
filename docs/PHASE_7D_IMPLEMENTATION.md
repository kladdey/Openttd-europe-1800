# Phase 7D — regional progression, lean validation

**Development candidate:** GS v4 / schema 4, with the **unchanged Historical AXIS 0.6.0** binary. No engine patch, NewGRF recompile, cargo-ID change, new rolling stock or recipe change was necessary. Phase 7C is complete with its recorded caveats; its reports and candidates remain unchanged.

## Implemented change

`ProgressionController` extends the same v1→v2→v3 controller. It changes site screening and adds a 32-event regional policy; it does not replace mine depletion, mill retirement, warning or closure code. The three original scheduled coal events also remain. The four original mine policies and the sole original-mill enrollment are unchanged; no further baseline industry is enrolled for closure.

The new siting screen uses the **union of actual layout tiles**, rather than an empty bounding rectangle. Occupied/water/road/house/non-level tiles in that union are rejected. Required nearby houses are checked within the native ±7 tile square for each potential industry tile. Collection depots also require the native 800-person town threshold. Recovery plants require an existing junkyard within the native distance limit. Every attempted construction still goes through stock `GSIndustryType.BuildIndustry`, including its random legal layout and remaining callbacks. There is no callback bypass, demolition, flattening or road removal.

Phase 7C's generic `ERR_SITE_UNSUITABLE` messages cannot retrospectively identify every failing callback. The verified improvement is that the layout/house-aware search finds legal sites using the same GRF. Dusseldorf's initial population is only **358**, versus **1,015 in Cologne** and **1,489 in Lille**. The Rhine package therefore has named Cologne, Dusseldorf and Elberfeld fallback windows; native population and house checks decide which are usable. Lille provides a second independently tested industrial region. Silesia remains conditional rather than artificially enlarging its towns.

Search is deterministic, region-bounded and capped at **96 native attempts / six batches** per event, with rejection-category counts. Invalid/occupied sites do not consume native-command attempts. Exhaustion produces cancellation, never an off-region substitute. Player growth and funding can still occupy alternatives. No ordinary houses were removed by the production siting code or the modern construction tests; the permitted house-replacement concession was unnecessary there.

## Policy and cargo purpose

All new dates are **proposed regional gameplay windows**, not claims of exact factory founding. The policy reuses the earlier 617-town inventory, placed-industry geography and its recorded regional sources; the nearest placement citation is geographic provenance, not proof of a proposed opening year. The Phase 7C historical sources remain applicable to its retained events. No independent site-by-site historical census was attempted.

| Group | Representative additional/retained events |
|---|---|
| 1830–1860 | Galician, British and northern French milling; existing early coal/iron network and unchanged scheduled coal events |
| 1860–1900 | Rhine, Sheffield and Silesian steel/sheet growth; French and Iberian food processing; the conditional Galician mill replacement |
| 1900–1945 | Italian metalworking/machinery and Scandinavian machinery; existing MPAR→GOOD/supplies recipes |
| 1945–1980 | Retained Rhine slag processing and French edible-oil food processing; existing CMNT/FERT/FOOD destinations |
| 1980–2025 | Rhine 1985, Silesia/Lille 1990 recycling packages; planned SCMT-consuming electric-arc furnaces; unchanged finite mine retirement policy, including its later Silesian window |

Normal openings require actual predecessor instances and configured cargo producers/acceptors. This is a presence/compatibility check, not proof of a connected transport route, sufficient throughput, all optional recipe boosts or profitability. Long-haul resource movement remains necessary. All seven requested broad regional groups are represented. Full definitions, native prerequisites, footprints, alternatives and cargo purpose are in `progression_policy.json` and `phase7d_event_policy.csv`.

The modern cargo graph is **not** SCMT→plastic:

```text
town recycling depot --RCYC--> junkyard --SCMT--> planned EAF
                    \--RCYC--> recovery plant --PLAS--> plastics plant --MNSP--> existing processors
```

The junkyard is a **location prerequisite** for recovery, not its cargo supplier. Native API/definitions confirm these inputs/outputs. EAF also accepts QLME; plastics also accepts MPAR. Recipes retain their existing AXIS behavior. No new paid modern delivery or full-input operating chain is claimed. The inherited EOIL and other byproducts remain game abstractions; this phase does not rewrite their chemistry.

## Persistence and versioning

Old v1–v3 save data is rejected explicitly; there is no automatic adoption. Fresh candidates enroll only the existing reviewed pilots. Own schema-4 saves reuse the inherited ledger validation; policy-contract changes still fail closed. The policy contract is cached once because immutable policy text need not be rehashed every fortnight. `Save()` returns a cloned schema-4 root even while inherited validation temporarily views it as v3; refused older loaded data is preserved rather than relabelled. This autosave edge was separately exercised in the actual engine.

The new scenario is an actual Scenario Editor save of a disposable Phase 7C copy. CITY/INDY/PATS/PSAC and every initial map plane match; all fifteen NewGRF references/parameters are identical. Calendar 1830, economy 1800 and seven-tile trains are retained. Only the GS package/version and separate scenario identity change. Existing scenarios, binaries, normal configuration and player saves are not overwritten.

## Lean evidence and limits

**Nine engine invocations total: seven completed runs and two early Squirrel syntax failures corrected before the successful tests.** No 75-test or 36-run matrix was repeated. Five focused Python tests pass. Raw logs stay in ignored local profiles; `phase7d_test_receipts.json` records commands, hashes, dates, selected observations and local log paths.

- **Small modern smoke:** depot, junkyard, recovery and plastics physically built; native accepted/produced labels verified; depot produced **320 RCYC** in the sampled month. No houses removed. Save/reload was not claimed for this standalone construction probe.
- **Europe smoke:** supported editor jump to 1984, then nine events built **1–4 January 1985**: all four Rhine and all four Lille facilities plus French food processing. This compresses some normal policy dates and is a construction fixture, not historical economic progression. All **542 originals and 617 towns** remained, with 551 industries total.
- **Continuous small map:** 1830→1991, save/reload, then 2026; approximately **36.5 seconds** across two processes. The earlier 28-event fixture built **11**, cancelled **17**, ended with 20 industries including nine controlled seeds, and produced no duplicate opening after reload. It retained cargo endpoint checks; its missing maritime endpoints, population and native sites caused real cancellations. The final four Lille events and revised Rhine anchors were validated in Europe, **not rerun over the full timeline**. Do not present that earlier fixture as certification of all 32 final events. The generated-map retail seeds legally replaced one house building in each of two towns (15/1,196 and 30/1,020 population loss, below the fixture's 5% cap); no real Europe town was altered this way.
- **Default-off guard:** five years, density enabled, deity availability false, **zero unplanned openings over 1,834 days**.
- **Targeted mine check:** normal candidate initialized schema 4 with 32 expansion rows and four legacy pilots; bare level 4 did not close mine 1, the existing one-shot handshake did, and its same-type neighbor survived. This does not repeat the prior ten-year service-bonus experiment.
- **Final startup/autosave:** actual final package loads the separate 1830 candidate with 617/542, calendar/economy 1830/1800; a temporary v3 validation view serializes as schema 4. Older-save refusal is additionally checked statically, not a new migration certification.

Initial preservation is byte-exact. During the Europe simulation, **21 height tiles and 437 water-class tiles changed remotely**, with no such changes within 16 tiles of any new placement; the nearest height change was 1,159 tiles away. Existing rail/road/station/bridge tile classes were not removed. These background simulation differences are recorded, not hidden or rolled back; no globally frozen-runtime-map claim is made.

## Reproduce

Use the documented local Python runtime and existing pinned assets:

```powershell
python scripts/lifecycle_phase7d_policy.py
python scripts/lifecycle_phase7d_smoke.py
python scripts/lifecycle_phase7d_validate.py timeline
python scripts/lifecycle_phase7d_validate.py europe
python scripts/lifecycle_phase7d_validate.py guard
python scripts/lifecycle_phase7d_validate.py legacy
python scripts/lifecycle_phase7d_validate.py startup
python scripts/lifecycle_phase7d_evidence.py
python -m unittest discover -s tests -p test_phase7d_progression.py
```

The Europe driver needs the separately engine-saved `f.scn` at 1984 in the recorded editor profile. `candidate.py --stage-editor` creates a unique new profile; save a new `UNNAMED.scn`, finalize with `candidate.py`, then save the future-year fixture separately. Do not rerun all drivers merely to launch the candidate. The earlier 28-event timeline receipt is retained as actually run; future invocations of the driver use the current 32-event policy.
