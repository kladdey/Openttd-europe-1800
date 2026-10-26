# Scenario tools

The geography and visualization tools are implemented. The current placement
checkpoint and limitations are tracked in [project status](../docs/PROJECT_STATUS.md).
Run commands from the repository root with Python 3.10+; no OpenTTD executable is
needed for these offline operations.

```powershell
python -m pip install -r requirements-visualization.txt
python scripts/register_coastal_regions.py --out scratch/coast-registration.json
python scripts/resolve_terrain_flags.py --profile data/geography/placement_profile_v11.json --preview --out scratch/reference-preview.csv
python scripts/review_remaining_terrain.py --out scratch/v11-candidate
python scripts/visualize_evidence.py --report scratch/v11-candidate --out scratch/v11-map --version V11
python -W error::ResourceWarning -m unittest discover -s tests -v
node tests/test_evidence_map.js scratch/v11-map/evidence_map.html scratch/v11-candidate/summary.json
```

Use new output paths. The resolver uses the committed, hash-checked regional
registration artifact. The first command reproduces its coastline fit separately.
Node.js is optional and needed only for the map-logic smoke test.

| Tool | Purpose |
|---|---|
| `validate_inland_features.py` | Frozen-model inland shape diagnostics, explicit component observations and reproducible lake/river overlays |
| `river_bank_diagnostics.py` | Read-only named-river and saved-terrain overlays called by the inland validator |
| `audit_heightmap_provenance.py` | Validate PNG fingerprints and compare decoded pixels against a package without archive extraction |
| `geography.py` | Standard-library inventory, bounds, duplicate and spacing audit |
| `scenario_geography.py` | Read-only supplied JGRPP terrain decoder and exact importer pixel mapping |
| `calibrate_heightmap.py` | V6 global coastline diagnostics and regional candidate reproduction |
| `expand_europe_towns.py` | V7 all-catalogue coverage and terrain audit |
| `review_europe_placements.py` | V8 historic-coordinate and explicit spacing review |
| `validate_landmarks.py` | V9 frozen-model landmark and terrain diagnostics |
| `register_coastal_regions.py` | Bounded coastline-only regional fitting and rejection gates |
| `resolve_terrain_flags.py` | Versioned explicit site corrections, coherent regional rebasing and deferrals; defaults to V10 for reproduction |
| `review_remaining_terrain.py` | Current V11 follow-up, source exclusions, bank-review holds and V10 delta |
| `visualize_europe_towns.py` | Earlier V7 map and atlas |
| `visualize_evidence.py` | Offline evidence HTML/PNG for a selected report directory |

See the [active workflow](../docs/GEOGRAPHY_WORKFLOW.md),
[coordinate mapping](../maps/calibration/geography_v6/README.md), and
[V11 reproduction details](../maps/calibration/geography_v11/README.md).
The original source assets and catalogue are read-only. No tool resaves a scenario
or changes NewGRF configuration. Historic-site evidence, sampled land, slope and
successful founding are distinct checks.

Omitting the shared resolver profile reproduces V10 intentionally. Use the V11
follow-up command above for the current candidate; all output paths must be new.
