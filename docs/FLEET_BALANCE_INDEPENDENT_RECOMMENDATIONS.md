# Fleet balance: independent recommendations

Part of the [independent reinvestigation](CLAUDE_FLEET_DISCREPANCY_REINVESTIGATION.md).
**Nothing here has been implemented, and no targets have been validated in modified
GRFs.** These are proposals for the next round of experiments.

## 1. Balancing philosophy

1. **Compare complete trains on the same duty, at in-service dates.** Do not compare
   isolated catalogue values. UKRS2's cost varies with age, calendar date, load and
   state. NARS 2.52 varies only between depot and moving. The Add-On and GETS are
   flat. A purchase-window figure is exact only for the flat sets
   ([forensics §5–6](NARS_UKRS2_RUNNING_COST_FORENSICS.md)).
2. **Normalize by haulage capability, not by horsepower.** £/hp exaggerates the cost of
   small engines in any set with a fixed per-locomotive component: Grasshopper's
   "11.43× per hp" mostly reflects that it has only 63 hp. A better unit is cost per
   unit of deliverable capacity on a defined duty (t/yr on the route at the 7-tile
   limit), measured under both supply-limited and supply-saturated conditions.
3. **Lifecycle, not year 1.** Use a 15–20-year horizon including purchase, the observed
   age drift (UKRS2 +£37/yr per year for Planet), calendar surcharges and replacement.
4. **Tolerate specialization; remove traps.** An engine may be worse on one duty if it
   has a real niche: earlier availability, TE on grades, speed, capacity or cheap
   capital. It should not be worse on *every* dimension at a higher lifecycle cost
   while it is contemporaneous with its rival. Obsolescence after a successor appears
   (Norris after Coppernob in 1844) is acceptable and historical.
5. **Players are not region-locked.** In OpenTTD any company can buy any set's engines
   anywhere on the map. "National fleets" only stay distinct if no set is cheapest for
   everything. That makes cross-set balance necessary, not optional.

## 2. Which baseline?

| Option | Assessment |
| --- | --- |
| UKRS2 as reference | **Reject.** UKRS2 is internally consistent but time-varying, and it is the *high-cost* outlier for 20th-century steam and diesel (steam 1914–45: £5.44/hp against an other-set median of £2.22). Anchoring to it would mark GETS, the Polish sets and the Add-On as "too cheap" and push the whole campaign's costs up. Anchoring to its 1830 values would understate its own lifecycle cost |
| Cross-set median | **Use as a check, per era and traction**, counting each economic profile once (GETS's 945 engines are mostly liveries and must not dominate). It works well from 1880, when four or more sets exist. Before 1880 only UKRS2 and the two NARS GRFs exist, so a median of two curves is not meaningful |
| Independently derived duty baseline | **Recommended primary baseline.** Define 3–4 reference duties per era (light mixed, heavy freight, express passenger). Measure delivered units per year and lifecycle cost per delivered unit in JGRPP on the real AXIS economy. Accept a set's engine if it lies within a band (for example 0.5–2× the duty-best contemporary) unless it has a documented niche |

## 3. Evaluating Codex's proposed changes

**Norris £6,300 → £1,575 (−75%).** I did not find these proposals in any committed
report. They are evaluated as quoted in the brief.

- The stated rationale, alignment with Coppernob, is the wrong comparison. Coppernob
  arrives six or seven years later and beats Norris in every performance dimension
  (250 vs 200 hp, 43 vs 19 kN, 64 vs 56 km-ish/h). Norris *should* become obsolete
  after 1844.
- The right comparison is Norris against **Planet**, in the 1837/38–1844 window. Under
  the [physics model](research/claude_forensics/train_physics_model.txt),
  Norris's maximum flat-route throughput with 12 loaded NARS hoppers is about
  **2.3× Planet's** (1,509 against 658 t/yr). Matching running cost per unit of
  capacity would put Norris at about £1,200/yr. Allowing up to 2× that for earlier
  heavy-train capability gives a **defensible test band of £1,200–£2,400**.
- **So the −75% target sits inside the band I derive, but for a different reason than
  Codex gave.** It is not excessive in magnitude. On a supply-limited route (typical in
  1838, see §4) even £1,575 makes Norris 3× Planet's cost for the same tonnage, so it is
  not generous either.

**Grasshopper £3,150 → £1,575 (−50%).**

- Grasshopper is contemporary with Planet (both 1830). It has lower capital (−£2,344)
  and lower weight, but less power (63 vs 120 hp) and less speed (38 vs 48). In game it
  delivered 0.79× Planet's tonnage on the same route (RUNTIME, Phase 3).
- At £1,575 Grasshopper still costs £1,050/yr more than Planet. Its capital saving is
  recovered in **2.2 years**, so it remains a trap. A budget-starter niche (break-even
  of about 8–10 years) needs about **£650–£1,050 (factor 5–8 at +3), i.e. −67% to
  −79%**.
- **The −50% target is therefore insufficient rather than excessive**, if the goal is a
  viable choice. Leaving Grasshopper as a documented historical curiosity is an
  acceptable alternative.

**What both proposals miss.** They are per-locomotive patches on top of a set-wide
issue. NARS 2.52's +4 exponent doubles the running cost of all 71 NARS 2.52 entries,
diesel and electric included. Fixing Norris alone leaves the NARS 1850 American (4.5×
its UKRS2 match), the 1869 Mogul (2.9×), the 1875 Consolidation (3.1×) and every NARS
diesel (5.3–6.4 £/hp against an other-set median of about 2.5–2.8) untouched.

## 4. Recommended candidate changes (to test, not adopt)

| # | Change | Scope | Expected effect | Risk to watch |
| --- | --- | --- | --- | --- |
| 1 | **NARS 2.52 running exponent +4 → +3, running only** (purchase unchanged) | All 71 NARS 2.52 locomotives | Brings NARS to about the other-set median in 10 of 12 era cells; Norris £6,300 → £3,150 | 1914–45 NARS heavy steam becomes about ½ of UKRS2 per hp *and* has 3–4× the TE, so UKRS2 20th-century freight steam may lose all cost competitiveness. Measure before adding any UKRS2 change |
| 2 | Norris factor 24 → 9–18 (at +3 after #1, giving £1,181–£2,362) | One engine | Puts Norris in the capacity-parity band against Planet in 1838–44 | Must not undercut Coppernob after 1844 on lifecycle cost |
| 3 | Grasshopper factor 24 → 5–8 (giving £656–£1,050) | One Add-On engine | Turns a trap into a budget starter | Do **not** change the Add-On's set-wide running parameter: from 1895 its engines are already 0.44–0.87× UKRS2 in 8 of 9 matched pairs |
| 4 | Review other low-power early NARS-family engines: NARS American 4-4-0 (1850, £3,806 after #1), Add-On C.P. T.D. Judah (1863, 126 hp, £3,937 = £31/hp), Duchess (1883, 350 hp, 3× its UKRS2 match) | Few engines | Removes residual fixed-cost traps | Only where a contemporaneous competitor dominates them |
| 5 | **No change** to UKRS2 in the first experiment | — | Keeps the reference stable while #1–3 are measured | UKRS2's age and calendar surcharges are deliberate obsolescence. Revisit only if UKRS2 steam stops being competitive at all after #1 |
| 6 | Polish duplicates (ST43, ET21, EN57, EN71, ED72) | Per-engine | Keep Codex Phase 2's targeted proposals: same exponents (+1), different factors, so a per-engine mechanism as Codex concluded (I confirmed the factors: ST43 121 vs 93, ET21 70 vs 75, EN57/EN71/ED72 equal running, unequal purchase) | Independent of the NARS/UKRS2 problem |

## 5. Implementation feasibility (SOURCE-checked)

| Route | Can it do #1? | Can it do #2–4? | Notes |
| --- | --- | --- | --- |
| **Existing parameters** | Partly. NARS 2.52 "Reduce vehicle costs" halves running **and purchase** | No | Halving purchase too would make NARS the cheapest capital outside GETS (NARS purchase is already 0.6–0.96× UKRS2). The Add-On's running parameter ½ → ¼ overshoots for all its later engines. UKRS2 has no cost parameter |
| **Compatibility GRF, base-cost override** | **Plausible, untested.** In `src/newgrf.cpp` `FinalisePriceBaseMultipliers()`, a GRF that declares the global "GRF match for engine allocation" override (Action 0 feature 08 prop 0x11, source→`44440302`) and **is loaded after** NARS has its explicitly set price-base multipliers copied onto NARS. Setting price 42 (steam running) to byte 11 (+3) halves running only | Probably not for NARS | One override target per source GRFID, so the Add-On would need its own compat GRF. `GetCurrentGRFOverride()` also copies translation tables to the target, so the compat GRF must define **no** cargo/railtype tables or it may alter NARS refits. Proof needed: JGRPP debug line `overrides price base multiplier 42`, NARS purchase unchanged, Add-On unaffected |
| Compatibility GRF, per-engine Action 0 prop 0x0D | n/a | **Unreliable for NARS and UKRS2.** Their rates are state-dependent, which means callback 0x36 supplies the factor. `GetVehicleProperty` prefers the callback result, so a static override is ignored. It may work for the Add-On, whose rates are flat (no evidence of a running-cost callback) | Replacing another GRF's Action 3 to take over its callbacks would also replace its graphics chain. Not recommended |
| **Source fork of the GRF** | Yes | Yes (most precise) | Requires the original source and a licence that permits modification and redistribution to all players. **The repository records no licence for UKRS2, NARS 2.52 or the NARS Add-On**, so this must be checked first. A fork also needs a version bump and identical files on every client |
| **JGRPP engine patch** | Not justified | Not justified | No engine defect was found: the cost path behaves as coded. JGRPP's `vehicle_costs_in_depot` / `vehicle_costs_when_stopped` settings exist (currently 1) but act on every set equally and do not fix cross-set gaps |

**Save and multiplayer compatibility.** Running costs are not stored per vehicle.
`GetRunningCost()` is recomputed every day, so any of these routes changes costs for
existing trains immediately on load. Price-base multipliers are recomputed from the GRF
list at load. The risks are therefore:

- adding a GRF to an *existing* save (normally blocked outside developer settings;
  test on a copy);
- every client needing byte-identical GRF files and parameters (the server enforces
  this by MD5);
- a forked GRF that keeps its GRFID but changes MD5 loads as a "compatible" substitute
  with a warning, so version it deliberately.

None of these changes rolling-stock identities, dates or physics.

## 6. Tests to run next, in order

1. **Recover or rerun the missing Codex experiment.** The `FLEET_*` and `NARS_UKRS2_*`
   reports and CSVs are not in the repository. Rerun the 32-tile, 12-hopper comparison
   of Planet, Grasshopper, Norris and Coppernob with **at least four seeds**, and record
   per-year ledgers, delivered tonnes, monthly speed and load, and station rating.
   Include supply-saturated and supply-limited variants. The model predicts Planet and
   Grasshopper are capacity-bound near 650 t/yr with 12 loaded hoppers, which is badly
   overloaded at 1 kN of flat traction margin. Use 4–6 hoppers for them.
2. **Callback state probe.** Sample `GSVehicle.GetRunningCost` for NARS, UKRS2 and
   Add-On consists while moving loaded, moving empty, waiting at a platform for full
   load, in depot, and at ages 0/10/20/30. This settles the biggest unknown for actual
   billing.
3. **Compat-GRF proof for change #1.** Build a minimal NFO/NML GRF with prop 0x11 and
   prop 0x08 (price 42 = 11). Load it after NARS in a disposable copy and confirm the
   debug log line, Norris £3,150, unchanged NARS purchase and an unchanged Add-On.
4. **Graded test.** Sustained 3% climbs with 1, 2 and 4 loaded hoppers. The model says
   Coppernob lifts 2 and Norris 1, and every early engine stalls with 12. Also run
   1914–45 heavy freight (NARS Mallet / Add-On Big Boy against UKRS2 8F at the 7-tile
   limit). This is where American specialization should appear.
5. **Economy-time check.** Confirm whether UKRS2's calendar surcharge follows the
   calendar date or the economy date (30 years behind) in the real scenario.
6. **Repeat on Historical AXIS 0.6.0.** All prior economic runs used AXIS **2.3.1**.
   Revenue levels, and therefore every profitability conclusion, must be re-checked on
   the economy the campaign will actually use.
