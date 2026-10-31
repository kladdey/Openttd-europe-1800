# OpenTTD Europe — Historical 1830–2025

A historically inspired, **4096 × 4096 Europe** transport scenario for **JGR's Patch Pack 0.73.4**, intended for a three-company multiplayer campaign. Development is ongoing: this is **not** a fully validated 1830–2025 release.

## Current playable development baseline (Phase 7B)

| Item | Verified development state |
|---|---|
| Towns | **617** |
| Starting industries | **542**, including 75 additional inland markets |
| Historical AXIS | **0.5.0 legacy-lifecycle candidate** (separate opt-in profile) |
| Active NewGRFs | **15**, exact versions/checksums required |
| Starting calendar / economy dates | **1830 / 1800** |
| Train length limit | **7 tiles** |
| Lifecycle | Scheduled industry opening/closure demonstrated; four original extractive sites in guarded depletion pilot |
| Readiness | **READY WITH CAVEATS** for controlled testing; not a 195-year certification |

**Start here:** [Current project status](docs/PROJECT_STATUS.md) · [Roadmap](docs/ROADMAP.md) · [Documentation index](docs/DOCUMENTATION_INDEX.md) · [Phase 7B readiness](docs/PHASE_7B_READINESS.md).

### What has been implemented

- **Phases 1–4:** vehicle and transport economy audit, with real JGRPP tests; [audit index](docs/VEHICLE_TRANSPORT_AUDIT_INDEX.md).
- **Phase 6B:** industrialized Europe and historical copper/salt processing; [readiness](docs/INDUSTRIALIZED_SCENARIO_READINESS.md).
- **Phase 6C:** 75 inland retail industries in 61 towns, 542 industries total; FOOD acceptance destinations **13 → 76**, GOOD **12 → 69**. [Readiness](docs/INLAND_MARKETS_READINESS.md) · [coverage](docs/INLAND_MARKET_COVERAGE.md) · [gameplay evidence](docs/INLAND_MARKET_GAMEPLAY_VALIDATION.md).
- **Phase 7A:** persistent server-side GameScript lifecycle and guarded NewGRF closure mechanism; separate **0.4.0** candidate. [Lifecycle documentation](docs/DOCUMENTATION_INDEX.md).
- **Phase 7B:** guarded decline, warnings, closure and service-sensitive finite extensions for **four** existing mines (out of 44 extractive sites); separate **0.5.0** candidate. [Readiness](docs/PHASE_7B_READINESS.md) · [safety](docs/PHASE_7B_MIGRATION_AND_SAFETY.md).
- **Phase 7C:** historical industrial expansion is **planned, not implemented or validated**.

### Run the Phase 7B local candidate

From the repository root, on the development PC with the locally built assets:

```powershell
python scripts/lifecycle_phase7b_launch.py
# Scenario Editor inspection:
python scripts/lifecycle_phase7b_launch.py --editor
```

The launcher verifies the isolated profile's local scenario, NewGRF and GameScript assets. **These binaries are not necessarily in GitHub**; cloning the repository alone is not a complete playable installation. See [Phase 7B readiness](docs/PHASE_7B_READINESS.md), [installation](docs/INSTALLATION.md) and [multiplayer](docs/MULTIPLAYER.md).

**Do not replace the NewGRF in an ongoing save.** Phase 7B's 0.5.0 candidate and GS v2 require an explicit compatible migration; automatic legacy-mine enrollment in old saves is not supported. Preserve earlier 0.3/0.4 scenarios and their GRFs.

### What is not yet proven

- Three simultaneous human clients with lifecycle closures, reconnects and competitive service.
- A balanced full **1830–2025** unattended simulation.
- Continent-wide depletion (only four original sites are enrolled).
- All coastal GOOD and Europe copper export routes.
- Profitable new-build horse-only freight networks in the tested 1830 cases.
- Automatic historically accurate industrial expansion across all eras.

### Historical geography archive

The original Europe **1800** geography research remains available: [V12 568-town checkpoint](maps/calibration/geography_v12/README.md) and [V13 613-town offline candidate](maps/calibration/geography_v13/README.md). Those are **earlier checkpoints**, not the latest 617-town industrialized scenario. Older documents retain their historical claims and should not be read as current build instructions.

### Multiplayer, licensing and release

- [Installation and exact asset requirements](docs/INSTALLATION.md)
- [Multiplayer tests and troubleshooting](docs/MULTIPLAYER.md)
- [Third-party licensing](docs/LICENSING.md)
- [Release process](docs/RELEASE_PROCESS.md)

**Do not redistribute unlicensed third-party NewGRF/JGRPP bundles.** Prefer scenario-only distribution with official upstream downloads and exact version/checksum instructions after a licensing review.

The development evidence reports describe tests performed by the project tooling; they do not establish independent external reproduction.
