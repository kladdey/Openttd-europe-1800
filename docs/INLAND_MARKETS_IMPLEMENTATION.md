# Phase 6C: implemented inland markets

The separate playable candidate is **Europe 1830 Historical AXIS 0.3.0 - Inland Markets.scn**, saved in `C:\Users\Kladd\Documents\OpenTTD\scenario`. SHA-256: `afcab50864e87f56a7260c62d87bd37560fa3d7676713afb14c480c555d0bc06`.

It contains **75 new retail industries in 61 existing towns**, bringing the scenario to **542 industries of 43 placed types**. All 617 original town identities, names and centres and all 467 original industries remain. No NewGRF change or migration is needed. Use the already installed `axis-historical-europe-0.3.0-candidate.grf`, SHA-256 `f0da622873c91107fa4d2b768d88cd95d5db009c2b2975bdb6d7ab6caaed3c33`. Do not replace GRFs in an existing save.

## Actual construction mechanism

**VERIFIED IN GAME — JGRPP 0.73.4.** Existing Historical AXIS retail types solve the acceptance shortage:

| Local industry ID | Type | Added | Declared and engine-accepted cargos |
|---|---|---:|---|
| 61 | General Store | 45 | FOOD, GOOD, BEER |
| 59 | Food Market | 18 | FOOD, FRUT, BEER |
| 57 | Hardware Store | 12 | GOOD, BDMT |

The source definitions and compiled runtime registration agree. These are one-tile `OnlyInTown`, road-adjacent industries, available to company construction in 1830. Normal deity construction is rejected under the preserved spawning callback. The supported company-mode `GSIndustryType.BuildIndustry` command legitimately replaces a HOUSE tile through the engine's town-clearing logic. It does not require new industry types or bypassing Historical AXIS.

A disposable London proof built industry 467 at tile 5233314, replacing vanilla house 25: population 11004 → 10992. Both FOOD and GOOD were accepted. The final network independently verifies each market's accepted cargo list, and full-candidate save/reload verifies persistence.

Construction fixtures receive technical funds outside company mode and temporarily disable industry-platform leveling; the original platform setting is restored before saving. There is **no terrain leveling in the delivered candidate**. Original PATS/settings and DATE chunks are retained. No construction company, grant, loan or transport fixture is promoted into the scenario.

## Selection and demolition safeguards

The planner minimizes excess producer-to-consumer Manhattan distance above a **160-tile diagnostic threshold**, with town size, historical commercial importance and hub spacing constraints. This is a regional coverage screen, not a profitability guarantee. Initial hubs require population ≥400 and at least 15 house tiles; the gap-filling extension permits ≥300. Hubs normally remain at least 110 Manhattan tiles apart. Twelve larger centres receive complementary Food/Hardware pairs; other selected hubs receive General Stores.

The completed sequence was 59 markets at 47 hubs, ten additional regional stores, then six Food Markets addressing FRUT acceptance. Those six are Bordeaux, Reims, Valencia, Sevilla, Firenze and Caltagirone, 41–84 Manhattan tiles between their town anchors and selected orchards (actual industry/stop distances differ slightly). General Stores do **not** accept FRUT. Villages do not automatically receive stores, and consumers are not placed beside every producer.

Only ordinary, unprotected, completed one-tile buildings adjacent to existing roads were selected. Parks, fountains, statues, churches, stadiums and protected buildings are excluded. An early trial included four parks; it was discarded and construction restarted from the immutable baseline with the stronger filter. It is not the delivered scenario.

**75 ordinary house tiles were replaced; all were 12-resident cottages. Total population loss: 900.** Every cumulative per-town reduction is below 5%; the maximum is **3.870968%**, Łomża 310 → 298. There were no final failed placement requests: all 75 selected requests succeeded on their first submitted valid site. The bounded site lists and exact engine receipts are retained. A bad Squirrel Unicode-escaping trial and superseded route fixtures were not promoted.

## Preservation and file handling

Source: `Europe 1830 Historical AXIS 0.3.0 Candidate - Industrialized.scn`, SHA-256 `b05ef51a3bd17eb453d6b5e4af544c0745fee372a6195f5354ab8bd927ce6e75`.

The candidate pipeline copies actual engine-generated town, map and industry records into a separately framed save, retaining the original untouched chunks and neutralizing new industry founders. It never invents town populations or constructs an industry by editing its binary definition. Both gameplay and Scenario Editor subsequently load/save the result.

Independent decoded comparisons establish:

- All **467 original INDY records and existing persistent-storage records** are bit-identical.
- All 617 town IDs, names and centres survive; population changes are engine-generated and reconciled per town.
- Exactly **75 map tiles** change, precisely the authorized HOUSE → INDUSTRY sites. Terrain heights, water classification, existing roads, bridges, stations and other infrastructure change on **zero tiles**.
- All 15 GRF identities, checksums and parameter bytes, all other settings and original calendar/economy dates are preserved. Calendar 1830, economy 1800, seven-tile limit, maintenance on, inflation off and spawning off remain the baseline.
- Other original chunks are identical except the intended CITY/INDY/map and associated engine-managed storage/animation/station-name records. Existing PSAC records are unchanged prefixes; ANIT and STNN are also identical.

The final file was created exclusively with `open('xb')`; neither source scenario nor GRF was overwritten. See [delivery manifest](research/inland_scenario_delivery.json), [preservation results](research/inland_preservation.json), [placements](research/inland_market_placements.csv) and [75 engine receipts](research/inland_market_engine_receipts.json).

## Historical interpretation

These markets represent **regional retail and wholesale activity**, not identified individual 1830 shop addresses. Town anchors and existing industrial regions determine geography; the algorithm cannot establish the historical existence of a particular building. Major-centre preferences reflect the requested historical commercial hierarchy; smaller hub choices are explicitly inferred gameplay representations.

Documented precedents include London's established [Covent Garden market](https://www.coventgarden.london/the-cg-edit/the-history-of-covent-garden), Vienna's [Naschmarkt history](https://www.wien.gv.at/en/leisure/naschmarkt-history), and [Leipzig's longstanding trade fairs](https://www.leipziger-messe.de/en/company/portrait/history/). Vienna's modern 1916 market location is not projected back to 1830. The [Kraków museum study](https://journals.akademicka.pl/krzysztofory/en/article/view/7719) documents changing historic market commerce, rather than a fictitious unchanged modern retail layout. Existing Scandinavian, Baltic, Eastern and Balkan town anchors support representative regional destinations; the dataset does not claim archival verification of each store.

## Reproduction

Use Python with NumPy/Pillow and the existing local JGRPP/assets/source tree. The session used `C:/Users/Kladd/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8`. Run without `-O`: safety assertions are required. Every engine run creates a unique disposable directory under `newgrfs/axis-historical-europe/.work/inland6c`, with isolated configuration, exact GRF assets, command/script hashes, engine log and exit save.

```powershell
python scripts/inland_phase6c_inventory.py --proof
python scripts/inland_phase6c_plan.py
python scripts/inland_phase6c_place.py
python scripts/inland_phase6c_candidate.py
python scripts/inland_phase6c_plan.py --extend
python scripts/inland_phase6c_place.py --extend
python scripts/inland_phase6c_candidate.py
python scripts/inland_phase6c_fruit_plan.py
python scripts/inland_phase6c_place.py --fruit
python scripts/inland_phase6c_candidate.py
python scripts/inland_phase6c_coverage.py
python scripts/inland_phase6c_reload.py
python scripts/inland_phase6c_regrowth.py
python scripts/inland_phase6c_regressions.py
python scripts/inland_phase6c_services.py rail_food --years 5
python scripts/inland_phase6c_services.py local_food --years 3
python scripts/inland_phase6c_services.py farm_fruit --years 3
python scripts/inland_phase6c_services.py local_goods --years 3
python scripts/inland_phase6c_services.py regional_food --years 3
python scripts/inland_phase6c_services.py coastal_food --years 3 --partial-load
```

`INLAND_ROUTE_RANK=1` selects the second bounded candidate for `long_goods` (five years) and the second unsuccessful `coastal_goods` road attempt. Default is rank 0. `coastal_goods_water` is a separately recorded unsuccessful shipping alternative. `--grant --partial-load` is only for technical salt/copper regressions. A fresh controlled copper regression uses the existing `industrial_phase6b_controls.fresh(script('copper'), 'phase6c-regression-copper', 600000)` helper; its scope is a separate 256×256 fixture, not Europe profitability. Run `inland_phase6c_evidence.py` after collecting cases, and the focused tests with `python -m unittest discover -s tests -p test_inland_phase6c.py`.

Candidate promotion refuses to overwrite an existing intermediate scenario. A rerun must use its newly returned path and must not overwrite the delivered file. GUI editor verification used an isolated `editor-final-*` directory; [its manifest](research/inland_editor_validation.json) records the exact commands and disposable save. The source/NewGRF hashes are checked on every run. No push or merge is part of this phase.
