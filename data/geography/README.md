# Geographic calibration evidence

Current offline candidate: [V13 coverage implementation](../../maps/calibration/geography_v13/README.md), 45 additions to the saved 568-town map, 613 full candidate, 17 deferred research leads. Run `python scripts/build_gap_additions.py --out /tmp/europe_v13_rebuild` from the repository root. The V12 checkpoint remains the last user-confirmed component; V13 founding is pending. Earlier version-specific details below remain historical.

`ne_50m_europe_coastline.geojson` is a derived subset of Natural Earth's
1:50m coastline, not a town gazetteer or exact historic coastline.

- Repository: `nvkelso/natural-earth-vector`.
- Source path: `geojson/ne_50m_coastline.geojson`.
- Retrieved source blob: `4ead47f5323a3a71495a12442ba936c969b6fae2`.
- Repository head at retrieval: `ca96624a56bd078437bca8184e78163e5039ad19`.
- [Pinned source](https://github.com/nvkelso/natural-earth-vector/blob/ca96624a56bd078437bca8184e78163e5039ad19/geojson/ne_50m_coastline.geojson).
- [Public-domain terms](https://www.naturalearthdata.com/about/terms-of-use/).
- Subset SHA-256: `f5d53fa83d12ee15a5e56e081651ec72ec45a29a30b7340e7250c8af6c83cc3f`.

Subset procedure: retain contiguous LineString coordinate runs with longitude
in [-13,36] and latitude in [30,65], discard runs shorter than two vertices,
and do not connect disconnected runs across the crop. Preserve original
vertex order and coordinates; replace descriptive feature properties with
`source: Natural Earth 1:50m coastline`. The committed file contains 153
LineStrings (151038 bytes), so reproduction needs no network request.

`regional_coordinate_overrides.csv` explicitly corrects Brandenburg to the
published approximate coordinate for Brandenburg an der Havel (52.417N,
12.533E), instead of the draft's Berlin-adjacent location. This is a regional
coordinate correction, not a population change or a training control.
The original catalogue and draft CSV remain untouched. Other draft town
coordinates are carried through provisionally, not silently declared surveyed.

## Current interpretation and review tables

V7 onward uses the documented provisional Boulogne-sur-Mer interpretation in the
full candidate. The older Paris-suburb input is not treated as geographically valid.
This is still an inference rather than a completed primary population-unit join;
see the V7 override table and V8/V10 decisions. Modica/Pozzallo remains held.

V10 evidence is in `historic_centre_references_v10.csv`,
`coastal_regions_v10.json`, `coastal_registration_v10.json`,
`terrain_decisions_v10.csv`, `supplemental_terrain_flags_v10.csv` and
`spacing_decisions_v10.csv`. These preserve attempted references, rejected models,
explicit outcomes and the newly exposed Orihuela case. Geographic correction comes
before proximity; no fitted model optimizes town land or a desired town count.

See [project status](../../docs/PROJECT_STATUS.md),
[V10 methodology](../../maps/calibration/geography_v10/README.md) and the
[active workflow](../../docs/GEOGRAPHY_WORKFLOW.md). The source CRS remains unknown;
coast-normal diagnostics are not survey accuracy or named-river validation.

## V11 source-review follow-up

The current profile is `placement_profile_v11.json`, with
`historic_centre_references_v11.csv`, `terrain_decisions_v11.csv` and
`spacing_decisions_v11.csv`. `remaining_case_research_v11.csv` records all 28
prior deferrals and `source_exclusions_v11.csv` records rejected/insufficient
lookup results. No geographic model is refitted in V11.

References carry explicit placement review states. Even clear land is ineligible
when bank alignment, source identity or historical context is held. Nine new
site references collapse onto previously sampled importer pixels. One additional
town is restored; remaining cases are documented, with all 600 master records
preserved. See [V11 findings](../../maps/calibration/geography_v11/README.md).

## Inland diagnostic sources

`inland_observations_v1.json` and `river_bank_observations_v1.json` document the
pinned public-domain Natural Earth geometry subsets, hashes and explicit image
observations. [Results and reproduction](../../maps/calibration/inland_v2/README.md)
retain all V11 coordinates and river-bank holds. Basin plateaus and generalized
centerlines must not be treated as surveyed controls or automatic town corrections.

`historic_river_bank_research_v1.json` records dated bank/crossing evidence, source
access status, inaccessible map locators and unresolved registration. Its
[offline report](../../maps/calibration/river_bank_research_v1/README.md) keeps both
V11 bank holds and all existing coordinates.

`coverage_additions_v1.json` supplies source-backed additions-only test generation;
[31-town supplement and audits](../../maps/calibration/coverage_additions_v1/README.md).
It preserves V11 and the old Swedish source pack.
`user_validation_v11_20261026.json` distinguishes the user-confirmed 537-town count
and saved checkpoint from unverified exact positions and growth.

`user_validation_coverage_20261026.json` records regional screenshot feedback and
the user’s completion confirmation after the 568-count/save prompt; no combined-count
screenshot or saved scenario was supplied. [V12](../../maps/calibration/geography_v12/README.md)
is the exact single-file merge for fresh maps only.

`coverage_gap_research_v1.json` contains 62 cited, approximate research points and
21 overlapping study windows. [The coverage screen](../../maps/calibration/coverage_gap_audit_v1/README.md)
does not generate town imports, change V12 or lift any recorded deferral.
