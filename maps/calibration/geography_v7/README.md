# V7: complete map-covered town import

[Town overview](visualization/Europe_1800_V7_TOWNS_OVERVIEW.png) ·
[Regional atlas](visualization/Europe_1800_V7_REGIONAL_ATLAS.png) ·
[Offline interactive map](visualization/Europe_1800_V7_INTERACTIVE_MAP.html)
([instructions](visualization/README.md)).

The user requested all towns after the V6 regional test. V7 now processes
**every one of the 600 master records**, with no region restriction:

- **576 towns** in `Europe_1800_V7_ALL_IN_BOUNDS_TEST.json`.
- **24 towns outside the fitted map footprint**, documented individually in
  `outside_map_deferred.csv`. They are not moved to invented interior positions.
- **520 direct clear-land targets** in the optional
  `Europe_1800_V7_TERRAIN_SCREENED_TEST.json` subset.
- **56 remaining in-bounds targets** flagged in `terrain_review.csv`.
- **10 pairs below 15 tiles** and **60 pairs from 15 through 30 tiles**
  documented in `close_pairs_review.csv`.

Use the **576-town ALL_IN_BOUNDS file** to test the complete catalogue on
this heightmap. It includes London, Rostock, Troyes, Greenwich, Versailles
and Boulogne; the earlier regional-only restrictions are removed.
The 520-town file is an optional terrain-only comparison, not a density
recommendation, substitute final count or guarantee of successful founding.
Do not import both files into the same map: the 520 towns are a subset.

## Important distinction from a final spacing-approved scenario

This is the requested comprehensive **test import**. Close settlements remain
included, with individual review pending. It does not claim that the original
spacing policy has been completed: under 15 tiles normally requires an
importance decision, and 15–30 tiles requires individual review. No automated
importance ranking, silent deletion or giant-town merging is applied.
Ports, industrial centres, mining towns and regional hubs remain available
for those decisions. The importer's own founding rules may reject close
towns or choose nearby tiles. Inspect the result before saving a playable map.

The V6 empirical coastline model is reused unchanged, including its uncertainty:
held-out median normal coastline distance 2.51 pixels, 90th percentile 9.17,
maximum 86.67. These are **not true town positional accuracy measurements**.
The full set has not been independently verified town by town or imported
in a running JGRPP instance. See [V6 mapping evidence](../geography_v6/README.md).

## Corrected source joins

The master and its draft geographic CSV remain unchanged. A separate
[`europe_coordinate_overrides_v7.csv`](../../../data/geography/europe_coordinate_overrides_v7.csv)
supplies twelve explicit records with source URLs:

- The six missing draft companions: Głogów, Łowicz, Sieradz, Rawicz,
  Písek and Krems an der Donau.
- Brandenburg an der Havel's documented V6 correction.
- Greenwich's approximate settlement coordinate.
- Boulogne provisionally interpreted as **Boulogne-sur-Mer**. The source
  region, 1800 de Vries population of 12,000, and the contrasting population
  of Boulogne-Billancourt support the Channel-port interpretation. This
  remains an explicit inferred identity correction; original name and
  population are preserved, and it should be checked against the original
  historical source before release. [Supporting research](../../../data/geography/README.md).
- **Brest, France**: the draft had incorrectly matched Brest in Belarus.
- **Münster, Germany**: the draft had incorrectly matched the Irish province.
- **Freiburg im Breisgau, Germany**: the draft had matched Swiss Fribourg.

Broad region bounding-box checks now reject those obvious wrong-country
joins. They are sanity checks, not exact borders or independent verification
of every town centre. Other source geographic coordinates remain provisional.
All names, populations and city flags in both JSONs are preserved exactly
from the 600-town master. The six replacement towns are not joined by row index.

## Terrain, boundaries and audits

Every in-bounds target uses the V6 row/column geographic transformation and
the pinned JGRPP 0.73.4 float32/truncation rules. No coordinate is snapped to
land, moved away from a neighbour, clamped at an edge or substituted with
an old geographically unreliable location.

The exact target's original heightmap red channel, V1 scenario tile type
and original industry scenario tile type are recorded. A direct clear-land
target must have nonzero raw elevation and type-zero land in **both** saved
scenarios. That does not guarantee founding, correct historical centre,
flat ground, usable town-growth space or compatibility with a populated map.
The original scenarios are used as read-only terrain evidence only.

For flagged targets, `nearby_clear_land_distance_tiles` checks a ±16-tile
square in the saved scenarios. It is a terrain diagnostic, **not an emulation
of the founding search**, slope rules or guaranteed founding success. The
full file deliberately preserves water/river/harbour targets for inspection;
it does not silently relocate London or important ports. Some may fail.

All 600 entries, their source coordinates, inclusion/deferment reasons,
terrain checks and nearest-neighbour policy bands appear in
`all_600_placement_audit.csv`. All 576 towns have nearest-neighbour distances
in `all_town_nearest_neighbours.csv`. Pair distances use the established
4096-scaled continuous space; `actual_target_distance_tiles` additionally
records distances between quantized game target tiles.

The 24 boundary deferrals include Stockholm, Oslo, Bergen, Kyiv and Odesa.
Stockholm and some eastern edge towns are close enough that projection
uncertainty affects precise coverage. They still cannot safely be inserted
by clamping. Accommodating every one of the 600 towns would require a
wider geographically sourced heightmap and recalibration.
No original raster or scenario has been extended or changed.

## Reproduce

From the repository root with Python 3.10+:

```powershell
python -m pip install -r requirements-geography.txt
python scripts/expand_europe_towns.py --out scratch/v7-reproduction
python -m unittest discover -s tests -v
```

The output directory must be new. The script requires the byte-identical
source assets already preserved under `source_assets/`, validates their
hashes before and after, and reports hashes for every other input.
The V6 model is frozen rather than refitted for this expansion. Tests cover
all 600-record accounting, metadata preservation, complete inclusion of the
in-bounds towns, corrected homonyms, deferred bounds, close-pair accounting,
actual land sampling and byte-identical regenerated output.

Validation: `python -W error::ResourceWarning -m unittest discover -s tests -v`
completed with **18 passing tests**, no skips, using the preserved real assets.

## Test in OpenTTD

1. Use JGRPP **0.73.4**. Create a **fresh empty 4096×4096** Scenario Editor
   map from `source_assets/heightmaps/Europe_heightmap_original.png`, choosing
   **counter-clockwise** rotation. Keep existing NewGRF configuration and
   the intended terrain generation settings.
2. Choose **Town Generation → Load from file** and load
   `Europe_1800_V7_ALL_IN_BOUNDS_TEST.json` from this directory.
3. There are **576 requested towns**, not 576 guaranteed successful towns.
   Inspect failure signs and actual centres, particularly the 56 terrain
   review entries and 70 close pairs. Confirm landmass and coast/river context
   across every region; the full model does not replace geographic review.
4. Save only under a **new** filename, e.g. `Europe_1800_V7_ALL_TOWNS_TEST.scn`.
   Never overwrite the original industry scenario or import into an existing
   populated scenario.
5. If comparing the 520-town terrain subset, generate another fresh empty
   map with identical settings and import only that subset there.

No scenario was edited by this workflow. Actual founding counts, final
spacing decisions and historical town-centre checks remain to be recorded.
