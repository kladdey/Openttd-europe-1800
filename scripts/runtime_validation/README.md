# Runtime validation harness

Measures the predictions of the running-cost forensics in JGRPP 0.73.4 on this PC.
Results: [`docs/RUNTIME_VALIDATION_RESULTS.md`](../../docs/RUNTIME_VALIDATION_RESULTS.md).
Python 3 standard library only.

| File | Purpose |
| --- | --- |
| `rv.py` | Environment check (`verify`), fixture preparation (flat or ramp heightmap, copied settings, test GRF copy hard-linked per run), run, production-file hash guard |
| `rv_probe.nut` | Measurement GameScript: engine catalogue, coal route with per-state `GetRunningCost` sampling, yearly ledgers, ramp speeds, cargo income quotes |
| `make_compat_grf.py` | Builds the test-only NARS price-42 compat GRF (Action 0 prop 0x11 override + prop 0x08) |
| `experiments.py` | Suites t1–t6 (tests 1–6 of RECOMMENDATIONS §6) |
| `analyze.py` | Evidence logs → CSV tables in `docs/research/runtime_validation/` |

Runs live outside the repository (`C:\Users\Kladd\OTTD-runtime-validation\runs`). Only
filtered evidence logs, manifests and receipts are committed.
