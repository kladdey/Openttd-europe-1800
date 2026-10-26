# Preserved original source assets

> Current project context: [status and limitations](../docs/PROJECT_STATUS.md). These assets remain read-only inputs for current offline terrain review; no scenario has been resaved.

Supplied in `Europe_1800_GitHub_Source_Assets.zip` on 2026-10-26.
Archive SHA-256: `3d23d483f4ca3960bc28fa24879a1e72585f8a69136078e39bd405d8112cdbfd`.
These files are copied byte for byte; neither scenario was edited or resaved.
They are preserved sources, not calibrated replacement scenarios. The archive
README states that the industry scenario matches its preserved backup.

| Relative path | Bytes | SHA-256 |
|---|---:|---|
| heightmaps/Europe_heightmap_original.png | 5210979 | beb1760c157e72f90b87713cc7a88b7455d47e235f91fe54a11de663c541d744 |
| scenarios/Europe_1800_Industries_Original.scn | 3842900 | b49bda4d118dc7037441e9e0661543f1d1ea06e13349b7d1517f7ca39c9044db |
| scenarios/Europe_1800_V1.scn | 3515504 | 904097ebfda8db35b6f58f27e07aad1bf0595805ea6c8196245b7f9b68f29f3e |

The raster is 4096×4096 RGBA, fully opaque. Exactly 47.340101% of its red-channel
pixels are zero. There are 13 non-grayscale RGB pixels; the target version's
PNG reader uses the red channel for RGBA, which this workflow reproduces.
The PNG has no embedded projection/geographic bounds metadata. Heightmap
origin is now identified as UseYourIllusion’s **Europe (4096 x 4096), version 4**,
published on BaNaNaS in March 2014. All decoded RGBA pixels match the archived
package; encoded PNG bytes differ. See the [provenance report](../maps/calibration/provenance_v1/README.md).
The package is GPL v2; its [bundled license](heightmaps/LICENSE-Europe-heightmap-GPL-2.0.txt)
is preserved alongside the image. The upstream DEM, CRS and original geographic
crop provenance remain unknown. This attribution does not license unrelated assets.

Both scenario containers are OTTX/LZMA with JGRPP's extended 0x8124 header and
`jgrpp-0.73.4` version label in the SLXI chunk. Their MAPS table records
4096×4096 dimensions. The read-only decoder reads framed MAPT and MAPH arrays;
it cannot write or resave a scenario. Height values range from 0 to 29 in both.
Terrain orientation is independently checked against all eight raster square
symmetries. See [V6 results](../maps/calibration/geography_v6/README.md).
