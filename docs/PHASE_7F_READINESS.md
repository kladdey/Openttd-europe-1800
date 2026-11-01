# Phase 7F — readiness

**PARTIAL.** A separate playable candidate and eight conditional port-related events are implemented. **Zero paid maritime deliveries were verified.** Keep Phase 7D/7E as the established development baseline; do not promote Phase 7F to a validated multiplayer release.

## Phase 7F.1 follow-up

**Still PARTIAL:** four additional targeted engine invocations and four focused tests. A legal joined receiving station now accepts MNSP at the Dublin mill, and native Liverpool–Dublin water-edge connectivity passes. Reload diagnostics show Wharf 458 producing 224 MNSP/month and 406 units waiting, but the Brig never loaded or delivered in either four-year attempt. A wider loading approach did not resolve navigation/berth access. No normal candidate or port policy changed. [Exact evidence and next manual experiment](PHASE_7F1_MARITIME_CONNECTIVITY.md). The seven-run results below remain the historical Phase 7F record.

## Candidate and launch

`C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.6.0 - Phase 7F Historical Ports.scn`

SHA-256: `0d21f3045e8bc2dc2d4888298ad467284e90ffb3cba1be012bced37ee7386c5f`

```powershell
python scripts/ports_phase7f_launch.py --verify-only
python scripts/ports_phase7f_launch.py
# Optional inspection:
python scripts/ports_phase7f_launch.py --editor
```

Use the isolated profile in the [candidate manifest](research/phase7f_candidate_delivery.json). It requires the exact local assets; cloning GitHub alone is not a playable binary package. AXIS **0.6.0 remains unchanged**, with separately packaged **GS v5/schema 4**. The initial 617 towns, 542 industries, 15 GRFs, 64 cargos, calendar/economy 1830/1800 and seven-tile trains are preserved. No old scenario or save was overwritten. Old running saves are not automatically migrated.

## Results and blockers

- Native Liverpool Port 39 construction succeeded in a disposable probe; existing compatible Gdańsk port/wharf facilities remain. Eight proposed Liverpool/Gdańsk events cover 1831/1875/1975/1995, extending the same scheduler to 40 rows. Later normal openings remain unverified.
- An intermodal Irish Sea attempt delivered grain and observed mill FOOD production, but its feeder/ships carried no observed FOOD over five economy years. No false shipping income is claimed.
- A direct Liverpool→Dublin supplies route had no legal receiving dock in the tested catchment. Liverpool→Greenock had no connected approach in the bounded water search. Both require route/approach diagnostics, not economic buffs or terrain changes.
- **Seven engine invocations**, including one permitted additional attempt and the editor; **eight focused tests passed**. Final normal profile hashes verified. A native editor save and new-controller gameplay startup are proven; normal-policy save/reload, opening idempotence and multiplayer are not newly verified.
- Phase 7E `4a6b056` is preserved in this branch's ancestry; its five paid modern road-freight legs are separate evidence and do not count as paid shipping.

## Minimum next validation

1. In a **new disposable profile**, use the recorded Liverpool wharf 458 and inspect every candidate loading/receiving dock's actual ship access tile. Choose a receiving **accepting coastal** processor whose approach lies in the same native connected-water component before building a fleet. Do not infer navigability from nearby water or `HasDock`; several API dock locations returned −1, requiring player-built docks.
2. Use **one** buildable/refittable Brig, normal load and unload/no-load orders. Record positive load, its decrease at the accepting destination and a positive vehicle-profit increment. If using Dublin's mill, first observe a horse feeder loading, transferring to the exact joined dock station and accumulating FOOD there; grain income alone is insufficient.
3. Only after one paid maritime leg, measure a full operating year, maintenance and capital, then save/reload the matching normal GS v5 policy and check for duplicate port openings. Reconnect Kladdey, Squirrel and Toni before multiplayer promotion. No blanket balance changes are justified now.

## Reproduction and evidence

```powershell
python scripts/ports_phase7f.py
python scripts/ports_phase7f_validate.py
python scripts/ports_phase7f_freight.py
python scripts/ports_phase7f_freight.py --direct
python scripts/ports_phase7f_evidence.py
python -m unittest discover -s tests -p test_phase7f_ports.py
```

The final probe targets Liverpool/Gdańsk; the recorded earlier exploratory probe targeted Liverpool/Hamburg. `--direct` now reproduces the final Greenock attempt; the earlier Dublin script is pinned by hash in its local profile. The intermodal route uses the earlier native-probe checkpoint and industry 542. These are known-negative diagnostic fixtures, not a successful shipping demonstration. Do not rerun the whole set merely to launch the candidate. Runtime files are under `newgrfs/axis-historical-progression/.work/runtime/phase7f`; existing Phase 7D assets are prerequisites. Editor staging/finalization uses `ports_phase7f_candidate.py --stage-editor`, a new native `UNNAMED.scn` save and then `ports_phase7f_candidate.py`, with exclusive copies and preservation checks.

See [implementation](PHASE_7F_IMPLEMENTATION.md), [events](research/phase7f_port_events.csv), [geography](research/phase7f_port_geography.json), [route results](research/phase7f_route_results.csv) and [all invocations](research/phase7f_test_receipts.json). No binaries or raw third-party assets are committed. Changes are local only; no push, merge or main modification.
