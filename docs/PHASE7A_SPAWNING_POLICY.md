# Phase 7A — Controlled industry spawning

## Verified engine behaviour

Historical AXIS 0.3.0 suppresses gameplay openings through its probability/availability callback. The same pathway is consulted by `GSIndustryType.CanBuildIndustry`, so simply retaining that veto blocks deity construction too. Simply lifting it would permit uncontrolled natural spawning. Initial fixture failures also exposed the campaign's one-industry-of-each-type-per-town rule; enlarging the test town set resolved those failures without changing campaign settings.

The verified separation is at **location callback 0x28**, whose industry resolver exposes `founder` through variable **0xA7**:

| Construction context | Founder | Opt-in result |
|---|---:|---|
| Natural random-generation helper | `OWNER_NONE = 16` | Rejected |
| GameScript deity construction | `OWNER_DEITY = 18` | Delegates to all existing location checks |
| Original policy / parameter 11 off | Existing behaviour | Unchanged |

Both natural and deity paths can have RandomCreation context. That context alone cannot identify the caller. `OWNER_WATER = 17` is not deity. The compiled candidate uses **18**, verified through successful real construction.

## Exact source change

[Build utility](../newgrfs/axis-historical-lifecycle/build_candidate.py) creates a separate source tree from prepared 0.3.0, changes numeric version 3→4 and minimum-compatible version 2→3, and adds default-off parameter 11. It leaves parameter 2's spawning flag zero in the experimental scenario. In Classic historical mode with parameter 11 enabled, availability permits the existing build path; the wrapper around `historical_location.pynml` rejects RandomCreation unless founder is deity, then calls the original historical location function.

All original dates, coast, terrain, proximity, cluster and town restrictions remain. The scheduler independently enforces individual opening dates. Player-funded construction is not turned into a scheduler event; its old native/GRF permissions remain, and it cannot invoke the new deity-only coal closure adapter. Arbitrary administrative deity tools share the engine's deity identity: authorization is a server-administration contract, not cryptographic isolation between scripts.

The five-file [source patch](../newgrfs/axis-historical-lifecycle/source-changes.patch) is reviewable. Industry recipes, cargos, IDs, layouts and base properties matched 0.3.0 across all six source economy models. This does not imply identical compiled callbacks, which intentionally differ. Only Classic historical mode was exercised end-to-end in the engine.

## Actual controls

**FIXTURE ENGINE TEST:** with original 0.3.0, deity coal `CanBuildIndustry=false`. With 0.4.0 parameter 11 off, still false. With it on, coal becomes available and two mines are constructed. Copper Refinery local ID **67**, unavailable in 1830, remains unavailable and its BuildIndustry call fails the precondition. Fishing Ground local ID 32 still rejects land. A production command below native minimum (3) fails. See the first three runs in [engine receipts](research/phase7a_engine_run_evidence.json).

**FIVE-YEAR FIXTURE ENGINE CONTROL:** original 0.3.0 and opt-in 0.4.0 each started with 47 map-generated industries at nonzero density 4. Over 1,834 calendar days, neither admitted any new unplanned industry. The opt-in run nevertheless reported deity construction available. This tests natural suppression beyond an empty-map/density-zero setting; it does not prove every possible future industry callback in all economies. [Control results](research/phase7a_natural_spawning_controls.json).

**FULL EUROPE ENGINE TEST:** the regional vertical slice added only its four named test events. All four were later physically removed; the final 542 industries matched baseline identities and no unplanned industry appeared. Existing settings were not toggled to let events through.

## Deployment and compatibility

0.4.0 retains GRFID `4B484531` and all existing IDs. This is a separately versioned candidate with an opt-in closure contract; metadata minimum compatibility is not permission to substitute it blindly into a live campaign. The experimental Europe copy was opened and saved through Scenario Editor with 0.4.0 selected and parameter 11 enabled; the original scenario/GRF were never changed.

Existing production saves require an explicit, tested migration and matching saved GS ledger. A missing ledger after the first scheduled event refuses bootstrap. Do not add the script mid-campaign expecting it to infer prior closures. Do not install two same-GRFID candidate versions into one testing profile. All multiplayer clients require the exact 0.4.0 GRF checksum; the server owns GS execution. No engine rebuild is required.

Stock source receipts are retained for `script/api/script_industrytype.cpp`, `industry_cmd.cpp`, `newgrf_industries.cpp`, `company_type.h` and callback constants in [source receipts](research/phase7a_engine_source_receipts.json). The probability callback cannot independently distinguish natural and deity requests; the founder-aware location check is the essential mechanism.
