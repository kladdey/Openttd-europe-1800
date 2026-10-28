# Historical industry feasibility — Europe 1830–2025

Investigation: 2026-10-28. **Verdict: PARTIAL with GameScript alone.** Scripted
openings, regional placement and announcements are supported. Enforced historical
availability for every construction route, forced retirement, and removal of the
existing anachronistic industries are not supported by ordinary GameScript APIs.
The existing playable scenario remains untouched; its 1830 start is the target.

## Scope, evidence and version pins

Read `ECONOMY_VEHICLE_OVERHAUL.md`, `PROJECT_STATUS.md`, geography workflow and
V12 import notes before designing this system. Those older economy notes describe
AXIS as a candidate and an 1800 start; the user's current report supersedes them
for this investigation: AXIS 2.3.1, Extreme Classic, 1830, about 1,387 industries,
three humans and JGRPP 0.73.4. That scenario/NewGRF configuration was **not supplied
as a newly verified save**. No claim is made that a committed older scenario is
the user's current map. No existing project status or scenario has been rewritten.

Primary source checkouts inspected locally:

* **JGRPP 0.73.4**, tag `jgrpp-0.73.4`, commit
  `cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8`.
* **AXIS 2.3.1 release**, commit
  `11c8353ccf7444b143e57080b1aa2b5e38839a23` (release commit, not repository HEAD).
  [BaNaNaS package metadata](https://bananas.openttd.org/package/newgrf/4a4b8808)
  independently identifies 2.3.1, GRFID `4a4b8808`, uploaded 2026-02-08 and partial
  MD5 `b580ae20`. Full installed binary hash/parameters remain to be captured.
* Upstream OpenTTD **15.0** industry and industry-type headers were fetched and
  compared for the principal APIs. Do not confuse today's online API reference
  with the pinned patch-pack implementation.

Source key (links pin the relevant code):

| Key | Source and relevant symbols |
|---|---|
| J1 | [JGR industry-type header](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/script/api/script_industrytype.hpp): `@api ai game`, `BuildIndustry`, cargo getters, `ResolveNewGRFID` |
| J2 | [JGR industry-type implementation](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/script/api/script_industrytype.cpp): deity availability uses `RandomCreation`, default probability 1 |
| J3 | [JGR industry header](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/script/api/script_industry.hpp): queries, control flags, production setter; setters marked `@api -ai` |
| J4 | [JGR industry commands](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/industry_cmd.cpp): `ClearTile_Industry`, `CmdBuildIndustry`, generation probabilities, `ChangeIndustryProduction` |
| J5 | [Probability callback implementation](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/newgrf_industries.cpp): `GetIndustryProbabilityCallback`, `IndustryProductionCallback` |
| J6 | [Game settings API](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/script/api/script_gamesettings.cpp), [density settings](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/table/settings/difficulty_settings.ini), [economy settings](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/table/settings/economy_settings.ini) |
| J7 | [Tile API implementation](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/script/api/script_tile.cpp): `DemolishTile` delegates to `LandscapeClear` |
| J8 | [Type enumeration](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/script/api/script_industrytypelist.cpp), [industry lists](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/script/api/script_industrylist.hpp) |
| A1 | [AXIS parameters/header](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/templates/header.pynml), [availability callback](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/templates/availability.pynml), [English parameter names](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/lang/english.lng) |
| A2 | [AXIS industry model](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/industry.py), [numeric IDs](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/global_constants.py) |
| A3 | [Extreme Classic economy](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/economies/basic_temperate.py), [economy order](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/economies/__init__.py) |
| A4 | [Primary production](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/templates/produce_primary.pynml), [secondary production](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/templates/produce_secondary.pynml), [secondary callbacks](https://github.com/EmperorJake/AXIS/blob/11c8353ccf7444b143e57080b1aa2b5e38839a23/src/templates/industry_secondary.pynml) |

## A. Creation and inspection

**Yes, at a selected tile, conditionally.** `GSIndustryType.BuildIndustry(type,
tile)` is exposed to **game**, not inferred from AI availability. In deity mode,
`CanBuildIndustry` checks the NewGRF random-creation availability callback;
construction still checks enabled type, layouts, terrain, proximity, town and
other NewGRF location rules. All enabled AXIS types can be addressed through the
same API; that does **not** mean all can be built in 1830, with every parameter,
at an arbitrary tile, or even somewhere on this particular map. Use bounded
attempts and handle failure. Primary-industry player construction settings do
not restrict deity placement (J1–J5).

`GSIndustryTypeList()` enumerates enabled industry specifications, **not only
currently buildable ones**. `GetAcceptedCargo` / `GetProducedCargo` give default
cargo lists; the API explicitly warns that construction callbacks may change
them. They do not expose production recipes, mandatory/optional relationships,
or GRF parameters. Use the pinned AXIS source for recipes, then validate live
instances. Resolve identity with `ResolveNewGRFID(0x4A4B8808, local_id)`; game-local
type IDs and translated display names are unsuitable stable identifiers (J1,J2,J8).

`GSIndustryList`, `GSIndustry.GetIndustryType`, `GetLocation`,
`GetLastMonthProduction`, `GetLastMonthTransported`, `GetStockpiledCargo`,
`IsCargoAccepted` and `GetProductionLevel` support inventory and monitoring.
`GSCargoList_IndustryAccepting` / `GSCargoList_IndustryProducing` support
instance cargo inspection. `GetProductionLevel` is an engine level, not a
complete account of AXIS's supply bonus/internal production state (J3,A4).

**Ownership is limited:** there is no `GSIndustry.GetOwner` or founder getter
in this pinned API. Engine `Industry` has separate `owner` and `founder` fields;
industries normally remain neutral even when funded. Exclusive supplier/consumer
rights can be queried, but are not ownership. See [engine structure](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/industry.h).

**Geographic regions are project data, not an API fact.** Locations are tiles;
the engine has no concept of Britain, Ruhr or Silesia. Region membership becomes
reliable only after calibrated tile polygons/resource sites are validated
against the actual scenario. See the coordinate safeguards below.

## B. Removal, prevention and runtime control

| Requirement | Verified result in JGRPP 0.73.4 |
|---|---|
| Close/remove an existing industry via dedicated GS method | **No such method** in J3. No `CloseIndustry` or `RemoveIndustry`. |
| Bulldoze it using `GSTile.DemolishTile` in normal deity mode | **No**: J7 reaches J4's `ClearTile_Industry`, which requires editor mode, water destruction or magic-bulldozer cheat. Deity has no ordinary bypass. |
| Force closure by `SetProductionLevel(id, 0, ...)` | **No**: API accepts levels **4–128**. Setting 4 is not a guaranteed closure, and the setter enables external production control. |
| Remove via an industry-close event | **No**: events report changes; they do not command or veto them. Flooding or cheats are not an acceptable historical control mechanism. |
| Per-type/year veto for natural spawning | **No GS type-availability setter/hook**. A script can refrain from building its own types, but cannot veto the engine's construction. |
| Per-type/year veto for player funding/prospecting | **No GS pre-construction veto**. An open event is already too late; exclusive cargo rights do not stop construction. |
| Override introduction/expiry dates or edit AXIS parameters at runtime | **No**. `GSGameSettings` edits engine integer settings, not arbitrary NewGRF internals. NewGRF callbacks remain authoritative. |
| Suppress automatic openings globally | **Yes, configuration**: `difficulty.industry_density=0` (**Funding only**, enum `FundedOnly`). J4 generation paths return early/zero; deity `CmdBuildIndustry` is not gated by this density check. Preserve AXIS spawning permission, below. |
| Globally forbid player funding of all industries | No complete GS control identified. `construction.raw_industry_construction=0` only forbids player **raw** construction; secondary funding remains. |
| Suppress closure globally/per type | **Yes, by applying an instance flag to all relevant instances**: `SetControlFlags(id, old_flags \| INDCTL_NO_CLOSURE)` in deity mode. Repeat for new industries. No global/per-type flag setter; cannot rescue an already announced closure. |
| Suppress natural production changes | Per-instance `INDCTL_NO_PRODUCTION_DECREASE` / `INCREASE` and `INDCTL_EXTERNAL_PROD_LEVEL` exist. Do not assume they override AXIS's own cargo callbacks/internal registers. |

Sources: J1–J7. Production/closure controls are **standard GS APIs**, also present
in [OpenTTD 15.0 industry header](https://github.com/OpenTTD/OpenTTD/blob/15.0/src/script/api/script_industry.hpp).
Construction, enumeration and stable NewGRF resolution likewise exist upstream
in the [15.0 type header](https://github.com/OpenTTD/OpenTTD/blob/15.0/src/script/api/script_industrytype.hpp).
They must not be advertised as unique JGRPP extensions. In contrast,
`economy.spawn_primary_industry_only` is marked `SettingFlag::Patch` in J6;
it is a broad JGRPP class filter, not a per-sector/year filter.
`economy.industry_event_rate` has minimum **1**, so setting it to zero is not a
supported way to freeze events. Neither setting solves player funding or retirement.

### Critical AXIS parameter interaction

AXIS's confusingly named internal `restrict_open_during_gameplay` is the UI
**Allow industries spawning during gameplay**, parameter 2 **bit 2** (A1).
False/default blocks random construction; true permits it. Deity GS uses
`RandomCreation` (J2,J4), so **turning this AXIS option off also blocks deity GS
construction**. Recommended test combination:

* AXIS allow-spawning **on**; engine density **Funding only**.
* GS in default deity context places only scheduled industries.
* Multiplayer agreement prohibits unscheduled player-funded secondaries;
  optional raw-industry funding restriction is only a partial guard.

This is a source-supported route, **not an in-game validated configuration**.
AXIS types with `prob_in_game=0` are not automatically impossible to script:
J2/J4 invoke availability with default probability **1**, while the natural
generator uses its own property weights. A callback returning “use property”
(`0x100`) preserves the caller's supplied default (J5). Always test
`CanBuildIndustry`, rather than rejecting a type solely on that property.

AXIS has source-level intro/expiry years and availability callbacks, but no
exposed per-type historical-date parameter. Most Classic types have no date
gate; examples that do are plastics (1900), offshore rigs (1967), recycling
plants (1978), machine shops (1790). Graphics-change dates are **not** introduction
dates. Expiry restricts **new construction**, not guaranteed removal of existing
instances. Scenario-editor bypass comments must be read cautiously: the AXIS
date switch wraps its game-mode switch; engine editor construction bypasses the
ordinary availability test in J4. Verify the editor UI separately.

## C. Safe scenario initialization options

| Option on a disposable copy | Viability and drawbacks |
|---|---|
| Manually bulldoze inappropriate industries in Scenario Editor | Supported by J4. Save under a **new filename**, preserve 1830 and all NewGRFs. Best first candidate from the reported 1,387-industry layout. Removal may break suppliers/customers; inventory before deleting. |
| Lower density when generating a fresh map | Supported, but reduces counts rather than selecting historical types. On an existing scenario it does not remove the saved industries. Regeneration would discard hand placement. |
| Empty/few-industry scenario plus scripted openings | Supported in principle. Funding-only world generation creates no ordinary industries; editor generation has separate behavior (J4). Do not assume an editor density change retroactively empties the map. Requires tested sites and an initial chain package; not recommended as the first migration. |
| AXIS parameters alone | Economy selection, supply bonus/threshold, coastal distance and broad spawning permission exist (A1); no historical-sector timetable. Turning off spawning conflicts with deity placement. |
| Funding-only density plus script | Most promising unmodified route. Stops natural openings, leaves saved industries and player secondaries intact. Must test on the exact save and after reload. |
| Dates or a historical AXIS variant | Stronger enforcement, but requires a custom NewGRF and a new disposable scenario built with it. Never hot-swap an industry economy in the working save. |

A scenario stores existing industries. Neither reducing density nor future
availability/expiry automatically purges them. Engine save/load explicitly
serializes the industry records, control flags and founder in
[industry_sl.cpp](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/saveload/industry_sl.cpp).
Starting an editor-authored scenario does not reconstruct it from scratch under
the current date gates. This behavior still needs an editor→game smoke test.

Do not rely on starving AXIS industries to retire them. The inspected primary
and secondary templates return `CB_RESULT_IND_PROD_NO_CHANGE` for random
production changes (A4); ordinary engine decline assumptions do not transfer
automatically. Primary output explicitly multiplies by `production_level`,
so the GS setter has a source-supported scaling effect there. Secondary
delivery recipes calculate output differently; measure their response rather
than promising uniform boom/decline control.

No global requirement for every AXIS type to exist was found in the inspected
generation/production code. Missing types need not make the engine fail, but can
leave cargoes commercially unusable. Location checks can depend on nearby
industries; some plants may require a cluster before they can be placed (A2).
Thus “no technical requirement for every type” is **not proof of playable chains**.
Ports supply advanced goods as well as historical commodities: they are an
explicit gameplay compromise, not evidence of 1830 electronics production.

## D. Progression, geography and scale

| Feature | Feasibility |
|---|---|
| Year-based openings and sector events | Yes for script-controlled construction, within NewGRF permission. A script “unlock” does not unlock/lock the player's funding menu. |
| Region weighting and expanding clusters | Yes with project-authored polygons, vetted resource sites, quotas and candidate queues; placement failures remain normal. |
| Booms/declines | More sites and reduced future investment are feasible. Engine production setters exist, but AXIS supply/recipe effects must be tested. Forced shutdown, conversion or replacing a type in place is not supported. |
| Resource-dependent siting | Geological/resource catalogue plus terrain/proximity checks. There is no general GS coal-seam map or historic deposit API. Ordinary land is not proof of a resource. |
| Multiplayer notices | `GSNews.Create` with `COMPANY_INVALID` targets all companies; use `NT_ECONOMY` or `NT_GENERAL` and a tile/industry reference. Story pages can hold a durable development ledger. |

News signature is verified in [script_news.hpp](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/script/api/script_news.hpp).
Use shared announcements and equal information for all three companies.

**Timekeeping trap:** in this exact patch pack, `GSDate.GetCurrentDate()` reads
`EconTime::CurDate()`, not a separately exposed calendar date. See
[script_date.cpp](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/script/api/script_date.cpp).
Require calendar-based timekeeping (`economy.timekeeping_units=0`) for the first
system. Wallclock mode decouples historical and economy time; do not silently
schedule history against its economy year. A separately verified clock solution
or new API is needed before supporting that mode. Calendar freeze/slowdown and
JGR day length must be included in testing.

### Coordinate safeguards

The repository's town imports and [geography workflow](GEOGRAPHY_WORKFLOW.md)
provide calibration evidence, not an authoritative GIS projection for the new
scenario. The existing transformation is empirical and the original DEM CRS is
unknown. Do not invent Ruhr/London/Silesia coordinates or assume image pixel Y
equals tile Y. Establish a scenario fingerprint (dimensions, hashes, NewGRF
manifest, independent landmark tiles). Register region polygons against actual
town positions and coastlines in that scenario, test orientation/axis conversion
with several widely separated landmarks, and visually approve border samples.
Classify industry anchor tiles with documented border rules; large footprints
may cross boundaries. Reject an unknown scenario fingerprint. Keep candidate
sites and regions in a separate versioned data module.

### Performance and persistence architecture

A 4096² map has **16,777,216 tiles**. Avoid full-map script scans, synchronous
prospecting loops and per-tick industry×cargo×region loops. A 1,387-industry
snapshot is modest if chunked: type/cargo metadata once, instance index by region
and type, open/close events plus periodic reconciliation. A full 64-cargo sweep
would be 88,768 queries; spread work over ticks and query relevant cargoes only.
At most a small fixed number of placement commands per scheduling interval;
cache rejected candidates with cooldowns and never retry an impossible region
forever. Built-in prospecting can try **5,000 locations and layouts** inside one
command (J4), so selected-site queues are preferable for geography and latency.

Modular design: (1) version/economy manifest and identity resolver; (2) extracted
cargo/recipe catalogue; (3) validated regions/resources/sites; (4) historical
policy and chain planner; (5) bounded placement queue; (6) event inventory,
notifications and save schema. Default to observation, then opt into placements
in a disposable copy. Never give the script filesystem scenario-editing duties.

GameScript runs authoritative game commands through the server; construction
uses command seeds for desync-free randomization in `CmdBuildIndustry` (J4).
Use GS randomness only with persisted scheduling decisions; no OS clock/network
inputs. Stable sorting, saved phase/event IDs, candidate/retry cursors and
successful site records prevent duplicate openings. Implement `Save()`/`Load()`,
version migrations and reconciliation of stored industry IDs (IDs can be reused).
Store type/site identity as well as ID. Test save during queued construction,
reload, server restart and client join. Source support is not a multiplayer
performance benchmark; a 195-year accelerated soak remains mandatory.

## Recommended approach and modification boundary

For the upcoming playtest, preserve the working scenario. Make a separate 1830
candidate, manually prune anachronistic plants, validate a small set of early
chains, use funding-only density with AXIS spawning permission enabled, and add
a small additive GS scheduler. Human agreement handles premature funding. Model
decline initially by ending new investment; do not promise forced closures.

For **strict enforcement**, build a separately versioned historical industry
NewGRF/AXIS-derived economy that gates construction dates and production recipes
consistently for random, funded and prospected construction. An unrelated small
add-on is not assumed able to override AXIS callbacks safely. That is a custom
NewGRF project with compatibility/licensing review and a fresh scenario, outside
this task's no-AXIS-modification boundary.

An **engine patch** is needed if the requirement is to keep the existing AXIS
binary unchanged while adding authoritative per-type/year construction vetoes,
a GS closure/removal command, explicit production/retirement controls independent
of NewGRF callbacks, or missing ownership/calendar-query functionality. Such
commands need multiplayer synchronization, permission semantics, save versioning
and tests. A patch is not required for additive scheduled placement.

## Tests performed, risks and unanswered questions

Performed: pinned source review; upstream-header comparison; executed the AXIS
Python metadata extraction (91 enabled Classic types, 64 cargo slots); checked
unique local IDs and coal-mine mapping; static POC API-symbol checks and Git
whitespace/diff review. Extraction uses upstream model methods with no-op renderer
and messaging dependencies; **no GRF compilation or binary decompilation**.
The [matrix](AXIS_INDUSTRY_MATRIX.md) separates extracted facts from design policy.

**Not performed:** Squirrel compilation, script loading, industry construction,
Scenario Editor operation, AXIS binary equivalence verification, three-player
join/rejoin, save/reload or long-run performance tests. The POC is written source,
not a demonstrated working GameScript. No scenario, NewGRF or map was modified.

Outstanding gates:

1. Capture the actual 1830 scenario/AXIS binary hashes, all parameters, timekeeping
   settings and current industry inventory; reconcile the older repository notes.
2. Confirm funding-only + AXIS allow-spawning works through save/reload and does
   not seed automatic industries. Test manual raw/secondary funding separately.
3. Measure whether `SetProductionLevel` has the intended effect on each AXIS
   class; callbacks use their own state, and zero is not allowed. Do not schedule
   historic contraction through this setter until measured.
4. Validate the coordinate transform, selected sites and supply chain throughput
   with the actual early vehicles. A cargo graph alone cannot prove transportability.
5. Decide whether modern-output ports, early machine-shop recipes and voluntary
   funding rules are acceptable compromises. If not, custom NewGRF work is a
   prerequisite, not an optional polishing step.

See [roadmap](HISTORICAL_INDUSTRY_ROADMAP.md) and
[isolated probe instructions](../prototypes/historical_industry_poc/README.md).
The [verification record](research/HISTORICAL_INDUSTRY_VERIFICATION.md) records
the exact local checks and limitations.
