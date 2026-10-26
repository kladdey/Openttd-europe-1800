# Scenario tools

The geography and visualization tools are implemented. The current placement
checkpoint and limitations are tracked in [project status](../docs/PROJECT_STATUS.md).
Run commands from the repository root with Python 3.10+; no OpenTTD executable is
needed for these offline operations.

```powershell
python -m pip install -r requirements-visualization.txt
python scripts/register_coastal_regions.py --out scratch/coast-registration.json
python scripts/resolve_terrain_flags.py --preview --out scratch/reference-preview.csv
python scripts/resolve_terrain_flags.py --out scratch/v10-candidate
python scripts/visualize_evidence.py --report scratch/v10-candidate --out scratch/v10-map --version V10
python -W error::ResourceWarning -m unittest discover -s tests -v
node tests/test_evidence_map.js scratch/v10-map/evidence_map.html scratch/v10-candidate/summary.json
```

Use new output paths. The resolver uses the committed, hash-checked regional
registration artifact. The first command reproduces its coastline fit separately.
Node.js is optional and needed only for the map-logic smoke test.

| Tool | Purpose |
|---|---|
| `geography.py` | Standard-library inventory, bounds, duplicate and spacing audit |
| `scenario_geography.py` | Read-only supplied JGRPP terrain decoder and exact importer pixel mapping |
| `calibrate_heightmap.py` | V6 global coastline diagnostics and regional candidate reproduction |
| `expand_europe_towns.py` | V7 all-catalogue coverage and terrain audit |
| `review_europe_placements.py` | V8 historic-coordinate and explicit spacing review |
| `validate_landmarks.py` | V9 frozen-model landmark and terrain diagnostics |
| `register_coastal_regions.py` | Bounded coastline-only regional fitting and rejection gates |
| `resolve_terrain_flags.py` | V10 explicit historic-site corrections, coherent regional rebasing and deferrals |
| `visualize_europe_towns.py` | Earlier V7 map and atlas |
| `visualize_evidence.py` | Offline evidence HTML/PNG for a selected report directory |

See the [active workflow](../docs/GEOGRAPHY_WORKFLOW.md),
[coordinate mapping](../maps/calibration/geography_v6/README.md), and
[V10 reproduction details](../maps/calibration/geography_v10/README.md).
The original source assets and catalogue are read-only. No tool resaves a scenario
or changes NewGRF configuration. Historic-site evidence, sampled land, slope and
successful founding are distinct checks.
