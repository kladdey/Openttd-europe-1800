# Industrialized scenario readiness

**READY WITH CAVEATS for an 1830 multiplayer playtest.** An actual separate
467-industry scenario is delivered and tested. **Not certified for an unattended
1830–2025 campaign:** neutral future-industry progression is still blocked by
the preserved spawning policy. Historical site review and inland final markets
also remain unresolved.

## Open this candidate

`C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.3.0 Candidate - Industrialized.scn`

The separately named matching GRF is already available under
`C:\Users\Kladd\Documents\OpenTTD\newgrf\axis-historical-europe-0.3.0-candidate.grf`.
Do not add a second Historical AXIS entry or replace GRFs in an existing save.
Keep the original 0.2.0 version for its existing scenarios. A preserved earlier
438-industry 0.2.0 Industrialized file is also available, but does not contain
the new copper/salt processing types.

The current candidate has **617 towns, 467 industries of 40 placed types, 96
registered industry types, 64 cargo types and 15 GRFs**. The source calendar
start is **1830**, the economy clock remains **1800**, and the seven-tile train
limit and infrastructure maintenance remain enabled. Inflation remains off.
No original scenario, save, NewGRF binary, town, vehicle or normal configuration
was overwritten. All 438 earlier industry records were preserved.

## Evidence supporting the playtest

- Actual Scenario Editor load/save/reload and two subsequent gameplay
  load/save round trips, retaining all town/industry records and map arrays.
- Zero terrain-height or protected road/house/object changes against Phase 6A.
  Coastal industry-owned water footprints are documented, not hidden.
- Real loaded and paid Europe-map coal deliveries in Britain and the Ruhr,
  plus grain, timber, ore, salt, coastal fish, passengers and mail.
- Controlled complete copper smelting and salt-curing output deliveries,
  missing-input negative controls and persisted stockpiles.
- Reproducible compilation from a complete local source ZIP to the identical
  candidate GRF hash. Original enabled recipes and all cargo assignments are
  preserved, verified across all six economies.

The construction and transport fixtures used grants to isolate functionality.
They do **not** prove starting-company profitability, capital recovery or fair
competition in the new industry geography. Earlier phase results cannot be
carried over as measured profits for these changed routes.

## Three starting-region assessment

| Region | Verified opportunities | Limits / first human test |
| --- | --- | --- |
| Britain | 118 industries, London passenger/mail deliveries, Lancashire coal, multiple ports/wharves, Swansea copper chain nodes | Run a realistic-budget coal or passenger service; test Cornwall/Parys ore shipping and Swansea output export |
| Western / Central Europe | Ruhr coal delivery observed; Belgian, German and Central European farm/forestry/industrial chains present | Compare an inland feeder and industrial rail start; inspect goods/food access to distant ports |
| Eastern / Southern Europe | Upper Silesian ore and Bochnia salt deliveries observed; Tagus grain delivery observed; agriculture, livestock, forestry and maritime nodes | Test one realistic-budget regional farm route plus a food/industrial export connection; long final-market distances matter |

This is evidence of opportunities and functioning cargo acceptance, not three
financially equivalent starts or a new company-growth simulation. Historical
regional differences are intentional; economic viability needs playtesting with
actual starting cash/loans and competition. No subsidies are in the scenario.

## Priority actions

| Priority | Issue | Smallest next action | Confidence |
| --- | --- | --- | --- |
| MAJOR for 1830–2025 | Spawning-disabled callback blocks deity GS construction too | Agree a separately tested progression policy before committing to 2025; do not rely on an untested scheduler | High, actual API rejection plus source |
| MAJOR historical caveat | Four inherited soda-ash mines have unverified 1830 mineral geography | Research or explicitly replace/defer these sites in a separate reviewed correction; completed placements were preserved here | High that evidence is missing; not a claim that every location is impossible |
| MAJOR market caveat | No local retail due strict town/house preservation; FOOD/GOOD often require long export trips | Test inland starts and decide how local retail may be introduced without silently changing the frozen baseline | High, failed construction and graph distances |
| MINOR for initial playtest | Aveiro salt pans, Allihies, Gwennap, Neath and seven wharf requests failed | Review bounded sites manually; do not terraform or claim them implemented | High on failure, mixed on exact rejection cause |
| MINOR | Full new copper/curing chains not all run on Europe geography | Human-run Cornwall/Parys–Swansea–wharf and mine–curer–food market routes | High |
| OPTIONAL | Generic graphics, broad regional factory/farm proxies | Historical visual/site refinement after the economy works | Medium |

No pricing, performance, dates, seven-tile limit or existing recipes were changed
to compensate for any issue. No pushes or merges were performed.

## First session for Kladdey, Squirrel and Toni

1. Each load the same **0.3.0 candidate** and verify the matching GRF checksum.
   Start a disposable multiplayer save, preserving the delivered scenario.
2. Select distinct British, mainland-industrial and agricultural/maritime starts.
   Use normal starting cash/loans. Record infrastructure/fleet investment and
   two complete economy years of delivered cargo, income and maintenance.
3. Include a short horse feeder, a first seven-tile-or-shorter railway and a
   coastal freight service. Verify loading, acceptance and actual credited money.
4. One player should test salt plus fish/livestock and FOOD export. Another should
   test ore/coal/sand at Swansea and COPR export. Missing inputs should stockpile,
   not produce free output. Do not interpret SLAG as a missing required payment.
5. Compete briefly at one producer or passenger corridor. Record rating/share
   effects and whether the inland player has a practical final market.
6. Save/reload the multiplayer session and compare towns, industries and active
   services. Review the progression policy before making it the long-term campaign.

Detailed [placement](INDUSTRY_PLACEMENT_RESULTS.md),
[chain validation](INDUSTRY_CHAIN_VALIDATION.md),
[historical geography](HISTORICAL_INDUSTRIAL_GEOGRAPHY.md) and
[copper/salt validation](COPPER_SALT_1830_VALIDATION.md) separate observed results
from source-derived coverage, inferred geography and untested economic claims.
