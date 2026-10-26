# Inland diagnostics — frozen model, no town movements

This offline review tests ten named lake basins against the unchanged V6
geographic transformation, and overlays two named rivers on the original heightmap
and both supplied scenarios. **No model was fitted and no town was moved or restored.**
V11 remains the current 537-town clear-target candidate; all 27 terrain deferrals
and all 600 master records are preserved. No OpenTTD execution is required.

## Results and practical limits

Seven lakes yield descriptive plateau-to-outline comparisons. Three are withheld:
Garda has only a partial isolated plateau, Vänern's projected reference is clipped,
and Loch Ness lacks a reliably identified plateau. Fragmented components at Geneva
and Balaton are explicitly recorded rather than automatically merged across land.

| Lake | Plateau vs outline centroid difference (pixels) | Plateau / projected area |
|---|---:|---:|
| Geneva | 5.793 | 0.5820 |
| Constance | 7.058 | 0.4861 |
| Balaton | 2.763 | 0.5243 |
| Lough Neagh | 2.992 | 0.5837 |
| Skadar | 0.476 | 0.4935 |
| Bracciano | 3.168 | 0.5179 |
| Vättern | 6.185 | 0.6774 |

These are **shape diagnostics, not measured town-position errors**. Constant-height
interiors occupy only about 49–68% of the projected geographic lake areas. Their
boundaries are inset and their centroids can shift as a result; do not translate
towns by these vectors. Geneva, Constance and Bracciano's isolated plateaus have
red-channel elevation 24, so a zero-elevation water detector would miss them.
An identifiable geographic lake basin does not imply in-game water at its target.

The broader shapes provide useful inland checks on the coastline-derived model,
without establishing an exact original CRS or inland accuracy. The features were
not used in V6 fitting, but Natural Earth lakes and coastlines share a generalized
cartographic source family. These are not statistically independent survey data.
Windows were located with the existing model and visually inspected; this is not
blind feature identification. All boxes, scalar elevations and seeds are explicit;
no nearest-point snapping, shape alignment or residual minimization occurs.

## Arles and Alençon bank holds

[River-bank overlays](river_bank_overlays.png) place the same fixed geographic
centerlines over the original heightmap, V1 terrain and Industries terrain.
Yellow circles mark the exact importer source pixels of the held V11 site references;
cyan marks generalized river centerlines. Water in saved terrain is blue. Saved
terrain arrays are mirrored into source-pixel orientation using the independently
verified importer mapping. This display does not edit either scenario.

| Case | Named river source | Saved water fraction on projected line, both scenarios | Decision |
|---|---|---:|---|
| Alençon | Sarthe, Natural Earth European supplement | 0.1379 | Keep bank-alignment hold |
| Arles | Rhône, Natural Earth main river layer | 0.1290 | Keep bank-alignment hold |

These fractions describe overlap with **any** saved water in each 80×80-pixel
window. They do not identify a named channel, measure river accuracy, or prove a
historic bank. The source-heightmap zero fractions are 0 and 0.0081 respectively.
The overlays show that the generalized projected lines and saved channels cannot
be treated as interchangeable. A point being clear in both scenarios therefore
still does not resolve its historical river-bank relationship. Neither hold is
lifted by this review. Next, obtain historic bank/bridge mapping or a confidently
identified channel in the raster; check its positional uncertainty before moving
neighbouring towns consistently. No evidence here resolves the other 25 cases.

## Sources and files

Natural Earth data is public domain. Geometry is taken from repository tag
`v5.1.2`, commit `f1890d9f152c896d250a77557a5751a93d494776`:

- [Lakes source and limitations](https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-lakes/).
- [Rivers source and limitations](https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-rivers-lake-centerlines/).
- [Terms of use](https://www.naturalearthdata.com/about/terms-of-use/).
- [Lake observation manifest](../../../data/geography/inland_observations_v1.json)
  and [geometry subset](../../../data/geography/ne_10m_inland_lakes_subset.geojson).
- [River observation manifest](../../../data/geography/river_bank_observations_v1.json)
  and [geometry subset](../../../data/geography/ne_10m_bank_review_rivers.geojson).
- [Lake audit CSV](inland_shape_audit.csv), [contact sheet](inland_contact_sheet.png),
  [river review CSV](river_bank_review.csv), [summary and hashes](summary.json).

The manifests retain original full-download SHA-256 hashes, pinned source URLs,
subset hashes, feature identities and selection notes. Geometry coordinates are
preserved from the upstream GeoJSON; unused properties/features are omitted.
No new third-party Python dependencies are introduced.

## Reproduction

From the repository root:

```powershell
python -m pip install -r requirements-visualization.txt
python scripts/validate_inland_features.py --out scratch/inland-review
python -W error::ResourceWarning -m unittest discover -s tests -v
```

The output directory must not exist. The script verifies original PNG, both
scenario hashes and both committed geometry-subset hashes, then generates the
CSV, summary and PNG artifacts without network access. It never reads a town list
as a source of fitting controls and never exports a replacement import JSON.
It reads the two frozen V11 historic-site references only to display their held
positions. Existing bounds, duplicate, spacing, land, source-preservation and
terrain tests continue to apply to the unchanged V11 candidate.

Seven new tests cover explicit component selection, decoy exclusion, invalid and
edge-touching observations, known vector shifts, polygon holes and clipping,
withheld controls, source/game crop orientation, deterministic reproduction and
preservation of inputs. No in-game founding or growth checks were performed.
