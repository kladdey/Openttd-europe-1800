# OpenTTD Europe 1800

Historical Europe scenario work for JGRPP 0.73.4, Windows 11 and a 4096×4096 map,
with an intended 1800–2025 campaign and FIRS 5.2.0 Temperate Basic industries.

The latest placement checkpoint is **V11**: a **537-town clear-target test import**,
plus separate 564- and 576-town comparisons. All 600 source records and original
populations remain preserved. Twenty-eight original terrain flags have clear-site corrections;
27 terrain cases remain unresolved, including the additional Orihuela conflict.
No in-game tests have been run; the user currently has no test platform.

- [Current status and limitations](docs/PROJECT_STATUS.md)
- [Candidate files, findings and import instructions](maps/calibration/geography_v11/README.md)
- [537-town candidate JSON](maps/calibration/geography_v11/Europe_1800_V11_CLEAR_TARGET_CANDIDATE_TEST.json)
- [Interactive map — download HTML and open locally](maps/calibration/geography_v11/visualization/evidence_map.html)
- [Static map](maps/calibration/geography_v11/visualization/evidence_overview.png)
- [All 600 retained/deferred decisions](maps/calibration/geography_v11/all_600_decisions.csv)
- [Original asset checksums](source_assets/README.md)
- [Offline workflow](docs/GEOGRAPHY_WORKFLOW.md) and [scripts](scripts/README.md)
- [Roadmap](docs/ROADMAP.md) and [all documentation](docs/DOCUMENTATION_INDEX.md)

A clear target is not a founding guarantee: 132 candidate targets have non-flat
corners in at least one supplied scenario. Source CRS and exact historical
shoreline/river registration remain uncertain. Continue geographic review offline;
reserve founding, growth and multiplayer checks for when OpenTTD is available.

Preserve original assets, the master dataset, previous experiments and NewGRF
configuration. Use fresh output directories and new scenario filenames.
