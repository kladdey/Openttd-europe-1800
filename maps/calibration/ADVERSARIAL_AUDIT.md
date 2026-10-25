# Adversarial audit - Europe 1800 town placement

Date: 2026-10-25
Verdict: **FAIL - do not ship/import as final calibrated scenario.**

## Independent challenge
The 29 geographical control points were manually picked on a 900x900 preview and used to fit the transformation. Reporting the low error of those same points is circular validation, **not** an independent accuracy measurement. The exact map projection is still unidentified. The heightmap itself has not been tested against town placements.

## Verified dataset integrity
- Original test JSON: 600 entries.
- Second-pass deduplicated JSON: **594** entries. Target of 600 unique towns is not met.
- Six removed duplicates: VIENNE/WIEN; Gdańsk/DANZIG (GDANSK); Elbląg/ELBING (ELBLAG); Brno/BRNO (BRUNN); Szczecin/STETTIN (SZCZECIN); Wrocław/BRESLAU (WROCLAW).
- The original 600-row CSV remains unchanged and still includes duplicate geographical places.
- Basic schema/coordinate range alone is not a terrain-placement test.

## Spatial red flags in deduplicated 594-town import
These are Euclidean distances in OpenTTD tiles for a 4096x4096 map, **not** ground-truth geographical distances.

| Town A | Town B | Separation (tiles) | Interpretation |
|---|---|---:|---|
| MANCHESTER | SALFORD | 4.6 | Close real neighbors; placement conflict likely |
| BARMEN | ELBERFELD | 5.2 | Close real neighbors; placement conflict likely |
| ALTONA | HAMBURG | 7.3 | Close real neighbors; placement conflict likely |
| FURTH | NURNBERG | 7.3 | Close real neighbors; placement conflict likely |
| BERLIN | BRANDENBURG | 7.6 | **Suspicious**; Brandenburg an der Havel is much farther from Berlin |
| BOULOGNE | PARIS | 8.3 | **Ambiguous**: Boulogne-Billancourt or Boulogne-sur-Mer? Must resolve historical source |
| BAEZA | UBEDA | 8.6 | Real neighboring towns; likely placement conflict |
| CALTANISSETA | CASTROGIOVANNI | 8.8 | Real neighboring towns; likely placement conflict |
| AMSTERDAM | ZAANDAM | 10.1 | Real neighbors; review game spacing |
| BOULOGNE | VERSAILLES | 10.3 | Ambiguous town name; review |
| DELFT | DEN HAAG | 10.5 | Real neighbors; review game spacing |
| LIER | MECHELEN | 10.7 | Real neighbors; review game spacing |
| MANCHESTER | STOCKPORT | 11.3 | Real neighbors; review game spacing |

**13 pairs under 12 tiles**, and the previous audit found **56 pairs under 20 tiles**. Proximity is a warning, not proof of error.

## High-priority failure modes
1. **Unverified projection**: no independently surveyed holdout coordinates.
2. **No terrain-mask check**: towns may fall on sea, lakes, or steep terrain.
3. **Name ambiguity**: e.g., Boulogne; the original CSV contains historical alternate names and current names.
4. **Duplicate settlements**: six known, more aliases possible.
5. **Population quality**: 221 added towns use generic provisional 300 gameplay population; these are NOT 1800 census estimates.
6. **Historical anachronisms**: manually added candidate names should be reviewed for towns founded or substantially urbanized after 1800; not every modern city is appropriate.
7. **Spatial bias**: inventory selection added many Central/Eastern European candidates; country/region distribution must be reviewed against the full heightmap footprint.
8. **No actual JGRPP test**: importing JSON in the running scenario editor and verifying signs/failed placements has not happened.
9. **No release-quality 600-town import**: the current deduplicated file contains 594 towns.

## Required gate before a claim of calibration
- Establish the heightmap's geographical bounds/projection from source metadata or robust independent map landmark verification.
- Validate 20+ holdout settlements *not used for fitting* and report median and worst-case pixel/tile errors.
- Raster-check all projected town points against sea and slope, using the actual 4096x4096 heightmap; review coastal towns manually.
- Resolve duplicate aliases and ambiguous names; select six genuinely distinct, historically plausible replacement towns.
- Import in JGRPP, inspect failed-town signs and terrain conflicts, then save a new test .scn (preserve base).
- Only then rename TEST to a release candidate.

**Conclusion:** This adversarial pass found concrete reasons to distrust the existing calibration. Do not interpret in-bounds coordinates or small training-anchor residuals as proof of correctness.
