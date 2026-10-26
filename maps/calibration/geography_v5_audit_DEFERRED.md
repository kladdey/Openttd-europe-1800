# Deferred geographic decisions

This is a diagnostic checkpoint, not a replacement import.

- **40 V4 towns structurally and spacing audited; 0 geographically validated.**
- **0 coordinates changed; 0 new spacing deferrals.**
- All 600 master records remain present. All are withheld from a new release
  until the raster and mapping can be independently checked.
- Five V2 anchors remain unchanged and provisionally accepted by prior user
  observation; they are not independently geodetically verified.

## Existing omissions requiring renewed review

| Town | Previous reason | Current decision |
|---|---|---|
| Greenwich | About 16.6 tiles from London in old coordinates | Keep documented; historical significance merits individual review after correction |
| Versailles | Crowding near Paris in V3 | Keep documented; verify correct position before deciding |
| Boulogne | Near Paris and ambiguous identity | Do not place until historical identity is resolved |

The draft CSV's Boulogne coordinate (48.83333, 2.25) points toward
Boulogne-Billancourt, **not proof** that the intended historical town was that
settlement. Trace the original de Vries population entry and coordinate join;
do not silently substitute Boulogne-sur-Mer.

Brandenburg's draft position (52.5, 13.5) lies near Berlin and is unsuitable
as a trusted Brandenburg an der Havel control. Confirm the intended historical
settlement and obtain sourced real-world coordinates before regenerating it.
Frankfurt AO is distinguished from Frankfurt AM in the source; retain that
distinction. Halle and other historical aliases still need source review.

## Complete review queue

`geography_v5_audit/catalogue_review.csv` lists every master entry and known
identity blockers, including six towns without matching draft CSV records.
`master_close_pairs.csv` is a **diagnostic** historical-exception review queue
for every pair at most 30 tiles apart; its coordinates are not geographically
trusted. `v4_close_pairs.csv` has no data rows because all V4 distances exceed
30 tiles. Empty flags are not geographical approval.

No importance ranking or transport exception is inferred from population alone.
Preserve ports, industrial centres, mining towns and regional hubs when a
reviewed correction and spacing decision justify them. Europe-wide expansion
remains blocked pending calibration; no arbitrary target count is imposed.
