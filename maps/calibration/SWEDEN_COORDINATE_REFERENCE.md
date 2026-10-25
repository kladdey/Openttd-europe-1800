# Sweden coordinate reference - terrain versus town placement

The original 4096x4096 heightmap was inspected directly, with known city coordinates overlaid on a 900x900 preview. The existing five reference points are broadly aligned with recognizable Scandinavian geography.

| City | Latitude | Longitude | Preview column | Preview row | Center grayscale elevation |
|---|---:|---:|---:|---:|---:|
| Oslo | 59.9139 | 10.7522 | 509 | 101 | 24 |
| Stockholm | 59.3293 | 18.0686 | 633 | 111 | 33 |
| Göteborg | 57.7072 | 11.9668 | 533 | 162 | 0 |
| Karlskrona | 56.1616 | 15.5866 | 597 | 208 | 29 |
| Copenhagen | 55.6761 | 12.5683 | 547 | 219 | 26 |

Pixel intensities were sampled at corresponding coordinates in the source 4096px raster. Zero does not by itself prove ocean, but Göteborg's zero pixel demonstrates terrain-placement vulnerability.

**Finding:** The existing approximate coordinates are not demonstrably the main cause of the screenshot's unusual Scandinavian coastline. The original heightmap shows water-shaped gaps through Sweden. This could reflect terrain-height clipping / sea-level handling or genuine inland water, and cannot be repaired by simply moving towns.

**Decision:** Do not overwrite the core 600-town JSON or import another Sweden pack yet. To fix terrain geography, inspect how the heightmap was generated and what height threshold the game applies. If terrain is acceptable for gameplay, place individual towns on nearby suitable land and retain the approximate geographical layout. Avoid calling this a verified GIS transform.

**In-game baseline:** Keep `Europe 1800 V1.scn` unchanged.
