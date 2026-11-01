# Phase 7C — implementation and reproduction

## Components

Historical AXIS **0.6.0 expansion candidate**, GRFID `4B484531`, native version 6 / minimum compatible version 5, is separately compiled from the pinned 0.5 source. The lifecycle parameter remains **default off**. The isolated campaign candidate explicitly retains its opt-in parameter, all other parameters and the existing fifteen GRF identities. No engine patch, rolling-stock change or direct scenario-byte edit is used.

GameScript v3 is the same persistent Historical Industry Lifecycle controller: `ExpansionLifecycleController extends LegacyLifecycleController extends LifecycleController`. The package concatenates the retained v1/v2 controller files with `expansion.nut`; its entry point is `expansion_info.nut`. The prior scripts/policies remain untouched. The Phase 7B primary-industry template is byte-identical. All 96 model source hashes match the previously audited matrix (`phase7c_recipe_source_checks.json`).

The schema-3 ledger retains the original scheduled events and four mine rows, and adds ten expansion rows plus one processor row. Full policy text is contracted into a deterministic hash. Save/reload preserves statuses, instance fingerprints, attempts, notices and authorization. Changed contracts and partial ledgers fail closed. Each new industry is identified by engine ID, type, location and construction date; lost/reused identities are never silently rebuilt. Non-native Squirrel `base.Method` calls and non-suspending `.call()` are avoided: inherited game-command methods use `.bindenv(this)`.

## Capacity and physical closure

Stock `SetProductionLevel` alone does not scale AXIS secondary processing: its normal production callback runs on cargo arrival. The new adapter applies **only** to the original mill's full tile, construction date, founder, random bits and layout, with lifecycle/historical/Classic gates enabled. Unregistered flour mills and every other secondary type retain their ordinary callbacks.

The adapter holds incoming cargo and processes at most one **eight-unit batch per input** every `16 - production_level` native 256-tick cycles. At normal level 16 the original arrival processing remains intact. Decline levels 14/12/10/8 progressively space complete batches. Partial batches stay in native input storage. Input and output ratios and the existing combinatory calculation are retained. This avoids the rejected prototype's defect where one-unit processing could round production to zero. Integer rounding/batch timing can differ from ordinary immediate processing; the change is narrowly confined to this retiring instance. A low-volume route need not visibly lose throughput until the cap binds.

The exact-instance monthly callback reserves PSA slots 200–202 for the one-shot protocol and 203 for the capacity-cycle counter. Existing recipe storage is below these slots. Level 11 arms a fingerprint-derived token, with NoClosure protection. After 40 economy days (no later than day 65), GS rechecks identity and the live local successor, clears NoClosure and commits level 4. The native callback independently checks the fingerprint and a token age of at most 90 calendar days, consumes the token and returns the supported physical-close result. GS reports closure only after the instance disappears. An unarmed level-4 request, expired token or unrelated mill cannot authorize closure. A timeout reprotects the site instead of reporting success.

News uses calendar time. The baseline deliberately has calendar 1830 and economy 1800; `GSDate.GetCurrentDate()` is economy time. The existing server-side StoryPage timestamp probe obtains actual calendar time and immediately removes the unshown page. Wallclock mode is rejected. Raw event `calendar` can precede `born` by a day when a native build suspends execution; use the native construction date for the exact physical opening date.

## Migration policy

Do **not** replace a GRF in an existing campaign. The delivered scenario is a separately engine-saved copy of the pinned 0.5 initial baseline. The prior scenarios, binaries, normal configuration and saves remain intact.

Loading a v2 ledger into v3 defaults to refusal. An explicit test-only `adopt_only` policy can retain its old mine/scheduled ledger while enrolling **zero** new expansion events and **zero** processors. That path and its reload were exercised in the stock engine. It does not enable this expansion policy in an ongoing save. General migration of a developed live campaign, arbitrary policy edits or changed cargo definitions is not supported. Version 6's compatibility declaration is not a promise that arbitrary substitutions are safe.

## Reproduce locally

Use the preserved local assets and the pinned build virtual environment. These scripts intentionally refuse missing/changed baseline assets rather than download or overwrite them implicitly.

```powershell
$p = 'C:/Users/Kladd/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& newgrfs/axis-historical-europe/.venv/Scripts/python.exe newgrfs/axis-historical-expansion/build_candidate.py --rebuild
& $p scripts/lifecycle_phase7c_policy.py
& $p scripts/lifecycle_phase7c_controls.py
& $p scripts/lifecycle_phase7c_validate.py europe
& $p scripts/lifecycle_phase7c_capacity.py
& $p scripts/lifecycle_phase7c_waves.py mini
& $p scripts/lifecycle_phase7c_safety.py blocked
& $p scripts/lifecycle_phase7c_safety.py native
& $p scripts/lifecycle_phase7c_safety.py off
& $p scripts/lifecycle_phase7c_safety.py assets
& $p scripts/lifecycle_phase7c_safety.py replay
& $p scripts/lifecycle_phase7c_safety.py dedicated
& $p scripts/lifecycle_phase7c_regression.py
& $p scripts/lifecycle_phase7c_chains.py
& $p scripts/lifecycle_phase7c_evidence.py
& $p -m unittest discover -s tests -p 'test_phase7*.py'
& $p -m unittest discover -s tests -p test_industrial_phase6b.py
& $p -m unittest discover -s tests -p test_inland_phase6c.py
```

For a new editor candidate, run `lifecycle_phase7c_candidate.py --stage-editor`, save a new `UNNAMED.scn` through JGRPP's actual editor, then run the script without arguments. Each staging profile is unique; prior candidates are preserved. The separate 1864 fixture was also saved through the editor's supported year control, under `f.scn`; `future-fixture.json` records its path. `lifecycle_phase7c_waves.py europe` uses that disposable snapshot and normal 1865 dates. It is not a continuous 1830→1867 economic run.

The small-map fixture uses real historical years through 2026 but abstract sites, two seed industries and explicitly omitted endpoint gates to isolate construction/persistence. It cannot prove Europe geography, future supply or revenue. The Europe early fixture compresses openings and retirement dates, retains a genuine five-calendar-year warning and operates real period road services without a cash grant. None of those test policies is packaged into the historically paced candidate.

The read-only evidence collector checks all initial map planes, CITY/INDY/PATS/PSAC, parameters and identities before making an exclusive separate copy in Documents/OpenTTD/scenario. The launcher checks the candidate, engine, GRF, script, policies, info file and all isolated asset archives/files. Use that launcher rather than opening the scenario through an unrelated profile which may select different GS or GRF versions.
