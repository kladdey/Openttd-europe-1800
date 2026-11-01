# Phase 7H — industrial transformation implementation

## Gate completed before expansion

Work started at local `80b6325`, retaining Phase 7G `4c22a58` and earlier 7E/7F/7F.1 ancestry, on `feature/phase-7h-industrial-transformation`. No reset, merge or push was used.

The first **two native invocations** reused the exact Phase 7G accelerated policy, saving a fresh active-boom checkpoint at 1830-06-15 and reloading it through downturn/recovery. Native loaded data showed **schema 5, stage=boom, target 542**, last change 668485. Mine identity remained **tile 5265405 / birth 668401**. Across both runs there was exactly **one construction, one baseline command, one boom command, one downturn and one restoration**. Reload emitted no new construction or repeated boom. The final state was ended/ended, level 16, flags 0, **543 industries / 542 originals / 617 towns**.

Relative to uninterrupted 7G, the resumed downturn command occurred at day **668575** rather than 668576; restoration at **668668** rather than 668667. Both are at or just after the policy threshold within the short polling/command cadence; this is not duplicate or prematurely replayed scheduling. No gate repair was needed. Only after this gate passed was the new transformation controller implemented.

## Exactly two new events

The old 40 expansion/port rows, Ruhr cycle, four-original-mine depletion and single-mill policy remain unchanged. New definitions are in `transformation_policy.json`; native cargo/type properties come from the pinned AXIS 0.6.0 matrix. No new cargo or industry type was introduced.

| Event | Normal approximate dates | Region / native type | Conditions and actual mechanism |
|---|---|---|---|
| `lancashire_textiles` | Open 1840; expire unbuilt after 1845 | Manchester/Lancashire; Textile Mill **local 42** | Require a FICR producer and GOOD accepter within 160 tiles. Legally construct one neutral mill in a 24-tile search around (2966,968). Construction completes the event; the facility then operates natively. |
| `silesian_transition` | Establish a pilot site 1975–1980; decline 1991; retire 2000 | Upper Silesia; Coal Mine **local 0** | Require a nearby COAL consumer within 160 tiles and a registered ENSP producer (global import/supply opportunity). Construct and track **one new mine**, protect it while active, reduce level 16→8 at the warning, then request the existing authorized new-mine closure callback at level 4. Physical removal, not the command alone, ends the event. |

The late mine is a **fictional regional capacity proxy**, not a named historical colliery, and its 1975 establishment is part of the same finite decline/retirement event. Original mines are never selected as targets. ENSP is a native optional supply input; no nearby ENSP producer is invented, and no delivery is forced. Neither event changes company funds, prices, ownership, exclusive service or routing.

The Lancashire mill uses native **FICR/COAT → TEXT/GOOD**. Existing local fibre producers include sheep farm 85 and ranch 175; furniture factory 215 accepts TEXT nearby and existing retail accepts GOOD. Generic AXIS FICR is a fibre/wool abstraction, **not evidence of an actual historical cotton-import service**. The fixture verified native acceptance/output registration, not a delivered textile recipe. Its production samples were zero without input services.

Local Silesian consumers include coke oven 407 and brick works 390/391. The actual late-site fixture location was (749,1494), near map town Katowice (729,1480); the textile site was (2970,978), near Manchester (2950,952). These are town-calibrated regional placements, not asserted factory plot locations.

Historical context: [Manchester City Council's Ancoats history](https://www.manchester.gov.uk/parks-leisure-and-the-arts/parks-playgrounds-allotments-and-open-spaces/conservation-areas/introduction24/ancoats-and-its-building-today) documents concentrated early industrial mills; the [Science and Industry Museum's Salford account](https://blog.scienceandindustrymuseum.org.uk/celebrating-salfords-centenary/) describes fibre processing, transport and regional industry. For Poland, the [World Bank's coal restructuring record](https://documents1.worldbank.org/curated/en/299031468763193315/pdf/290700PL.pdf) documents the 1998–2002 reform program. **1840/1975/1991/2000 and the level cut are proposed scenario approximations**, not sourced exact founding, closure or tonnage claims.

## Mechanism, safety and persistence

`TransformationController` extends the existing `CyclesController`. It adds a two-row persistent ledger, not another competing GameScript or a repeating expansion queue. Rows are planned → active → ended/cancelled; factory construction ends its opening row, while the coal row moves operating → declining → closing → retired. Ended rows never rebuild missing facilities. Lost active identities cancel without touching a reused ID.

Native `BuildIndustry` checks remain mandatory. The inherited full-layout, level-ground screen rejects water, houses, roads and occupied tiles. Searches stay within the named region, with **96 native attempts / six monthly batches** and an explicit expiry date. Prerequisite checks use real registered labels. Missing resources/sites defer or cancel; they never cause demolition or relocation to another region.

Only a newly captured full **ID/type/tile/birth** signature is controlled. Every original baseline signature is protected. The coal site uses supported deity `SetProductionLevel`; no cargo or revenue is injected. The unmodified AXIS `lifecycle_coal_closure` callback only accepts the opt-in historical/basic economy, **founder 18** (GS/deity-founded) and level 4. The controller clears its own no-closure flag only after the warning date. This is distinct from, and does not change, the guarded original-mine handshake. If native removal fails for 180 economy days, capacity/control are restored and the row cancels rather than retrying indefinitely.

The package is separately versioned **GS v7/schema 6**, with exact transformation and inherited policy contracts. Old schema-5 running saves are refused before parent initialization; no automatic migration is supplied. Accepted own schema-6 data temporarily uses inherited schema views during validation, while `Save()` normalizes its own root to 6. Refused old data is not relabelled. The normal candidate and accelerated fixture have different contracts and cannot be mixed.

Public news announces new opportunities, decline and retirement without company-specific privilege. Normal tick work is bounded: two rows, monthly placement attempts, and a cheap identity check while a native closure is pending. The coal capacity warning precedes retirement by nine proposed calendar years in the normal policy.

## Actual effects and scope

One combined, short **1830 compressed fixture** proved both new effects; historical introduction checks still ran. The normal 1840/1975/1991/2000 chronology was not simulated.

- **New textile demand:** instance **543**, local type 42, tile **4008858**, constructed after 39 native attempts in one batch. Native FICR and COAT acceptance was true; TEXT/GOOD outputs registered. No textile input, output haul or revenue was tested.
- **New Silesian mine:** instance **542**, local type 0, tile **6120173**, constructed after two attempts in one batch. A settled operating sample was **180 COAL/month at level 16**; later level-8 samples were **80–90**. An earlier construction-period sample of 300 is retained, not used as a stable baseline.
- **Physical decline/retirement:** level 4 was requested at day **668638**; the engine reported level 0 while closing, and the matching mine was physically absent at **668698**, 60 calendar days later. The state became ended/retired. No original mine was closed.
- **New-schema reload:** schema 6 with two saved rows loaded natively. The factory remained present, the retired coal signature remained absent, both rows stayed ended, and no opening/decline/retirement command replayed during the bounded advance. This is an **ended-state** new-schema reload; an active/closing Phase 7H row was not reloaded.

IDs are fixture-local: **Ruhr gate mine 542 at tile 5265405 is not Silesian fixture mine 542 at tile 6120173**. They belong to separate disposable saves and different contracts.

Five engine invocations total: two mandatory gate runs, one combined transformation fixture, one editor save, one schema-6 reload. No failures or extra corrective runs. All **542 original signatures and 617 towns** remained; the completed transformation fixture had **543 industries**, with the new factory retained and the new coal site removed. No height changes occurred within ten tiles of either new site. Initial candidate CITY/INDY/PATS/PSAC, all map planes and all 15 GRF references/parameters match Phase 7G exactly. Natural runtime growth/background changes are not a frozen-whole-map claim.

## Proposed longer timeline — NOT IMPLEMENTED HERE

Only the two records above were added. These are research/playtest proposals, **not new policy entries**:

- 1830–1850: further regional fibre/food processing tied to demonstrated suppliers and final consumers.
- 1850–1913: selected steel/metalworking networks with verified iron/coke/parts chains.
- 1914–1945: conservative industrial transitions; no automatic wartime destruction or company subsidies.
- 1945–1980: manufacturing and energy changes respecting actual industry introduction gates.
- 1980–2000: additional carefully warned, instance-specific restructuring after closure and replacement tests.
- 2000–2025: circular-material demand shifts only after throughput and paid delivery tests; no assumed shipping solution.

No paid profitability, three-human multiplayer, whole-Europe balance or 195-year progression is certified by this slice. Existing Phase 7F maritime problems remain out of scope.
