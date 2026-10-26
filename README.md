# Openttd-europe-1800
Home project 

## Europe 1800 geography work

The latest experiment is the **V6 corrected regional test**: 36 towns, with
7 further regional entries deferred for documented review. It is not yet
validated by founding the towns in OpenTTD.

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
```

The output directory must be new. The 600-town master catalogue, previous
V2/V3/V4 experiments and original scenarios remain preserved. Use a fresh
empty map for testing; never import into the existing playable scenario.
