# Inland market coverage

**ENGINE-CALCULATED distances from verified industry locations and acceptance.** These Manhattan distances are lower-bound diagnostics, not constructed road lengths, travel times, ship access or profits.

| Cargo | Producers | Consumers before → after | Median tiles | P90 tiles | Maximum tiles | Producers >160 tiles | Producers >300 tiles |
|---|---:|---:|---:|---:|---:|---:|---:|
| FOOD | 92 | 13 → **76** | 524.5 → **72** | 1215.9 → **162** | 2394 → **303** | 70 → **11** | 60 → **1** |
| GOOD | 56 | 12 → **69** | 648.5 → **90.5** | 1162 → **317** | 1747 → **428** | 51 → **10** | 45 → **6** |

All previous consumers remain. New Food Markets and General Stores add 63 FOOD destinations; General and Hardware Stores add 57 GOOD destinations. FOOD and GOOD outputs are not changed. Fresh fruit has six additional targeted regional Food Markets; the FOOD/GOOD statistics do not count FRUT producers as FOOD producers.

## Regional consumer distribution

Regions inherit the Phase 6B geographic categories. New markets are assigned to the nearest existing industry region, a reproducible approximation near borders rather than a new historical frontier claim.

| Region | FOOD before → after | GOOD before → after |
|---|---:|---:|
| GB — British Isles | 4 → 12 | 3 → 11 |
| FR — France | 1 → 11 | 1 → 9 |
| BX — Belgium/Netherlands | 0 → 3 | 0 → 3 |
| DE — German states | 1 → 7 | 2 → 8 |
| PL — Polish/Silesian territories | 1 → 6 | 1 → 6 |
| CE — Central Europe | 0 → 5 | 0 → 5 |
| SC — Scandinavia | 2 → 5 | 1 → 4 |
| BA — Baltic | 0 → 3 | 0 → 3 |
| IB — Iberia | 4 → 9 | 4 → 7 |
| IT — Italian states | 0 → 7 | 0 → 5 |
| SE — Southeastern/Eastern allocation | 0 → 8 | 0 → 8 |

The existing Phase 6A broad coastal-town screen classifies the resulting FOOD consumers as **51 inland / 25 coastal**, and GOOD as **46 inland / 23 coastal**. Before implementation all 13/12 consumers were coastal trade industries. A town being broadly coastal does not prove a market has dock catchment, navigable water or sea access. Four new Phase 6A port towns are preserved; none is assigned an invented dock result.

## Remaining gaps and intentional trade distances

Worst FOOD destinations by nearest-distance screen:

| Producer industry ID | Producer region | Nearest market town | Tiles |
|---|---|---|---:|
| 284 | Iberia | Madrid | 303 |
| 255 | Britain | Leicester | 251 |
| 273 | Polish territories | Gorzów Wielkopolski | 239 |
| 268 | German states | Gorzów Wielkopolski | 230 |
| 279 | Baltic | Klaipėda | 210 |

Worst GOOD: producer 244 → Szolnok **428**, 233 → Uzhhorod **381**, 377 → Roma **367**, 237 → Kristiansand **365**, 238 → Helsingborg **356**. The sixth >300-tile producer is retained in the full dataset. These are unsolved regional logistics, not silently certified practical routes. Mountain passes, water crossings and small town populations can worsen access. Adding a store to every village merely to eliminate distance outliers would defeat the hierarchy and demolition safeguards.

Actual route tests establish access for selected Kraków, Prague, London, Valencia and French regional supply lines. They do not certify all 148 FOOD/GOOD producer routes or prove identical regional opportunities. Three-player choices now include inland consumption as well as coastal export; costly trunk distribution remains a real strategic decision.

Data: [summary](research/inland_market_coverage_summary.csv), [148 producer rows](research/inland_producer_market_distances.csv), [regional counts](research/inland_market_regional_coverage.csv), [placement locations and town anchors](research/inland_market_placements.csv). Recalculate with `scripts/inland_phase6c_coverage.py`.
