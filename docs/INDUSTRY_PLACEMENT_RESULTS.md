# Phase 6B industry placement results

**467 industries, 40 types, 617 preserved towns.** The 0.3.0 copper/salt
candidate is an actual separate scenario, not a placement list.

## Delivered local files

| File | Purpose | SHA256 |
| --- | --- | --- |
| `C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.3.0 Candidate - Industrialized.scn` | Current 467-industry candidate | `b05ef51a3bd17eb453d6b5e4af544c0745fee372a6195f5354ab8bd927ce6e75` |
| `C:\Users\Kladd\Documents\OpenTTD\newgrf\axis-historical-europe-0.3.0-candidate.grf` | Matching separately named GRF | `f0da622873c91107fa4d2b768d88cd95d5db009c2b2975bdb6d7ab6caaed3c33` |
| `C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.2.0 - Industrialized.scn` | Preserved earlier 438-industry working version, without new copper/salt processors | `728069c6bed1e6e8c4cf40fba88fc25a0f224ddd4832b893cf98989687a73169` |

The Phase 6A Coastal Towns source and both original/current GRF versions remain
separate. The normal OpenTTD configuration was not edited. Binary artifacts
are local and excluded from Git. Exact delivery metadata is in
[the delivery manifest](research/industrialized_scenario_delivery.json).

## Actual construction method

JGRPP 0.73.4 executed supported GameScript industry-funding commands on isolated,
paused copies. Every requested type was checked against the source's 1830
policy; editor bypasses of introduction restrictions were not used.

Construction copies temporarily allowed raw funding and used industry-platform
margin zero, with a fixture-company construction grant. Margin zero does **not**
disable terraforming by itself. Candidate-site flatness checks and post-save
height comparisons enforce the preservation requirement. The campaign's raw
funding/platform values were restored and its complete original settings chunk
retained in delivered files. The construction company and grant are not in the
delivered scenarios and are not evidence of starting-company affordability.

The initial insufficient-funds diagnostic placed 93 sites and was discarded
as a candidate. With sufficient fixture funds the accepted 0.2.0 pass placed
438. The separately validated 0.3.0 copy added 18, then 11 more at refined
coastal candidates. Completed industry sites were not retried or relocated.

Only engine-created industry, persistent-storage, animation, industry station
and map records were promoted. The named U8 `founder` field was normalized to
neutral OWNER_NONE (16), rather than leaving the disposable company's owner.
No production statistics, cargo amounts or vehicle properties were patched.
All scenario framing is parsed and reconstructed with the known JGRPP table
schemas, and every resulting candidate was loaded and saved by the real engine.
The 0.3.0 NewGRF row came from a fresh engine-generated registration save, not
an invented checksum. No existing file's NewGRF configuration was edited in place.

## Requests and failures

The complete plan has **708 distinct requests: 467 placed and 241 failed**.
Retries do not count as additional industries or additional planned sites.
[The result CSV](research/industry_placement_results.csv) records IDs, tiles,
coordinates, localities, nearby towns, source links, attempt counts, last API
errors and raw engine-case paths.

| Failed category | Requests | Explanation |
| --- | ---: | --- |
| General Store 61 | 59 | Requires existing house tiles |
| Hardware Store 57 | 56 | Requires existing house tiles |
| Food Market 59 | 48 | Requires existing house tiles |
| All other types combined | 78 | Bounded candidate search, occupied/unsuitable land, coast/layout or NewGRF siting rejections |

JGRPP `industry_cmd.cpp` explicitly requires HOUSE tiles for `OnlyInTown` and
clears them during construction. Those 163 retail placements were therefore
not forced: replacing houses would change the preserved towns/populations.
The source town-center probes did not supply FOOD/GOOD acceptance. These cargos
use the implemented ports/wharves instead; local retail remains a limitation.

Remaining copper/salt-specific failures include Allihies (no qualifying bounded
flat footprint), Gwennap and Neath (last API error `ERR_UNKNOWN`), and the Aveiro
Salt Evaporator (`ERR_SITE_UNSUITABLE`). The exact custom rejection behind
`ERR_UNKNOWN` is not decoded. Nearby bounded options were tried, without
altering the terrain or moving to another historic region. Seven additional
wharf requests also remain failed. None is reported as an operating industry.

## Preservation and engine round trips

[The validation manifest](research/industrialized_scenario_validation.json)
records the complete checks and raw case paths:

- All **617 complete town rows** are bit-identical to the Phase 6A baseline,
  including the four added port towns, names, coordinates and populations.
- All **438 previously completed industry rows** are bit-identical after upgrade
  and new placement.
- Terrain-height changes: **0**. Protected road/bridge/house/object changes: **0**.
- Changed map tiles: **4,944**. Industries occupy **527 original water tiles**;
  these are industry-owned coastal footprints, not deliberate filling or
  terrain changes. Remaining water metadata changes are not represented as
  bit-identical source water bytes. Water can only remain water or become an
  industry/industry-station tile under the guard.
- Calendar remains **1 January 1830**; original economy date remains **1800**.
  The complete original settings and seven-tile train limit are preserved.
- All **15 intended GRF identities** are retained; only Historical AXIS's
  separately versioned candidate checksum/version changes. The other 14 full
  references and all parameter vectors match the source.
- Actual Scenario Editor load, save and reload succeeded. The GUI-saved copy's
  town/industry/NewGRF records and **all map arrays** equal the candidate.
- Two subsequent gameplay load/save round trips retained the same records and
  map arrays, with **467 instances, 96 registered types and 64 cargos**.

Combined headless load/probe/exit-save runs took **12.687 s** and **10.125 s**
on this PC. These are combined harness timings, not separately measured load
and save benchmarks or multiplayer performance guarantees. There was no crash
in the recorded placement, movement and persistence tests.

## Reproduce

See the [candidate build instructions](../newgrfs/axis-historical-copper-salt/README.md).
Scripts require the recorded local assets; they do not download rolling stock.

1. Extract source rules with `scripts/industrial_phase6b_rules.py` and its
   `--candidate` variant, using the pinned build environment.
2. Generate the base plan with `industrial_phase6b_plan.py`; place with
   `industrial_phase6b_place.py`; clean with `industrial_phase6b_candidate.py`.
3. Register the compiled candidate, run its production/persistence controls,
   then `industrial_phase6b_migrate_candidate.py` to a new copy.
4. Generate additions with `industrial_phase6b_plan.py --additions`, place with
   `industrial_phase6b_place.py --additions`; retain that pass's plan/candidate
   manifest before a bounded `--additions --retry` pass.
5. Run `industrial_phase6b_results.py`, route tests and
   `industrial_phase6b_final_validation.py`. The GUI editor round trip is a
   separate recorded computer-use operation, not simulated by that script.
6. `industrial_phase6b_deliver.py` requires matching validation and reproducible
   build evidence. It refuses to overwrite any differing existing file.

The ignored `.work/industrial6b/` directory retains raw scripts, configs, logs,
preliminary failures and saves. Committed datasets preserve results and source
paths, rather than redistributing the user's other GRFs.

Request order and bounded site lists are reproducible. The supported GS build
API chooses layouts using engine/script randomness; the logs record each actual
success and attempt count. Bit-identical placement replay across different
startup contexts has not been established. This is distinct from the verified
bit-identical GRF rebuild.
