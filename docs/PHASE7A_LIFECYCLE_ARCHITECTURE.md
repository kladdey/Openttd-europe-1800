# Phase 7A — Historical industry lifecycle foundation

Verdict: **READY WITH CAVEATS**. A real, persistent coal-mine lifecycle works in unmodified JGRPP 0.73.4. This is an experimental foundation, not a completed 1830–2025 campaign scheduler. See [engine evidence](PHASE7A_ENGINE_VALIDATION.md) and [remaining work](PHASE7A_READINESS.md).

## Baseline and scope

The input is Phase 6C's **Europe 1830 Historical AXIS 0.3.0 - Inland Markets.scn**, with 617 towns, 542 industries, 15 NewGRFs, 96 registered industry types and 64 cargo slots. Its SHA-256 is `afcab50864e87f56a7260c62d87bd37560fa3d7676713afb14c480c555d0bc06`. The source scenario, normal configuration, original GRFs and all earlier research remain untouched.

The foundation manages **new, explicitly scheduled deity-founded coal mines**. It does not automatically manage the existing 542 industries or close farms, shops and factories. Production scheduling contains three source-backed opening districts; test schedules separately compress lifetimes and move events to suitable test locations. They are never silently substituted for historical dates.

## Implemented architecture

* **Historical AXIS 0.4.0 candidate:** five template/language changes, preserving all industry/cargo models. Parameter 11, `lifecycle_scheduler_mode`, defaults off. Its opt-in policy admits deity construction while rejecting natural random placement. A narrowly scoped monthly coal callback accepts a closure command encoded by native production level 4.
* **Historical Industry Lifecycle GameScript v1, schema 1:** server-side rules, bounded construction searches, persistent industry identities, warning/decline/closure/replacement states and news. Uses actual supported APIs. No custom executable or save-byte rewriting.
* **External JSON authoring and compilation:** `schedule.json` compiles to native `schedule.nut`; there is no assumed runtime JSON library. The validated production schedule is committed alongside its generated form and CSV.
* **Isolated engine fixtures:** disposable small maps and copies of the full Europe scenario; exact asset identities and source hashes guarded before/after execution. Experimental files remain under `.work/runtime`, outside the user's normal OpenTTD profile.

Industry identity combines runtime ID, type, tile and construction date. The Europe replacement reused a deleted industry's numeric ID at another location; the ledger correctly distinguished them. Save/Load retains statuses, warning dates, deadlines, attempts, service counts, signatures, seed and schedule contract. Supported legacy schema 0 migrates to 1; unknown schemas remain preserved and inactive. Schedule edits require explicit migration, rather than resetting an old ledger.

## Time and determinism

`GSDate.GetCurrentDate()` reads **economy time**. The Europe scenario starts at calendar **1830-01-01 (668394)** but economy **1800-01-01 (657437)**. Using GSDate directly would schedule events thirty years incorrectly.

The stock engine stamps a newly created StoryPage with `CalTime::CurDate()`. The script reads that date and immediately removes the unshown page, approximately once per fortnight. This supplies actual calendar time through supported commands. Gregorian decoding is accepted only with `economy.timekeeping_units = 0`; wallclock mode fails closed. This workaround creates two Storybook commands per sample and could cause UI churn; a native calendar accessor is preferable eventually. There is no hard-coded thirty-year offset.

Seed **7341830**, stable event IDs, ordered candidate tiles and a deterministic hash choose finite lifetimes. Replaying the same saved checkpoint produced the same significant transitions. Native `BuildIndustry` still chooses layouts through engine RNG; independent cold-start maps are not promised byte-identical. Execution remains server-authoritative; no client-side timers are involved.

## Lifecycle policy

The path is `planned → eligible/opening → operating → warned → closing → closed`, with explicit deferred/failed states. A mine opens only after its calendar eligibility date and any predecessor has physically disappeared. Site checks require a flat clear/tree 5×5 footprint covering coal layouts, with no roads, water, houses or intentional terraforming. Native historical, town, proximity, terrain and layout restrictions still apply.

Construction is bounded by 48 attempts and three monthly batches per production event. Unsafe candidates are skipped; impossible events fail visibly. A newly opened mine is protected from ordinary closure. Proposed operating lifetimes are 110–140 years, with ten-calendar-year warning. These lifetimes are a gameplay proposal, **not claims about historical mine closure dates**.

At warning, native production level drops from 16 to 8. Persistent industry text identifies decline and the earliest closure year; news links to the site. There is a near-deadline reminder, extension notice, physical closure confirmation and explicit failure/defer message. A late-loaded warning still grants the full notice interval from the actual warning.

Transporting at least 40% in a sampled month accumulates service credit: 12 qualifying months earn ten extra years, 60 earn fifteen total. The extension is finite. Boundary tests injected earlier service counts and used actual current transport observations; they do not establish decades of observed service behaviour. This policy and the 50% decline require economic calibration before broad deployment.

The final operating coal producer is protected, including other queued closures. If closure remains pending for 120 economy days, the script restores protection and level 8, announces failure and never reports a nonexistent success. Deferred/failed closure requires administrator review; automatic retry is deliberately absent in v1.

## Historical rules

| Event | Production eligibility | Evidence and distinction |
|---|---|---|
| South Hetton district | 1833-08-05 | [Durham Mining Museum](https://www.dmm.org.uk/colliery/s007.htm); opening, rather than earlier shaft work |
| Zollverein district | 1851-01-01 | [Zollverein history](https://www.zollverein.de/zollverein-unesco-world-heritage-site/history/); first coal in 1851, rather than foundation in 1847 |
| Guido district | 1860-01-01 | [Polish heritage register](https://zabytek.pl/pl/obiekty/zabrze-zespol-zabudowan-i-wyrobisk-chodnikowych-dawnej-kopalni-g); production in 1860, rather than foundation in 1855 |

January 1 represents year-only source precision. Coordinates are town-calibrated district anchors, not exact shaft reconstructions. Existing representative mines lie about eight tiles from South Hetton's anchor and two from Guido's. Their successful future placement on Europe is **not proven**; native proximity/one-industry-per-town rules may reject them. Phase 7B must resolve this geographic overlap explicitly. No existing mine was removed or placement restriction bypassed.

Reproduction, source receipts, logs and scoped results: [engine validation](PHASE7A_ENGINE_VALIDATION.md).
