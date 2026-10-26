# Original heightmap provenance — pixel identity established

Research date: 2026-10-26. This report changes no placement candidate. V11 remains
537 clear-target towns, with 27 unresolved terrain cases and 63 total deferrals.

## Identification

The supplied `source_assets/heightmaps/Europe_heightmap_original.png` is a
pixel-identical copy of **UseYourIllusion's Europe (4096 x 4096), version 4**,
BaNaNaS heightmap ID `00000ae3`, published **2014-03-03 15:08:09 UTC**.
The PNG bytes differ, but every decoded RGBA value agrees at all **16,777,216**
positions. Red-channel elevations also agree exactly. No rotation, resampling,
crop, elevation correction or tolerance was used in this comparison.

Evidence:

- [Official package listing](https://bananas.openttd.org/package/heightmap/00000ae3).
- [Pinned author record](https://github.com/OpenTTD/BaNaNaS/blob/a402c8640fa9750b593c7104d3a5452772c41080/heightmap/00000ae3/authors.yaml).
- [Pinned version record](https://github.com/OpenTTD/BaNaNaS/blob/a402c8640fa9750b593c7104d3a5452772c41080/heightmap/00000ae3/versions/20140303T150809Z.yaml).
- [Public archive index](https://kompot.snt.utwente.nl/pub/games/openttd/bananas/index.html)
  and [download](https://kompot.snt.utwente.nl/pub/games/openttd/bananas/heightmap/Europe_4096_x_4096-4.tar.gz).
- [Machine-readable pixel comparison](pixel_comparison.json), including hashes of
  both encoded PNGs, raw row-major RGBA bytes and raw red-channel bytes.
- [Source metadata and research boundaries](sources.json).

The downloaded archive is 7,030,642 bytes, exactly the official version's
reported size. Its image member `Europe_4096_x_4096-4/flevo_2.png` has MD5
`6ab07e287d53419af312fcd55b823f61`, agreeing with the official `6ab07e28` prefix.
Archive SHA-256 is `ab5b9cf3f6ae4805fd8c9445de00c5c6c29ecdaf263077658d7c794b01afc4d5`.
Its image metadata says **Software: Paint.NET v3.5.10**. This identifies an editor,
not the upstream DEM or GIS projection. Both images include the same 13 blue
non-grey pixels in the Dutch delta; these are useful corroboration, while the
full-image exact comparison provides the stronger evidence.

The archive bundles GPL version 2. Its exact license text is preserved in
[source_assets/heightmaps/LICENSE-Europe-heightmap-GPL-2.0.txt](../../../source_assets/heightmaps/LICENSE-Europe-heightmap-GPL-2.0.txt).
Credit UseYourIllusion for this heightmap. This finding does not establish licensing
for unrelated scenario content, NewGRFs or the entire repository.

## What this establishes about the projection

**The distributed source image is identified; the upstream DEM, original CRS,
exact geographic bounds and any prior image transformations remain unknown.**
Neither the package contents (PNG, title, ID and license) nor its official
metadata supplies a GIS sidecar or geographic control coordinates. PNG `pHYs`
is print resolution, not ground resolution. The archived PNG's Software, sRGB,
gamma and DPI fields are not a georeference. The supplied copy has only IHDR,
IDAT and IEND chunks, so even its editor metadata was removed during re-encoding;
the re-encoding software and date cannot be recovered from these files.

Existing V6 coastline evidence supports a linear longitude/latitude image fit
much better than the tested Mercator fit. Its empirical model is:

```text
source_column = 104.42263446189997 * longitude + 1379.7176323206816
source_row    = -164.09816527178702 * latitude + 9729.142746398953
```

These coefficients imply approximate image-edge bounds of 13.213°W–26.003°E
and 34.334°N–59.289°N. They are fitted bounds, **not recovered original bounds**.
V6's held-out coast-normal median residual is about 2.51 pixels and its 90th
percentile about 9.17 pixels. Coast-normal residuals cannot measure inland
position error or along-coast displacement. Do not assign an EPSG code or claim
survey accuracy from this fit. V10's supported regional translations still apply.
See [V6](../geography_v6/README.md) and the
[current mapping workflow](../../../docs/GEOGRAPHY_WORKFLOW.md).

Importer axes remain independently established from JGRPP code and saved terrain:
JSON `x = source_row / 4095`, JSON `y = source_column / 4095`, with the exact
float32/truncation behavior implemented in `scenario_geography.py`. Knowing the
package author does not alter that mapping or justify moving any town.

## Reproduce without OpenTTD

From the repository root, using Python and the existing visualization dependencies:

```powershell
python -m pip install -r requirements-visualization.txt
New-Item -ItemType Directory -Force scratch/provenance
curl.exe -fL "https://kompot.snt.utwente.nl/pub/games/openttd/bananas/heightmap/Europe_4096_x_4096-4.tar.gz" -o scratch/provenance/europe4.tar.gz
python scripts/audit_heightmap_provenance.py --source source_assets/heightmaps/Europe_heightmap_original.png --archive scratch/provenance/europe4.tar.gz --output scratch/provenance/pixel_comparison.json
python -m unittest discover -s tests -p test_heightmap_provenance.py -v
```

Use a new output filename; the script refuses to overwrite an existing report.
The report is deterministic and should match `pixel_comparison.json` exactly.
The script never extracts archive paths to disk. It validates PNG chunk CRCs,
compares all four channels and exits nonzero if no PNG matches exactly.
A failed match should be investigated, not treated as proof that the source changed.
Archive absence/network failure is separate from a pixel mismatch. The downloaded
package is kept outside the repository; it need not be redistributed to run tests.

## Next useful offline investigation

Look for the author's original forum post or earlier image-making notes describing
the DEM and crop. Do not infer GIS settings from Paint.NET alone. If those cannot
be recovered, add independent inland river/confluence controls and assess a
conservative regional model before revisiting the 27 terrain holds. These findings
remove the source-identity uncertainty; they do not resolve those terrain cases.
No OpenTTD tests were run, and original assets, towns and scenarios are unchanged.
