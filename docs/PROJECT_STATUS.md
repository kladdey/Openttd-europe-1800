## Economy and vehicle overhaul - 2026-10-27

The three-company 1800-1813 multiplayer session was a **disposable playtest**, not the campaign save. The player reported insufficient FIRS Temperate Basic industry variety and poor early-era vehicle choice (two-horse passenger versus six-horse mail carriage; no useful trains by 1813). **AXIS Extreme Classic is a candidate only**, not installed or verified. Priorities: audit early road/rail/ship NewGRFs, verify AXIS's cargo compatibility and JGRPP 0.73.4 behavior, and plan historical industry progression on fresh scenario copies. See [economy and vehicle overhaul](ECONOMY_VEHICLE_OVERHAUL.md).

## Multiplayer playtest - 2026-10-26

**Confirmed by user:** Squirrel joined the hosted Europe 1800 game and was able to play on the 4096 x 4096 map using the current multiplayer setup. This verifies at least one successful end-to-end client join, scenario load and gameplay session. It does **not** establish long-duration stability, a clean-install test, or Toni's compatibility. Toni previously received 'Network - Game connection lost'; cause remains unknown.

## October 2026 multiplayer and release notes

A separate user-supplied **Europe 1800 - Toni** scenario was packaged for JGRPP 0.73.4, Windows. The earlier portable build included the game and nine NewGRFs; its ZIP integrity was checked, but Windows execution and multiplayer were **not** validated. Toni reported **"Network - Game connection lost"**; root cause is unknown. See [multiplayer diagnostics](MULTIPLAYER.md).

The 568-town V12 checkpoint remains the last user-confirmed town-placement baseline. The 613-town V13 candidate remains untested. The Toni scenario is a separate supplied file and must not be silently identified with V13.

A prior public release was deleted by the repository owner. **Do not re-upload the portable bundles as public releases** pending a full licensing audit. A scenario-only distribution with upstream downloads is the preferred route. See [licensing](LICENSING.md), [installation](INSTALLATION.md) and [release process](RELEASE_PROCESS.md).

# Project status

Current offline candidate: [V13 coverage implementation](../maps/calibration/geography_v13/README.md), 45 additions to the saved 568-town map, 613 full candidate, 17 deferred research leads. Run `python scripts/build_gap_additions.py --out /tmp/europe_v13_rebuild` from the repository root. The V12 checkpoint remains the last user-confirmed component; V13 founding is pending. Earlier version-specific details below remain historical.

Current full import checkpoint: **V12, 568 towns**. See the
[combined import](../maps/calibration/geography_v12/README.md); V11 remains the preserved 537-town component. See the
[V11 follow-up](../maps/calibration/geography_v11/README.md) for exact files and evidence.
The earlier V10 data was committed in
[085c7a9](https://github.com/kladdey/Openttd-europe-1800/commit/085c7a97c5d75c52611a2d106acaef6a819f20d1).
Documentation was synchronized and merged in [PR #1](https://github.com/kladdey/Openttd-europe-1800/pull/1).

| Item | Status |
|---|---|
| Preserved master catalogue | 600 records; names, populations and city flags unchanged |
| Full test import | 568 towns: preserved 537-town V11 baseline + 31 additions |
| Comparison imports | 564 previously retained / 576 all in-bounds |
| Original 54 terrain flags | 28 corrected to supported clear targets; 26 unresolved |
| Supplemental terrain conflict | Orihuela; unresolved |
| Deferrals from clear candidate | 63: 27 terrain, 11 spacing, 24 outside map, 1 identity |
| Heightmap provenance | Exact pixel match to UseYourIllusion’s Europe v4 (2014); original DEM CRS still unknown |
| Original heightmap and scenarios | Committed and hash-checked; no scenario edited |
| Inland checks | 10 lake basins reviewed, 7 diagnostic comparisons; Arles/Alençon bank holds remain open |
| Automated validation | 86 Python tests; V9/V10/V11 map smoke tests passed |
| In-game validation | 537-count screenshot; supplement regional views and completion confirmation after 568-count/save prompt; no save supplied |

Clear means nonzero source elevation and clear ground in both supplied scenario
terrain arrays. It does not establish exact historical placement or founding.
V11 has 132 non-flat targets and the supplement adds 11, for 143 combined.
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

The [V12 full JSON](../maps/calibration/geography_v12/README.md) is an exact merge,
not a replacement import for an already populated save. All records are unchanged.
The user confirmed completion after the 568-count/save prompt; this is recorded as
user-reported feedback. A fresh-map one-step V12 import remains to be tested.

The [whole-map coverage screen](../maps/calibration/coverage_gap_audit_v1/README.md)
records 62 research leads and 83 distinct existing deferrals, with no new import
or coordinate change. Priority gaps include Jutland/Funen, southern Norway, Wales,
northern Spain, Portugal, Corsica/Sardinia, Crete, southern Italy and the western
Belarus strip. Distance alone does not justify filling rural or mountain terrain.
