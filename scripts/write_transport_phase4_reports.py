"""Write the launch decision from retained observations, with explicit limitations."""
import csv,collections,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs';R=D/'research'
def rows(name):
    with (R/name).open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))
def money(n):return f"£{float(n):,.0f}"
def table(headers,data):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(str(x) for x in r)+' |' for r in data])
def groups(data):
    out=collections.defaultdict(list)
    for r in data:
        if r.get('economy_year') and r.get('service_commissioned')=='True':out[(r['tag'],r['company_id'])].append(r)
    return out
def stats(rr):
    cap=int(rr[0]['infrastructure_initial_gbp'])+int(rr[0]['fleet_initial_gbp'])
    return [len(rr),money(cap),money(sum(int(r['annual_revenue_gbp']) for r in rr)/len(rr)),money(sum(int(r['annual_operating_profit_gbp']) for r in rr)/len(rr)),f"{sum(float(r['sampled_load_factor'] or 0) for r in rr)/len(rr):.0%}",rr[-1]['observed_capital_recovery_year']]
def main():
    horses=groups(rows('horse_transport_tests.csv'));ships=groups(rows('maritime_profitability_tests.csv'));market=groups(rows('competition_tests.csv'));company=rows('three_company_simulation.csv')
    credit=[r for r in company if r['tag']=='three-credit-matched'];primary='three-credit-matched' if len(credit)==60 else 'three-final'
    htags=['road-access-horse_straight_pass','road-access-horse_straight_mail','road-access-horse_local_fast','road-access-cheap','final-horse_regional','road-access-horse_farm_small','road-access-horse_farm_fleet','final-horse_fruit','coal-matched-control']
    htable=table(['Retained test tag','Years','Initial capital','Mean revenue/year','Mean operating profit/year','Mean sampled load factor','Observed payback year'],[[t,*stats(horses[(t,'0')])] for t in htags if (t,'0') in horses])
    stags=[('three-final','0'),('final-ship_medium','0'),('final-ship_low_demand','0'),('fish-fixed','0'),('final-ship_fleet','0')]
    stable=table(['Test tag','Years','Initial capital','Mean revenue/year','Mean operating profit/year','Mean sampled load factor','Observed payback year'],[[t,*stats(ships[(t,c)])] for t,c in stags if (t,c) in ships])
    milestones=table(['Run / company','Observed years','Cash','Loan','Company value','Cumulative operating profit','Capital invested'],[[('ordinary-credit mixed run' if tag==primary else 'cash-only control')+' / '+str(c),n,money(r['cash_gbp']),money(r['loan_gbp']),money(r['company_value_gbp']),money(r['cumulative_operating_profit_gbp']),money(r['capital_invested_to_date_gbp'])] for tag in ['three-final',primary] for n in [5,10,20] for c in range(3) for r in company if r['tag']==tag and int(r['company_id'])==c and int(r['economy_year'])==1799+n])
    markets=table(['Market test / company','Years','Mean annual revenue','Mean annual operating profit','Total paid units'],[[t+' / '+str(c),len(market[(t,str(c))]),money(sum(int(r['annual_revenue_gbp']) for r in market[(t,str(c))])/len(market[(t,str(c))])),money(sum(int(r['annual_operating_profit_gbp']) for r in market[(t,str(c))])/len(market[(t,str(c))])),sum(int(r['delivered_units']) for r in market[(t,str(c))])] for t in ['final-shared_coast_navigable','final-shared_coast_navigable_reverse','final-shared_coal'] for c in range(3) if (t,str(c)) in market])
    endings=[r for r in company if r['tag']==primary and r['economy_year']=='1819']
    period_profit=table(['Strategy','Mean profit/year, opening five years','Mean profit/year, next five years','Mean profit/year, final ten years'],[[['A: maritime','B: railway','C: road then mixed'][c],*[money(sum(int(r['annual_operating_profit_gbp']) for r in company if r['tag']==primary and int(r['company_id'])==c and lo<=int(r['economy_year'])<hi)/(hi-lo)) for lo,hi in [(1800,1805),(1805,1810),(1810,1820)]]] for c in range(3)])
    ending=table(['Strategy','Cash near 1850','Loan','Company value','Cumulative operating profit'],[[['A: maritime','B: railway','C: road then mixed'][int(r['company_id'])],money(r['cash_gbp']),money(r['loan_gbp']),money(r['company_value_gbp']),money(r['cumulative_operating_profit_gbp'])] for r in endings])
    report=f'''# Transport economy Phase 4

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

{htable}

These are observed financial series; `NOT REACHED` means no recovery within the actual horizon. The short street cases use two vehicles and a four-tile station separation. Their post office/bus stops lie on a continuous existing street. Earlier detouring fixtures and failed urban-depot attempts remain in the datasets as different layouts, not proof that all local horse transport fails.

The straight passenger case averaged about **£704 revenue and -£157 operating profit/year**, despite roughly **94%** sampled load factor. The straight mail case averaged about **£911 revenue and +£16/year**, with roughly **84%** load factor. Good loading alone does not overcome low short-trip payments and fixed company costs. Faster four-horse carriages on a different urban alignment did not justify their greater running cost; this is not a reason to buy faster horses indiscriminately.

Normal debt management changes the margin. Reducing unused borrowing from £20,000 to £10,000 saves **£200/year** at 2%. Holding the observed service unchanged, that gives approximately **+£43/year passenger** and **+£216/year mail**. These are **ENGINE-CALCULATED conditional interest substitutions**, not observed alternative-policy profit runs. Remaining liquidity and service demand must still be checked.

The farm-to-mill experiment isolates fleet scale more usefully: two one-horse grain carriages lose money, while eight on the same chain make several hundred pounds/year. The fuller fleet amortizes company and infrastructure costs. Loaded/empty patterns and waiting queues show that the producer is not simply absent or devoid of demand. Slow turnover, cargo payment per trip and overhead matter. A small fruit-to-cannery route was not profitable under the tested icebox-carriage configuration.

**Niche conclusion:** small postal/local services and low-capital feeders can contribute to a larger company that already pays its company overhead. A standalone horse enterprise is fragile, and a horse-first stage is not financially compulsory: the starting cash already affords rail. Do not lock Toni, Squirrel or Kladdey into road-only play. No horse buff is supported by this evidence alone. Same-street short-distance rail profitability was not measured; cheaper road entry and the absence of a new right-of-way are verified advantages, not a fabricated rail profit comparison.

## Shipping: high returns are real, but not universal

{stable}

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

{ending}

{period_profit}

{milestones}

The primary mixed-policy run permits a normal £10,000 additional loan at year ten if needed. The cash-only control deliberately does not. Both retain identical settings and existing vehicles. The matched repeat reuses the frozen control harness; pre-intervention company-year ledgers are checked for identity. Credit is repaid/borrowed through ordinary company actions, never a grant.

The cash-only road company finishes with positive cash but grows far more slowly. Its missed one-shot cash guard was a controller policy, not an engine restriction. The prior Phase 3 horse-to-rail experiment remains additional real evidence, with its qualification that most capital came from unused starting borrowing. Company investment growth must distinguish accumulated earnings, borrowed cash and the value of owned assets.

The mixed company's final-decade earnings exceed its opening road-only earnings substantially. This is a real ordinary-credit expansion, not a cash grant. The old horse route continues to receive credited road revenue; road revenue minus direct road running expense is a contribution before shared Property/finance, not a separately allocated net profit. Different cargo markets and sites remain part of the explanation, so the outcome is not an intrinsic ranking of vehicle modes.

The main fleets age normally; sampled breakdown exposure and actual running expenses enter the recorded profits. No optimal replacement policy is claimed. A/B are held to their configured initial services; humans may expand them. For a mixed company, delivered passenger and grain totals are engine aggregates of unlike units, not tonnage, and aggregate load factors/revenue per unit are suppressed.

## Competition, terminal access and first movers

{markets}

With clear approaches, both competing ship companies earn money. Reversing construction order transfers the preferred-site result to the other company ID: roughly **£5,097/year versus £963/year** over five years. This is a real placement/site advantage, not proof of an AI identity advantage or a permanent timestamp-based monopoly. Sites also differ in catchment and credited distance. A full two-year delayed-entry experiment was not run; the first-session protocol specifies it.

At the coal producer, two functioning services collected and delivered cargo. The third commissioned fixture never loaded; its unproductive state is not evidence that ratings alone starved it. It requires approach/depot inspection. The isolated one-horse/eight-carriage control uses the same cargo/vehicle family and endpoints; realized layout costs and global-world history are retained, so differences are not treated as an exact one-variable causal estimate.

Early naive port layouts demonstrated a more direct risk: a later legal dock can occupy an earlier ship depot's exit approach. The earlier boat then records no loaded service. Clear-approach siting restores operation. The affected pilot rows are retained and explicitly excluded from clean demand-sharing interpretation. This warrants a **no deliberate access-blocking agreement and visual approach check**, not a locomotive price change.

JGRPP `station_cmd.cpp::MoveGoodsToStation` allocates cargo using company-best and station ratings, rather than a simple permanent first-owner bonus. Multiple stations owned by one company do not automatically create extra company share. CargoDist, catchments, frequency and terminal geometry still matter. Exclusive town rights are enabled in the saved settings but were not purchased in these experiments; their use and current buy-window cost should be agreed/checked by the players. No unverified price or claim of immunity to monopoly tactics is supplied.

## Seven tiles and post-launch work

Keep seven tiles. The twelve-wagon/brake-van train is **2.75 tiles** and the twenty-four-wagon/brake-van train **5.0 tiles**; both fit, yet the shorter configuration earns more on the tested line. Power, alignment, load and formation rules explain more of this early choice than the length ceiling. No opening-period benefit from increasing the limit is demonstrated. Modern long freight/MU constraints can be reviewed later with loaded duties; they are not a reason to change the intentional baseline now.

GETS's earliest powered introduction in the retained roster is **1881**, outside this launch window. The Class 66 zero-speed result came from a short orderless Phase 2 track, not a demonstrated failure on an ordered loaded route. Other GETS train tests recorded positive movement. The exact Class 66 cause remains **MANUAL TEST REQUIRED**, post-launch. ST43/ET21/EN57/EN71/ED72 remain narrow later-era validation tasks; their Phase 2 targets were not implemented or operationally endorsed here. See [post-launch evidence](research/transport_phase4_postlaunch.json).

## Reproduction, validation and limits

Use the bundled Python environment, or an equivalent environment with NumPy for the retained scenario reader. The existing local Phase 2 asset copies and verified configuration template are prerequisites; assets are not included in the repository. If `python` points to another installation, use `C:\\Users\\Kladd\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe` explicitly.

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
'''
    (D/'TRANSPORT_ECONOMY_PHASE4.md').write_text(report,encoding='utf8')
    readiness=f'''# Multiplayer economy readiness

## READY WITH CAVEATS

No confirmed critical economic defect prevents a three-player 1830 start. Ships and rail support profitable businesses. Horses support narrower, slower local/feeder work and can remain part of a mixed company. This is a defensible launch decision for a monitored campaign, not a certification of equal returns, every terminal or human competitive enjoyment.

No prices, performance, dates, GRFs, scenario, saves, multiplayer settings or train length were changed. The test companies are controlled profiles, not simulations of Kladdey, Squirrel or Toni's skill. Human network/desync testing was not performed.

## Ten answers

| Question | Decision |
| --- | --- |
| 1. Is the opening viable for three companies? | Yes: ordinary companies operate together with equivalent initial cash/loan conditions. Both locomotives are available on day one, not only in 1832 |
| 2. Can each find worthwhile investments? | Yes, with different margins and geographic opportunities. Do not impose road-only play on one person. Mixed investment and normal loan management are available |
| 3. Are ships excessively profitable? | High profits are verified on the best short coast, but not universally. Fleet saturation, poor loading, long cycles and competing terminals reduce returns. A universal ship nerf is not supported |
| 4. Do horses have a niche? | A limited one: the straight postal service is near break-even, the eight-carriage farm service makes money, and shared company overhead improves incremental roles. Standalone urban passenger growth is weak; optimized human local/feeder play needs monitoring |
| 5. Are early railways reasonably balanced? | Useful and profitable in demonstrated duties, with real formation/power/alignment trade-offs. Grasshopper remains an unattractive choice on the tested duties; no automatic repricing is justified here |
| 6. Does competition change profitability? | Yes. Both navigable competing ferry companies make money, but terminal/site outcomes differ substantially. Shared-producer margins are thin. Isolated-route profits must not be assumed to persist |
| 7. Serious first-mover exploits? | No irreversible financial exploit was established. Preferred terminal sites provide strong advantages, and legal building can obstruct access. Delayed entry and exclusive-rights tactics still need player checks |
| 8. Is seven tiles appropriate? | Retain it. The tested early freight alternatives both fit; the larger train performs worse. No launch evidence supports raising the limit |
| 9. Necessary changes before launch? | No economic/NewGRF/scenario changes. Agree how to avoid deliberate access obstruction, confirm terminal approaches and acknowledge the manual checks below |
| 10. What should humans test first? | Opening availability/prices, one competitive passenger market, one small local/feeder investment, one supported postal wharf, normal borrowing for expansion, then ageing/replacement through 1850 |

## Observed core outcome

{ending}

Read [the full evidence](TRANSPORT_ECONOMY_PHASE4.md) for exact horizons, matched/control differences and capital attribution. Company value is an engine valuation; it is not cash. Operating profit includes running, infrastructure Property, interest and Other expenses. It excludes capital purchases, which are recorded separately.

## Practical first session: Kladdey, Squirrel and Toni

1. **Opening check, 5–10 minutes:** all three inspect the actual campaign's GRF list, GBP display, maintenance and seven-tile setting. Record starting cash/loan. Confirm Planet/Grasshopper availability immediately. Record the chosen sites and commission dates. Do not modify settings to force a railway-free period.
2. **Opening businesses, 1830–1832:** choose or draw benchmark roles for this test, then permit normal diversification. Suggested roles are Kladdey maritime, Squirrel railway, Toni road/mixed; these are optional test assignments, not campaign handicaps. Use available stock only. Road trials should include a short **straight** street and a real farm/industry chain, not a long detour paid as a short journey.
3. **Shared corridor, 1831–1835:** two players run one ship each between the same towns, with separate legal terminals and unobstructed depot exits/docking water. Before starting, the third player checks both water approaches. Record annual income, all expense categories, delivered units, loading, ratings and catchments. Do not infer demand starvation from a trapped vehicle.
4. **Delayed-entry check:** have the later company enter a working market after approximately two economy-years. Record its ordinary capital/loan history and commission date. Compare only common post-entry windows. If the newcomer struggles, inspect access, catchments and frequency before proposing a price change. In a disposable restart, swap which player receives the preferred terminal to separate skill and site quality.
5. **Postal/freight check:** reproduce a paid FISH delivery from an existing fishing industry to an accepting harbor. For mail, inspect actual MAIL production/acceptance and docking water at both ends. If a standalone wharf lacks catchment, use a supported, separately costed combined station or real feeder; record every vehicle and infrastructure cost. Require actual loaded delivery and credited revenue. Venice fixtures remain unresolved and must not be assumed to work.
6. **Expansion, 1835–1840:** allow the mixed player to invest in rail/shipping using normal cash or borrowing. Record loan principal separately from profit. A profitable vehicle may still leave a company losing money after Property/interest/Other. Twelve Open Wagons require the existing brake van in the demonstrated formation. Keep the total train within seven tiles.
7. **Ageing, 1840–1850:** retain the same companies. Record replacements, capital purchases, reliability/breakdown disruption and any lost services. Compare whether each player can continue investing without a special grant. Humans may manage ageing; the automated fixed-fleet controls were not an optimal replacement policy.

At each checkpoint save or export evidence to a **new disposable playtest save**, never overwrite the original scenario or existing saves. Record date, cash, loan, company value, revenue, running, Property, interest, Other, capital, fleet/consists/refits, delivered cargo and interruptions. Record mixed cargo separately rather than summing passengers and tonnes as one throughput measure. Note subsidies, exclusive rights and terminal changes explicitly.

## Stop/review triggers

- **CRITICAL:** any starting company cannot use its legitimate credit/build options, required stock is missing, a repeatable core delivery failure affects otherwise valid services, or multiplayer desync prevents continued play. None was established by this audit.
- **MAJOR:** intentional access blocking, a repeatable rights/station tactic removes realistic competition, or a demonstrated market yields near-unlimited profit despite saturation. Pause the disputed tactic and inspect evidence; do not immediately change all prices.
- **MINOR:** one chosen alignment loses money, a brake van is missing, a vehicle is underloaded, or unused debt incurs avoidable interest. Correct the service/management first.
- **OPTIONAL:** later-era duplicate-price corrections or a modern train-length review. Defer them until they affect the campaign.

After a satisfactory first checkpoint, continue the campaign with monitoring. A particular unprofitable route does not make the whole campaign unready. If the group wants a compulsory profitable horse-only era, that is a different design goal; it is not provided by the current day-one railway availability and generous opening cash.
'''
    (D/'MULTIPLAYER_ECONOMY_READINESS.md').write_text(readiness,encoding='utf8')
    action='''# Final economy action plan

**Recommendation: launch with caveats and a recorded first-session check. Apply no automatic balancing changes.**

| Priority / severity | Problem and evidence | Root cause / recommended action | Expected impact | Confidence / risks | Change required |
| --- | --- | --- | --- | --- | --- |
| P0 / MAJOR conduct risk | A later legal dock can block an existing depot's exit; affected boats never load | Agree no deliberate access obstruction. Inspect docking water and depot exits before building near another terminal; repair only in disposable tests during validation | Preserves meaningful competition without a price adjustment | High for observed interference; generic distance alone does not guarantee access | No game change; player agreement and layout check |
| P0 / MINOR readiness check | Human CargoDist competition, late entry and network operation are not fully certified | Follow the short first-session protocol with Kladdey, Squirrel and Toni; log comparable post-entry windows | Detects actual competitive unfairness and connection problems early | Moderate financial generality; player skill/geography remain confounders | Nothing in NewGRF/scenario/settings |
| P1 / MINOR management issue | Tiny local services are dominated by company overhead and unused-loan interest | Repay genuinely unused debt while retaining a sensible buffer; judge incremental services in the full company account | Avoids misdiagnosing interest/Other as vehicle-price defects | High for measured costs; do not drain working capital blindly | Normal company actions only |
| P1 / MINOR role limitation | Horses have weak standalone passenger growth; eight farm carriages outperform two | Prefer short direct streets, postal/feeder work, appropriate cheap vehicles and enough fleet scale. Permit mixed expansion; do not mandate a road-only player | Retains a useful but limited historical role | High for tested duties, moderate beyond them; more vehicles can congest stops | No buff or price change |
| P1 / MANUAL TEST REQUIRED | Coastal MAIL and Venice navigation have no verified paid service | Check MAIL catchments and navigable docking tiles; test supported station extension or a real costed feeder | Closes the specific remaining coastal-postal gap | High that evidence is missing; not proof of a broken cargo/ship | Disposable layout validation; no campaign edit |
| P1 / MANUAL TEST REQUIRED | Third shared-coal fixture never loaded | Inspect depot/road-stop approaches, then retest the third service. Do not call this ratings-based starvation | Separates geometry from market allocation | High for zero-load observation, unresolved exact failing connection | Disposable test layout only |
| P2 / MINOR selection warning | Grasshopper loses more than Planet on the demonstrated coal/timber duties | Show full-consist operating costs in the starter guide; retain targeted review for an appropriate light duty | Avoids a cheap-purchase trap without flattening historical variety | High locally; lighter engine/other duties not exhausted | No implemented adjustment |
| P2 / MINOR formation requirement | Long UKRS2 freight failed without the brake van and ran with it | Provide a known working twelve-wagon + brake-van recipe; verify loading and grades before lengthening | Makes early rail usable without changing the seven-tile baseline | High; a recipe is not optimal on every alignment | Existing stock configuration only |
| P2 / MINOR policy uncertainty | Exclusive town rights are enabled but were not purchased in these tests | Agree their use before competition; inspect the actual current action cost, duration and effect in a disposable test if contested | Avoids an untested monopoly tactic becoming a dispute | Source mechanism known; no unverified cost is asserted | Player agreement; no setting edit performed |
| P3 / OPTIONAL, post-launch | GETS Class 66 zero movement remains unresolved in a short orderless fixture | At the relevant future date, build a connected ordered route with correct rail/power compatibility; observe bare and loaded trains. Other GETS models moved in Phase 2 | Resolves a specific late vehicle issue | High that it does not affect 1830–1850; exact cause still unknown | Test only; no GRF patch |
| P3 / OPTIONAL, post-launch | ST43/ET21/EN57/EN71/ED72 targets lack loaded-route qualification | Test exact duplicate families with matched consists, duty and dates for at least three full years before choosing corrections | Keeps later proposals evidence-based | Original price/build gaps remain; final targets unapproved | No current change; any future source/parameter edit needs a separate decision |
| P3 / OPTIONAL, post-launch | Modern long consists can encounter the seven-tile cap | Review when modern stock enters service; both tested early long freight alternatives already fit | Avoids an unsupported launch-rule change | High for early examples, untested for every future duty | Retain seven tiles |

No confirmed **CRITICAL** economic defect remains. The major access-blocking risk calls for conduct/layout safeguards, not an automatic economy intervention. High coastal profit is a monitoring issue, not sufficient evidence for a blanket ship nerf. No change to purchase cost, running-cost factors, performance, dates, roster or shared base costs is recommended for implementation from this phase.

The smallest practical pre-launch work is to agree terminal-access/exclusive-rights conduct and run the recorded shared-market/postal checks during the first session. The campaign can otherwise proceed. Keep a separate post-launch issue for Class 66 and the Polish duplicate families so they do not turn the opening decision into another 1830–2025 audit.

See [readiness and the player procedure](MULTIPLAYER_ECONOMY_READINESS.md), [quantitative analysis](TRANSPORT_ECONOMY_PHASE4.md), and the four structured research CSVs. Every proposed action is a recommendation; no balancing correction has been applied.
'''
    (D/'FINAL_ECONOMY_ACTION_PLAN.md').write_text(action,encoding='utf8')
    print('Wrote Phase 4 report, readiness decision and action plan; primary world:',primary)
if __name__=='__main__':main()
