# Current local installation — Phase 7H (development only)

The latest separate development candidate is **Europe 1830 Historical AXIS 0.6.0 - Phase 7H Industrial Transformation.scn**. It retains **617 towns / 542 initial industries**, JGRPP **0.73.4**, unchanged Historical AXIS **0.6.0**, the exact **15 NewGRFs / 64 cargos**, calendar/economy **1830/1800** and seven-tile trains. Its isolated profile packages **GS v7/schema 6**. Verdict: **READY WITH CAVEATS for controlled playtesting**, not multiplayer certification.

On the development Windows PC, from the repository root:

```powershell
python scripts/transformation_phase7h_launch.py --verify-only
python scripts/transformation_phase7h_launch.py
# Optional Scenario Editor inspection:
python scripts/transformation_phase7h_launch.py --editor
```

The scenario is in `C:\Users\Kladd\Documents\OpenTTD\scenario`. SHA-256: `88d7a56e341ba7c2972e634fe3c8ec779e6357e6f2ab09adac2e2746c01aa647`. Use the [manifest-pinned isolated profile](research/phase7h_candidate_delivery.json), not the normal OpenTTD configuration. The [readiness report](PHASE_7H_READINESS.md) separates observed effects from untested milestones. Accelerated fixture saves are not the normal 1830 campaign.

**Compatibility:** start a fresh separate candidate. GS v7/schema 6 refuses older running-save schemas/contracts; no automatic migration is provided. Do not replace GRFs or scripts in an ongoing save. Earlier candidates remain distinct:

| Candidate | GS / schema | Launcher | Evidence |
|---|---|---|---|
| Phase 7D established baseline | v4 / 4 | `lifecycle_phase7d_launch.py` | [Readiness](PHASE_7D_READINESS.md) |
| Phase 7F ports | v5 / 4 | `ports_phase7f_launch.py` | [PARTIAL; shipping unresolved](PHASE_7F1_MARITIME_CONNECTIVITY.md) |
| Phase 7G cycles | v6 / 5 | `cycles_phase7g_launch.py` | [Readiness](PHASE_7G_READINESS.md); active reload subsequently passed in 7H |
| Phase 7H transformations | v7 / 6 | `transformation_phase7h_launch.py` | [Current readiness](PHASE_7H_READINESS.md) |

Compiled scenarios, GRFs and local dependencies are not included in a Git clone. Other machines need the exact licensed assets and matching server-side GS/policy. This PC's absolute-path manifest is not a portable installer. Verify all checksums before hosting. See [multiplayer](MULTIPLAYER.md), [licensing](LICENSING.md) and [release process](RELEASE_PROCESS.md).

---

## Earlier Europe 1800 installation guidance (historical)

# Installation - Europe 1800

## Recommended public distribution

Use a **scenario-only** archive. This avoids mirroring JGRPP and NewGRF binaries whose distribution conditions vary.

1. Install **JGR's Patch Pack 0.73.4** from the [official releases](https://github.com/JGRennison/OpenTTD-patches/releases). Use the same build as the host.
2. Put the provided `.scn` file in the scenario directory used by your JGRPP installation (commonly `Documents\\OpenTTD\\scenario` on Windows; portable configurations can use a different directory).
3. Start JGRPP and choose **Play Scenario**.
4. If the game reports missing NewGRFs, use **Find missing content online** or the **Online Content** menu. Obtain **the exact versions** specified in the scenario.
5. If automatic downloading fails, obtain the matching file from its original publisher and place it in the NewGRF directory that your JGRPP installation actually uses. Restart or rescan content.
6. Start the scenario and check the NewGRF list and FIRS economy before multiplayer.

### Previously identified NewGRFs

- FIRS Industries 5 **5.2.0** (Temperate Basic)
- Sailing Ships community **0.73**
- Polish Rolling Stock Pack **0.19.11**
- Industrial Stations Renewal **1.0.2**
- CHIPS Station Set 2 **2.0.0**
- eGRVTS **v2.1 r240**
- UKRS2 **1.05**
- av8 Aviators Aircraft Set **2.21**
- Polish Train Set **3.0.3**

This list came from the prior multiplayer package configuration. The **scenario's own embedded NewGRF requirements are authoritative**. If they differ, record and investigate the difference.

## Which map?

- **V12**: saved 568-town checkpoint, user-tested town placement; the latest known user-approved town baseline.
- **V13**: offline 613-town candidate, **not yet in-game validated**.
- **Toni multiplayer scenario**: a separate user-supplied `.scn` file, not automatically equivalent to V13. Do not silently overwrite it with an experimental import.

The scenario may require substantial RAM and time to load: the map is **4096 x 4096**.

## Portable installs

OpenTTD/JGRPP may read content from a user data directory rather than the directory containing `openttd.exe`. If the scenario or NewGRFs do not appear, inspect the actual content paths and active configuration. Do not assume copying files next to the executable is sufficient.

## Known limitation

The earlier complete portable ZIP was archive-tested but **not Windows-launch-tested**. It should not be treated as a validated public release. See [LICENSING.md](LICENSING.md).
