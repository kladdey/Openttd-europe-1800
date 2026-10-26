# V9 — frozen-model landmark checks and town evidence map

V9 adds evidence and diagnostics. **The proposed import remains V8's 564-town
candidate. No coordinates, populations, scenarios or NewGRFs changed in V9.**
All 600 master entries remain accounted for; 36 are deferred (24 outside the
fitted raster, 11 spacing recommendations and one unresolved combined identity).
No OpenTTD session or founding test was run.

- [Open the offline interactive evidence map](visualization/evidence_map.html)
  (download the HTML, then open it in a browser; GitHub's file page does not run it).
- [Static overview](visualization/evidence_overview.png)
- [All 600 evidence statuses](all_600_evidence_status.csv)
- [Landmark vector audit](landmark_vector_audit.csv) and
  [contact sheet](landmark_contact_sheet.png)
- [54 retained terrain diagnostics](retained_terrain_diagnostics.csv)
- [Modica/Pozzallo source investigation](MODICA_POZZALLO.md)
- [Machine-readable results and input hashes](summary.json)
- [Current candidate, spacing review and deferred list](../geography_v8/README.md)

## What the landmark check measures

The [22 named reference features](../../../data/geography/landmark_observations_v9.csv)
were selected before measuring their raster positions. Published latitude/longitude
comes from the linked Wikipedia articles, accessed 26 October 2026. These are
approximate modern feature references, sometimes lighthouse locations, not exact
historic shoreline surveys. Dunnet Head uses the northern tip coordinate in its
infobox rather than the article header's more southerly peninsula coordinate.

Each raster observation uses a manually identified feature box and an explicit
land extremum (minimum/maximum row or column). Land means source RGBA **red > 0**.
The script finds the requested extremum, chooses the middle of equal candidates
in row-major order, and rejects observations touching the box boundary. Its output
must equal the recorded observation. This process never selects the coast point
closest to the projected reference. A reader can inspect or challenge the boxes,
feature definitions, exclusions and observations in the contact sheet and CSV.
Cyan crosses show projected references; yellow circles show observed features.

There are **21 approximate morphological matches**, and one unresolved
identification at Cape Finisterre. It has no assigned observation or residual;
several local protrusions need a better feature match. It remains in the report.
For the 21 measured observations the two-dimensional differences are:

| Statistic | Source pixels |
|---|---:|
| Median | 3.772 |
| 90th percentile | 8.196 |
| Maximum | 8.610 |

Cape St Vincent (8.196 pixels) and Malin Head (8.610 pixels) exceed their
8-pixel feature-identification estimates. Those estimates describe ambiguity in
matching a named feature to a generalized shoreline; they are **not statistical
model error bounds**. No passing threshold proves that a town is well placed.

The model was frozen at V6 and was not refitted to these observations. Of all
22 attempted features, 8 fall in coastline-fit held-out cells, 10 in training
cells and 4 outside the original fit-sample extent in northern Scotland. Thus
this is **not a fully independent or blinded validation set**: the crops were
located with the existing model, new points in training cells share coastline
information with the original fit, and feature identification uses approximate
published references. The checks supply evidence against axis flips and gross
regional shifts. They do not establish survey accuracy or inland accuracy.
No inland river or town-centre control is claimed here. The map's original CRS
and DEM source remain unknown.

The unchanged empirical transform is:

```text
source column = 104.42263446189997 * longitude + 1379.7176323206816
source row    = -164.09816527178702 * latitude + 9729.142746398953
```

This is a fitted axis-aligned affine approximation. Source row/4095 is importer
JSON `x`; source column/4095 is importer JSON `y`. The importer uses float32
arithmetic and counter-clockwise rotation in the supplied scenarios. The exact
rounding and sampling helpers remain in `scripts/scenario_geography.py`.
See [V6 mapping evidence](../geography_v6/README.md) for the source-code and
scenario evidence establishing that relationship.

## What was learned about the 54 terrain flags

All 54 retained V8 flags were re-sampled against the source raster and **both**
original scenario terrain arrays. Their targets were not moved.

| Priority | Targets | Remaining evidence needed |
|---|---:|---|
| Coast or harbour | 13 | Historic centre/port feature on the correct coast; verify the raster shoreline |
| Inland channel or centre | 38 | Identify the named channel and appropriate historical bank/centre |
| Road occupancy | 3 | Check the source of the saved road and historically suitable founding area |

The new CSV measures source land fraction and common saved clear-ground fraction
within circular radii of 5, 10 and 16 pixels. It also reports the source land
pixel's distance to the nearest zero pixel (zero for zero pixels). These quantify
sensitivity to local displacement. They are neither town corrections nor a
replica of the importer's spiral search. No clear-ground fraction proves
flatness, historical appropriateness or successful founding. Inland saved water
can be a generated channel; this report does not identify it as a particular
real-world river.

**Zero terrain flags were resolved.** A nearby land pixel alone is insufficient
evidence to relocate a town. The existing V8 clear/flat diagnostics and source
contact sheets remain available alongside these new measurements.

## Reading the evidence map

The map shows the original raster in source-image orientation, with zoom, pan,
search across all 600 master names, layer toggles and clickable evidence details.
All resources are embedded: no server, external tiles or online service is needed.
The PNG is a static overview of the same point set.

- Green: 502 retained clear targets with no recorded boundary flag.
- Orange: 54 retained targets with unresolved terrain flags.
- Purple: 8 retained clear targets requiring boundary review.
- Red: 12 in-bounds deferrals. The 24 out-of-map deferrals are available in search.
- White: 21 approximate observed landmarks, linked to projected references.

These are **evidence classes, not confidence probabilities**. Every town still
uses an uncertain empirical transformation and founding is untested. Terrain
class takes display precedence over boundary class; both underlying flags remain
in the all-600 CSV. The existing spacing decisions remain in V8.

## Reproduce without launching OpenTTD

From the repository root, with Python 3.10+:

```powershell
python -m pip install -r requirements-visualization.txt
python scripts/validate_landmarks.py --assets source_assets --out scratch/v9-evidence
python scripts/visualize_evidence.py --report scratch/v9-evidence --out scratch/v9-map
python -W error::ResourceWarning -m unittest discover -s tests -v
node tests/test_evidence_map.js scratch/v9-map/evidence_map.html
```

Use new output directories. The scripts reject existing output directories and
read/hash-check the original assets. The numerical reports, contact sheet and
summary reproduce exactly with the supplied inputs. Figure compression and font
rendering can vary with library/platform versions. Node.js is optional and only
needed for the map-logic smoke test.

Validation completed here: **29 Python tests passed**; the Node smoke test passed
for dataset counts, town search, out-of-map deferrals, layer toggles and reset.
The static figures were visually inspected. The Node test uses a minimal DOM;
it does not establish browser rendering, touch behavior or accessibility.

## Later OpenTTD check, when ready

No new V9 import file is necessary because town coordinates are unchanged.
In JGRPP 0.73.4 create a **fresh empty 4096×4096 editor map** from
`source_assets/heightmaps/Europe_heightmap_original.png`, using **counter-clockwise**
rotation. In Town Generation → Load from file select:

```text
maps/calibration/geography_v8/Europe_1800_V8_DESK_REVIEWED_CANDIDATE_TEST.json
```

It requests 564 towns; actual founding may fail or shift within the importer's
search. Check the 54 flagged names first, compare source-image coordinates with
the documented game transform, and save only to a new scenario filename.
For a full comparison, use the separate V8 576-town corrected import on another
fresh map. Do not import both into one map. Preserve the original scenarios and
NewGRF configuration.

The next geographic work is named inland controls and source-backed centre
positions for the flagged towns, followed by re-sampling and spacing review if
any corrections are justified. Modica/Pozzallo additionally needs the original
population-table page/notes to settle the combined entry's scope.
