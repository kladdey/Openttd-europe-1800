# Europe heightmap alignment - initial control-point fit

**Status: approximate, NOT validated in-game.** Generated from 29 visually selected geographical control points on a 900x900 preview of the original 4096x4096 heightmap. These are hand-estimated pixel positions, not GIS georeferencing.

OpenTTD JSON uses normalized map coordinates with X/Y swapped relative to image pixel axes. Reference: https://github.com/OpenTTD/OpenTTD/blob/master/docs/importing_town_data.md

Input: 600 town inventory. Output: 600 in-bounds candidate town positions; 0 outside map frame. No coastline/land-height check has been performed. Some towns may appear in the sea or on steep slopes, and names may overlap.

The geographic map's exact projection and bounds are still unverified. Treat this JSON as a **test import only**. Keep the original `Europe_1800_Base.scn` backed up. A final calibration requires checking the actual terrain raster, coastline, and Scenario Editor placement results.

## Out-of-frame candidates

None

## Control points (preview pixels)
| City | Latitude | Longitude | Image column | Image row |
|---|---:|---:|---:|---:|
| London | 51.5074 | -0.1278 | 317 | 350 |
| Paris | 48.8566 | 2.3522 | 369 | 414 |
| Amsterdam | 52.3676 | 4.9041 | 414 | 326 |
| Berlin | 52.52 | 13.405 | 562 | 316 |
| Warsaw | 52.2297 | 21.0122 | 682 | 323 |
| Prague | 50.0755 | 14.4378 | 572 | 378 |
| Vienna | 48.2082 | 16.3738 | 600 | 424 |
| Rome | 41.9028 | 12.4964 | 536 | 635 |
| Milan | 45.4642 | 9.19 | 484 | 514 |
| Madrid | 40.4168 | -3.7038 | 240 | 655 |
| Lisbon | 38.7223 | -9.1393 | 145 | 702 |
| Barcelona | 41.3874 | 2.1686 | 352 | 622 |
| Copenhagen | 55.6761 | 12.5683 | 547 | 219 |
| Stockholm | 59.3293 | 18.0686 | 633 | 111 |
| Edinburgh | 55.9533 | -3.1883 | 272 | 220 |
| Dublin | 53.3498 | -6.2603 | 196 | 296 |
| Athens | 37.9838 | 23.7275 | 786 | 769 |
| Budapest | 47.4979 | 19.0402 | 649 | 456 |
| Zagreb | 45.815 | 15.9819 | 592 | 508 |
| Belgrade | 44.7866 | 20.4489 | 672 | 553 |
| Bucharest | 44.4268 | 26.1025 | 777 | 570 |
| Oslo | 59.9139 | 10.7522 | 509 | 101 |
| Naples | 40.8518 | 14.2681 | 569 | 672 |
| Marseille | 43.2965 | 5.3698 | 419 | 558 |
| Bordeaux | 44.8378 | -0.5792 | 314 | 514 |
| Hamburg | 53.5511 | 9.9937 | 509 | 288 |
| Munich | 48.1351 | 11.582 | 521 | 434 |
| Sarajevo | 43.8563 | 18.4131 | 636 | 575 |
| Sofia | 42.6977 | 23.3219 | 725 | 631 |
