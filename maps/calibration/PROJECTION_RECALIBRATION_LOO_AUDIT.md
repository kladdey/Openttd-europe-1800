# Projection recalibration: independent-fit diagnostic

Date: 2026-10-25

## Method
Tested the original 29 manually estimated image anchors using leave-one-out thin-plate-spline interpolation: each anchor is predicted using the other 28. Longitude was multiplied by 0.65 to approximately normalize geographical distance. Read center elevations directly from the original 4096x4096 RGBA heightmap.

## Results
- Median leave-one-out positional error: **30.7 source pixels**.
- 90th-percentile error: **64.6 source pixels**.
- Worst: **Athens, 238.1 pixels**.
- 7/29 anchor pixels had elevation zero.
- Other major outliers: Edinburgh 88.2 px, Dublin 73.6 px, Sofia 62.4 px, Marseille 60.0 px, Lisbon 54.7 px.

These leave-one-out errors quantify the instability of the *manually picked anchor dataset*, not true map accuracy. A low residual at a training anchor would not establish independent correctness.

## Decision
**Do not regenerate a purportedly final 600-town JSON using these anchors.** A spline can interpolate wrong anchors perfectly while misplacing the actual settlements. Moving towns to nearest nonzero pixels would also be unsafe.

## What is required to actually repair it
1. Obtain original heightmap provenance: exact source projection, geographic bounds, crop, rotation and any resampling applied; or build an independently checked set of coastline/landmark control points.
2. Fit a physically appropriate projection; check 20+ independent holdout landmarks against the actual raster, not the training points.
3. Reproject all 600 towns, inspect elevations and coastlines at full resolution, then test placement inside JGRPP.
4. Preserve original base scenario and all previous TEST files until the replacement passes.

This audit identifies the blocking input rather than inventing false precision. 
