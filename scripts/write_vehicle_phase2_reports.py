"""Build Phase 2 narrative and proposals from recorded measured tables."""
import csv,json,collections,math
from pathlib import Path
from vehicle_economy_phase2 import ROOT,R,SETS,ERAS,loadcsv,writecsv

def table(headers,rows):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+'\n'.join('| '+' | '.join(str(x).replace('|','/') for x in row)+' |' for row in rows)+'\n'
def money(v):return 'UNVERIFIED' if v in ('',None) else '£'+f'{float(v):,.0f}'
def number(v):return '—' if v in ('',None) else f'{float(v):.2f}'

def main():
    manifest=json.loads((R/'vehicle_phase2_manifest.json').read_text())
    n=loadcsv(R/'vehicle_economy_normalized.csv');sets=loadcsv(R/'vehicle_set_comparison.csv');trains=loadcsv(R/'representative_train_tests.csv');routes=loadcsv(R/'route_profitability_tests.csv');overlaps=loadcsv(R/'vehicle_overlap_comparison.csv');contexts=loadcsv(R/'vehicle_running_context_tests.csv')
    index={(r['snapshot_year'],r['test_id']):r for r in trains}
    model={(r['snapshot_year'],r['source_grfid'],r['local_vehicle_id']):r for r in n}
    def entry(y,g,i):return model[str(y),g,str(i)]
    plans=[]
    def plan(priority,y,g,i,label,target_p,target_c,confidence,evidence,consequence):
        v=entry(y,g,i);P=float(v['purchase_gbp']);C=float(v['display_running_gbp_year'])
        plans.append(dict(priority=priority,source_grfid=g,set_name=SETS[g],local_vehicle_id=i,vehicle=label,verification_year=y,current_purchase_gbp=P,proposed_purchase_gbp=target_p,purchase_change_percent=round((target_p/P-1)*100,3),current_display_running_gbp_year=C,proposed_display_running_gbp_year=target_c,running_change_percent=round((target_c/C-1)*100,3),status='PROPOSAL FOR PRIVATE BENCHMARK ONLY; NOT IMPLEMENTED',confidence=confidence,evidence=evidence,expected_effect='Remove or reduce an existing duplicate-choice trap without changing performance or dates',unintended_consequences=consequence,implementation='Targeted source economic property/callback edit; preserve GRFID/local IDs, performance, dates, all variants; cross-GRF override not proven'))
    plan(1,1970,'4D560103',134,'ST43',22265,2833,'High for discrepancy; medium for matching-cost target','Equal principal stats; equal 120t coal consist capacity and length; actual four-wagon purchase 43592 vs 35389, moving-empty rate 4143 vs 3290','Cheaper PTS version competes with adjacent PTS diesels; benchmark these too. Aligning a duplicate does not by itself lower the cheapest option already available.')
    plan(2,2025,'4D560105',1800,'EN57',43359,1068,'High for capital premium; medium for target','Same full built unit capacity and length; identical observed moving rate; PTS comparator already available at target','Check mail refits, ageing and model reliability before matching every livery; consider alternative rebuilding cost rather than indiscriminate family-wide scaling.')
    plan(3,2025,'4D560105',2100,'EN71',63281,1715,'High for purchase gap; medium/low for target','Same 364-seat built unit length and observed moving rate; comparator purchase 63281 vs 83203','Model reliability differs with seeded engine generation. The two units need repeat breakdown-duty tests before a final target is adopted.')
    plan(4,2025,'4D560105',2200,'ED72',62109,1800,'High for duplicate premium; low for the proposed trade-off point','Both built units 338 seats, same length and observed active rate; PTS speed130 versus PRSP120; current prices66796 versus85546','62109 is a policy test point on the attainable factor53 price grid: about7.0% below the faster comparator, not an extracted fair price. Check route time and demand before adoption.')
    plan(5,1990,'4D560105',570,'ET21',31640,1968,'High for measured gap; low/medium for target','Same coal capacity, length, hp and weight; PTS stronger333 vs310kN and cheaper purchase/running; four-wagon actual47108/2425 versus52967/2566','31640 is a policy test point on the factor27 price grid, about6.9% below the stronger PTS version; it restores a capital/TE trade-off instead of pricing unequal performance identically.')
    for p in plans:
        factor=round(p['proposed_purchase_gbp']*256/300000)
        assert 300000*factor//256==p['proposed_purchase_gbp']
        p['proposed_effective_purchase_factor_at_local_exponent_zero']=factor
    writecsv(R/'vehicle_balancing_candidates.csv',plans)
    coverage=[]
    for a,b in ERAS:
        row={'introduction_era':f'{a}-{b}'}
        for g in SETS:row[SETS[g]]=sum(r['snapshot_year']=='2025' and r['source_grfid']==g and r['kind']=='powered' and a<=int(r['introduction_year'])<=b for r in n)
        coverage.append(row)
    writecsv(R/'vehicle_era_coverage.csv',coverage)
    era_table=table(['Introduction era']+list(SETS.values()),[[r['introduction_era']]+[r[s] for s in SETS.values()] for r in coverage])
    comparison=table(['Set','Purchasable profiles','Raw median purchase','Raw median list running/year','Matched £/hp ratio','Matched running/hp ratio','Matched running cells'],[(r['set_name'],r['available_economic_profiles'],money(r['median_purchase_gbp']),money(r['median_display_running_gbp_year']),number(r['matched_purchase_per_hp_relative_median']),number(r['matched_running_per_hp_relative_median']),r['matched_running_per_hp_cells']) for r in sets if r['snapshot_year']=='2025' and r['kind']=='powered'])
    keys=[('1830','planet_passenger_4_uk'),('1830','grasshopper_passenger_4_uk'),('1970','st43_pts_coal_4'),('1970','st43_prsp_coal_4'),('1990','et21_pts_coal_4'),('1990','et21_prsp_coal_4'),('2025','en57_pts'),('2025','en57_prsp'),('2025','en71_pts'),('2025','en71_prsp'),('2025','ed72_pts'),('2025','ed72_prsp'),('2025','class66_uk_coal_12'),('2025','class66_gets_coal_12')]
    train_table=table(['Year / test','Actual build+refit','Capacity by AXIS label','Length tiles','Depot rate/year','Peak empty-moving rate/year'],[(y+' '+key,money(index[y,key]['purchase_actual_gbp']),index[y,key]['cargo_capacities_json'],number(index[y,key]['length_tiles']),money(index[y,key]['built_depot_running_rate_gbp_year']),money(index[y,key]['moving_empty_rate_peak_gbp_year']) if index[y,key]['moving_empty_rate_peak_gbp_year'] and float(index[y,key]['moving_empty_rate_peak_gbp_year'])>=0 else 'UNVERIFIED') for y,key in keys])
    examples=[r for r in routes if r.get('snapshot_year')=='1830' and r.get('test_id') in ['planet_passenger_4_uk','grasshopper_passenger_4_uk','planet_coal_4_uk','grasshopper_coal_4_uk'] and r.get('fill_assumption')=='1.0' and r.get('loading_unloading_turnaround_days_assumed')=='10' and r.get('cost_rate_basis')=='observed_empty_motion_proxy']
    route_table=table(['Test','Route tiles','Cruise days, one way','Capital model','Revenue model/year','Opex model/year','Profit model/year','Break-even fill'],[(r['test_id'],r['distance_tiles'],r['cruise_transit_days_lower_bound'],money(r['initial_capital_estimate_gbp']),money(r['revenue_model_gbp']),money(r['total_annual_opex_model_gbp']),money(r['annual_profit_model_gbp']),number(100*float(r['breakeven_fill_model']))+'%') for r in examples])
    counts=collections.Counter(r['status'] for r in trains);paircounts=collections.Counter(r['match_type'] for r in overlaps)
    phase2=f"""# Vehicle economy Phase 2 — 1830–2025

The six sets do **not** currently offer consistently comparable economic choices: several overlapping Polish definitions have reproducible capital or operating disadvantages without a corresponding measured performance benefit. However, the evidence does **not** justify making all six sets share one price scale, imposing a universal £/hp target, or applying a campaign-wide price increase.

The strongest supported near-term work is a small set of duplicate-family economic corrections, tested privately. Whether the *actual Europe campaign* is too profitable remains unresolved: the tests below measured construction, refitting, attachment, empty motion and payment calculations, but did not observe controlled loaded cargo delivery to accepting destinations. Calculated route envelopes are explicitly conditional, not simulated profits.

## Scope and reproducible evidence

Continued on `audit/local-vehicle-economy`; the original [inventory](VEHICLE_NEWGRF_INVENTORY.md), [price audit](LOCOMOTIVE_PRICE_AUDIT.md), [recommendations](VEHICLE_BALANCING_RECOMMENDATIONS.md), vehicle roster and six snapshots were retained byte-for-byte. The same 15 scenario GRF identities and parameter vectors were used. No original executable, GRF, scenario, save, roster, performance statistic, introduction date or multiplayer setting was changed. Test companies, construction and a capital grant existed only on disposable generated maps under `.vehicle-audit-runtime/phase2`; that grant is not counted as revenue.

Phase 2 added eight fresh observations at **1830, 1849, 1879, 1913, 1945, 1970, 1990 and 2025**, covering every requested era endpoint plus the opening year:

- **{manifest['raw_train_observations']:,} train observations**, retaining all 2,854 train definitions per snapshot.
- **{manifest['economic_profiles']:,} economic profiles across snapshots**, after conservative within-set de-duplication of identical economic/performance/availability properties. This is not a count of distinct historical prototypes.
- **{manifest['statistically_flagged_profiles']:,} statistical screening rows**, not confirmed balance defects.
- **{manifest['overlap_pairs']:,} cross-set overlap/neighbour rows**: {paircounts['name_family_and_identical_principal_stats']} named-family rows with identical listed principal stats, {paircounts['name_family_near_equivalent']} near-equivalent named rows, {paircounts['name_family_distinct_variant']} materially different named variants and {paircounts['statistical_neighbour_not_identity']} statistical neighbours. These include repeated calendar observations, not that many unique prototype pairs.
- **{manifest['train_tests']:,} requested train cases**: {counts['BUILT_REFITTED_ATTACHED']} successful builds/refits/attachments, {counts['BLOCKED']} blocked by locomotive availability, and {counts['PARTIAL_OR_FAILED']} partial 24-wagon builds rejected with `ERR_VEHICLE_TOO_LONG`. The scenario permits **seven-tile trains**. Failed/partial cases are excluded from profitability calculations.
- **227 positive-speed empty-train observations**. Successful construction is recorded separately from motion; an empty motion observation does not establish hauling capacity when loaded.
- **27,648 live cargo-income checks and 512 cargo-weight profile checks**, using the actual 64-label AXIS configuration; all matched the extracted cargo definitions and integer payment model.
- **{manifest['route_envelopes']:,} conditional route sensitivities**, plus explicit blocked maritime comparisons.

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

{era_table}

The normalized CSV classifies steam, diesel and electric using explicit resolved traction labels where present, otherwise a uniquely decoded static traction candidate. Battery shunting is noted separately below. Primary operational groups are light passenger, heavy passenger, express, light freight, heavy freight, shunting, mixed traffic and multiple units. Powered controls at <=1 hp are retained but excluded from locomotive efficiency ranking.

**Roles are inferred**, not certified historical assignments. Name cues, era-relative speed, power, TE and carrying capacity determine capability groups. Mixed traffic and heavy passenger frequently overlap in reality. Multiple-unit capacity and power-head names prevent high-speed units from being treated as freight locomotives; actual multi-part composition still requires build tests. Freight test selection is limited to currently buyable locomotives with speed <=140, rather than simply selecting the strongest high-speed unit. Legacy maximum-power `heavy_` screening cases are explicitly excluded from route economics.

The Polish sets' saved parameters use their 1918 start convention; early Polish definitions are absent before then. This is a documented roster design choice, not a pricing anomaly, and no date change is proposed. Older, less efficient engines and later technological successors are not automatically treated as peers or as balance failures.

## Normalization and statistical method

Every normalized row retains original GBP purchase/list running values and adds purchase/hp, running/hp, purchase/kN, running/kN, running/purchase, hp/t, speed/purchase, speed/running and capacity ratios. Undiscounted **5/10/20/30-year frozen-display full-duty costs** are also provided, with flags when the horizon exceeds nominal vehicle life. These are conditional `P + years × R` comparisons; they exclude resale, replacement, breakdown/repair expense and changing callbacks, and are not advertised as actual fleet lifecycle costs.

For comparisons, one economic profile receives one weight. Groups require the **same snapshot, introduction era, traction, inferred role, rail type and power octave**; multiple units additionally use a capacity octave. Wagons are split into passenger, mail, bulk, liquid, general freight and brake/control categories, with a capacity octave. At least six profiles are required for statistical dispersion; at least two sets are required for matched cross-set indices.

Outliers use log-transformed median/MAD scores, a robust-scale floor of log(1.10), threshold |z| >3.5 and at least a **1.5× practical difference** from the group median. Exactly zero MAD is not turned into an infinite score. These thresholds screen candidates; scores are not p-values or proof of imbalance. A high purchase/TE ratio can be justified for an express design; speed and TE do not have interchangeable value. The role assumptions and sparse cells remain limitations even after robust statistics.

## How the sets compare

2025 provides a useful common endpoint. Raw medians below deliberately remain labelled raw: each set has a different roster. Matched ratios are medians of set-to-cell-median ratios from comparable groups, with every eligible cell receiving equal weight. Ratios are descriptive associations, not causal estimates of a GRF multiplier.

{comparison}

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

{train_table}

Early passenger and mail were tested with 2/4/8 coaches; coal and goods used actual refits. Four-wagon mixed trains were built with COAL/GOOD/WOOD/IORE, six units each in the opening-year UKRS2-wagon cases. High-power industrial freight tests used 12 wagons, while 24-wagon attempts exposed the saved seven-tile length constraint. Modern bulk and passenger/express cases use currently buyable wagons/units; fallback wagons are selected by live availability, cargo refit and compatible rail type, and the actual chosen IDs are recorded. No assumption that all wagons carry all AXIS cargos was made.

Loaded/empty weight estimates and 0/1/3% whole-train grade force margins are in the CSV. The low-speed screen uses JGRPP's axle plus rolling resistance of approximately 25 N/t; the grade term is mass × percent ×100 N. This screens necessary traction margins but omits air drag, per-part mass rounding, actual slope occupancy, curves, power loss, braking and breakdowns. Negative uniform-3% margins in some early trains warn against assuming that a flat timetable works over European terrain. The acceleration column is a simple force/mass upper estimate, not JGRPP's complete integer time-step result.

## Conditional route profitability

The route CSV covers short industrial feeders (32 tiles), medium coal (128), long bulk (512), regional passenger (32), intercity passenger (256), and early mail (64). Maritime-versus-rail cases explicitly remain blocked: no controlled seaway, refitted ship, cargo supply and accepting destination were constructed.

A real coal-delivery fixture was also attempted in **1830 and 1970**, with an ordinary test company, full saved campaign industry density and GS deity mode verified. `GSIndustryType.CanBuildIndustry` returned false for the coal-producing Coal Mine and Bulk Terminal types, preventing controlled origin construction. The source API checks the industry's availability/probability callback; this test did not bypass that gate or change the GRF. [Attempt evidence](research/vehicle_route_attempt_evidence.log) and `BLOCKED_FIXTURE_CREATION` rows preserve the result. This does not prove that existing map-generated campaign coal mines are absent or unusable. Routing between existing producers and accepting industries, with a verified catchment, is a remaining path for a future end-to-end test. No delivery revenue or observed annual route profit was fabricated.

Unlike arbitrary real-world km-per-tile assumptions, cruise timing follows JGRPP's map-axis movement clock: two train movement passes per tick, `192 ×16 ×4/3` progress per tile and 74 ticks/day, giving **one-way days >= ceil(distance ×2048 / (74 ×speed))**. It is an optimistic cruise calculation, not measured loaded travel time. Turnaround/loading/unloading assumptions of **2/10/30 economy-days** and fill fractions **25/50/75/100%** are explicit sensitivities; no undocumented loading-speed statistic is invented. Passenger examples assume paid traffic in both directions; coal uses an empty return.

AXIS payment properties were read directly from the original installed AXIS GRF without extracting assets. Payment arithmetic is the modern JGRPP algorithm, including the long-transit tail and integer rounding. Cargo profit callbacks are absent in the validated profiles. **Full packet quantity is priced before rounding**; multiplying a rounded one-unit API quote by capacity was rejected. Every one-unit validation point matched, including all dates, distances and sampled transit times, and all cargo weights matched. The envelope uses the API's default days-to-cargo-age mapping; any vehicle-specific cargo-age callback/period affecting real deliveries remains unverified.

Capital models combine actual train command cost with measured rail/depot/station unit costs for a simple single-track route. Rail maintenance uses the engine's nonlinear whole-network formula, including **rounded-to-nearest IntSqrt**, validated against the test-layout accessor at every rail type/year. Station maintenance follows the source formula. These are modelled routes, not observed station build invoices. Land, earthworks, bridges, tunnels, signals, finance, subsidies, actual supply/acceptance, network congestion and maintenance scale shared with the rest of the company are excluded. Scenario infrastructure maintenance is enabled throughout Phase 2.

The table illustrates the **100%-filled, 10-day-turnaround, flat cruise, empty-motion-rate proxy** case. The low break-even values must not be read as guaranteed demand or real campaign profit. Loaded callbacks may differ from the empty rate, and some trains may never reach the assumed cruise speed loaded.

{route_table}

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

For a future run, use a **new tag** and preserve this report/output set in a dated directory before exporting. The runner refuses to overwrite prior runtime logs. Raw GS evidence, config hashes, original input hashes and corrections are in the manifest/evidence log. No new library or rolling stock was installed. Actual execution used the existing bundled Python at `C:\\Users\\Kladd\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe` and the existing 0.73.4 executable.

Primary implementation references are the already inspected local 0.73.4 source in the adjacent checkout's `.research/jgr734/src`: `script/api/script_engine.cpp`, `script_vehicle.cpp`, `script_cargo.cpp`, `script_infrastructure.cpp`, `engine.cpp`, `train_cmd.cpp`, `ground_vehicle.cpp`, `vehicle_base.h`, `economy.cpp`, `rail.cpp`, `station.cpp`, `maintenance_func.h`, `core/math_func.cpp`, `table/pricebase.h`, `table/railtypes.h`, `currency.cpp` and `newgrf/newgrf_act0_cargo.cpp`. These explain the arithmetic and API context; the installed GRFs and actual executable produced the reported observations.
"""
    (ROOT/'docs/VEHICLE_ECONOMY_PHASE2.md').write_text(phase2,encoding='utf8')
    plan_table=table(['Priority / vehicle','Current purchase → proposed','Change','Current list running → proposed/year','Change','Confidence'],[(str(p['priority'])+' '+p['set_name']+' '+p['vehicle'],money(p['current_purchase_gbp'])+' → '+money(p['proposed_purchase_gbp']),number(p['purchase_change_percent'])+'%',money(p['current_display_running_gbp_year'])+' → '+money(p['proposed_display_running_gbp_year']),number(p['running_change_percent'])+'%',p['confidence']) for p in plans])
    details='\n'.join(f"### {p['priority']}. {p['set_name']} — {p['vehicle']} ({p['source_grfid']} / {p['local_vehicle_id']})\n\nEvidence: {p['evidence']}.\n\nExpected effect: {p['expected_effect']}.\n\nRisk and qualification: {p['unintended_consequences']}\n\nMethod: {p['implementation']}.\n" for p in plans)
    proposal=f"""# Vehicle balancing proposal — private benchmark candidates only

**No changes have been implemented.** The smallest evidence-supported starting point is **five overlapping vehicle families**, rather than a whole-campaign multiplier or a change to performance, dates or roster. Only the ST43 matching-cost target is comparatively straightforward; the remaining targets require callback/reliability and loaded-route qualification. The absolute target points below are economic policy proposals, not extracted historical prices.

Evidence and limitations are in [Phase 2 analysis](VEHICLE_ECONOMY_PHASE2.md). The machine-readable proposal, including evidence, unintended effects and implementation method, is [vehicle_balancing_candidates.csv](research/vehicle_balancing_candidates.csv).

## Economic framework

Use contemporary duty groups and actual complete trains. Preserve the distinction between capital-constrained early operators, operating efficiency, high-speed capability, gradient capacity, loading/refit flexibility and infrastructure demand. Historical improvements may make old engines economically inferior; that is not an error to eliminate. Compare prices in constant GBP at the same settings, but preserve state-dependent running behaviour and meaningful performance trade-offs.

A change should correct a demonstrated choice trap or cost-system discontinuity, not merely move an outlier toward a median. Do not price all horsepower alike, conflate an express power head with a shunter, count liveries as independent prototypes, or treat a quoted annual cost as a billed fixed overhead. Demand and actual loaded route performance remain prerequisites for broad profitability policy.

## Prioritized candidate changes

The verification years and exact base IDs are in the CSV. Running targets refer to the same engine-list callback context as the current verified figure; any source change must then be checked in the actual built train. Values are in GBP under the saved low-cost difficulty and no inflation.

{plan_table}

For variants/liveries, apply any future change only to economically identical verified members of the intended prototype family. Do not indiscriminately change every name sharing a prefix. Preserve all GRF/local IDs, variant identities, dates, graphics, physics, capacities, refits and reliability behaviour.

The suggested purchase prices respect the current Polish sets' integer property-factor grid: `floor(300000 × factor /256)` under low construction cost and local purchase exponent zero. Proposed effective factors are respectively **19, 37, 54, 53 and 27**. These are economic-property/callback result targets, not literal pound constants to embed in a GRF. If a callback overrides the base property, its economic branch must be changed and retested. Prices under other difficulty settings scale through the normal engine formula.

{details}

## Approaches evaluated in order

1. **Existing parameters:** retain current parameters for the baseline. They are valid coarse controls, but cannot discriminate the opposite-direction ST43/ET21 overlaps or selected MU families. UKRS2 lacks a general purchase slider in its current metadata.
2. **Set-wide purchase/running multipliers:** no blanket adjustment is supported yet. NARS's half-cost option couples purchase and running; reducing high running costs would also halve capital already comparable in some groups. The add-on's independent running scale is more flexible, but halving it again would affect every era, not only an early locomotive. Raising GETS capital would change many unrelated designs and wagons. Require duty- and era-specific route outcomes before choosing such a multiplier.
3. **Targeted source definitions:** preferred for these five candidate families. Edit only economic property values or the applicable economic callback branch, rebuilding a private experimental fork while preserving identity and all non-economic definitions. The common Polish base exponents show that a global base shift is not the whole explanation. Re-test both standalone and complete trains, including nearby competitors in the same set.
4. **Compatibility/balancing GRF:** not approved as a verified arbitrary-property mechanism. JGRPP has engine-scope overrides, but that alone does not prove that a separate ordinary GRF can safely replace these cost properties through callback 0x36 and load order. A minimal private proof would be required before considering it an implementation method. No balancing GRF was created.

General base-cost controls operate by category and/or GRF, not individual engine ID. Their existence is not evidence for an individual-vehicle override capability.

## Hold unchanged for now

- **EU07, ET22, ET41:** same-price TE differences need grade, adhesion, variant and loaded-performance validation. Do not alter their physics or automatically charge a TE premium.
- **Class 66:** the capital gap is verified, but state costs, slightly different performance/length and the unresolved GETS empty-motion result prevent a sufficiently supported full-service target.
- **Planet, Grasshopper, Norris and other early stock:** their role, capital, weight, duty and route revenue trade-offs matter. The early recollection of prices is not used as an anchor, and no broad early-steam change is proposed on that basis.
- **ASF/EL16 battery shunters:** zero listed running cost at 23 hp and speed 6 is a special case worth testing, not sufficient evidence of a mainline exploit.
- **Wagons and coaches:** keep all existing types. Use capacity, usable train length, weight, actual AXIS refits and same-duty complete trains before changing price. A cheaper small coach is not interchangeable with a larger fast one.

## Adoption gate for a later implementation task

Construct matched loaded services with actual AXIS supply and acceptance and timed station orders; include flat and graded cases. Record duty-state expense, cargo packet payments, delivered volume, breakdown/repair cost, finance and allocated infrastructure. Repeat seeded reliability cases and observe vehicle/calendar ageing. Test 5/10/20/30-year cash flows with realistic replacement/resale rather than frozen new-engine rates. Resolve any hidden attachment, heating, powered-wagon or refit differences before treating a cheaper duplicate as an unconditional winner.

For each candidate, accept the change only if it removes the identified choice trap without introducing a new advantage over neighbouring contemporary engines. Re-evaluate the five-family list after those tests: it is a **minimal starting experiment**, not a proof that five changes balance the entire 195-year campaign. No release, production file change, push or merge is part of this proposal.
"""
    (ROOT/'docs/VEHICLE_BALANCING_PROPOSAL.md').write_text(proposal,encoding='utf8')
    print('Wrote Phase 2 report, proposal, coverage and candidate tables')
if __name__=='__main__':main()
