# Phase 7C — actual engine validation

## Evidence boundary

The final evidence set contains **36 actual stock JGRPP 0.73.4 invocations**, all using the corrected 0.6 GRF (`023099757b94573f33e0c8380804cdbe80d3155b914d5441f98e89e55c9d8b84`). Commands, durations, script hashes, input profiles, observations and raw-log hashes are retained in `docs/research/phase7c_engine_receipts.json` and `phase7c_logs/`. Earlier development/prototype runs are not counted as final passes.

**75 focused Python tests pass**: the 63 retained Phase 6B/6C/7A/7B tests and 12 new Phase 7C tests. These reconcile actual receipts and check policy compilation/safety; they do not substitute for engine execution. Broad repository discovery was also attempted: 199 tests, 3 failures, 11 errors and 15 skips. That wider suite is **not green**: missing SciPy, stale earlier coastline registration hashes and an earlier platform-dependent path snapshot are outside this change. Those older files were not edited to hide the failures. See `phase7c_test_results.json`.

## Europe opening, paid chain and replacement — VERIFIED IN GAME

The real 4096² scenario was copied into an isolated profile. The fixture deliberately moves the two Galician mill openings and retirement forward, but retains a **genuine five-calendar-year minimum warning**. It grants no cash and builds only available existing period vehicles.

| Actual fixture event | Date / result |
|---|---|
| New Galician flour mill, local type 34 / runtime 30 / industry 542 | 1831-01-12; tile 6373982 = (606,1556) |
| Original mill 275 receives warning | 1831-01-12; gradual levels 14 → 12 → 10 → 8 |
| Nearby successor, industry 543 | Native construction date 1832-01-12; tile 6255170 = (578,1527). The pre-command GS log is one day earlier. |
| Both paid transport legs confirmed | 1834-01-19 |
| One-shot retirement armed / committed | 1837-01-07 / 1837-02-20 |
| Original mill physically absent | 1837-04-04; successor remains present |
| Final checkpoint | 1838-01-04: 543 industries = 542 originals + 2 new − 1 authorized retirement; all 541 other originals intact; all 617 towns present |

The successor is 64 Manhattan tiles from the retiring mill and has nearby existing grain production and a food market. No exact-old-tile replacement is claimed.

The route is existing farm **66** → new mill **542** → existing general store **474**. It uses eight 1 Horse Hopper Carriages on grain and eight 1 Horse Ice Box Carriages on food, selected through actual buildability/refit APIs. Source and destination stations, vehicles and turning loops are real engine objects. Samples recorded **£100** and **£37** positive vehicle-profit increments near the accepting destinations, after loaded observations. Those are **sampled net increments**, not gross delivery invoices, annual profit or a balance forecast. Both legs ran and the mill produced cargo. No cargo was fabricated or enabled by a vehicle-name assumption. See `phase7c_paid_deliveries.csv` and the raw `I6 CONTROL_SERVICE` / `I6 CONTROL_PAID` records.

Checkpoint save/reload occurs after the first opening, after the successor, during warning and after closure. Replaying the pre-closure checkpoint reproduces the same significant opening/arm/commit/physical-closure/final-checkpoint ledger. Reloading the terminal state neither reconstructs a closed site nor authorizes closure twice. A separate observer compares the company vehicle IDs/engines and station IDs/locations before and after closure: identical. This proves preservation of that road-service fixture; it is not a separate test of every possible player railway/bridge layout.

## Later historical wave — VERIFIED IN GAME, construction scope

A separate Europe copy was saved with the supported Scenario Editor year control at **1864**. This is a date-jump fixture, not simulated continuous growth since 1830. Its economy clock remains 1800 initially, deliberately exercising correct separation from calendar time.

On **1865-01-05**, the controller physically constructed local type **103** sheet/pipe mill at tile **5359587**, followed by local type **2** historical steelworks at **5384183**. The normal 1865 policy dates, native availability and regional candidate sites were used. The source's historical steel recipe still requires IRON and COKE. Two extra industries persisted through the 1867 checkpoint. This validates a different Europe opening wave/type; **a paid steel chain was not operated**.

## Capacity correction — VERIFIED IN GAME with a limited inference

A separate four-economy-year old-mill route test feeds original industry 275 and hauls its food to market. It runs normal level 16 for two years, then capped level 8 for two years. Both routes record loaded cargo and positive destination income. At level 8, grain remains stockpiled (observed maximum 78 units) while food continues to be produced; partial batches are not consumed into zero output.

The normal phase totals 83 sampled monthly food units over 25 boundary observations; the capped phase totals 108 over 24 observations. These totals **do not demonstrate a percentage output decline**: startup, station ratings, input arrival and observation boundaries differ. The observed backlog shows that the cap binds; finite processing capacity follows from the independently inspected batch/cycle callback. Do not turn this into a claimed profit comparison. All observations are preserved in `phase7c_capacity_observations.csv`.

The rejected prototype processed one-unit batches and could round input contributions to zero. Its binary and logs remain in ignored local prototype profiles; it is not delivered or counted as a final pass. The corrected build processes complete eight-unit batches at progressively longer intervals and retains partial inputs.

## Multi-era run — VERIFIED IN GAME, small-map construction scope

The 256² test progressed in genuine historical calendar years from 1830 through **2026**. It used abstract sites, a seeded farm and blast furnace, and explicitly omitted cargo-endpoint gates. It is not Europe geography or economic validation.

Seven of ten opening events built: flour (1835), sheet/steel (1865), successor mill (1887), metal workshop (1910), slag grinding (1955), recycling depot (1985). Nine industries remained including the two seeds. This covers a constructed sample in all five era bands.

The junkyard exhausted its 96 native attempts with `ERR_SITE_UNSUITABLE`; its house-adjacency/clear-footprint constraints were not bypassed. The API did not expose the exact failing tile callback, so the precise rejection cause remains UNVERIFIED rather than attributed conclusively to one check. The recovery and plastics plants then deferred and ultimately cancelled because their prerequisite did not exist. There was **no invented modern chain completion**. The production policy uses Dusseldorf town-centred alternatives rather than the fixture's abstract coordinates, but that future Europe siting remains unverified. Correcting/validating that package is post-pilot work.

No full 1830–2025 Europe run was performed. The delivered scope is early Europe operation/closure, a later Europe construction snapshot, the separate ten-year mine regression, and small-map historical-year construction. Global compatibility graphs do not establish future regional resource adequacy.

## Safety, controls and inherited regressions

- Five-year nonzero-density native control: **zero new neutral industries over 1,834 economy days**, with deity construction availability enabled. Lifecycle availability did not globally enable random spawning.
- Blocked footprint with no safe alternative: bounded cancellation. Occupied farm tile plus a safe alternative: actual mill construction without removing the farm. Unavailable steel in 1831: deferred/cancelled. Missing grain endpoint: deferred/cancelled.
- A fresh default-off profile rejects controller startup before enrollment or construction.
- Native bare level-4 factory request: mill survives. Expired factory token: mill survives. Same request to unregistered mill 276: survives. Fresh authorized legacy mine request: mine physically disappears. These are commands in disposable copies, not recommended gameplay actions.
- v2→v3 defaults to refusal; explicit `adopt_only` keeps the prior ledger and enrolls zero expansions/processors; its reload succeeds. Changed policy contracts and partial expansion/factory ledgers fail closed.
- Actual dedicated-server restore: multiplayer mode true, saved warning state and two expansion rows retained, clean quit without forced termination. **No human join/reconnect or three-human session was tested.**
- The unchanged Phase 7B served comparison was rerun against the final 0.6 binary. Mine 1 qualifies once at **2,074 transported units / 38%**, receives the fixture's finite two-year extension and later physically closes. The other three pilots close earlier; all four closures complete, **538 unmanaged originals and 617 towns** remain, and the coal delivery records a positive £89 sampled net increment. The normal production policy is unchanged and still has its original windows/caps; fixture dates/bonus are not shipped.

## Initial preservation and reproducibility

The final scenario is a real Scenario Editor save and loads/saves/reloads as gameplay with the actual production controller. Before any simulation, CITY, INDY, PATS, PSAC and all map-plane bytes match the pinned Phase 7B baseline. It preserves 617 towns, 542 industries, 15 GRF identities and their parameters, calendar 1830 / economy 1800 and seven-tile trains. The deliberate AXIS binary/version reference and GS package change are separately recorded.

All 96 audited industry model file hashes match; the four-mine primary callback template is byte-identical. The launcher validates 41 isolated asset files, including archived NewGRFs and base-media files, rather than checking only loose GRFs. The original scenarios/GRFs/engine are guarded by hashes. Raw logs are committed with `-text` attributes so Git cannot invalidate their hashes by newline conversion. See `PHASE_7C_IMPLEMENTATION.md` for drivers and the exact distinction between fixtures and the normal candidate.
