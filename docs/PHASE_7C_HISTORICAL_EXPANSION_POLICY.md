# Phase 7C — historical expansion policy

This is a representative regional vertical slice, not a complete reconstruction of European industry through 2025. Ten new opening events extend the three existing Phase 7A events. One original processor joins the four unchanged Phase 7B managed mines. Nothing changes at the initial 617-town / 542-industry snapshot.

## Historical interpretation

All ten new dates are **regional gameplay proxies**, not identified factory founding dates. The mill retirement is a proposed modernization scenario, not a discovered historical closure. Coordinates use the existing scenario's town/industry inventory, not an uncalibrated latitude/longitude projection. Galicia anchors are Wieliczka (621,1526), Bochnia (582,1529), Krakow (634,1514); the German cluster is the Rhineland/Ruhr industrial region near the existing blast furnace and Dusseldorf (2008,1323). Names do not imply precise cadastral sites.

| Era | Events / normal dates | Existing-cargo transport chain | Evidence and limits |
|---|---|---|---|
| 1830–1860 | Galicia flour mill, 1835; nearby modernization successor, 1887 | Existing farm GRAI → mill FOOD → existing market/general store. MNSP boosts the retained recipe. | The regional milling history documents renewed activity from the later eighteenth century and use of mill infrastructure into the nineteenth/twentieth century. It does **not** establish an 1835 Wieliczka factory or an 1895 closure. Actual new-mill deliveries tested separately. |
| 1860–1900 | Rhineland/Ruhr sheet mill and steelworks, 1865 | Existing IORE / COAL / LIME → coke oven and blast furnace → IRON + COKE → steelworks STEL → sheet mill MPAR / BDMT → machine shop / hardware consumers. | Krupp's archive records Bessemer adoption in 1862 and open-hearth adoption in 1869. These support the regional steel expansion, not an exact mapped establishment. Steel's historical recipe requires both inputs; do not treat it as generic combinatory production. |
| 1900–1945 | Regional metal workshop, 1910 | STEL → workshop MPAR / MNSP → existing machine shop and mills. ALUM / COAT remain optional combinatory boosts. | Thyssen's archive describes early twentieth-century vertical integration and manufacturing expansion. This policy does not reenact wartime destruction. Construction verified on the small map, not a paid Europe route. |
| 1945–1980 | Regional slag grinding plant, 1955 | Existing blast-furnace / scheduled steel SLAG → grinding CMNT / FERT → existing wharf / farms. | German cement history supports postwar recovery; native AXIS dates prohibit this type before 1945. The retained FERT output is an AXIS abstraction, not a claim that every slag has the same chemistry. Native siting requires a blast furnace / BOF / EAF within 56 tiles; the historical steelworks alone is insufficient. |
| 1980–2025 | Dusseldorf recycling collection, junkyard, recovery plant and plastics plant, 1985 | Town RCYC → recycling plant PLAS → plastics plant MNSP → existing processors. Junkyard is a native location prerequisite and has a separate SCMT output. | European waste legislation provides a policy-era context; 1985 is not a verified local commissioning date. Collection opened in the small-map test. Junkyard construction failed there, so the downstream pair safely cancelled. This chain is **not operationally validated**. |

The schedule and source links are in `gamescripts/historical_industry_lifecycle/expansion_policy.json`; `docs/research/phase7c_regional_chain_matrix.csv` includes actual local IDs, dimensions, input/output labels, constraints and anchor tiles. The initial roster has **96 registered industry models** (the earlier 92 plus four copper/salt additions) and the same **64 cargo slots**.

## Sources

- [Krakow milling infrastructure research](https://yadda.icm.edu.pl/baztech/element/bwmeta1.element.baztech-e4b3fd16-d0b9-435d-9ca9-62a628336f0a/c/Michalowski_Infrastruktura_PB_6_2024.pdf): regional context and uncertainty of exact mill identities.
- [Krupp corporate history](https://www.thyssenkrupp.com/en/company/history/krupp-and-thyssen-history/krupp-corporate-history): steelmaking methods and railway-related manufacturing.
- [Thyssen corporate history](https://www.thyssenkrupp.com/en/company/history/krupp-and-thyssen-history/thyssen-corporate-history): Ruhr integration and early twentieth-century expansion.
- [Heidelberg Materials history](https://www.heidelbergmaterials.com/en/company/heritage/publications/150-years-of-heidelberg-materials), [VDZ history](https://www.vdz-online.de/historisches), [Beckum cement museum](https://zement-museum.de/beckumer-zementrevier.html): development and postwar recovery of German cement production. These do not identify the scheduled slag plant.
- [European Parliament chronology of waste legislation](https://www.europarl.europa.eu/workingpapers/envi/pdf/100_en.pdf): 1970s legislation as context for the later collection/recovery proxy.

## Coverage and deliberate gaps

The graph in `phase7c_chain_graph.json` adds compatibility edges involving new events and retiring mill 275; unchanged baseline chains remain in the earlier graph. Distances are Manhattan tile distances, not surveyed routes. `phase7c_projected_chain_coverage.csv` is explicitly **MODELLED**: it assumes conditional openings and is not an actual future production census.

FOOD has existing final consumers in 1830. Flour's EOIL byproduct has no 1830 consumer in the registered roster: food processing first becomes available in 1850 and liquids terminals in 1970, neither is added by this schedule. SCMT also needs an appropriate future consumer; the modernization pilot does not automatically create an EAF or copper refinery. These are honest coverage gaps, not invented conversions. The core grain/food chain still works. No new recipes, cargo IDs or vehicles are introduced to hide these gaps.

Construction is conditional on actual cargo endpoint presence and predecessor events. It does not guarantee sufficient production, a navigable route, affordable infrastructure or profitable hauling. New industries are protected from automatic closure; further factory retirement requires a new reviewed policy. There is no claim of complete 195-year industrial balance.

## Replacement and fairness

Original flour mill 275 at (622,1507) is the sole processor enrolled. Normal notice begins in 1885, earliest retirement is 1895, and the reviewed window ends in 1905. A live same-type successor must be within 96 tiles, with a grain producer and food acceptor within 160 tiles of it. If these checks fail, or a late notice cannot receive its full lead time within the window, the mill stays open at reduced capacity for administrator review. It is never closed simply because a date passed.

Factory survival has **no pickup-based extension**. Phase 7B's four mine policies, finite deadlines and rolling-service extension remain unchanged; their public pickup metric still cannot establish final delivery attribution or rule out pickup/dump abuse. New openings use deity construction and public news, with no company reservation, cash transfer, subsidy or leading-company preference.

Every event has five years' nominal advance announcement, native availability checks, a bounded regional alternative-site list, at most 96 construction commands and six search batches. Occupied sites are skipped; no player infrastructure is bulldozed. Cancellation is a visible outcome, not a reason to silently move an industry elsewhere in Europe.
