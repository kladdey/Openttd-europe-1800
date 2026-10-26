# Openttd-europe-1800
Home project 

## Europe 1800 geography work

The latest experiment is the **V7 complete map-covered import**: 576 towns
from the 600-town master, with 24 outside-map entries documented separately.
Close neighbours and terrain-risk targets are included and flagged for review.
It is not yet validated by founding the towns in OpenTTD.

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
```

The output directory must be new. The 600-town master catalogue, previous
V2/V3/V4 experiments and original scenarios remain preserved. Use a fresh
empty map for testing; never import into the existing playable scenario.
