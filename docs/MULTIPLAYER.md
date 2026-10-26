# Multiplayer test guide - Toni and Squirrel

**Target:** Windows 11, JGRPP **0.73.4**, 4096 x 4096 Europe 1800 scenario.

## Before connecting

1. Both host and clients launch the **same JGRPP build**, not stock OpenTTD.
2. Each player loads the same exact NewGRF versions; check for missing or incompatible content.
3. The host starts a **multiplayer server** using the intended Europe 1800 scenario (not a local single-player game).
4. Clients join from the multiplayer server list or via the host's address, as appropriate.
5. Avoid changing NewGRFs in an active multiplayer save. Keep a backup before any scenario or industry edits.

## 'Network - Game connection lost'

This message alone does **not** identify the cause. Capture:

- Does the server appear in the browser?
- Does disconnect occur immediately, during map transfer/loading, or after entering the game?
- Exact JGRPP version on both machines.
- Any missing NewGRF warnings, content IDs or mismatched checksums.
- Server and client console/log messages.
- Whether a smaller default map can be joined successfully.

### Diagnostic sequence

1. Test the host/client connection with a **small default map** using the same JGRPP build.
2. If that works, host the Europe 1800 scenario with the required NewGRFs.
3. If the large map fails, note **when** it fails, check logs and memory usage, and retry with no other downloads in progress.
4. If a small map also fails, investigate network/firewall/server configuration rather than blaming the scenario.
5. Check router/NAT and OpenTTD's current networking guidance only if direct hosting needs it. Do not guess ports or expose services unnecessarily.

A 4096 x 4096 map can stress transfer/loading and client memory, but **map size alone has not been established as the cause** of Toni's disconnection.

## Reproducibility record

For every test, record date, host, client, JGRPP version, scenario filename and checksum, NewGRF list, connection stage, exact error and whether the test passed. Store screenshots/logs with personal IP addresses and private details redacted.

## Development safety

Keep the **V12 568-town** checkpoint and the **V13 613-town** candidate distinct. Industry density and geographic placement are ongoing work; do not overwrite the multiplayer scenario without testing a copy.

See [INSTALLATION.md](INSTALLATION.md) and [LICENSING.md](LICENSING.md).
