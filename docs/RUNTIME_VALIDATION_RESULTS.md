# Runtime validation of the NARS/UKRS2 running-cost forensics

Measured on the project PC, November 2026, in JGRPP 0.73.4 with the production GRF
set. This checks the predictions in:

- [CLAUDE_FLEET_DISCREPANCY_REINVESTIGATION.md](CLAUDE_FLEET_DISCREPANCY_REINVESTIGATION.md)
- [NARS_UKRS2_RUNNING_COST_FORENSICS.md](NARS_UKRS2_RUNNING_COST_FORENSICS.md)
- [UKRS2_UNDERPRICING_ASSESSMENT.md](UKRS2_UNDERPRICING_ASSESSMENT.md)
- [FLEET_BALANCE_INDEPENDENT_RECOMMENDATIONS.md](FLEET_BALANCE_INDEPENDENT_RECOMMENDATIONS.md) (§6 test plan)

**Labels.** Every number is labelled:

- **RUNTIME**: measured in the game in this work.
- **SOURCE**: read from code or a GRF/debug log.
- **DERIVED**: calculated from RUNTIME values.

Evidence lives in [`docs/research/runtime_validation/`](research/runtime_validation/):
- tables `t1_*.csv` … `t6_*`;
- one folder per run under `runs/<tag>/`, holding the filtered log `evidence.log`, the
  full configuration in `manifest.json`, and `receipt.json` with the exit reason and the
  full-log SHA-256.

The harness is in [`scripts/runtime_validation/`](../scripts/runtime_validation/).

## 0. Environment and isolation

| Item | Value |
| --- | --- |
| Engine | `C:\Users\Kladd\Downloads\OpenTTD\openttd.exe`, changelog `v0.73.4 (2026-10-12)`, config `version_string = jgrpp-0.73.4`, SHA-256 `1b3fd69c…2789` (same binary as the prior Codex audit) |
| Production config | `C:\Users\Kladd\Documents\OpenTTD\openttd.cfg`. Its 15-GRF list is identical (GRFID, MD5, parameters, order) to the scenario's |
| Scenario | `Europe 1830 Historical AXIS 0.6.0 - Phase 7I Transport-Driven Growth.scn` (chosen by the user), SHA-256 `88d7a56e…a647`. Calendar date 1830-01-01 against economy date 1800: **10,957 days (30 years) apart**, decoded from its DATE chunk (RUNTIME/SOURCE) |
| Vehicle GRFs | NARS 2.52 (`44440302`), NARS Add-On 2cc 2401131718 (`4E4D0518`, params 4 3 2), UKRS2 1.05 (`44441000`, params 0 0 0 0 0 3 2), GETS 0.7, PTS 3.0.3, PRSP 0.19.11 |
| Industry GRF | Historical AXIS **0.6.0** expansion candidate (`4B484531`). This is what production uses. AXIS 2.3.1 is installed but not active |
| Settings | Inherited from the scenario's PATS: running cost low (`vehicle_costs` 0), `vehicle_costs_in_depot`/`_when_stopped` 1, inflation off, realistic acceleration, slope 3%, 7-tile trains, freight ×1, breakdowns reduced, infrastructure maintenance on, calendar timekeeping, day length 1. Each run logs them (`RV_SETTING`) |

**Isolation (hard rules kept).**

- No production GRF, scenario, savegame, `openttd.cfg` or economy setting was modified,
  and none was loaded for writing.
- Every run uses a generated 256×256 heightmap fixture in its own directory under
  `C:\Users\Kladd\OTTD-runtime-validation\runs\`, with its own `test.cfg`.
- GRFs come from a single test copy, hard-linked into each run.
- OpenTTD ran with `-X` (no personal or global search paths) and `-x` (never write the
  config).
- SHA-256 of the executable, production config, Phase 7I scenario and every production GRF
  was checked before and after each suite, and passed every time. The config and scenario
  were also checked around every run.

**Fixture.**

- Flat ground at height 2; a coal mine and a coke oven built by the GameScript.
- 32-tile line, 7-tile stations, full load at the mine, unload at the oven.
- Rolling stock: NARS Single Hopper (local 101), as in the Codex experiments.
- One train, no competitors.
- Industry production level fixed at 16 (the Codex setting, about 2,700 t/yr produced)
  or 128 (saturated).
- Year 1850 unless stated.

**Deviations from a production game.**

- Calendar and economy dates start together on generated fixtures. The scenario's 30-year
  offset is tested separately (§5).
- Subsidies are on in the scenario. They contaminated revenue at production level 128
  (see note in §1), so the saturated results use a subsidies-off control.
- The bootstrap AI company had autorenew on (set from the GameScript, not the config). The
  first age run was renewed at 25.6 years, so it was rerun with autorenew off; that run is
  marked superseded.

**Mishap during the work.** The first harness copied the GRFs into every run, about
408 MB each. After about 200 runs this filled drive C:. I deleted only those per-run copies
and switched to hard links to one test copy. No production file was involved, and the guard
confirmed that. A few runs that died for lack of space were deleted and rerun.

## 1. Test 1: four-locomotive comparison, 32 tiles, 4 seeds

Seeds 734–737. The commissioning year (1850) is excluded, leaving years 1851–1855, i.e.
4 seeds × 5 years per cell. Units:

- **t/yr**: tonnes unloaded at the oven (RUNTIME). It equals the company's
  completed-quarter delivery counter.
- **running**: the ledger "train running" expense (RUNTIME).
- **net**: revenue − running − property (DERIVED).
- **speed**: mean `GetCurrentSpeed` over moving samples, in km-ish/h (RUNTIME).

Source: [`t1_summary.csv`](research/runtime_validation/t1_summary.csv) and
`t1_years.csv`.

**Codex consist, production level 16 (supply as Codex had it):**

| Loco + hoppers | t/yr mean [min–max] | Running £/yr | Revenue £/yr | Net £/yr | Speed moving / loaded |
| --- | --- | --- | --- | --- | --- |
| Planet 12 | 684 [480–720] | 976 | 10,377 | 8,501 | 20.3 / 15.3 |
| Grasshopper 12 | 540 [480–720] | 3,716 | 7,964 | 3,348 | 16.1 / 12.3 |
| Norris 12 | 1,044 [960–1,200] | 6,162 | 15,880 | 8,818 | 34.5 / 29.1 |
| Coppernob 12 | 1,224 [960–1,440] | 1,290 | 18,614 | 16,424 | 42.3 / 37.1 |
| Planet 6 | 606 [600–720] | 680 | 9,605 | 8,025 | 35.9 / 31.7 |
| Grasshopper 6 | 456 [360–480] | 3,467 | 7,228 | 2,861 | 27.6 / 23.5 |
| Norris 6 | 780 | 6,362 | 12,363 | 5,101 | 45.9 / 43.0 |
| Coppernob 6 | 882 | 1,120 | 13,980 | 11,960 | 52.3 / 49.3 |
| Planet 4 | 472 [400–480] | 593 | 7,587 | 6,094 | 41.0 / 38.9 |
| Grasshopper 4 | 364 [320–400] | 3,377 | 5,851 | 1,575 | 32.2 / 29.7 |
| Norris 4 | 560 | 6,266 | 9,002 | 1,836 | 49.0 / 47.2 |
| Coppernob 4 | 628 [560–640] | 1,019 | 10,095 | 8,176 | 55.4 / 53.7 |

**Saturated supply (level 128, subsidies off), 12 hoppers:** Planet 708 t, Grasshopper
540 t, Norris 1,188 t, Coppernob 1,464 t (RUNTIME). Running costs are within 3% of level 16.

**Comparison with the Codex run.** The Codex results were found locally, uncommitted, in
`Documents\Codex\2026-10-28\openttd-europe-1830-2025-local-newgrf\docs\fleet_simulation_results.csv`.
That was seed 734 only, on the same fixture design and AXIS 0.6.0.

| 12 hoppers | Codex t/yr | Measured t/yr (4 seeds) | Codex running | Measured running |
| --- | --- | --- | --- | --- |
| Planet | 660 | 684 | 1,012 | 976 |
| Grasshopper | 540 | 540 | 3,773 | 3,716 |
| Norris | 1,020 | 1,044 | 5,979 | 6,162 |
| Coppernob | 1,140 | 1,224 | 1,245 | 1,290 |

The Codex numbers are reproduced to within 0–7% (DERIVED). They were real measurements,
not fabrications; they had simply never been committed.

Observations:

- Planet and Grasshopper with 12 hoppers are speed-bound at 12–15 km-ish/h loaded. Their
  output barely responds to supply: 684 vs 708 t.
- Halving the consist to 6 hoppers costs Planet only 11% of its tonnage, and raises
  Grasshopper's moving speed by 71%.

**Revenue note.** In the first saturated runs, some years paid about 2.3× per tonne for the
same tonnage. A control with `subsidy_duration = 0` returned revenue per tonne to the
level-16 value: for example, Planet 4 earned £7,523 against £7,587. The saturated mines were
attracting subsidies. Only the subsidies-off revenues are used here.

## 2. Test 2: running cost by state and age (`GSVehicle.GetRunningCost`)

**Method.**

- One consist per locomotive (loco + 4 NARS hoppers) in service from 1845 to 1876, 31 years.
- A second, identical consist built at the same moment and kept stopped in the depot.
- The running consist was sampled every 5 ticks and classed as: moving loaded, moving
  empty, standing at a platform while loading, unloading, other stop, or in depot.
- Seeds 734 and 735. Source: `t2_state_by_age.csv` and `t1_years.csv`.

**Separating engine from wagons (DERIVED).** Each NARS hopper adds exactly £38 to the
consist rate in every state:

- Planet: 4 / 6 / 12 hoppers move at £546 / 622 / 850 and stand at £283 / 359 / 588.
- Norris and Grasshopper show the same +£38 steps.

So the hoppers are flat at their catalogue rate, and engine rate = consist rate − 38 × n.

**Engine rates, age 0 to the first step (RUNTIME consist rate, DERIVED engine rate):**

| Engine (catalogue) | Moving loaded | Moving empty | At platform, waiting for full load | In depot | Moving/catalogue | Stationary/catalogue |
| --- | --- | --- | --- | --- | --- | --- |
| UKRS2 Planet (£525) | £394 | £394 | £131 | £131 | **0.75** | **0.25** |
| UKRS2 Coppernob (£1,181) | £787 | £787 | £394 | £394 | **0.67** | **0.33** |
| NARS Norris (£6,300) | £6,300 | £6,300 | £1,575 | £1,575 | **1.00** | **0.25** |
| Add-On Grasshopper (£3,150) | £3,150 | £3,150 | £3,150 | £3,150 | **1.00** | **1.00** |

**Platform waits are billed at the stationary (depot) rate** for UKRS2 and NARS. The
rate in the "standing at a platform while loading" class equals the depot rate, and so
does the stopped twin in the depot. So the discount follows speed 0, not depot occupancy.
The Add-On charges full rate while waiting.

**Age (RUNTIME).**

- UKRS2 costs rise in **discrete steps at fixed ages**, not linearly:
  - Planet steps at exactly 12.0 and 24.0 years (age 4,383 and 8,766 days);
  - Coppernob steps at 9.0 and 21.0 years.
- Each step adds 3 factor units (+£394/yr) to the moving rate:
  - Planet moving engine goes 394 → 787 → 1,181;
  - Coppernob 787 → 1,181 → 1,575.
- The stationary rate steps too: Planet 131 → 394 → 525.
- Both seeds give identical step ages and rates.
- NARS Norris and the Add-On Grasshopper are flat at every age to 31 years. Only the billed
  totals move, with the share of time spent moving.
- The engines' maximum ages (Planet 9,150 days, Coppernob 10,248 days) do not coincide with
  the steps.

**Billed lifecycle (RUNTIME means across both seeds; ratios DERIVED):**

| Ages | Planet | Grasshopper | Ratio | Norris | Coppernob | Ratio |
| --- | --- | --- | --- | --- | --- | --- |
| 1–5 | £578 | £3,338 | 5.78× | £6,192 | £1,047 | 5.92× |
| 1–20 | £747 | £3,388 | 4.54× | £6,270 | £1,245 | 5.04× |
| 1–31 | £1,009 | £3,423 | 3.39× | £6,274 | £1,466 | 4.28× |

The Planet bill rises from £510 (age 1) to £2,116 (age 31), seed 734.

## 3. Test 3: compatibility-GRF proof (test directory only)

**The GRF.** [`make_compat_grf.py`](../scripts/runtime_validation/make_compat_grf.py) writes a 154-byte GRF, GRFID `52560001`. It contains:

- Action 8;
- Action 0 global property 0x11: source `52560001`, target NARS `44440302`;
- Action 0 global property 0x08: price 42 set to 0x0B, i.e. +3.

It has no vehicles, translation tables, sprites or callbacks. It exists only in
`runs\_compat\` and the run folders, and was loaded directly after the NARS Add-On, after
NARS.

| Pass criterion | Result |
| --- | --- |
| Debug line | **Present** (RUNTIME, `t3-catalogue-*-compat/evidence.log`): `'rv_nars_compat.grf' overrides price base multiplier 42 of '…newnars.grf'`, followed by `newnars.grf sets local price base multiplier 42 to 3` (the base run logs `to 4`) |
| Norris running £3,150 | **£3,150** (from £6,300), at both 1850 and 2000 (RUNTIME) |
| NARS purchase prices unchanged | **All 113 NARS 2.52 entries unchanged** at both dates (RUNTIME) |
| Add-On unchanged | **All 216 Add-On entries unchanged** in price and running cost (RUNTIME). UKRS2 (94) and GETS (1,602) are also unchanged |
| Scope of the halving | **Exactly 71 NARS 2.52 entries halve**: every locomotive, including the steam Mallet (£25,462 → £12,731), EMD/GE diesels, electrics and railcars. The 42 NARS wagons are unchanged (RUNTIME) |
| Billed cost in service | Norris + 4 hoppers, 32 tiles, 2 seeds: billed running **£6,281 → £3,276/yr**. Moving rate £6,452 → £3,302; stationary £1,727 → £939. Tonnage is identical (560 t/yr) (RUNTIME). The NARS stationary callback still works on top of the new base |

Not tested: multiplayer and savegame behaviour of adding this GRF, and a separate Add-On
compat GRF.

## 4. Test 4: graded and heavy freight

**Terrain.** A 20-tile sustained ramp, every tile an incline, so 3% on every tile
(`train_slope_steepness` 3). It runs from height 2 to 22 between the loading station
(bottom) and the unloading station (top). The height profile is logged (`RV_PROFILE`). Loaded
trains climb; empty trains descend.

**What a stall looks like.** JGRPP never lets a train come to a complete stop on a grade. A
train that cannot climb crawls at 2–3 km-ish/h and completes about 1 trip a year.

Source: `t4_early_summary.csv` and `t4_heavy_nosub_summary.csv`; 1850, saturated
supply, 2 seeds.

| Loaded hoppers | Planet | Grasshopper | Norris | Coppernob |
| --- | --- | --- | --- | --- |
| 1 | stalls (min 2, 20 t/yr) | stalls (2, 20 t/yr) | **climbs** (mean 31.9, 125 t/yr) | **climbs** (31.2, 135 t/yr) |
| 2 | stalls | stalls | stalls (40 t/yr) | **climbs** (22.1 mean; min 3 in one seed, 20 in the other: marginal) |
| 4 | stalls | stalls | stalls | stalls (80 t/yr) |

The same consists on flat track: Planet 1/2/4 hoppers deliver 130 / 250 / 480 t/yr, Norris
150 / 280 / 560, Coppernob 165 / 340 / 640.

**1914–45 heavy freight (1943).**

- Each train filled with NARS Large Hoppers to the 7-tile limit: 480 t for the Mallet and
  8F, 440 t for the Big Boy and Yellowstone.
- 4 seeds, 3 stable years, subsidies off.

| Loco | Flat t/yr | Flat net £/yr | 3% ramp t/yr | Ramp mean speed / min | Running £/yr | Purchase |
| --- | --- | --- | --- | --- | --- | --- |
| UKRS2 8F | 4,160 | **50,470** | **480 (stalls)** | 2.6 / 2 | 5,743 | 71,808 |
| NARS Mallet | 4,560 | 32,758 | 3,840 | 43.2 / 7–34 | 26,990 | 105,206 |
| Add-On Big Boy | 4,987 | 49,537 | 4,107 | 53.0 / 39 | 16,861 | 134,574 |
| Add-On Yellowstone | 4,253 | 42,279 | 3,777 | 51.3 / 10–42 | 14,222 | 129,886 |

All figures are RUNTIME means. Net is DERIVED.

## 5. Test 5: calendar or economy date for the UKRS2 surcharge

**Calendar-mode controls** (calendar = economy), catalogue cost (RUNTIME, `t5_date_basis.csv`):

| Year | 1900–1941 | 1945 | 1950 | 1955 | 1960 | 1970 |
| --- | --- | --- | --- | --- | --- | --- |
| Planet | 525 | 787 | 1,181 | 1,443 | 1,837 | 2,493 |
| Coppernob | 1,181 | 1,443 | 1,837 | 2,100 | 2,493 | 3,150 |
| 8F | 6,431 | 6,693 | 7,087 | 7,350 | 7,743 | 8,400 |
| Norris, Grasshopper | 6,300 / 3,150 at every year | | | | | |

**Discriminating run (`t5b-wallclock-frozen-1945`).**

- Setup: wallclock timekeeping with the calendar frozen at 1945, while the economy date
  that GameScript `GSDate` reports is **1920** for the whole run (RUNTIME, `RV_DATE`).
- The calendar is confirmed at 1945 independently: the 8F (1933) and Big Boy (1942) are
  buildable, and both appear by calendar date.
- UKRS2 catalogue costs equal the **calendar-1945** values: Planet £787, 8F £6,693. They do
  not equal the economy-1920 values (£525, £6,431).

So **the surcharge follows the calendar date**.

A first wallclock run that let the calendar run 12× faster did not advance the calendar
measurably, and is recorded as inconclusive (`t5b-wallclock-1900`).

## 6. Test 6: AXIS 2.3.1 against Historical AXIS 0.6.0

- **Every route measurement above already uses AXIS 0.6.0**, the production economy.
- Full routes on AXIS 2.3.1 could **not** be run. On the fixture, 2.3.1's industry
  availability callback makes `CanBuildIndustry` false for every coal producer and acceptor,
  even with the committed baseline parameter vector `0 0 0 0 0 0 16 150 80 300`
  (`runs/t6-probe`: `BLOCKED|coal industry types`). Building industries through the scenario
  editor would be needed, and was out of scope.
- Measured instead: the cargo payment schedule. `GSCargo.GetCargoIncome` was queried for
  COAL, COKE, PASS and GOOD at 16–128 tiles and 0–80 days, at 1850 and 1900.
- **All 120 quotes are identical between 2.3.1 and 0.6.0** (RUNTIME, `t6-income-*`). For
  example, coal pays £13/unit at 32 tiles, flat out to 80 days in transit.
- Revenue per delivered tonne is therefore the same under both economies. Differences can
  only come from industry behaviour (production, closures, acceptance), which this fixture
  fixes.

## 7. Prediction-by-prediction verdicts

C = confirmed, R = refuted, P = partly confirmed, U = untested.

| # | Prediction (source report) | Verdict | Measured value | Evidence |
| --- | --- | --- | --- | --- |
| 1 | Catalogue Planet £525, Grasshopper £3,150, Coppernob £1,181, Norris £6,300 (all four reports) | **C** | Identical (RUNTIME, 1850) | any `t1-*/evidence.log` `RV_ENGINE` |
| 2 | NARS 2.52 sets price 42 to +4; UKRS2 and Add-On +3 (forensics §2) | **C** | Debug log: NARS 4, UKRS2 3, Add-On 3, GETS −3, PTS/PRSP 1 (RUNTIME) | `t1-planet-4-l16-s734/evidence.log` |
| 3 | The +4 applies to all NARS 2.52 locomotives, diesel and electric included (forensics §2) | **C** | All 71 halve under the +3 override (RUNTIME) | `t3_compat_catalogue.csv` |
| 4 | Planet and Grasshopper are overloaded with 12 hoppers, near 650 t/yr, crawling at 16–22 (reinvestigation §4) | **C** | 684 / 540 t/yr; 15.3 / 12.3 km-ish/h loaded; output unchanged at saturated supply (708 / 540) (RUNTIME) | `t1_summary.csv` |
| 5 | Model ceilings Norris 1,509 and Coppernob 1,926 t/yr; shortfalls point to supply limits (reinvestigation §4) | **R** | Saturated supply gives 1,188 / 1,464 t/yr, 21–24% below the model (RUNTIME). The gap is not supply: the physics model overstates throughput | `t1_summary.csv` (`l128nosub`) |
| 6 | Coppernob's round trip about 22% shorter than Norris's (reinvestigation §4) | **P** | 6.1 vs 4.95 trips/yr saturated, i.e. 19% shorter (DERIVED) | `t1_years.csv` |
| 7 | The 32-tile Codex table is unverifiable (reinvestigation §0/§1) | **R** (it exists) | Found uncommitted on this PC; reproduced to 0–7% over 4 seeds (RUNTIME) | §1 table |
| 8 | Coppernob outperforms Norris (reinvestigation §1) | **C** | 1,224 vs 1,044 t/yr; net £16,424 vs £8,818 (12 hoppers, level 16) (RUNTIME/DERIVED) | `t1_summary.csv` |
| 9 | Norris/Coppernob billed about 4–5×, quoted 4.8× (forensics §7) | **C** | 4.78× with 12 hoppers, 6.15× with 4 (DERIVED from RUNTIME ledgers) | `t1_summary.csv` |
| 10 | Planet/Grasshopper 5.1× billed in years 1–5, about 3.5× over Planet's life (forensics §7) | **C** | 5.78× at ages 1–5, 4.54× at 1–20, 3.39× at 1–31 (DERIVED) | `t2_state_by_age.csv` |
| 11 | UKRS2 depot ≈ ¼ (forensics §5) | **P** | Planet engine 0.25; Coppernob engine **0.33** (RUNTIME/DERIVED) | §2 |
| 12 | UKRS2 moving-empty ≈ 0.77–0.81, dearer when loaded (forensics §5/§6) | **P / R** | Moving engine 0.75 (Planet) and 0.67 (Coppernob) of catalogue, **identical loaded and empty**. No load-dependent branch exists | §2 |
| 13 | NARS ¼ in depot, full while moving (forensics §5) | **C** | Norris engine 1,575 / 6,300 (RUNTIME/DERIVED) | §2 |
| 14 | Add-On flat (forensics §5) | **C** | 3,150 in every state and at every age (RUNTIME) | `t2_state_by_age.csv` |
| 15 | The NARS/UKRS2 "stationary" branch may or may not fire at a platform during a full-load wait (forensics §5, "the main open question") | **Resolved** | It fires: platform waits are billed at the depot rate (UKRS2 and NARS); the Add-On pays full | §2 |
| 16 | UKRS2 cost grows with age, about +£37/yr per year (forensics §6) | **P** (direction C, shape R) | Step function: Planet +£394 at 12 and 24 years; Coppernob at 9 and 21 years. Billed £510 → £2,116 over 31 years (RUNTIME) | §2 |
| 17 | Year-1 Planet billing above catalogue implies a load-dependent branch (forensics §6) | **R** | Loaded and empty rates are identical. The excess came from wagons and stop/start mix, not load | §2 |
| 18 | UKRS2 calendar surcharge: zero to 1913, +2 factor by 1945, +5 by 1950, same additive step for every engine; NARS, Add-On and GETS flat (forensics §6) | **C** | Planet +262 / +656 / +1,968 at 1945 / 1950 / 1970; 8F the same steps; Norris and Grasshopper flat. The onset lies between 1941 and 1945 (RUNTIME) | `t5_date_basis.csv` |
| 19 | The surcharge may follow economy time, i.e. 30 years later in the campaign (forensics §6, assessment) | **R** | It follows the calendar date (RUNTIME, §5). In Phase 7I the surcharge therefore arrives on the calendar schedule, 1941–45 | `t5b-wallclock-frozen-1945` |
| 20 | Graded: Coppernob lifts 2 loaded hoppers, Norris 1, Planet and Grasshopper 0; all stall with 12 (reinvestigation §4) | **C** | Exactly as predicted. Coppernob with 2 is marginal in one seed (RUNTIME) | `t4_early_summary.csv` |
| 21 | 1914–45 American TE advantage on 3% grades: 3–4× the trailing load against the UKRS2 8F (reinvestigation §4) | **C** (direction), **U** (magnitude) | At a full 7-tile load the 8F stalls (480 t/yr) while the Mallet, Big Boy and Yellowstone deliver 3,777–4,107 t/yr. Load ratios were not swept | `t4_heavy_nosub_summary.csv` |
| 22 | The compat GRF with a 0x11 override can halve NARS running only (recommendations §5) | **C** | All pass criteria met; billed Norris halves in service (RUNTIME) | §3 |
| 23 | A static prop 0x0D per-engine override is unreliable for NARS/UKRS2 (recommendations §5) | **U** | Not built | — |
| 24 | Grasshopper −50% insufficient, break-even about 2.2 years (recommendations §3) | **C** | At £1,575 the engine bills about £1,727 with 4 hoppers against Planet's £593, a £1,134/yr gap; the £2,344 capital saving is recovered in **2.1 years** (DERIVED from RUNTIME rates) | §1, §2 |
| 25 | Norris capacity-parity band £1,200–£2,400 against Planet (recommendations §3) | **C** (lower bound), model ratio **R** | The measured Norris/Planet throughput ratio is 1.68× (12 hoppers, saturated), not 2.3×. Parity per delivered tonne puts the Norris catalogue rate at about **£1,260** (DERIVED) | §8 |
| 26 | Grasshopper loses money on coal (reinvestigation §1, Phase 3) | **R on this fixture** | +£1,575/yr net with 4 hoppers and +£3,348 with 12, on AXIS 0.6.0 at 32 tiles. Phase 3 was a 26-tile AXIS 2.3.1 route with UKRS2 open wagons, so the routes differ | `t1_summary.csv` |
| 27 | Every profitability figure must be re-checked on AXIS 0.6.0 (all reports) | **Done**; 2.3.1 routes **U** | All runs on 0.6.0; payment schedules identical to 2.3.1; 2.3.1 industries cannot be built on the fixture | §6 |
| 28 | Class 66 billed reversal UKRS2 vs GETS (reinvestigation §1) | **U** | Not run | — |
| 29 | GETS flat in every state (forensics §5) | **U** | Not run | — |
| 30 | PTS/PRSP duplicate factors (reinvestigation §1) | **U** | Not run | — |

## 8. Updated recommendations (only where the measurements change them)

1. **NARS +4 → +3 compat GRF (change #1): feasible as designed.** It is now proven
   end-to-end in a disposable copy: catalogue, bill, and isolation from the Add-On, UKRS2,
   GETS and purchase prices. Before production use, still check:
   - adding a GRF to existing saves;
   - multiplayer MD5 distribution;
   - whether its GRFID needs registering.
2. **Norris target: about £1,260 rather than £1,575 for strict capacity parity.**
   - Measured Planet with 12 hoppers costs £952/yr for 708 t (£1.34/t running).
   - The same cost per tonne on Norris's 1,188 t gives £1,597 for the consist; minus
     £456 for the hoppers, that leaves about £1,140 billed for the engine.
   - Norris's measured billed/catalogue ratio over a year is about 0.91, because of the
     stationary discount. That puts the catalogue rate near £1,260 (DERIVED).
   - So £1,575 (−75%) is still inside a "parity to 2× parity" band. The band should be
     re-stated as **£1,260–£2,520**, not £1,200–£2,400, which used the overstated
     2.3× model ratio.
   - The +3 compat alone leaves Norris at £3,150, which is 2.5× parity.
3. **Stationary discounts matter more than assumed.**
   - UKRS2 and NARS bill full-load platform waits at ¼–⅓ of the engine rate; the Add-On
     and GETS bill 100%.
   - On supply-limited routes this widens the effective Add-On gap.
   - Compare sets on billed cost from duty runs, never on catalogue values.
4. **UKRS2 ageing is a step, not a slope.** Lifecycle models should use steps at the
   measured ages (Planet 12/24 years, Coppernob 9/21 years) rather than +£37/yr. The
   20-year Planet/Grasshopper billed ratio is 4.5×, not about 3.5×, which strengthens the
   case for a Grasshopper cut. −67% to −79% remains the right range.
5. **UKRS2's calendar surcharge needs no extra allowance for the campaign's 30-year economy
   offset.** It follows the calendar, so the calendar-date snapshots used in the
   forensics are already the in-game behaviour.
6. **American heavy-freight niche confirmed.** On a sustained 3% grade at the 7-tile
   limit, the UKRS2 8F is unusable. On the flat it has the best net of the four, because
   its running cost is ⅓–⅕ of theirs.
   - This supports keeping UKRS2 20th-century freight steam unchanged.
   - It also confirms the risk noted for change #1: halving NARS running would make the
     Mallet's flat net about £46k, close to the 8F's £50k (DERIVED from the compat
     factor 0.5 × £26,990).

## 9. Reproduction

From the repository root, on this PC (Python 3 standard library only):

```bash
python -B scripts/runtime_validation/rv.py verify
cd scripts/runtime_validation && python -B experiments.py --suite all --jobs 10 && python -B analyze.py
```

Runs already present (receipt in `docs/research/runtime_validation/runs/<tag>`) are skipped.
Superseded runs kept for transparency:

- `t2-age-*`: autorenew replaced the engine at 25.6 years;
- `t5-wallclock-1900`: no buildability logging;
- `t1-*-l128-*`: revenue includes subsidies; their tonnage and costs remain valid.
