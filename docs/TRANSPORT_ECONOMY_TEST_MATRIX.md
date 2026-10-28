# Transport economy test matrix

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

`C:\Users\Kladd\Documents\Codex\2026-10-28\openttd-europe-1830-2025-historical-industry\.research`

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
