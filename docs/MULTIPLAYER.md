# Current multiplayer test protocol — Phase 7D

**Candidate:** JGRPP **0.73.4**, **617 towns / 542 starting industries**, unchanged Historical AXIS **0.6.0**, server-side **GS v4/schema 4**, exact 15 GRFs. Launch using `python scripts/lifecycle_phase7d_launch.py` and the isolated [Phase 7D profile](PHASE_7D_READINESS.md). Calendar/economy starts **1830/1800**; train length remains seven tiles.

**READY WITH CAVEATS**, not a certified three-human campaign. Phase 7D demonstrated modern construction in Rhine and Lille, limited depot production, a small-map timeline through 2026 and save/reload without duplicate openings. Earlier dedicated-server and client evidence belongs to its recorded earlier candidates; no new three-player session, paid modern recycling chain or full Europe progression certification is claimed.

**Phase 7F is PARTIAL:** the separate port candidate is not multiplayer-certified and has no verified paid maritime leg. First resolve its [single-route validation steps](PHASE_7F_READINESS.md), then verify matching GS v5 save/rejoin and duplicate-opening safety in a disposable host/client test. Keep the Phase 7D/7E baseline and its evidence distinct; no silent live-save migration.

## First session: Kladdey, Squirrel and Toni

1. Verify identical JGRPP and all GRF hashes against the [candidate manifest](research/phase7d_candidate_delivery.json). Host the fresh normal 1830 candidate with the matching GS v4 package; do not use accelerated or future-year fixtures.
2. Have all three players join separate companies in distinct regions. Record loading time, exact missing-content errors, disconnects and desyncs; redact private addresses in shared logs.
3. Build modest passenger and valid freight routes. Verify actual production, loading, acceptance and paid revenue; compare infrastructure/vehicle expenses and opportunities under competition. Record annual finances rather than assuming construction proves profitability.
4. Save a disposable checkpoint, restart the host and reconnect both clients. Confirm towns/industries, company finances and GS ledger persist without duplicate events or unexplained closures.
5. For lifecycle warnings/retirement and future recycling, use separately labelled disposable fixtures with their matching policies. Verify RCYC deliveries to recovery and junkyard, PLAS to plastics, downstream MNSP acceptance and SCMT/EAF supply. Do not mix fixture saves with the normal policy.
6. Report dates, filenames/hashes, host/client versions, observed outcomes and relevant logs. Stop and preserve the checkpoint on desync, accidental baseline demolition or migration refusal; do not work around it by changing GRFs in the save.

Modern economic throughput, competing-company effects and all final regional events remain unverified. Consult [Phase 7D evidence limits](PHASE_7D_READINESS.md), [implementation](PHASE_7D_IMPLEMENTATION.md) and retained [mine safety rules](PHASE_7B_MIGRATION_AND_SAFETY.md).

---

## Earlier multiplayer troubleshooting (historical)

## Confirmed successful client playtest - 2026-10-26

User reports that **Squirrel successfully joined the hosted Europe 1800 game, loaded the map and played**. This is an end-to-end multiplayer success on the 4096 x 4096 scenario, not merely a server-browser connection. Toni's earlier disconnect remains unresolved. The exact client-side build, NewGRF checksums, test duration and logs were not recorded; do not infer those details.

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
