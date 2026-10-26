# Openttd-europe-1800
Home project 

## Europe 1800 geography work

The latest evidence pass is **V9**: 22 named landmark checks, diagnostics for
54 retained terrain flags, a Modica/Pozzallo source investigation, and an
offline interactive evidence map. The import remains the V8 564-town candidate;
V9 makes no coordinate or population changes and runs no in-game tests.

- [V9 findings, limitations and reproduction](maps/calibration/geography_v9/README.md)
- [Interactive evidence map — download HTML and open locally](maps/calibration/geography_v9/visualization/evidence_map.html)
- [Static evidence map](maps/calibration/geography_v9/visualization/evidence_overview.png)
- [Landmark observations](maps/calibration/geography_v9/landmark_contact_sheet.png)


The latest town-placement desk review is **V8**: a proposed 564-town candidate and a separate
corrected full 576-town comparison import. Two Sicilian inputs were corrected
before reviewing close pairs. All 600 source entries remain accounted for;
54 retained terrain flags and in-game founding remain unresolved.

- [V8 review, evidence and reproduction](maps/calibration/geography_v8/README.md)
- [Proposed 564-town candidate](maps/calibration/geography_v8/Europe_1800_V8_DESK_REVIEWED_CANDIDATE_TEST.json)
- [Corrected full 576-town import](maps/calibration/geography_v8/Europe_1800_V8_CORRECTED_ALL_IN_BOUNDS_TEST.json)
- [All 600 retained/deferred decisions](maps/calibration/geography_v8/all_600_decisions.csv)
- [Refined terrain contact sheet](maps/calibration/geography_v8/terrain_review_contact_sheet.png)

- [V7 results and import instructions](maps/calibration/geography_v7/README.md)
- [Full 576-town test JSON](maps/calibration/geography_v7/Europe_1800_V7_ALL_IN_BOUNDS_TEST.json)
- [Complete 600-record audit](maps/calibration/geography_v7/all_600_placement_audit.csv)

- [V6 results, coordinate mapping and import instructions](maps/calibration/geography_v6/README.md)
- [Corrected regional town JSON](maps/calibration/geography_v6/Europe_1800_V6_REGIONAL_GEOGRAPHIC_TEST.json)
- [Regional spacing audit](maps/calibration/geography_v6/regional_spacing.csv)
- [Deferred town report](maps/calibration/geography_v6/regional_deferred.csv)
- [Original source asset manifest](source_assets/README.md)
- [Earlier audit checkpoint](docs/GEOGRAPHY_WORKFLOW.md)

From the repository root, with Python 3.10+:

```powershell
python -m pip install -r requirements-geography.txt
python -m unittest discover -s tests -v
python scripts/calibrate_heightmap.py --assets source_assets --out scratch/v6-reproduction
python scripts/expand_europe_towns.py --out scratch/v7-reproduction
python scripts/review_europe_placements.py --out scratch/v8-reproduction
```

The output directory must be new. The 600-town master catalogue, previous
V2/V3/V4 experiments and original scenarios remain preserved. Use a fresh
empty map for testing; never import into the existing playable scenario.
