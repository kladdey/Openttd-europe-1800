# Whole-map coverage audit — V12, 568 towns

This checks the original heightmap against the complete **568-town V12 import**.
It identifies research priorities without adding towns or changing any import.
The user's current saved scenario has not been supplied for direct decoding;
locations here are the planned importer targets, not independently observed town tiles.

## Where further filling is most justified

| Area | Places to research first | Why it stands out |
|---|---|---|
| Jutland and Funen | Aarhus, Odense, Ribe, Aalborg; then Viborg, Randers and Kolding | The existing Danish coverage concentrates on Copenhagen; these are missing historic port/market/episcopal centres. Randers and Viborg are about 281 and 270 tiles from the nearest current target. |
| Southern Norway | Stavanger, Kristiansand, Arendal | No Norwegian towns are imported within this map's southern coastal strip. Nominal distances to current targets are about 656, 413 and 332 tiles. Oslo/Bergen remain outside the map, not candidates to clamp to an edge. |
| Wales | Swansea, Cardiff, Carmarthen, Merthyr Tydfil | The current catalogue contains no Welsh towns. Swansea/Merthyr offer historically relevant metalworking connections; Cardiff should begin as its smaller historic town, without assuming later coal-dock growth. |
| Northern Spain | Oviedo, León, Santander, A Coruña, Vigo; then Pamplona and Logroño | The existing Spanish set is much stronger in Andalusia. Oviedo is about 257 tiles from the nearest current target; other missing northern hubs offer coherent regional and coastal routes. |
| Portugal | Faro, Lagos, Braga, Viseu and Bragança; Setúbal/Guimarães individually | Only Coimbra, Elvas, Évora, Lisbon and Porto are represented. The Algarve and northeast are particularly weak; Lagos is about 253 tiles from the nearest current target. |
| Corsica | Ajaccio and Bastia | The island has no imported towns. Both have documented pre-1800 Genoese port/citadel contexts and are roughly 197 and 166 tiles from current targets across the sea. |
| Sardinia | Review Cagliari first; research Oristano, Iglesias and Alghero | Sassari is the only imported town. Cagliari is an existing hold, not a missing source record. Regional administrative/mining/port roles justify selective coverage. |
| Crete and the Ionian route | Chania, Heraklion, Corfu town | Crete has no towns in the current import. Chania and Heraklion are about 405 and 457 tiles from the nearest existing target. These are historical-port research leads, not ready founding sites. |
| Western Belarus, within the eastern crop | Grodno, Brest (Belarus), Lida | The mapped western strip lacks these regional centres. Brest must be qualified to distinguish it from the existing French Brest. |
| Southern mainland Italy | Salerno, Cosenza, Catanzaro, Potenza, L'Aquila | The Italian catalogue is stronger in the north and Sicily than in several mainland southern/interior corridors. Review these regional hubs alongside the existing Naples hold. |

Geographic labels in this table are for orientation, **not claims about 1800
political boundaries**. Recommendations concern historical roles and regional
connections, not a fixed number of towns per country.

## Secondary, selective improvements

- **Ireland:** Derry, Sligo, Tralee and Wexford could strengthen northern, western
  and southeastern links beyond the eight current towns.
- **Scotland:** Stirling and Dumfries are regional-centre leads; Oban and Stornoway
  are selective western/sea-route leads. Do not fill the Highlands uniformly.
- **Swiss/Alpine corridor:** Lausanne, Lucerne, St. Gallen and Sion warrant review
  as historic lake, market or episcopal centres; mountain corridors need terrain
  and infrastructure-space checks.
- **North Africa:** Tlemcen, Constantine, Kairouan and Sousse could complement the
  seven existing coastal additions. Do not populate the whole southern mountain/
  rural strip simply because the distance map shows large gaps.

Mainland France, the Benelux area, much of central England, northern Italy and
Sicily already have substantially closer town spacing. Extra settlements there
should address a specific historical or transport omission rather than blank colour.
The Alps, Highlands, interior mountains and clipped map margins should retain
appropriate sparse space. Missing towns beyond the crop remain out of scope.

## Recover existing deferrals before inventing replacements

The combined review accounts for **83 distinct known deferrals**: 63 from the
original 600-town catalogue and 20 additional proposals from the coverage review.
Palma is counted once. These include outside-map, spacing, identity, terrain and
registration cases; they are not all candidates for reinstatement.

The largest gaps around existing held records include:

| Existing held town | Nearest current target distance (tiles) |
|---|---:|
| Cagliari | 257.099 |
| Oran | 248.485 |
| Annaba | 227.607 |
| Visby | 202.714 |
| Ibiza | 194.517 |
| Napoli | 170.602 |

These important places deserve recovery review, not deletion or substitution with
less important neighbours. Their historic-site and geographic/terrain holds remain
in force. The supplied terrain arrays may differ from the user's fresh 568-town
save; that difference could be investigated through a later save-based or in-game
review. This audit alone lifts no holds.

## Map, screening method and limits

[Coverage gap map](coverage_gap_map.png): white dots are current V12 targets;
yellow rings/IDs identify the research queue; red squares are mapped deferrals.
Green means closer to an existing town; orange/purple means farther away.

The generator:

1. Verifies the full import, original heightmap/scenario and deferral input hashes.
2. Reconstructs exact float32/truncated CCW importer targets and expresses them in
   the source PNG's north-up column/row frame.
3. Samples the raster every **8 source pixels** and measures Euclidean distance to
   all 568 target centres. The sampled mask is **red-channel elevation > 0**,
   not a comprehensive land/water or historic settlement map.
4. Summarizes 128×128-source-pixel cells: **735** cells contain sampled nonzero
   elevation. Regional summaries use **21 approximate overlapping rectangles**;
   these include neighbouring shores/borders and **are not country counts**.
5. Projects **62 research leads** from cited published city-reference coordinates
   without moving them to clear terrain. It records nearest towns, nominal spacing,
   source/saved terrain at the point and local nonzero elevation range in raw units.

About **26.88%** of nonzero source samples lie over 100 tiles from a current target,
and **6.98%** lie over 200 tiles away. These are coarse screening statistics;
100/200 are visualization bands, **not required catchment radii or instructions
to add towns**. The mask misses zero-elevation land and can include raised lake
basins. Pixel colours contain no information about historical rural population,
roads, sailing access, economic demand or suitability for founding.

Distances cross seas, rivers and mountains. An island can appear near a town on
another landmass without having local settlement coverage. A large inland distance
can be historically appropriate. Local relief is a raw source-elevation range,
not metres or a validated slope/founding metric. These limitations are why the
research priorities use geography and historical roles in addition to distance.

The queue contains **61 gap-research leads and one close-neighbour case**:
**Helsingør is only 9.220 tiles from Helsingborg** across the strait. It needs an
individual importance/landmass exception review, not automatic inclusion. The
proposed **Braga–Guimarães** pair is **22.804 nominal tiles** apart and also requires
joint review before both could be added. No hypothetical pair is approved here.

Published city-reference points may be coarse, modern or on unsuitable terrain.
Source/saved clearance in the CSV is a diagnostic, not a historic founding-site
approval. Per-site pre-1800 existence, appropriate footprint, coastal/bank context,
land placement, spacing and starting population still need verification. No import
JSON or gameplay population proposal is generated by this audit.

## Evidence and files

- [Research queue with per-point coordinate/history links](candidate_research_queue.csv).
- [Existing deferrals and recovery distances](existing_deferral_recovery.csv).
- [735-cell screen](coverage_grid.csv), [regional study windows](regional_windows.csv),
  [proposed close pairs](candidate_pair_reviews.csv), [summary/hashes](summary.json).
- [Source manifest and explicit limitations](../../../data/geography/coverage_gap_research_v1.json).

Institutional context sources support the regional examples, not every proposed
site. Particularly useful references include:

- [Ribe trading-centre history, University of Copenhagen](https://names.ku.dk/selectednames/ribe),
  and [Aarhus municipal historical atlas](https://webgis.aarhus.dk/kommuneatlas/byhistoriske_hovedtraek/Byhistoriske_hovedtraek_12.htm).
- [Industrial Wales, Cadw](https://cadw.gov.wales/learn/sites-through-centuries/industrial-wales).
- [Bastia citadel](https://www.visit-corsica.com/en/Mon-sejour/Patrimoine-culturel/Tout-le-patrimoine-culturel/LA-CITADELLE-DE-BASTIA)
  and [Ajaccio citadel](https://www.visit-corsica.com/en/Mon-sejour/Patrimoine-culturel/Tout-le-patrimoine-culturel/CITADELLE-D-AJACCIO), official Corsican tourism.
- [Oristano](https://www.sardegnaturismo.it/it/esplora/oristano) and
  [Iglesias](https://www.sardegnaturismo.it/en/explore/iglesias), official Sardinian tourism.
- [Oviedo](https://www.spain.info/en/destination/oviedo/), Spain's official tourism site;
  [Braga](https://visitbraga.travel/en/braga-cidade/), the local tourism site.

Coordinate facts were read from the linked city articles. Broad historical-role
notes are research hypotheses, not completed verification of every city in the queue.
The 568-town import, original catalogue, previous experiments, `.scn` assets and
NewGRF setup are unchanged. No new in-game test or saved-map decode was performed.

## Reproduction

```powershell
python -m pip install -r requirements-visualization.txt
python scripts/audit_coverage_gaps.py --out scratch/coverage-gap-audit
python -W error::ResourceWarning -m unittest discover -s tests -v
```

Use a new output directory. Generation is offline and refuses to overwrite an
existing directory. Five new regression tests check analytical distances, sampled
masks, same-name/different-place identity, duplicate deferral accounting, close
proposals, research-only output and deterministic preservation. The full suite
passes **86 Python tests**.
