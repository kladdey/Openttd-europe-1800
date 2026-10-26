# Geographic audit and calibration workflow

**Historical V5 checkpoint.** The user subsequently supplied the source assets.
See [V6](../maps/calibration/geography_v6/README.md) for the recovered importer
mapping, read-only scenario validation, coastline fit and corrected regional test.
The missing-asset statements below describe the earlier inspection, not current
availability. The current importer validator requires strict `0 < x,y < 1`.

## Current evidence and limitations

Repository inspected at `a4d9312100ae093b01fa244c09f1cebc6edf2072`.
The complete default-branch tree contains **no heightmap, scenario binary,
importer source, calibration screenshots, executable generation script, or
dependency manifest**. `scripts/README.md` describes planned tooling only.
No alternate branch was present at inspection. No AGENTS.md was present.
Earlier reports describe a 4096 × 4096 RGBA raster, but that raster is absent
from the repository and current workspace. Its dimensions, shoreline and
projection cannot presently be independently checked. The user is supplying
assets separately.

The master JSON has 600 records with `name`, integer `population`, boolean
`city`, and normalized game `x`, `y`. All records pass structural checks.
The draft CSV supplies real-world latitude/longitude but is **not an exact
geographic companion to the current master**: Głogów, Krems, Písek, Rawicz,
Sieradz and Łowicz exist only in the JSON; six historical duplicate-name
rows exist only in the draft CSV. Do not join these files by row number or
invent coordinates for unmatched names. See generated summary for both lists.

The 29 `control_points_900px.json` points are approximate preview pixel
observations. Prior full-resolution and leave-one-out reports explicitly
reject their reliability. Do not convert them into authoritative controls.
V2 has five provisional visually accepted game-space anchors; V4 preserves
them. They remain unchanged. A global fit to these five towns would be
unjustified.

V4's minimum continuous game-space separation is 32.084661 tiles. This
establishes spacing only. Neither correct landmass nor land placement has
been established for any of its 40 towns in this audit.

Existing metadata differences also need a deliberate future decision:

| Town | Master population / city | V4 population / city |
|---|---|---|
| Dublin | 3350 / true | 1200 / false |
| Paris | 10000 / true | 7500 / true |
| Berlin | 3000 / true | 2600 / true |

No populations, flags or coordinates were modified by this workflow.

## Reproduce the audit

Use Python 3.10 or newer from the repository root:

```powershell
python scripts/geography.py audit --out scratch/geography-audit-1
python -m unittest discover -s tests -v
```

Use a **new output directory** each time. Existing output directories are
refused. The audit uses only the standard library. It generates master and
V4 nearest-neighbour CSVs, all pairs at most 30 tiles apart, an existing
metadata discrepancy report, a complete 600-row review register, and a
summary with SHA-256 input hashes. Outputs are deterministic for identical
inputs. The committed snapshot is in `maps/calibration/geography_v5_audit/`.

Names are checked with Unicode NFKC, case folding and whitespace normalization.
That detects textual duplicates, not all historical aliases. Source coordinates
remain unverified even when names are unique and numbers lie in [0,1].

## Establish the coordinate transformation

There are two separate mappings to prove:

1. Geographic longitude/latitude → original raster column/row. Obtain source
   CRS, bounds, crop and any rotations/resampling, or independently identify
   coastline and inland landmarks on the full-resolution raster. Use controls
   distributed across the intended region, not only town centres in one cluster.
2. Raster pixels → normalized game coordinates. Verify JGRPP **0.73.4**
   importer code, heightmap generation rotation, crop/scaling, map dimensions
   and tile rounding against identifiable in-game points. Isometric screen
   positions are not game tile coordinates.

The older alignment report claims an X/Y swap and links upstream master
documentation; this is not sufficient evidence for the target binary and
actual scenario orientation. No axis swap, flip or north-up projection is
assumed by the new script. The precise mapping is **unresolved**.

Optional diagnostic dependencies:

```powershell
python -m pip install -r requirements-geography.txt
```

Prepare a CSV with columns
`name,longitude,latitude,column,row,role,evidence`. Roles are `fit` or
`holdout`; evidence identifies the actual source and how the point was
located. Column/row are full-resolution pixel centres. Use at least three
noncollinear fit controls and three independent holdouts to run the diagnostic;
the release review should use 20+ independently verified holdouts across Europe.
Do not relabel training points as holdouts or reuse locations under aliases.

```powershell
python scripts/geography.py fit --controls controls.csv --max-error-pixels 10 --out affine-diagnostic.json
```

The example 10-pixel threshold is a caller-supplied diagnostic tolerance,
not a historical accuracy guarantee. The fit is ordinary least squares:

```text
[column, row] = [longitude, latitude, 1] @ coefficients
```

The 3×2 coefficient matrix, all residuals, holdout median and worst error are
reported. Holdouts are excluded from fitting. This tests an **affine model
hypothesis**, not a known projection. Curvature, cropping or regional
distortions may invalidate it. A passing threshold never marks a model
release validated and never emits a town JSON. Prefer the documented original
projection if recovered. Account for control uncertainty and coverage; assess
regional errors before extrapolating.

## Raster diagnostics

Once the original raster and mapping evidence exist, prepare a manifest:

```json
{
  "mapping_evidence": "Reference verified target importer and in-game orientation evidence here",
  "raster_sha256": "SHA-256 of the exact original raster",
  "raster_dimensions": [4096, 4096],
  "pixel_convention": "normalized_endpoints_nearest",
  "game_to_raster_matrix": [[1, 0, 0], [0, 1, 0]],
  "zero_elevation_threshold": 0
}
```

**The identity matrix above is a schema example, not this map's mapping.**
Replace it with verified coefficients before sampling. For each game point,
the explicit 2×3 matrix maps `[x,y,1]` to normalized raster `[u,v]`; column
is `round(u*(width-1))`, row is `round(v*(height-1))` using Python's nearest,
ties-to-even rounding. This endpoint convention is explicit and may require
replacement if target importer evidence uses another convention. The tool
refuses mismatched raster hashes, dimensions, singular mappings, unsupported
image modes and non-grayscale/transparent sampled pixels.

```powershell
python scripts/geography.py terrain --towns maps/calibration/baseline_v2/Europe_1800_40_city_V4_REGIONAL_TEST.json --raster original.png --manifest mapping.json --out v4-terrain.csv
```

This reads full-resolution pixel values, without moving towns. A nonzero
pixel alone does not prove correct geography or successful founding. A zero
pixel may represent sea or lowlands. Game height conversion, sea level,
neighbourhood slope and founding rules still require checks. The report
therefore retains `UNVERIFIED_IN_GAME` land status. Synthetic raster tests
exercise the code; they are not tests of this absent European raster.

## Spacing and deferred decisions

Distances are continuous Euclidean game distances:
`4096 * hypot(x1-x2, y1-y2)`. This is not ground distance or exact quantized
founding-tile separation. Less than 15 triggers importance review; 15 through
30 inclusive requires individual review; over 30 generally allows coexistence.
The script flags pairs, **never automatically deletes towns**. Apply these
decisions only after geographic correction. Record retained/deferred decisions
and historical port, mining, industrial or regional-hub exceptions explicitly.

The review register withholds all 600 towns from a *new release*, pending
geography. This is not 600 spacing deferrals, nor a change to the catalogue.
No replacement regional JSON or complete Europe import is emitted while the
necessary geographic evidence is missing.

## OpenTTD test procedure after correction

There is currently **no new corrected import to test**. To reproduce the
existing provisional baseline while supplying further evidence:

1. Back up the original heightmap and playable scenario outside the test folder.
2. In JGRPP 0.73.4 Scenario Editor, generate a **fresh empty** 4096×4096 test
   map from the exact original heightmap with the original rotation and settings.
   Keep NewGRF configuration unchanged.
3. In Town Generation → Load from file, choose
   `maps/calibration/baseline_v2/Europe_1800_5_city_CONTROL_V2_TEST.json`.
4. Record actual founding success/failure and town tile coordinates. Capture
   full-resolution coastline context and generation settings. Do not judge
   relative bearings from isometric screen axes alone.
5. For V4 comparison, generate another fresh empty map with identical settings
   and load `Europe_1800_40_city_V4_REGIONAL_TEST.json` from the same directory.
   Check all 40 towns, particularly Brandenburg and the Baltic ports.
6. Save only under a new test filename, such as `Europe_1800_V5_DIAGNOSTIC.scn`.
   Never overwrite the base or existing playable industry scenario.

After a corrected candidate exists, repeat those checks with the new filename,
review landmass, river/coast relationships and close pairs, and compare expected
town count with actual successful placements before considering release.
