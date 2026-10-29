# Dock and sailing validation

Source: `C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.2.0 - No Industries.scn`. SHA256 `9b4dbd70e27653fcb72d5778993988d257d5f83adcaf4a394c01af110d366735`.

Separate output: `C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.2.0 - Coastal Towns.scn`. SHA256 `6c7a7b8ccbf72a744102ab06df755d119d692ca435e397e1bbbac3267ee1b60d`.

Original towns: **613**. Added: **4**. Final: **617**. Industries: **0**.

## Actual engine evidence

Every new port passed GSTestMode BuildDock and both PASS/MAIL acceptance (at least 8/8) and positive production checks using `GSStation.GetCoverageRadius(STATION_DOCK)`, which returned **5** under this scenario. Temporary real docks were then built in a separate unpaused gameplay copy. Each new dock's departure water was traversed with actual `GSMarine.AreWaterTilesConnected` edges to an open-water witness in the sea component. This tests local shoreline/bridge access; a coarse pixel component alone is not claimed as proof.

| Region | Moved | Destination dock reached/loading | Loaded observed |
|---|---|---|---|
| British Isles | true | true | true |
| Iberia | true | true | false |
| Mediterranean | true | true | true |
| Baltic / North Sea | true | true | true |

Sailing Brig engine 616, already present in the active vehicle collection, was built with a passenger refit in the disposable copy. The refined script sampled every five ticks and required either an actual loading state or a destination-to-origin order transition within four tiles of the destination. It also recorded movement, minimum destination distance and any positive cargo load. These are VERIFIED IN GAME movement/loading observations, not static path-distance estimates. The first 50-tick sampler missed short stops, and its 30,000-tick window was too short for Porto–Lisboa; its incomplete results remain in the evidence archive. The refined test allowed 100,000 ticks and used the supported ResolveOrderPosition API. Revenue and economic balance were outside this phase and were not inferred from loading. Porto–Lisboa proves navigation, not loaded delivery: no positive passenger load was sampled on that voyage. Route endpoints, dock tiles and witness tiles are in `research/coastal6a_shipping_plan.json`; results are in `research/coastal_accessibility_results.csv`.

No full coastwide shortest-path graph is asserted. Local engine-edge traversal is bounded to 20,000 expansions / 85 tiles; representative real ship voyages cover British Isles, Iberia, Mediterranean and Baltic waters. North Sea-specific long voyages and every possible inter-port pairing are not tested. Existing inland river ports and lakes remain separately labelled; the 82-town catchment count is not a count of ocean-reachable ports.

## Isolation and load/save/reload

Only copies under `newgrfs/axis-historical-europe/.work/coastal6a` were operated. JGRPP 0.73.4 executable and the same licensed local GRF assets were reused. `-X -x -c <isolated cfg>` prevents normal user-data/config writes. Paused founding prevents original-town growth; movement copies alone clear their copied pause byte. All delivered DATE/settings bytes retain the source values, including 1830 calendar start, inherited 1800 economy date and seven-tile train limit.

The candidate was loaded, saved by JGRPP, and the engine-produced save loaded again. Original towns and all map arrays survived the real save unchanged. Runtime API enumerated all 15 loaded GRFs and confirmed train limit 7. Embedded NGRF identities/checksums/parameters match the source exactly. Final output retains the original no-player/no-network chunks rather than packaging the temporary measurement company or GameScript. The final file uses source chunks plus only engine-generated CITY and map changes; this deliberate composition preserves original settings and is explicitly checked by the second engine load.

## Reproduction

Use Python with NumPy/Pillow; coastal analysis additionally needs SciPy (this run used an isolated ignored local target). From the repository root: run `scripts/coastal_phase6_runtime.py scripts/coastal_phase6_inventory.nut --tag inventory --ticks 15000`, then `scripts/coastal_phase6_analysis.py`, `scripts/coastal_phase6_proposals.py`, review local terrain rasters, and `scripts/coastal_phase6_implement.py`. `coastal_phase6_finalize.py` performs name/load/save/reload/preservation checks and refuses to overwrite an existing output. `coastal_phase6_run_shipping.py` performs disposable real sailing tests; `write_coastal_phase6_reports.py` consumes the retained evidence. Run all Python commands with `-X utf8`; do not use `-O`, which disables safety assertions.

`scripts/verify_coastal_phase6.py` is the repeatable read-only verification of the delivered candidate. Evidence contains exact scripts, commands, source/script/log hashes and C6 measurements. Two exploratory script issues (wrong error-class API and a missing UTF-8 BOM) were corrected; non-ASCII final names are verified through JGRPP, not assumed from source text. An incomplete 10,000-tick inventory was not substituted for the complete earlier scan. Squirrel requires the BOM for UTF-8 literals in this release.
