# 15-town validation checkpoint - 2026-10-25

**Status: provisional / incomplete.** The user's screenshots show plausible landmass placement for the British and Irish groups, but they do not establish accurate real-world coordinates.

## Findings

- London, Oxford, Cambridge and Reading: correct landmass; relative positions visually plausible, exact locations not verified.
- Dublin, Kilkenny and Waterford: correct landmass; southern grouping plausible, exact locations not verified.
- Paris, Versailles and Boulogne: **review required**. Boulogne is ambiguous (Boulogne-sur-Mer vs Boulogne-Billancourt); original source coordinates were extremely close to Paris. Versailles needs relative bearing and settlement-overlap review.
- Berlin, Potsdam, Brandenburg and Magdeburg: correct general landmass; **review required** for relative directions and spacing. Screenshot alone does not establish exact positions.
- Stockholm: accepted as provisional five-city V2 control; not shown in 15-town screenshot.

## Decision

Keep the original 600-town target. **Do not extrapolate local translation globally** or overwrite original coordinates. Preserve the five V2 control anchors. Correct flagged clusters and test independent cities before a bulk import. No scenario file changed.

See `Europe_1800_15_city_VALIDATION.csv` for nearest-neighbour distances computed from the 15-town test coordinates. These distances indicate crowding, **not geographic accuracy**.
