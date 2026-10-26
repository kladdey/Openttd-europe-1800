# V6: source-backed geographic regional test

**36 corrected candidate towns; 7 regional entries deferred; 0 in-game
founding tests completed.** All 600 master entries remain accounted for in
`catalogue_projection_review.csv`. No arbitrary final count was selected.

The source heightmap and two original scenarios are now preserved under
[`source_assets/`](../../../source_assets/README.md). All original hashes
are checked before and after analysis. No scenario or NewGRF configuration
was modified. V2/V3/V4 and the complete master remain unchanged.

## Results

| Check | Result |
|---|---|
| Regional entries reviewed | 43: V4's 40 plus Greenwich, Versailles, Boulogne |
| Corrected targets retained for test | 36 |
| Corrected targets on nonzero original pixels | 36/36 retained |
| Corrected targets on clear land in both original scenarios | 36/36 retained |
| Raster landmass checks | 10 Great Britain, 8 Ireland, 18 continental Europe |
| Minimum retained continuous separation | 38.299583 tiles |
| Regional entries deferred | 7, all documented |
| Full-catalogue projection register | 600 records, including 6 unmatched draft names |
| Independently surveyed town positions | 0 |
| In-game founding tests | 0 |

The candidate preserves **master** populations and city flags. This restores
Dublin (3350/true), Paris (10000/true) and Berlin (3000/true), whose V4 values
differed from the master without a recorded justification. It does not alter
either original file. Source names, including historical spellings, are kept.

## Proven importer mapping

All code references are pinned to JGRPP 0.73.4 commit
`cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8` in the canonical repository
`JGRennison/OpenTTD-patches` (the older `JGRennison/OpenTTD` URL redirects).

- [LoadTownData](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/genworld.cpp#L423)
- [GreyscaleToMapHeights and PNG decoding](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/heightmap.cpp#L328)
- [MAPS/MAPT/MAPH serialization](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/sl/map_sl.cpp)
- [Chunk framing and gamma lengths](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/sl/saveload.cpp)

For this 4096-square raster at the same game dimensions:

```text
Clockwise heightmap: source column = game Y; source row = game X
Counter-clockwise:  source column = 4095 - game X; source row = game Y

JSON x = projected raster row / 4095
JSON y = projected raster column / 4095
```

`LoadTownData` reads proportions as float32, requires **strictly**
`0 < x,y < 1`, multiplies by `Map::MaxX/Y()` (4095, not 4096) and truncates
to unsigned tile coordinates. For clockwise it requests `(x*4095,y*4095)`;
for counter-clockwise it requests `((1-y)*4095,x*4095)`. Therefore JSON axes
stay row/column in either rotation; the importer applies the rotation.
Float32/complement/truncation can move a requested raster sample by one pixel.
The V6 audit emulates those operations, rather than rounding an idealized
endpoint transform. Both scenarios demonstrably match counter-clockwise
generation. Use counter-clockwise for this reproducible test.

The original raster has 13 non-grayscale pixels. Target PNG decoding uses
channel zero for RGBA; no silent Pillow luminance conversion is used.
Raw zero is the initial sea-level code, but scenario rivers and subsequent
terrain changes require the separate saved-tile checks. Tile type zero is
clear land; type six is water and seven is void.

## Scenario evidence and old anchor discrepancies

The read-only decoder validates the exact supplied container header/version,
framed chunk boundaries, dimension schema and 16,777,216-byte terrain arrays.
It rejects unsupported formats rather than searching arbitrary binary bytes
for a plausible `MAPT` string. It does not implement a general scenario editor.

All eight square symmetries were compared on a deterministic 8-tile grid,
excluding map edges. The horizontal reflection of raster rows into game
Y/X arrays wins in both scenarios: height correlation about **0.994** and
zero-pixel/water agreement about **98.4%**. Other symmetries correlate much
less strongly. Small coast differences and later rivers mean agreement is
not 100%. This independently establishes the saved terrain orientation.

All 40 original V4 targets lie on clear saved tiles, illustrating why land
alone cannot validate geography. The coastline model places Berlin about
458 tiles from its V4 location, Dresden about 468, Dublin about 100 and Paris
about 117. V4's Stockholm point maps to roughly 56N, 10.2E, on the same
connected raster landmass as continental Europe, consistent with Jutland
rather than Stockholm. The true Stockholm input projects just beyond the
fitted north boundary (about seven pixels); because model errors exceed
that amount, exact boundary coverage remains uncertain. It is deferred,
never clamped or moved to another landmass.

This new full-raster evidence justifies changing anchor-derived positions
in a **separate candidate**. The original accepted V2 anchors remain intact.

## Geographic model and its limits

Source projection metadata is absent. V6 tests a geographical hypothesis
against Natural Earth's independently sourced 1:50m coastline, rather than
fitting any of the old town coordinates or the five V2 anchors.

The original raster's ocean-connected zero-elevation boundary is extracted
at full resolution. Dense coastline vertices are thinned into 0.05-degree
longitude × 1/30-degree latitude bins. Fit samples cover longitude (-11,25),
latitude (35.5,58.5). Entire 2-degree cells satisfying
`(floor(lon/2)+2*floor(lat/2)) % 4 == 0` are held out, so training and holdout
cells never overlap. The remaining 2646 samples fit the model; 946 samples
in held-out cells evaluate it. Model families and initial parameters are
fixed in the script; no town coordinates are used for tuning.

The simplest well-performing fit is:

```text
column = 104.4226344619 * longitude + 1379.7176323207
row    = -164.0981652718 * latitude + 9729.1427463990
```

This is an empirical affine mapping of geographic degrees, consistent with
an approximately equirectangular crop. It is **not recovered source CRS
metadata**. Its approximate footprint is 13.213W–26.003E, 34.334N–59.289N;
those numbers are model estimates, not exact surveyed bounds.

| Model | Held-out median coast distance | 90th percentile | Maximum |
|---|---:|---:|---:|
| Axis-aligned affine | 2.51 px | 9.17 px | 86.67 px |
| General affine | 2.47 px | 9.27 px | 86.46 px |
| Mercator with independent axis scaling | 13.51 px | 53.28 px | 200 px penalty |

The objective is distance to the nearest raster coastline, using robust
least squares. These are **coast-normal residuals**, which can be small
despite along-coast displacement; they are not 2D town positional errors.
Natural Earth is generalized, coast/lowland details differ, and held-out
cells share the same source dataset. Model-family comparison also uses the
holdout results, so they are not an untouched final release test set.
Independent named landmark checks are still required before release.
The raster overlay is provided for visual review, not as proof of precision.

Controls near the edges are not fitted; towns within 90 pixels of the
fitted boundary require manual review. No global extrapolation is accepted
as release geography. The full 600-row projected register is diagnostic
only: 24 positions are outside fitted bounds and six have no geographic
companion row. A full Europe import is withheld until regional testing and
source-coordinate review establish credibility. The crop itself also limits
Scandinavian and eastern coverage; spacing cannot repair missing geography.

## Deferred towns and historical review

| Town | Reason and required next check |
|---|---|
| London | Corrected target is water in both scenarios, likely the Thames; inspect a historically appropriate bank and founding search. Do not use nearest-land snapping. |
| Rostock | Corrected target is water; inspect the Warnow/harbour context and preserve its port function. |
| Troyes | Corrected target is water; inspect river channels and local centre position. |
| Stockholm | Fitted location lies near/outside north edge; verify map coverage independently. |
| Greenwich | Prior individual spacing review, about 20.8 tiles from London under the draft coordinates; source centre also needs correction. |
| Versailles | Prior Paris crowding review; court significance merits an explicit decision after correction. |
| Boulogne | Strong historical evidence favours the Channel port, but draft coordinates describe the Paris suburb. Resolve the source identity join first. |

All three water-target towns remain in the catalogue and projection report.
The importer can search around a target, so a water target does not prove
founding would fail. Deferral here is conservative pending geographic and
in-game review. It does not erase an important city or port. The regional
projection report also retains the current provisional positions of deferred
satellites to make their earlier spacing decisions traceable.

No retained pair is within 30 tiles. Distances follow the existing 4096×4096
continuous normalized-space policy; actual quantized target distances differ
slightly. Future pairs below 15 normally need an importance decision, and
15–30 need individual historic/transport review. The script stops if a new
retained pair requires such a decision; it never chooses an automatic winner.

## Reproduce and test

Use Python 3.10+ from the repository root:

```powershell
python -m pip install -r requirements-geography.txt
python scripts/calibrate_heightmap.py --assets source_assets --out scratch/v6-reproduction
python -m unittest discover -s tests -v
```

The output directory must not exist. The source hashes must match.
NumPy 2.3.5 / SciPy 1.17.0 produced this snapshot. Minor optimizer variations
across versions are possible; review residuals and target-tile changes, rather
than treating many decimal places as geographic accuracy. The test suite
covers the **actual** source raster and both saved scenario terrain arrays,
plus bounds, names, master metadata, spacing, explicit importer float32
arithmetic, spatially disjoint holdouts and malformed chunk rejection.

The earlier `scripts/geography.py fit/terrain` commands remain generic V5
diagnostics; their example endpoint mapping is not the target-version mapping.
Use `calibrate_heightmap.py` and `scenario_geography.py` for V6 reproduction.

## Exact OpenTTD test procedure

1. Keep the original scenarios backed up. Use JGRPP **0.73.4**, with the
   project's existing NewGRF configuration unchanged.
2. Create a **fresh empty** 4096×4096 Scenario Editor map from
   `source_assets/heightmaps/Europe_heightmap_original.png`. Choose
   **counter-clockwise** heightmap rotation. Keep the intended height and
   generation settings, and record them; those settings were not fully
   recovered by this read-only terrain audit.
3. In **Town Generation → Load from file**, choose
   `maps/calibration/geography_v6/Europe_1800_V6_REGIONAL_GEOGRAPHIC_TEST.json`.
   Do not load it into an existing populated or playable industry scenario.
4. Expect **36 imported towns** if all founding attempts succeed. Inspect
   failure signs, terrain conflicts and town centres; the importer can
   search up to 16 tiles around targets. Record actual centres and failures.
5. Inspect every region against the overlay and CSV, especially corrected
   Berlin/Brandenburg, Baltic ports, the Irish coast and river cities. Check
   that town growth leaves room for routes. Review deferred London, Rostock
   and Troyes separately before adding any bank-adjusted positions.
6. Save only as a new scenario, e.g. `Europe_1800_V6_GEOGRAPHY_TEST.scn`.
   Do not overwrite either preserved original or the working scenario.

Successful import proves founding feasibility, not historical accuracy.
Record independent named coastal/inland landmarks before promoting this
experimental file or expanding into a complete release dataset.
