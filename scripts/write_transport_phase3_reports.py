"""Publish Phase 3 observations. Does not change or regenerate Phase 1/2 research."""
import csv,json,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs';R=D/'research'
def load(name):
    with (R/name).open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))
def money(x):return f"£{float(x):,.0f}"
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,row))+' |' for row in rows])
def main():
    results=load('transport_route_results.csv');summaries=load('transport_mode_comparison.csv');by={r['tag']:r for r in summaries};exp=load('transport_expansion_test.csv');attempts=load('transport_test_attempts.csv')
    chosen=['ship-pax-final','ship-barque','ship-schooner','rail-lodi','horse-lodi','horse-existing-road','horse-london','horse-city-road','horse-coal-final','horse-coal-fleet4','rail-coal-ledger','rail-coal-12-brake','rail-coal-24-brake','rail-coal-keep','rail-coast','horse-coast','rail-general2','rail-wood-final','rail-grasshopper','rail-wood-grasshopper','horse-mail']
    overview=table(['Test / retained tag','Years','Initial infrastructure + fleet','Mean revenue/year','Mean net cash/year','Observed capital payback'],[[t,by[t]['observed_years'],money(by[t]['initial_capital_gbp']),money(by[t]['mean_annual_revenue_gbp']),money(by[t]['mean_annual_net_cash_gbp']),by[t]['observed_capital_payback_years']] for t in chosen if t in by])
    coastal=table(['Koper–Trieste mode/configuration','Mean revenue, 1831–1834','Mean net cash, 1831–1834','Mean delivered units/year'],[[t,money(by[t]['common_mean_revenue_gbp']),money(by[t]['common_mean_net_cash_gbp']),by[t]['common_mean_delivered_units']] for t in ['ship-pax-final','ship-barque','ship-schooner','rail-coast','horse-coast'] if t in by])
    growth=load('company_growth_simulations.csv')
    milestones=table(['Strategy','Observed years','Cash','Loan','Cumulative operating cash profit','Capital invested so far'],[[tag,n,money(x['cash_gbp']),money(x['loan_gbp']),money(x['cumulative_post_construction_cash_profit_gbp']),money(x['initial_capital_investment_gbp'])] for tag in ['ship-pax-final','rail-lodi','rail-coal-ledger','horse-coal-fleet4','horse-transition'] for n in [5,10,15,20] for x in growth if x['tag']==tag and int(x['years_after_start'])==n])
    main_report=f'''# Transport economy Phase 3

The 1830 economy can support profitable shipping and passenger railways. Horses have a much narrower margin: an eight-carriage coal company retained enough cash to add a railway after ten years, mainly from its unspent starting reserve, but several passenger/mail strategies lost money. **A complete three-player campaign has not been validated, and a robust economic niche for horses is not yet established.** These are operational observations on disposable copies of the actual Europe scenario, not forecasts derived from cargo-payment tables.

There are **{len(results)} route-year observations across {len(summaries)} operating configurations**, plus **{len(exp)} observed company-years in the horse-to-rail expansion**. Two unchanged fleets ran for twenty economy-years. Actual paid deliveries cover PASS, MAIL, COAL, GRAI and WOOD. Failed fixtures and exploratory harness errors remain in the [attempt register](research/transport_test_attempts.csv), outside successful financial comparisons.

## Environment and preservation

- Branch: `audit/local-vehicle-economy`. Nothing pushed or merged. Phase 1/2 research remains byte-identical to the input manifest.
- Executable: `C:\\Users\\Kladd\\Downloads\\OpenTTD\\openttd.exe`, JGRPP **0.73.4**, original binary. Local runtime copies/hardlinks of already-installed assets; no additional rolling stock.
- Source: `C:\\Users\\Kladd\\Documents\\OpenTTD\\scenario\\Europe 1800 V2 newGRFS.scn`, SHA-256 `5710beea8b3badf6aecc8ab679caea1fb2c4b66e96c4393b342a816c064e0688`, 4096×4096, calendar 1830-01-01.
- The disposable scenario changes only **GSDT**, attaching a measurement Game Script where no active GS was configured. Every other chunk, including geography, industries, PATS, DATE, ECMY, engine state and NGRF, is preserved. A byte-for-byte encoder roundtrip verifies this claim independently of the copy manifest.
- All **15** referenced NewGRF identities match their OpenTTD MD5s in the test assets. GRF v2 identity MD5 covers its data section, not necessarily the entire binary; original SHA-256 fingerprints are retained separately.
- Normal configuration, scenarios, saves, executables and GRFs were not edited. `-c test.cfg -x`, null drivers, autosaving disabled and per-case directories isolate writes. The measurement GS uses ordinary company construction/build/refit/order/loan commands, with no money grants.

Evidence: [copy manifest](research/transport_scenario_copy_manifest.json), [input hashes](research/transport_phase3_inputs.json), [validation](research/transport_validation.json), [15 identities and parameters](research/scenario_vehicle_references.json), [complete saved settings and live confirmations](research/transport_economic_settings.json).

## Embedded economic settings

| Setting | Actual baseline |
| --- | --- |
| New company | £100,000 cash, £100,000 loan, maximum loan £300,000; interest 2% |
| Currency | GBP, internal money rate 1; original currency presentation retained |
| Inflation | Disabled; saved price/payment multipliers both 65536 = 1.0 |
| Construction / running difficulty | Both low, 0; original per-GRF parameters retained |
| Infrastructure maintenance | **Enabled**, both saved and runtime confirmed; paid Property expenses measured |
| Train length | **Seven tiles**, unchanged; platforms and consists described per test |
| Breakdowns | Saved level 1; actual ageing/reliability and operating expenses observed |
| Time | Calendar-based timekeeping 0, day length 1, cargo ageing 100, payment algorithm 1 |
| Distribution | Passenger/mail symmetric 2; default cargo asymmetric 1 |
| Towns | Growth rate 2; other embedded town controls retained in settings JSON |
| Industries | AXIS 2.3.1, economy parameter 0; saved restriction bit and all production/supply parameters retained |
| Subsidies | Saved multiplier/duration retained. Income is actual game revenue, including any applicable game awards; subsidy events were not separately instrumented |

**Clock correction:** calendar DATE is 668394 (1830-01-01), economy DATE is 657437 (1800-01-01). `GSDate.GetCurrentDate` reads economy time in this JGRPP version. The offset is **10,957 days**, not a price multiplier. Financial year 1800 maps to the campaign's opening 1830 window. Leap-year alignment can shift later window boundaries by a day. CSVs retain economy years and exact mapped calendar bounds. Twenty economy-years finish in late 1849. Phase 2's equal annual rate assumption remains useful; interpreting every script year as a calendar year would be incorrect.

## Measurement method and qualifications

The GS locates real towns/industries, tests legal construction commands, commits a route, builds/refits existing vehicles, issues orders and starts them. No industries are created. Construction/fleet expenditure comes from actual bank debits, **not GSAccounting dry-run totals**. Dry-run path search also accumulates hypothetical command costs in that object, so those totals were rejected.

Most railway cases use a Planet with four UKRS2 wagons/coaches, two-tile platforms and the unchanged seven-tile limit. Coal/grain/timber are actual homogeneous refits. The longer freight cases use twelve wagons plus brake van with four-tile platforms, or twenty-four plus brake van with seven-tile platforms. Their observed lengths are **44/16 and 80/16 tiles**, both within seven. Road fleets use actual eGRVTS two-horse carriages; shipping uses Sailing Ships brig, barque and schooner. Actual refitted capacities appear in the route CSV, rather than inferred catalogue capacities.

Cargo loading is sampled every five ticks. Positive load, company cargo-delivered counters and actual credited transport income establish successful delivery. Monthly position/speed/profit traces give additional evidence. Annual finance-ledger categories provide running, Property, interest and Other expenses where available. Earlier runs have measured quarterly operating expenses plus the source-verified £300 annual Other charge, explicitly labelled ENGINE-CALCULATED aggregation. No payment estimate is used as delivered income.

The £300 Other charge is a recurring company charge from `economy.cpp`'s monthly interest routine, `_price[Price::StationValue] >> 2`, distinct from paid infrastructure maintenance. Quarterly `expenses` omit this category. Vehicle profit also excludes company interest and infrastructure. These omissions can turn an apparently profitable carriage into a losing company.

Cash is sampled about one day after the financial-year boundary, whereas the annual ledger covers the completed finance year. A delivery crossing that boundary can create a visible difference. [Validation](research/transport_validation.json) retains all ledger-versus-cash differences rather than forcing them to match. Annual ledger net and observed cash change are separate columns. Capital payback means the first observed year cumulative operating cash profit actually covers initial investment. No projected payback is substituted when it was not reached. Means include the partial construction year unless the common-period column is used.

**Fixture correction:** initial road fixtures used clear land for stops and no bridge construction. Later variants allow stops on existing town roads, existing bridge/tunnel connections and legal wooden road bridges. Their scripts and results remain separate. Greenfield failures are not evidence that every possible horse strategy fails. Path search is bounded and is not a human route optimizer. Rail bridge/tunnel/terraforming construction is not automated.

Loaded-sample fraction means time sampled with any cargo, **not** capacity utilization. Station-tile touches are retained as raw observations, not departures or a reliable service frequency. Ship visits occur on docking water tiles, so the simple station-tile counter can be zero despite verified deliveries. Timetable frequency, full capacity load factors, breakdown-delay attribution and actual loaded mass are UNVERIFIED. The observed accounts include their real combined effects under the baseline settings.

## Actual company results

All rows below are VERIFIED IN GAME. Pounds are constant GBP. Revenue and cash are observed; means are arithmetic summaries. Different routes carry different demand and are not interchangeable investments. `NOT REACHED` means not recovered within the actual observation period.

{overview}

Full fields: [route results](research/transport_route_results.csv), [mode comparison](research/transport_mode_comparison.csv), [company growth](research/company_growth_simulations.csv). Raw evidence is [retained as text](research/transport_runtime_evidence.log), without redistributing GRF assets.

## Comparable coastal task

These services connect the same Koper and Trieste towns. They use different legal station sites, catchments, gradients and paths; this is a comparable task, not a pure causal estimate of mode alone. To remove unequal horizons and construction-year effects, this table uses the same four complete finance-years, approximately **1831–1834**.

{coastal}

Shipping's advantage in these fixtures is operationally real. The land services showed low loaded-speed samples and weak delivery rates. Siting, catchments, path geometry, grades and consist effects were not isolated, so the deficit cannot be attributed to terrain alone. Shipping cannot directly replace inland Lodi–Crema or a mine away from navigable water. No unlimited profit exploit is established; competitive demand limits remain unmeasured. A three-company market test remains necessary.

## Freight scalability and handling rules

Planet four-wagon coal service is viable but slow to recover its investment. The twelve-wagon service **with the existing 10t Brake Van** materially improves throughput and cash earnings. The twenty-four-wagon service fits the limit but performs worse on this alignment: loaded monthly samples include 2 km/h. Greater capacity does not guarantee greater profit.

Without the brake van, both twelve- and twenty-four-wagon builds succeeded but start failed with `ERR_NEWGRF_SUPPLIED_ERROR`. Adding only the existing UKRS2 brake van allowed operation. The GRF contains a brake-van requirement string. The exact returned localized string ID was not decoded, so the diagnosis rests on the controlled start/fail comparison plus that definition. This is a supported train-formation rule, not evidence of an engine or scenario bug. Original blocked runs remain visible.

Timber from forest 869 to sawmill 369 produced, loaded, delivered and paid, but both tested locomotives lost money on the route. Loaded slow-running samples support a hauling/alignment problem; the evidence does not justify calling the WOOD cargo chain broken. Grain from farm 260 to flour mill 286 was profitable. No assumption was made that every wagon accepts every AXIS cargo.

## Longitudinal and company growth

{milestones}

The explicit expansion case starts with eight horse coal carriages. After ten finance-years the company has **£19,355 cash and £30,000 loan**. It builds a Planet passenger railway for **£14,529**, leaving **£4,826**, while the horses keep working. After five further observed years it has **£20,510 cash**, the same **£30,000 loan**, and **£27,136 total capital investment**. It received no grant and borrowed no additional money. Ten-year horse profit was **£1,962**, compared with the **£14,529** railway purchase; most affordability came from unspent starting borrowing. This demonstrates an actual cash-financed transition, not profit-funded railway capital accumulation or a prediction from theoretical headroom. Aggregate delivered units after expansion mix passengers and coal and must not be treated as single-cargo tonnage. See [expansion ledger](research/transport_expansion_test.csv).

This qualification matters for mode balance. The eight-horse coal fixture costs £12,607 initially, versus £16,283 for the twelve-wagon railway. Both are immediately affordable from £100,000 starting cash. In the common 1831–1834 window, mean net cash is £216.50/year for the horses versus £3,597.50 for rail, with mean delivered units 236 versus 468. Rail's higher throughput is a real technological advantage, but the small capital barrier weakens the proposed horse-first progression. A positive horse profit alone does not prove an attractive niche. Test optimized local/feeder work before deciding whether intervention is needed.

Unused-loan management matters. The two-year coal control retaining the original £100,000 loan pays £2,000/year interest. Repaying idle borrowing leaves a £30,000 loan and £600/year interest. This normal management action changes the railway from loss to profit without any economic-setting change. The 10k liquidity buffer is a tested strategy choice, not a campaign setting.

The unchanged twenty-year Planet fleet remains cash-positive over the full run but operating expense grows with age/context. The unchanged inter-town horse fleet loses money and ends with negative cash; no expansion or rescue borrowing was commanded. This is evidence about those strategies, not a statement that a human must leave an ageing fleet untouched. Replacement, broader fleets, optimal station placement and competing companies need further validation.

## Planet, Grasshopper and Phase 2 proposals

The controlled costs remain Planet £7,031 / list running £525 and Grasshopper £4,687 / £3,150. Both have listed TE 11 kN; Planet is 120 hp, 14t, 48 speed, Grasshopper 63 hp, 8t, 38 speed. They differ in weight and performance. Under identical four-wagon coal duty, the Grasshopper's lower capital price did not compensate for operating cost. Its timber test also lost more. These two duties support a targeted concern, not an automatic whole-NARS discount or a claim about every possible consist.

The ST43, ET21, EN57, EN71 and ED72 proposals retain their Phase 2 catalogue/build evidence. **None gained later-era loaded-route validation here.** They remain private benchmark candidates, not approved changes. No future snapshot is presented as a 1830 observation. No ordinary cross-GRF arbitrary-property override is claimed. Existing cost controls are broad and can alter otherwise sound vehicles; there is no Phase 3 basis for a campaign-wide multiplier.

## Reproduction and remaining work

Run from the repository with the bundled Python. Example (choose a fresh tag):

```powershell
python scripts/transport_phase3.py --script scripts/transport_phase3_services.nut --tag coal-repeat --ticks 180000 --constants 'CASE <- "coal_repeat"; MODE <- "rail"; CARGO <- 14; A <- 438; B <- 456; ENGINE <- 1534; POLICY <- "repay_idle"; YEARS <- 5; ENDPOINTS <- "industry"; WAGONS <- 12; PLATFORM <- 4; BRAKE_VAN <- true;'
python scripts/analyze_transport_phase3.py
python scripts/write_transport_phase3_reports.py
python scripts/validate_transport_phase3.py
python -m unittest discover -s tests -p "test_transport_phase3.py"
```

Frozen per-case measurement scripts and parameters are in [harness sources](research/transport_harness_sources.json) and [run configurations](research/transport_run_configs.json). For exact retained harness replay, use `--replay rail-coal-12wagons --tag a-new-tag --ticks 5000`; this blocked case was replayed successfully to verify the mechanism. Replays require the retained exact assets/configuration template and matching original scenario. Financial headline exports use an explicit selected-tag set; add new accepted cases deliberately. Existing logs are never overwritten. Runtime copies stay ignored by Git.

Read the [test matrix and manual procedures](TRANSPORT_ECONOMY_TEST_MATRIX.md) for uncompleted cases. Priority gaps are a real three-company trial, maritime freight with supported feeder/wharf arrangements, reliable coastal mail catchments, later duplicate tests and actual replacement/expansion variants. No result establishes subjective enjoyment or competitive fairness from a single-company automated run.

Validation: nine Phase 3 evidence/finance tests and eleven preserved Phase 2 economy tests pass. Original-file validation checks 83 GRF instances and all fifteen scenario identities. An attempted full repository discovery also encountered eight unrelated geography-test import errors because the bundled Python lacks SciPy, with 38 tests skipped; those tests/dependencies were not changed or installed. The scoped economy checks and scenario-preservation checks pass independently.
'''
    (D/'TRANSPORT_ECONOMY_PHASE3.md').write_text(main_report,encoding='utf8')
    matrix='''# Transport economy test matrix

Statuses distinguish observation from arithmetic. VERIFIED IN GAME means the installed engine performed the event in a disposable actual-scenario copy. ENGINE-CALCULATED means a live command test/query or documented arithmetic, not delivered revenue. MODELLED / ESTIMATED is reserved for assumptions; no modelled route-profit row is substituted for these tests. BLOCKED / NOT TESTED means the stated observation is absent.

## Coverage

| Requested task | Evidence / retained tags | Status and practical limit |
| --- | --- | --- |
| Local passengers | horse-city-road, horse-london, horse-local-bridge3 | VERIFIED IN GAME, five years each. Urban services, legal existing stock. Local rail on identical stops NOT TESTED |
| Regional passengers | rail-lodi, horse-lodi, horse-existing-road | VERIFIED IN GAME, same Lodi/Crema towns, different legal sites/catchments; five to ten years |
| Coastal passengers | ship-pax-final, ship-barque, ship-schooner, rail-coast, horse-coast | VERIFIED IN GAME; common four-year comparison in main report |
| Coastal mail | ship-mail | BLOCKED: automated Koper mail stop siting found no acceptable legal dock. This is a siting/catchment result, not proof the ship cannot carry mail |
| Mail delivery | horse-mail | VERIFIED IN GAME, four actual mail-refitted horse carriages, Oldham–Manchester, five years; loss-making strategy |
| Short industrial feeder | horse-coal-final, horse-coal-fleet4, rail-coal-ledger | VERIFIED IN GAME, mine 438 to coke oven 456; one/eight horses versus four-wagon train |
| Medium coal | rail-medium, mine 237 to power plant 76 | BLOCKED: bounded rail builder found no contiguous station/path without rail bridges/tunnels/terraforming. Not an AXIS cargo or industry-creation failure |
| Longer industrial bulk | rail-wood-final, rail-wood-grasshopper | VERIFIED IN GAME, forest 869 to sawmill 369, five years each, losses and loaded low speeds |
| Grain chain | rail-general2 | VERIFIED IN GAME, farm 260 to flour mill 286, five years, profitable |
| Longer coal consists | rail-coal-12-brake, rail-coal-24-brake | VERIFIED IN GAME; actual refits/formation/start/delivery. Seven-tile limit preserved |
| Brake-van control | rail-coal-12wagons, rail-coal-24wagons, replay-brake-required | BLOCKED without brake van despite legal length; controlled resolution by adding existing brake van |
| Mixed manufactured freight on one train | Phase 2 refit tests plus homogeneous Phase 3 cargo routes | BLOCKED / NOT TESTED for paid mixed-cargo operation; requires multiple accepting branches and adequate upstream production |
| Bulk ship versus rail | coastal-industry-check | ENGINE-CALCULATED dock feasibility screen, not a loaded maritime freight test |
| 1830–1835 / 1835–1840 | see annual rows | VERIFIED IN GAME for multiple routes and modes |
| 1840–1850 | rail-coal-ledger, horse-passenger-final2 | VERIFIED IN GAME to late 1849, unchanged fleets; no optimal replacement policy claimed |
| Company growth/rail transition | horse-transition | VERIFIED IN GAME, ten years horses then five with added railway, same company and loan |
| Loan strategy | rail-coal-keep versus rail-coal-ledger | VERIFIED IN GAME; normal company debt action, unchanged loan ceiling/interest settings |
| ST43/ET21/EN57/EN71/ED72 | Phase 2 findings | BLOCKED / NOT TESTED in loaded future-era operation in Phase 3; no proposed correction implemented |
| Three competing human companies | none | BLOCKED / NOT TESTED. Requires the multiplayer trial below |

Endpoints, actual station coordinates, costs, capacity and annual accounts are in [route results](research/transport_route_results.csv). [All attempts](research/transport_test_attempts.csv) include exploratory script errors; failed/incomplete builds are not counted as profitable routes. [Existing industries](research/transport_existing_industries.csv), [towns](research/transport_existing_towns.csv) and [buyable opening vehicles](research/transport_available_1830.csv) permit further fixture selection without another disk scan.

## Coal-construction blocker resolved

Local authoritative source paths are under:

`C:\\Users\\Kladd\\Documents\\Codex\\2026-10-28\\openttd-europe-1830-2025-historical-industry\\.research`

1. `jgr734/src/script/api/script_industrytype.cpp::CanBuildIndustry` uses `IndustryAvailabilityCallType::RandomCreation` for deity-mode construction and UserCreation for company construction.
2. `axis/src/templates/availability.pynml` routes gameplay random creation through the availability parameter; the zero value returns `CB_RESULT_IND_NO_CONSTRUCTION`.
3. `axis/src/templates/header.pynml` defines `restrict_open_during_gameplay` at **parameter 2, bit 2**. Installed AXIS Action 14 independently confirms MASK **020201**, labelled “Allow industries spawning during gameplay.” The scenario's AXIS vector is `[0,0,0,0,0,0,16,150,80,300]`, so that bit is zero. Labels can be confusing: inspect the callback result, not the variable name alone. [Source hashes and installed mask](research/transport_source_checks.json) preserve the check.
4. Company raw-industry construction is also disabled by the saved setting 0. Scenario-editor availability follows a separate allowed branch. Neither AXIS nor JGRPP was patched.

The scenario already has suitable producers: the inventory identified **1,387 industries** and **613 towns**. Mine 438 produces COAL and coke oven 456 accepts it; paid deliveries demonstrate that this chain works. There was no need to change industry construction rules or build an artificial world. The earlier generated-map fixture failure is not evidence that the actual campaign lacks coal.

Additional source checks: `script_date.cpp` proves the economy-time API basis, also verified against [the official JGRPP 0.73.4 source](https://github.com/JGRennison/OpenTTD-patches/blob/jgrpp-0.73.4/src/script/api/script_date.cpp); `company_cmd.cpp` defines which expense categories enter quarterly graphs; `economy.cpp` handles actual maintenance, interest and Other charges; `script_vehicle.cpp::GetLength` returns cached ground-vehicle length. These sources were read locally, not modified.

## Maritime freight feasibility screen

The live test inspected **84 coal-producing/accepting industries**, including **35 positive-production coal producers**, for an immediately legal dock on untouched coast within a five-tile industry catchment. Eleven producers had candidate sites; **no consumer did**. No examined coal site had a built-in dock. Details: [coastal coal sites](research/transport_coastal_coal_sites.csv).

This screen is bounded: it does not terraform a shore, construct canals, extend a station inland, or add a feeder. It does **not** establish that coal shipping is impossible. It explains why there is no honest direct mine-to-consumer maritime profit row. A connected-water component is checked before ship construction; the first failed pilot selected a depot on disconnected water, which was corrected in subsequent successful services.

## Smallest manual completion procedures

Perform all steps in a fresh isolated scenario copy with the same fifteen GRFs and seven-tile/maintenance settings. Keep financial screenshots or exported ledgers and dated saves inside the disposable workspace. Never overwrite the campaign source.

1. **Three-player opening:** one player starts a coastal passenger service, one an inland passenger railway, one a small horse freight/local network. Use the normal £100k loan/cash, permit ordinary loan repayment, and record every capital debit and annual finance category. Run 1830–1835, then 1835–1840; allow actual reinvestment/replacement and record it separately. In the second pass, contest one coastal market to measure split demand and CargoDist effects. Finish 1840–1850 if earlier results are acceptable.
2. **Mail catchment:** inspect the Koper/Trieste dock catchment overlays in the test copy. Choose a larger viable coastal town or a legal combined dock/post-office station. Verify MAIL production and acceptance and actual ship refit before buying. Run the same 1831–1834 observation window. Record any extra station infrastructure in capital/Property costs; do not treat a large catchment extension as free.
3. **Bulk maritime chain:** begin with mine 667 or one of the screened Bulk Terminals. Find an accepting industry's water access. Use supported shore construction, a canal or a separately costed horse/rail feeder if necessary. Confirm continuous navigable water in both directions. Track transfer credits separately from final company receipts and verify final accepted cargo/revenue. Repeat with rail on its actual land alignment, retaining geographical differences.
4. **Medium coal / difficult alignment:** connect mine 237 to power plant 76 using ordinary bridge/tunnel/terrain tools. First run Planet + 12 Open Wagons + 10t Brake Van, with platforms long enough and total length <=7. Measure loaded speed across each grade. If it stalls, test a shorter consist before changing economics.
5. **Mixed industrial freight:** use actual nonzero producers; Machine Shop and several factories initially have zero output and require inputs. Establish one valid upstream supply before measuring downstream freight. Refit each wagon explicitly, unload to accepting branches, and record capacity/weight per cargo. No name-only compatibility assumptions.
6. **Later duplicates:** use an appropriate disposable future snapshot with the same GRFs/parameters. For each exact ST43/ET21/EN57/EN71/ED72 pair, use the same wagons/refits, line, stopping pattern and observation dates. Record full train purchase, running/Property/interest, reliability, delivered units and revenue for at least three full years. Do not implement Phase 2 targets before those comparisons.

For every manual service, capture date, vehicle/refit/consist and length, actual path/endpoints/grades, station catchments, original and loaded capacity, route construction, capital, loan actions, yearly income/running/Property/interest/Other, delivered cargo, departures/journey times, ageing, breakdowns and subsidy awards. Use `VERIFIED IN GAME` only once cargo loading, accepting delivery and credited income are each visible. Otherwise record the precise missing observation as `BLOCKED / NOT TESTED`.
'''
    (D/'TRANSPORT_ECONOMY_TEST_MATRIX.md').write_text(matrix,encoding='utf8')
    findings='''# Transport economy findings and campaign readiness

**Provisional verdict: playable businesses and an actual horse-to-rail transition are demonstrated. Competitive balance and enjoyment for three players remain unverified. No balancing changes should be applied from this phase alone.**

## Executive assessment

| Question | Answer and evidence |
| --- | --- |
| Is 1830 playable? | Yes for several observed strategies. Capital requirements fit the actual starting loan/cash; paid deliveries and positive company cash flow were observed. This is not a certification of every start location |
| Can ships make money? | Yes. Brig, barque and schooner carried passengers and earned substantial net cash on Koper–Trieste. Brig recovered initial capital in one observed year; barque in two |
| Can horses make money? | Yes, narrowly and inconsistently. Eight coal carriages produced a small positive ten-year company result. A later railway purchase relied mainly on unspent starting cash. Several local/passenger/mail fixtures lost money or had weak five-year results |
| Can early railways make money? | Yes. Lodi–Crema passenger rail recovered initial capital within four observed years. Coal profitability improves with a legal longer consist; timber/poor coastal alignment can lose money |
| Are modes differentiated? | Geography and infrastructure produce real differences: shipping excels on this coast, rail works inland, and horse entry is affordable but margins are fragile. Whether horses have a satisfying competitive niche needs human testing |
| Are infrastructure costs appropriate? | They matter and are actually charged, but no universal verdict is justified. Four-wagon coal rail used £4,290 infrastructure; road siting changed costs materially. Legal twelve-wagon rail outperformed the larger alternative. No maintenance/length relaxation is supported |
| Can a company grow without an obvious exploit? | Demonstrated once: a horse company bought a railway after ten years from cash, mostly its unspent starting reserve, then ran five further years with the same £30,000 loan. Unrestricted coastal profit replication/three-player market sharing remain untested |
| Any vehicles or cargo chains clearly broken? | No campaign-blocking cargo defect was established. Coal, grain, timber, passengers and mail all paid. The Grasshopper is a poor economic choice on both tested duties. Freight brake-van restrictions are valid formation rules, not bugs |
| Which Phase 2 proposals survive operation? | None of the five later Polish duplicate adjustments receives new operational validation here. Their original evidence remains; their final targets stay pending |
| Minimum work before three players? | A shared 1830–1840 opening/reinvestment trial, one contested coastal market, supported maritime-freight/mail fixtures, and a short starter guide covering loan repayment and brake vans. Then extend the same companies to 1850 |

## Prioritized action plan

| Priority / severity | Action | Evidence and confidence |
| --- | --- | --- |
| 1 / Major readiness gap | Run the three-player trial before declaring the campaign balanced, including an optimized horse local/feeder start | Automated single-company income cannot prove market sharing, CargoDist competition or enjoyment. Horses show weak growth while rail is already affordable; the transition used mostly starting reserves. High confidence in these observations |
| 2 / Major localized economic concern | Keep Grasshopper economics under targeted review; test additional appropriate light duties/consists before choosing a correction | Lower purchase cost failed to offset running cost on identical coal duty; timber also lost more than Planet. High confidence for these two duties, moderate for a roster-wide conclusion |
| 3 / Major gameplay risk, not a confirmed defect | Test whether easy coastal passenger growth overwhelms other starting strategies under competition | Ten-year brig mean net cash about £6,309/year, short capital payback, versus thin horse margins. Geographic/catchment/hauling differences are material. High for this route, moderate for generality |
| 4 / Minor onboarding issue | Document repayment of idle borrowing and ordinary cash management | The same coal service changes sign when interest falls from £2,000 to £600/year. No setting change needed. High |
| 5 / Minor onboarding issue | Provide supported early freight recipes with brake vans and practical train lengths | Twelve/twenty-four wagons failed start without brake van and ran with it. Twelve outperformed twenty-four on the tested alignment. High |
| 6 / Major validation gap | Complete a real bulk maritime/feeder chain and legal coastal mail catchment | No immediately legal untouched-coast coal-consumer dock in the screen; Koper automated mail siting failed. Neither is proof a cargo/ship is broken. High on the bounded results |
| 7 / Optional | Test later duplicate candidates in future-year loaded operation | Phase 2 evidence retained, no Phase 3 implementation or operational endorsement. High |
| 8 / Optional | Add replacement, reinvestment and more efficient human route layouts to follow-up tests | Ageing and poor alignments affect cash flow; unchanged fleets and bounded builders do not represent optimal play. High |

**Critical:** no confirmed defect prevents starting the intended campaign. Readiness gaps are not automatically game bugs. **Major:** local choice traps and unresolved competitive balance deserve testing. **Minor:** company management and formation rules need clear examples. **Optional:** later-era and optimization work can follow an acceptable early multiplayer trial.

## Minimum economic intervention

Implement **no price, performance, date, roster, NewGRF, AXIS or multiplayer-setting changes yet**. Preserve the seven-tile limit and infrastructure maintenance. The smallest justified next step is operational validation and a starter guide, not a global cost slider.

Existing NARS/other set multipliers are broad. They would also affect vehicles not implicated by these duties and cannot fix route geography, debt management, catchments or train-formation rules. If later tests justify a residual per-vehicle economic correction, use a proven economic-property/callback edit or verified compatibility mechanism, with the Phase 2 implementation restrictions. An arbitrary cross-GRF override has not been proved here.

The [main report](TRANSPORT_ECONOMY_PHASE3.md) contains all measured totals, clock/accounting qualifications and reproducibility steps. The [test matrix](TRANSPORT_ECONOMY_TEST_MATRIX.md) gives the exact remaining observations and smallest manual procedures. [Company growth](research/company_growth_simulations.csv) separates observed operating cash from calculated borrowing headroom. No simulated payment estimate is presented as delivered revenue.
'''
    (D/'TRANSPORT_ECONOMY_FINDINGS.md').write_text(findings,encoding='utf8')
    print(f'Wrote three reports: {len(results)} route-years, {len(summaries)} configurations, {len(exp)} expansion years')
if __name__=='__main__':main()
