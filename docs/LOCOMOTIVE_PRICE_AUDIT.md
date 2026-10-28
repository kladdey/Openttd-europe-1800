# Locomotive price audit — measured baseline

The player-reported **Grasshopper ≈ £6,000 / Planet ≈ £1,500** purchase-price comparison was **not reproduced** under the newest scenario's verified settings. At the common 1830 baseline the installed UKRS2 Planet is **£7,031**, while the NARS Add-On Grasshopper is **£4,687**. Their annual engine API running costs are **£525** and **£3,150**, respectively. The running-cost imbalance is real in this measurement, but the claimed fourfold purchase-price direction is not established.

## What was measured

The existing JGRPP 0.73.4 executable ran a read-only engine-query GameScript on a disposable 64 × 64 generated map. The map used the exact newest scenario's **15 GRF identities, order and parameters**, its 1830 date, matching low purchase/running difficulty, no inflation and day length 1. The original 4096-square scenario was separately loaded without saving and its final local multipliers were checked. The later autosave retains the same settings. Thus these are controlled **JGRPP API measurements**, not guessed stats or manually transcribed buy-window screenshots.

The script queries GSEngine name, design date, price, annual cost, speed, power, weight, maximum TE, default articulated capacity, reliability and cargo-refit labels. JGRPP's GRF diagnostics join runtime engine IDs to **GRFID + local ID**. Runtime IDs are session-specific; use GRFID/local ID as stable keys. The engine API calls the same Engine::GetCost/GetRunningCost property and callback path used for engine prices. No depot, locomotive or wagon was built or changed. Whole-consist attachment/refit/build-command costs have not been measured.

Results: **2,887 entries = 2,854 train entries + 33 ship entries**. Heuristic powered categories separate 1,330 locomotive/powered entries, 436 multiple-unit/railcar candidates and 42 powered control/dummy entries; 1,046 wagon entries are identified by the engine API. These counts include liveries, rather than distinct historical prototypes. There are **28 early train entries**, including **five locomotives** with runtime introduction years through 1850; the remainder are wagons. The complete loaded roster is in [vehicle_roster.csv](research/vehicle_roster.csv). Six snapshots at **1830, 1850, 1900, 1950, 2000 and 2025** provide **17,322 observations** in [vehicle_economy_snapshots.csv](research/vehicle_economy_snapshots.csv). All six runs completed their full enumeration. Future definitions queried in an early snapshot are not thereby purchasable then.

## Early locomotive comparison

Values below are the 1830 API snapshot of each definition, including later introductions. Introduction dates are game definitions, not historical claims. Some engine dates have normal game randomisation; base introduction of both Planet and Grasshopper is explicitly 1830-01-01. Reliability is a transient runtime value and must not be treated as a fixed performance advantage. Speed is the API's km-ish/h integer (mph × 1.6), not a claim of exact SI km/h.

| Set / local ID | Engine | Intro year | £ purchase | £/year | hp | kN | t | km-ish/h |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 44441000 / 113 | 0-4-0 Coppernob (Steam) | 1844 | 12890 | 1181 | 250 | 43 | 37 | 64 |
| 44441000 / 114 | 4-2-0 Crampton (Steam) | 1847 | 16406 | 1706 | 350 | 21 | 47 | 88 |
| 44441000 / 124 | 2-2-0 Planet (Steam) | 1830 | 7031 | 525 | 120 | 11 | 14 | 48 |
| 44440302 / 0 | 4-2-0 Norris | 1838 | 11718 | 6300 | 200 | 19 | 20 | 56 |
| 4E4D0518 / 116 | 0-4-0 Grasshopper (Steam) | 1830 | 4687 | 3150 | 63 | 11 | 8 | 38 |

| Engine | £/hp | £/year/hp | £/kN | Annual / purchase |
| --- | --- | --- | --- | --- |
| 0-4-0 Coppernob (Steam) | 51.56 | 4.724 | 299.7674 | 9.16% |
| 4-2-0 Crampton (Steam) | 46.8743 | 4.8743 | 781.2381 | 10.40% |
| 2-2-0 Planet (Steam) | 58.5917 | 4.375 | 639.1818 | 7.47% |
| 4-2-0 Norris | 58.59 | 31.5 | 616.7368 | 53.76% |
| 0-4-0 Grasshopper (Steam) | 74.3968 | 50.0 | 426.0909 | 67.21% |


No early GETS, Polish Train Set or Polish Rolling Stock Pack locomotive appears in the enabled-throughout-history 1830–1850 subset. This does not mean those sets failed to load: their later definitions are in the full roster. NARS's first locomotive here is the 1838 Norris. Grasshopper comes from its separate add-on.

## Planet versus Grasshopper: source, factors and modifiers

| Field | Planet | Grasshopper |
| --- | --- | --- |
| Provider | UK Railway Set (UKRS2), archive 1.05 | NARS Add-On Set 2cc rev.2401131718 |
| GRFID / local ID | 44441000 / 124 | 4E4D0518 / 116 |
| Measured runtime engine ID | 1534 | 2038 |
| Introduction | 1830-01-01 | 1830-01-01 |
| Purchase, low difficulty | £7,031 | £4,687 |
| Annual running cost, 1830 | £525 | £3,150 |
| Power / TE | 120 hp / 11 kN | 63 hp / 11 kN |
| Weight / speed | 14 t / 48 km-ish/h | 8 t / 38 km-ish/h |
| Resolved train purchase-base exponent | 0 (1×) | +1 (2×) |
| Resolved steam running-base exponent | +3 (8×) | +3 (8×) |
| Effective purchase factor inferred from exact runtime price | 6 | 2 |
| Effective running factor inferred from exact runtime cost | 4 | 24 |
| Raw factor extraction | UNVERIFIED: UKRS2 uses runtime transformations | Purchase 2 and running 24 directly decoded in Action 0 at byte offset 24148 |

"Effective factor" is a numerical inference from the verified base, local exponent and final cost, not an assertion that every raw field equals that value. Grasshopper's raw 0E running base is `0x4C30`, steam; raw power 63, weight 8 and TE coefficient 36 were also decoded. Runtime evaluation is authoritative if callbacks alter a property.

At this baseline the core train purchase base is £400,000 and steam running base £5,600 before difficulty. Low difficulty multiplies each relevant base by 6/8. With no inflation and the observed local exponents:

```text
Planet purchase     = floor(400000 × 0.75 × 6 × 2^0 / 256) = £7031
Grasshopper purchase= floor(400000 × 0.75 × 2 × 2^1 / 256) = £4687
Planet running      = floor(5600 × 0.75 × 4 × 2^3 / 256)   = £525/year
Grasshopper running = floor(5600 × 0.75 × 24 × 2^3 / 256)  = £3150/year
```

The raw purchase factor ratio is 3:1 in Planet's direction, while the add-on's purchase-base scaling adds 2× in Grasshopper's direction, producing Planet's net 1.5× price. Running bases have the same exponent, so the 6× annual running gap comes from the effective individual running factors. This is a mixture of set-level and vehicle-level definitions, not evidence for blaming one vehicle's nominal price alone.

Changing only construction difficulty from low to medium would predict Grasshopper **£6,250**, close to the player's approximate £6,000, but also predicts Planet **£9,375**, not £1,500. This is a **counterfactual calculation**, not proof of the player's original settings. Neither currency, accumulated inflation nor the latest autosave explains the entire reported pair. A company buy-window observation from the exact file/date/engine instance is still required to reconcile it. A diagnostic company-mode API query at the immediate test-map start returned "not buildable", so it supplies no additional price confirmation and is not used in the numerical tables.

At 1830, Planet adds £2,344 in capital cost but saves £2,625/year in engine running costs: simple break-even **0.893 full-cost operating years**. It has nearly twice the horsepower and higher speed, with the same API maximum TE. Grasshopper is lighter and cheaper up front, so it is **not strictly dominated on every dimension**. Actual route results depend on loads, gradients, running time, wagon speed limits, servicing and attachment behaviour.

## Complete-consist estimates, 1830 baseline

These are **additive estimates from verified individual API values**, not built-train command quotes. Four coaches deliberately compare a standard vehicle count; the capacities are unequal. Do not infer equal earning potential or equal train length.

| Representative consist | Purchase estimate | Annual cost estimate | Default seats | Notes |
| --- | --- | --- | --- | --- |
| Planet + 4 UKRS2 Passenger Coaches (ID 44) | £9,935 | £677 | 36 | 4 × £726, 4 × £38/year; 9 seats each |
| Grasshopper + 4 NARS Passenger Cars (ID 80) | £22,311 | £3,910 | 100 | 4 × £4,406, 4 × £190/year; attachment untested |
| Norris + 4 NARS Passenger Cars | £29,342 | £7,060 | 100 | Appropriate locomotive introduction is 1838 |
| Planet + 4 UKRS2 Open Wagons (ID 12) | £8,059 | £553 | 24 default cargo units | Capacity 6 each, cargo/refit compatibility must be checked |
| Grasshopper + 4 NARS Single Hoppers (ID 101) | £15,187 | £3,302 | 80 default cargo units | Capacity 20 each, attachment untested |

UKRS2's early coach is £80.67 per default seat versus NARS's £176.24. The open wagon is £42.83 per default capacity unit versus £131.25 for the NARS hopper; however they are different wagon types with different speeds, weights and cargo options. Larger wagons may save train length and total dead weight per transported unit. Mixing cheap wagons across sets is a potential exploit to test, not a verified compatible consist.

## Ten highest-priority numerical balance findings

The following are **verified displayed-stat/engine-cost discrepancies**, ranked for investigation. "Candidate domination" means the listed purchase/running/performance dimensions favour one definition. Reliability, rail compatibility, articulation, heating, cargo/refit callbacks and purchase availability can still give an apparent loser a useful role. No vehicle removal is proposed. Later-year comparisons use the **2000 snapshot**, not 1830 prices for future technology.

| Rank | Comparison and numerical evidence | Implication / limit |
| --- | --- | --- |
| 1 | 1830 Grasshopper £3,150/year, 63 hp versus Planet £525/year, 120 hp: **£50 versus £4.375/year/hp (11.43×)** | Very strong early operating-cost disparity. Planet needs extra capital and is heavier; decide whether either set's early costs fit campaign earning rates. |
| 2 | Norris (1838) £11,718 / £6,300 yearly / 200 hp / 19 kN / 56 speed; Coppernob (1844) £12,890 / £1,181 / 250 hp / 43 kN / 64 speed | A £1,172 capital premium buys a £5,119 annual saving and stronger performance. After 1844 this is a candidate economic displacement; Norris has earlier availability and lower weight. |
| 3 | Polish ST43: PTS local 134 **£30,468 / £3,686 yearly**, PRSP local 330 **£22,265 / £2,833**. Both 2,071 hp, 316 kN, 118 t, speed 100 | PRSP is £8,203 cheaper and £853/year cheaper with matching main stats. Candidate domination, pending operational callback checks. |
| 4 | ET21: PTS local 147 **£33,984 / £1,968 yearly / 333 kN**; PRSP local 570 **£39,843 / £2,109 / 310 kN**. Both 2,494 hp, 121 t, speed 100 | PTS is cheaper to buy/run and has higher TE. Candidate domination across overlapping definitions. |
| 5 | EU07: PTS local 148 versus PRSP local 620 both **£41,015 / £2,221 yearly / 2,682 hp / speed 125**; TE **223 versus 278 kN**, weight 81 versus 80 t | PRSP grants 24.7% more maximum TE without a monetary premium. Investigate axle/adhesion assumptions before treating the higher TE as historically appropriate. |
| 6 | ET22: PTS and PRSP both **£48,046 / £3,093 yearly / 4,023 hp / 120 t / speed 125**; TE **353 versus 413 kN** | PRSP offers 17.0% more TE at the same cost. A base-cost-only solution would miss the performance reason. |
| 7 | UKRS2 Class 66 local 91 **£49,218 / £10,106 yearly / 3,300 hp / 411 kN** versus GETS BR266 local 2660 **£20,507 / £6,870 / 3,200 hp / 400 kN**; both speed 120 | UKRS2 costs 2.40× to purchase and 1.47× annually for only about 3% more power/TE. Strong near-equivalent freight comparison, not strict domination. |
| 8 | EN57: PTS local 161 **£43,359**, PRSP local 1800 **£58,593**; both £1,068/year, 939 hp, 96 kN, 126 t, speed 110 and 265 default seats | PRSP premium 35.1% with matching principal passenger-unit stats. PTS also lists mail refit, so capacity does not explain this premium. |
| 9 | EN71: PTS local 162 **£63,281**, PRSP local 2100 **£83,203**; both £1,715/year, 2,092 hp, 195 kN, 182 t, speed 110, 364 seats | PRSP premium 31.5%; reliability differs in this runtime snapshot, so do not call unconditional domination. Recheck with equal reliability assumptions. |
| 10 | ED72: PTS local 163 **£66,796 / speed 130**, PRSP local 2200 **£85,546 / speed 120**; both £1,800/year, 1,877 hp, 195 kN, 182 t, 336 seats | PRSP costs 28.1% more and is slower with otherwise matching measured main stats. Candidate domination; verify whole-unit composition and callbacks. |

An additional same-cost discrepancy occurs with ET41: TE 460 versus 562 kN. Livery rows are not independent examples of a pricing anomaly; the 1,602 GETS entries include many variants and must not be used to overweight that set in aggregate statistics.

## Time-dependent costs and raw properties

The six snapshots expose effects that a binary-only factor list would miss. Planet remains £7,031 to buy, but its engine annual cost is £525 in 1830, 1850 and 1900, **£1,181 in 1950, £4,462 in 2000 and £5,775 in 2025**. Grasshopper stays £4,687 / £3,150 throughout these snapshots. This is a **GRF calendar-context effect** with inflation off; no old train was constructed and aged in the test. It is not a measured per-vehicle wear curve. Historical definitions can remain queryable after purchase expiry, so these late Planet values do not prove the player can buy it then.

The source path in JGRPP is `src/engine.cpp`: `Engine::GetCost` selects the train or wagon cost base, obtains the cost property through `GetEngineProperty`, and calls `GetPrice(..., -8)`. `GetRunningCost` similarly resolves the running factor and its steam/diesel/electric class. `src/newgrf_engine.cpp` permits callback 0x36 to replace eligible properties. `src/economy.cpp` applies difficulty, accumulated inflation, global base exponents and GRF-local exponents; `GetDisplayRunningCost` may additionally apply client calendar/day-length display scaling. GBP is a presentation unit; it is not the raw property factor.

Resolved local base exponents in this configuration (multipliers are powers of two):

| Set | Train purchase (15) | Wagon purchase (16) | Steam running (42) | Diesel running (43) | Electric running (44) |
| --- | --- | --- | --- | --- | --- |
| Polish Train Set | 0 | +4 | +1 | +1 | +1 |
| Polish Rolling Stock Pack | 0 | +4 | +1 | +1 | +1 |
| UKRS2 | 0 | +2 | +3 | -3 | +5 |
| NARS 2.52 | -1 | +3 | +4 | -3 | No explicit local entry observed |
| NARS Add-On 2cc | +1 | +3 | +3 | +2 | +1 |
| GETS | -2 | +1 | -3 | -5 | No explicit local entry observed |

An omitted entry is **not automatically zero**: defaults and inherited/global multipliers must be resolved by the engine. These exponents alone do not rank prices, because cost-factor ranges differ too. The matching Polish base exponents demonstrate that their ST43/ET21/EMU discrepancies are not explained by different set-wide base scales alone.

## Sources, reproduction and remaining uncertainty

Primary evidence is local: `C:\Users\Kladd\Documents\Codex\2026-10-28\openttd-europe-1830-2025-historical-industry\.research\jgr734\src` supplies the 0.73.4 source definitions cited above, plus `script/api/script_engine.cpp`, `table/pricebase.h`, `newgrf_config.cpp` and the `sl`/`saveload` loaders. Public cross-checks: [JGRPP source at release](https://github.com/JGRennison/OpenTTD-patches/tree/jgrpp-0.73.4/src), [train property specification](https://newgrf-specs.tt-wiki.net/wiki/Action0/Vehicles/Trains), [GETS 0.7 catalogue identity](https://bananas.openttd.org/package/newgrf/53410808/2026-05-03T23%3A08%3A38%2B00%3A00). The public specification explains property formats; the locally executed JGRPP build determines reported numbers.

Preserved evidence: [runtime rows](research/vehicle_runtime_evidence.log), [engine mapping and multiplier diagnostics](research/vehicle_runtime_mapping.log), [scenario references](research/scenario_vehicle_references.json), [snapshot manifest](research/vehicle_snapshot_manifest.json), [parameter definitions](research/vehicle_grf_parameters.json). The checked-in data contain metadata and measurements only, no GRF assets.

Repeat from repository root, using an installed Python with NumPy (the existing scenario chunk module imports it). First choose a **new** output directory for the raw scan; the scanner refuses to overwrite an existing inventory. The preparation/export scripts currently use the recorded `vehicle_audit_v2` path; update that path for a new dated run and retain prior reports in a dated directory before regenerating. The preparation utility copies source files only into `.vehicle-audit-runtime/newgrf` and does not install anything.

```powershell
python scripts/audit_vehicle_newgrfs.py --root "$env:USERPROFILE/Documents/OpenTTD/newgrf" --root "$env:USERPROFILE/Documents/OpenTTD/content_download/newgrf" --root "$env:USERPROFILE/Documents/OpenTTD/scenario" --root "$env:USERPROFILE/Downloads/OpenTTD/newgrf" --root "$env:USERPROFILE/Downloads/OpenTTD/scenario" --output docs/research/vehicle_audit_v2
python scripts/vehicle_audit_tables.py
python scripts/extract_vehicle_grf_parameters.py
python scripts/prepare_vehicle_probe.py
python scripts/run_vehicle_probe.py --exe "$env:USERPROFILE/Downloads/OpenTTD/openttd.exe" --year 1830 --log probe-detailed.log
python scripts/run_vehicle_probe.py --exe "$env:USERPROFILE/Downloads/OpenTTD/openttd.exe" --scenario "$env:USERPROFILE/Documents/OpenTTD/scenario/Europe 1800 V2 newGRFS.scn" --ticks 1 --log scenario-load.log
# Repeat the runtime probe with --year 1850, 1900, 1950, 2000 and 2025,
# giving each log the corresponding name probe-1850.log, etc.
python scripts/export_vehicle_audit.py
python scripts/analyze_vehicle_snapshots.py
python scripts/write_vehicle_audit_reports.py
python scripts/validate_vehicle_audit.py
```

Actual execution used the bundled Python `C:\Users\Kladd\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`; no dependencies were installed. OTTS/zstd autosave decoding uses the already installed Git `libzstd.dll`; OTTX scenarios use Python lzma. Files were never extracted from TARs into the installation.

UNVERIFIED: exact purchase-expiry/retirement dates; historical accuracy of each model's attributes; all MU/DVT classifications; built-consist costs and articulation effects; refitted capacities for every cargo; actual route revenue and profitability; company-specific/depot buy-window confirmation of the reported prices; compatibility/attachment of mixed-set wagons; existing-vehicle age/wear running costs. API -1 values are explicitly UNVERIFIED in the roster (the snapshot CSV preserves the raw -1). Introduction randomisation and reliability values mean not every future definition's date/reliability is identical across independent starts. No statistical extrapolation replaces these missing tests.
