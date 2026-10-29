# Historical industrial geography, 1830 candidate

The delivered 0.3.0 candidate places **467 industries of 40 types** across the
617-town Europe map. It is an implemented playtest candidate, not a census of
individual 1830 factories. Named mining/iron districts use historical sources;
farms, mills, salteries and trade sites often represent inferred regional
activity. Those distinctions are retained in the placement datasets.

## Geographic method

The immutable Phase 6A source has SHA256
`6c7a7b8ccbf72a744102ab06df755d119d692ca435e397e1bbbac3267ee1b60d`.
The calibrated projection from Phase 6A was reused, with inverse-distance
residuals from up to four nearby real town anchors, bounded to eight tiles per
axis. Actual terrain/water arrays filter candidate sites. Named inland
district searches are bounded to 12–18 Manhattan tiles, maritime districts to
38. No unrestricted nearest-land snapping, terrain flattening or cross-region
fallback is used. Tile coordinates, anchor names, source links, actual nearby
towns and each command's outcome are recorded.

The 668-entry 0.2.0 plan is retained separately. Forty copper/salt/export
requests were added, then failed coastal sites retried against sloping shore
warehouse positions in the actual layouts. The resulting 708 distinct requests
yielded 467 placements. A failed request is not an industry in the scenario.

## Implemented regional allocation

| Region code | Geographic grouping | Industries |
| --- | --- | ---: |
| GB | British Isles | 118 |
| FR | France | 53 |
| BX | Belgium / Netherlands | 29 |
| DE | German states | 52 |
| CE | Central Europe / Austrian and Bohemian districts | 30 |
| PL | Polish / Silesian districts | 45 |
| BA | Baltic and eastern hubs | 14 |
| SC | Scandinavia represented within map bounds | 33 |
| IB | Iberia | 42 |
| IT | Italian states | 26 |
| SE | Southeastern / Mediterranean hubs | 25 |
| **Total** | | **467** |

These are placement groupings, not modern national statistical totals. Some
automatically grouped coastal sites use coarse regional rules. Consult the
locality and coordinates before interpreting a code as a historical border.

| Sector grouping | Industries |
| --- | ---: |
| Farms, ranches, vineyards and orchards | 120 |
| Forests | 15 |
| Mines, quarries and clay pits | 44 |
| Food, drink and curing processors | 109 |
| Metalworking and machinery | 14 |
| Wood products, paper, printing and textiles | 83 |
| Coke, building materials and glass | 32 |
| Fishing grounds and fishing harbours | 25 |
| Ports and wharves | 25 |

The starting count is deliberately below the old approximately 1,387-industry
map. The allocation provides regional chains and export destinations rather
than six industries in every town. It has not been economically optimized to
equalize regions or calibrated from three-company demand forecasts.

## Historical anchors and exclusions

Britain is the largest initial concentration: South Wales, Lancashire,
Yorkshire, Tyneside/Durham, the Midlands, Scotland and the copper districts.
Coalbrookdale's coke iron tradition is documented by
[English Heritage](https://www.english-heritage.org.uk/visit/places/iron-bridge/history).
Blaenavon's earlier workings must be distinguished from the later Big Pit;
the [historic landscape record](https://heneb.org.uk/archive/ggat/cadw/historic_landscape/blaenavon/english/Blaenavon_005.htm)
supports pre-1830 activity. The [New Lanark listing](https://whc.unesco.org/en/list/429)
supports Scottish manufacturing.

Belgian districts use [Grand-Hornu's recorded industrial history](https://connaitrelawallonie.wallonie.be/grand-hornu)
and the [Belgian State Archives' Seraing record](https://www.arch.be/index.php?a=2012-12-14-plus-de-220-m-d-archives-d-entreprises-siderurgiques-liegeoises-ouvertes-a-la-recherche&l=fr&m=actualites&r=toutes-les-actualites).
The Ruhr uses [Nachtigall's early workings](https://zeche-nachtigall.lwl.org/en/history/),
not modern deep-pit concentrations. Upper Silesia and Ostrava are represented
by early coal/iron districts. The Vítkovice coke blast furnace is excluded:
[the Rothschild Archive chronology](https://www.rothschildarchive.org/collections/archivists_choice/august_2016_acquisition_of_the_witkowitz_ironworks_1842)
places it after the scenario opening.

Forestry, agriculture, regional processing and maritime trade supply lower
industrial-density regions. [Norsk Folkemuseum](https://norskfolkemuseum.no/en/waterpower)
supports Norwegian water-powered trades; [Gdansk's maritime museum](https://nmm.pl/en/national-martitme-musuem/historia-spichlerzy-na-olowiance/)
documents grain commerce. [Catalonia's archives](https://patrimoni.gencat.cat/en/catalunyapaisdarxius/digital-resource/resource/perspective/industrialization-and-trade-in-catalonia-lights-and-shadows-of-an-engine-of-change/)
support textile/trade context without backdating the later steam-mill boom.
Southern Swedish districts are used within the map; Falun, Bergslagen and other
out-of-bounds northern sites are not relocated southwards.

Copper and salt have a separate [source and implementation report](COPPER_SALT_1830_VALIDATION.md).
The economy includes Swansea smelting, Dolcoath/Parys ore and Wieliczka/Bochnia
salt. Salt curing is represented regionally. No petroleum industry or modern
copper/slag processor was introduced.

## Historical compromises requiring review

The inherited 0.2.0 placement draft contains four **Soda Ash Mine 86** sites
associated with glass-support clusters in England, central Germany, Bohemia
and the Venetian region. Their natural-mineral exploitation at those sites
in 1830 is **UNVERIFIED**. A glass-making district is not evidence of a local
trona/soda-ash mine. They were retained to preserve all completed placements,
not endorsed as established historical facts. A historical release needs a
specific correction decision; their SALT by-product is not the validated salt
chain's upstream justification.

Other compromises include generic FIRS/AXIS machinery/material labels, reused
modern-looking graphics and regional farm/trade proxies rather than researched
individual businesses. Original recipes were preserved. These limit historical
certification even where game transport is functional.

Primary inputs: [regional plan](../data/geography/industrial_1830_regions.json),
[mineral districts](../data/geography/industrial_1830_minerals.json),
[copper/salt additions](../data/geography/industrial_copper_salt_1830.json).
Outputs: [complete location plan](research/historical_industry_locations.csv),
[actual placement results](research/industry_placement_results.csv),
[regional/type counts](research/regional_industry_distribution.csv).
