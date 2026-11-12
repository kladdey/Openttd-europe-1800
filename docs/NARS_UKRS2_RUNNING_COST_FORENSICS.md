# NARS / UKRS2 running-cost forensics

Independent reinvestigation, November 2026. Companion to
[CLAUDE_FLEET_DISCREPANCY_REINVESTIGATION.md](CLAUDE_FLEET_DISCREPANCY_REINVESTIGATION.md).
Nothing in the game installation, GRFs, scenario or settings was changed.

**Main finding:** the early 5–6× catalogue gap has three separate causes, and the
prior audit only identified one of them:

1. **A 2× set-wide scale.** NARS 2.52 sets its running-cost base exponent to +4. UKRS2
   and the NARS Add-On use +3. Both NARS 2.52 and UKRS2 price **every** locomotive
   (steam, diesel and electric) on the *steam* running base. So this 2× applies to the
   whole NARS 2.52 fleet, not only to steam.
2. **A differently shaped cost curve.** NARS 2.52 and the Add-On give every locomotive a
   large fixed factor of about 18–20 units, plus a small amount per horsepower. UKRS2
   prices close to proportionally to horsepower. Small early engines are therefore
   expensive in NARS and cheap in UKRS2. The gap closes as power rises.
3. **Different callback behaviour.** The catalogue figure shows none of this. UKRS2
   lowers running cost when a train is empty or in a depot, raises it as the vehicle
   ages, and from about 1940 adds a surcharge that grows with the calendar year. NARS
   2.52 reduces cost only in a depot. The Add-On and GETS charge a flat rate whatever
   the train is doing.

Evidence classes used below: **SOURCE** (JGRPP 0.73.4 code, fetched from the tagged
release), **ENGINE LOG** (JGRPP's own debug output, committed by the prior audit),
**RUNTIME** (committed GameScript API measurements and in-game ledgers), **DERIVED**
(my arithmetic on those), **MODEL** (my re-implementation of engine physics),
**UNVERIFIED** (cannot be checked with the available evidence).

The GRF binaries were *not* available to me: the content server (BaNaNaS) was
blocked by this environment's network policy. Raw Action 0 / callback bytes were
therefore not re-decoded. Every per-vehicle factor below is **inferred from exact
runtime costs** using the source formula. Each inference is exact, never approximate:
see "Factor inference" below.

## 1. Calculation path, GRF to ledger (SOURCE)

| Step | Location in JGRPP 0.73.4 | Effect |
| --- | --- | --- |
| Base price | `src/table/pricebase.h`: `RunningTrainSteam` 5600, `Diesel` 5200, `Electric` 4800, category *Running* | Start values |
| Difficulty | `src/economy.cpp` `RecomputePrices()`: `vehicle_costs` 0 → ×6, then `>> 3` | Low running cost = 6/8 → steam £4,200 |
| Inflation | same function, `× inflation_prices` (65536 = 1.0 in campaign) | None |
| Global GRF multiplier | `_price_base_multiplier[i]`, set only if a GRF sets a base price for a feature it has no vehicles of | None observed in this GRF list |
| Per-GRF local exponent | `src/newgrf/newgrf_act0_globalvar.cpp` Action 0 feature 08 prop 0x08: `factor - 8`; resolved in `src/newgrf.cpp` `FinalisePriceBaseMultipliers()` | Power-of-two per set and price class |
| Running-cost class and factor | `Engine::GetRunningCost()` (`src/engine.cpp`): class from `running_cost_class` (Action 0 prop 0x0E), factor via `GetEngineProperty(PROP_TRAIN_RUNNING_COST_FACTOR)` (prop 0x0D, may be replaced by callback 0x36) | Catalogue value = `GetPrice(class, factor, grf, -8)` |
| Catalogue display | `Engine::GetDisplayRunningCost()`: ×`DayLengthFactor()` only if `show_running_costs_calendar_year` | Day length 1 → no effect |
| Actual consist rate | `Train::GetRunningCost()` (`src/train_cmd.cpp:7023`): sums every part using **`GetVehicleProperty(v, …)`**, i.e. callback 0x36 *with the real vehicle's state*. Multiheaded parts are halved. If `cur_speed == 0`, the total is divided by `vehicle_costs_in_depot` / `vehicle_costs_when_stopped` | Campaign stores both divisors = **1** (RUNTIME, `transport_economic_settings.json`), so JGRPP applies **no** stationary discount. Every depot/stationary reduction observed below comes from a GRF callback |
| Accrual | `Train::Tick()`: `running_ticks++` unless stopped/waiting in depot and speed 0 | Loading, waiting for full load and signal stops **all accrue** |
| Charge | `Train::OnNewEconomyDay` path: `GetRunningCost() * running_ticks / (365 × 74)`, booked as `ExpensesType::TrainRun` | Each day is charged at the rate in force *at that moment*, × that day's ticks |

So the purchase-window figure is the engine-list callback context (no vehicle). The
bill is the per-vehicle callback context, sampled once a day. **The two coincide
only for sets that do not use a state-dependent callback.**

## 2. Resolved exponents and base classes

**Exponents (ENGINE LOG).** `docs/research/vehicle_runtime_mapping.log` contains
JGRPP's own `[grf:3] … sets local price base multiplier` lines. Index 42 =
`RunningTrainSteam`, 43 = Diesel, 44 = Electric, 15 = train purchase, 16 = wagon
purchase (indices verified against `pricebase.h` ordering):

| Set | 42 steam | 43 diesel | 44 electric | 15 train buy | Parameters in campaign |
| --- | --- | --- | --- | --- | --- |
| UKRS2 1.05 | +3 | −3 | +5 | 0 | `0,0,0,0,0,3,2` (no cost slider exists) |
| NARS 2.52 | **+4** | −3 | — | −1 | `0` = "Reduce vehicle costs" **off** (halves purchase *and* running when on) |
| NARS Add-On 2cc | +3 | +2 | +1 | +1 | `4,3,2`: purchase ×1 (default); running **×1/2** (the add-on author's own default, value 3) |
| GETS 0.7 | −3 | −5 | — | −2 | `3,2` |
| PTS 3.0.3 / PRSP 0.19.11 | +1 | +1 | +1 | 0 | defaults |

The add-on's running parameter is index 3 = "1/2", its declared default
(`vehicle_grf_parameters.json`). Its +3 is therefore *after* a ½ setting. It is a
plausible inference, but UNVERIFIED without the binary, that "1 (default)" would
resolve to +4, the same scale as NARS 2.52.

**Base classes (DERIVED, new).** `scripts/claude_forensics/infer_cost_factors.py`
tests each base class against every observed catalogue cost. For each class it uses
that set's logged exponent and looks for an integer factor 1–255 that reproduces the
cost **exactly**. Results for the 1830 snapshot:

| Set (traction label) | Base class that reproduces the costs exactly |
| --- | --- |
| UKRS2 steam / diesel / electric (24 / 18 / 12 entries) | **steam, all 54** |
| NARS 2.52 steam / diesel / electric (21 / 35 / 15) | **steam, all 71** |
| NARS Add-On | steam for steam; mostly diesel/electric for the others |
| PTS / PRSP | steam / diesel / electric as labelled |
| GETS | mostly not reproducible with factor ≤255 at its negative exponents (coarse step size or larger callback values). GETS factors are not used below |

Example: UKRS2 EMD Class 66, catalogue £8,137 at calendar base → `8137 × 256 /
(4200 × 2³) = 62.0` on the steam base. On the diesel base with −3 it is not an integer.
**Consequence:** the prior audit's exponent table listed UKRS2 diesel −3 / electric
+5 and NARS diesel −3. Those exponents exist, but the locomotives do not use them. A
comparison by "diesel exponent" would be meaningless for these two sets. The 2× NARS
scale reaches every NARS 2.52 diesel and electric.

## 3. Worked calculations (DERIVED; reproduced by `verify_claims.py`)

`cost = floor(4200 × factor × 2^exp / 256)`

| Engine | Set | Factor | Exp | Calculation | Catalogue (RUNTIME) |
| --- | --- | --- | --- | --- | --- |
| Planet 2-2-0 (1830) | UKRS2 | 4 | +3 | 4200×4×8/256 | £525 ✔ |
| Grasshopper 0-4-0 (1830) | Add-On | 24 | +3 | 4200×24×8/256 | £3,150 ✔ |
| Coppernob 0-4-0 (1844) | UKRS2 | 9 | +3 | 4200×9×8/256 = 1181.25 | £1,181 ✔ |
| Norris 4-2-0 (1837/38) | NARS 2.52 | 24 | +4 | 4200×24×16/256 | £6,300 ✔ |
| Crampton 4-2-0 (1847) | UKRS2 | 13 | +3 | 4200×13×8/256 = 1706.25 | £1,706 ✔ |

Decomposition:

- **Grasshopper / Planet = 6.00** = factor ratio 24/4 × exponent ratio 2⁰. *None* of
  this gap comes from the base exponent.
- **Norris / Coppernob = 5.33** = factor ratio 24/9 (2.67) × exponent ratio 2¹ (2).
  The exponent explains **2.0× of 5.33×**: in log terms, 41% of the gap. The
  individual factor explains the remaining 2.67×.

The Phase 1 audit's raw decode of Grasshopper (factor 24, base `0x4C30` steam, at byte
offset 24148) matches my inferred factor 24. That decode is consistent with this
analysis but I could not reproduce it myself (no binary).

## 4. Why the factors differ: cost-curve shape (DERIVED)

These are least-squares fits of factor = a + b·hp over steam locomotives introduced
by 1950. They use the 1913 snapshot, before any UKRS2 calendar surcharge
(`docs/research/claude_forensics/cost_curve_analysis.txt`):

| Set | n | Fixed factor a | Factor per 1000 hp | R² | Exp | Fixed £/yr | £/yr per hp |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UKRS2 | 22 | −7.7 | 48.3 | 0.92 | +3 | ≈0 | 6.34 |
| NARS 2.52 | 21 | **19.8** | 15.9 | 0.99 | +4 | **£5,193** | 4.17 |
| NARS Add-On | 30 | **17.8** | 14.4 | 0.96 | +3 | **£2,334** | 1.90 |
| PTS | 15 | 19.9 | 50.1 | 0.98 | +1 | £652 | 1.64 |
| PRSP | 19 | 16.6 | 54.7 | 0.94 | +1 | £546 | 1.79 |

The NARS family charges a large fixed cost per locomotive and little per horsepower.
UKRS2 charges almost purely per horsepower. With the curves overlaid, the gap is huge
at 63–250 hp and disappears near 3,000 hp. The following predictions come from the
fits (MODEL, at UKRS2's pre-1913 calendar base):

| hp | UKRS2 | NARS 2.52 | NARS Add-On |
| --- | --- | --- | --- |
| 120 | £131 | £5,694 | £2,561 |
| 250 | £579 | £6,236 | £2,808 |
| 800 | £4,067 | £8,530 | £3,850 |
| 2,000 | £11,678 | £13,535 | £6,126 |
| 3,000 | £18,021 | £17,705 | £8,021 |

Size- and era-matched pairs, each with the nearest UKRS2 engine within ±35% hp and
±20 years (`steam_matched_pairs.csv`):

| NARS 2.52 engine (intro, hp) | UKRS2 match | Running ratio | = factor × exponent | Purchase ratio |
| --- | --- | --- | --- | --- |
| Norris (1837, 200) | Coppernob (1844, 250) | **5.33** | 2.67 × 2 | 0.91 |
| American 4-4-0 (1850, 450) | Long Boiler (1855, 375) | 4.46 | 2.23 × 2 | 0.96 |
| Mogul (1869, 650) | Goods 0-6-0 (1873, 600) | 2.90 | 1.45 × 2 | 0.67 |
| Consolidation (1875, 800) | Goods 0-6-0 | 3.10 | 1.55 × 2 | 0.71 |
| Ten-Wheeler (1885, 900) | Edwardian (1904, 1000) | 1.67 | 0.83 × 2 | 0.63 |
| Mikado (1911, 2000) | Pacific (1922, 1750) | **1.20** | 0.60 × 2 | 0.72 |
| Hudson (1933, 2500) | Streak (1937, 2000) | 1.09 | 0.54 × 2 | 0.79 |
| Jubilee 4-4-4 (1938, 2100) | Streak | 1.00 | 0.50 × 2 | 0.63 |

For NARS Add-On engines matched the same way, the ratio is 1.2–3.0 before about 1890.
From 1895 it is **0.44–0.87** in 8 of 9 pairs, meaning the add-on is *cheaper* than UKRS2 (the exception is Light Pacific 1908, 1.18×). In every
pair, NARS **purchase** prices are 0.6–0.96× UKRS2's.

The Norris/Coppernob and Grasshopper/Planet pairs are therefore the **most extreme
points** of a gap that shrinks steadily with engine size. They are not representative
of the whole fleet.

## 5. State-dependent rates (RUNTIME, reinterpreted)

The rates below come from `representative_train_tests.csv`, where GameScript
`GSVehicle.GetRunningCost` was called on real built consists. "Catalogue sum" is
engine plus wagons.

| Set / example (year) | In depot | Moving, empty | Catalogue sum | Behaviour |
| --- | --- | --- | --- | --- |
| UKRS2 Planet + 4 open wagons (1849) | £161 | £424 | £553 | depot ≈ ¼, moving-empty ≈ 0.77 |
| UKRS2 Class 66 solo (2025) | £2,887 | £9,450 | £11,681 | depot ≈ ¼, moving-empty ≈ 0.81 |
| NARS 2.52 Norris + 4 open wagons (1849) | £1,605 | £6,330 | £6,328 | depot ≈ ¼, moving = full |
| Add-On Grasshopper + 4 open wagons (1849) | £3,180 | £3,180 | £3,178 | flat |
| GETS BR 266 solo (2025) | £6,870 | £6,870 | £6,870 | flat |
| PTS / PRSP (110 cases) | median 0.37 | median 1.00 | — | depot reduced, moving full |

Across all built cases (medians, depot/catalogue and moving/catalogue): UKRS2 0.41 and
0.77; NARS 2.52 0.28 and 1.00; Add-On 1.00 and 1.00; GETS 1.00 and 1.00.

Because the JGRPP divisors are 1, these reductions are **GRF callback behaviour**:
callback 0x36 on property 0x0D, the only state-aware route to a running cost. It is
not engine behaviour. UNVERIFIED: whether the NARS and UKRS2 "stationary" branch fires
only in depots or whenever speed is 0, for example while waiting for a full load. No
committed measurement captures a train standing at a platform. This matters a great
deal. A UKRS2 train waiting for full load would be billed about ¼ while it waits; an
Add-On or GETS train would be billed 100%.

## 6. UKRS2 time effects (RUNTIME + DERIVED, new)

**Calendar surcharge.** Across the 1830–2025 snapshots, *only* UKRS2 locomotive
running costs change: 42 of 54 engines vary. No NARS, Add-On, GETS, PTS or PRSP engine
changes at all. For UKRS2 steam, the change is the **same additive factor step for
every engine, whatever its design year**. It is zero up to 1913, then +2 by 1945,
+5 (1950), +15 (1970), +25 (1990), +30 (2000) and +40 (2025): roughly +0.5 factor per
year from about 1941. Planet, Coppernob and Crampton all gain exactly +£656 by 1950,
+£3,937 by 2000 and +£5,250 by 2025. Because the step does not depend on design age,
it is a function of the calendar date. UKRS2 diesels get a later, non-uniform increase
from somewhere between 1970 and 1990. Its mechanism is unresolved. UKRS2 electrics are
flat.

UNVERIFIED: whether UKRS2 reads calendar or economy time in this campaign, where the
economy date runs 10,957 days (30 years) behind the calendar
(`TRANSPORT_ECONOMY_PHASE3.md`). In upstream-derived JGRPP, NewGRF date variables
normally see calendar time, but this was not tested here.

**Vehicle-age effect.** The Phase 3 ledgers (`transport_route_results.csv`, tag
`rail-coal-ledger`) record the same Planet + 4 open wagons on the same 26-tile coal
route for 20 years, calendar 1830–1849, when the snapshots show no calendar surcharge.
Billed running cost rose from **£666 in year 1 to £1,288 in year 20** (OLS +£37/yr per
year of age; 20-year mean £934). A second Planet route (`rail-lodi`) rose from £712 to
£1,032 over 10 years. Reliability stayed at 91–96% throughout, so breakdowns are not
the driver. The Grasshopper bill stayed flat at £3,180–3,320. The most likely cause is
a UKRS2 callback reading vehicle age. That inference is strongly supported but
UNVERIFIED at the byte level.

Year-1 Planet billing (£666) is also *above* the £553 catalogue sum, even though
moving-empty is only 77% of catalogue. So the UKRS2 loaded-moving rate exceeds the
catalogue figure. This suggests a load- or effort-dependent branch (UNVERIFIED).

## 7. How much survives actual gameplay

**Planet vs Grasshopper** (RUNTIME, same route, consist and calendar years;
`ledger_analysis.txt`):

| Measure | Ratio |
| --- | --- |
| Engine catalogue | 6.00× |
| Consist catalogue (+4 open wagons) | 5.75× |
| **Billed, years 1–5** | **5.12×** (£3,251 vs £635) |
| Billed vs Planet's 20-year mean (Grasshopper flat, as observed) | **3.48×** |

Operating result over years 1–5, as revenue minus running minus £132 property:
Planet **+£1,607/yr**, Grasshopper **−£1,562/yr**. Planet also delivered more: 206 vs
163 units/yr, from its higher speed.

**Norris vs Coppernob.** No committed in-game route exists for this pair. Callback
rates (§5) mean Norris pays full rate whenever it moves. Coppernob pays about ¾ when
empty and less in depots, so the billed gap should stay close to or above the 4.1×
consist-catalogue ratio while trains run. The brief quotes Codex's unpublished figures
of £5,979 vs £1,245, which is 4.8×. That value is consistent with these rates but
UNVERIFIED.

**Later engines.** The catalogue gap falls to about 1.0–1.3× for NARS steam from
1910 on. By 1970 it reverses once UKRS2's calendar surcharge is included: Streak
£16,668 vs NARS Jubilee £14,700.

## 8. The other investigated factors

| Factor | Finding |
| --- | --- |
| Base classes / multipliers | §1–2. The only cross-set exponent difference that matters between NARS 2.52 and UKRS2 is +4 vs +3 on steam, and it applies to all their locomotives |
| Individual factors | §3–4. The NARS family uses a fixed-heavy curve; UKRS2 prices in proportion to power |
| Callbacks | §5–6. They reduce cost when stationary (UKRS2, NARS, PTS, PRSP), reduce it when moving empty (UKRS2) and add age and calendar surcharges (UKRS2). The Add-On and GETS are flat |
| Calendar vs economy time | Accrual is tick-based (`running_ticks / (365×74)`) and independent of the date. Only UKRS2's surcharge depends on a date |
| Day length | 1 in the campaign; affects only the display path (`DayLengthFactor`) |
| Age / reliability | UKRS2 cost rises with age (§6). Reliability did not track cost. With breakdowns on reduced and improved breakdowns off, breakdowns cost time, not running cost |
| Loaded vs empty | UKRS2 is cheaper empty and dearer loaded. The NARS, Add-On and GETS moving rate does not change with load as far as measured |
| Stationary vs moving | No engine-level discount (divisors 1). Only GRF callbacks reduce it |
| Power and consist | Each part pays its own rate; multiheaded parts are halved. Wagon rates are small next to engine rates: UKRS2 open wagon £7, NARS hopper £38 per year |
| Global difficulty | Low running cost (6/8) applies to every set equally and cannot create cross-set gaps |
| Parameters and load order | NARS 2.52 has a coupled ½ purchase+running switch (off). The Add-On running is at its ½ default. Exponents are per-GRF local. Load order matters only for GRFs that declare an engine-allocation override (§9 of the recommendations) |
| JGRPP-specific | The `vehicle_costs_in_depot` / `vehicle_costs_when_stopped` divisors exist but are 1 here. The calendar/economy split shifts economy dates (30 years) but not accrual |

## Reproduction

```bash
scripts/claude_forensics/run_all.sh     # regenerates docs/research/claude_forensics/, then 19 assertion checks
```

Inputs are only committed files: `vehicle_economy_snapshots.csv`,
`vehicle_economy_normalized.csv`, `representative_train_tests.csv`,
`transport_route_results.csv`, `vehicle_runtime_mapping.log` and
`transport_economic_settings.json`. The JGRPP source used is the `jgrpp-0.73.4` tag:
`src/engine.cpp`, `economy.cpp`, `train_cmd.cpp`, `ground_vehicle.cpp`, `train.h`,
`newgrf.cpp`, `newgrf/newgrf_act0_globalvar.cpp`, `table/pricebase.h` and
`script/api/script_{engine,vehicle}.cpp`.
