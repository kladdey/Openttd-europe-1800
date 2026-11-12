# Fleet Phase 4: balance experiments

Europe 1830, JGRPP 0.73.4, Historical AXIS 0.6.0, November 2026. Branch
`claude/europe-1830-fleet-phase4`, built on `c51be8f`. **Nothing here is deployed or
approved.** No production GRF, save, scenario, configuration or multiplayer setup was
modified.

Companion documents:

- [Variant comparison](FLEET_PHASE4_VARIANT_COMPARISON.md)
- [Callback validation](FLEET_PHASE4_CALLBACK_VALIDATION.md)
- [Historical regression](FLEET_PHASE4_HISTORICAL_REGRESSION.md)
- [Compatibility](FLEET_PHASE4_COMPATIBILITY.md)
- [Final recommendation](FLEET_PHASE4_FINAL_RECOMMENDATION.md)

Data: [`fleet_phase4_results.csv`](fleet_phase4_results.csv) (455 configurations) and
[`fleet_phase4_proposed_values.csv`](fleet_phase4_proposed_values.csv). Evidence:
[`research/fleet_phase4/`](research/fleet_phase4/), with one folder per run holding the
filtered log, manifest and receipt.

**Labels.**

- **RUNTIME**: measured in JGRPP.
- **DERIVED**: arithmetic on RUNTIME values. Every operating profit is DERIVED: ledger
  revenue − ledger train running − property.
- **ANALYTIC**: an estimate, not simulated.
- **UNVERIFIED**: not tested.

## 1. Recovery and verification of previous work

| Item | Where it actually is |
| --- | --- |
| Commit `c51be8f` | `origin/claude/europe-1830-running-cost-forensics-9fypo5` (verified) |
| `RUNTIME_VALIDATION_RESULTS.md`, `NARS_UKRS2_RUNNING_COST_FORENSICS.md` | `docs/` on that branch |
| `FLEET_SIMULATION_RESULTS.md`, `FLEET_BALANCE_CHANGESET_PROPOSAL.md` | **Not in the repository.** They are uncommitted files in the local Codex checkout `Documents\Codex\2026-10-28\openttd-europe-1830-2025-local-newgrf\docs\` (branch `feature/phase-7j-private-client-installer`). They were read, not copied |
| Runtime harness | `scripts/runtime_validation/`, reused and extended |
| Experimental GRF of Phase 3 | `runs\_compat\rv_nars_compat.grf` (test area only) |

All 31 Phase-3 findings quoted in the brief re-derive exactly from the committed
evidence: [`scripts/fleet_phase4/verify_prior_evidence.py`](../scripts/fleet_phase4/verify_prior_evidence.py),
31/31 PASS. The re-derived findings are:

- the catalogue figures;
- the ¼ / ⅓ / flat standstill rates and ¾ / ⅔ moving rates;
- loaded = empty;
- the ageing steps at 12/24 and 9/21 years;
- the climbing limits;
- the 8F stall;
- the 71-engine compat halving;
- the £6,281 → £3,276 service bill.

## 2. Harness changes and disk protection (fixes the Phase-3 incident)

| Requirement | Implementation (`scripts/runtime_validation/rv.py`) |
| --- | --- |
| One shared asset store | `runs\_shared\` holds a single test copy of the production GRFs and basesets, created once before any worker starts |
| Reuse binaries | Runs **hard-link** to `_shared`, never to production files. Hard links cost no space (`runs_gb()` counts only files with link count 1) |
| Immutable store | `verify_shared()` compares every shared GRF's SHA-256 with the production original before and after every suite |
| Mutable experimental GRFs | Copied (116–379 bytes) into each run, never linked |
| Unique working dirs | One directory per tag; refuses to overwrite |
| Disk budget | `RV_MIN_FREE_GB` (default 40): refuses to start and kills a run that drops below it. `RV_RUN_BUDGET_GB` (default 8) caps run directories |
| Cleanup scope | `cleanup()` deletes a run directory only if it lies under `runs\`, carries the `.rv_created` marker written by `prepare()`, and is not an `_` store |
| Logs kept | Compact evidence (about 9–30 KB per run, monthly samples dropped) is copied to the repository before deletion. The full-log SHA-256 is kept in the receipt |
| Saves | Only cloned saves under `runs\_saves\` can be loaded (asserted). Large autosaves are kept outside git |

Result: 2,191 Phase 4 runs. Free space stayed at 77–78 GB throughout; the run area held
3.2 GB, nearly all of it the Phase-3 directories left in place. The production files and
the shared store were verified unchanged after every suite.

## 3. Mechanism feasibility (RUNTIME, suite `feas`)

Each candidate mechanism was tried in an isolated GRF on one engine. It was then measured
two ways:

- in the purchase-list catalogue;
- in service: GameScript `GetRunningCost` sampled moving, at the platform and in the depot.

| Mechanism | NARS 2.52 | NARS Add-On | UKRS2 |
| --- | --- | --- | --- |
| Static running-cost factor, Action 0 prop 0x0D | **Trap**: the catalogue drops (Norris £6,300 → £3,150) but the in-service rate is unchanged (£6,452 consist) | **Works** in catalogue and service (Grasshopper £3,150 → £1,575 flat) | **No effect** anywhere |
| Running-cost class switch, prop 0x0E, to class 44, plus a set-local class-44 exponent | **Works**: catalogue £5,400; service moving £5,400, standstill £1,350 (¼ kept) | not needed | **Works**: Planet £525 → £1,800; service ¾ / ¼ kept |
| Set-local class-42 exponent (prop 0x08 through the engine-allocation override 0x11) | Works for all 71 NARS locomotives (Phase 3, re-proved here) | n/a | possible, not used |
| Class 44 free? | Yes: changing its multiplier alters **no** NARS vehicle | No: 8 EMUs use it | Yes |
| Class 43 free? | **No**: carries all 42 NARS coaches and wagons | No (138 entries) | No (40 coaches) |

The trap matters. A catalogue-only check would have "proven" a NARS per-engine factor
override that does nothing to the actual bill.

**Granularity.** For NARS and UKRS2, an engine can only be repriced by moving it between
two groups, each scaled by a power of two:

- class 42 (base 4,200);
- class 44 (base 3,600).

The achievable ratios are ×{1, 0.857} × 2^k. For Norris that gives £6,300, 5,400, 3,150,
2,700, 1,575, 1,350 or 675. The Add-On can be set exactly, in steps of £131.25.

## 4. Norris sweep (1850, 5 seeds, RUNTIME)

Ten duties per value:

- flat 32 tiles with 6 and 12 hoppers, at supply-limited (level 16) and saturated (level 128) supply;
- flat 96 tiles with 6 and 12 hoppers;
- moderate grade (alternating 3% tiles) with 4 hoppers;
- sustained 3% with 1 and 2 hoppers;
- 48-tile passengers with 4 coaches.

Subsidies off. Delivered tonnage is identical at every cost level: cost does not change
physics.

| Norris catalogue | 12 hoppers, saturated: profit | 6 hoppers, limited supply | Passengers | 20-year cash, 12 hoppers |
| --- | --- | --- | --- | --- |
| £6,300 (original) | £10,851 | £5,178 | £6,322 | £132,560 |
| £5,400 | £11,718 | £6,037 | £7,145 | — |
| £3,150 (global ½) | £13,884 | £8,186 | £9,203 | — |
| **£2,700** | **£14,316** | **£8,616** | **£9,616** | **£195,396** |
| £1,350 | £15,616 | £9,904 | £10,851 | £218,958 |
| £675 | £16,267 | £10,550 | £11,468 | — |
| *Planet (contemporary)* | *£8,751* | *£8,185* | *£9,935* | *£120,893* |
| *Coppernob (1844)* | *£20,419* | *£12,228* | *£12,902* | *£275,862* |

The 20-year cash flows are measured from 20-year runs with autorenew off, minus purchase
(`lifecycle_summary.json`). Grades: Norris climbs a sustained 3% with 1 loaded hopper (mean
32 km-ish/h) and stalls with 2, at every cost level. On grades it loses money at 32 tiles,
as does every 1850 engine.

## 5. Grasshopper sweep (1850, 5 seeds, RUNTIME)

| Grasshopper | 6 hoppers, limited supply: profit (vs Planet £8,185) | 12 hoppers, saturated | Passengers (vs £9,935) | 20-year cash, 6 hoppers (vs Planet £140,088) |
| --- | --- | --- | --- | --- |
| £3,150 (original) | £3,466 (42%) | £3,860 | £4,876 | £45,660 |
| £1,575 (−50%) | £5,042 (62%) | £5,435 | £6,453 | £77,182 |
| £1,050 | £5,567 (68%) | £5,962 | £6,978 | — |
| **£787** | **£5,830 (71%)** | **£6,224** | **£7,240** | **£92,929** |
| £525 (= Planet) | £6,092 (74%) | £6,487 | £7,503 | £98,178 |

## 6. Recorded failures

| Failure | Count | Cause | Handling |
| --- | --- | --- | --- |
| 96-tile coal routes: `industry placement / ERR_SITE_UNSUITABLE` | 130 | Historical AXIS 0.6.0 refuses a Coke Oven 96 tiles from the coal mine on every candidate tile, which looks like a location rule | Archived in `research/fleet_phase4/failures/`. The GameScript gained a logged fallback to another coal acceptor; all 130 reruns completed |
| Passenger towns could not be founded | 18 | Random terrain on two 1940 seeds | Recorded; the other seeds stand |
| GMD F59PH listed for 1980 | 5 | My error: it is a 1989 engine | Recorded as a failed configuration |
| 1832 7-tile coal trains | 30 runs, completed | 26 hoppers overload Planet and Grasshopper, which then crawl at 2 km-ish/h even on the flat | Kept as evidence of the 7-tile constraint; not used for balance |
| Wallclock / multiplayer client | — | See [compatibility](FLEET_PHASE4_COMPATIBILITY.md) | Server verified; client join UNVERIFIED |

## 7. Reproduction

```bash
cd scripts/fleet_phase4
python -B verify_prior_evidence.py
python -B phase4.py --suite feas
python -B phase4.py --suite sweep
python -B phase4.py --suite erabase
python -B phase4.py --suite lifecycle
python -B phase4.py --suite autoreplace
python -B phase4.py --suite catalogue
python -B phase4.py --suite era-A_targeted   # also era-B_steam, era-C_cross
python -B savetest.py --variant C_cross
python -B savecompare.py C_cross
python -B mptest.py --variant C_cross
python -B p4_analyze.py
python -B catcheck.py
python -B lifecycle.py
python -B make_proposed.py
python -B build_balance_grfs.py
python -B test_phase4.py
```

Runs whose receipts exist are skipped, so a rerun only fills gaps.
