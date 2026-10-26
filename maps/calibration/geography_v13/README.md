# V13 coverage additions — 45 new town candidates

The 62 research leads from the whole-map audit yield **45 additions**, **17 deferrals**, and a **613-town full candidate**. Existing 568 records are preserved exactly. The original 600-town master and all original assets remain unchanged. Earlier holds for Cagliari, Napoli, Oran, Annaba, Visby and Ibiza are not lifted.

## Test on your saved map

1. Keep your saved 568-town scenario as a backup and open a copy in JGRPP 0.73.4 Scenario Editor.
2. Download [Europe_1800_V13_ADDITIONS_ONLY_TEST.json](Europe_1800_V13_ADDITIONS_ONLY_TEST.json) using the raw/download button; ensure it remains JSON.
3. Under Town Generation → Load from file, import this additions-only file **once**. Expected total if all found: **613 towns**.
4. Inspect the new towns, especially slopes and coastal references. A clear source tile does not guarantee founding. If the total differs, identify missing towns before retrying; do not load the whole file again.
5. Save under a new filename, keeping the 568-town checkpoint.

[Europe_1800_V13_FULL_IMPORT_TEST.json](Europe_1800_V13_FULL_IMPORT_TEST.json) is exclusively for a **fresh empty 4096×4096 map**, using the original heightmap and established counterclockwise import rotation. Never load the full file into a populated map. Preserve NewGRFs.

## Method and limits

Published approximate city coordinates use the existing frozen V6 empirical model: source column = 104.42263446189997 × longitude + 1379.7176323206816; source row = −164.09816527178702 × latitude + 9729.142746398953. Import JSON x = row / 4095 and y = column / 4095. Float32/truncation determines actual target tiles; source column = 4095 − game tile x and source row = game tile y. This is an established empirical fit, not a recovered original CRS or survey-grade transform.

Targets must have nonzero original raster elevation and clear ground in both supplied scenarios, including all nine deterministic half-pixel probes. These probes are sensitivity checks, not an uncertainty bound. Seventeen retained additions have non-flat target corners. These are offline candidates: the user's current saved map has not been decoded, and founding, precise historic river banks, coastlines and growth remain unverified.

Eight references fail base terrain checks, eight fail sensitivity checks, and Helsingør is deferred at about 9.2 tiles from Helsingborg. Braga and Guimarães receive an individual retain-both review at about 22.8 tiles: distinct historic centres, modest starting populations. No nearest-land search, coordinate shift or final town-count quota is used. Historic landmark alternatives remain further research; they were not substituted to force an import.

New populations are provisional game settings, not census estimates: 350, except Oban and Merthyr Tydfil at 200. All new city flags are false. Existing populations and flags are unchanged. Per-town historical rationale and source URLs are in the input configuration and decision CSV; role descriptions do not claim exact historical population or footprint.

## Audit and reproduce

- [Every candidate and decision](all_candidate_decisions.csv)
- [Deferred towns and reasons](deferred_towns.csv)
- [Nearest neighbours](nearest_neighbours.csv)
- [New close-pair reviews](new_spacing_review.csv)
- [All combined close pairs](combined_spacing_audit.csv)
- [Terrain sensitivity probes](sensitivity_probes.csv)
- [Counts, hashes and limitations](summary.json)
- [Research configuration](../../../data/geography/gap_additions_v1.json)

From the repository root, with the existing Python dependencies installed:

```sh
python scripts/build_gap_additions.py --out /tmp/europe_v13_rebuild
python -W error::ResourceWarning -m unittest discover -s tests
```

Use a new output directory; the builder refuses to overwrite one. It verifies original asset, master, V12 and frozen-model hashes. Tests cover all 62 decisions, full-import composition, coordinate bounds, duplicate identities, all addition terrain probes and spacing reviews.
