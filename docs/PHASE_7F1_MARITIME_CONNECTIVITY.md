# Phase 7F.1 — maritime connectivity follow-up

**PARTIAL. No paid shipborne delivery.** Four new JGRPP invocations (the three-run budget plus one explained, targeted alternative), four focused tests passed. The work stays on `feature/phase-7f-historical-ports`, descending from `2f9a179` and Phase 7E `4a6b056`.

## Diagnosis and implemented fixture corrections

The direct candidate is native Liverpool **Wharf 458 → Dublin Flour Mill 260**, cargo **MNSP (38)**, existing buildable/refittable **Brig 616**, capacity **50**. Both industries already exist; no industry was funded, moved, modified or forced to produce.

The old Dublin failure was a receiving-station geometry problem. `ScriptRoad::BuildDriveThroughRoadStation` explicitly supports an existing station ID, subject to native spread/placement rules. A legal joined truck stop at **(3356,966), tile 3960092** extends the receiving dock's station catchment to the mill. It joins **station 1**, whose dock is **(3349,973), tile 3988757**. Native commands succeeded; the local MNSP acceptance score was **32 eighths**, above eight, and `GSIndustry.IsCargoAccepted(260,MNSP)` returned accepted. No horse or feeder is needed for this direct station extension. This uses ordinary combined-station catchment; it is not a new GS cargo-transfer mechanism.

Industry-owned port graphics are not player dock stations. The fixture builds real player-company docks; it does not use invalid `GetDockLocation=-1` results as destinations. `DockWater` reads the built dock's adjacent water part and the next outward tile. Native `GSMarine.AreWaterTilesConnected` edges reached both selected dock approaches in **60,769 visited water tiles**. This resolves the bounded *tile-connectivity* check for Liverpool–Dublin; it does **not** prove the ship pathfinder can enter each berth from every incoming direction.

## What actually ran

| Invocation | Observation |
|---|---|
| 1 — access | Dock station 0 at Liverpool tile **3959783 (3047,966)**; approach **3951591**. Dublin station 1/extension as above; approach **3996949**. Connected native edge search, legal station join/acceptance, Brig buildability and refit confirmed. No ship spawned yet. |
| 2 — delivery | Reloaded that own diagnostic checkpoint. Built **vehicle 0**, Brig 616, refitted capacity 50, depot **3951593**, actual ship purchase **£3,808**, two orders. After **1,460 economy days**, maximum load=0, observed unloading=0, delivery-income increment=0. Current/previous economy-year profits **−£41 / −£492**, not the total four-year loss. |
| 3 — reload/diagnostic | Reloaded the saved ship and orders, then sampled another 35 economy days. Source Wharf 458 was actually producing **224 MNSP/month**, level **16**; loading station held **406 MNSP**. Ship was running, current order **0** (source), at **(3263,983)** and still empty. Data/orders/ship survived reload; this does not certify the normal GS v5 lifecycle ledger. |
| 4 — permitted narrow alternative | Source dock moved legally to **3984359 (3047,972)**, source approach **3984361 (3049,972)** and depot **3984363 (3051,972)** in a fresh disposable copy. Added a conservative flat, unobstructed five-tile water-approach screen; retained Dublin's accepted joined station. Connectivity again passed. Another 1,460 economy days produced **zero observed ship load, unload or payment**. No further engine runs. |

The initial access observation `source_production=0` was a startup sample, not proof of a non-producing port. The reload evidence rules out a general absence of source MNSP in the first delivery fixture. Likewise, cargo waiting at the source is not proof that the ship can reach its loading position. The first delivery log's `mill_food=-1` queried an unproduced cargo label at the mill; that diagnostic query was corrected for subsequent runs and is not production-failure evidence.

Orders are ordinary source **OF_NONE**, destination **OF_UNLOAD | OF_NO_LOAD**, with no transfer order or feeder credit. Positive income would only count after observed ship loading, load decrease near the receiving dock and positive vehicle-profit movement. None occurred. GSDate values are economy dates, while the fresh candidate starts at calendar 1830/economy 1800. No annual profitability, payback, delivered quantity greater than zero or successful sailing service is claimed.

## Remaining blocker and smallest next experiment

**Unresolved ship navigation/berth access.** The first ship remained running on its source order despite a cargo-producing source, waiting MNSP, refit capability, legal stations and a connected tile-edge graph. A wider loading approach alone did not fix this. The exact native pathfinder/berth-entry cause has **not** been isolated. There is no evidence justifying a recipe, ship-price, terrain or port-policy change.

The next experiment should be **one manual inspection of the retained disposable ship checkpoint**, rather than another multi-year automatic run:

1. Open the recorded delivery profile/checkpoint in its isolated environment. Inspect vehicle 0's actual station names/orders, current destination, speed and lost/pathfinding indication; confirm its precise reachable docking position.
2. Trace a short buoy waypoint sequence from the ship to the loading berth. Test each segment with the same vessel. If it reaches the berth, observe real MNSP loading before testing the Dublin destination. Do not move towns, reclaim water or alter prices.
3. Only after a loaded voyage, record unloading/acceptance and positive ship-income evidence. If a waypoint or corrected berth entry resolves it, implement that one route change and retest once. Until then Phase 7F stays PARTIAL.

The older Greenock search remains a failure of its selected approaches/bounds, not proof that all Clyde shipping is impossible. The Irish Sea FOOD feeder's earlier non-loading failure remains unresolved; a direct joined-station test avoids that additional variable without claiming to fix it.

## Reproduction, safety and evidence

```powershell
python scripts/ports_phase7f1.py access
python scripts/ports_phase7f1.py delivery
python scripts/ports_phase7f1.py reload
# Only the explicitly justified fourth alternative:
python scripts/ports_phase7f1.py fixed
python scripts/ports_phase7f1_evidence.py
python -m unittest discover -s tests -p test_phase7f1_connectivity.py
```

These commands reproduce diagnostic/negative fixtures, **not a proven paid service**. Each invocation uses a unique profile below `newgrfs/axis-historical-progression/.work/runtime/phase7f/f1-*`; the index receipts are in its `connectivity` subdirectory. Raw logs and actual native `save/autosave/exit.sav` checkpoints remain local; paths, source/script/log hashes, durations and commands are in [receipts](research/phase7f1_receipts.json). [Route results](research/phase7f1_route_results.csv) preserve the negative amounts. The reload probe deliberately reads its own fixture state and does not migrate an ongoing campaign's GS data.

Native API evidence came from the already cached JGRPP 0.73.4 source in the adjacent checkout: `.research/jgr734/src/script/api/script_road.hpp` (explicit station joining/spread errors), `script_marine.cpp` (neighbour water-edge connectivity and native dock command), `script_station.hpp` (coverage/cargo waiting), and `script_vehicle.hpp` (vehicle state). No engine patch or new dependency was installed.

The unchanged Phase 7F candidate SHA-256 remains **`0d21f3045e8bc2dc2d4888298ad467284e90ffb3cba1be012bced37ee7386c5f`**. All manifest-pinned normal profile/engine/GRF/script assets were verified after testing. Initial **617 towns / 542 industries / 15 GRFs / 64 cargos / seven tiles** and all eight port events remain untouched. No original scenario/save, GS schema, recipe, price, economic setting, terrain or water was changed. The standalone company-mode test purchased its own infrastructure/ship from ordinary company funds; it injected neither cargo nor money. No push, merge or main change.
