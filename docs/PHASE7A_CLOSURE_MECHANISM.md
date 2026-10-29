# Phase 7A — Real closure mechanism

## What stock JGRPP permits

JGRPP 0.73.4 exposes deity construction, industry control flags, text and production-level commands. Its GameScript API has **no arbitrary delete/close-industry command**. `GSIndustry.SetProductionLevel` accepts native levels 4–128; neither zero nor callback result 3 can be passed as a production level. The engine probe actually rejected level 3.

A NewGRF monthly production callback can return `CB_RESULT_IND_PROD_CLOSE = 0x03`. The engine applies closure safeguards, queues closure, and removes the industry in a subsequent economy-month update. Therefore script state alone must never certify closure.

## Implemented handshake

The separate Historical AXIS 0.4.0 candidate adds a coal monthly callback (0x35). It returns CLOSE only when all of these conditions hold:

1. Lifecycle parameter 11 is enabled.
2. Historical mode and Classic economy are active.
3. The coal industry was founded by `OWNER_DEITY = 18`.
4. Its native production level is **4**, reserved as an explicit scheduler closure request.

The GameScript protects managed mines with `INDCTL_NO_CLOSURE` during normal operation. After the actual warning lead and any earned finite extension, it clears that flag and requests level 4. A level 8 command at warning produces real decline. The ordinary base is level 16. Returning callback code 3 is a GRF action; requesting production level 4 is a separate supported GS action. They must not be confused.

The script retains the industry's complete signature, polls for its physical absence, then announces `closed`. A replacement can depend on that confirmed state. If native guards prevent removal for more than 120 economy days, the script protects the surviving industry, restores level 8 and records `failed_closure`. It does not compensate companies, delete rolling stock or edit save bytes.

## Evidence

* **Fixture engine probe:** two deity mines opened; the requested one ceased existing while the other remained. `P7 CLOSURE|0|still_exists=false|other_exists=true` is retained in [engine receipts](research/phase7a_engine_run_evidence.json).
* **Small-map vertical slice:** an operating producer/consumer route loaded coal and registered positive net vehicle income. Three scheduled mines opened, declined, warned and physically disappeared after save/reload. Replacement construction reused a former runtime ID at a different tile without confusing the ledger. This particular run ended with its replacement still `closing`; it is not counted as four confirmed closures.
* **Full Europe vertical slice:** three regional test mines plus a replacement opened; all **four physically closed** by 1832-12-31 under explicitly accelerated test lifetimes. A separate post-closure reload found all four signatures absent and all 542 baseline industry signatures intact. FOOD acceptance remained 76 industries and GOOD acceptance 69. No retail closure was used to simplify the test.
* **Real warning duration:** a separate 35-year small-map run used ordinary calendar-year arithmetic and shortened **30-year test lifetimes**. The first three mines received 3,662 / 3,661 / 3,661 days of notice before closure requests in 1861/1862/1863. Actual physical closure followed. The replacement remained open as the protected last producer.
* **Injected timeout boundary:** a deliberately overdue pending request left a real industry alive and protected, reporting failure. This proves the safe-failure branch, not an observed four-month organic engine blockage.

The final Europe run observed real reduced output at level 8 (for example, monthly samples around 63–80 tonnes versus 160–180 at level 16); month length, prior production periods and service also affect samples. The callback's base scaling is halved. This is not a controlled profitability estimate.

## Fairness and current limits

Production configuration gives ten calendar years of warning, persistent industry text and a near-deadline reminder. Public economic news is broadcast with a tile link. A Windows GUI test actually displayed the warning and clicking it centred the managed Wolverhampton-area mine. Closed mines leave stations, roads, rails and vehicles behind. The Europe test still had two horse vehicles after closure; there is no silent liquidation, refund or subsidy.

Well-served managed mines can earn at most fifteen extra years. Service thresholds were verified with **injected earlier history and an actual qualifying current month**, rather than a fabricated five-year transport observation. Real long-duration service and severe economic-loss tests remain Phase 7B work. Ten years of notice is implemented; whether a 50% decline throughout that interval is fair is not yet calibrated.

Baseline neutral and player-funded industries are excluded from this adapter. Existing farms/forests/shops are not treated as finite coal resources. No general mechanism is claimed for retiring every existing industry, nor can arbitrary GS text be assumed readable as a NewGRF marker. To retire a selected pre-existing mine safely, Phase 7B needs an explicitly verified per-instance handshake or engine API and a migration plan. Production level 4 is a reserved protocol value for experimental deity-founded coal; other deity administration tools must not use it casually.

Native engine last-instance protection remains enabled. The scheduler also counts queued closures before requesting another, and explicitly defers the last coal producer. Future multi-stage recipes, factory migration, reused brownfield land and economic replacement guarantees are outside this coal-only foundation.
