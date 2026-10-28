# Historical AXIS gameplay validation — Phase 5

**PARTIALLY READY.** These are actual JGRPP 0.73.4 engine runs of Historical Europe **0.2.0**, not a certification of the existing Europe scenario. No installed GRF, original scenario or save was edited. Work is local on `feature/axis-historical-integration`; nothing was pushed.

## Executed evidence

| Test | Evidence | Result and limit |
|---|---|---|
| Fresh 1830, 1850, 1870, 1900, 1925, 1950, 1975, 2000, 2025 | VERIFIED BY ENGINE TEST | All nine passed, with the campaign's other 14 GRFs loaded. Each checked all 92 types in deity and company contexts and inspected generated instances. Before-date BuildIndustry calls rejected. Eligibility is not a promise of a suitable placement site |
| Steelworks/EAF/BOF exact boundaries; history off; AXIS spawning off | VERIFIED BY ENGINE TEST | All 16 legacy construction fixtures rerun on the new binary passed. Eligible types were actually placed in both company and deity contexts; before-date attempts rejected. Natural generation tested separately from funding |
| One persistent 1830–2025 world | VERIFIED BY ENGINE TEST | Nine milestone checks passed; disk save reloaded in 1872. Industry counts: 50, 55, 61, 73, 82, 90, 100, 107, 117. No calendar jumps or forced closure commands. Original ID/type matches remained 50, but ID reuse means this is not a unique-lifetime census |
| Coal/ore → coke/pig iron → steel → customer | VERIFIED BY ENGINE TEST | Actual transported inputs, stockpile persistence and downstream steel delivery. Reload: 8 IRON/0 COKE; then production 6 STEL/2 SLAG; 4 STEL delivered, 2 IRON retained. Uses diagnostic default trucks, artificial fixture funding and no breakdowns; **not an economic test** |
| Cargo and model invariants | STATICALLY VERIFIED | 64 Classic slots; all 320 emitted slot/label records identical to compiled stock AXIS. All original 91 industry model records, recipes and layouts unchanged. Other economy models unchanged. Added policy wrappers are separate from those records |
| Compiled source bundle rebuild | STATICALLY VERIFIED | Extracted matching corresponding source rebuilt to identical GRF SHA256 |
| Existing Europe conversion | MANUAL TEST REQUIRED | Not hot-swapped or byte-patched. Different industry GRFID and surviving anachronistic industries prevent claiming a safe conversion |
| Editor placement, funding-window presentation, human join/rejoin/desync | MANUAL TEST REQUIRED | Precise procedures below. Static callback guards do not substitute for these runtime checks |

Machine evidence: [fresh worlds](../newgrfs/axis-historical-europe/integration-result.json), [construction boundaries](../newgrfs/axis-historical-europe/runtime-phase5-result.json), [persistent world](../newgrfs/axis-historical-europe/progression-result.json), [production](../newgrfs/axis-historical-europe/production-phase5-result.json), [binary/source](../newgrfs/axis-historical-europe/validation-phase5-result.json).

## Five-year operating services, 1830–1834

All rows below are **VERIFIED BY ENGINE TEST**: ordinary companies, actual vehicle operation, delivered cargo and negative native revenue-ledger entries. No money grants or force-enabled vehicles in these services. Each service was tested separately; they are not a three-company world. Installed vehicle binaries and parameter vectors stayed unchanged.

| Service | Delivered units over five years | Revenue, GBP | Operating profit, GBP |
|---|---:|---:|---:|
| Planet + four wagons + brake van, coal mine → coke oven | 528 | 12,936 | 3,855 |
| Four horse hopper carriages, grain → flour mill | 176 | 4,027 | **−4,813** |
| Planet + four wagons + brake van, forest → sawmill | 504 | 15,120 | 5,635 |
| Two small horse passenger carriages | 460 passengers | 5,932 | 1,358 |
| Brig passenger service | 1,357 passengers | 31,441 | 24,084 |

Profit includes native running, Property, interest, Other and sharing expenses; excludes construction and vehicle purchases. Revenue is credited income, not a cargo-payment lookup. Native money is GBP base units. Each first year is a commissioning/partial service year, not twelve full months of mature operation. The five years do not prove capital recovery. Initial cost and every annual ledger are in [gameplay years](research/axis_historical_gameplay_years.csv) and [attempts](research/axis_historical_gameplay_attempts.csv).

Stock controls of the three freight fixtures also operated for five years. Coal delivered **528** units with **£12,936** revenue in both; timber **504**, **£15,120** in both. Grain was **160/£3,547** stock versus **176/£4,027** historical. Stock operating profits were £3,654, −£5,280 and £5,708 respectively. These are similar-duty, same-seed flat fixtures, **not identical random histories**: layouts, setup timing, breakdowns and accounting differ. Do not infer a historical-fork efficiency boost from the small differences. Both versions lose money on this grain road duty. There is no evidence here for a vehicle-price change.

The inherited flat rail fixture initially shuttled between depot and source without delivery. The Phase 5 harness connects facing station ends and puts the depot behind the source. Generated-map trials also failed station/path placement. Coastal selection initially chose disconnected water or overlapping dock sites; the successful test explicitly checks legal, separate docks in connected water. Failed attempts remain documented; these are harness/layout issues, not established GRF defects. An 1830 IRON service still lacks a verified supplied blast-furnace fixture with the actual vehicle stack; the 1860 diagnostic establishes the underlying chain only.

## Settings and reproducibility

Fresh 256² maps replace the 4096² Europe geography. Gameplay fixtures inherit scalar economy, vehicle, difficulty, construction and CargoDist settings from the **embedded** `scenario_economy_settings.json`, rather than the normal config. Inflation stays off, maintenance on, train length **7**, max loan £300,000, initial cash/loan £100,000 each, normal breakdown setting. Calendar/economy years both begin 1830 in these fresh games; the campaign's saved financial-year offset is not transplanted. Arrays and town/site history are not copied. Flat freight fixtures have density zero and deity-built, date-eligible endpoints; no company paid to fund those industries. Port demand, town growth and terrain therefore differ from Europe.

Raw AXIS parameter 2 is **4** for runtime fixtures, enabling the natural/deity path; the stock campaign reference has **0**. Both stock controls and historical fixtures use 4. History parameter 10 defaults to 1. Fresh availability tests additionally enable raw-industry funding to exercise the company callback. Those are disposable test-context differences, not campaign setting changes. The progression soak enables normal industry density and actually observes industries accumulating, but is not a statistical spawning-frequency experiment.

The matrix separates **policy permission** from original map/random probability properties. Some AXIS types retain `prob_in_game=0`: a true policy flag does not give them spontaneous openings. GameScript availability queries use the engine's default probability 1, so deity construction may be allowed for such a type even while its actual natural probability remains zero. Original site/keystone rules still apply. This distinction is intentional; no upstream spawn weights were rewritten.

Run from repository root with Python 3.12 and the dependencies in `requirements-test.txt`:

```powershell
python newgrfs/axis-historical-europe/integration_test.py
python newgrfs/axis-historical-europe/progression_test.py
python newgrfs/axis-historical-europe/production_phase5.py
python newgrfs/axis-historical-europe/gameplay_test.py --controlled --case coal_rail
python newgrfs/axis-historical-europe/gameplay_test.py --controlled --case grain_horse
python newgrfs/axis-historical-europe/gameplay_test.py --controlled --case timber_rail
python newgrfs/axis-historical-europe/gameplay_test.py --case passenger_horse
python newgrfs/axis-historical-europe/gameplay_test.py --case passenger_ship
```

Repeat the three controlled freight commands with `--stock` for controls. The harness requires the exact licensed GRFs/config retained in `.vehicle-audit-runtime/phase2`, the original scenario fingerprint, and the disposable engine/base set described in the fork README. It does not fetch substitutes. Each run creates a unique local case directory; raw logs, configs, generated GS source and disposable saves remain under `.work/`. Committed JSON retains observations and hashes. `summarize_phase5.py` regenerates the research CSVs and rechecks installed assets. `python -m unittest discover -s tests -p test_axis_historical_phase5.py -v` checks the retained acceptance evidence.

## Human validation still required

1. In the disposable installation, create a new historical 1830 world with the exact 14 other GRFs. Inspect the funding window: EAF/BOF/modern factories must be unavailable; coal, coke, farms, forests and iron works available subject to raw-funding settings. Attempt a forbidden placement and retain its error.
2. Repeat in the scenario editor at 1830, 1860, 1906 and 1952. Attempt the same types before and at their dates, with ordinary editor restrictions first. Record any explicit editor ignore-restrictions option separately. Location wrappers exist, but this editor behavior has not been observed.
3. Prepare the separate Europe candidate using the migration guide. Count every industry/cargo label, inspect representative stations/refits/graphics, and operate supplied coal/coke/iron and agricultural chains at three geographically separate starting areas. Recheck route distances and availability; a successful 256² fixture proves neither geography nor competitive access.
4. Kladdey, Squirrel and Toni join the **new candidate**, save/rejoin, deliver freight and passengers, then advance through 1850 with ordinary borrowing. Retain the original stock campaign fallback. Monitor closures, breakdowns, replacements and blocked access. Never overwrite the original scenario or an existing save.
