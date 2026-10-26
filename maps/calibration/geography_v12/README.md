# V12 — one full 568-town import

[Download the complete import](Europe_1800_V12_568_TOWN_FULL_IMPORT_TEST.json).
This combines the **537-town V11 baseline** with the **31 coverage additions**.
All source records retain their names, population settings, city flags and coordinates.
No new placement decisions or coordinate corrections are introduced by this merge.

**Use this file once on a fresh empty map. Do not import it into your populated
568-town save, or into the older 537-town checkpoint.** Your existing populated
save already contains the combined set; it does not need another import.

## Fresh-map instructions

1. In JGRPP 0.73.4 Scenario Editor, generate a new empty **4096×4096** map from the
   original heightmap with **counter-clockwise rotation** and your intended NewGRFs.
2. Download the JSON using GitHub's **Download raw file**, retaining `.json`.
3. Use **Town Generation → Load from file**, choosing the full V12 file **once**.
4. Expect **568 towns** if every founding succeeds; record any failures and inspect
   actual placement. Save under a new scenario filename.

Do not combine the full file with V11 or any regional/additions import. Keep all
prior saved checkpoints. No original scenario or NewGRF configuration is changed.

## Content and validation

| Component | Towns |
|---|---:|
| V11 baseline | 537 |
| Swedish additions | 20 |
| North African additions | 7 |
| Balearic additions | 4 |
| **Full import** | **568** |

The output is the original baseline array followed by the additions array; each
record is unchanged. Checks cover duplicate identities, schema, population/city
field types, coordinate bounds and exact float32 importer arithmetic. All **50**
combined pairs within the review range have documented reviews. Minimum actual
target spacing remains **15.620499 tiles**, Manchester–Oldham.

Terrain/geographic evidence is inherited from [V11](../geography_v11/README.md)
and [the coverage supplement](../coverage_additions_v1/README.md), including their
limitations and explicit deferrals. There are **143 non-flat targets** across the
two components (132 + 11); clear terrain does not imply successful founding or
future growth. The original 600-town master remains unchanged; deferred towns
are not silently reinstated.

The user supplied regional screenshots of the new towns and confirmed completion
after the 568-town count/save prompt. This is documented as
[user-reported validation](../../../data/geography/user_validation_coverage_20261026.json),
not independent decoding of the save or verification of every actual town tile.
A fresh-map, one-step V12 import has not yet been independently observed. In-game
population realization, growth and multiplayer remain separate checks.

## Reproduce

```powershell
python scripts/build_full_import.py --out scratch/full-v12
python -W error::ResourceWarning -m unittest discover -s tests -v
```

Use a new output directory. Generation never modifies either input JSON.
[summary.json](summary.json) records source/output hashes and composition checks;
[combined_spacing_audit.csv](combined_spacing_audit.csv) records the close pairs.
The full test suite passes **81 Python tests**.
