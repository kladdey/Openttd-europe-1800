# Full-resolution anchor verification - FAILED

Date: 2026-10-25

Inspected the actual original 4096x4096 grayscale heightmap using the 29 manually chosen 900x900 image reference coordinates scaled to full resolution. This is an **anchor diagnostic**, not a complete 600-town verification.

- 17 / 29 reference locations: nonzero center pixel and moderate 33x33-pixel elevation variation.
- 5 / 29: rough elevation neighborhood (90th-10th percentile grayscale range >25).
- **7 / 29: zero-valued center pixel**, including Rome, Dublin, Athens, Zagreb, Naples, Sarajevo, Sofia.

Zero-valued heightmap pixels may include lowlands as well as sea, but multiple major city anchors failing this test demonstrate the control points are not reliably georeferenced. This undermines the 600-town interpolation.

**Do not auto-snap towns**: that can move cities to the wrong coastline or country.

The original 600-town candidate has not been independently verified in JGRPP; there is no confirmed placement success count or corrected .scn.

## Next steps
1. Re-georeference the heightmap with identifiable independent coastline/landmark points, ideally a GIS reference layer using the same projection and crop.
2. Recompute all 600 town coordinates from the corrected transform.
3. Run the full-resolution per-town pixel/elevation and spacing audit.
4. Test JSON import in JGRPP, review failure signs and save a *new* scenario file.

The existing JSON is TEST-only.
