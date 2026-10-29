# Phase 7B — Depletion and survival policy

The inventory contains **44 actual extractive sites**: 14 coal mines, seven iron-ore mines, two copper mines, two salt mines, eight quarries, seven clay pits and four soda-ash mines. The inventory derives local IDs from the compiled engine registration and cargo definitions from the prepared AXIS source; it does not infer cargo from English names. Full native fingerprints, nearest towns, source provenance and compatible downstream consumers are retained in CSV/JSON. Consumer matching establishes cargo compatibility, not a guaranteed profitable route.

All four soda-ash sites (196–199) remain **unmanaged with unresolved historical provenance**, including the earlier generic regional representations. Missing provenance is not authorization to delete them.

## Limited production pilot

| Original ID | Site representation | Decline begins | Base exhaustion | Latest permitted year | Evidence status |
|---|---|---:|---:|---:|---|
| 1 | Coalbrookdale integrated district, Britain | 1880 | 1900 | 1920 | Regional gameplay window; not a named shaft's verified reserve or closure |
| 11 | Nachtigall shallow Ruhr workings | 1860 | 1882 | 1892 | Early/shallow district proxy; historical closure in 1892 bounds the proposal |
| 12 | Queen Louise Upper Silesian workings | 1950 | 1978 | 1998 | District proxy; historical terminal year 1998 bounds the proposal |
| 438 | Dolcoath copper working | 1890 | 1911 | 1920 | Copper recorded through 1910; eventual mine closure bounds the proposal; no tin conversion |

These are finite **policy windows**, not extracted mineral reserves or a reconstruction of each business balance sheet. Do not confuse exhaustion of a game representation with a precisely proven geological exhaustion date. First warning is ten calendar years ahead, with a five-year reminder and notices of extension/actual closure. Initial 1830 mines are not punished immediately for lack of service.

Historical anchors: [LWL's Nachtigall history](https://zeche-nachtigall.lwl.org/de/geschichte/), [regional heritage authority's Queen Louise history](https://www.metropolia.slaskie.travel/culturalheritage/1703/sztolnia-krolowa-luiza-strefa-carnall), [Durham Mining Museum's Dolcoath production records](https://www.dmm.org.uk/colliery/d241.htm), and the [UNESCO Cornish mining nomination](https://whc.unesco.org/uploads/nominations/1215.pdf). The Queen Louise authority records 1791 construction and 1998 cessation. Dolcoath's records list copper in 1910; the UNESCO nomination records closure in 1920. The generic Coalbrookdale district has lower dating confidence and requires human review before campaign-wide policy adoption.

## Rolling service rule

The model retains 36 actual economy-month observations. An extension requires the full window, more than two calendar years elapsed across samples, aggregate transported cargo ≥1,200 and aggregate transported/produced ≥25%. The normal extension is at most ten years and capped by the site's latest year. It is earned once, remains finite, and cannot make a mine immortal. This rewards sustained throughput without abruptly penalizing a recession, replacement interruption or lost train for a month.

Initial native previous-month counters can be zero at new-game bootstrap. This is a rolling window of observed economy-month counters, not 36 invoices or a guarantee of 36 complete paid calendar months. The successful served case used real repeated transport; no prior service history was injected.

Production decline changes the engine's native production level in stages, retaining the existing commodity recipe and supplies system. Normal coal policy uses levels 14/12/10/8; copper uses the steeper 12/10/8 curve. Reserved arm levels 5/6/7/9 never appear in ordinary decline curves. These shapes are explicit game proposals; actual engine tests establish native production control, not a reconstruction of historical yearly ore grades. No cargo ID, wagon, payment, running cost or vehicle performance changes are involved. Initial supply/base-production differences mean two mines need not emit identical tonnage at the same level. Mine output observations must therefore be compared alongside native level and base production, not treated as exact geological reserve depletion.

The five-year-warning Europe comparisons deliberately use **1837–1839 test exhaustion windows**, with decline starting in 1831 and an earned two-year extension. These dates are confined to disposable fixtures. The playable candidate uses the separate production policy above. Paid deliveries and causal survival are measured in those controlled runs; this does not prove historical dates themselves were reached in the normal candidate.

## Limits and fairness

No modelled reserve tonnage is invented. The rolling metric cannot independently prove that every picked-up unit reached a final accepting consumer. Public industry counters reveal production/transport, whereas payment attribution is vehicle/company state; the engine validation therefore records actual paid routes separately. Larger policy rollout should investigate cargo dumping incentives and how multiple companies jointly serving one mine receive the public survival benefit.

The last producer of a type is protected. Failure to satisfy warning lead within a hard historical cap defers closure for review, rather than violating either constraint silently. Unserved sites can still work for decades; strongly served sites can still exhaust. Infrastructure and vehicles remain after a closure. There is no automatic compensation, demolition, forced rerouting or subsidy.
