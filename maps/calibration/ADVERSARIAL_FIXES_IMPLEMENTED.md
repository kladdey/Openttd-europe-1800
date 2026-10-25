# Implemented adversarial fixes - v0.2

**Status: working test import, not release-calibrated.**

- 600 town records, all unique by exact case-insensitive name.
- Six duplicates removed: VIENNE/WIEN, Gdańsk/DANZIG, Elbląg/ELBING, Brno/BRNO, Szczecin/STETTIN, Wrocław/BRESLAU.
- Six historically established distinct replacements: Głogów, Łowicz, Sieradz, Rawicz, Písek, Krems.
- Corrected BRANDENBURG (Brandenburg an der Havel) from erroneously near Berlin to 52.4125 N, 12.5561 E, then projected approximate map position.
- BOULOGNE retained near Paris according to source geocoding; historical identity remains to be confirmed.
- All six new towns use provisional 300 gameplay population, not census claims.

## Not fixed yet

- Projection is still based on the same 29 manually estimated reference points, not independently verified.
- Land/water/slope checks against the original full-resolution heightmap have not been completed.
- No JGRPP 0.73.4 test import or founding-success count has been run.
- Modern place names and historical year-specific settlement status still need review.
- This file must not be called a final playable scenario.

Reference: `data/towns/europe_1800_import_AUDIT_FIXED_TEST.json`.
