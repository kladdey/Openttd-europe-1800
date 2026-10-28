# Vehicle and transport economy audit

Start with [multiplayer readiness](MULTIPLAYER_ECONOMY_READINESS.md) and the
[final action plan](FINAL_ECONOMY_ACTION_PLAN.md). The conclusion is **READY WITH
CAVEATS**, applying to the exact 1830 scenario and fifteen NewGRF identities
recorded in the audit. Original game files were investigated read-only; gameplay
tests used disposable copies. No balancing proposals were automatically applied.

## Reports

| Phase | Evidence and interpretation |
| --- | --- |
| 1: identities and prices | [Installed NewGRFs](VEHICLE_NEWGRF_INVENTORY.md), [locomotive prices](LOCOMOTIVE_PRICE_AUDIT.md), [initial recommendations](VEHICLE_BALANCING_RECOMMENDATIONS.md) |
| 2: complete vehicle economics | [Analysis](VEHICLE_ECONOMY_PHASE2.md), [unimplemented proposals](VEHICLE_BALANCING_PROPOSAL.md) |
| 3: loaded operation | [Analysis](TRANSPORT_ECONOMY_PHASE3.md), [test matrix](TRANSPORT_ECONOMY_TEST_MATRIX.md), [findings](TRANSPORT_ECONOMY_FINDINGS.md) |
| 4: competition and launch decision | [Analysis](TRANSPORT_ECONOMY_PHASE4.md), [readiness and player protocol](MULTIPLAYER_ECONOMY_READINESS.md), [action plan](FINAL_ECONOMY_ACTION_PLAN.md) |

## Main datasets

- [NewGRF inventory](research/newgrf_inventory.json) and [original roster](research/vehicle_roster.csv).
- [Normalized economics](research/vehicle_economy_normalized.csv), [set comparisons](research/vehicle_set_comparison.csv) and [overlapping definitions](research/vehicle_overlap_comparison.csv).
- [Phase 3 route observations](research/transport_route_results.csv) and [company growth](research/company_growth_simulations.csv).
- [Horse tests](research/horse_transport_tests.csv), [maritime tests](research/maritime_profitability_tests.csv), [three-company simulations](research/three_company_simulation.csv) and [competition tests](research/competition_tests.csv).

Evidence labels distinguish actual gameplay, engine calculations, models and
blocked/manual tests. A blocked service's observed expenses are not evidence that
the transport mode is intrinsically unprofitable. Raw text evidence, parameters,
source fingerprints and frozen measurement scripts accompany the datasets in
`docs/research/`; no NewGRF graphics or binaries are included in these additions.

## Reproduction

Follow each report's commands and prerequisites. The Windows tools require the
matching locally installed JGRPP/GRFs and retained disposable runtime copies.
They are not a portable modpack or an asset downloader. The bundled Python
environment has NumPy for the saved-scenario reader.

Focused checks:

```powershell
python -m unittest discover -s tests -p test_vehicle_economy_phase2.py
python -m unittest discover -s tests -p test_transport_phase3.py
python -m unittest discover -s tests -p test_transport_phase4.py
python scripts/validate_transport_phase4.py
```

The preservation validator deliberately checks the original local source files
and prior research bytes; it is not a generic GitHub CI test. An unrelated
geography suite has additional dependencies and is not covered by these thirty
economy tests.

## Historical industry work

The separately developed [historical-industry implementation](AXIS_HISTORICAL_IMPLEMENTATION.md)
and [AXIS prototype source](../newgrfs/axis-historical-europe/README.md) are also
retained. Their build/production checks do not mean the historical fork was
active in the vehicle-economy baseline. Use each report's exact scenario hash,
GRF identities and scope before comparing results.
