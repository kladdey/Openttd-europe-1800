# Project status

Current placement checkpoint: **V10**, committed to `main` in
[085c7a9](https://github.com/kladdey/Openttd-europe-1800/commit/085c7a97c5d75c52611a2d106acaef6a819f20d1).

| Item | Status |
|---|---|
| Preserved master catalogue | 600 records; names, populations and city flags unchanged |
| Clear-target test import | 536 towns |
| Comparison imports | 564 previously retained / 576 all in-bounds |
| Original 54 terrain flags | 27 corrected to supported clear targets; 27 unresolved |
| Supplemental terrain conflict | Orihuela; unresolved |
| Deferrals from clear candidate | 64: 28 terrain, 11 spacing, 24 outside map, 1 identity |
| Original heightmap and scenarios | Committed and hash-checked; no scenario edited |
| Automated validation | 39 Python tests and V9/V10 map smoke tests passed |
| In-game validation | Unavailable; none run |

Clear means nonzero source elevation and clear ground in both supplied scenario
terrain arrays. It does not establish exact historical placement or founding.
131 retained targets have non-flat corners in at least one supplied scenario.
The geographic transformation remains empirical; original DEM CRS is unknown.

The user currently has no OpenTTD test platform. Continue source-backed geographic
review, terrain diagnostics and spacing checks offline. Do not make game access a
prerequisite for that work. Record failed references and temporary deferrals;
never move a town solely to reach nearby land.

Start with the [V10 results and files](../maps/calibration/geography_v10/README.md),
[active workflow](GEOGRAPHY_WORKFLOW.md), [roadmap](ROADMAP.md),
[tool guide](../scripts/README.md) and [documentation index](DOCUMENTATION_INDEX.md).
The Swedish add-on and V2-V9 experiments are historical comparison artifacts,
not extra imports to append to V10. Population-source work remains separate from
game-scaled population values. Modica/Pozzallo's combined identity remains held.

Do not overwrite the 600-town master, original PNG, source `.scn` files, earlier
experiment outputs or NewGRF configuration. Publish new candidate versions to
separate directories. No arbitrary final town count or country quota is imposed.
