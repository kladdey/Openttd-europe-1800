# Phase 7G — regional economic cycles implementation

## Supported mechanism

This is a two-event, one-site vertical slice on the actual Europe map, not a continent-wide business-cycle model. It uses **stock JGRPP 0.73.4 / unchanged Historical AXIS 0.6.0**, extending the existing lifecycle controller with **GS v6/schema 5**.

| Requested effect | Verified capability | Implementation / limit |
|---|---|---|
| Individual industry production level | `GSIndustry.SetProductionLevel`, deity only, **4–128**, automatically sets `INDCTL_EXTERNAL_PROD_LEVEL`; clearing it returns normal control | Used at a newly constructed coal mine: 16 → 32 → 8 → 16. Actual output measured, not assumed from the level. |
| New freight opportunity | `GSIndustryType.BuildIndustry` plus existing native callbacks and safe siting | One neutral Ruhr mine, finite regional search; no existing industry commandeered. |
| Production restoration | `Get/SetControlFlags`, native level restoration | Restore saved level and the original external-production/no-closure bits; preserve unrelated current flags. Mine remains present. |
| Cargo acceptance/recipes | Defined by NewGRF; no verified per-instance GS recipe override | Unchanged. No cargo labels, input recipes or payment values edited. |
| Cargo injection / guaranteed revenue | Not used; no verified mechanism needed for this task | No injected cargo or money. Supply evidence is not paid transport evidence. |
| Announcements / persistence | Existing public news and saved ledger architecture | Four transition notices to all companies; versioned contracts and fail-closed old-save handling. Reload is not engine-tested in this phase. |

Primary implementation evidence is the pinned local engine source in the adjacent checkout, `.research/jgr734/src/script/api/script_industry.hpp/.cpp` and `industry_cmd.cpp` (`CmdIndustrySetProduction`). That command sets the external-control flag, changes the level and recomputes multipliers. AXIS's compiled `coal_mine.nml` computes output using `production_level`, its internal base-production register and supply factors. There is no general promise that doubling the GS level doubles a particular monthly observation. Existing coal closure adapters use special low levels; this cycle never uses their 4/5 authorization sequence.

## Historical policy and fairness

A new neutral Ruhr site is proposed near **(2039,1285)**, within a 24-tile Manhattan search. The map already has nearby coal consumers: Coke Oven 406 and Brick Works 380/389. A registered accepting COAL industry within 160 tiles is required. There is no company reservation, cash transfer, exclusive access, ownership change or privileged routing.

| Event / transition | Normal gameplay date | Effect |
|---|---|---|
| Ruhr expansion establishes capacity | 1850-01-01; construction window ends 1850-12-31 | Open one new coal mine at native base level, retain its full identity and flags. |
| Boom intensifies | 1851-01-01 | New mine level 32; original mines untouched. |
| Ruhr downturn | 1873-01-01 | Expansion ends, temporary downturn starts at level 8. |
| Recovery / cycle ends | 1879-01-01 | Restore saved base level and owned control bits; no forced closure or replacement. |

There are **two implemented events**, not four independently spawning factories. Opening/ramp-up belong to expansion; recovery ends the downturn. Dates and amplitudes are **proposed gameplay approximations**, not measured historical coal output or exact colliery founding dates. The Ruhr industrial breakthrough around 1850 is documented by [DHM's economic history](https://www.dhm.de/lemo/kapitel/reaktionszeit/wirtschaft/schwerindustrie); [LWL's Henrichshütte history](https://henrichshuette.lwl.org/en/history/) records industrial restructuring associated with the 1873 crisis. These support the regional narrative, not a claim that Ruhr coal output universally fell by the tested percentage or recovered in exactly 1879.

The state machine is planned → baseline establishment/active boom → intensified boom → active downturn → ended; unavailable sites or missing/lost identities cancel or defer within explicit budgets. Construction has at most **96 native attempts / six monthly batches**, a bounded region and a latest opening date. The union of real coal layouts must be clear, level and free of water, roads and houses. No terraforming/demolition commands are used. Only a mine created by this controller can be targeted, and matching original baseline IDs are conservatively refused. A lost target is not rebuilt or reassigned. No further cycles are silently queued.

## Integration and compatibility

`CyclesController` subclasses `PortsController`, retaining all **40** previous expansion rows, including eight Liverpool/Gdańsk events, the three scheduled coal events, four original managed mines and the single old-mill retirement. Phase 7E and 7F/7F.1 work is retained through ancestry `a707318` → new `feature/phase-7g-economic-cycles` branch; no reset/cherry-pick/merge was used. Blocked maritime routing was not retested.

The first runtime fixture found an inherited land-siting problem: `PortsController.SiteReason`'s `base.SiteReason` expression raises `the index 'base' does not exist` in this runtime. The new controller delegates land checks explicitly to `ProgressionController.SiteReason.bindenv(this)` and coastal checks to the existing port method. **The archived GS v5 source and candidate were not edited**; this narrow correction is active only in the new v6 package. It also matters to other land openings under v6, whose full historical matrix was not repeated.

New saves must have **schema 5 and the exact cycle contract**. Old v1–v5 GS save schemas/contracts are not adopted automatically; a separate fresh scenario is required. The inherited hierarchy temporarily views its prior schemas during validation, while the new `Save()` normalizes an accepted own root to schema 5. Refused old state is not relabelled. This logic has focused static/unit coverage and a native saved checkpoint, **not a completed engine reload test**. Accelerated fixture contracts differ from the normal 1850–1879 policy and must never be mixed.

## Actual engine observations

Four engine invocations total: one editor session, two failed headless attempts, one completed headless fixture. The failures were a Squirrel statement-termination error (fixed) and the inherited land-delegation defect (fixed). The editor initially loaded the prototype compile error; the corrected package was reloaded in the same process before the separate save. No further engine run was spent after the four-invocation budget.

The successful fixture compresses the four policy dates into **1830**, without changing the underlying industry's historical availability. It constructed **industry 542, coal type local ID 0**, at **tile 5265405 (2045,1285)**. All **542 original industry signatures** and **617 towns** were retained; final count **543**. No height changes occurred within ten tiles of the new mine. Initial candidate CITY/INDY/PATS/PSAC, all map planes and all 15 GRF references/parameters match Phase 7F exactly. Natural simulation growth/background changes are not represented as a frozen whole map.

| Settled observation (≥45 days since last level command) | GS level | Actual last-month COAL | Control flags |
|---|---:|---:|---:|
| Baseline establishment | 16 | 210 | 12 |
| Boom | 32 | 270 | 12 |
| Downturn | 8 | 63 | 12 |
| Restored native control | 16 | 135 | 0 |

These are **actual sampled quantities**, not projected annual tonnage or paid deliveries. The boom sample is 28.6% above the initial sampled baseline; downturn is 76.7% below the boom sample. They establish a real opportunity/supply change, not calibrated multipliers. Recovery restores the native *level/flags*, not a guaranteed return to the first sample's output: monthly binning, initialization and NewGRF production internals can differ; the specific reason for 210 versus 135 at level 16 was not isolated. Transitional rows are retained and labelled in [raw monthly samples](research/phase7g_production_samples.csv), not averaged into a false precise effect.

No vehicle service, cargo payment, profitability, company growth or three-human session was tested. A checkpoint was natively saved after both events ended, with schema 5 observed, but **save/reload/idempotence was not exercised** after the two concrete fixes consumed the budget. Final result was boom=ended, downturn=ended, stage=ended. Full 1850–1879 calendar progression and long-term old-mine interactions remain unverified.
