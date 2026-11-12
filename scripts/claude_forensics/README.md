# Running-cost reinvestigation scripts

These scripts back the independent reinvestigation
(`docs/CLAUDE_FLEET_DISCREPANCY_REINVESTIGATION.md`). They read only committed
evidence in `docs/research/` and write to `docs/research/claude_forensics/`. They need
no game, GRF or network access: Python 3 standard library only.

| Script | Purpose |
| --- | --- |
| `infer_cost_factors.py` | Finds the exact running-cost base class and integer factor for each engine, using the JGRPP formula and logged exponents |
| `cost_curve_analysis.py` | Fits per-set factor-vs-hp curves and builds size/era-matched NARS/UKRS2 pairs |
| `fleet_era_comparison.py` | Median in-service running and purchase £/hp by era × traction × set, plus the NARS ×½ counterfactual |
| `train_physics_model.py` | Simplified re-implementation of JGRPP realistic acceleration (a model, not a measurement) |
| `ledger_analysis.py` | Compares in-game ledger running expense with catalogue and vehicle age |
| `heavy_freight_te.py` | Top-TE freight locomotives to 1945 and the load each can lift on a sustained 3% grade |
| `verify_claims.py` | 19 assertions for the headline claims; fails if the evidence no longer supports them |

Run everything: `scripts/claude_forensics/run_all.sh`
