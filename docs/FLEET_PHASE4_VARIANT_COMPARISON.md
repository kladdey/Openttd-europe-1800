# Fleet Phase 4: variant comparison

The three competing experimental variants were run against the untouched original fleet
under identical seeds (734–738), routes, cargo supply, consists filled to the 7-tile limit,
orders, station layouts, gradients and settings, with subsidies off. JGRPP 0.73.4 and
Historical AXIS 0.6.0. The full per-era table, with every locomotive and duty, is
[`research/fleet_phase4/era_comparison_table.md`](research/fleet_phase4/era_comparison_table.md),
generated from `fleet_phase4_results.csv` by `gen_tables.py`.

## The variants (exact GRF content: `grf_build/MANIFEST.json`)

| | A: targeted | B: steam-era normalisation | C: cross-set normalisation |
| --- | --- | --- | --- |
| NARS 2.52 | Norris and 4-4-0 American moved to running-cost class 44 at +3: ×0.4286 (£6,300 → £2,700; £7,612 → £3,262) | All 21 NARS steam locomotives moved to class 44 at +3: ×0.4286. Diesels and electrics untouched | All 71 NARS locomotives ×0.5 (NARS-local class 42: +4 → +3). Norris and American additionally on class 44 at +3: ×0.4286 |
| NARS Add-On | Grasshopper factor 24 → 6 (£3,150 → £787); T.D. Judah 30 → 12 (£3,937 → £1,575) | — | As A |
| UKRS2 | — | — | — (deliberately; see below) |
| Engines changed (RUNTIME catalogue) | 4 | 21 | 73 |
| GRFs | 2 (132 + 116 bytes) | 1 (379 bytes) | 2 (142 + 116 bytes) |

Mechanisms are the ones proven in game ([callback validation](FLEET_PHASE4_CALLBACK_VALIDATION.md)).
The catalogue integrity check (`catalogue_integrity.json`) covers all 2,854 rail engines at
1850, 1925 and 2000. Each variant changes exactly its intended engines and **no**
purchase price, power, tractive effort, weight, speed, introduction date or capacity of
any engine.

## Why C does not touch UKRS2

The original-fleet era baseline (RUNTIME) puts UKRS2 beside GETS and the Add-On, not
above them:

- flat, saturated, 1945: 8F £50.2k against GETS BR 50 £52.6k;
- 2000: Class 66 £70.1k against GETS 266 £61.8k and Add-On SD80MAC £68.1k;
- 1903: Jinty £39.1k against GETS G5.4 £44.5k.

UKRS2's grade weakness (8F, Mineral and Class 58 stall on 3% at full load) is a
performance property, not a price error. Raising UKRS2 would push the whole campaign's
cost level up. Nothing measured requires it.

## Results: share of the best profit among the tested engines in each era and duty

Operating profit is DERIVED from RUNTIME ledgers, the mean of 5 seeds × 3 stable years.
Values are the NARS-family engine's share of the era-best.

| Era / duty | NARS engine | Original | A | B | C |
| --- | --- | --- | --- | --- | --- |
| 1850 passenger | Norris | 0.66 | 0.82 | 0.82 | 0.82 |
| 1850 passenger | Grasshopper (Add-On) | 0.30 | 0.41 | 0.30 | 0.41 |
| 1860 flat, saturated | 4-4-0 American | 0.56 | 0.69 | 0.69 | 0.69 |
| 1878 flat, saturated | Mogul / Consolidation | 0.84 / 0.94 | 0.84 / 0.94 | 0.90 / 1.00 | 0.90 / 1.00 |
| 1890 passenger | 4-4-0 Express | 0.81 | 0.81 | 0.94 | 0.92 |
| 1903 flat, saturated | Ten-Wheeler / Consolidation II | 0.86 / 0.89 | same | 0.96 / 1.00 | 0.96 / 1.00 |
| 1925 flat, saturated | Mikado / Santa Fe | 0.88 / 0.79 | same | 1.00 / 0.98 | 1.00 / 0.96 |
| 1925 3% sustained | Santa Fe | 0.77 | 0.77 | 1.00 | 1.00 |
| 1940 passenger | Hudson / Jubilee | 0.81 / 0.82 | same | 0.99 / 0.99 | 0.97 / 0.97 |
| 1945 flat, saturated | Mallet | 0.63 | 0.63 | 0.90 | 0.87 |
| 1945 3% sustained | Mallet | 0.63 | 0.63 | 1.00 | 0.98 |
| 1955 flat, saturated | GP9 / RS3 | 0.89 / 0.89 | same | same | 0.98 / 0.97 |
| 1977 flat, saturated | SD40-2 / GP38-2 | 0.85 / 0.87 | same | same | 0.96 / 0.95 |
| 1977 3% sustained | SD40-2 | 0.83 | 0.83 | 0.83 | 1.00 |
| 1980 passenger | F40PH | 0.80 | 0.80 | 0.80 | 0.94 |
| 2000 flat, saturated | SD70MAC / C44-9W | 0.83 / 0.83 | same | same | 0.97 / 0.98 |
| 2025 flat, saturated | SD70MAC / GE Evolution | 0.85 / 0.84 | same | same | 0.98 / 0.99 |
| 2025 3% sustained | SD70MAC / GE Evolution | 0.77 / 0.79 | same | same | 0.95 / 0.99 |

**Highest share any NARS engine reaches over the best other engine under C:** 1.04–1.06
(1878 Consolidation against UKRS2 Goods, flat; 1925 Santa Fe against Add-On Angus,
grade; 1977 SD40-2 against GETS V320, grade). There is no new outlier. This is enforced in
`test_phase4.py` with a ≤ 1.10 bound.

## Verdict per variant

- **A (targeted)** fixes the two 1850 traps. It leaves every later NARS engine 11–37%
  behind its contemporaries: 1860 American at 0.69, 1945 Mallet at 0.63, NARS diesels
  0.77–0.89. It is too narrow.
- **B (steam-only)** proves the steam-only restriction works (21 engines exactly). It is
  the best 1878–1945 result, but NARS diesel and electric traction stays at 0.77–0.89
  from 1955 to 2025. Its single class-44 group also forces Norris onto the same ×0.43 as
  the Mallet.
- **C (cross-set)** brings the tested NARS engines to 0.87–1.00 of the era-best on their
  saturated-flat, grade and passenger duties, from 1878 to 2025. The exceptions are the
  residuals listed below, plus engines on grades they physically cannot climb (GP38-2,
  Mikado), where every engine loses money. It does this without beating the best British,
  German or Add-On engine by more than 6%, and it keeps the early fixes of A. **C
  performed best.**

Residual gaps under C are role or physics properties, not prices:

- **1860 American at 0.69**: it delivers 2,002 t against the Long Boiler's 2,574 t.
- **1850 Grasshopper at 0.41**: 63 hp.
- **Mallet at 0.67 on supply-limited flat duty**: a 431 t engine on a light, low-demand
  service.

## Determinism control

The unaffected UKRS2 Class 66 and GETS BR 266 were rerun under every variant's GRFs: 180
runs. Their delivered tonnage, revenue and running cost are **identical** to the
original-fleet runs on every seed (RUNTIME, `test_phase4.py`). The variants change
nothing outside their engines, and the simulation is deterministic.
