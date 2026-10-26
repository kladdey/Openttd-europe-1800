## Playing, multiplayer and redistribution

- [Install JGRPP and the scenario](docs/INSTALLATION.md)
- [Multiplayer setup and connection troubleshooting](docs/MULTIPLAYER.md)
- [Third-party licensing and distribution policy](docs/LICENSING.md)
- [Public release checklist](docs/RELEASE_PROCESS.md)

**Release warning:** Do not publish the earlier bundled portable ZIPs as public GitHub assets. The project uses third-party NewGRFs with mixed or unverified redistribution terms. Prefer a scenario-only distribution and official upstream downloads. The V12 568-town checkpoint is the last user-confirmed town baseline; V13 (613 towns) is still an offline candidate. The separately supplied Toni multiplayer scenario has not been independently validated as equivalent to either.

# OpenTTD Europe 1800

Historical Europe scenario work for JGRPP 0.73.4, Windows 11 and a 4096×4096 map,
with an intended 1800–2025 campaign and FIRS 5.2.0 Temperate Basic industries.

The latest offline candidate is **V13: 613 towns**, with **45 additions** for the saved 568-town checkpoint. Seventeen research leads remain deferred. Use the additions-only file once on a copy of your saved map; the full file is for fresh empty maps only. All 600 original source records remain preserved.

- [V13 downloads, audit and import instructions](maps/calibration/geography_v13/README.md)

The user confirmed completion after the 568-town count/save prompt and supplied
regional screenshots. Exact actual town positions, growth and playability remain
unverified; no fresh-map one-step V12 test has yet been independently observed.

- [Complete 568-town V12 JSON — fresh maps only](maps/calibration/geography_v12/Europe_1800_V12_568_TOWN_FULL_IMPORT_TEST.json)
- [V12 composition and import instructions](maps/calibration/geography_v12/README.md)
- [31-town coverage supplement — import once into your saved 537-town map](maps/calibration/coverage_additions_v1/README.md)
- [Whole-map coverage audit — gaps and research priorities](maps/calibration/coverage_gap_audit_v1/README.md)
- [Current status and limitations](docs/PROJECT_STATUS.md)
- [Earlier V11 files, findings and instructions](maps/calibration/geography_v11/README.md)
- [Earlier 537-town baseline JSON](maps/calibration/geography_v11/Europe_1800_V11_CLEAR_TARGET_CANDIDATE_TEST.json)
- [Interactive map — download HTML and open locally](maps/calibration/geography_v11/visualization/evidence_map.html)
- [Static map](maps/calibration/geography_v11/visualization/evidence_overview.png)
- [All 600 retained/deferred decisions](maps/calibration/geography_v11/all_600_decisions.csv)
- [Heightmap source identified: UseYourIllusion’s Europe v4](maps/calibration/provenance_v1/README.md)
- [Historic river-bank research: Arles and Alençon](maps/calibration/river_bank_research_v1/README.md)
- [Reverse audit: findings and fixes](maps/calibration/reverse_audit_v1/README.md)
- [Inland lake checks and river-bank overlays](maps/calibration/inland_v2/README.md)
- [Original asset checksums](source_assets/README.md)
- [Offline workflow](docs/GEOGRAPHY_WORKFLOW.md) and [scripts](scripts/README.md)
- [Roadmap](docs/ROADMAP.md) and [all documentation](docs/DOCUMENTATION_INDEX.md)

A clear target is not a founding guarantee: 160 V13 combined targets (143 in V12) have non-flat
corners in at least one supplied scenario. Source CRS and exact historical
shoreline/river registration remain uncertain. Continue geographic review offline;
test actual founding, growth and multiplayer separately.

Preserve original assets, the master dataset, previous experiments and NewGRF
configuration. Use fresh output directories and new scenario filenames.
