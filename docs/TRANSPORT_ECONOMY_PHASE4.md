# Transport economy Phase 4

**Verdict: READY WITH CAVEATS.** Existing stock supports viable opening businesses. Shipping is the easiest tested growth strategy, rail is viable, and horses have a limited local/feeder and mixed-company role. There is no evidence requiring an automatic price, NewGRF or scenario correction before launch. Competition and physical terminal access materially affect results. The first human session must check those effects and the remaining postal/navigation cases.

## Evidence and scope

This phase reused the 172 Phase 3 route-years and 15 growth-years without regenerating them. It added targeted vehicle/service comparisons and actual multiple-company worlds. Every gameplay test used JGRPP 0.73.4 and the same disposable Europe scenario copy, all fifteen GRF identities/parameters, infrastructure maintenance enabled and maximum train length seven. Only the disposable copy's measurement GS differs from the campaign. No original scenario, save, executable, GRF or normal configuration changed. No balancing change, extra stock, push or merge occurred.

The three-company experiment creates three ordinary AI-controlled companies in one world, each with **£100,000 cash, £100,000 loan, £300,000 maximum loan**, maintenance on and length seven. A measurement GS constructs/operates predeclared services through ordinary company commands. There are no grants or artificial subsidies. This is **VERIFIED IN GAME**, not a spreadsheet profit forecast. It tests the shared economic engine, not network latency, human skill or enjoyment.

The cash-only control ran twenty finance-years. A matched repeat changes only the year-ten normal-credit decision; its frozen pre-intervention harness/financial history is retained. The main CSV identifies both worlds. Do not concatenate them as one continuous company history. The policy comparison was necessary because the original road company's £15,801 missed a scripted £16,000 one-shot expansion guard by £199.

## Method validation

- Actual annual finance categories determine revenue, running, Property, interest, Other and construction/vehicle capital. Quarterly graphs omit the **£300/year Other** company charge; it is included here. Vehicle profit is not company profit.
- Phase 4 construction capital uses actual construction/new-vehicle ledger deltas. This avoids both dry-run GSAccounting totals and accidentally classifying elapsed monthly overhead as construction expenditure.
- Company valuation is the live engine calculation. Its floor of £1 does **not** establish bankruptcy. Cash and valuation are separate columns.
- Financial year 1800 starts at calendar 1830-01-01. The saved clock offset is 10,957 days. CSVs retain exact mapped bounds; twenty economy-years end in late 1849. Engine design dates use calendar time and must **not** receive that offset.
- Fleet-wide samples record load/capacity, loaded time, stopped-at-station time and breakdown state. Ratios are **ENGINE-CALCULATED** from observations. They are samples, not exact timetables. The sampled load factor includes empty return journeys. A full one-way freight service can therefore average around 50% without excess capacity.
- Paid delivery requires observed cargo aboard, positive delivered counters and credited revenue. Entire-horizon services with no confirmed loaded paid delivery are marked **BLOCKED**, even though their actual expenses are preserved. A long-route opening year with no revenue is retained if later deliveries succeed.
- Automatic game awards, if any, remain in revenue under the unchanged campaign subsidy policy; award events were not separately instrumented. No artificial subsidy was granted by the harness.
- Exact departure frequency and cargo-age-specific decay were not isolated. Fleet size/speed, monthly positions, station time and actual delivery rates are observed proxies; record timed round trips in the human check.
- No multi-seed confidence interval or equalized geographic opportunity is claimed. The core strategies use different markets. Shared-corridor mirrors test placement order, including its effect on selected sites, catchments and paid distance; they do not isolate a time-only advantage.

Data: [horses](research/horse_transport_tests.csv), [maritime](research/maritime_profitability_tests.csv), [three-company worlds](research/three_company_simulation.csv), [competition](research/competition_tests.csv), [route geometry/capital](research/transport_phase4_routes.csv), [station samples](research/transport_phase4_station_samples.csv), [raw evidence](research/transport_phase4_runtime_evidence.log).

## Horses: useful, but not an attractive universal starting mode

| Retained test tag | Years | Initial capital | Mean revenue/year | Mean operating profit/year | Mean sampled load factor | Observed payback year |
| --- | --- | --- | --- | --- | --- | --- |
| road-access-horse_straight_pass | 3 | £1,909 | £704 | £-157 | 94% | NOT REACHED |
| road-access-horse_straight_mail | 3 | £1,909 | £911 | £16 | 84% | NOT REACHED |
| road-access-horse_local_fast | 3 | £3,467 | £504 | £-866 | 73% | NOT REACHED |
| road-access-cheap | 3 | £1,909 | £106 | £-747 | 63% | NOT REACHED |
| final-horse_regional | 5 | £4,735 | £274 | £-722 | 16% | NOT REACHED |
| road-access-horse_farm_small | 3 | £5,453 | £477 | £-538 | 46% | NOT REACHED |
| road-access-horse_farm_fleet | 3 | £8,897 | £1,951 | £447 | 49% | NOT REACHED |
| final-horse_fruit | 5 | £8,261 | £868 | £-350 | 47% | NOT REACHED |
| coal-matched-control | 3 | £10,654 | £1,584 | £-189 | 47% | NOT REACHED |

These are observed financial series; `NOT REACHED` means no recovery within the actual horizon. The short street cases use two vehicles and a four-tile station separation. Their post office/bus stops lie on a continuous existing street. Earlier detouring fixtures and failed urban-depot attempts remain in the datasets as different layouts, not proof that all local horse transport fails.

The straight passenger case averaged about **£704 revenue and -£157 operating profit/year**, despite roughly **94%** sampled load factor. The straight mail case averaged about **£911 revenue and +£16/year**, with roughly **84%** load factor. Good loading alone does not overcome low short-trip payments and fixed company costs. Faster four-horse carriages on a different urban alignment did not justify their greater running cost; this is not a reason to buy faster horses indiscriminately.

Normal debt management changes the margin. Reducing unused borrowing from £20,000 to £10,000 saves **£200/year** at 2%. Holding the observed service unchanged, that gives approximately **+£43/year passenger** and **+£216/year mail**. These are **ENGINE-CALCULATED conditional interest substitutions**, not observed alternative-policy profit runs. Remaining liquidity and service demand must still be checked.

The farm-to-mill experiment isolates fleet scale more usefully: two one-horse grain carriages lose money, while eight on the same chain make several hundred pounds/year. The fuller fleet amortizes company and infrastructure costs. Loaded/empty patterns and waiting queues show that the producer is not simply absent or devoid of demand. Slow turnover, cargo payment per trip and overhead matter. A small fruit-to-cannery route was not profitable under the tested icebox-carriage configuration.

**Niche conclusion:** small postal/local services and low-capital feeders can contribute to a larger company that already pays its company overhead. A standalone horse enterprise is fragile, and a horse-first stage is not financially compulsory: the starting cash already affords rail. Do not lock Toni, Squirrel or Kladdey into road-only play. No horse buff is supported by this evidence alone. Same-street short-distance rail profitability was not measured; cheaper road entry and the absence of a new right-of-way are verified advantages, not a fabricated rail profit comparison.

## Shipping: high returns are real, but not universal

| Test tag | Years | Initial capital | Mean revenue/year | Mean operating profit/year | Mean sampled load factor | Observed payback year |
| --- | --- | --- | --- | --- | --- | --- |
| three-final | 20 | £4,917 | £7,912 | £6,555 | 97% | 1 |
| final-ship_medium | 5 | £4,917 | £2,558 | £1,194 | 47% | 5 |
| final-ship_low_demand | 5 | £8,916 | £2,873 | £821 | 18% | NOT REACHED |
| fish-fixed | 5 | £4,625 | £4,029 | £2,739 | 48% | 2 |
| final-ship_fleet | 5 | £12,533 | £10,316 | £7,629 | 43% | 3 |

The twenty-year core brig earns about £6,555/year operating profit under its current sites, consistent in scale with the prior ten-year £6,309 net-cash observation. The definitions/horizons differ slightly; they are not asserted to be identical measurements.

Three brigs sharing one company's corridor produce only a modest total-profit increase over one brig, with roughly 43% sampled fleet load factor instead of the single core brig's approximately 97%. Three purchases do not triple the market. The longer, low-demand Pula–Zadar barque has roughly 18% load factor, substantial opening losses, and no observed capital recovery within five years. It eventually earns real revenue. That is a valid long-route result, not a zero-income placeholder or a steady-state projection from its best year.

The medium Koper–Pula route and the Fishing Grounds 1289 → Fishing Harbor 1303 FISH service both produced actual loaded paid deliveries. The fish service closes the maritime-industrial-freight uncertainty for that chain. Its source uses the existing industry dock; no industry was created or modified.

**Payment/decay interpretation:** revenue per delivered unit and actual utilization are recorded. Longer distance can increase gross payment per passenger while sparse loads, long cycles and running costs reduce annual profit. These tests do not separately estimate a cargo-age decay curve holding every other variable fixed. No static payment estimate is presented as delivery income.

**Postal/navigation boundary:** Venice-origin passenger/mail fixtures built and started but did not establish paid deliveries in the observation period. A Marseille–Toulon MAIL fixture could not find a legal accepting destination dock within the unchanged catchment/site rules. These are **BLOCKED service validations**, not evidence that mail refits or shipping economics are broken. Local road MAIL paid successfully. A practical coastal postal fixture remains a limited human check: inspect catchments and navigable docking tiles, then test supported station extension or a separately costed feeder.

## The 1830–1832 opening

Planet and Grasshopper are both purchasable at the actual initial state, with calendar design date **1830-01-01**. There are **no two railway-free years** in this scenario. Live [opening queries](research/transport_phase4_opening.csv) preserve the company-specific checks; the [Phase 3 opening catalogue](research/transport_available_1830.csv) supplies the rest without another roster audit.

Immediate options include the available sailing ships, eGRVTS passenger/mail/freight horse vehicles and early locomotives with compatible wagons. Verified starting investments range from approximately **£1,909** for the tested two-vehicle straight-street services, through **£8,882** for eight farm carriages, to **£16,283** for the twelve-wagon coal railway. All fit the actual £100,000 starting cash. The wharf/brig core costs £4,917. The higher loan ceiling remains ordinary expansion credit, not free equity.

Tested opportunities cover inland grain and coal, northern fishing grounds, Adriatic passengers and longer coastal services. Not every site works. A valuable first terminal is an advantage, but the evidence does not show that securing one corridor removes all worthwhile opportunities elsewhere. Region and site quality must not be confused with intrinsic mode superiority or player skill.

## Three-company development

| Strategy | Cash near 1850 | Loan | Company value | Cumulative operating profit |
| --- | --- | --- | --- | --- |
| A: maritime | £146,142 | £20,000 | £131,524 | £131,061 |
| B: railway | £86,125 | £30,000 | £66,590 | £72,411 |
| C: road then mixed | £92,167 | £30,000 | £78,686 | £85,981 |

| Strategy | Mean profit/year, opening five years | Mean profit/year, next five years | Mean profit/year, final ten years |
| --- | --- | --- | --- |
| A: maritime | £6,229 | £6,702 | £6,640 |
| B: railway | £3,712 | £3,950 | £3,410 |
| C: road then mixed | £444 | £477 | £8,138 |

| Run / company | Observed years | Cash | Loan | Company value | Cumulative operating profit | Capital invested |
| --- | --- | --- | --- | --- | --- | --- |
| cash-only control / 0 | 5 | £46,226 | £20,000 | £33,683 | £31,146 | £4,917 |
| cash-only control / 1 | 5 | £32,274 | £30,000 | £16,692 | £18,559 | £16,283 |
| cash-only control / 2 | 5 | £13,338 | £20,000 | £2,114 | £2,221 | £8,882 |
| cash-only control / 0 | 10 | £79,738 | £20,000 | £65,855 | £64,658 | £4,917 |
| cash-only control / 1 | 10 | £52,022 | £30,000 | £33,915 | £38,308 | £16,283 |
| cash-only control / 2 | 10 | £15,801 | £20,000 | £3,857 | £4,604 | £8,882 |
| cash-only control / 0 | 20 | £146,176 | £20,000 | £131,558 | £131,095 | £4,917 |
| cash-only control / 1 | 20 | £88,379 | £30,000 | £68,844 | £74,667 | £16,283 |
| cash-only control / 2 | 20 | £20,498 | £20,000 | £8,554 | £9,382 | £8,882 |
| ordinary-credit mixed run / 0 | 5 | £46,226 | £20,000 | £33,683 | £31,146 | £4,917 |
| ordinary-credit mixed run / 1 | 5 | £32,274 | £30,000 | £16,692 | £18,559 | £16,283 |
| ordinary-credit mixed run / 2 | 5 | £13,338 | £20,000 | £2,114 | £2,221 | £8,882 |
| ordinary-credit mixed run / 0 | 10 | £79,738 | £20,000 | £65,855 | £64,658 | £4,917 |
| ordinary-credit mixed run / 1 | 10 | £52,022 | £30,000 | £33,915 | £38,308 | £16,283 |
| ordinary-credit mixed run / 2 | 10 | £15,801 | £20,000 | £3,857 | £4,604 | £8,882 |
| ordinary-credit mixed run / 0 | 20 | £146,142 | £20,000 | £131,524 | £131,061 | £4,917 |
| ordinary-credit mixed run / 1 | 20 | £86,125 | £30,000 | £66,590 | £72,411 | £16,283 |
| ordinary-credit mixed run / 2 | 20 | £92,167 | £30,000 | £78,686 | £85,981 | £23,812 |

The primary mixed-policy run permits a normal £10,000 additional loan at year ten if needed. The cash-only control deliberately does not. Both retain identical settings and existing vehicles. The matched repeat reuses the frozen control harness; pre-intervention company-year ledgers are checked for identity. Credit is repaid/borrowed through ordinary company actions, never a grant.

The cash-only road company finishes with positive cash but grows far more slowly. Its missed one-shot cash guard was a controller policy, not an engine restriction. The prior Phase 3 horse-to-rail experiment remains additional real evidence, with its qualification that most capital came from unused starting borrowing. Company investment growth must distinguish accumulated earnings, borrowed cash and the value of owned assets.

The mixed company's final-decade earnings exceed its opening road-only earnings substantially. This is a real ordinary-credit expansion, not a cash grant. The old horse route continues to receive credited road revenue; road revenue minus direct road running expense is a contribution before shared Property/finance, not a separately allocated net profit. Different cargo markets and sites remain part of the explanation, so the outcome is not an intrinsic ranking of vehicle modes.

The main fleets age normally; sampled breakdown exposure and actual running expenses enter the recorded profits. No optimal replacement policy is claimed. A/B are held to their configured initial services; humans may expand them. For a mixed company, delivered passenger and grain totals are engine aggregates of unlike units, not tonnage, and aggregate load factors/revenue per unit are suppressed.

## Competition, terminal access and first movers

| Market test / company | Years | Mean annual revenue | Mean annual operating profit | Total paid units |
| --- | --- | --- | --- | --- |
| final-shared_coast_navigable / 0 | 5 | £6,469 | £5,097 | 2529 |
| final-shared_coast_navigable / 1 | 5 | £2,313 | £963 | 1554 |
| final-shared_coast_navigable_reverse / 0 | 5 | £2,313 | £963 | 1554 |
| final-shared_coast_navigable_reverse / 1 | 5 | £6,469 | £5,097 | 2529 |
| final-shared_coal / 0 | 5 | £1,568 | £-217 | 712 |
| final-shared_coal / 1 | 5 | £1,449 | £-18 | 690 |
| final-shared_coal / 2 | 5 | £0 | £-1,302 | 0 |

With clear approaches, both competing ship companies earn money. Reversing construction order transfers the preferred-site result to the other company ID: roughly **£5,097/year versus £963/year** over five years. This is a real placement/site advantage, not proof of an AI identity advantage or a permanent timestamp-based monopoly. Sites also differ in catchment and credited distance. A full two-year delayed-entry experiment was not run; the first-session protocol specifies it.

At the coal producer, two functioning services collected and delivered cargo. The third commissioned fixture never loaded; its unproductive state is not evidence that ratings alone starved it. It requires approach/depot inspection. The isolated one-horse/eight-carriage control uses the same cargo/vehicle family and endpoints; realized layout costs and global-world history are retained, so differences are not treated as an exact one-variable causal estimate.

Early naive port layouts demonstrated a more direct risk: a later legal dock can occupy an earlier ship depot's exit approach. The earlier boat then records no loaded service. Clear-approach siting restores operation. The affected pilot rows are retained and explicitly excluded from clean demand-sharing interpretation. This warrants a **no deliberate access-blocking agreement and visual approach check**, not a locomotive price change.

JGRPP `station_cmd.cpp::MoveGoodsToStation` allocates cargo using company-best and station ratings, rather than a simple permanent first-owner bonus. Multiple stations owned by one company do not automatically create extra company share. CargoDist, catchments, frequency and terminal geometry still matter. Exclusive town rights are enabled in the saved settings but were not purchased in these experiments; their use and current buy-window cost should be agreed/checked by the players. No unverified price or claim of immunity to monopoly tactics is supplied.

## Seven tiles and post-launch work

Keep seven tiles. The twelve-wagon/brake-van train is **2.75 tiles** and the twenty-four-wagon/brake-van train **5.0 tiles**; both fit, yet the shorter configuration earns more on the tested line. Power, alignment, load and formation rules explain more of this early choice than the length ceiling. No opening-period benefit from increasing the limit is demonstrated. Modern long freight/MU constraints can be reviewed later with loaded duties; they are not a reason to change the intentional baseline now.

GETS's earliest powered introduction in the retained roster is **1881**, outside this launch window. The Class 66 zero-speed result came from a short orderless Phase 2 track, not a demonstrated failure on an ordered loaded route. Other GETS train tests recorded positive movement. The exact Class 66 cause remains **MANUAL TEST REQUIRED**, post-launch. ST43/ET21/EN57/EN71/ED72 remain narrow later-era validation tasks; their Phase 2 targets were not implemented or operationally endorsed here. See [post-launch evidence](research/transport_phase4_postlaunch.json).

## Reproduction, validation and limits

Use the bundled Python environment, or an equivalent environment with NumPy for the retained scenario reader. The existing local Phase 2 asset copies and verified configuration template are prerequisites; assets are not included in the repository. If `python` points to another installation, use `C:\Users\Kladd\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` explicitly.

```powershell
python scripts/transport_phase4.py horse_straight_mail --tag new-mail-repeat --years 3
python scripts/transport_phase4.py shared_coast_navigable --tag new-market-repeat
python scripts/analyze_transport_phase4.py
python scripts/write_transport_phase4_reports.py
python scripts/validate_transport_phase4.py
python -m unittest discover -s tests -p "test_transport_phase4.py"
```

Use a fresh tag; existing directories are not overwritten. [Run configurations](research/transport_phase4_run_configs.json), [frozen harness sources](research/transport_phase4_harness_sources.json), [attempts and precise blockers](research/transport_phase4_attempts.csv), and [preservation/accounting validation](research/transport_phase4_validation.json) make the distinction between observations and calculations reviewable. The credit comparison deliberately derives from the retained frozen control harness, not later layout revisions. Runtime assets remain local/ignored; no GRF assets are redistributed.

The remaining tests are bounded human checks, not grounds for another full audit. See [readiness and the first-session protocol](MULTIPLAYER_ECONOMY_READINESS.md) and [the prioritized action plan](FINAL_ECONOMY_ACTION_PLAN.md). All modelled/conditional statements are identified; no hypothetical future revenue is inserted into the measured company ledgers.

Validation: ten new Phase 4 evidence/accounting tests and the twenty existing Phase 2/3 economy tests pass. Preservation checks cover all fifteen GRF identities, 83 original asset instances and 75 prior research files. The matched runs have thirty identical pre-intervention company-year pairs. The broader geography suite is outside this phase and its previously identified SciPy dependency was not installed or changed.
