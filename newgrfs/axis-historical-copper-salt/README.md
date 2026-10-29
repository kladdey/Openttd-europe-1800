# Historical AXIS 0.3.0 copper and salt candidate

Separately built candidate for the 1830 Europe scenario. Same project GRFID
`4B484531` (KHE1), numeric version 3, minimum compatible version 2. Do not load
both Historical AXIS versions as separate entries. The 0.2.0 binary and source
are preserved. No vehicle or cargo ID changes.

Classic gains existing Salt Mine 105 and new Traditional Copper Smelter 123,
Fish Saltery 124 and Meat Curing House 125. This gives **96 industry types and
the same 64 cargo slots**. Original 92 enabled Classic recipes/properties/layouts
and every other economy's enabled models remain unchanged. New industry
registration can extend automatically generated neighbour checks.

All inputs in each new processor's batch are mandatory:

| Type | Inputs | Outputs |
| --- | --- | --- |
| Traditional Copper Smelter | 6 CORE, 18 COAL, 1 SAND | 1 COPR, 4 SLAG |
| Fish Saltery | 3 FISH, 1 SALT | 3 FOOD |
| Meat Curing House | 3 LVST, 1 SALT | 3 FOOD |

These are explicitly game batches, not historical ore assays or universal curing
yields. Copper uses a coal-fired Welsh-process abstraction, not acid leaching or
electrolysis. Salt is not converted into food on its own. Slag has no 1830
industrial sink and is a waste by-product. The existing wharf accepts copper
exports and existing ports accept food. No modern downstream technology is
backdated. Existing graphical layouts are reused as visual proxies.

## Build and reproduce

First prepare/build 0.2.0 using its pinned instructions in
[the base fork](../axis-historical-europe/README.md). From repository root:

```powershell
newgrfs/axis-historical-europe/.venv/Scripts/python.exe newgrfs/axis-historical-copper-salt/build_candidate.py
newgrfs/axis-historical-europe/.venv/Scripts/python.exe newgrfs/axis-historical-copper-salt/validate_models.py
newgrfs/axis-historical-europe/.venv/Scripts/python.exe scripts/industrial_phase6b_rules.py --candidate
```

For a subsequent candidate rebuild use `build_candidate.py --rebuild`. It archives
the preceding candidate artifact and never edits the 0.2.0 source or GRF.
Do not rebuild into a running test library: rerun registration into a new case.

Runtime scripts require the local exact 15-GRF library, the original 617-town
baseline and JGRPP 0.73.4 at the paths recorded in the research. They create
unique disposable directories and leave normal game configuration untouched:

```powershell
python scripts/industrial_phase6b_register_candidate.py
python scripts/industrial_phase6b_availability.py
python scripts/industrial_phase6b_controls.py copper
python scripts/industrial_phase6b_controls.py meat
python scripts/industrial_phase6b_controls.py fish
python scripts/industrial_phase6b_validate_controls.py
python -m unittest discover -s tests -p test_industrial_phase6b.py -v
```

`package.py --verify-rebuild`, run with the pinned build environment, produces a
local complete corresponding-source ZIP and checks its reconstructed GRF hash.
Generated GRFs, licensed source assets, source ZIPs and disposable saves are
excluded from Git. Only the overlay, code, manifests and research are committed.

## Migration

The 438-industry 0.2.0 working copy was upgraded in a **new file**, using an
engine-generated 0.3.0 reference record. The engine preserved all existing
industry IDs/types/locations, all 617 complete town records and every map byte
before new placement. This verifies that particular append-only migration,
not every arbitrary save. Preserve old versions and exact checksums. Downgrading
a map containing IDs 105/123/124/125 to 0.2.0 is unsupported. Stock AXIS is a
different migration problem and is not a compatible replacement for this file.

See [copper/salt validation](../../docs/COPPER_SALT_1830_VALIDATION.md),
[placement results](../../docs/INDUSTRY_PLACEMENT_RESULTS.md) and
[readiness](../../docs/INDUSTRIALIZED_SCENARIO_READINESS.md). No push or merge.
