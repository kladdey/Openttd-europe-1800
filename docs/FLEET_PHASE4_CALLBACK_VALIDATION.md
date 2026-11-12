# Fleet Phase 4: callback and ageing validation

Does each experimental change reach every operating state? Does it leave unrelated
callbacks and properties alone? All values are RUNTIME (GameScript
`GSVehicle.GetRunningCost` sampled every 5 ticks, plus ledgers) unless labelled DERIVED.

## 1. Which override mechanisms reach the bill

From suite `feas` (Norris, Grasshopper or Planet with 4 NARS hoppers, 1850, subsidies
off). Consist rates include 4 × £38 for the hoppers.

| Test GRF | Catalogue | Moving loaded | Moving empty | Platform (loading) | Depot | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Original Norris | £6,300 | £6,452 | £6,452 | £1,727 | £1,727 | reference |
| NARS prop 0x0D factor 24 → 12 | **£3,150** | **£6,452** | £6,452 | £1,727 | £1,727 | **Does not work**: the callback ignores the property in service; only the purchase list changes |
| NARS prop 0x0E → class 44, class-44 exponent +4 | £5,400 | £5,552 | £5,552 | £1,502 | £1,502 | **Works**: engine 5,400 / 1,350, ¼ kept |
| Original Grasshopper | £3,150 | £3,302 | £3,302 | £3,302 | £3,302 | flat set |
| Add-On prop 0x0D factor 24 → 12 | £1,575 | £1,727 | £1,727 | £1,727 | £1,727 | **Works** in every state |
| Original Planet | £525 | £546 | £546 | £283 | £283 | reference |
| UKRS2 prop 0x0D factor 4 → 8 | £525 | £546 | £546 | £283 | £283 | **No effect** |
| UKRS2 prop 0x0E → class 44 (UKRS2 exponent +5) | £1,800 | £1,502 | £1,502 | £602 | £602 | **Works**: engine 1,350 / 450, the ¾ / ¼ shape kept |

## 2. The variants keep every engine's state behaviour

The standstill/moving ratio was computed per engine from the platform and moving rates
of the era runs, minus wagons (`callback_state_ratios.json`). It is identical, within 0.01,
between the original fleet and every variant for all 33 engine × variant combinations:

| Family | Ratio (original = variant) |
| --- | --- |
| NARS 2.52 steam and diesel (Norris, American, Mogul, Consolidations, Ten-Wheeler, Santa Fe, GP9, RS3, GP38-2, SD40-2, SD70MAC, C44-9W, GE Evolution) | 0.23–0.25: the ¼ standstill branch survives the class switch and the exponent change |
| NARS Mallet | **1.00**: it has *no* standstill discount in the original either (new finding) |
| NARS Add-On (Grasshopper, Judah) | 1.00: flat before and after the factor change |
| UKRS2 (unchanged) | 0.34–0.50 depending on engine and age |

Loaded and empty moving rates were equal before and remain equal under all variants. No
modified engine gained or lost a load-dependent branch.

## 3. Ageing (20-year runs, autorenew off, `lifecycle_years.csv`)

| Consist | Depot rate, year 1 | Depot rate, year 20 | Billed, years 1–5 | Billed, years 16–20 |
| --- | --- | --- | --- | --- |
| Norris £6,300 (original), 12 hoppers | £2,032 | £2,032 | £6,238 | £5,896 |
| Norris £2,700 (A/C), 12 hoppers | £1,132 | £1,132 | £3,020 | £2,846 |
| Norris £1,350, 12 hoppers | £794 | £794 | £1,813 | £1,703 |
| Grasshopper £787 (A/C), 6 hoppers | £1,016 | £1,016 | £1,107 | £1,107 |
| Planet (unchanged), 6 hoppers | £359 | £622 | £662 | £1,060 |
| Coppernob (unchanged), 12 hoppers | £850 | £1,244 | £1,325 | £1,603 |

NARS and Add-On engines do not age before or after modification. The class switch does
not import UKRS2-style ageing. UKRS2's age steps are untouched: Planet's depot rate steps
£359 → £622 at 12 years, as in Phase 3. Billed totals vary with moving share and with
reliability (breakdowns "reduced" are on in the scenario settings, so breakdown stops and
depot visits are included in the ledger).

## 4. Autoreplace (suite `autoreplace`, 1850 to 1853)

A rule was set by GameScript after one year, autorenew on, with 4 hoppers:

| Rule | Fleet | Replaced train: parts / capacity | Rate of the new engine at replacement (in depot) |
| --- | --- | --- | --- |
| Norris → Coppernob | original / A | 5 / 80 t (kept) | £546 / £546 (Coppernob unchanged) |
| Coppernob → Norris | original | 5 / 80 t | £1,727 = 1,575 + 152 |
| Coppernob → Norris | **A** | 5 / 80 t | **£827 = 675 + 152** (¼ of £2,700) |
| Grasshopper → Planet | original / A | 5 / 80 t | £283 |
| Planet → Grasshopper | original | 5 / 80 t | £3,302 |
| Planet → Grasshopper | **A** | 5 / 80 t | **£939 = 787 + 152** |

Replacement onto or away from a modified engine keeps the consist and applies the new
engine's modified rate immediately.

## 5. Save, reload and rollback (cloned campaign save)

The clone is a copy of the latest campaign save, `… 1893-06-04.sav`: calendar 1893,
economy 1863, 176 trains, 15 GRFs. The production save and the production save folder
were verified unchanged before and after (`savetest_*.json`).

| Step | Result |
| --- | --- |
| GRF list rewrite | Every chunk except NGRF and GSDT re-encodes byte-identically |
| Load with balance GRF inserted after its target | All 176 trains keep owner, unit number, engine, wagon count and length |
| Costs after load | Only engines the variant targets change. With Variant B, the one targeted engine in use (NARS 4-4-0 Express) goes £9,450 → £4,050; all 13 other engine types are identical. **No purchase price changes** |
| Game-written save | Autosaves were written by JGRPP inside the test run directory (LZMA forced), never in the production folder |
| Rollback | That game-written save, with the balance GRF removed from its GRF list, loads with all 176 identities intact, and **every engine cost returns to the original** |

Variant C results are in `savetest_C_cross.json` and `savecompare_C_cross.json` (see
[compatibility](FLEET_PHASE4_COMPATIBILITY.md)).

## 6. Unrelated callbacks and properties

- **Catalogue integrity**, 2,854 engines × 3 dates × 3 variants: only running cost
  changes, and only for the intended engines. Purchase price, power, tractive effort,
  weight, max speed, wagon flag, design date and capacity are unchanged for every engine.
- The GRFs contain no Action 2/3 and no callbacks, so graphics, refits, articulation and
  sound chains cannot be replaced (SOURCE: GRF bytes, `balance_grf.py`).
- **Determinism**: 180 control runs reproduce the original exactly (see the comparison).

## 7. Grasshopper standstill discount: possible?

**Not without breaking the Add-On's design or graphics.** The Add-On engine has no
running-cost callback; its rate is the flat property. A standstill discount needs
callback 0x36 on that engine, and a callback can only come from an Action 3 attached to
the engine. An Action 3 from a second GRF replaces the engine's whole sprite-group chain,
graphics included. JGRPP's `vehicle_costs_when_stopped` and `vehicle_costs_in_depot`
settings act on every set at once.

This is SOURCE-based and was not built: the graphics loss cannot be observed headless.
It is also unnecessary. Grasshopper moves 89–93% of the time on every duty (RUNTIME), so a
perfect ¼ standstill rate would save about 0.08 × 0.75 × 3,150 ≈ **£190/yr** (DERIVED),
against £2,363 from the base-cost cut to £787.
