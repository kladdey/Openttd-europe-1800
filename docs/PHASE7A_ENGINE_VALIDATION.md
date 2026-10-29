# Phase 7A — Engine validation and reproduction

All engine results below used **stock JGRPP 0.73.4 Windows x64**, SHA-256 `1b3fd69c1ea5f77eebe881c6d8a6ad9a03b71f98928a05e0c3c08c79482e2789`. No engine patch was compiled or substituted. Source files inspected are individually hashed in [source receipts](research/phase7a_engine_source_receipts.json). Earlier Phase 6B/6C evidence was reused and preserved.

## Assets and preservation

| Asset | SHA-256 |
|---|---|
| Original Inland Markets 0.3 scenario | `afcab50864e87f56a7260c62d87bd37560fa3d7676713afb14c480c555d0bc06` |
| Original Historical AXIS 0.3 GRF | `f0da622873c91107fa4d2b768d88cd95d5db009c2b2975bdb6d7ab6caaed3c33` |
| Separate Historical AXIS 0.4 lifecycle GRF | `e05de519b4695bc68bde7064c17ee0ae833edfe281579c3b92cb79532f466c52` |
| Editor-created Lifecycle Foundation scenario | `e73952d2ec40f0fb6ad5dce9753c9254e2df1e317c8d5cd7e25e8042f8ce03fc` |

The 0.4 build was repeated and produced the identical GRF hash. Its engine NewGRF partial MD5 is `1517ac2ebc706df1e4fab6ecf61024bd`; this is not the whole-file MD5. GRFID remains `4B484531`, version 4, minimum-compatible version 3. New parameter 11 defaults off; only the separate experimental scenario enables it.

The scenario was created through actual Scenario Editor operations, saved and reopened in the Windows GUI. The named candidate is an exclusive byte-for-byte copy of that editor save, not a patched compressed scenario. Initial **CITY, INDY, all map layers, PATS and PSAC** match the 0.3 baseline. The only differing chunks are GLOG, DATE, VIEW, GSTR, GSDT and NGRF. DATE differs only in unique save identifier; both start clocks remain unchanged. VIEW is editor viewport state; NGRF records the explicit version/parameter change and the remaining fourteen references are preserved. All 617 town records and 542 initial industry records are identical.

The exact production script/schedule passed two gameplay save/reload runs with no premature events and all initial map/town/industry/settings records intact. Experimental scenario, assets and configuration are isolated. No original save, normal cfg, scenario or GRF was overwritten.

## Actual test results

| Scope | Result | Limits |
|---|---|---|
| Small-map availability/closure probes | Original 0.3/off reject coal deity construction; 0.4 opt-in admits it and physically removes a selected mine | Other mine survives; future refinery 67, coast and production-minimum checks remain enforced |
| Small-map natural control | Both versions: 47 initial industries, zero new unplanned industries over 1,834 days at density 4 | Not an all-economy or 195-year proof |
| Small-map ordinary opening dates | South Hetton 1833-08-11, Zollverein 1851-01-03, Guido 1860-01-13; three real openings over 31 years | Abstract test coordinates, genuine production eligibility dates, approximately fortnightly polling |
| Small-map vertical slice | Operating producer/consumer, actual coal loading/payment, warnings, three physical closures, replacement, checkpoint reload | Compressed test lifetimes; replacement still closing at that run's end |
| Full Europe regional slice | Three new mines plus replacement, four physical closures by 1832-12-31, checkpoint reload and post-closure reload | Explicit test dates and regional extension sites; not a claim of actual named historical mine operation in 1830 |
| Small-map normal-year warning | Three mines warned in 1851/52/53 and requested closure in 1861/62/63; 3,662/3,661/3,661-day lead; actual deletion follows | 30-year test lifetimes, 35-year run to 1865; production lifetimes stay 110–140 years |
| Same-checkpoint replay | Significant openings/decline/closing/closed transitions identical in two reruns | Saved RNG/state replay, not unrelated cold-map identity |
| Schema migration and rejection | Supported schema 0→1; rejected schema 99 preserved across another save/reload; lost ledger and changed schedule refused | Deliberately injected legacy/error conditions, not arbitrary save compatibility |
| Full Europe boundary tests | Finite service bonuses, safe timeout, late notice and bounded unsafe-site retries | Earlier service counters and pending states deliberately injected; clearly labelled in data |
| Native Windows GUI | Warning visible; clicking news centred the managed mine; editor candidate save/reload visible | Manual UI observation, not automated pixel inference |
| Actual dedicated server | `-v dedicated -D127.0.0.1:39873`, multiplayer true, four-event ledger restored, clean console quit | Startup/save-load smoke with zero human clients; no three-client desync/closure campaign test |

The corrected dedicated test used the **dedicated video driver**. An earlier null-driver run with `-D` reported multiplayer false and is not counted as evidence. Likewise, early fixture construction errors and an incorrectly selected future-industry probe were diagnostic failures, not passes; the final future gate explicitly uses Copper Refinery **local ID 67**.

### Final full-Europe event coordinates

Exact observed dates and signatures are in [event CSV](research/phase7a_engine_events.csv). The test plan is [retained separately](research/phase7a_europe_test_schedule.json).

| Test event | Region / coordinates | Actual test opening | Meaning |
|---|---|---|---|
| `test_gb_coalfield` | Wolverhampton district, **2954,1095** | 1830-02-06 | New managed extension, source-backed regional coal geography |
| `test_de_coalfield` | Ruhr/Münster district, **1953,1251** | 1830-06-14 | New extension satisfying native town/proximity restrictions |
| `test_pl_coalfield` | Katowice district, **748,1495** | 1830-10-05 | New Upper Silesian extension |
| `test_replacement` | Leeds district, **2859,927** | 1831-06-17 | Opens only after first mine is physically absent; elsewhere, not an identical replacement at the old tile |

Production-source opening coordinates were tested on the small map at **150,40**, **150,150** and **214,210** respectively. These are fixture coordinates; do not interpret them as Europe geography. Production Europe anchors are 2862,736 / 1980,1280 / 753,1476, subject to the collision caveat in [architecture](PHASE7A_LIFECYCLE_ARCHITECTURE.md).

### Deliveries and economics

The small route recorded a **£233 positive sampled net vehicle-profit increase**; the final full-Europe route recorded **£64**, retained in [paid-delivery CSV](research/phase7a_paid_deliveries.csv). Cargo was observed loaded, then positive vehicle income near an accepting coal stop. These are actual game observations, **not gross shipment invoices, annual profit or proof of commercial balance**. Company starting cash was £100,000; no arbitrary cash grant was added. Coal acceptance used actual AXIS definitions and an existing Europe consumer.

After the final Europe closures, all baseline 542 industry signatures and 617 towns survived, no unplanned industry appeared, and two test horse vehicles remained. Post-closure FOOD acceptance was 76 industries and GOOD 69. Closure does strand assets and requires players to adapt; it does not silently refund investments.

## Performance and evidence boundaries

The final Europe test's exact elapsed times and commands are stored in the run receipts. It simulated three calendar years, using an initial checkpoint run plus 120,000 null-driver ticks after reload; combined harness time was roughly two minutes on this PC. These include simulation, idle/paused ticks and save work, **not isolated loading benchmarks**. No crash or runaway placement loop occurred. The actual dedicated startup/save-load smoke completed in 1.532 seconds. The script scans a bounded three-event production schedule, not all 96 types every tick.

Full 195-year progression, all production Europe sites, other economy modes, player-funded closure, actual sustained 60-month service, three connected humans and severe balance impacts remain unverified. Initial candidate preservation is byte-exact; ordinary gameplay evolution after running is not expected to preserve every town/population/map byte.

## Reproduction

Run from repository root with Python **without `-O`**. Build commands require the existing prepared 0.3 source and pinned AXIS environment; see [candidate build instructions](../newgrfs/axis-historical-lifecycle/README.md). Scripts record resolved commands, input hashes, logs, script hashes, dates, seed and saves in unique isolated case folders. No raw save encoding is used.

```powershell
# Build once; an existing prepared candidate requires explicit --rebuild.
newgrfs/axis-historical-europe/.venv/Scripts/python.exe newgrfs/axis-historical-lifecycle/build_candidate.py
python scripts/lifecycle_phase7a_schedule.py
python scripts/lifecycle_phase7a_probe.py
python scripts/lifecycle_phase7a_fixture.py
python scripts/lifecycle_phase7a_soak.py natural
python scripts/lifecycle_phase7a_soak.py historical
python scripts/lifecycle_phase7a_warning_years.py
python scripts/lifecycle_phase7a_europe.py --smoke
python scripts/lifecycle_phase7a_europe_plan.py
python scripts/lifecycle_phase7a_europe_slice.py
python scripts/lifecycle_phase7a_persistence.py replay
python scripts/lifecycle_phase7a_persistence.py migration
python scripts/lifecycle_phase7a_boundaries.py
python scripts/lifecycle_phase7a_candidate.py
python scripts/lifecycle_phase7a_contract_test.py
python scripts/lifecycle_phase7a_dedicated.py
python scripts/lifecycle_phase7a_evidence.py
python -m unittest discover -s tests -p test_phase7a_lifecycle.py
```

The editor creation and GUI visibility checks are manual steps; tooling does not pretend to recreate those through a missing API. The existing editor manifest and profile are prerequisites to Europe/candidate helpers. To recreate on another PC: copy the original into a new isolated profile, load that copy in Scenario Editor, select separately compiled 0.4 with old parameters preserved and parameter 11 enabled, attach GS v1, save as a **new** scenario, reopen, and verify preservation before running gameplay tests. Do not alter the source scenario's embedded configuration in place.

Portable JSON/CSV receipts are committed; large local logs, copyrighted graphics, compiled GRFs and save/scenario files are excluded from Git. Raw logs remain on this PC and their hashes are in the receipts. Negative-test FATAL messages are expected only in clearly labelled rejection cases. The focused unit suite reconciles these independently captured receipts and validates compiler rejection cases; it does not rerun the engine implicitly.

Final verification: **19 Phase 7A tests passed**, along with the unchanged Phase 6B suite (10) and Phase 6C suite (16): **45 passing tests**. The retained receipts cover **29 engine invocations, 830 event records and two paid-delivery observations**. This is not a count of 830 independent gameplay experiments. The editor UI observation is separately recorded in [its manual receipt](research/phase7a_editor_observation.json).
