# Current local installation — Phase 7B (development only)

The latest tested development profile is **Europe 1830 Historical AXIS 0.5.0 - Legacy Mine Lifecycle**, with **617 towns / 542 starting industries**. It requires **JGRPP 0.73.4**, the **exact 15 active NewGRFs**, the separately built **Historical AXIS 0.5.0 legacy candidate**, and packaged **GameScript v2/policy**. **Do not use the older FIRS-based nine-GRF list below to set up this candidate.**

On the original development Windows PC, from the repository root:

```powershell
python scripts/lifecycle_phase7b_launch.py
python scripts/lifecycle_phase7b_launch.py --editor
```

The isolated launcher validates local assets. The scenario and compiled NewGRF are **local build outputs, not guaranteed to be included in a Git clone**. Exact SHA-256 hashes, paths and requirements are in [Phase 7B readiness](PHASE_7B_READINESS.md) and [delivery manifest](research/phase7b_candidate_delivery.json). Do not manually substitute versions based on similar filenames.

**Migration warning:** A 0.3/0.4 save is not automatically a 0.5 lifecycle save. Legacy enrollment on existing campaigns requires a separately reviewed explicit migration; do not replace NewGRFs or scripts in an ongoing game. The normal 7B policy is not the accelerated 1837/1839 test fixture.

For other machines, obtain licensed upstream assets and verify every exact GRF/script/checksum before hosting; a clone alone is not a ready-to-play package. See [multiplayer](MULTIPLAYER.md) and [licensing](LICENSING.md).

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
