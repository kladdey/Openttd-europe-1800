# AXIS industry matrix — 2.3.1, Extreme Classic

Extracted 2026-10-28 from release commit
`11c8353ccf7444b143e57080b1aa2b5e38839a23`: **91 enabled industry
types, 64 cargo slots**. These are industry *types*, not the scenario's reported
1,387 instances. Extreme Classic is internal economy **BASIC_TEMPERATE**, numeric
economy 0 / first UI selection. STEELTOWN is **Steel City**, not Classic.
See [economy source](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/economies/basic_temperate.py)
and [English names](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/lang/english.lng).

## Reading the evidence

The table uses **source identifiers and four-character cargo labels**, not
invented English display names. Local IDs are scoped to AXIS GRFID `4A4B8808`;
resolve them through `GSIndustryType.ResolveNewGRFID`, never treat them as
game-local type IDs. Each row links its definition. Inherited defaults and
economy overrides were evaluated with upstream Python model methods, not scraped
from screenshots. [Machine-readable extraction](research/axis-2.3.1-extreme-classic.json)
includes class, ratios/multipliers, dates, probability and source paths.

Reproduce using Python standard library, a trusted AXIS checkout pinned to the
release commit, and:

```text
python scripts/extract_axis_industry_matrix.py PATH_TO_AXIS docs/research/axis-2.3.1-extreme-classic.json
```

The extractor runs trusted upstream Python definitions with renderer/message
stubs; it does not render or compile a NewGRF. Facts are **source verified**,
not a binary/runtime audit. Production numbers are retained in JSON: primary
multipliers and secondary output ratios are different units, so the table
deliberately lists labels only.

Inputs mean **accepted**, not all simultaneously mandatory. Extractive industries
accept `ENSP`, organic ones `FMSP` as optional boosts; port-type primary producers
also have baseline output. Secondary delivery recipes can process partial inputs
at lower efficiency. See [industry model](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industry.py)
and [secondary recipe template](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/templates/produce_secondary.pynml).
An empty output is a sink; an empty input is a source. Town/vehicle sinks must be
included separately in chain planning.

Selected label traps from upstream cargo files/English strings:
`POWR` = **electrical parts**, not electricity; `MNSP` = **packaging**;
`RFPR` = **refined oil**, despite the Python cargo ID `chemicals`;
`PETR` = petroleum fuels; `COAT` = paints/coatings;
`AORE` = bauxite; `IRON` = pig iron; `STEL` = steel;
`WDPR` = lumber; `WOOD` = logs; `FICR` = plant fibres;
`VPTS` = vehicle parts; `ENSP`/`FMSP` = engineering/farm supplies.
See [cargo sources](https://github.com/EmperorJake/AXIS/tree/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/cargos).
Do not import FIRS label semantics without checking AXIS.

## Proposed timing (policy, not AXIS behavior)

P1 = present at 1830 / expansion 1830–1850; P2 = 1850–1880;
P3 = 1880–1914; P4 = 1914–1945; P5 = 1945–1970;
P6 = 1970–2000; P7 = 2000–2025. Existing P1 activities often predate 1830.
These broad bands are **proposals needing regional/site historical review**;
they are not exact invention dates or implemented unlocks. Every recipe needs
the dependency review in the roadmap before accepting that band.

`P1*` flags a gameplay proxy/concession with modern cargoes/graphics: an early
machine shop can accept electrical/vehicle parts, and ports can produce advanced
goods. Such sites must not be described as historically literal. Exclude/import
marks types inappropriate as ordinary European resources; no assertion is made
that every European location lacks those minerals. There is no obligation to
place all 91 types.

The **AXIS gate** column records actual source years: `none` means defaults 0
through `max_game_date`, not an 1830 policy date. Most types are available well
before the proposed phase. Graphics changes are not gates. The table omits types
disabled for Classic, even if present in other AXIS economies.

| Local ID | AXIS source identifier | Accepted cargo labels | Produced cargo labels | AXIS gate | Proposed band |
|---|---|---|---|---|---|
| 0 | [coal_mine](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/coal_mine.py) | ENSP | COAL | none | P1 |
| 4 | [iron_ore_mine](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/iron_ore_mine.py) | ENSP | IORE | none | P1 |
| 5 | [peatlands](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/peatlands.py) | ENSP | BIOM | none | P1 |
| 7 | [blast_furnace](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/blast_furnace.py) | IORE, COKE, LIME | IRON, SLAG | none | P1 |
| 8 | [aluminium_plant](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/aluminium_plant.py) | AORE, SCMT, COKE, ACID | ALUM, SLAG | none | P3 |
| 9 | [metal_workshop](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/metal_workshop.py) | STEL, ALUM, COAT | MPAR, MNSP | none | P3 |
| 10 | [quarry](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/quarry.py) | ENSP | SAND, LIME | none | P1 |
| 11 | [forest](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/forest.py) | FMSP | WOOD | none | P1 |
| 12 | [sawmill](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/sawmill.py) | WOOD | WDPR | none | P1 |
| 13 | [furniture_factory](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/furniture_factory.py) | WDPR, TEXT, MPAR, GLAS | GOOD | none | P1 |
| 15 | [oil_wells](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/oil_wells.py) | ENSP | OIL_ | none | P3 |
| 16 | [oil_rig](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/oil_rig.py) | ENSP | OIL_, PASS | from 1967 | P5 |
| 17 | [oil_refinery](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/oil_refinery.py) | OIL_ | RFPR, PETR, CTAR | none | P3 |
| 18 | [plastics_plant](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/plastics_plant.py) | PLAS, MPAR | MNSP | from 1900 | P4 |
| 19 | [fish_farm](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/fish_farm.py) | FMSP | FISH | none | P5 |
| 20 | [dredging_site](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/dredging_site.py) | ENSP | SAND | none | P1 |
| 21 | [iron_works](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/iron_works.py) | IRON, ALUM, SAND | MPAR | none | P1 |
| 22 | [glass_works](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/glass_works.py) | SAND, SASH, QLME | GLAS, MNSP | none | P1 |
| 23 | [recycling_plant](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/recycling_plant.py) | RCYC | PLAS | from 1978 | P6 |
| 24 | [recycling_depot](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/recycling_depot.py) | — | RCYC | none | P1* |
| 25 | [junk_yard](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/junk_yard.py) | RCYC | SCMT | none | P1* |
| 26 | [arable_farm](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/arable_farm.py) | FMSP | GRAI, SGBT | none | P1 |
| 27 | [sheep_farm](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/sheep_farm.py) | FMSP | LVST, FICR | none | P1 |
| 28 | [dairy_farm](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/dairy_farm.py) | FMSP | LVST, MILK | none | P1 |
| 29 | [farm](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/farm.py) | FMSP | OLSD, LVST | none | P1 |
| 30 | [fruit_plantation](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/fruit_plantation.py) | FMSP | FRUT, OLSD | none | P1 |
| 32 | [fishing_grounds](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/fishing_grounds.py) | — | FISH | none | P1 |
| 33 | [vehicle_distributor](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/vehicle_distributor.py) | VEHI | — | none | P4 |
| 34 | [flour_mill](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/flour_mill.py) | GRAI, MNSP | FOOD, EOIL | none | P1 |
| 35 | [brewery](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/brewery.py) | GRAI, FRUT, MNSP | BEER, BIOM | none | P1 |
| 36 | [dairy](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/dairy.py) | MILK, MNSP | FOOD, EOIL | none | P1 |
| 37 | [stockyard](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/stockyard.py) | LVST, MNSP | FOOD | none | P1 |
| 38 | [machine_shop](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/machine_shop.py) | POWR, VPTS, MPAR, TYRE, GLAS | GOOD, ENSP, FMSP | from 1790 | P1* |
| 39 | [port](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/port.py) | BDMT, FOOD, BEER, PAPR | ENSP, FMSP, POWR, MPAR | none | P1* |
| 40 | [ammonia_plant](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/ammonia_plant.py) | RFPR, NITR, BIOM, ACID | FERT, BOOM | none | P3 |
| 41 | [lumber_yard](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/lumber_yard.py) | WDPR, MPAR, COAT | BDMT, MNSP | none | P1 |
| 42 | [textile_mill](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/textile_mill.py) | FICR, COAT | TEXT, GOOD | none | P1 |
| 43 | [vineyard](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/vineyard.py) | FMSP | FRUT | none | P1 |
| 44 | [clay_pit](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/clay_pit.py) | ENSP | CLAY | none | P1 |
| 45 | [brick_works](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/brick_works.py) | CLAY, SAND, COAL | BDMT | none | P1 |
| 46 | [wharf](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/wharf.py) | COPR, BOOM, GOOD, CMNT | MNSP, RAMT, ENSP, FMSP | none | P1* |
| 47 | [orchard_piggery](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/orchard_piggery.py) | FMSP | FRUT, LVST | none | P1 |
| 48 | [ranch](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/ranch.py) | FMSP | FICR, OLSD | none | P1 |
| 51 | [bulk_terminal](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/bulk_terminal.py) | ZINC, FERT, VEHI, STEL | IORE, COAL, AORE, CORE | none | P6 |
| 52 | [trading_post](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/trading_post.py) | ENSP | SCMT | none | P1* |
| 53 | [rubber_plantation](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/rubber_plantation.py) | FMSP | RUBR | none | Exclude/import |
| 54 | [limestone_mine](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/limestone_mine.py) | ENSP | LIME | none | P1 |
| 56 | [food_processor](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/food_processor.py) | FRUT, FISH, EOIL, MNSP, SALT | FOOD | none | P2 |
| 57 | [hardware_store](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/hardware_store.py) | GOOD, BDMT | — | none | P1 |
| 59 | [food_market](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/food_market.py) | FOOD, FRUT, BEER | — | none | P1 |
| 60 | [petrol_pump](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/petrol_pump.py) | FOOD, GOOD, PETR | — | none | P3 |
| 61 | [general_store](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/general_store.py) | FOOD, GOOD, BEER | — | none | P1 |
| 62 | [assembly_plant](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/assembly_plant.py) | STEL, GLAS, VPTS, MPAR, TYRE, COAT | VEHI | none | P4 |
| 64 | [copper_mine](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/copper_mine.py) | ENSP | CORE | none | P2 |
| 65 | [nitrate_mine](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/nitrate_mine.py) | ENSP | NITR | none | Exclude/import |
| 66 | [power_plant](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/power_plant.py) | COAL, PETR, BIOM | — | none | P3 |
| 67 | [copper_refinery](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/copper_refinery.py) | CORE, SCMT, ACID | COPR, SLAG | none | P2 |
| 68 | [cement_plant](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/cement_plant.py) | CMNT, COKE, SAND, LIME | BDMT, QLME | none | P2 |
| 69 | [supply_yard](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/supply_yard.py) | VEHI, PETR, BOOM | ENSP | none | P4 |
| 70 | [tyre_plant](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/tyre_plant.py) | RUBR, MPAR, SULP | TYRE, GOOD | none | P3 |
| 71 | [pyrite_mine](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/pyrite_mine.py) | ENSP | PORE | none | P2 |
| 72 | [pyrite_smelter](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/pyrite_smelter.py) | PORE, COKE, ACID | ZINC, RAMT | none | P2 |
| 73 | [paper_mill](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/paper_mill.py) | CLAY, WOOD, SULP | PAPR, MNSP | none | P2 |
| 74 | [liquids_terminal](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/liquids_terminal.py) | CHLO, RUBR, EOIL, PETR | OIL_, ACID, RFPR, COAT | none | P6 |
| 77 | [basic_oxygen_furnace](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/basic_oxygen_furnace.py) | IRON, QLME, RAMT | STEL, SLAG | none | P5 |
| 78 | [coke_oven](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/coke_oven.py) | COAL | COKE, SULP | none | P1 |
| 79 | [electric_arc_furnace](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/electric_arc_furnace.py) | SCMT, QLME | STEL, SLAG | none | P3 |
| 80 | [slag_grinding_plant](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/slag_grinding_plant.py) | SLAG | CMNT, FERT | none | P5 |
| 82 | [biorefinery](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/biorefinery.py) | SGBT, BIOM, OLSD | RFPR, PETR, PLAS | none | P7 |
| 83 | [electrical_works](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/electrical_works.py) | COPR, TYRE, PLAS, RAMT | POWR | none | P3 |
| 86 | [soda_ash_mine](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/soda_ash_mine.py) | ENSP | SASH, SALT | none | P1 |
| 87 | [chlor_alkali_plant](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/chlor_alkali_plant.py) | SALT | ACID, CHLO | none | P3 |
| 88 | [component_factory](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/component_factory.py) | MPAR, PLAS, TEXT, POWR | VPTS | none | P4 |
| 90 | [fishing_harbour](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/fishing_harbour.py) | FISH, MNSP | FOOD | none | P1 |
| 92 | [fischer_tropsch_plant](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/fischer_tropsch_plant.py) | COAL | RFPR, CTAR | none | P4 |
| 93 | [printing_plant](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/printing_plant.py) | PAPR, COAT | GOOD, MAIL | none | P1 |
| 99 | [lime_kiln](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/lime_kiln.py) | LIME, PETR | QLME | none | P1 |
| 100 | [appliance_factory](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/appliance_factory.py) | MPAR, POWR, GLAS, PLAS | GOOD | none | P5 |
| 102 | [paint_factory](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/paint_factory.py) | RFPR, QLME, PLAS, MNSP | COAT, GOOD | none | P4 |
| 103 | [sheet_and_pipe_mill](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/sheet_and_pipe_mill.py) | STEL, ZINC, ACID | MPAR, BDMT | none | P2 |
| 104 | [solvay_plant](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/solvay_plant.py) | SALT, LIME, RFPR | SASH | none | P2 |
| 109 | [sulphuric_acid_plant](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/sulphuric_acid_plant.py) | SULP, NITR, RFPR | ACID | none | P2 |
| 111 | [polyethylene_plant](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/polyethylene_plant.py) | RFPR, CHLO, ACID | PLAS, RUBR, FICR | from 1900 | P4 |
| 112 | [ethylene_cracker](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/ethylene_cracker.py) | RFPR, CTAR | PETR, COKE, SULP | none | P5 |
| 113 | [sugar_refinery](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/sugar_refinery.py) | MNSP, SGBT | FOOD, BIOM | none | P2 |
| 115 | [bauxite_mine](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/bauxite_mine.py) | ENSP | AORE | none | P3 |
| 116 | [tar_sands_mine](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/tar_sands_mine.py) | ENSP | SAND, CTAR | none | Exclude/import |
| 117 | [salt_evaporator](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/salt_evaporator.py) | ENSP | SALT | none | P1 |
| 119 | [seaweed_farm](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/seaweed_farm.py) | FMSP | BIOM | none | P6 |
| 120 | [farm_supply_yard](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/farm_supply_yard.py) | VEHI, PETR, FERT | FMSP | none | P4 |
| 122 | [edible_oil_refinery](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industries/edible_oil_refinery.py) | OLSD | EOIL, BIOM | none | P1 |
