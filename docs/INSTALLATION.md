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
