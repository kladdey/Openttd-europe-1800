# Fleet Phase 4: historical progression regression

Representative locomotives were run in every requested era, original fleet against
Variants A, B and C. Requested eras map to tested years as follows:

| Requested | Tested |
| --- | --- |
| 1830 | 1832, and 1850 for the Norris comparison |
| 1875 | 1878 (Consolidation intro is randomised around 1875) |
| 1900 | 1903 |
| 1950 | 1945 (steam heavy freight) and 1955 (first-generation diesel) |
| 1975 | 1977 |
| 1925, 2000, 2025 | as requested |

Passenger eras are 1850, 1890, 1940 and 1980. Each cell is 5 seeds × 3 stable years, on
three duties:

- 7-tile coal, flat, saturated supply;
- 7-tile coal, flat, supply-limited (low utilisation);
- 7-tile coal, sustained 3% grade.

Passenger runs use 7-tile trains on 48–96 tiles. Profit is DERIVED from RUNTIME ledgers.
Full data: [`research/fleet_phase4/era_comparison_table.md`](research/fleet_phase4/era_comparison_table.md).

## Era by era under Variant C (the recommended variant)

**1830/1832.** At the 7-tile limit (26 hoppers) both Planet and Grasshopper are overloaded
and lose money on any terrain (crawl at 2 km-ish/h). Early engines need short trains;
this is physics, not price. With 6 hoppers (1850 sweep), Planet earns £8.2k. Grasshopper
earns £3.5k originally and £5.8k under C. Planet stays the better 1830 engine.

**1850.**

- Norris at £2,700 earns:
  - £14.3k with 12 hoppers, against Planet £8.75k;
  - £8.6k with 6 hoppers, against Planet £8.2k;
  - £17.8k on passengers with full trains, against Planet £13.2k.
- It never beats Coppernob (1844) or Crampton (1847): £21.8k and £21.2k on passengers.
- Early-engine dominance: **none**. The 1838 engine beats the 1830 engine, and the
  1844–47 engines beat both.

**1860.**

| Engine | Original | Variant C |
| --- | --- | --- |
| NARS American | £17.9k | £22.1k |
| Long Boiler | £31.8k | £31.8k |
| Coppernob | £24.9k | £24.9k |
| Add-On Winans | £22.5k | £22.5k |

The American remains the weakest. Its capacity is lower (2,002 t against 2,574 t), so the
remaining gap is performance, not price.

**1878.**

| Engine | Original | Variant C |
| --- | --- | --- |
| Mogul | £33.4k | £37.0k |
| Consolidation | £37.4k | £41.3k |
| UKRS2 Goods | £39.7k | £39.7k |

The NARS 8-coupled freight engine edges the UKRS2 0-6-0 by 4%. Judah is a light
passenger engine and is poor on coal at any cost.

**1890 passenger.** NARS Express £31.7k → £36.2k, against Spinner £36.9k and Canadian
Pacific #374 £39.3k.

**1903.** Ten-Wheeler £38.4k → £42.9k and Consolidation II £39.5k → £44.6k, against
PRR D16 £44.2k, GETS G5.4 £44.5k and Jinty £39.1k. This is parity.

**1925.**

- Flat: Mikado £48.1k → £54.3k against Angus £54.4k; Santa Fe £42.8k → £52.5k.
- 3% grade: Santa Fe £26.8k → £36.6k against Angus £34.6k. The UKRS2 Mineral and the
  Mikado lose money there.

**1940 passenger.** Hudson and NARS Jubilee £38k → £45.7–45.8k, against UKRS2 Jubilee
£47.3k and Royal Hudson £42.6k.

**1945, heavy freight.**

| Engine | Flat, original → C | 3% grade, original → C |
| --- | --- | --- |
| Mallet | £33.0k → £45.7k | £23.6k → £36.4k |
| Big Boy (unchanged) | £48.2k | £37.2k |
| Yellowstone (unchanged) | £42.5k | £35.7k |
| Santa Fe | £41.6k → £51.3k | £26.1k → £35.8k |
| UKRS2 8F (unchanged) | £50.2k | −£3.0k (stalls) |
| GETS BR 50 (unchanged) | £52.6k | £28.2k |

On supply-limited flat duty the Mallet stays at £17.8k against the 8F's £26.4k.

**1955.**

- Flat: GP9 and RS3 £55.5–55.7k → £60.5–60.9k, against Alco RSD7 and GETS V200 £62.4k.
- 3% grade: GP9 and RS3 still lose money (light road switchers stall), and so do the 8F
  and V200. The six-axle RSD7 climbs.

**1977.**

- Flat: SD40-2 £57.4k → £64.9k and GP38-2 £58.5k → £64.1k, against Brush Type 4 £67.5k,
  Add-On SD40 £64.2k and GETS V320 £56.6k.
- 3% grade: SD40-2 £34.9k → £42.6k, against SD40 £41.9k and V320 £42.2k. The Brush
  Type 4 loses money.

**1980 passenger.** F40PH £48.6k → £56.8k, against Brush Type 4 £60.4k and BR 218 £57.7k.

**2000.**

- Flat: SD70MAC and C44-9W £58.2–58.4k → £67.9–68.6k, against Class 66 £70.1k, Class 58
  £68.0k, SD80MAC £68.1k and GETS 266 £61.8k.
- 3% grade: SD70MAC £40.1k → £49.7k, against SD80MAC £54.9k, Class 66 £48.2k and GETS 266
  £44.1k. The Class 58 breaks even.

**2025.** SD70MAC and GE Evolution £58.2–58.5k → £68.0–68.4k, against Class 66 £69.1k and
SD70ACe £68.4k. On the grade, £39.4–40.5k → £48.9–50.6k, against SD70ACe £51.3k.

## Checks requested by the brief

| Question | Answer (Variant C) |
| --- | --- |
| Preserves useful historical progression? | **Yes.** Within NARS, the best engine's profit rises each era: Norris £14.3k (1850), American £22.1k (1860, a different route), Consolidation £41.3k (1878), Consolidation II £44.6k (1903), Mikado £54.3k (1925), GP9 £60.9k (1955), SD40-2 £64.9k (1977), SD70MAC £67.9k (2000) |
| Encourages sensible modernisation? | **Yes.** Each later NARS generation out-earns the previous one on the same duty class. The UKRS2 ageing steps (unchanged) still push British steam towards replacement |
| Avoids permanently dominant early locomotives? | **Yes.** Norris (£2,700) loses to Coppernob and Crampton from 1844/47. The American loses to the Long Boiler. No early engine leads beyond its own decade |
| Preserves heavy-freight specialisation? | **Yes, and sharpens it.** American heavy engines (Santa Fe, Mallet, Big Boy, Yellowstone, SD40-2, SD70MAC, SD80MAC) keep the only profitable 3% results at full 7-tile load; the 8F, Mineral, GP9, Brush Type 4 and Class 58 still stall or break even. On flat, supply-limited duty the British 8F still out-earns every American heavy engine |
| Avoids penalising modern American diesels? | **Yes.** It removes the existing penalty: NARS diesels go from 0.77–0.89 of the era-best to 0.95–0.99 |
| Reasonable operating margins? | Every flat 1850–2025 duty is profitable under both the original fleet and C. Payback on train capital (DERIVED, from 1850): saturated supply 0.8–8.3 years originally and 0.9–6.6 under C; supply-limited 0.8–286 originally (the Mallet: one seed loses money) and 1.2–11.1 under C. The worst case under C is Judah on coal |
| New cross-set outliers? | **None.** No NARS engine exceeds the best other engine by more than 6% in any era or duty (test bound ≤ 1.10). Variants A and B were checked too and also create none |

## Weaknesses that remain (not price problems)

- **NARS American 1851** at 0.69: lower capacity and speed than the Long Boiler.
- **Grasshopper** at 0.41 of passenger best and 71% of Planet on freight: 63 hp. It is
  meant to be a budget curiosity; making it competitive would need cutting its cost
  below Planet's.
- **Mallet on low-demand flat routes**: a 431 t engine is the wrong tool there. On its
  intended duty, a sustained grade, it reaches 0.98.
