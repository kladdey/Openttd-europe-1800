# Project status

Current placement checkpoint: **V11**. See the
[V11 follow-up](../maps/calibration/geography_v11/README.md) for exact files and evidence.
The earlier V10 data was committed in
[085c7a9](https://github.com/kladdey/Openttd-europe-1800/commit/085c7a97c5d75c52611a2d106acaef6a819f20d1).
Documentation was synchronized and merged in [PR #1](https://github.com/kladdey/Openttd-europe-1800/pull/1).

| Item | Status |
|---|---|
| Preserved master catalogue | 600 records; names, populations and city flags unchanged |
| Clear-target test import | 537 towns |
| Comparison imports | 564 previously retained / 576 all in-bounds |
| Original 54 terrain flags | 28 corrected to supported clear targets; 26 unresolved |
| Supplemental terrain conflict | Orihuela; unresolved |
| Deferrals from clear candidate | 63: 27 terrain, 11 spacing, 24 outside map, 1 identity |
| Heightmap provenance | Exact pixel match to UseYourIllusion’s Europe v4 (2014); original DEM CRS still unknown |
| Original heightmap and scenarios | Committed and hash-checked; no scenario edited |
| Inland checks | 10 lake basins reviewed, 7 diagnostic comparisons; Arles/Alençon bank holds remain open |
| Automated validation | 78 Python tests; V9/V10/V11 map smoke tests passed |
| In-game validation | User screenshot confirms 537 towns in JGRPP 0.73.4; checkpoint saved; exact coordinates/growth unverified |

Clear means nonzero source elevation and clear ground in both supplied scenario
terrain arrays. It does not establish exact historical placement or founding.
132 retained targets have non-flat corners in at least one supplied scenario.
The geographic transformation remains empirical; original DEM CRS is unknown.

The user now has OpenTTD access and has confirmed the 537-town count and a saved
checkpoint. Continue geographic review and terrain diagnostics offline, then test
additions in a copy of that saved map. No user save has been uploaded for decoding. Record failed references and temporary deferrals;
never move a town solely to reach nearby land.

Start with the [V11 results and files](../maps/calibration/geography_v11/README.md),
[active workflow](GEOGRAPHY_WORKFLOW.md), [roadmap](ROADMAP.md),
[tool guide](../scripts/README.md) and [documentation index](DOCUMENTATION_INDEX.md).
The Swedish add-on and V2-V10 experiments are historical comparison artifacts,
not extra imports to append to the current candidate. Population-source work remains separate from
game-scaled population values. Modica/Pozzallo's combined identity remains held.

Do not overwrite the 600-town master, original PNG, source `.scn` files, earlier
experiment outputs or NewGRF configuration. Publish new candidate versions to
separate directories. V11 reviewed all 28 prior terrain deferrals with 25 new site references,
restored Namur, and kept two clear alternatives on explicit bank-alignment holds.
No arbitrary final town count or country quota is imposed.

The [reverse audit](../maps/calibration/reverse_audit_v1/README.md) found and fixed
two inland dependency-validation gaps. No V11 candidate errors were found within
the audited structural/terrain scope. Exact minimum importer-target spacing is
15.620499 tiles (Manchester–Oldham); the legacy normalized report gives 16.221519.
Current [inland V2](../maps/calibration/inland_v2/README.md) retains all bank holds.

[Historic river-bank research](../maps/calibration/river_bank_research_v1/README.md)
strengthens both bank contexts and records the Arles boat-bridge gap in 1800.
Both held sites remain sensitive to subpixel shifts; no hold was lifted. Historic
map downloads failed with bounded requests/access errors, explicitly documented.

The [coverage supplement](../maps/calibration/coverage_additions_v1/README.md) adds
31 test towns: 20 Sweden, 7 North Africa and 4 Balearics. It is additions-only and
not yet game-tested; expected combined count is 568 if all found. Twenty new
proposals remain deferred, plus the unchanged existing Palma hold. The original
600-town master and its 27 terrain deferrals remain unchanged.
