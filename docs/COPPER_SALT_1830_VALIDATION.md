# Copper and salt in 1830

Status: **validated, separately versioned 0.3.0 candidate**, incorporated into
the industrialized scenario copy. This is not a change to the Phase 6A source
or to Historical AXIS 0.2.0. No push or merge.

## What the actual definitions permit

The prepared 0.2.0 Classic source registers **92 industries and 64 cargos**.
[The complete source matrix](research/industrial_1830_source_matrix.json)
contains the actual IDs, properties, inputs, outputs, dates, layouts and siting
checks. Fifty types meet the source's 1830 construction policy. This policy is
partly provisional historical research, not evidence that every possible site
or graphical detail existed in 1830.

| Existing definition | Finding | Decision |
| --- | --- | --- |
| Copper Mine 64 | CORE producer already available | Reuse unchanged |
| Copper Refinery 67 | CORE/SCMT/ACID inputs; 1850 construction gate | Do not backdate or alter its recipe |
| Salt Mine 105 | Existing definition, disabled in Classic; existing salt-only output in other economies | Enable that existing SALT recipe in Classic |
| Salt Evaporator 117 | Existing 1830 primary SALT producer with restrictive water/coast layout | Preserve; Aveiro placement failed, not certified operational there |
| Food Processor 56 | 1850, accepts several inputs including SALT through existing secondary production logic | Do not backdate or use as a salt-only food converter |
| Fishing Harbour 90 / Stockyard 37 | Existing food routes without compulsory salt | Preserve; do not retrofit new compulsory inputs |
| Wharf 46 / Port 39 | Existing COPR / FOOD consumers respectively | Reuse as downstream export markets |
| Slag Grinding Plant 80 | 1945 | Do not backdate to consume early waste |

A dedicated **Copper Smelter** is necessary to represent the coal-fired process
without changing the later refinery. A separate raw **Salt Works** type is not
necessary for the validated mined-salt chain: SALT already represents finished
salt, and the existing mine includes its preparation. There is no brine cargo
slot to justify inventing a SALT-to-SALT refining chain. Coastal pan placement
remains a separate unresolved siting issue. Dedicated food-curing processors
provide historically plausible salt demand without changing existing recipes.

## Implemented candidate

GRFID **4B484531 / KHE1**, numeric version **3**, minimum compatible **2**.
The candidate registers **96 industries and exactly the same 64 cargo slots**.
No cargo label, slot order, vehicle or original enabled recipe is changed.

| Industry | Local ID | Earliest year | Mandatory game batch |
| --- | --- | --- | --- |
| Traditional Copper Smelter | 123 | 1700 | 6 CORE + 18 COAL + 1 SAND → 1 COPR + 4 SLAG |
| Fish Saltery | 124 | 0 | 3 FISH + 1 SALT → 3 FOOD |
| Meat Curing House | 125 | 0 | 3 LVST + 1 SALT → 3 FOOD |
| Salt Mine, enabled in Classic | 105 | 0 | Existing SALT primary production, ENSP optional boost |

These integers are **authored game recipes**, not extracted historical assays,
measured curing yields or economic calibration results. SAND abstracts silica
hearth/flux supply. Real ore mixtures, flux needs and fuel use varied. The
Welsh process's coal-fired furnaces, repeated roasting/melting and slag removal
are documented by [Historic England's copper-smelting research](https://historicengland.org.uk/research/results/reports/5884/Post-MedievalandModernCopperSmelting).
The [1823 Hafod account held by Amgueddfa Cymru](https://museum.wales/collections/online/object/c7f6ffdf-f60b-30de-b4e8-64870393cdc8/Proceedings-at-the-Hafod-Works-on-Smelting-Copper-1823-book/)
anchors pre-1830 operation. [Royal Commission archaeological research](https://coflein.gov.uk/media/36/934/aent28_11.pdf)
supports the fuel-intensive South Wales smelting geography. No acid leaching,
electrolysis or twentieth-century slag cement is introduced.

Salt curing of fish and meat is documented by the [Portuguese agricultural
authority's traditional Aveiro salt description](https://tradicional.dgadr.gov.pt/pt/cat/sal-marinho-e-flor-de-sal/1040-sal-de-aveiro-flor-de-sal-de-aveiro).
The [Cracow Saltworks Museum](https://muzeum.wieliczka.pl/en/exhibition/the-cracow-saltworks-the-royal-enterprise)
documents the established Wieliczka/Bochnia mining enterprise. Regional curing
layouts are representative trades, not verified individual factory addresses.

The new production callback consumes the minimum complete batch available
across **all** required inputs. Incomplete inputs remain stockpiled. Reused
copper-refinery and stockyard graphics are visual proxies, not new historical
artwork. The original 92 enabled Classic models and all other economies'
enabled models compare identically in separate interpreter evaluations;
[the preservation evidence](research/copper_salt_source_preservation.json)
includes both GRF hashes. Registration can extend globally generated neighbour
checks, so this is not a claim of byte-identical old callbacks.

## Actual engine tests

JGRPP **0.73.4**, exact campaign 15-GRF library. The initial controls used new
256×256 disposable maps with calendar/economy year 1830 and construction grants.
Only buildable period vehicles were used. No forced vehicle availability or
performance changes. These are functionality tests, not annual-profit tests.

| Test | Observed result | Evidence |
| --- | --- | --- |
| Ore alone | CORE stock 6; COAL/SAND 0; COPR production 0 | VERIFIED IN GAME |
| Ore + coal, no sand | CORE 24; COAL 22; SAND 0; COPR 0 | VERIFIED IN GAME |
| Complete copper chain | Ore, coal and sand loaded/delivered/paid; COPR production observed, then COPR delivered and paid at wharf | VERIFIED IN GAME |
| Salt alone at meat works | SALT stock 6; LVST 0; FOOD 0 | VERIFIED IN GAME |
| Complete meat chain | SALT/LVST deliveries, FOOD production, FOOD delivered and paid at port | VERIFIED IN GAME |
| Salt alone at fish saltery | SALT stock 6; FISH 0; FOOD 0 | VERIFIED IN GAME |
| Complete fish chain | Brig delivered FISH; horse vehicles delivered SALT and exported FOOD; all paid | VERIFIED IN GAME |
| Persistence | Two successive paused reload probes per processor retained identical stockpiles/production readings | VERIFIED IN GAME |
| Availability | New processors permitted in 1830 company context; types 67/56 still unavailable | VERIFIED IN GAME |
| Compilation | Successful build; full corresponding-source ZIP rebuilt to identical GRF SHA256 | ENGINE-CALCULATED |

First observed positive monthly outputs were 4 COPR, 6 meat FOOD and 6 fish FOOD
in the recorded fixtures. These are sampled outputs, not fixed industry rates.
Raw positive vehicle-profit deltas document payment events, not annual net
profit or GBP-normalized economic comparisons. See
[runtime evidence](research/copper_salt_runtime_validation.json) and
[availability evidence](research/copper_salt_availability_validation.json).

Two harness defects were resolved before accepting results: starting and then
stopping held vehicles could obstruct the shared depot, and reusing a receiving
stop could miss the producer catchment. `HasDock()` also only signals an industry
flag; an actual valid dock location must be checked. Failed exploratory cases
remain under the ignored local work directory and are not counted as passes.

## Geography incorporated

The separately delivered 467-industry candidate includes:

| Industry | Tile x,y |
| --- | --- |
| Dolcoath copper district mine | 3270,1490 |
| Parys Mountain copper district mine | 3165,971 |
| Hafod/Swansea smelter representation | 3124,1247 |
| Swansea ancillary mineral supply quarry | 3124,1238 |
| Swansea export wharf | 3128,1268 |
| Wieliczka salt mine | 622,1532 |
| Bochnia salt mine | 582,1523 |
| Krakow regional meat curing | 636,1516 |
| Bochnia regional meat curing | 591,1526 |

Five fish salteries and a third meat-curing site complete the regional additions.
[Parys Mountain's recorded ore shipments to Swansea](https://coflein.gov.uk/en/sites/33752)
support that trading pattern. Cornwall's historical mining importance is
documented by [UNESCO](https://whc.unesco.org/en/list/1215/). Allihies, Gwennap,
Neath and the Aveiro evaporator remained failed requests; no site was moved to a
different historical region to obtain a success.

All primary and processor nodes have existing downstream cargo edges: CORE
to the smelter, COPR to wharves, SALT plus fish/livestock to curing, FOOD to
ports. **SLAG is explicitly an untransported waste by-product in 1830.** No
false complete slag chain is claimed. Four inherited soda-ash mines also list
SALT as output, but their regional historical siting is unverified. The new
salt-chain validation does not depend on them.

On disposable copies of the real Europe map, Bochnia SALT was actually delivered
and paid at the nearby curing house. Full copper and curing output chains were
operated on the controlled maps; a full Cornwall/Anglesey–Swansea maritime ore
service has **not** yet been operated on the Europe map. That geographical route
and the long-distance FOOD markets remain human-playtest items.

## Compatibility and files

No existing scenario had its NewGRF list changed in place. A **new copy** used an
engine-generated 0.3.0 reference record, retaining the same parameters and other
14 references. Before additional placement, all 438 industry identities and all
617 town records/map arrays survived engine reload unchanged. After placement,
all 438 old industry records remain bit-identical.

New local scenario:
`C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.3.0 Candidate - Industrialized.scn`.
Matching, separately named GRF:
`C:\Users\Kladd\Documents\OpenTTD\newgrf\axis-historical-europe-0.3.0-candidate.grf`.
Old GRFs, the Phase 6A source, settings and previous placements were preserved.
Do not downgrade a new-type scenario to 0.2.0. Only this tested append-only
upgrade is certified; arbitrary saves and stock AXIS swaps are not.

GRF SHA256: `f0da622873c91107fa4d2b768d88cd95d5db009c2b2975bdb6d7ab6caaed3c33`.
Scenario SHA256: `b05ef51a3bd17eb453d6b5e4af544c0745fee372a6195f5354ab8bd927ce6e75`.
Reproduction commands are in the [candidate README](../newgrfs/axis-historical-copper-salt/README.md).
