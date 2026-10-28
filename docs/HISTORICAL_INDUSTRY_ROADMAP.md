# Historical industry roadmap — 1830–2025

Research/design only, 2026-10-28. Read the
[feasibility findings](HISTORICAL_INDUSTRY_FEASIBILITY.md) and
[91-type AXIS matrix](AXIS_INDUSTRY_MATRIX.md) first. Preserve the working
scenario, map, NewGRFs and **1830** start. No campaign conversion is authorized
by this design. Every experiment uses a new disposable scenario filename.

## Implementation decision

Start with a **curated 1830 scenario plus additive GameScript**. Engine industry
density is Funding only; AXIS's allow-spawning option must remain on for deity
construction. Player agreement covers premature secondary-industry funding.
The initial model does not forcibly close industries. If those compromises are
unacceptable, stop before implementing the scheduler and scope a custom industry
NewGRF. Do not promise to solve them with nonexistent script APIs.

Keep the code split into manifest/identity, cargo recipes, geography/resources,
historical policy, placement scheduler, inventory and save-state modules. Data
must be versioned separately from the scheduler so historical edits do not
require rewriting construction logic.

## Historical model

These bands are **design hypotheses**, not blanket dates for all of Europe.
The matrix assigns a draft band to each enabled type. Distinguish invention,
first commercial site, regional adoption and mass diffusion. Weight regional
growth gradually after a verified earliest site; never create an entire sector
at a continent-wide midnight threshold.

| Campaign band | Development policy using actual Classic types | Necessary qualifications |
|---|---|---|
| 1830–1850 | Farms, forests, coal/iron mines, coke ovens, blast furnaces, iron works, sawmills, textiles, glass, brick, flour, food markets and coastal trade. Connect existing early centers by canal, shipping and early rail. | Blast furnace produces **pig iron**, not steel in Classic. Iron works can consume it. Modern inputs to some early factories remain optional or require declared compromises. Canals/rail are transport policy, not AXIS industry types. |
| 1850–1880 | Expand coal/coke/iron districts; paper, cement, copper processing, engineering proxies and selected chemical works. | Classic has no enabled generic early `steel_mill` or `smithy_forge` in this extraction. Do not introduce an EAF or oxygen furnace just to fill the Bessemer/open-hearth gap. Imported steel or a custom historic steelworks is needed for that representation. |
| 1880–1914 | Petroleum, electrical works, late chemical processes, initial aluminium, and selected EAF sites near the end of the band. | Aluminium is **not wholly post-1945**: commercial electrolysis belongs to the late nineteenth century; expand hydro-linked production later. Synthetic ammonia reaches industrial operation in **1913**, at the end of this band. Do not equate all old chemical production with modern petrochemistry. |
| 1914–1945 | Vehicle/component/tyre chains, larger electrical/chemical capacity, selected plastics and synthetic-fuel sites. | Fischer–Tropsch/coal synthesis is an interwar specialization, not 1830. Broad plastics diversification needs process-specific evidence, even where AXIS permits 1900. No dedicated aircraft factory or aviation sector type is present in the Classic extraction. |
| 1945–1970 | Expand manufacturing and petrochemistry; appliances, oxygen steelmaking and larger aluminium clusters; offshore oil only from AXIS's 1967 gate. | Oxygen steelmaking gets a mid-century onset; postwar aluminium is an expansion wave. Container adoption can start late in this band, rather than waiting for 1970. |
| 1970–2000 | Port/logistics concentration, bulk/liquid terminals, recycling from AXIS's 1978 plant gate, manufacturing restructuring. | Terminals and material recovery existed earlier: use the listed late bands for their modern-scale representation. Coal/steel decline means reduced investment initially; GS cannot order retirement. |
| 2000–2025 | Modern biorefinery emphasis, recycling/logistics intensification, selected high-value manufacturing expansion. | No invented “advanced manufacturing” industry. Use existing appliance/component/electrical/assembly types and transport networks; existing industries need not disappear at phase boundaries. |

Historical anchors used to refine the initial brief:

* [Aluminum Association process history](https://www.aluminum.org/aluminum-miracle-metal)
  dates Hall–Héroult electrolysis to 1886 and the Bayer process to 1887. These
  support a late nineteenth-century start, not a map-wide 1886 unlock.
* [BASF chronology](https://www.basf.com/hu/hu/who-we-are/History/chronology)
  distinguishes the dye/inorganic chemical business founded in 1865, industrial
  ammonia synthesis in 1913, and interwar high-pressure synthesis. Exact AXIS
  “ammonia plant” Classic outputs are fertiliser/explosives, not an ammonia cargo.
* [voestalpine's LD-process history](https://www.voestalpine.com/group/en/media/press-releases/2012-11-27-voestalpine-celebrates-60-years-of-the-ld-process/)
  dates the first operating LD plant to November 1952. This supports reserving
  `basic_oxygen_furnace` for the postwar band.

Other table dates, process substitutions and all site quotas remain proposals
requiring site-specific museum/archive/company-history references. This task
does not claim an exhaustive European economic history. Do not use AXIS graphics
dates or availability defaults as historical evidence.

## Regional specialization and calibrated geography

No coordinates are specified here. Use the actual scenario's tile system,
independent landmark checks and the existing empirical calibration evidence.
Regions are economic districts, not necessarily modern national borders. Keep
geographic membership fixed unless a documented policy event changes it; do not
infer historical political borders from town language or modern country tags.

| District | Initial concentration / later policy | AXIS representation and caveats |
|---|---|---|
| Great Britain | Coal, textiles, coke/pig iron, engineering; later steel and manufacturing | Coal mines/textile mills/blast furnaces/iron works; shipbuilding is a transport/manufacturing proxy, **no dedicated Classic shipyard type**. |
| Ruhr and Rhineland | Coal/coke/iron/engineering; later chemicals and larger steel clusters | Mines, coke ovens and furnaces; paper/refining/chemical sites only after source and recipe review. Do not give all Germany a single resource weight. |
| Belgium | Coal, metallurgy, glass and textiles | Glass/textile/iron chains near verified districts; customer markets and imported intermediates may be shared with France/Rhine. |
| Northern France | Coal, textiles and metallurgy | Concentrate around documented basins; distinguish local ore from imported ore and avoid equal country-wide spawning. |
| Silesia | Coal, zinc, iron and steel | Coal mines and metallurgical sites; AXIS's pyrite smelter produces zinc/rare metals, which is a recipe proxy needing geological review, not a literal zinc mine. |
| Bohemia | Coal, glass, textiles and engineering | Glass/textile/iron and later machine/component sites; validate actual mapped Bohemian geography. |
| Scandinavia | Timber, ore and later pulp/paper; hydro-linked aluminium expansion | Forests/sawmills/iron mines/paper mills; no dedicated pulp industry in this Classic extraction. Aluminium's electricity dependence is a siting policy, not an electricity cargo edge. |
| Iberia | Mining, agriculture, textiles; later industry | Basin/site-specific iron/copper/pyrite, farms/textiles and selected later manufacturing; prioritize coastal export routes. |
| Northern Italy | Textiles and agriculture; later engineering/manufacturing | Textile/food chains first, component/electrical/assembly clusters later; allow imported ores and coal. |
| Eastern Europe | Agriculture, forestry and selected mines; later heavy-industry clusters | Distinguish basins and cities; do not treat the entire east as one uniform or historically industry-free region. |

This is a specialization specification derived from the brief, **not a verified
site catalogue**. Before assigning weights, every extraction site needs evidence
for commodity, activity dates and map position. Forestry/farm regions can use
broader suitability polygons. Imported rubber and nitrates should not force
European rubber plantations or invented saltpetre deposits. Avoid using
`tar_sands_mine` merely because it is available.

A site record should contain: stable ID, region ID, source URL/date, coordinates
in the validated map frame, candidate tiles/footprint constraints, commodity,
earliest date, density cap and phase weights. Region records contain polygons,
scenario fingerprint, border policy and confidence. Proposed weight is a product
of eligibility, resource suitability, regional priority, chain demand and nearby
cluster preference, normalized across **eligible sites**, not across all tiles.
Hard caps prevent a few dense regions consuming the whole industry's budget.

## Cargo dependency graph and viable phase algorithm

Use [extracted metadata](research/axis-2.3.1-extreme-classic.json) as the initial
graph, then enrich it from the production templates and live tests. Cargo labels
are stable keys; game cargo slots and translated names are resolved at runtime.
The 64 slots are not 64 universally interchangeable recipe nodes.

Represent a bipartite directed graph:

* **Industry nodes** hold local NewGRF ID, phase eligibility, model class,
  location prerequisites, optional supplies and tested production recipes.
* **Cargo nodes** link producers to consumers. Mark natural baseline sources,
  delivery-dependent processors, import/export interfaces and final sinks.
* A recipe is a weighted transformation/hyperedge, not just a list of accepted
  cargoes. Keep input alternatives and efficiency boosts separate from truly
  mandatory inputs. Preserve byproducts and shared output capacity.

AXIS primaries can work without engineering/farm supplies; these are boost
loops, not bootstrap requirements. Secondary recipes sum recent supplied-input
ratios and multiply incoming quantities by the current ratio; multiple inputs
improve output. For example a flour mill accepts grain and packaging but grain
alone can produce at reduced efficiency. This is source-supported, not measured
tonnage. The graph must not reject that useful early chain merely because a
packaging factory has not appeared. Conversely, a mathematical path with tiny
output or no customer is not a viable transport business. Sources:
[primary](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/templates/produce_primary.pynml),
[secondary](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/templates/produce_secondary.pynml).

Proposed planning algorithm, **not implemented**:

1. Load the exact manifest; resolve enabled types/cargoes and compare the live
   inventory to the source catalogue. Refuse a mismatched economy/version.
2. For each historical interval, build eligible region/type/site sets. Include
   existing industries and town consumers. Mark historical exclusion decisions
   independently from AXIS's permissive construction date gates.
3. Seed a reachable-cargo set from baseline sources and explicitly approved
   imports. Iteratively add processor outputs if at least one tested operating
   recipe has sufficient reachable supply. Preserve capacities and avoid counting
   the same tonnes at multiple customers. Stop at a fixed point.
4. Find strongly connected components for remaining cycles. Bootstrap only with
   genuine baseline production, seed stock/imports that the chosen mechanics
   actually support, or another operating recipe. A cycle does not create its
   own initial cargo. Optional supply-boost loops should not block the base graph.
5. Work backwards from final markets or downstream demand. Remove/defer planned
   sources with no viable reachable customer unless explicitly strategic/reserve.
   Distinguish all-output disposal from useful partial-output transport: some
   byproducts may be unused, but document the economic consequence.
6. Add inter-region cargo edges with tested ports/terminals or ordinary
   cross-region routes. Imports must have an **actual on-map producing industry**;
   there is no implicit external market. Ports in AXIS are fixed recipes,
   not a script-selectable import menu. Modern port outputs can be anachronistic;
   either accept that declared compromise or use a custom GRF.
7. Select the smallest candidate package that closes a useful source→processor→
   sink chain at viable throughput, with a plan for the players' available
   vehicles/refits, distance, terrain and shipping/rail links. Score packages for
   historical fit and regional specialization rather than maximizing counts.
8. Place upstream/downstream dependencies in a validated order, rechecking the
   live inventory and AXIS location restrictions. Commands are **not atomic as a
   package**, and GS cannot roll back a successful industry by removing it.
   Prefer editor-vetted packages, capped attempts and a repair/defer plan for
   partial construction. Never claim a complete chain until all required sites
   exist and are inspected.
9. Observe actual deliveries, output and transported share over several economy
   months. Record shortages and retry later; tune weights/quotas only after
   measurements. Optional imports allow regional specialization without forcing
   every region to contain every step.

Candidate 1830 smoke chains: farm grain→flour mill→food market; forest→sawmill→
furniture/hardware demand; sheep/ranch fibres→textile mill→goods consumers;
coal→coke oven plus ore/limestone→blast furnace→iron works. These are **proposals**:
check output rate, cargo refits, partial recipes and market acceptance in-game.
Do not assume early steel, aluminium, electrical parts or motor-vehicle parts
are required solely because a late-style factory accepts them.

## Milestones and release gates

| Milestone | Work and dependencies | Required evidence before advancing |
|---|---|---|
| M0 — preserved baseline | Inventory actual scenario, hash files, collect complete GRF/settings manifest. No modifications. | Correct 1830 year, 4096² dimensions, AXIS binary/version/economy, industry count/type/cargo/location dump and archive of the working files. |
| M1 — technical probe | Install the isolated probe only in a disposable test installation. Depends on M0. | Script loads under API 16; inventory correct; one selected-site coal mine builds or fails clearly; missing AXIS/timekeeping/API cases fail safely; no ordinary map altered. |
| M2 — spawning/funding/closure controls | Test funding-only + AXIS allow-spawning; separately toggle raw funding and per-instance closure protection. | Several game years without natural openings, script still builds, player secondary funding limitation explicitly demonstrated; save/reload settings; production effects measured by AXIS class. |
| M3 — 1830 chain fixture | Manually curate a new scenario copy; validate 3–4 early chains and vehicle refits. | Measured deliveries/output and real final consumers; no unsupported dependency; before/after inventory and original file hashes unchanged. Decide import/modern-cargo compromises now. |
| M4 — calibrated two-region slice | Validate region polygons and a small historical site catalogue. Add bounded additive scheduler with versioned Save/Load state. Depends on M1–M3. | Independently checked landmarks/borders, deterministic site selection, failure cooldowns, duplicate prevention after save/reload and reconciliation of closed/reused IDs. |
| M5 — early multiplayer playtest | 1830–1850, three humans, shared notifications. | Join/rejoin and server restart pass; equal information/access; no desync; script latency/memory and placement failures recorded; playable early transport choices. |
| M6 — later phases | Extend tested recipes/sites in chronological increments. | Test immediately before/after each unlock and AXIS gate (1900/1967/1978); no stranded chain after failed placement; decline policy remains honest about no forced retirement. |
| M7 — long campaign candidate | Accelerated 1830–2025 soak at 4096², plus human checks at representative eras. | Logs of industry counts, script ticks/latency, save size/reload behavior, no runaway placement, correct timekeeping, and three-player recovery tests. Acceleration is not proof of normal-speed economic balance. |
| Separate strict-history track | Custom NewGRF for date gates/early recipes, or synchronized engine APIs if AXIS must remain unchanged. | Independent versioning/licensing, new scenario, callback-route tests for random/fund/prospect/GS, save compatibility and multiplayer regression tests. No hot-swap into the working map. |

The next smallest action is **M1 inventory-only loading followed by one opt-in
coal-mine placement** in a fresh disposable 1830 test. Do not begin the full
regional scheduler before the spawning-parameter interaction is demonstrated.

## Current completion record

Completed here: primary-source investigation, full Classic metadata extraction,
proposed history/regions and dependency algorithm, isolated POC source and
static source checks. **No in-JGRPP test, Squirrel compilation, scenario editing,
construction success, campaign conversion or performance benchmark was run.**
The milestones above remain acceptance work, not completed features.
