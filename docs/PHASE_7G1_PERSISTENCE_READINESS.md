# Phase 7G.1 — persistence readiness

**PASS for the ended-state reload gate. Active-boundary reload remains UNVERIFIED.** Two new JGRPP invocations total: first native reload succeeded but its observer assertion crossed a legitimate 1831 opening; the corrected, shorter observation passed all ended-state invariants. Three focused receipt-validation tests passed. No production code or saved-state schema repair was needed.

## Reused native checkpoint

The existing successful Phase 7G fixture checkpoint was present:

`newgrfs/axis-historical-progression/.work/runtime/phase7g/cycle-part1-1793518249452176200/save/autosave/exit.sav`

SHA-256 **`0fe80e8acde0d9b3333a92703350d0570aef0c67ca9380d3199b709aab171e33`**.

The instrumented part-2-equivalent path uses the existing `prepare`, `bundle`, `policy(True)` and engine execution helpers, loading this actual `.sav`; it never reconstructs the cycle. GS **v6/schema 5** accepted the exact accelerated fixture contract **117022446**. The native saved-data log showed schema 5, ended phase and mine 542 **before initialization**, followed by successful inherited ledger loading. The observer adds no alternative migration path.

## Before / after the successful bounded advance

| Field | Before | After |
|---|---|---|
| Calendar day / date | 668750 / 1830-12-23 | 668752 / 1830-12-25 |
| Economy day | 657793 | 657795 |
| Schema / cycle contract | 5 / 117022446 | unchanged |
| `ruhr_expansion` / `ruhr_downturn` | ended / ended | unchanged |
| Cycle phase / already boosted | ended / true | unchanged |
| Mine ID / native engine industry type | 542 / 1 (AXIS local coal type 0) | unchanged |
| Mine tile / birth day | 5265405 / 668401 | unchanged |
| Last effect day / last attempt month | 668667 / 21961 | unchanged |
| Construction attempts / batches | 1 / 1 | unchanged |
| Saved base level / flags | 16 / 0 | unchanged |
| Actual level / flags | 16 / 0 | unchanged |
| Actual last-month COAL | 135 | 135 |
| Matching pilot instances | 1 | 1 |
| Total industries / original signatures intact | 543 / 542 | unchanged |
| Town count | 617 | 617 |

There were **zero new cycle openings and zero cycle-level commands** after reload: no repeated expansion, boost, downturn or restoration. The external-production and no-closure bits remained cleared. Phase/timers/full target signature and the one-shot `boosted` flag survived; all persisted cycle fields recorded by the observer matched exactly. The native game advanced two calendar/economy days without schema rejection or crash. This is an ended-state observation, not proof that an active transition executes correctly after reload.

## First attempt and the fixture-only correction

The first attempt also loaded schema 5 successfully, retaining the same cycle state and restored mine. Its requested ten-day window actually advanced **16 calendar days** after command/scheduling overhead, crossing from 1830-12-23 into **1831-01-08**. The unchanged Phase 7F scheduler legitimately opened **Liverpool Port 543**, increasing the count to 544; the observer's fixed `industries==543` assertion then failed. The existing 542 original signatures and single pilot mine still matched. This was **not a duplicate mine, lost ledger or stuck multiplier**.

The only correction shortened the diagnostic observation to two days, before that unrelated scheduled opening. No port dates, parent policies, production code or simulation settings were changed. Both attempts and the failed assertion remain in the [machine-readable receipts](research/phase7g1_persistence_receipts.json); raw logs/checkpoints remain in unique ignored profiles. No third engine run was used.

## Active-boundary case and remaining risk

No pre-existing active-boundary checkpoint was available in the relevant Phase 7G profiles. The other old checkpoint came from the pre-opening failed prototype. Creating a fresh June-1830 checkpoint and then reloading it would require two more invocations; generating it alone would not prove reload. The budget was therefore spent on completing the ended-state gate. **Test B was not run.**

Next smallest remaining test: one disposable June-1830 boom checkpoint followed by one native reload crossing the downturn and restoration, comparing transition firing counts against the uninterrupted 7G evidence. Also retain separate future checks for normal 1850–1879 dates and human save/rejoin. This report makes no multiplayer or paid-profitability certification.

## Reproduction and preservation

```powershell
# One new engine invocation, from the existing exact checkpoint:
python scripts/cycles_phase7g1_persistence.py
# Read existing evidence only; no engine invocation:
python scripts/cycles_phase7g1_persistence.py --verify-receipts
python -m unittest discover -s tests -p test_phase7g1_persistence.py
python scripts/cycles_phase7g_launch.py --verify-only
```

The short observer is a disposable subclass; GS v6/schema 5, cycle policy, earlier 7A–7F policies, AXIS, cargoes and normal campaign dates remain unchanged. It uses the same accelerated contract as the saved fixture and refuses to rebuild a missing checkpoint. Do not point it at an old schema-4 or player save. New profiles are `phase7g/g1-ended-reload-*`; their saves/logs are local only. The normal-profile launcher and all pinned asset hashes were verified after testing.

The original Phase 7G candidate remains SHA-256 **`5a6d3b52d59224a6dcb918c306cd92b4f74f39e333f6905db101e23d802d74f2`**. Source checkpoint hash was checked before/after each invocation. No original scenario/save, normal configuration, GRF, map, vehicle setting or schema was modified. Branch: `feature/phase-7g1-persistence`, from `4c22a58`; local commit only, no push/merge/main change.
