# Industry-chain validation, Phase 6B

The 467-industry candidate has actual loaded-delivery evidence, but graph
coverage alone is not treated as a working route or an economic result.

## Source and graph coverage

[The 96-type candidate matrix](research/industrial_1830_candidate_matrix.json)
is evaluated from the actual prepared Python definitions. The original
[92-type matrix](research/industrial_1830_source_matrix.json) is retained.
[The cargo graph](research/industry_chain_graph.json) joins those recipes to
actual placed industry IDs. [Coverage CSV](research/industry_chain_coverage.csv)
contains producer/consumer counts, regions and nearest-consumer distances.
Optional supply boosts and ordinary acceptance edges must not be mistaken for
mandatory input requirements.

| Cargo | Placed producers | Placed accepting industries | Interpretation |
| --- | ---: | ---: | --- |
| CORE | 2 | 1 | Cornwall / Parys to Swansea |
| COPR | 1 | 12 | Existing wharf export markets |
| SALT | 6 | 8 | Two added historic salt mines plus four inherited soda-ash by-product sources; use the two mines as the verified historical basis |
| FOOD | 92 | 13 | Export ports, not forced town retail |
| GOOD | 56 | 12 | Export wharves |
| SLAG | 5 | 0 | Explicit early waste stream, not a fabricated 1830 cement chain |

Established chains include coal–coke/brick, ore–ironworking, grain–flour/brewing,
wood–sawmills/furniture/paper, livestock–food, fish–food and manufactured exports.
Some source industries require no compulsory co-inputs but accept optional
boosts. Their original behavior is retained; no claim is made that the original
FIRS abstractions are exact historical mass balances.

Food and goods have **no preserved local retail sites**. The farthest producer's
nearest accepting industry is 2,394 Manhattan tiles for FOOD and 1,747 for GOOD.
These are straight grid metrics, not constructed route distances. They expose
an important inland market limitation. No profitability or travel-time claim
is derived from those numbers.

## Observed deliveries on the actual Europe map

Every row below uses a disposable gameplay copy of the delivered candidate,
period-buildable vehicles and actual produced cargo. A construction grant
isolates route functionality. Candidate files and normal game settings remain
unchanged. Positive sampled vehicle-profit changes near the receiving stop
document credited income after observed loading; they are not complete invoice
totals, annual profit, or GBP-normalized comparisons.

| Service | Actual locations | First paid delivery after commissioning | Evidence |
| --- | --- | ---: | --- |
| British COAL | Lancashire mine → regional brick works | 141 economy days | VERIFIED IN GAME |
| Ruhr COAL | Nachtigall district mine → regional brick works | 253 | VERIFIED IN GAME |
| GRAI | Tagus farm → flour mill | 183 | VERIFIED IN GAME |
| WOOD | South Norway forest → sawmill | 202 | VERIFIED IN GAME |
| IORE | Upper Silesian ore mine → blast furnace | 214 | VERIFIED IN GAME |
| SALT | Bochnia mine → nearby meat-curing works | 126 | VERIFIED IN GAME |
| FISH by Brig | Copenhagen fishing grounds → fishing harbour | 184 | VERIFIED IN GAME |
| PASS by horse | Local London service | 96 | VERIFIED IN GAME |
| MAIL by horse | Local London service | 301 | VERIFIED IN GAME |

The candidate preserves the source's calendar 1830 / economy 1800 distinction.
The table's elapsed days are **economy-clock observations**, not an assertion
that the initial economy year was changed to 1830. Source production peaks are
not measured for passenger/mail services; zero in their harness sentinel is
not a measured zero town production.

Raw route identities, coordinates, engine-case paths, script and source hashes,
payment observations and acceptance dates are in
[industrial_route_validation.json](research/industrial_route_validation.json).
Land freight used real eGRVTS horse vehicles; these tests do not certify
seven-tile locomotive hauling performance. The iron test certifies ore arrival
and payment, not every subsequent metalworking stage.

## New processor controls

Before integration, separate fresh maps demonstrated all three complete new
production routes: CORE/COAL/SAND → COPR → wharf; SALT/LVST → FOOD → port;
SALT/FISH → FOOD → port. Inputs were loaded and delivered, output was produced,
and output deliveries were credited. Missing-input controls produced nothing.
Stockpiles persisted across successive reloads. See
[the copper/salt report](COPPER_SALT_1830_VALIDATION.md) and
[raw control evidence](research/copper_salt_runtime_validation.json).

The fresh maps used calendar/economy 1830, unlike the original Europe's economy
1800. They validate recipe functionality, not equivalent route prices, cargo
decay, annual output or multiplayer economics. Full maritime ore delivery from
Cornwall/Anglesey to Swansea and curing-output export on the actual Europe map
remain **MANUAL TEST REQUIRED**.

## Missing stages, intentional waste and blockers

- SLAG and other unused early by-products are waste or future-use cargos.
  No future slag grinder is backdated to create artificial coverage.
- Modern chains with no 1830 inputs/types are not forced into the opening map.
  The matrix/graph marks unavailable or missing producers rather than zeros
  masquerading as successful tests.
- Retail construction requires house replacement. Existing town records and
  houses were protected, so ports/wharves are the current final markets.
- Aveiro's unchanged Salt Evaporator could not be sited. Its region can import
  salt, but local salt-pan production there is **BLOCKED**, not verified.
- Four inherited soda-ash mines need historical site review. Do not justify
  new salt geography using their unverified mineral locations.

## Future industry progression

The source parameter vector is preserved. Parameter **2, bit 2**, is zero.
Despite the internal variable name `restrict_open_during_gameplay`, the compiled
AXIS availability switch returns no construction when that bit is zero for
`IND_CREATION_RANDOM`. JGRPP's deity GameScript API calls that same RandomCreation
availability path. An actual 1830 test returned `CanBuildIndustry=false` and
`BuildIndustry=false / ERR_PRECONDITION_FAILED`, with no industry created.
Company-funded new processors are allowed; raw mines additionally require the
raw-funding setting, which is disabled in the campaign. Existing industries
continue production, but continued operation is not proof of future openings.

An ordinary scheduler GS therefore **cannot** simply add neutral industries
under the present settings. A technically supported company-mode construction
path was exercised in the placement controls, but it charges a real company's
cash and does not solve neutral, free, historically scheduled progression.
That is not silently substituted for an approved campaign policy.

To complete 1830–2025 progression, a separate decision and disposable test must
cover a newly created scenario configuration permitting the necessary callback
category while explicitly suppressing unwanted random openings, or a deliberately
revised/versioned availability policy. Then test scheduled eligible sites,
closures, raw funding, budgets, and future milestone chains. No such parameter
change or speculative engine/AXIS patch was made in this phase. Current API/source
evidence is in [the availability validation](research/copper_salt_availability_validation.json).
