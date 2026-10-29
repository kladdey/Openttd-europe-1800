# Inland market gameplay validation

**Actual engine observations, JGRPP 0.73.4; no calculated cargo payments are presented as deliveries.** Final-candidate route tests, financial ledgers, load/payment events and hashes are in [route results](research/inland_route_results.csv), [33 annual ledgers](research/inland_route_finances.csv), [17 paid-leg observations](research/inland_paid_deliveries.csv) and [portable engine evidence](research/inland_gameplay_evidence.json). Twelve retained cases include blocked attempts, technical regressions and two different fruit fleets; they are not twelve successful or independent profitable strategies. Superseded GOOD horse-tram diagnostics are retained separately.

## Measurement and corrections

Each test uses a fresh disposable copy of the final 542-industry Europe map and its exact GRFs. Ordinary comparisons start with **£100,000 cash, £100,000 outstanding loan and £300,000 maximum loan**, maintenance enabled and seven-tile train limit unchanged. No grant is used for those comparisons. Unneeded loan is repaid after building, retaining a £10,000 reserve; borrowing can increase in legitimate £10,000 increments if reserves fall below £5,000. This is a declared financing policy, not hidden free capital.

GBP has engine currency rate **1**. GameScript money is recorded directly as pounds; no arbitrary division by two is applied. Calendar starts 1830 while `GSDate` and annual expense tables follow economy year 1800. Tables explicitly map 1800–1804 to calendar 1830–1834. They do not claim five years of historical technology changes independent of the game's clocks.

For each leg the script observes positive cargo load, then a positive vehicle-profit increment at/near its accepting destination. This establishes loaded transport and credited payment. The sampled increment is **net vehicle profit since the previous sample**, not the exact gross value of a whole shipment. Annual gross revenue and expenses come separately from `GSCompany.GetAnnualExpenseValue` after year rollover. Construction and vehicle purchases are capital; operating expenses include vehicle running, infrastructure/property, interest and the engine's other-expense category. Taxes/fees are not invented to explain that category. Company-wide totals encompass the complete tested chain, not only its attractive final leg.

Tests exposed and corrected fixture problems before economic interpretation:

- Cheapest compatible GOOD selection initially chose horse **tram 315**. Final road comparisons require road type 0 and use ordinary carriages. The superseded GOOD tram trial is retained separately. Inspection of the actual engine lines confirms that both fruit fleet tests used ordinary Ice Box Carriage 430; they are valid road observations.
- Passenger-style partial-load orders caused empty long outbound trips while processors waited for supplies. Final road/rail chains use full-load-any orders at production; coastal FOOD retains its recorded partial-load policy. These policies are visible in the results.
- A UKRS2 train requires its brake van. Tight adjacent legal rail bends were unusable with the campaign's turn restriction. The corrected planner avoids those bends and keeps a straight terminal approach; no campaign setting was changed. Only the moving, paid corrected railway is used economically.
- The final train prefers the actual compatible UKRS2 Open Wagon 1430; it is not the earlier refittable Single Bolster experiment. A previous final-year ledger-label issue was corrected; the evidence generator rejects duplicate annual labels instead of silently relabelling them.
- An early technical salt run requested a grant inside company mode; the API did not apply it (initial cash remained £100,000). It remains conservatively **technical-only**, with no profitability claim. The helper now applies and checks grants in deity context before entering company mode. The copper Europe attempt records the actual £1,000,100,000 initial balance and is also technical-only.

## Completed loaded chains and ordinary-budget results

Amounts below are **VERIFIED IN GAME**, cumulative over the stated observation period. Capital recovery means observed cumulative operating surplus covering construction plus vehicles, not debt repayment or a forecasted ratio. Except coastal FOOD, recovery was **not observed**.

| Complete service | Legs: industry IDs and Manhattan tiles | Years | Infrastructure / fleet capital | Gross revenue | Operating profit | First all-leg payment |
|---|---|---:|---:|---:|---:|---:|
| Kraków local horse FOOD | GRAI 66→275: 31; FOOD 275→474: 17 | 3 | £11,445 / £2,296 | £1,960 | **−£3,308** | 388 economy days |
| Prague local horse GOOD | FICR 187→370: 45; GOOD 370→522: 20 | 3 | £14,898 / £2,296 | £1,338 | **−£4,763** | 757 days |
| British regional horse FOOD | GRAI 47→257: 33; FOOD 257→479: 99 | 3 | £20,868 / £2,296 | £1,687 | **−£6,297** | 624 days |
| French longer horse GOOD | FICR 181→364: 48; GOOD 364→481: 164 | 5 | £49,203 / £2,296 | £2,184 | **−£27,912** | 1200 days |
| Valencia orchard → Food Market | FRUT 171→538: 40 | 3 | £12,177 / £1,148 | £1,308 | **−£3,837** | 163 days |
| Kraków rail + horse FOOD | GRAI 66→275 by rail: 31; FOOD 275→474 by road: 17 | 5 | £11,842 / £11,731 | £29,070 | **+£16,498** | 131 days |
| Coastal fish → harbour → FOOD export | FISH 141→413: 29; FOOD 413→154: 29, both ship | 3 | £2,218 / £15,232 | £34,013 | **+£23,934** | 284 days |

The longer GOOD case is the second bounded geographical candidate (`INLAND_ROUTE_RANK=1`), after the first route could not build a turning loop. It really delivered; it is not a theoretical payment calculation. Its company borrowed from £70,000 after commissioning to **£90,000**, finishing with £10,587 cash. A 164-tile carriage trunk with new infrastructure and low throughput is a poor observed investment. This does not prove all French starts or all GOOD delivery are unviable.

The railway is Planet 1534, **12 Open Wagons, a brake van, 72 grain capacity, length 44 sixteenth-tile units (2.75 tiles)** and four-tile stations, below the unchanged seven-tile limit. Its first-year operating profit was £2,439; five-year surplus £16,498 remains below £23,573 capital. Final cash £32,922, loan £40,000. The otherwise comparable two-horse-per-leg chain loses money: throughput and infrastructure utilization matter more than nominal locomotive price.

The coastal chain uses two buildable compatible Brigs on each leg. Annual revenue was £7,574 / £12,884 / £13,555; operating profit £4,464 / £9,456 / £10,014. Cumulative surplus exceeds £17,450 capital in year three. This is isolated-route evidence, not proof against port competition or a recommendation to nerf ships. The eight-carriage fruit alternative (engine 430, partial-load orders) invested £12,177 infrastructure plus £4,592 fleet, made £4,201 gross and lost £2,535 over three years; one year was positive, which does not establish long-term viability. Its higher throughput reduced the observed loss versus two carriages but did not eliminate it; fleet size and loading policy both differed, so this is not an isolated fleet-size experiment. A separate preliminary four-horse carriage trial also lost money and is not the final comparison.

Short horse freight is **functional but weak in these tested new-build configurations**. Small 8-unit carriages, long cycle times, limited fleet throughput, new-road maintenance, interest and company overhead explain the measured losses. For example, Valencia's two carriages earn £330–653 in later years against £167 running, £648 property, £600 interest and £300 other expense. This is not evidence that acceptance is broken, nor a justified universal horse buff. Existing-road/shared-infrastructure, passenger/mail cross-subsidy and denser feeder fleets require a human comparison. No prices or cargo payment settings were altered.

## Copper, salt and coastal regressions

**VERIFIED IN GAME on final Europe candidate:** SALT 443→445 (30 tiles), LVST 446→445 (59), then FOOD 445→Kraków market 474 (6). All three legs loaded and paid; complete chain by day 619. Observed first payment increments £117, £117 and £4 respectively. This is a technical functionality test, not a claim that its sparse six-carriage chain is profitable.

**VERIFIED IN GAME on a separate controlled 256×256 map:** fresh copper regression with the exact unchanged candidate GRF. Ore alone produced no copper; ore plus coal without sand produced none; adding all required inputs produced COPR (observed monthly 4) and paid export (£43 sampled net increment). All three inputs were also delivered and paid. The final pass line happened in a later zero-production sample; it follows a positive-production observation and does not mean copper production was fabricated. See [controlled receipt](research/inland_copper_regression.json). This proves the recipe, cargo compatibility and output acceptance, not a Europe route's financial performance.

**BLOCKED / MANUAL TEST REQUIRED on Europe geography:**

| Attempt | Observed limitation | Smallest manual completion |
|---|---|---|
| Textile 374→coastal wharf 459, following fibre 191→374 | Destination road station rejected `ERR_FLAT_LAND_REQUIRED`; first supply route was built | Inspect the wharf's actual accepting footprint; build an alternative roadside catchment/shared station without leveling terrain, or choose a water transshipment |
| Fibre 175→coastal textile 358→wharf 458 | Road commit at tile 3898231/3898232 rejected `ERR_AREA_NOT_CLEAR` after a nominal path search | In a disposable save, construct a nonintersecting approach/bridge and commission the two legs; record loaded GOOD and positive delivery revenue |
| Alternative all-water 176→358→458 | Bounded dock search found no legal origin station; `ERR_NONE` supplies no more precise engine diagnosis | Inspect source catchment and navigable coast, add a legitimate road-to-port transfer if needed; do not infer a GRF cargo rejection |
| Europe copper 440→456 after CORE/COAL/SAND supply construction | Bounded destination road-station search exhausted, `ERR_NONE` | Inspect Swansea works 440 and existing wharf 456; select a legal accepting station/sea transfer; run until COPR is loaded and paid |

These are builder limitations, **not proven impossibility** and not paid routes. No terraforming or recipe/GRF change was used to force a pass. Exact disposable cases, raw logs and exit-save paths are recorded in the route CSV/evidence. Open only those copies for manual completion. The 467 old industries and cargo recipes are unchanged, but unchanged bytes alone cannot prove an untested coastal GOOD route operates. This remains a caveat.

## Town regrowth and road observation

**VERIFIED IN GAME:** five unassisted years on the final 542-industry candidate, normal growth settings, no added services or forced growth:

| Town | Original population | Immediately after markets | After five years | Houses after markets → five years |
|---|---:|---:|---:|---:|
| London | 11004 | 10980 | 12469 | 485 → 486 |
| Prague | 1814 | 1802 | 1944 | 75 → 77 |
| Kraków | 559 | 547 | 644 | 26 → 27 |

The results show viable growth with these markets, not guaranteed universal recovery. Original population is a game value, not the historical population of the city. Full six-snapshot rows are in [regrowth CSV](research/inland_town_regrowth.csv); industry count remained **542 throughout**. House upgrades can grow population without increasing house count monotonically.

One original road tile, **(1142,979), tile 4011126**, became a house during the disposable five-year simulation. It was a one-bit dead-end road with one neighboring road before and after. This is consistent with ordinary town redevelopment but **causation was not isolated by a no-market control**. It is explicitly not counted as preservation of every road throughout gameplay. The delivered paused candidate changes zero road tiles. Do not disable ordinary town growth to conceal this observation; inspect it in human playtesting if road preservation during later growth is important.

## Save/reload and performance scope

Two gameplay load/save cycles retain identical town/industry/GRF rows and normalized map arrays. A real Scenario Editor save/reopen also retains these, PATS and calendar/economy fields; its only DATE-field difference is a newly generated unique save ID. The delivered file retains the baseline DATE chunk, not this editor-generated UUID. See [reload evidence](research/inland_reload_validation.json) and [editor evidence](research/inland_editor_validation.json).

Reload harness wall time includes process startup and a fixed tick budget; it is not a clean loading benchmark. No crash, industry disappearance or registration mismatch occurred in the completed tests. Neither these short runs nor a successful 1830 load certifies 195 years of progression, multiplayer competition, every possible route or all future cargo chains.
