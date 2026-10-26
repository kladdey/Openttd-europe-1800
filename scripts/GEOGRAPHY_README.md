# Reproducible town geography tools

See [the complete workflow](../docs/GEOGRAPHY_WORKFLOW.md) for coordinate
conventions, evidence requirements, dependencies and OpenTTD import instructions.
See [deferred decisions](../maps/calibration/geography_v5_audit_DEFERRED.md)
and [the generated summary](../maps/calibration/geography_v5_audit/summary.json).

From the repository root:

```powershell
python scripts/geography.py audit --out scratch/new-geography-audit
python -m unittest discover -s tests -v
```

The output directory must not already exist. Audit needs Python 3.10+ only;
optional calibration and raster commands require `requirements-geography.txt`.
No command modifies the source catalogue, previous experiments or scenarios.
The current output is diagnostic: original raster and importer orientation
evidence are required before generating corrected import coordinates.
