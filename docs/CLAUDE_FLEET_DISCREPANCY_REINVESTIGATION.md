# Fleet running-cost discrepancy: independent reinvestigation

Independent review of the earlier Codex vehicle-economy work for Europe 1830
(JGRPP 0.73.4, 1830 scenario), November 2026. **Read-only:** no production GRF,
scenario, save or setting was modified, and no balance change was implemented.

Detailed reports:

- [NARS/UKRS2 running-cost forensics](NARS_UKRS2_RUNNING_COST_FORENSICS.md): the
  calculation path, factors, callbacks and worked arithmetic.
- [UKRS2 underpricing assessment](UKRS2_UNDERPRICING_ASSESSMENT.md): hypotheses A, B,
  C and D.
- [Independent recommendations](FLEET_BALANCE_INDEPENDENT_RECOMMENDATIONS.md):
  baseline, proposals, feasibility and next tests.

Scripts are in [`scripts/claude_forensics/`](../scripts/claude_forensics/) and outputs
in [`docs/research/claude_forensics/`](research/claude_forensics/).
`scripts/claude_forensics/run_all.sh` regenerates everything and runs **19 assertion
checks** against committed evidence.

## 0. Evidence situation (read first)

**The seven files named in the brief do not exist in this repository**, on any
branch or pull request (all 32 fetched remote branch and pull-request refs searched by filename and content):

- `FLEET_ECONOMY_AUDIT.md`
- `NARS_UKRS2_COST_COMPARISON.md`
- `FLEET_SIMULATION_RESULTS.md`
- `NARS_UKRS2_PROFITABILITY.md`
- `FLEET_BALANCE_CHANGESET_PROPOSAL.md`
- `fleet_vehicle_statistics.csv`
- `fleet_simulation_results.csv`

The quoted 32-tile, 12-hopper results (660 / 540 / 1,020 / 1,140 t, £8,083, and so on)
and the −75% / −50% proposals appear nowhere in committed text. They were presumably
produced in an unpushed local Codex session (the committed logs use
`C:\Users\Kladd\Documents\Codex\…` paths). I therefore treat them as **claims quoted in
the brief**, not as evidence.

What *is* committed, and was used as primary evidence, is the earlier four-phase Codex
audit (`docs/LOCOMOTIVE_PRICE_AUDIT.md`, `VEHICLE_ECONOMY_PHASE2.md`,
`TRANSPORT_ECONOMY_PHASE3.md`, `…PHASE4.md`) and its raw data:

- 17,322 engine snapshot rows and 22,832 Phase 2 rows;
- 994 built-train tests;
- 172 in-game route-year ledgers;
- JGRPP's own debug log of price multipliers.

I also read the JGRPP 0.73.4 source from the tagged release.

**Constraints on this investigation:**

- The GRF binaries could not be obtained. The content server (BaNaNaS) is blocked by
  this environment's network policy, so raw GRF bytes were not re-decoded. Per-vehicle
  factors are inferred exactly from runtime costs instead.
- No OpenTTD/JGRPP runtime was possible here (no GRFs), so **I ran no new game
  experiments**. Physics results are a labelled **model** re-implemented from JGRPP
  source.
- The committed economic baseline used **AXIS 2.3.1**, not Historical AXIS 0.6.0 as
  the brief states. Every profitability figure (Codex's and mine) needs re-checking on
  0.6.0.

## 1. Classification of prior conclusions

Labels: **V** = independently verified (re-derived from runtime data and/or source);
**S** = supported but not independently reproduced; **M** = potentially misleading;
**X** = incorrect; **U** = unverifiable with available evidence.

| Prior conclusion | Class | Basis |
| --- | --- | --- |
| Planet £525 / Grasshopper £3,150 / Coppernob £1,181 / Norris £6,300 catalogue | **V** | Reproduced exactly from `floor(4200 × factor × 2^exp / 256)` with logged exponents (`verify_claims.py`). The runtime numbers themselves are Codex measurements I could not re-run |
| Grasshopper/Planet 6×, Norris/Coppernob 5.33× | **V** | Arithmetic and decomposition checked: 6 = 6 × 1; 5.33 = 2.67 (factor) × 2 (exponent) |
| Grasshopper/Planet 11.43× per hp | **V arithmetic, M interpretation** | Per-hp magnifies small-engine gaps when costs have a fixed component; Grasshopper has only 63 hp |
| "NARS steam base exponent contributes 2×" | **V, but incomplete** | +4 vs +3 is confirmed from the engine log. It applies to *all* NARS 2.52 locomotives (diesel and electric also use the steam base), it does **not** apply to Grasshopper (the Add-On is +3), and it explains 2.0× of Norris/Coppernob's 5.33× |
| Phase 1 exponent table (UKRS2 diesel −3 / electric +5, NARS diesel −3) | **M** | Those exponents are set but unused by these sets' locomotives: every UKRS2 and NARS 2.52 engine reproduces exactly only on the steam base |
| Planet's API cost rises 11× by 2025 with inflation off (Phase 1) | **V**, mechanism added | A uniform additive calendar surcharge on all UKRS2 steam from about 1940; no other set varies |
| UKRS2 operating expense grows with age (Phase 3) | **V**, quantified | +£37/yr per year of age (£666 → £1,288 over 20 years, calendar 1830–49) |
| Grasshopper's lower capital fails to compensate on coal and timber (Phase 3) | **V** | Ledger: Planet +£1,607/yr against Grasshopper −£1,562/yr operating, years 1–5 |
| Engine-list cost ≠ annual bill; callbacks lower depot rates (Phase 2) | **V**, strengthened | Engine divisors are 1, so the reductions are GRF callbacks. The Add-On and GETS have none |
| 32-tile, 12-hopper results (Planet 660 t … Coppernob £15,189) | **U** | No data committed. Planet's 660 t/yr matches my model ceiling (658), which is consistent with an overloaded, speed-bound train. Norris and Coppernob figures sit below their model ceilings, which suggests supply or loading limits |
| "Coppernob outperformed Norris" | **S** (direction) | Expected from specifications: 2.26× TE, 1.25× hp, higher top speed, lower cost. Magnitude unverifiable |
| Proposed Norris −75%, Grasshopper −50% | **U** as to validation; magnitude evaluated in recommendations §3 | Never tested in modified GRFs. Norris's target is defensible by capacity parity with Planet, not Coppernob. Grasshopper's −50% is insufficient to remove the trap |
| Class 66 reversal (UKRS2 dearer catalogue, cheaper actual than GETS) | **S** (mechanism), **U** (numbers) | UKRS2 bills about ¼ in depot and 0.81 moving empty; GETS is flat 100%. A reversal is plausible with substantial stationary time. The supporting run is not committed |
| PTS/PRSP duplicate discrepancies (Phase 2) | **V** at factor level | Same exponents (+1), different factors (for example ST43 121 vs 93) |
| UKRS2 as the correct baseline (implicit in "reduce NARS to match") | **X** | UKRS2 is the high-cost outlier for 20th-century steam and diesel ([assessment](UKRS2_UNDERPRICING_ASSESSMENT.md)) |

## 2. Mechanisms (summary; details in forensics)

1. **Scale.** NARS 2.52 is +4 on the steam base for all locomotives; UKRS2 and the
   Add-On are +3. The Add-On's +3 already includes its default ½ running parameter.
2. **Curve shape.** NARS 2.52 factor ≈ 19.8 + 0.0159·hp (R² 0.99); Add-On ≈ 17.8 +
   0.0144·hp; UKRS2 ≈ proportional to hp. The gap is largest for small engines:
   5.33× at 200 hp, 1.0–1.2× at 2,000–2,500 hp, and the Add-On is cheaper than UKRS2
   in 8 of 9 matched pairs from 1895.
3. **Callbacks.** UKRS2 bills about ¼ in depot and about ¾ moving empty, more when
   loaded, plus an age surcharge and a calendar surcharge from about 1940. NARS 2.52
   bills about ¼ in depot and full while moving. The Add-On and GETS are flat. JGRPP's
   own stationary divisors are 1, so none of this is engine behaviour.
4. **Accrual.** Running cost accrues whenever a train is not stopped, including loading
   and full-load waits (`Train::Tick`). Whether NARS and UKRS2 discount platform waits
   is the main open question for actual billing.

## 3. Early steam: comparability

| | Planet | Grasshopper | Norris | Coppernob |
| --- | --- | --- | --- | --- |
| Set / intro | UKRS2 1830 | Add-On 1830 | NARS 1837–38 (randomized) | UKRS2 1844 |
| hp / kN / t / km-ish/h | 120 / 11 / 14 / 48 | 63 / 11 / 8 / 38 | 200 / 19 / 20 / 56 | 250 / 43 / 37 / 64 |
| Purchase / running | £7,031 / £525 | £4,687 / £3,150 | £11,718 / £6,300 | £12,890 / £1,181 |

- **Planet vs Grasshopper** are contemporaneous and a fair pair. Grasshopper is weaker
  in every performance metric and cheaper only to buy.
- **Norris vs Coppernob is not a fair pair.** They are six or seven years apart, and
  Coppernob is a second-generation engine that beats Norris on power, TE and speed.
  Norris's real competitor in its 1837/38–1844 window is **Planet**. Against Planet,
  Norris offers about 2.3× heavy-train capacity (model) for 12× the running cost.
- These pairs are the **extreme ends** of a gap that shrinks with size. Further pairs
  across decades are in [forensics §4](NARS_UKRS2_RUNNING_COST_FORENSICS.md): American
  1850 4.5×, Mogul 1869 2.9×, Ten-Wheeler 1885 1.7×, Mikado 1911 1.2×, Jubilee 1938
  1.0×.

## 4. The simulation, challenged

The committed data does not allow the run to be reproduced (§0), and no game runtime
was available. Using the JGRPP-derived physics model
(`research/claude_forensics/train_physics_model.txt`):

- **Overloaded consist.** With 12 loaded NARS hoppers (about 400 t), Planet and
  Grasshopper have about 1 kN of flat traction margin. Codex Phase 2 recorded the same:
  `flat_low_speed_force_margin` 1.05 / 1.2 kN. They crawl at 16–22 km-ish/h and top out
  near 650 t/yr. This test design measures their overload, not their economics.
- **Coppernob vs Norris.** The model gives a 22% shorter round trip for Coppernob
  (45.5 vs 58.1 running days) from higher TE (faster acceleration) and higher terminal
  speed loaded (47.6 vs 41.0). Together with its lower running cost, this explains the
  reported outcome without invoking callbacks or experimental artefacts. The reported
  tonnages (1,020 / 1,140 t) are well below the model ceilings (1,509 / 1,926 t),
  which points to supply or loading limits. Differences of less than one trainload a
  year (240 t) cannot be read as locomotive quality from one seed.
- **Gradients.** On a sustained 3% grade every 1830s–1840s engine stalls with 12 loaded
  hoppers. The most loaded hoppers each can lift is Coppernob 2, Norris 1, Planet and
  Grasshopper 0. **There is no early American gradient advantage.** One appears from
  about 1914: NARS Mallet 560 kN, Add-On Big Boy 600 kN and Yellowstone 649 kN, against
  the UKRS2 8F at 142 kN, which is 3–4× the trailing load on a sustained 3% grade
  (`heavy_freight_te.txt`).

## 5. Broader fleet

| Family | Same problem? |
| --- | --- |
| NARS 2.52 later steam (1850–1890s) | Yes, diminishing: 4.5× → 1.7× against matched UKRS2 |
| NARS 2.52 1900s+ steam | Roughly at parity with UKRS2 (1.0–1.3×), but 2× the other-set median |
| NARS 2.52 diesels and electrics | Yes, the set-wide 2× scale: 5.3–6.4 £/hp against an other-set median of about 2.5–2.8 for diesels |
| NARS Add-On | Only low-power early engines (Grasshopper, Judah, Duchess). From 1895 it is cheaper than UKRS2 in 8 of 9 matched pairs |
| UKRS2 express and freight steam | Not underpriced. Above the cross-set median from 1880, with calendar and age surcharges |
| UKRS2 diesels and Class 66 | The catalogue figure is misleading because of the state callback (about ¼ depot, 0.81 empty). Compare billed costs, not catalogue |
| Polish duplicates | A different mechanism (per-engine factors, same exponents). Codex Phase 2's targeted proposals stand |
| Multiple units | UKRS2 MUs share the steam base and surcharges. Polish MU premiums are purchase-side (Codex Phase 2) |

**Methodological problem in the prior audit:** the headline ratios compare catalogue
values across sets with fundamentally different callback behaviour, at a single date,
for the smallest engines, normalized per hp. Each of those four choices inflates the
apparent NARS/UKRS2 gap. Codex Phase 2 itself warned that engine-list costs are not
bills. The brief's headline numbers ignore that warning.

## 6. Final assessment

1. **Is NARS overpriced, or UKRS2 underpriced?** **NARS 2.52 is overpriced in running
   cost by about 2× set-wide** (exponent +4), measured against the cross-set median
   rather than UKRS2. On top of that, the NARS family's fixed-cost curve over-penalizes
   small early engines. **UKRS2 is not underpriced in general.** It is cheap only at
   1830s small-engine sizes, consistently with its own curve, and it is a high-cost set
   later on.
2. **What causes the 5–6×?** Grasshopper/Planet 6× is entirely the individual factor
   (24 vs 4), with equal exponents. Norris/Coppernob 5.33× is 2× from the exponent and
   2.67× from the factor. The factor gaps come from NARS's fixed component of about
   20 factor units.
3. **How much survives gameplay?** Planet/Grasshopper: 6.0× catalogue → **5.1× billed**
   in years 1–5 → about **3.5×** over Planet's 20-year life, because UKRS2's cost rises
   with age. Norris/Coppernob: callbacks imply about 4–5× while running (the quoted
   4.8× is consistent but unverified). The gap falls to about 1× for 1910s+ engines.
4. **Fair comparisons?** Planet/Grasshopper, yes. Norris/Coppernob, **no**: different
   generation, and Coppernob is superior. Norris should be compared with Planet.
5. **Compensating advantages?** Norris has earlier availability, about 2.3× Planet's
   heavy-train capacity, a cheaper purchase and lower weight. Grasshopper has only a
   lower purchase price and weight. NARS purchase prices are 0.6–0.96× UKRS2's
   throughout. American heavy freight has a real TE advantage from about 1914.
6. **Are −75% and −50% excessive?** Norris −75% (£1,575) falls inside my
   capacity-parity band (£1,200–£2,400), so it is not excessive, though Codex
   justified it with the wrong comparison. Grasshopper −50% is **insufficient** to
   remove the trap (break-even 2.2 years). A budget niche needs −67% to −79%. Both
   proposals miss the set-wide NARS scale.
7. **Other families?** NARS 2.52 early steam and all NARS 2.52 diesels and electrics
   (scale); low-power early Add-On engines. Not later Add-On engines, and not UKRS2.
   Class 66 is a measurement artefact of catalogue comparison.
8. **Most defensible baseline?** An independently derived duty baseline (cost per
   delivered unit on reference duties, in game, per era), checked against the per-era
   cross-set median weighted by profile. Not UKRS2.
9. **What to test next?** In order: rerun the missing 4-locomotive experiment with
   ≥4 seeds and right-sized consists; probe callback rates at platform, depot, loaded
   and ages 0–30; prove a running-only NARS exponent override via a compatibility GRF;
   run graded and 1914–45 heavy-freight tests; check whether UKRS2's surcharge follows
   calendar or economy time; repeat everything on Historical AXIS 0.6.0
   ([recommendations §6](FLEET_BALANCE_INDEPENDENT_RECOMMENDATIONS.md)).
10. **Codex: correct, misleading, unsupported?** *Correct:* the catalogue figures and
    ratios, the existence of the 2× exponent, the observations of time-dependence and
    age drift, the Grasshopper coal loss, the Polish duplicates, and the warning that
    catalogue ≠ bill. *Misleading:* the 11.43× per-hp headline, the unused UKRS2/NARS
    diesel and electric exponents in the Phase 1 table, Norris/Coppernob as the
    representative comparison, framing the 2× as steam-only, and implicitly using UKRS2
    as the baseline. *Unsupported or unverifiable:* the 32-tile simulation table, the
    Class 66 billed reversal figures, and the −75% / −50% targets (none committed, none
    tested).
