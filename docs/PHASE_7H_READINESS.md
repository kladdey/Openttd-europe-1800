# Phase 7H — readiness

**READY WITH CAVEATS for controlled transformation playtesting.** The mandatory active-cycle reload gate passed, and both new regional transitions had actual native effects. This is not multiplayer or full-campaign certification.

## Separate candidate and manifest

`C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.6.0 - Phase 7H Industrial Transformation.scn`

SHA-256 **`88d7a56e341ba7c2972e634fe3c8ec779e6357e6f2ab09adac2e2746c01aa647`**.

```powershell
python scripts/transformation_phase7h_launch.py --verify-only
python scripts/transformation_phase7h_launch.py
# Optional Scenario Editor inspection:
python scripts/transformation_phase7h_launch.py --editor
```

Use the [manifest-pinned isolated profile](research/phase7h_candidate_delivery.json), **GS v7/schema 6**, unchanged Historical AXIS **0.6.0** and JGRPP **0.73.4**. Initial state remains **617 towns, 542 industries, 15 GRFs, 64 cargos, seven-tile trains, calendar 1830/economy 1800**. All initial map planes and town/industry/settings/storage chunks match Phase 7G; exact GRF references and parameters are identical. Previous candidates/saves/configuration were not overwritten. A clone alone lacks local compiled dependencies.

## Native results

| Test | Observed result |
|---|---|
| Active 7G gate — two invocations | Fresh boom checkpoint saved and reloaded under exact schema 5 contract; same Ruhr mine 542; no repeated opening/boom; downturn and restoration each once; final level 16/flags 0, all originals retained. |
| Lancashire textile opportunity | New mill 543 legally constructed; native FICR/COAT acceptance and TEXT/GOOD registration verified. Output remained zero without input services; no textile delivery/profit claim. |
| Silesian restructuring | New mine 542 produced settled 180 COAL/month at level 16, then 80–90 at level 8; native retirement requested and matching instance physically removed after 60 calendar days. All original mines preserved. |
| New schema-6 ended reload | Both rows loaded ended; factory still present, retired mine absent; no repeated new effect. Final fixture 543 industries, 542 original identities and 617 towns. |
| Preservation | Native separate editor save, unchanged source/assets, exact initial map planes and 15 GRF records; zero local height changes at both constructed sites. |

**Five JGRPP invocations total, zero failures; six focused Python tests passed.** Raw logs and disposable saves remain local; [compact receipts](research/phase7h_engine_receipts.json), [production samples](research/phase7h_production_samples.csv) and [event results](research/phase7h_event_results.csv) retain exact IDs/dates/commands/hashes. The two new events use compressed 1830 fixture dates; normal 1840 and 1975–2000 milestones are **not** simulated history.

## Compatibility and remaining risks

Use a fresh separate scenario. **Schema 5 and older running saves are not automatically migrated to schema 6.** Do not load accelerated fixture saves with the normal policy. All previous port schedules, recycling evidence, old mine/mill rules and Ruhr cycle remain intact. The new layer reuses supported native control/closure behavior; AXIS, recipes, prices and cargo IDs were not edited.

Before a live campaign: reload a new Phase 7H active/closing row, test the normal calendar milestones with realistic industry/site competition, and operate fibre/textile/coal routes to measure throughput and finances. The 7G active gate and H ended-state reload do not prove every H mid-command autosave/closure case. Industry availability and native siting can legitimately cancel a normal event. No guarantee of profitable freight or permanent factory survival is offered. Multiplayer fairness is implemented through neutral facilities/public news, but a three-human session was not tested.

## Reproduce selectively

```powershell
# Gate first; uses the existing exact Phase 7G fixture contract:
python scripts/transformation_phase7h_gate.py 1
python scripts/transformation_phase7h_gate.py 2
# New events, normal parent policies retained; only the H dates compressed:
python scripts/transformation_phase7h_validate.py
python scripts/transformation_phase7h_reload.py
python scripts/transformation_phase7h_evidence.py
python -m unittest discover -s tests -p test_phase7h_transformations.py
```

These four headless commands plus the one editor session are the five recorded invocations, not a suggested broad regression campaign. Do not rerun them just to launch the candidate. New-case paths and gate checkpoints are under `newgrfs/axis-historical-progression/.work/runtime/phase7h`; earlier Phase 7G/7G.1 indices/checkpoints are preserved. Candidate rebuilding uses `transformation_phase7h_candidate.py --stage-editor`, a native new `UNNAMED.scn` save, then finalization without overwriting any prior candidate.

See [implementation, capability boundaries and proposed-only timeline](PHASE_7H_IMPLEMENTATION.md). Work is local on `feature/phase-7h-industrial-transformation`; no push, merge or main change.
