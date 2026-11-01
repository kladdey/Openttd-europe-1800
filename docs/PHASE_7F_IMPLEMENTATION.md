# Phase 7F — historical ports implementation

**PARTIAL:** a separate playable development candidate and conditional port policy are implemented; no paid shipborne delivery was achieved. Do not mistake vessel buildability or port construction for a working freight service.

## Integrated base and scope

Remote main was `aaf6f6f`; local Phase 7E `4a6b056` existed and descends from it. New branch `feature/phase-7f-historical-ports` starts at that integrated base, preserving all 7E drivers, reports and paid modern-freight evidence. Main was not modified. AXIS 0.6.0, all 15 NewGRFs, 64 cargos, seven-tile trains and initial calendar/economy **1830/1800** are retained.

The new **GS v5 / schema 4** subclasses the existing progression controller; it adds no competing scheduler. The first 32 expansion rows, four-mine policies, one-mill retirement and three scheduled coal events remain unchanged. Eight additional conditional events represent Liverpool and Gdańsk:

| Approximate gameplay year | Native industry / local ID | Purpose |
|---|---|---|
| 1831 | Port 39 | Breakbulk trade: accepts BDMT/FOOD/BEER/PAPR, generates ENSP/FMSP/POWR/MPAR |
| 1875 | Wharf 46 | Expanded trade: accepts COPR/BOOM/GOOD/CMNT, generates MNSP/RAMT/ENSP/FMSP |
| 1975 | Bulk terminal 51 | Late reconstruction/industrial bulk: accepts ZINC/FERT/VEHI/STEL, generates IORE/COAL/AORE/CORE; native earliest 1970 |
| 1995 | Supply yard 69 | Land-side modern logistics proxy: accepts VEHI/PETR/BOOM, produces ENSP; native earliest 1914 |

These repeat in both regions, yielding 40 conditional expansion rows total. The modern supply yard is **not a container terminal**; no container cargo, new port type or cargo slot was invented. There is no liquids-terminal event or claim that the full postwar oil economy was implemented. Existing native trade-port production is an AXIS import/export abstraction, not a measured overseas economy. Endpoint prerequisites check registered producers/consumers, not connected profitable routes.

Every new event has a ±32-tile Manhattan search around its named town, a 20-year expiry window, six batches and at most 96 native construction attempts. Cancellation replaces no town or infrastructure. Future event construction and economic usefulness remain conditional and unverified.

## History and port selection

Liverpool is supported by the [UNESCO nomination dossier](https://whc.unesco.org/uploads/nominations/1150.pdf), including nineteenth-century dock expansion and the 1832 timber-trade Brunswick Dock. Gdańsk's [port authority history](https://www.portgdansk.pl/en/sustainable-development/investments-and-development/the-port-and-the-city/) supplies regional maritime context and the Northern Port's 1974 milestone. **1831/1875/1975/1995 are proposed gameplay windows, not exact founding dates or site-level historical reconstructions.**

| Candidate | Actual evidence / decision |
|---|---|
| Liverpool | Existing wharf 458; a new native Port 39 built in the disposable probe at tile **3914711**, 20 attempts. Chosen for conditional development. |
| Gdańsk | Existing Phase 6B Port 155 and Wharf 463 retained at (765,796)/(750,803); substantial coastal water around town 100. Chosen as the second compatible port region. No new Gdańsk opening or paid Baltic route was tested this phase. |
| Hamburg | Native site search passed **zero candidates** through the conservative union-footprint screen within its bounded window. It did not demonstrate a native callback failure or prove Hamburg impossible. Narrow river geometry is present; no widening or relocation attempted. Deferred. |
| London/Thames | Water exists one tile from the town anchor, but navigability, adequate native port footprint and legal stations were not tested. Deferred to avoid another speculative placement. |
| Rotterdam / Antwerp | Nearest mapped water is 35 / 33 Manhattan tiles from town anchors. Water occurs in the surrounding square, but suitable port geometry and sea connection were not established. Deferred, not declared impossible. |

The [map geography dataset](research/phase7f_port_geography.json) distinguishes water proximity from navigability. Town anchors come from the saved 617-town inventory; modern latitude/longitude was not used as tile coordinates. Hamburg's real tidal-port expansion is well documented by its [port authority](https://www.hafen-hamburg.de/en/experience/geschichte/); the map search failure is a game-geography constraint, not a claim about historical Hamburg.

## Native siting and persistence

The 7D land-only screen rejected water and is unsuitable for built-on-water AXIS ports. The new override permits native coast/water envelopes **only for the added coastal types**, rejecting houses, roads, occupied or unbuildable land. It checks the union of all layouts, including native signed offsets encoded as 255 → −1. A coastal/water envelope is required; native `BuildIndustry` and all callbacks still decide legal construction. No terrain, sea reclamation, demolition or recipe commands were introduced. Ordinary land events retain the previous screen.

Industry events are server/deity construction only. Docks, depots, horses and vessels in the diagnostic routes were built through supported company-mode GameScript commands as **player-company infrastructure**; the normal scheduler does not grant fleets or docks, and players must finance/build their own services.

The existing contract/ledger/attempt budgets provide deterministic scheduling and safe cancellation. The GS package is separately versioned to 5, while the ledger stays schema 4. MinVersionToLoad 4 permits the empty prior scenario configuration to initialize; an old running v4 save has a different policy contract and must fail closed. No automatic migration is supplied. Final metadata was corrected to use each actual industry's rules/source; the runtime startup evidence precedes that metadata-only correction and is not a certification of the final contract's save/reload.

The Scenario Editor saved a separate candidate. Initial CITY/INDY/PATS/PSAC, every map plane and every GRF reference/parameter match Phase 7D exactly. All 617 towns and 542 initial industries are preserved, including existing port facilities. Previous scenarios, normal configuration and GRFs remain untouched. The normal game loaded the new controller and enrolled the original four mines and mill with **542 baseline industries / schema 4**; route construction then failed before a normal monthly scheduler cycle. Normal scheduled port openings, event-boundary reload/idempotence and multiplayer are **UNVERIFIED** in Phase 7F.

## Real-engine route attempts

Seven invocations total, including the editor. No more engine runs were performed after the permitted seventh alternative:

1. First native probe: Squirrel statement-terminator failure; corrected.
2. Native probe: legal Liverpool port construction; Hamburg conservatively deferred; actual 1830 vessel capability checked.
3. First intermodal run: shared mode-independent depot cache offered a ship depot to a horse vehicle (`ERR_VEHICLE_NOT_AVAILABLE`). Fixed **in the new harness** by separating the depot caches; prior 7E code is untouched.
4. Corrected intermodal run: farm **50 GRAI → mill 260**, horse FOOD feeder to a dock joined to station 0 at Dublin Port 150, two Brigs to Liverpool Port 542. Grain was genuinely paid; occasional monthly mill FOOD production reached 6–7. Over **1,825 economy days**, neither feeder nor ship was observed carrying FOOD; sampled dock FOOD remained zero. Root cause of feeder failure was not isolated. Ship result: loaded=false, paid=false, peak=0, income samples=0; current+previous-year vehicle profit **−£1,004**. This is a completed negative observation, not proof that sailing ships are inherently uneconomic.
5. Scenario Editor: separate native save of the untouched 1830 baseline with the new profile.
6. Direct MNSP **Liverpool wharf 458 → Dublin mill 260**: no legal destination dock in the builder's native catchment candidates. New-controller startup succeeded; shipment did not.
7. Permitted indispensable alternative, announced beforehand: MNSP **458 → Greenock fishing harbour 410**. Docks built, but the bounded water-component check found no connected approach (182,449 visited tiles; 700-tile Manhattan envelope / 350,000-node bound). No ships were commissioned for that route. This establishes failure for the chosen approaches/search, **not global disconnection of the Irish Sea or Clyde**.

The early test Brigs were existing Sailing Ships engine **616**, native purchase **£3,808**, list running **£492/year**, refitted capacity **50**. API buildability also listed schooner/barque/merchantman/clipper variants; none was newly installed or enabled. Horses were engines **402** and **430**, capacity eight. Dates in finance/sampling logs use **economy time** (1800 onward); the fixture's actual calendar starts in 1830. Road transfer credits were not counted as maritime delivery revenue.

No positive shipborne payment or amount transported is verified. No shipping profitability/payback calculation is justified. No price, production, cargo-payment or vehicle changes were made. [Route results](research/phase7f_route_results.csv) and [receipts](research/phase7f_test_receipts.json) retain failures and negative observations; large raw logs stay local.
