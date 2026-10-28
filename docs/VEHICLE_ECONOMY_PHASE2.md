# Vehicle economy Phase 2 — 1830–2025

The six sets do **not** currently offer consistently comparable economic choices: several overlapping Polish definitions have reproducible capital or operating disadvantages without a corresponding measured performance benefit. However, the evidence does **not** justify making all six sets share one price scale, imposing a universal £/hp target, or applying a campaign-wide price increase.

The strongest supported near-term work is a small set of duplicate-family economic corrections, tested privately. Whether the *actual Europe campaign* is too profitable remains unresolved: the tests below measured construction, refitting, attachment, empty motion and payment calculations, but did not observe controlled loaded cargo delivery to accepting destinations. Calculated route envelopes are explicitly conditional, not simulated profits.

## Scope and reproducible evidence

Continued on `audit/local-vehicle-economy`; the original [inventory](VEHICLE_NEWGRF_INVENTORY.md), [price audit](LOCOMOTIVE_PRICE_AUDIT.md), [recommendations](VEHICLE_BALANCING_RECOMMENDATIONS.md), vehicle roster and six snapshots were retained byte-for-byte. The same 15 scenario GRF identities and parameter vectors were used. No original executable, GRF, scenario, save, roster, performance statistic, introduction date or multiplayer setting was changed. Test companies, construction and a capital grant existed only on disposable generated maps under `.vehicle-audit-runtime/phase2`; that grant is not counted as revenue.

Phase 2 added eight fresh observations at **1830, 1849, 1879, 1913, 1945, 1970, 1990 and 2025**, covering every requested era endpoint plus the opening year:

- **22,832 train observations**, retaining all 2,854 train definitions per snapshot.
- **15,000 economic profiles across snapshots**, after conservative within-set de-duplication of identical economic/performance/availability properties. This is not a count of distinct historical prototypes.
- **373 statistical screening rows**, not confirmed balance defects.
- **398 cross-set overlap/neighbour rows**: 60 named-family rows with identical listed principal stats, 15 near-equivalent named rows, 19 materially different named variants and 304 statistical neighbours. These include repeated calendar observations, not that many unique prototype pairs.
- **994 requested train cases**: 314 successful builds/refits/attachments, 659 blocked by locomotive availability, and 21 partial 24-wagon builds rejected with `ERR_VEHICLE_TOO_LONG`. The scenario permits **seven-tile trains**. Failed/partial cases are excluded from profitability calculations.
- **227 positive-speed empty-train observations**. Successful construction is recorded separately from motion; an empty motion observation does not establish hauling capacity when loaded.
- **27,648 live cargo-income checks and 512 cargo-weight profile checks**, using the actual 64-label AXIS configuration; all matched the extracted cargo definitions and integer payment model.
- **8,700 conditional route sensitivities**, plus explicit blocked maritime comparisons.

Main files: [normalized roster](research/vehicle_economy_normalized.csv), [outliers](research/vehicle_economy_outliers.csv), [set comparison](research/vehicle_set_comparison.csv), [overlaps](research/vehicle_overlap_comparison.csv), [built train tests](research/representative_train_tests.csv), [route sensitivities](research/route_profitability_tests.csv), [manifest and input hashes](research/vehicle_phase2_manifest.json), [condensed runtime evidence](research/vehicle_phase2_runtime_evidence.log).

## Measurement validation and corrections

| Question | Finding and implication |
| --- | --- |
| Currency | `currency.cpp` defines GBP rate **1**, so script money values match GBP numerically. Currency presentation does not explain set-to-set differences. Phase 2 retains the original client's GBP setting rather than replacing its enum string from a saved numeric table. |
| Inflation | Campaign PATS disables inflation and ECMY stores 65536/65536, i.e. 1.0. Fresh tests also disable inflation. Prices are comparable in the same constant internal pounds; no inflation deflator was applied. |
| Difficulty | Purchase and running settings are both low in every test: relevant base prices use 6/8 of medium. These common factors do not explain differences between the six sets. |
| Phase 1 snapshots | Their configurations differ in starting year, not their cost/inflation/day-length assumptions. They are valid engine-list snapshots, not measurements of one persistent fleet ageing for 195 years. |
| Campaign mismatch found | Phase 1 copied client configuration with **infrastructure maintenance false**, while the scenario saves **true**. This does not invalidate engine purchase costs, but would invalidate route estimates that omitted maintenance. Phase 2 applies saved campaign settings before generating its test layout. Linkgraph distribution also differed; the saved passenger/mail/default distribution settings were restored in the disposable configuration. Full differences are in the manifest. |
| Calendar/economy time | Saved calendar mode, day length 1, cargo ageing rate 100 and modern cargo-payment algorithm 1. Running APIs use economy-years; at this day length/calendar mode no additional calendar display multiplier is needed. Real-time minutes per calendar year are not a separate price multiplier here. |
| Availability | Deity-mode engine validity means enabled at some point, not currently buyable. Phase 2 creates an ordinary test company and measures `IsBuildable` before construction. Contemporary set statistics exclude non-buyable/future entries. No purchase expiry dates were guessed from model life. |
| Reliability | Engine-model reliability varies with engine seed/age and calendar context. It is retained as an observation, but excluded from de-duplication and treated as a confounder in dominance conclusions. It is not a fixed historical locomotive rating. The generated test-map seed is not claimed to reproduce every saved campaign engine seed. |
| Engine versus actual train costs | `GSEngine.GetRunningCost` uses a no-vehicle callback context; `GSVehicle.GetRunningCost` traverses the actual consist and queries per-vehicle callbacks. Depot, moving, loading/age/consist context can change rates. Engine-list annual cost is not a fixed annual bill. |
| Stopped/idle expenses | JGRPP accrues running ticks when a train is not flagged stopped, or is still physically moving. A fully stopped parked train does not automatically pay a quoted annual depot rate. Some callbacks return lower rates in depot/loading contexts. Actual expenditure needs duty time. Our instantaneous `stopped_query` is explicitly invalid as an expense measurement because the script speed getter masks speed after setting the stopped flag. |
| Capacity and weight | Refit/attachment queries revealed real capacities different from default engine-list capacities. Built capacities take precedence for those tests. Empty weights are still sums of catalogue weights; loaded weights are continuous estimates from verified cargo weights. Actual train cargo weight rounds per part. No claim of a fully measured loaded mass is made. |
| Static traction decoding | Raw Action 0 IDs may be transformed by Action 6. A unique static candidate is therefore not always the right runtime engine: UKRS2 Class 66 would be wrongly classified as steam by that shortcut. Resolved GRF traction labels take precedence; remaining static-class candidates are identified as such. No unqualified runtime traction getter is claimed. |
| Livery and alternative variants | All raw entries remain. Identical economic profiles get one weight per statistical group. Different prices, capacities, rail types, dates, refits or availability remain separate. Named overlap detection retains prototype aliases even when economic de-duplication merges two equivalent profiles. |

**Conclusion on reliability:** Phase 1 is reliable for its stated engine-list context and file identities. It is insufficient on its own for annual operating expense, refitted full-train capacity or actual route profit. Phase 2 corrects those interpretations without replacing the original evidence.

## Historical eras, traction and roles

The table counts powered definitions above 1 hp by runtime introduction year, using the full 2025 catalogue (including expired entries) to show historical coverage. It is not a table of engines available to buy in 2025 and is not de-duplicated historical production volume.

| Introduction era | GETS | UKRS2 | Polish Train Set | Polish Rolling Stock Pack | NARS 2.52 | NARS Add-On 2cc |
| --- | --- | --- | --- | --- | --- | --- |
| 1830-1849 | 0 | 3 | 0 | 0 | 1 | 1 |
| 1850-1879 | 0 | 5 | 0 | 0 | 3 | 5 |
| 1880-1913 | 98 | 6 | 0 | 0 | 8 | 13 |
| 1914-1945 | 226 | 10 | 14 | 20 | 18 | 39 |
| 1946-1970 | 174 | 13 | 17 | 38 | 22 | 73 |
| 1971-1990 | 97 | 7 | 12 | 46 | 10 | 30 |
| 1991-2025 | 309 | 10 | 16 | 394 | 9 | 19 |


The normalized CSV classifies steam, diesel and electric using explicit resolved traction labels where present, otherwise a uniquely decoded static traction candidate. Battery shunting is noted separately below. Primary operational groups are light passenger, heavy passenger, express, light freight, heavy freight, shunting, mixed traffic and multiple units. Powered controls at <=1 hp are retained but excluded from locomotive efficiency ranking.

**Roles are inferred**, not certified historical assignments. Name cues, era-relative speed, power, TE and carrying capacity determine capability groups. Mixed traffic and heavy passenger frequently overlap in reality. Multiple-unit capacity and power-head names prevent high-speed units from being treated as freight locomotives; actual multi-part composition still requires build tests. Freight test selection is limited to currently buyable locomotives with speed <=140, rather than simply selecting the strongest high-speed unit. Legacy maximum-power `heavy_` screening cases are explicitly excluded from route economics.

The Polish sets' saved parameters use their 1918 start convention; early Polish definitions are absent before then. This is a documented roster design choice, not a pricing anomaly, and no date change is proposed. Older, less efficient engines and later technological successors are not automatically treated as peers or as balance failures.

## Normalization and statistical method

Every normalized row retains original GBP purchase/list running values and adds purchase/hp, running/hp, purchase/kN, running/kN, running/purchase, hp/t, speed/purchase, speed/running and capacity ratios. Undiscounted **5/10/20/30-year frozen-display full-duty costs** are also provided, with flags when the horizon exceeds nominal vehicle life. These are conditional `P + years × R` comparisons; they exclude resale, replacement, breakdown/repair expense and changing callbacks, and are not advertised as actual fleet lifecycle costs.

For comparisons, one economic profile receives one weight. Groups require the **same snapshot, introduction era, traction, inferred role, rail type and power octave**; multiple units additionally use a capacity octave. Wagons are split into passenger, mail, bulk, liquid, general freight and brake/control categories, with a capacity octave. At least six profiles are required for statistical dispersion; at least two sets are required for matched cross-set indices.

Outliers use log-transformed median/MAD scores, a robust-scale floor of log(1.10), threshold |z| >3.5 and at least a **1.5× practical difference** from the group median. Exactly zero MAD is not turned into an infinite score. These thresholds screen candidates; scores are not p-values or proof of imbalance. A high purchase/TE ratio can be justified for an express design; speed and TE do not have interchangeable value. The role assumptions and sparse cells remain limitations even after robust statistics.

## How the sets compare

2025 provides a useful common endpoint. Raw medians below deliberately remain labelled raw: each set has a different roster. Matched ratios are medians of set-to-cell-median ratios from comparable groups, with every eligible cell receiving equal weight. Ratios are descriptive associations, not causal estimates of a GRF multiplier.

| Set | Purchasable profiles | Raw median purchase | Raw median list running/year | Matched £/hp ratio | Matched running/hp ratio | Matched running cells |
| --- | --- | --- | --- | --- | --- | --- |
| GETS | 137 | £68,261 | £7,485 | 0.76 | 1.13 | 19 |
| UKRS2 | 21 | £43,359 | £11,681 | 1.27 | 1.82 | 4 |
| Polish Train Set | 31 | £52,734 | £3,093 | 1.00 | 0.91 | 13 |
| Polish Rolling Stock Pack | 270 | £46,875 | £2,315 | 1.01 | 0.94 | 20 |
| NARS 2.52 | 12 | £50,976 | £18,637 | 1.00 | 2.33 | 5 |
| NARS Add-On 2cc | 22 | £48,046 | £9,354 | 1.00 | 1.41 | 7 |


Across the sampled eras GETS generally offers cheaper capital per horsepower in matched groups; UKRS2 and NARS often have higher quoted running cost per horsepower; Polish sets generally have lower running-cost ratios. The add-on sits between these systems in many later groups. This is not evidence that every GETS locomotive is a bargain, every NARS engine is bad, or a high-cost design lacks a role. The available count, matched-cell count, duty behaviour, usable capacity and performance matter.

Wagon costs differ independently from locomotive costs. The saved set-local purchase exponents are: train/wagon **GETS -2/+1; UKRS2 0/+2; PTS and PRSP 0/+4; NARS -1/+3; add-on +1/+3**. These are powers of two applied to different underlying property factors, not relative final prices. Steam/diesel/electric running categories have their own scales. It would be incorrect to normalize only locomotive prices and presume that complete trains then match.

Verified parameter mechanisms are retained from installed Action 14 metadata: NARS has a coupled halve-purchase-and-running switch; its add-on has independent purchase/running scales (currently 1× and 1/2×); GETS has separate running and purchase selectors (currently their defaults); the Polish sets expose separate purchase/running scales at defaults. UKRS2's exposed current metadata has no broad purchase slider. UKRS2 parameter display indices use MASK mappings, so raw zeros do not mean its locomotives are disabled.

**What explains differences:** shared OpenTTD difficulty/currency/inflation do not explain cross-set gaps here; explicit GRF-local scales and individual cost factors/callbacks do. Matched Polish overlaps have the same set-local base exponents, so their opposite price advantages cannot be explained away by one global scale. State-dependent costs and invalid static-ID interpretation were genuine methodological confounders, now separated from raw cost definitions.

## Duplicates, poor choices and justified differences

ST43, ET21, EU07, ET22, EN57, EN71, ED72 and Class 66 were all examined. Programmatic overlap discovery also found counterparts including ST44, ET40, ET41, ET42, EP05, EP09, EU43/EU44, several steam classes and newer units; [overlap CSV](research/vehicle_overlap_comparison.csv) preserves variant/year/physics/refit evidence. Statistical neighbours do not establish common historical identity. Generic wheel-arrangement names alone do not identify the same prototype.

The strongest economy-choice traps under the tested conditions are:

1. **PTS ST43 versus PRSP ST43:** both 2,071 hp, 316 kN, 118 t, speed 100. The same 120-tonne coal consist is 2.375 tiles long in both cases, but PTS costs £8,203 more to build and £853/year more at the measured empty-moving rate. Availability, actual attachment and capacity are verified in 1970/1990. A breakdown/reliability and loaded-duty qualification remains before declaring unconditional operational domination.
2. **PRSP EN57:** a capital premium over the PTS equivalent survives actual whole-unit builds. Built capacity is **264 seats**, not the earlier default-list 265, and both have equal length and measured active running rate.
3. **PRSP EN71:** both whole units have 364 seats and equal length/running rate, while the premium survives construction. Seeded model reliability differs, so an absolute claim of domination would go too far.
4. **PRSP ED72:** both built units have **338 seats** and equal length/observed running rate; PRSP costs £18,750 more and has lower maximum speed (120 versus 130). Equal model reliability and nominal life in the sampled 2025 run strengthen the comparison, but other seeds and operation still merit verification.
5. **PRSP ET21:** equal hp, weight, capacity and test consist length, but the PTS alternative has higher TE and lower purchase/running expense in the tested state. It is a stronger candidate for targeted pricing than for a whole-set multiplier.

Other differences are trade-offs or unresolved, rather than confirmed defects:

- EU07 and ET22/ET41 have same-cost TE advantages in one collection. Extra TE can matter on grades; their actual performance definitions are not being changed. Pricing compensation needs loaded acceleration/grade tests and historical variant checks first.
- Class 66 is close in role, year, power, weight, TE and speed, but not identical. UKRS2 is dearer to buy and quotes a lower depot rate; GETS built successfully but no positive speed appeared in its short orderless test window, for either bare or tested coal train. The cause is unresolved. No GETS motion cost or loaded-route profit is fabricated, and no Class 66 price target is recommended yet.
- A zero-running-price ASF battery shunter exists in the Polish collections: **£1,171, 23 hp, 39 kN, speed 6**. That is a special low-speed yard tool, not evidence of a free high-performance mainline engine. Its four raw entries include livery variants. It is retained without a proposed nerf pending an actual yard-use exploit test.
- Higher capacity, higher speed, greater TE, lower empty weight, earlier availability, useful refits and consist length can justify higher prices. Different traction/gauge/role variants and ordinary generational improvement are not normalized away. Documented author intent was not inferred merely from price differences.

## Complete train tests

These are actual GS-accounted build/refit/attach command costs and real vehicle capacity/length queries. Annual rates are state queries; **they are not billed annual expenditure**. Moving observations were empty, on short flat stubs; they were not loaded-route performance runs. `UNVERIFIED` means no positive-speed observation, not zero running cost.

| Year / test | Actual build+refit | Capacity by AXIS label | Length tiles | Depot rate/year | Peak empty-moving rate/year |
| --- | --- | --- | --- | --- | --- |
| 1830 planet_passenger_4_uk | £9,935 | {"PASS": 36} | 1.06 | £283 | £546 |
| 1830 grasshopper_passenger_4_uk | £7,591 | {"PASS": 36} | 0.94 | £3,302 | £3,302 |
| 1970 st43_pts_coal_4 | £43,592 | {"COAL": 120} | 2.38 | £944 | £4,143 |
| 1970 st43_prsp_coal_4 | £35,389 | {"COAL": 120} | 2.38 | £944 | £3,290 |
| 1990 et21_pts_coal_4 | £47,108 | {"COAL": 120} | 2.31 | £738 | £2,425 |
| 1990 et21_prsp_coal_4 | £52,967 | {"COAL": 120} | 2.31 | £822 | £2,566 |
| 2025 en57_pts | £43,359 | {"PASS": 264} | 2.00 | £393 | £1,068 |
| 2025 en57_prsp | £58,593 | {"PASS": 264} | 2.00 | £393 | £1,068 |
| 2025 en71_pts | £63,281 | {"PASS": 364} | 2.62 | £393 | £1,715 |
| 2025 en71_prsp | £83,203 | {"PASS": 364} | 2.62 | £393 | £1,715 |
| 2025 ed72_pts | £66,796 | {"PASS": 338} | 2.62 | £478 | £1,800 |
| 2025 ed72_prsp | £85,546 | {"PASS": 338} | 2.62 | £478 | £1,800 |
| 2025 class66_uk_coal_12 | £88,590 | {"COAL": 360} | 5.75 | £4,258 | £10,821 |
| 2025 class66_gets_coal_12 | £59,879 | {"COAL": 360} | 6.06 | £8,241 | UNVERIFIED |


Early passenger and mail were tested with 2/4/8 coaches; coal and goods used actual refits. Four-wagon mixed trains were built with COAL/GOOD/WOOD/IORE, six units each in the opening-year UKRS2-wagon cases. High-power industrial freight tests used 12 wagons, while 24-wagon attempts exposed the saved seven-tile length constraint. Modern bulk and passenger/express cases use currently buyable wagons/units; fallback wagons are selected by live availability, cargo refit and compatible rail type, and the actual chosen IDs are recorded. No assumption that all wagons carry all AXIS cargos was made.

Loaded/empty weight estimates and 0/1/3% whole-train grade force margins are in the CSV. The low-speed screen uses JGRPP's axle plus rolling resistance of approximately 25 N/t; the grade term is mass × percent ×100 N. This screens necessary traction margins but omits air drag, per-part mass rounding, actual slope occupancy, curves, power loss, braking and breakdowns. Negative uniform-3% margins in some early trains warn against assuming that a flat timetable works over European terrain. The acceleration column is a simple force/mass upper estimate, not JGRPP's complete integer time-step result.

## Conditional route profitability

The route CSV covers short industrial feeders (32 tiles), medium coal (128), long bulk (512), regional passenger (32), intercity passenger (256), and early mail (64). Maritime-versus-rail cases explicitly remain blocked: no controlled seaway, refitted ship, cargo supply and accepting destination were constructed.

A real coal-delivery fixture was also attempted in **1830 and 1970**, with an ordinary test company, full saved campaign industry density and GS deity mode verified. `GSIndustryType.CanBuildIndustry` returned false for the coal-producing Coal Mine and Bulk Terminal types, preventing controlled origin construction. The source API checks the industry's availability/probability callback; this test did not bypass that gate or change the GRF. [Attempt evidence](research/vehicle_route_attempt_evidence.log) and `BLOCKED_FIXTURE_CREATION` rows preserve the result. This does not prove that existing map-generated campaign coal mines are absent or unusable. Routing between existing producers and accepting industries, with a verified catchment, is a remaining path for a future end-to-end test. No delivery revenue or observed annual route profit was fabricated.

Unlike arbitrary real-world km-per-tile assumptions, cruise timing follows JGRPP's map-axis movement clock: two train movement passes per tick, `192 ×16 ×4/3` progress per tile and 74 ticks/day, giving **one-way days >= ceil(distance ×2048 / (74 ×speed))**. It is an optimistic cruise calculation, not measured loaded travel time. Turnaround/loading/unloading assumptions of **2/10/30 economy-days** and fill fractions **25/50/75/100%** are explicit sensitivities; no undocumented loading-speed statistic is invented. Passenger examples assume paid traffic in both directions; coal uses an empty return.

AXIS payment properties were read directly from the original installed AXIS GRF without extracting assets. Payment arithmetic is the modern JGRPP algorithm, including the long-transit tail and integer rounding. Cargo profit callbacks are absent in the validated profiles. **Full packet quantity is priced before rounding**; multiplying a rounded one-unit API quote by capacity was rejected. Every one-unit validation point matched, including all dates, distances and sampled transit times, and all cargo weights matched. The envelope uses the API's default days-to-cargo-age mapping; any vehicle-specific cargo-age callback/period affecting real deliveries remains unverified.

Capital models combine actual train command cost with measured rail/depot/station unit costs for a simple single-track route. Rail maintenance uses the engine's nonlinear whole-network formula, including **rounded-to-nearest IntSqrt**, validated against the test-layout accessor at every rail type/year. Station maintenance follows the source formula. These are modelled routes, not observed station build invoices. Land, earthworks, bridges, tunnels, signals, finance, subsidies, actual supply/acceptance, network congestion and maintenance scale shared with the rest of the company are excluded. Scenario infrastructure maintenance is enabled throughout Phase 2.

The table illustrates the **100%-filled, 10-day-turnaround, flat cruise, empty-motion-rate proxy** case. The low break-even values must not be read as guaranteed demand or real campaign profit. Loaded callbacks may differ from the empty rate, and some trains may never reach the assumed cruise speed loaded.

| Test | Route tiles | Cruise days, one way | Capital model | Revenue model/year | Opex model/year | Profit model/year | Break-even fill |
| --- | --- | --- | --- | --- | --- | --- | --- |
| planet_passenger_4_uk | 32 | 19 | £14,375 | £11,756 | £588 | £11,168 | 5.00% |
| planet_coal_4_uk | 32 | 19 | £12,499 | £2,509 | £492 | £2,018 | 19.59% |
| planet_coal_4_uk | 128 | 74 | £19,699 | £3,049 | £997 | £2,052 | 32.70% |
| grasshopper_passenger_4_uk | 32 | 24 | £11,461 | £9,641 | £2,829 | £6,812 | 29.34% |
| grasshopper_coal_4_uk | 32 | 24 | £9,585 | £2,077 | £2,728 | £-651 | 131.35% |
| grasshopper_coal_4_uk | 128 | 94 | £16,785 | £2,433 | £3,547 | £-1,114 | 145.78% |


Thus early railways cannot be labelled uniformly too expensive or uniformly overprofitable. Under these specified assumptions passenger services can have attractive capital recovery, while the tested Grasshopper coal service remains unattractive even at full fill. The smaller passenger threshold says more about passenger payment, capacity and assumed two-way demand than about an intrinsically fair locomotive price. There is no measured Europe-wide demand/utilisation series or loaded delivery result establishing a campaign-level nerf.

## Lifecycle and operating-cost interpretation

Quoted annual costs become expenditure only through activity time and callback state. Infrastructure, loan interest and repair expenses are separate. Route sensitivities scale the selected rate by cruise-active time and exclude dwell-running expense, so they can understate waiting/loading cost; conversely, no breakdown or terrain delay is modelled. Both engine-list and observed empty-rate proxy variants remain in the data. A low parked rate is not automatically a useful annual saving.

The 5/10/20/30-year normalized costs freeze one snapshot's rate. Actual lifecycle evaluation would require constructing the train and observing it through calendar ageing, vehicle ageing, maintenance and replacement, or a verified callback model. A 30-year freeze beyond nominal vehicle life is flagged, rather than silently treating an expired train as new. The old Planet's later engine-list rates are not proof of a surviving train's wear curve, or of continued availability.

## Balancing conclusion and remaining tests

Existing parameters can address a broad set-wide offset, but **cannot solve most of the confirmed local overlap problems**: ST43 favours PRSP, ET21 favours PTS, and the passenger-unit premiums occur in selected families. A scalar that fixes one of these can worsen another. No global multiplier change is recommended from these data.

The [proposal](VEHICLE_BALANCING_PROPOSAL.md) specifies five private benchmark candidates with current/target costs, percentages, evidence and confidence. Prices are proposals, not extracted fair values. No implementation was performed. Required next checks are controlled loaded routes with real AXIS producer/consumer acceptance, matched supply/demand and station orders, callback duty-state and ageing tests, reliability/breakdown replication, and resolution of the GETS Class 66 motion result. More detailed historically documented role/variant classification is also needed before using statistical rankings as policy.

## Reproduction

The existing Phase 1 local copies are prerequisites; do not rerun its installation search. From repository root:

```powershell
python scripts/run_vehicle_phase2.py --tag verified --years 1830 1849 1879 1913 1945 1970 1990 2025 --ticks 220000
python scripts/vehicle_economy_phase2.py --tag verified
python scripts/write_vehicle_phase2_reports.py
python -m unittest discover -s tests -p test_vehicle_economy_phase2.py -v
python scripts/validate_vehicle_audit.py
```

For a future run, use a **new tag** and preserve this report/output set in a dated directory before exporting. The runner refuses to overwrite prior runtime logs. Raw GS evidence, config hashes, original input hashes and corrections are in the manifest/evidence log. No new library or rolling stock was installed. Actual execution used the existing bundled Python at `C:\Users\Kladd\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` and the existing 0.73.4 executable.

Primary implementation references are the already inspected local 0.73.4 source in the adjacent checkout's `.research/jgr734/src`: `script/api/script_engine.cpp`, `script_vehicle.cpp`, `script_cargo.cpp`, `script_infrastructure.cpp`, `engine.cpp`, `train_cmd.cpp`, `ground_vehicle.cpp`, `vehicle_base.h`, `economy.cpp`, `rail.cpp`, `station.cpp`, `maintenance_func.h`, `core/math_func.cpp`, `table/pricebase.h`, `table/railtypes.h`, `currency.cpp` and `newgrf/newgrf_act0_cargo.cpp`. These explain the arithmetic and API context; the installed GRFs and actual executable produced the reported observations.
