# Geographic correction workflow

See [project status](PROJECT_STATUS.md) for the current checkpoint and remaining
cases. The user has no OpenTTD test platform; this workflow runs offline.

## Inputs and invariants

Preserve `data/towns/europe_1800_import_AUDIT_FIXED_TEST.json` as the complete
600-town master. Original normalized coordinates are not geographically reliable.
Preserve names, populations and city flags unless a separate justified change is
authorized. Join geographic source tables by reviewed names, never row number.
Read the original heightmap and two scenario files from `source_assets/`; their
checksums are documented in the asset manifest. Never edit these files or the
NewGRF setup. Earlier experiment outputs remain historical snapshots.

## Mapping and uncertainty

The source PNG is 4096×4096 RGBA. The target reader samples its red channel.
Importer JSON `x` corresponds to source row/4095 and `y` to source column/4095;
these are not ordinary east/north axes. Use `scenario_geography.py` to reproduce
float32 parsing, counter-clockwise rotation and truncation exactly. The geographic
fit and mapping evidence are in the [V6 report](../maps/calibration/geography_v6/README.md).

The distributed heightmap is now identified by exact pixel comparison as
[UseYourIllusion’s Europe v4](../maps/calibration/provenance_v1/README.md).
The global fit is empirical; the original DEM CRS is unknown. V10 adds three
accepted regional translations, with [declared gates](../data/geography/coastal_regions_v10.json).
Rejected fits must not be applied. Any accepted geographic correction must also
be applied consistently to neighbouring catalogue towns in its declared region.
Re-sample every affected target to catch newly exposed conflicts such as Orihuela.
Coast-normal residuals do not establish two-dimensional town or inland accuracy.

## Review and export

1. Identify a historically appropriate centre, port, industrial site or regional
   hub using linked sources. Distinguish an old site from a modern rebuilt building.
2. Record geographic coordinates, historical basis, interpretation and uncertainty.
   Keep failed alternatives in the evidence table.
3. Apply the supported map transformation; do not search for a nearby clear pixel
   and retroactively call it the historic centre.
4. Check actual source land, landmass and both saved terrain arrays. Record slope
   separately; clear ground does not imply flatness or successful founding.
5. Recompute all proximity after correction. Normally retain the more important
   settlement below 15 tiles; individually review 15–30; generally allow coexistence
   beyond 30. Document historical exceptions and avoid merged urban growth.
6. Give every source record a retained or documented deferred outcome. Produce
   a clear-target test import and separate full comparisons, with no town-count quota.
7. Run automated checks, inspect maps, commit reviewable results and preserve prior
   candidate files. Founding/growth/playability remain a later validation stage.

## Reproduction

```powershell
python -m pip install -r requirements-visualization.txt
python scripts/register_coastal_regions.py --out scratch/coast-registration.json
python scripts/review_remaining_terrain.py --out scratch/v11-candidate
python scripts/visualize_evidence.py --report scratch/v11-candidate --out scratch/v11-map --version V11
python -W error::ResourceWarning -m unittest discover -s tests -v
node tests/test_evidence_map.js scratch/v11-map/evidence_map.html scratch/v11-candidate/summary.json
```

All output paths must be new. The resolver uses the committed registration by
default; the separate fit command reproduces that evidence. See the
[tool guide](../scripts/README.md) for earlier audit/reproduction scripts.

## When OpenTTD becomes available

In JGRPP 0.73.4 generate a fresh empty 4096×4096 editor map from the original
heightmap with counter-clockwise rotation. Keep the intended NewGRF configuration.
Town Generation → Load from file should receive one current test JSON only.
Record failures, actual town coordinates and settings; compare against the offline
map. Save to a new filename. Never combine overlapping candidate/comparison imports
or overwrite an original playable scenario. See the [V11 instructions](../maps/calibration/geography_v11/README.md).

V11 adds an explicit historic-placement review state. A clear pixel with a
bank, source, identity or context hold is ineligible until the hold is resolved.
Source exclusions and repeated importer-pixel aliases remain documented.
