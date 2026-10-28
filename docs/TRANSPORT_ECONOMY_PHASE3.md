# Transport economy Phase 3

The 1830 economy can support profitable shipping and passenger railways. Horses have a much narrower margin: an eight-carriage coal company retained enough cash to add a railway after ten years, mainly from its unspent starting reserve, but several passenger/mail strategies lost money. **A complete three-player campaign has not been validated, and a robust economic niche for horses is not yet established.** These are operational observations on disposable copies of the actual Europe scenario, not forecasts derived from cargo-payment tables.

There are **172 route-year observations across 24 operating configurations**, plus **15 observed company-years in the horse-to-rail expansion**. Two unchanged fleets ran for twenty economy-years. Actual paid deliveries cover PASS, MAIL, COAL, GRAI and WOOD. Failed fixtures and exploratory harness errors remain in the [attempt register](research/transport_test_attempts.csv), outside successful financial comparisons.

## Environment and preservation

- Branch: `audit/local-vehicle-economy`. Nothing pushed or merged. Phase 1/2 research remains byte-identical to the input manifest.
- Executable: `C:\Users\Kladd\Downloads\OpenTTD\openttd.exe`, JGRPP **0.73.4**, original binary. Local runtime copies/hardlinks of already-installed assets; no additional rolling stock.
- Source: `C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1800 V2 newGRFS.scn`, SHA-256 `5710beea8b3badf6aecc8ab679caea1fb2c4b66e96c4393b342a816c064e0688`, 4096×4096, calendar 1830-01-01.
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

| Test / retained tag | Years | Initial infrastructure + fleet | Mean revenue/year | Mean net cash/year | Observed capital payback |
| --- | --- | --- | --- | --- | --- |
| ship-pax-final | 10 | £4,917 | £7,681 | £6,309 | 1 |
| ship-barque | 5 | £8,916 | £11,948 | £10,029 | 2 |
| ship-schooner | 5 | £6,821 | £9,581 | £8,262 | 2 |
| rail-lodi | 10 | £14,420 | £5,656 | £3,793 | 4 |
| horse-lodi | 5 | £7,409 | £1,556 | £29 | NOT REACHED |
| horse-existing-road | 10 | £6,867 | £1,688 | £188 | NOT REACHED |
| horse-london | 5 | £4,714 | £1,507 | £84 | NOT REACHED |
| horse-city-road | 5 | £6,092 | £1,405 | £-90 | NOT REACHED |
| horse-coal-final | 10 | £6,867 | £340 | £-738 | NOT REACHED |
| horse-coal-fleet4 | 10 | £12,607 | £2,732 | £254 | NOT REACHED |
| rail-coal-ledger | 20 | £12,349 | £2,387 | £421 | NOT REACHED |
| rail-coal-12-brake | 5 | £16,283 | £5,320 | £3,347 | 5 |
| rail-coal-24-brake | 5 | £21,091 | £3,416 | £955 | NOT REACHED |
| rail-coal-keep | 2 | £12,349 | £2,208 | £-821 | NOT REACHED |
| rail-coast | 5 | £17,764 | £1,680 | £-145 | NOT REACHED |
| horse-coast | 5 | £19,798 | £784 | £-1,609 | NOT REACHED |
| rail-general2 | 5 | £11,644 | £2,822 | £1,203 | NOT REACHED |
| rail-wood-final | 5 | £29,853 | £1,096 | £-944 | NOT REACHED |
| rail-grasshopper | 5 | £10,005 | £1,822 | £-2,410 | NOT REACHED |
| rail-wood-grasshopper | 5 | £27,509 | £773 | £-3,866 | NOT REACHED |
| horse-mail | 5 | £11,196 | £602 | £-1,280 | NOT REACHED |

Full fields: [route results](research/transport_route_results.csv), [mode comparison](research/transport_mode_comparison.csv), [company growth](research/company_growth_simulations.csv). Raw evidence is [retained as text](research/transport_runtime_evidence.log), without redistributing GRF assets.

## Comparable coastal task

These services connect the same Koper and Trieste towns. They use different legal station sites, catchments, gradients and paths; this is a comparable task, not a pure causal estimate of mode alone. To remove unequal horizons and construction-year effects, this table uses the same four complete finance-years, approximately **1831–1834**.

| Koper–Trieste mode/configuration | Mean revenue, 1831–1834 | Mean net cash, 1831–1834 | Mean delivered units/year |
| --- | --- | --- | --- |
| ship-pax-final | £8,003 | £6,610 | 625.0 |
| ship-barque | £13,044 | £11,087 | 1018.75 |
| ship-schooner | £9,975 | £8,626 | 773.75 |
| rail-coast | £1,556 | £-297 | 120.0 |
| horse-coast | £929 | £-1,482 | 68.0 |

Shipping's advantage in these fixtures is operationally real. The land services showed low loaded-speed samples and weak delivery rates. Siting, catchments, path geometry, grades and consist effects were not isolated, so the deficit cannot be attributed to terrain alone. Shipping cannot directly replace inland Lodi–Crema or a mine away from navigable water. No unlimited profit exploit is established; competitive demand limits remain unmeasured. A three-company market test remains necessary.

## Freight scalability and handling rules

Planet four-wagon coal service is viable but slow to recover its investment. The twelve-wagon service **with the existing 10t Brake Van** materially improves throughput and cash earnings. The twenty-four-wagon service fits the limit but performs worse on this alignment: loaded monthly samples include 2 km/h. Greater capacity does not guarantee greater profit.

Without the brake van, both twelve- and twenty-four-wagon builds succeeded but start failed with `ERR_NEWGRF_SUPPLIED_ERROR`. Adding only the existing UKRS2 brake van allowed operation. The GRF contains a brake-van requirement string. The exact returned localized string ID was not decoded, so the diagnosis rests on the controlled start/fail comparison plus that definition. This is a supported train-formation rule, not evidence of an engine or scenario bug. Original blocked runs remain visible.

Timber from forest 869 to sawmill 369 produced, loaded, delivered and paid, but both tested locomotives lost money on the route. Loaded slow-running samples support a hauling/alignment problem; the evidence does not justify calling the WOOD cargo chain broken. Grain from farm 260 to flour mill 286 was profitable. No assumption was made that every wagon accepts every AXIS cargo.

## Longitudinal and company growth

| Strategy | Observed years | Cash | Loan | Cumulative operating cash profit | Capital invested so far |
| --- | --- | --- | --- | --- | --- |
| ship-pax-final | 5 | £46,649 | £20,000 | £31,566 | £4,917 |
| ship-pax-final | 10 | £78,171 | £20,000 | £63,088 | £4,917 |
| rail-lodi | 5 | £36,662 | £30,000 | £21,082 | £14,420 |
| rail-lodi | 10 | £53,509 | £30,000 | £37,929 | £14,420 |
| rail-coal-ledger | 5 | £21,182 | £30,000 | £3,531 | £12,349 |
| rail-coal-ledger | 10 | £23,520 | £30,000 | £5,869 | £12,349 |
| rail-coal-ledger | 15 | £25,121 | £30,000 | £7,470 | £12,349 |
| rail-coal-ledger | 20 | £26,064 | £30,000 | £8,413 | £12,349 |
| horse-coal-fleet4 | 5 | £18,557 | £30,000 | £1,164 | £12,607 |
| horse-coal-fleet4 | 10 | £19,935 | £30,000 | £2,542 | £12,607 |
| horse-transition | 5 | £18,129 | £30,000 | £736 | £12,607 |
| horse-transition | 10 | £19,355 | £30,000 | £1,962 | £12,607 |
| horse-transition | 15 | £20,510 | £30,000 | £17,646 | £27,136 |

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
