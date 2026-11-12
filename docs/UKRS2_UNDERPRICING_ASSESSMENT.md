# Is UKRS2 underpriced? Hypothesis assessment

Part of the [independent reinvestigation](CLAUDE_FLEET_DISCREPANCY_REINVESTIGATION.md);
mechanisms are in [running-cost forensics](NARS_UKRS2_RUNNING_COST_FORENSICS.md).

**Verdict:** UKRS2 is **not generally underpriced**. Its early steam is cheap only
relative to the NARS family. That cheapness comes from UKRS2 pricing roughly in
proportion to horsepower, not from a scale error. From 1880 onward UKRS2 is one of
the **two most expensive** sets to run per horsepower, with the highest purchase
prices. Its effective cost also rises with vehicle age and, from about 1940, with the
calendar year. The evidence best supports a combination:

- **A**, for NARS 2.52's *set-wide* running scale (2× too high against the
  cross-set median);
- **C/D**, for the *early small-engine* gap: incompatible curve shapes, not a defect
  in either set;
- a **rejection of B**, except in the narrow sense that UKRS2's 1830s engines are the
  cheapest early option.

## The three hypotheses tested

### B: "UKRS2 operating costs are excessively low"

**Against other sets, era by era.** The table below gives median **in-service**
running £/hp. Each engine is evaluated at the first Phase 2 snapshot year within 25
years of its introduction, so UKRS2's surcharges are included
(`docs/research/claude_forensics/fleet_era_comparison.txt`):

| Traction, era | UKRS2 | NARS 2.52 | Add-On | GETS | PTS | PRSP |
| --- | --- | --- | --- | --- | --- | --- |
| Steam 1830–79 | **4.57** | 11.71 | 7.58 | – | – | – |
| Steam 1880–1913 | 4.29 | 7.62 | 3.83 | 2.92 | – | – |
| Steam 1914–45 | **5.44** | 5.78 | 2.22 | 2.64 | 2.01 | 2.04 |
| Diesel 1946–70 | 3.65 | 6.43 | 3.10 | 2.52 | 2.46 | 2.46 |
| Diesel 1971–90 | 4.41 | 5.34 | 2.76 | 2.87 | 2.09 | 2.03 |
| Electric 1946–70 | 3.04 | 5.80 | 2.68 | 1.78 | 0.83 | 0.85 |
| Electric 1991–2025 | 3.38 | 2.53 | 2.40 | 1.30 | 0.86 | 0.77 |

Purchase £/hp follows the same pattern. UKRS2 is the highest or second highest in
almost every cell: for example, steam 1914–45 costs £24.9/hp against NARS £14.8, the
Add-On £15.8 and GETS £6.5. UKRS2 sits **at or above the median** after 1880. Only in
1830–1879 does it look cheap, and in those years its only competitors are the two NARS
GRFs, which share one fixed-heavy cost curve.

**Against later UKRS2 generations.** Within UKRS2, the 1830–1913 steam roster prices
consistently at £3.7–5.5/hp (Planet £4.38, Coppernob £4.72, Goods £4.38, Mineral £4.07,
Edwardian £5.51). The early engines are not anomalously cheap *within the set*. UKRS2
is internally consistent.

**Against NARS and GETS.** Size-matched pairs (forensics §4) show NARS at 5.33× UKRS2
for 200 hp, falling to 1.0–1.2× at 2,000–2,500 hp. The NARS Add-On is *cheaper* than
UKRS2 in 8 of 9 matched pairs from 1895. GETS has no locomotives before about 1880, and from then on it is
cheaper than UKRS2 in every era.

**Against the project's cargo revenues (RUNTIME, Phase 3 in-game).** UKRS2 early steam
does not produce outsized profit:

| Phase 3 service (Planet, UKRS2 wagons) | Capital | Mean revenue/yr | Payback |
| --- | --- | --- | --- |
| Coal, 4 wagons, 26 tiles (`rail-coal-ledger`) | £12,349 | £2,387 | **not reached in 20 years** |
| Coal, 12 wagons + brake van | £16,283 | £5,320 | 5 years |
| Passenger, Lodi (`rail-lodi`) | £14,420 | £5,656 | 4 years |

In comparison, the Phase 3 sailing ships paid back in 1–2 years. Payback periods of
4–20 years are not the signature of an underpriced locomotive. If Planet's running
cost were raised to Grasshopper's level, the 4-wagon coal route would become a
permanent loss: the Grasshopper version lost £1,562/yr on the identical route.

**Against investment and replacement economics.** The UKRS2 bill rises about £37/yr
for every year of age (Planet on coal: £666 in year 1, £1,288 in year 20). From about
1940 a calendar surcharge also builds up, reaching +40 factor units, or +£5,250/yr, by
2025. UKRS2 therefore *does* make players pay to keep old steam running. Its low 1830
catalogue figure is the **new-vehicle, early-calendar minimum** of a rising curve.
Comparing it with a set whose cost never changes (NARS) exaggerates the lifecycle gap:
5.1× billed in years 1–5, but about 3.5× over a 20-year Planet life.

**Against other historical NewGRFs.** Not testable here. No sets beyond the six
installed were measured, and none could be downloaded (BaNaNaS blocked). The six-set
comparison above is the best available proxy.

**Conclusion on B: rejected** as a general claim. UKRS2's 1830s engines are the cheapest
early option, but they are consistent with UKRS2's own curve, with later UKRS2 engines,
with the cross-set median after 1880 and with modest observed paybacks.

### A: "NARS operating costs are excessively high"

The claim has two separable parts.

1. **Set-wide scale: supported.** NARS 2.52 uses +4 on the steam base for every
   locomotive. Halving all NARS 2.52 running costs (+4 → +3) as a counterfactual puts
   it within about ±30% of the other sets' median in 10 of 12 era/traction cells. The
   exceptions are electric 1880–1913 (only two sets) and electric 1946–70:

   | Cell | NARS now | NARS ×½ | Median of other sets |
   | --- | --- | --- | --- |
   | Steam 1880–1913 | 7.62 | 3.81 | 3.83 |
   | Diesel 1971–90 | 5.34 | 2.67 | 2.76 |
   | Electric 1991–2025 | 2.53 | 1.27 | 1.30 |
   | Steam 1830–79 | 11.71 | 5.86 | 6.07 |

   It is consistent with this that the NARS Add-On, from a related design lineage,
   ships its running-cost multiplier at **½ by default**. That is soft evidence that
   its author also judged the NARS-style scale too high (an inference, not a
   documented intent).
2. **Small early engines: supported, with a different cause.** Even at ×½, Norris would
   still be £3,150 (£15.75/hp), against Planet's £4.38/hp and Coppernob's £4.72/hp.
   The remaining excess comes from the fixed factor (about 20 units) in the NARS curve.

NARS also has **compensating cheaper purchase prices**: 0.6–0.96× of the matched UKRS2
engine. Its higher running cost is partly a design choice ("cheap to buy, dearer to
run"). That choice only becomes a trap for small, early, lightly loaded trains.

### C: "Both sets use incompatible economic scales"

**Supported for the early era**, though not exactly as phrased. The sets do not differ
by one scalar. They differ in **curve shape** (fixed + per-hp against proportional) and
in **callback philosophy** (flat against state-, age- and calendar-dependent). No single
multiplier on either set can reconcile both a 200 hp and a 2,000 hp comparison.
Multiplying UKRS2 by 5.33 to match Norris would make the UKRS2 Pacific 4.4× the NARS
Mikado.

### D: "Neither set is misconfigured; different design assumptions"

**Partly true.** Both sets are internally consistent. UKRS2 builds in obsolescence
through its age and calendar surcharges. NARS charges a heavy fixed overhead per
locomotive, which rewards long, heavy trains. That suits North American practice, and
it shows in the TE-heavy freight roster from 1914 onward: Mallet 560 kN, Big Boy
600 kN, against the UKRS2 8F at 142 kN (`heavy_freight_te.txt`). The *combination* of
these sets in one 1830 campaign, where any player may buy any set, is what produces the
trap. D explains the cause. It does not remove the need for an adjustment, because
OpenTTD does not restrict players to their "national" set.

## Answer

| Claim | Status |
| --- | --- |
| UKRS2 early steam is cheap relative to NARS | True (RUNTIME + DERIVED) |
| UKRS2 is underpriced in general | **False**: above the cross-set median after 1880, highest capital, rising lifecycle cost |
| UKRS2 early steam produces excessive profit | Not supported: Phase 3 paybacks of 4–20 years with in-game ledgers |
| UKRS2 is the right baseline for everyone | **No**. It is the high-cost outlier for 20th-century steam and diesel, so using it as the reference would make GETS, Polish and Add-On engines look "too cheap" |
| The correct framing | NARS 2.52 has a 2× set-wide running scale outlier, plus a fixed-cost curve that punishes small early engines. UKRS2 is internally consistent but time-varying, so compare it at in-service dates, not 1830 catalogue values |

UNVERIFIED and worth testing: UKRS2's calendar surcharge may read the economy date,
which runs 30 years behind the calendar in this scenario. If so, the campaign would see
the surcharge three decades later than the snapshots suggest. UKRS2's loaded-moving
rate is also untested on graded, fully loaded routes.
