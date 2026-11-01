# Phase 7G — readiness

**READY WITH CAVEATS for controlled cycle playtesting.** One regional boom and one downturn changed real COAL output in JGRPP; this is not a balanced 195-year economy or a multiplayer certification. Phase 7F shipping remains unresolved and out of scope.

## Separate candidate

`C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.6.0 - Phase 7G Regional Cycles.scn`

SHA-256: `5a6d3b52d59224a6dcb918c306cd92b4f74f39e333f6905db101e23d802d74f2`

```powershell
python scripts/cycles_phase7g_launch.py --verify-only
python scripts/cycles_phase7g_launch.py
# Optional native inspection:
python scripts/cycles_phase7g_launch.py --editor
```

Use the [manifest-pinned isolated profile](research/phase7g_candidate_delivery.json), GS **v6/schema 5**, unchanged AXIS **0.6.0** and exact JGRPP **0.73.4**. Initial state remains **617 towns / 542 industries / 15 GRFs / 64 cargos / seven-tile trains / calendar 1830, economy 1800**. Old scenarios, binaries, player saves and normal configuration were not overwritten. Compiled/local dependencies are not included in a Git clone.

## Verified versus remaining work

- **VERIFIED IN GAME:** new neutral Ruhr coal mine 542; sampled output **210 baseline → 270 boom → 63 downturn → 135 restored**, with levels 16/32/8/16 and control flags returning from 12 to 0. This proves supply change, not exact 2×/½× production or paid profit.
- **VERIFIED IN GAME / READ-ONLY CHECKS:** all original 542 industry identities and 617 towns retained in the completed fixture; one additional mine, 543 total; no local height changes. Initial native editor candidate is byte-equal to Phase 7F in all map planes and town/industry/settings/storage chunks, with identical GRF references/parameters.
- **SCOPE:** normal expansion/boom/downturn/recovery policy is 1850/1851/1873/1879. The one completed fixture compressed those dates into 1830; normal historical dates were not simulated. Original four-mine/one-mill policies and all eight port events are retained unchanged.
- **TEST COUNTS:** four engine invocations: editor, one compile failure, one runtime failure, one complete boom/downturn/recovery run. Six focused tests passed. No shipping, full regression or paid recycling reruns.
- **UNVERIFIED / before a live campaign:** engine save/reload and duplicate-prevention under schema 5; normal historical milestone progression; competition, paid transport and sustained profitability. A native checkpoint exists, but no successful reload is claimed. The two prototype fixes used the budget.

A new candidate is required: old running save schemas/contracts are explicitly refused, not migrated. Do not use accelerated fixture saves with the normal policy or manually substitute this GS into an existing campaign. Native no-closure/external-production flags apply only to the new pilot mine during its finite cycle. After recovery the mine remains available under native control; it is not automatically enrolled in an additional depletion program.

## Reproduce selectively

```powershell
python scripts/cycles_phase7g.py
python scripts/cycles_phase7g_validate.py 1
python scripts/cycles_phase7g_evidence.py
python -m unittest discover -s tests -p test_phase7g_cycles.py
```

The final part-1 driver now covers the whole short cycle and writes a native checkpoint. A part-2 reload mode remains available for a future targeted test, **not run this phase**. It consumes the prior fixture checkpoint and is not a campaign migration utility. Re-running it adds an engine invocation; do not repeat the old 7A–7F matrix. The collector preserves both earlier failed profiles and the successful observations. Raw logs/checkpoints are local under `newgrfs/axis-historical-progression/.work/runtime/phase7g`.

Candidate rebuilding: `cycles_phase7g_candidate.py --stage-editor` creates a unique disposable profile; save a fresh `UNNAMED.scn` natively, then run `cycles_phase7g_candidate.py` for exclusive delivery and preservation checks. Never overwrite a prior candidate.

Next smallest test: reload the accelerated checkpoint with its matching fixture contract, verify both ended states and no second mine; then test an active-boundary checkpoint before live multiplayer (`cycles_phase7g_validate.py 1 --boundary 1830-06-15`, followed by part 2). Those reload commands were not run in this phase. Review actual hauled COAL and finances separately before tuning the cycle amplitude. No price or recipe changes are recommended from supply-only evidence.

See [implementation/capability matrix/history](PHASE_7G_IMPLEMENTATION.md), [monthly samples](research/phase7g_production_samples.csv) and [all engine receipts](research/phase7g_engine_receipts.json). Local commits only; no push, merge or main modification.
