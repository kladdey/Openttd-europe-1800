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
| Automated validation | 59 Python tests; V9/V10/V11 map smoke tests passed |
| In-game validation | Unavailable; none run |

Clear means nonzero source elevation and clear ground in both supplied scenario
terrain arrays. It does not establish exact historical placement or founding.
132 retained targets have non-flat corners in at least one supplied scenario.
The geographic transformation remains empirical; original DEM CRS is unknown.

The user currently has no OpenTTD test platform. Continue source-backed geographic
review, terrain diagnostics and spacing checks offline. Do not make game access a
prerequisite for that work. Record failed references and temporary deferrals;
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
