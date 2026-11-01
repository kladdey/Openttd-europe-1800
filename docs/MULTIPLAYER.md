# Current multiplayer test protocol — Phase 7H

**Candidate:** JGRPP **0.73.4**, unchanged AXIS **0.6.0**, **GS v7/schema 6**, exact 15 GRFs, initial **617 towns / 542 industries / 64 cargos**, calendar/economy **1830/1800**, seven-tile trains. Use the fresh [Phase 7H scenario/profile](PHASE_7H_READINESS.md) through `python scripts/transformation_phase7h_launch.py`. Do not upgrade an ongoing older-schema save in place.

**READY WITH CAVEATS for controlled testing.** Phase 7H proved the existing 7G active-boom reload through downturn/recovery, legal Lancashire textile construction, Silesian pilot decline and physical retirement, and the new schema-6 ended-state reload. Phase 7E proved paid modern road freight. These are separate observations, not a successful three-human campaign. Paid maritime freight remains unresolved; normal historical milestones, new H active/closing-row reload and sustained route economics still need verification.

## First session: Kladdey, Squirrel and Toni

1. Verify identical engine and GRF hashes against the [manifest](research/phase7h_candidate_delivery.json). The host must use the matching GS v7 normal policy, a fresh 1830 scenario and a disposable campaign save. Do not use accelerated fixtures.
2. Have all three players join separate companies in distinct regions. Record loading time, missing-content errors, disconnects and desyncs; redact private addresses in shared logs.
3. Build modest passenger and compatible freight routes. Verify actual loading, acceptance and paid income, recording capital, vehicle expenses and maintenance under competition. Industry construction or displayed production alone does not establish profit.
4. Save, stop/restart the host and reconnect both clients. Confirm company finances, industries, original map identities and GS state persist without duplicate openings or unexplained closures. This three-human gate has not been completed.
5. In a separately labelled disposable accelerated profile, save during a new H active/closing row, reload and verify one-shot decline/retirement. Keep its exact fixture contract; do not load it under the normal policy. All original industries must remain except already authorized old lifecycle actions.
6. Record dates, hashes, host/client versions, outcomes and logs. Preserve a checkpoint on errors; do not work around schema refusal or desync by changing NewGRFs in the save.

Next targeted freight work: right-size downstream recycling fleets, supply and haul textiles, and resolve one genuine paid maritime leg. No artificial subsidies or price changes are recommended from the current supply-only transformation tests. See [7H limitations](PHASE_7H_READINESS.md), [implementation](PHASE_7H_IMPLEMENTATION.md) and retained [original-mine safeguards](PHASE_7B_MIGRATION_AND_SAFETY.md).

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
