# Terrain verification - coarse raster challenge

**Result: FAIL / diagnostic only.** Verified the original 4096x4096 RGBA heightmap is predominantly grayscale, opaque, and has 47.34% exactly-zero elevation pixels. The water/land test below used a 64x64 nearest-neighbor sample of that *actual* raster, not an imagined coastline. This is **not** a full-resolution or in-game validation.

- Towns in candidate: 600.
- Towns on nonzero pixels at coarse sample: 502.
- Towns on zero-valued pixels at coarse sample: **98**.
- Town pairs separated by fewer than 12 OpenTTD tiles: 13.

**Important limitations:** The 64x64 mask is only one elevation sample per 64x64 source-pixel cell. It can misclassify coastal towns, lakes, narrow straits, and low-lying land. Zero elevation can also represent flat lowlands, not necessarily water. Do **not** automatically snap these cities to land or call them definitively offshore.

## Flagged zero-elevation candidates (coarse mask)
- ACIREALE (image col 2672, row 3453)
- ALICANTE (image col 1388, row 3256)
- ALTA MURA (image col 2775, row 3038)
- BARI (image col 2798, row 2995)
- BATH (image col 1261, row 1582)
- BERGEN (image col 1883, row 373)
- BILBAO (image col 1206, row 2582)
- BIRMINGHAM (image col 1298, row 1440)
- BOLOGNA (image col 2359, row 2488)
- BRISTOL (image col 1241, row 1571)
- CAGLIARI (image col 2180, row 3196)
- CALTAGIRONE (image col 2619, row 3497)
- CALTANISSETA (image col 2581, row 3462)
- CAMBRIDGE (image col 1465, row 1491)
- CASTEL VETRANO (image col 2477, row 3430)
- CASTROGIOVANNI (image col 2586, row 3455)
- CATANIA (image col 2666, row 3466)
- COLCHESTER (image col 1529, row 1534)
- CORK (image col 741, row 1499)
- COVENTRY (image col 1331, row 1452)
- DUBLIN (image col 896, row 1339)
- EXETER (image col 1163, row 1655)
- FIRENZE (image col 2349, row 2594)
- FOGGIA (image col 2692, row 2957)
- GALWAY (image col 689, row 1323)
- GIRGENTI (image col 2542, row 3483)
- GOTEBORG (image col 2425, row 739)
- KILKENNY (image col 823, row 1424)
- KING'S LYNN (image col 1490, row 1409)
- LECCE (image col 2912, row 3099)
- LEICESTER (image col 1373, row 1419)
- LIMERICK (image col 722, row 1406)
- LIVORNO (image col 2277, row 2616)
- LUCCA (image col 2293, row 2574)
- MARSALA (image col 2447, row 3413)
- MASCALI (image col 2674, row 3434)
- MAZZARINO (image col 2594, row 3487)
- MESSINA (image col 2702, row 3379)
- MODENA (image col 2329, row 2463)
- MODICA/POZZALLO (image col 2648, row 3565)
- MONOPOLI (image col 2834, row 3016)
- MUNSTER (image col 718, row 1444)
- NAPOLI (image col 2588, row 3054)
- NEWRY (image col 900, row 1227)
- NICOSIA (image col 2608, row 3431)
- NOTO (image col 2667, row 3545)
- ORIHUELA (image col 1349, row 3292)
- OXFORD (image col 1352, row 1547)
- PALERMO (image col 2522, row 3379)
- PALMA (image col 1650, row 3089)
- PARMA (image col 2286, row 2436)
- PERUGIA (image col 2435, row 2706)
- PIAZZA (ENNA) (image col 2612, row 3453)
- PISA (image col 2284, row 2592)
- PLYMOUTH (image col 1112, row 1695)
- RAGUSA (image col 2637, row 3538)
- READING (image col 1375, row 1591)
- REGGIO (image col 2307, row 2453)
- REGGIO DI CALABRIA (image col 2712, row 3390)
- ROMA (image col 2440, row 2888)
- SASSARI (image col 2136, row 2982)
- SIENA (image col 2354, row 2663)
- SIRACUSA (image col 2684, row 3521)
- TARANTO (image col 2832, row 3082)
- TERMINI (image col 2549, row 3398)
- TRAPANI (image col 2453, row 3385)
- VITERBO (image col 2410, row 2813)
- WENLOCK (image col 1244, row 1414)
- WOLVERHAMPTON (image col 1278, row 1425)
- WORCESTER (image col 1276, row 1481)
- Zagreb (image col 2694, row 2312)
- Dubrovnik (image col 2882, row 2780)
- Osijek (image col 2927, row 2378)
- Sarajevo (image col 2895, row 2617)
- Mostar (image col 2851, row 2683)
- Banja Luka (image col 2804, row 2476)
- Tuzla (image col 2920, row 2526)
- Zenica (image col 2857, row 2567)
- Bihać (image col 2697, row 2456)
- Travnik (image col 2839, row 2562)
- Niš (image col 3191, row 2739)
- Kragujevac (image col 3104, row 2619)
- Kraljevo (image col 3088, row 2656)
- Skopje (image col 3162, row 2912)
- Prilep (image col 3184, row 2998)
- Kotor (image col 2940, row 2815)
- Sofia (image col 3300, row 2872)
- Athens (image col 3577, row 3500)
- Patras (image col 3325, row 3430)
- Larissa (image col 3336, row 3239)
- Volos (image col 3415, row 3287)
- Ioannina (image col 3170, row 3216)
- Serres (image col 3354, row 3053)
- Trikala (image col 3271, row 3243)
- Lamia (image col 3391, row 3350)
- Tallinn (image col 3444, row 540)
- Pärnu (image col 3423, row 679)
- Viljandi (image col 3512, row 687)

## Very close town pairs
- ALTONA / HAMBURG: 7.3 tiles
- AMSTERDAM / ZAANDAM: 10.1 tiles
- BAEZA / UBEDA: 8.6 tiles
- BARMEN / ELBERFELD: 5.2 tiles
- BOULOGNE / PARIS: 8.3 tiles
- BOULOGNE / VERSAILLES: 10.3 tiles
- CALTANISSETA / CASTROGIOVANNI: 8.8 tiles
- DELFT / DEN HAAG: 10.5 tiles
- FURTH / NURNBERG: 7.3 tiles
- LIER / MECHELEN: 10.7 tiles
- MANCHESTER / SALFORD: 4.6 tiles
- MANCHESTER / STOCKPORT: 11.3 tiles
- Łódź / Łowicz: 11.6 tiles

## Remaining blockers
- Full-resolution per-town elevation and slope/neighborhood check.
- Independent holdout landmark alignment against a labeled basemap.
- JGRPP import founding-success count and failure signs.
- Confirmation that the saved scenario uses the same heightmap rotation as the town JSON.

The candidate remains TEST-only. No automatic relocation was applied because coarse terrain masking is not sufficiently reliable.
