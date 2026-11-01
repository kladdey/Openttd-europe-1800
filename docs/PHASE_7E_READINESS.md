# Phase 7E — modern freight readiness

**READY WITH CAVEATS.** Actual paid recycling deliveries now work on the real 4096×4096 Europe map. This closes the Phase 7D construction-only gap for the tested Lille chain; it does not certify sustained profit, all regions or multiplayer.

## What ran

Starting commit: merged Phase 7D `aaf6f6f`. Branch: `feature/phase-7e-modern-freight`. **Six JGRPP invocations: three completed, three failed fixture attempts. Eight focused Python tests pass.** No broad regression or full-Europe historical simulation was repeated.

1. Capability probe loaded the existing Phase 7D Europe modern checkpoint: **617 towns / 551 industries / seven-tile trains**. Actual buildability/refit checks found engines 407 and 369 compatible with the required cargos. These are existing eGRVTS trucks, available at this 1985 calendar fixture, not newly enabled engines.
2. Three early delivery attempts exposed fixture defects: nonexistent `GSTile.IsIndustryTile` API; no turning-loop access at a chosen station; a vehicle entering the road before its loop was finished. Each stopped after the observed error. Fixes use the supported industry-tile lookup, test turning access before station commitment, and keep the fleet stopped until all routes/loops are complete. No AXIS or production-GS change was necessary.
3. Corrected Europe run: actual RCYC loading, unloading and payment to recovery and junkyard; PLAS delivered to plastics; MNSP delivered to accepting food processor. It sampled **366 economy days**, including construction. All four legs paid.
4. Secondary run reloaded that disposable gameplay save, retained the existing fleet, constructed EAF 551 through the native API at tile **5925256** (2440,1446), and operated SCMT from junkyard 548. Paid delivery and actual **STEL/SLAG** production were observed over another 366 economy days. QLME remained zero in sampled stocks.

Raw logs stay in ignored isolated profiles. [Receipts](research/phase7e_engine_receipts.json) record every invocation, source/script/log hashes, commands, failed attempts and sampled observations. [Route CSV](research/phase7e_paid_routes.csv) records industry, vehicle, engine and station IDs. [Cargo contracts](research/phase7e_cargo_contracts.json) pin source and generated NML definitions.

## Topology and contracts

| Leg | Cargo ID | Industry IDs (local type IDs) | Stations | Vehicles / engine |
|---|---:|---|---|---|
| Depot → recovery | RCYC 48 | 547 (24) → 549 (23) | 16 → 17 | 0,1 / 407 |
| Recovery → plastics | PLAS 44 | 549 (23) → 550 (18) | 18 → 19 | 2,3 / 369 |
| Plastics → food processor | MNSP 38 | 550 (18) → 546 (56) | 20 → 21 | 4,5 / 369 |
| Depot → junkyard | RCYC 48 | 547 (24) → 548 (25) | 16 → 22 | 6,7 / 407 |
| Junkyard → EAF | SCMT 52 | 548 (25) → 551 (79) | 23 → 24 | 96,28 / 407 |

Food processor 546 already existed in the Phase 7D nine-opening fixture; it is not one of the original 542 industries. All endpoints above are actual registered/accepting instances. Destination station acceptance scores were at least 48 eighths, above the required eight. The junkyard is recovery's siting prerequisite, not the source of PLAS.

The active **BASIC_TEMPERATE** recipes are RCYC 6 → PLAS 3 at recovery; PLAS 5 / MPAR 3 → MNSP 6 at plastics; RCYC 6 → SCMT 3 at junkyard; SCMT 4 / QLME 2 → STEL 6 + SLAG 2 at EAF. These ratios are native production arithmetic, not a promise of those quantities per truckload. The generated callbacks combine supplied input contributions; they are **not mandatory all-input gates**. PLAS alone produced MNSP, and SCMT alone produced steel/slag in the tests. MPAR and QLME are additional accepted production inputs, not proven mandatory requirements. This is the existing AXIS abstraction; no fictitious new conversion or recipe was introduced. Electricity is not a required cargo in this active EAF recipe. A fully supplied EAF and downstream steel/slag deliveries remain untested.

## Sampled economics — GBP

| Leg | Station Manhattan tiles | Approx. measured route cash outlay | Positive vehicle-income samples | Vehicle profit, current + previous economy year | Peak load / capacity |
|---|---:|---:|---:|---:|---:|
| RCYC → recovery | 30 | £15,940 | £7,829 | £6,963 | 32/32 |
| PLAS → plastics | 23 | £12,515 | £893 | £128 | 8/32 |
| MNSP → food processor | 20 | £11,143 | £170 | **−£648** | 5/32 |
| RCYC → junkyard | 16 | £9,967 | £3,200 | £2,245 | 32/32 |
| SCMT → EAF (later run) | 83 | £24,043 | £1,775 | £854 | 13/32 |

Engine 407 is the **Prime Carrimor Hopper Truck**, purchase £2,953, list running £403/year; engine 369 is the **Witsharp Brooks Box Truck**, purchase £2,666, list running £356/year. Two trucks per leg, capacity 32 each after refit. The observed peak is not mean utilization; route distance is station Manhattan separation, not driven path length. Costs were checked in the actual loaded fixture, not normalized to a different economy.

Positive income samples are increases in vehicle profit near the accepting stop after a sampled load decrease, with no transfer orders. Loading is also independently observed. Income can be credited after the load reaches zero, so the payment row itself may show zero before/after load. The unload flag is service-wide; these are positive vehicle-income observations, not an exact itemized gross-revenue ledger. Vehicle profit includes native vehicle expenses but excludes shared infrastructure maintenance, interest and capital. The current/previous-year sum is the recorded figure for the sampled window, not an extrapolated annual profit.

Initial company cash was **£97,700**, loan **£100,000**; after the four-route run cash was **£52,752**, loan unchanged. Route cash outlays sum to **£49,565**. The remaining approximately £4,617 cash contribution is a **calculated residual**, not a clean controlled annual operating-profit figure: build timing and shared expenses affect allocation. The later run started at £52,750 and ended at £36,171 after its new £24,043 route, while the previous services continued operating. Do not attribute that company's entire income to scrap transport. Cash-delta outlays include infrastructure, vehicles, turning loops and contemporaneous account movement; scheduled industry construction is not charged as a player-funded factory investment. No company cash was injected, no loan increased and no cargo/production was forced.

**Technical operation: proven. Sampled downstream operation: mixed.** MNSP delivery was paid but the two-truck fleet lost money. PLAS was only slightly positive before shared infrastructure costs. The high-capacity upstream services subsidize this demonstration's downstream overcapacity. Sustained profitability, capital payback, competing-company effects, breakdown sensitivity and seasonal/long-term throughput remain unverified. No price, production or blanket-subsidy changes are proposed. First test a smaller/slower-dispatched downstream fleet and measure actual demand before considering balance changes.

## Safety and reproduction

The normal Phase 7D candidate remains unchanged at SHA-256 `8eb114a0a4b4ea95363b810bfc815c0b30998e254399ff0d0dad8574e8456ec9`: **617 towns / 542 initial industries / 15 GRFs / 64 cargos / calendar 1830, economy 1800 / seven tiles**. Its normal engine, GRF, GS and profile assets were hash-verified after testing. AXIS 0.6.0 binary, GS v4/schema 4, four-mine and one-mill policies were not edited. Source snapshot hashes were checked before/after each completed invocation. No source scenario, player save or global configuration was overwritten.

The 551-industry snapshot is the earlier engine-built **1985 calendar construction fixture**, not a new campaign baseline. GSDate outputs in receipts are **economy dates around 1801–1803**, not claims that modern trucks existed in 1801. Inflation/currency and other economic settings are inherited from the scenario; GBP's API conversion rate is one. No date/economic settings were changed for this phase. Modern availability comes from the existing supported Phase 7D calendar jump.

The transport probe deliberately replaces the GS only in an isolated disposable profile. It does not load the fixture's lifecycle ledger; the engine reports that fixture-only saved script data was not loaded. This is **not** a normal-save migration or a new proof of lifecycle persistence. Physical industries, vehicles and orders were reloaded for the secondary run. Native EAF placement uses a bounded 96-attempt, full-layout-union check rejecting occupied/house/road/water/non-level tiles; native callbacks still decide final construction. No demolition/flattening/cargo-spawning commands are used. Do not substitute this probe into a real campaign.

On the development PC with the retained Phase 7D assets and modern fixture:

```powershell
python scripts/modern_phase7e.py capability
python scripts/modern_phase7e.py delivery
python scripts/modern_phase7e.py secondary
python scripts/modern_phase7e_evidence.py
python -m unittest discover -s tests -p test_phase7e_modern_freight.py
```

The driver creates unique ignored profiles under `newgrfs/axis-historical-progression/.work/runtime/phase7e`; `secondary` uses the latest successful delivery checkpoint. The six recorded invocations include the three failed development attempts; rerunning the corrected three commands adds new invocations, it does not erase them. Raw logs are not required for the eight focused tests, which validate the committed receipts and fixture safety logic. A repository clone alone lacks compiled/local fixture dependencies. The normal campaign still launches with `python scripts/lifecycle_phase7d_launch.py`.

**Next:** one-versus-two-truck downstream comparison, actual final steel/slag use, then Kladdey/Squirrel/Toni save/rejoin and competitive freight testing. No further economic correction is justified by this short demonstration. Changes are committed locally only; no push or merge is authorized for Phase 7E.
