# Phase 7B — Actual engine validation

Verdict: **READY WITH CAVEATS**. A genuine 1830 mine can decline, warn, physically close and survive longer under sustained paid service. The preserved normal-play candidate contains ordinary production dates; accelerated exhaustion dates exist only in disposable fixtures.

## Runtime and evidence

Stock **JGRPP 0.73.4 Windows x64**, SHA-256 `1b3fd69c1ea5f77eebe881c6d8a6ad9a03b71f98928a05e0c3c08c79482e2789`. No engine patch. Historical AXIS **0.5.0 legacy candidate**, SHA-256 `473b4ac0ebc6962959408633dbbc2cf254546fe9bc7fdd6c3531b0f0a232e534`, GRFID `4B484531`, version 5 / minimum compatible 4. GameScript v2, schema 2, seed 7341830. Other fourteen active NewGRF references and parameters remain unchanged.

[Engine receipts](research/phase7b_engine_receipts.json) include 36 invocations in the final validation matrix, commands, timings, hashes, paths and observations, plus 25 archived earlier accepted invocations. [Raw logs](research/phase7b_logs/) are committed separately. The current dataset contains 708 legacy monthly observations and 2,485 event records; these are not independent experiments. Deliberate negative tests are labelled safe rejections. Diagnostic syntax/inheritance failures are excluded from the pass count.

Raw log attributes preserve exact native CRLF bytes for checksum verification across platforms. Some deliberately rejected fresh fixtures never initialize a ledger and emit the native Save-function warning; those are expected rejection cases, not successful save migrations or production-run failures.

## Real Europe matched comparison

Both runs began with the original 617 towns and 542 industries. Both enrolled original IDs 1/11/12/438, used the same finite test policy, no subsidies and real five-calendar-year warning periods. The served case added eight buildable **1 Horse Hopper Carriage** vehicles on a coal route from original mine 1 to an existing compatible consumer. It started with £100,000 cash and spent £11,967 on its initial route/fleet. These tests establish lifecycle causality, not annual commercial profitability.

| Site | Unserved control: actual physical closure | Served comparison: actual physical closure |
|---|---|---|
| Coalbrookdale coal, ID 1 | **1837-04-07** | **1839-04-14** |
| Nachtigall/Ruhr coal, ID 11 | 1837-04-07 | 1837-04-08 |
| Queen Louise/Silesian coal, ID 12 | 1837-04-07 | 1837-04-08 |
| Dolcoath copper, ID 438 | 1837-04-07 | 1837-04-08 |

The served mine earned its extension on **1832-11-30** after a real 36-month observation window: **2,060 units transported, 38% of observed production**. Its forecast moved to 1839-01-01. The actual physical survival difference was **737 days**, about two years. It still closed within the capped test year. Other pilot mines received no service extension. One-day differences arise from engine command/poll timing and the service setup; no artificially equal timing is asserted.

Initial warnings appeared on 1832-01-08 (control) and 1832-01-09 (served). Each unextended closure followed **1,916 days** of notice; the served mine had **2,652 days**. Forecasts identify the requested closure window, not an exact deletion day: arming, monthly callbacks and the physical removal update add approximately three months in these runs. Production-policy latest years are year bounds; do not interpret January 1 forecasts as promises of same-day deletion. Failure/late-notice cases defer or remain open rather than fabricating success.

Native levels actually fell **16 → 14 → 12 → 10 → 8** in the comparisons. Monthly coal/copper output fell accordingly; e.g. comparable unsupplied samples around 160–180 units at level 16 became 80–90 at level 8. The larger Silesian mine retained a higher base output. These are game-production observations, not ore-grade or geological reserve measurements. The normal policy's resource-specific stage timings remain proposals.

Loading was observed and the served route registered a **£91 positive sampled net vehicle-income increase at its accepting destination**. This is not a gross cargo invoice or annual profit. Monthly transport counters measure cargo picked up; the independent paid-delivery observation establishes that this route actually delivered, not that every counter unit was audited to payment. See [paid delivery](research/phase7b_paid_deliveries.csv), [monthly ledger](research/phase7b_production_service_ledger.csv), [annual observation totals](research/phase7b_annual_observations.csv) and [survival comparison](research/phase7b_survival_comparison.csv).

## Safety and persistence matrix

| Case | Actual result | Scope/limit |
|---|---|---|
| Bare level 4 at allowlisted original mine | Survives without nonce; later explicit valid handshake physically removes it | Full Europe neutral mine, not a newly created substitute |
| Parameter 11 OFF | Controller refuses commands; direct arm/commit attempts leave the original mine alive | Separately editor-saved OFF control; normal candidate unchanged |
| ON, zero enrolled legacy sites | Zero enrollment and no native legacy commands | Initial full-Europe controller check |
| Missing GS | No script ran; 542 industries survived 162 calendar days | Isolated profile without registered info; saved script table empty |
| Wrong GRF version | Explicit safe refusal on 0.4 | No version-5 legacy commands |
| Missing/partial/mismatched state | Eight deliberate cases rejected before authorization | Missing ledger, missing field/site, contract, identity, deadline, unknown state and an attempted scheduled-event alias onto an original mine |
| Expired nonce | Original selected mine survives commit after 150 days | Unregistered same-type mine and different-type industry also survive |
| Reused original engine ID | New industry 1 at tile 4488074 survives stale legacy row; row becomes LOST | Different location/date, actual engine construction |
| Exact old tile reuse | **Not executed successfully:** native `ERR_SITE_UNSUITABLE` | No bypass or terrain alteration. Exact subrule unresolved; do not claim a same-tile engine pass |
| Replacement after actual closure | New regional coal working built using Phase 7A `Open`, protected and recorded | Explicit test-only replacement rule, not an automatically deployed production promise |
| Save/load | Before warning (1831), during warning (1833), before closure (1836), after closure (1840) | Supported engine saves; no binary edits |
| Checkpoint replay | Significant authorization, closure and final transitions exactly matched | Same saved RNG/checkpoint; no cold-map byte-identity claim |
| Migration from 7A | Default refusal; explicit adopt-only retained three old events, enrolled zero legacy sites, then reloaded | Does not silently activate four-site policy on an existing campaign |
| Five-year natural control | 47 starting industries at density 4, zero unplanned openings over 1,834 days | Small map with exact 0.5 GRF |
| Original scheduled lifecycle regression | Four openings and four physical closures, replacement, 31-year run to 1861 | Small fixture, accelerated lifecycle dates, no enrolled Europe sites |
| Dedicated server | Multiplayer true, four-site ledger restored, public linked news returned success, clean quit | Actual dedicated driver on loopback, **zero human clients** |

Closure authorization includes original identity plus a one-shot persistent nonce. A missing GS after arming cannot issue commit; an already committed legitimate engine closure may still complete. No claim is made that stopping the GS reverses an irreversible authorized command.

## Preservation and performance

The normal candidate's **CITY, INDY, PATS, PSAC and all normalized map bytes** are identical to Phase 7A at start. There are 617 towns, 542 industries, 15 active GRFs, 96 registered types and 64 cargos. Calendar is 1830, economy 1800. Seven-tile trains, maintenance, inflation and all other stored settings are preserved. Only DATE's unique identifier differs inside that table. See [preservation diff](research/phase7b_preservation_diff.json).

After physical closures, the engine confirmed **538 unmanaged identities intact**, **zero unmanaged native production-level changes**, **zero unmanaged control-flag changes**, all 617 towns present, FOOD acceptance **76**, GOOD acceptance **69**. Normal production/cargo counters and town growth evolve during gameplay; raw runtime industry rows are not claimed byte-identical after ten years.

Each ten-year comparison used four staged save/reload invocations, about **435.5 / 435.7 seconds** of combined harness time on this PC. Those budgets include paused/idle ticks and save work; they are not loading-only benchmarks or multiplayer frame-rate measurements. The final small 31-year regression took 4.578 seconds; dedicated restoration/news smoke took 1.765 seconds. State retains 36 observations per enrolled mine, not an unbounded history. Engine files and state-size receipts remain local; portable paths/hashes and raw logs are included.

At the served comparison's final checkpoint, the saved GS payload was **43,736 bytes**, including the complete baseline ledger and fixture route state; the save was 8,235,338 bytes. Per-checkpoint sizes/hashes are included in engine receipts. Final focused verification passed **18 Phase 7B tests**, plus the unchanged Phase 7A (19), Phase 6B (10) and Phase 6C (16) suites: **63 passing tests**. These unit checks reconcile real-engine receipts; they are not 63 additional engine simulations.

## Reproduce

Build with the existing pinned AXIS environment and prepared 0.4 source; missing assets produce explicit failure, never an implicit substitute. Commands run from repository root, Python without `-O`:

```powershell
python scripts/lifecycle_phase7b_inventory.py
newgrfs/axis-historical-europe/.venv/Scripts/python.exe newgrfs/axis-historical-legacy/build_candidate.py
python scripts/lifecycle_phase7b_policy.py
python scripts/lifecycle_phase7b_probe.py
python scripts/lifecycle_phase7b_compare.py control
python scripts/lifecycle_phase7b_compare.py served
python scripts/lifecycle_phase7b_safety.py
python scripts/lifecycle_phase7b_validate.py controls
python scripts/lifecycle_phase7b_validate.py soak
python scripts/lifecycle_phase7b_validate.py roundtrip
python scripts/lifecycle_phase7b_validate.py migration
python scripts/lifecycle_phase7b_validate.py dedicated
python scripts/lifecycle_phase7b_validate.py replay
python scripts/lifecycle_phase7b_postcheck.py
python scripts/lifecycle_phase7b_evidence.py
python -m unittest discover -s tests -p test_phase7b_legacy.py
```

The named editor candidate and the OFF control require actual UI saving. `lifecycle_phase7b_candidate.py --stage-editor` stages a copy; save a new file, then run it without flags to validate/package that engine save. Never save over the original 0.3 or 0.4 scenario. Existing build trees require explicit `--rebuild`. The compiler artifacts and scenario are local, not redistributed in Git.
