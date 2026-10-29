# Phase 6C readiness

**READY WITH CAVEATS for an 1830 multiplayer playtest.** The inland market shortage is substantially corrected in an actual delivered scenario. This is not certification of a balanced unattended 1830–2025 campaign.

Open **`C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.3.0 - Inland Markets.scn`** with the existing Historical AXIS 0.3.0 candidate and exact embedded 15-GRF collection. SHA-256 `afcab50864e87f56a7260c62d87bd37560fa3d7676713afb14c480c555d0bc06`. No source scenario, GRF, vehicle, normal configuration or existing save was overwritten.

## Decision and evidence

| Question | Assessment |
|---|---|
| Can inland FOOD/GOOD actually reach paying destinations? | **Yes.** Grain→flour/FOOD→Kraków, fibre→textiles/GOOD→Prague and a longer French manufactured-goods route all loaded and paid. Valencia fruit also reaches a Food Market. |
| Was historical variety preserved? | **Yes.** Existing 467 industries, recipes, vehicle roster, prices, dates and all GRFs/parameters preserved. 75 existing retail types added at 61 town anchors. Individual shop addresses are representative, not archival claims. |
| Can a normal-budget inland freight company profit? | **Yes in the tested rail/road FOOD configuration:** +£16,498 over five years. It has not yet recovered £23,573 capital. Tested sparse horse-only chains lose money. |
| Does coastal trade remain useful? | **FOOD verified:** +£23,934 over three years; capital recovered in year three. Coastal GOOD on Europe geography remains a manual check after bounded construction failures. |
| Did demolition damage towns? | 75 ordinary cottages / 900 population, maximum 3.87% per town. All 617 identities/names/centres survive. London, Prague and Kraków exceeded their post-market populations after five normal-growth years. |
| Are map and save integrity established? | **Yes for the delivered snapshot:** exactly 75 authorized tile changes, zero height/water/infrastructure changes, two gameplay round trips and real editor save/reopen. One dead-end road redeveloped during later ordinary growth in a disposable save; see the gameplay report. |
| Are copper and salt still functional? | Salt→curer→inland FOOD paid on Europe; copper complete recipe/output paid in a fresh controlled fixture. Europe copper export station remains unbuilt by the bounded automation. |
| Are three starts financially equivalent? | **Not established or required.** Britain has a profitable coastal example, Polish territory a profitable rail example; Prague/French/Valencia horse freight tests warn against assuming any rural road investment pays. No concurrent competition test was added here. |

## Prioritized actions

| Severity / scope | Evidence and root cause | Smallest action | Confidence / risk |
|---|---|---|---|
| **MAJOR for committing to 1830–2025; not an opening-playtest blocker** | Preserved spawning policy also blocks neutral deity creation through the GRF availability callback | Phase 7 must separately validate a historical lifecycle/progression mechanism, closures, replacements and future industry availability. Do not silently enable random spawning or claim a scheduler already works | High; unplanned future cargo gaps if ignored |
| **MAJOR economy warning; monitor in first session** | All tested sparse ordinary horse-only new-build FOOD/GOOD/FRUT chains lose money, with property maintenance and overhead exceeding low throughput | Try existing-road/shared-infrastructure feeders and a larger sensible fleet; compare full company accounts. Do not buff horses or add more markets from this evidence alone | High on measured losses, limited generalization; subsidies or cheaper cargo would risk exploits |
| **MINOR validation gap** | Coastal GOOD and Europe copper export station/approach construction exhausted bounded searches | Human-complete one GOOD export and Swansea copper export in disposable copies; exact endpoints/errors in gameplay report | High on builder failure, unknown on route viability; do not terraform to manufacture success |
| **MINOR regional access gaps** | 11 FOOD / 10 GOOD producers remain >160 Manhattan tiles away; six GOOD producers >300 | Inspect one of the longer actual routes and its capital/throughput, retaining regional specialization. No automatic village-by-village market expansion | High distance evidence; access/profit not established for every producer |
| **MINOR growth observation** | One one-bit dead-end road became housing over five ordinary-growth years | Inspect (1142,979) and market access during human play; distinguish normal redevelopment from snapshot construction damage | High observation; causal link not established |
| **Historical review carried forward** | Four inherited soda-ash mine sites still lack verified 1830 mineral exploitation evidence | Resolve in a separately reviewed Phase 6B correction; preserve them here as instructed | High that evidence is missing; no claim each site is historically impossible |
| **OPTIONAL** | Generic industry graphics and representative retail locations | Historical visual refinement after operations are understood | Low priority; avoid a new GRF/save migration merely for this phase |

No balance correction is implemented or justified solely to force equal mode profitability. The rail and shipping examples show genuine inland/coastal economic activity; negative carriage results are useful counterevidence, not omitted failures.

## First session for Kladdey, Squirrel and Toni

1. Start a **new** disposable multiplayer game from the delivered Inland Markets scenario. Verify 617 towns, 542 industries, Historical AXIS 0.3.0 candidate, calendar 1830 and seven-tile limit. Do not change normal settings or GRFs in an existing campaign save.
2. Choose geographically distinct businesses: Britain coastal/industrial trade, Polish/Central European rail-to-market freight, and a Western/Southern short feeder using existing roads. Players may switch modes and finance a mixed company; do not require a road-only company to match a shipping company.
3. Reproduce one known working baseline each: FISH 141→413→FOOD 154, grain 66→275→FOOD 474, or fruit 171→Food Market 538. Industry IDs/coordinates are in the CSVs; confirm actual cargo acceptance and vehicle refits in game. Use compatible period wagons, UKRS2 brake van and realistic loading orders.
4. Record construction, fleet investment, loan, annual gross revenue, running costs, infrastructure maintenance, interest, transported units and company cash at years 1, 3 and 5. Keep income separate from loans. Compare against the phase's complete-chain ledgers, not just vehicle profit.
5. For the road start, test an existing-road/shared-station feeder before building an expensive 100+ tile trunk. If it still cannot fund expansion, retain the save and exact accounts; do not infer that more final consumers will fix low throughput.
6. Test coastal GOOD textile 358→wharf 458 (with a valid fibre feeder) and copper works 440→wharf 456. Choose a legal station/port catchment and navigable approach; observe loaded output and credited income. These have **not** passed Europe end-to-end validation yet.
7. Add one competing service to a shared producer/market only after recording an isolated baseline. Watch station rating, demand sharing, port congestion and access; previous isolated profits do not establish multiplayer fairness or absence of first-mover advantages.
8. Inspect market towns and the recorded dead-end-road coordinate after several years. Save separate checkpoints and agree a Phase 7 progression decision before a long campaign advances toward unsupported industry transitions.

## What Phase 7 may rely on

Stable existing cargo IDs, unchanged recipes/parameters, existing retail types and recorded producer/consumer locations are available. Markets are final demand sinks and remain potentially useful as production expands; their presence is not proof of permanent capacity, future-year availability, closure immunity or acceptance for new cargos. A lifecycle system must preserve or intentionally replace enough retail demand, respect historical introduction restrictions and test its actual construction context under the spawning callback. It must not retrofit a changed GRF list into this save.

Full details: [implementation](INLAND_MARKETS_IMPLEMENTATION.md), [coverage](INLAND_MARKET_COVERAGE.md), [gameplay evidence and manual blockers](INLAND_MARKET_GAMEPLAY_VALIDATION.md). Source, scripts, reports and focused evidence are committed locally on `feature/axis-historical-integration`; this phase does not authorize a push or merge.

Validation completed: **16 focused Phase 6C checks and 10 existing Phase 6B regression checks passed**. The Phase 6C tests reconcile engine receipts, exact delivered artifacts, all 617 reloaded towns, finance ledgers and actual paid-chain evidence; blocked routes are never counted as passes.
