# Fleet Phase 4 scripts

Experimental, test-only balance work for Europe 1830 (JGRPP 0.73.4, Historical AXIS 0.6.0).
Reuses `scripts/runtime_validation/` (harness `rv.py`, GameScript `rv_probe.nut`).
Results: `docs/FLEET_PHASE4_*.md`. Standard library only.

| Script | Purpose |
| --- | --- |
| `verify_prior_evidence.py` | Re-derives the 31 Phase-3 findings from committed evidence |
| `balance_grf.py` | Builds override GRFs (Action 8 + Action 0: 0x11 override, 0x08 prices, per-engine 0x0D / 0x0E) |
| `variants.py` | Exact specs of variants A, B and C |
| `phase4.py` | Suites: feas, sweep, erabase, lifecycle, autoreplace, catalogue, era-<variant> |
| `save_tools.py`, `savetest.py`, `savecompare.py` | Cloned-save NGRF/GSDT rewrite, load / autosave / rollback, identity and cost comparison |
| `mptest.py` | Localhost dedicated server + null-video client join / rejoin / refusal |
| `p4_analyze.py`, `catcheck.py`, `lifecycle.py`, `gen_tables.py`, `make_proposed.py` | Analysis and tables |
| `build_balance_grfs.py` | Deterministic build of every variant GRF with SHA-256 manifest |
| `test_phase4.py` | Automated validation of every Phase 4 claim |

Disk protection (in `rv.py`): one shared GRF store hard-linked into runs (never production
files), SHA-256 verification of the store, `RV_MIN_FREE_GB` / `RV_RUN_BUDGET_GB` guards,
deletion only of marked harness directories.
