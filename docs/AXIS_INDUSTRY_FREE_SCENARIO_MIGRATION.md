# Industry-free Europe scenario → Historical AXIS

**Completed for the specific supplied industry-free scenario.** JGRPP 0.73.4 loaded and saved the converted scenario, then a separate paused gameplay child passed a save/reload test. This does not authorize converting populated stock-AXIS saves.

## Delivered files

- Scenario: `C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.2.0 - No Industries.scn`
- Installed distinct GRF: `C:\Users\Kladd\Documents\OpenTTD\newgrf\axis-historical-europe-0.2.0.grf`
- Matching GPL corresponding source: `C:\Users\Kladd\Documents\OpenTTD\newgrf\axis-historical-europe-0.2.0-source.zip`

The scenario starts **paused on 1 January 1830**, is still deliberately **industry-free**, and retains 613 towns on the 4096² map. Stock AXIS remains installed for the original scenario. If an already-running game has not scanned the new GRF, rescan NewGRFs or restart before loading this scenario. No settings or files in the user's running Steam game were controlled.

## Six requested checks

| Request | Verified outcome |
|---|---|
| All industries removed? | **Yes: zero INDY instances and zero industry-class map tiles.** Stations, vehicles and persistent storage were also empty; these are mandatory cleanup preconditions |
| Embedded NewGRFs? | **15 entries.** Stock AXIS `4A4B8808`, version 6749, MD5 `b580ae20d12247f3a7edd28fadc6f2e5` was replaced by Historical AXIS `4B484531`, version 2, MD5 `8a395985234b85df126aeac4e3c8cc7c`. The other 14 entries remain identical, including MD5s, parameters, palettes and relative order |
| Safe replacement? | **Validated for this empty world after orphan-mapping cleanup.** An editor-only replacement was insufficient: old saved industry/tile-ID mappings exhausted allocation. No populated-world migration is claimed |
| Towns/terrain/rivers/features preserved? | **Byte-identical CITY and every original map-data chunk after the final editor save.** This covers town names/positions/state, heights, river/water tiles, houses, roads, bridges, trees and all tile metadata. Other chunks also match except DATE, GLOG, NGRF, IIDS and TIDS |
| Separate working 1830 scenario? | **Created and installed alongside the original.** The scenario contains no measurement GS, no added industries and no changed vehicle sets |
| JGRPP load/save? | **Passed editor load/save and fresh gameplay load/save/reload.** Both gameplay processes reported 613 towns, zero industries, 64 cargos, all 92 historical types and train length 7; no industry/tile allocation overflow |

MD5 above uses OpenTTD's GRF identity region, not whole-file MD5. Full GRF SHA256 remains `0728a246327826ae2dccdcbb13578631ea401d088b56e1e954b917eb2f7af8a7`. Final scenario SHA256: `9b4dbd70e27653fcb72d5778993988d257d5f83adcaf4a394c01af110d366735` (4,876,032 bytes).

## Method and the actual blocker

The original supplied file was fingerprinted (`06273051c3e76e6c750e7bdda2859ce3fbece2f3eac5998591dfe645169162fb`) and copied into a disposable user-data directory. The editor selected Historical AXIS in stock AXIS's original position and saved a pilot. No manually fabricated NGRF identity entry was used.

The source still carried **106 industry mappings and 512 industry-tile mapping records** despite having no industries. The editor's ordinary reload retains persistent mappings: `ResetIndustries()` resets overrides, not those mappings. The pilot logged **186** industry-tile allocation-overflow messages and could not be accepted as working. It also evolved trees/shore tiles while the editor ran unpaused; that pilot was not delivered.

A guarded utility therefore takes the **engine-authored NGRF/GLOG**, restores every other source chunk, removes orphan **IIDS/TIDS records only**, and sets only the DATE pause byte to normal pause. It refuses worlds with any industries, industry tiles, vehicles, stations or persistent storage, and refuses changes to the other 14 GRFs or original AXIS parameter values. Its encoder first proves a byte-identical framing roundtrip of the source. JGRPP's `src/sl/newgrf_sl.cpp::Load_NewGRFMapping` resets each mapping manager before reading its records, so empty mapping tables are rebuilt by the engine from the selected Historical AXIS. The candidate was then **actually reopened and saved by the editor**, rebuilding mappings without overflow. The delivered file is this engine-saved output.

Final mapping tables contain 92 industry records and a dense tile table through index 350; the tile count includes padding/default positions, not 351 custom tile definitions. Actual runtime resolution of every one of the 92 historical industry types and all 64 cargos passed twice.

The gameplay child changes **GSDT only** to attach a read-only probe; it is never delivered. Auto-exit saves use JGRPP's packed `WMAP` representation. The checker normalizes its little-endian Tile/TileExtended arrays to the original per-field map representation and verifies identical hashes after save/reload. Towns, economic settings and other protected chunks also match. The delivered scenario's GS data is untouched.

One pilot assertion initially mistook `GSDate.GetCurrentDate()` for calendar time. In this saved campaign it exposes the **economy year 1800**, while the calendar remains **1830**. The corrected check explicitly retains that inherited offset and verifies calendar date 668394 in the save. No campaign timekeeping setting or economy date was changed to make the test pass.

## Parameters and limits

Original AXIS parameters `0 0 0 0 0 0 16 150 80 300` are preserved; Historical mode appends `1`. **Natural/deity spawning remains off (parameter 2 = 0).** Consequently the industry-free scenario does not automatically populate itself. It is a working historical editor/placement base, not a complete populated campaign economy. A future industry-placement task or explicitly approved spawning change is still needed. Historical date/proxy and multiplayer caveats from Phase 5 remain; this conversion establishes map compatibility, not full campaign balance.

JGRPP still emits unrelated existing City Objects sprite-group diagnostics and an industry map-sprite reference diagnostic. They are retained in local logs; they did not disable the fork, exhaust allocations or invalidate the 92-type inventory. No blanket warning-free claim is made.

## Evidence and reproduction

- [Original inspection](research/axis_industry_free_source.json)
- [Editor-only pilot comparison](research/axis_migration_editor_pilot.json)
- [Strict cleanup manifest](research/axis_empty_scenario_cleanup.json)
- [Final editor roundtrip comparison](research/axis_migration_editor_roundtrip.json)
- [Gameplay load/save/reload evidence](research/axis_europe_migration_runtime.json)
- [Delivered paths, hashes and original/config protection](research/axis_europe_scenario_delivery.json)

Tools: `scripts/historical_scenario_migration.py`, `stage_historical_scenario_editor.py`, `repair_industry_free_editor_candidate.py`, `test_historical_scenario_candidate.py`, `deliver_historical_scenario.py`. These scripts use the explicitly supplied source path and local audited runtime assets; they refuse overwriting existing evidence/deliverables. The UI stage was performed with the computer-use skill and the official editor, not an engine patch. Run `python -m unittest discover -s tests -p test_historical_scenario_migration.py -v` for the safety/evidence checks. Raw logs and intermediate copies remain in ignored `newgrfs/axis-historical-europe/.work/europe-migration/`. No scenario, GRF or source ZIP is committed or uploaded.
