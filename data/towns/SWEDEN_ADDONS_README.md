# Sweden supplemental towns - V1

> Current project context: [status and limitations](../../docs/PROJECT_STATUS.md). Historical add-on experiment; its import instructions do not apply to the V10 candidate. Do not append it without a new geographic audit.

Adds **35 towns**, predominantly southern and central Sweden, to the already-imported Europe 1800 scenario. These are **additional towns only**, not the original 600.

File: `data/towns/sweden_additions_V1_TEST.json`

## Import instructions
1. **Save a separate backup** of `Europe 1800 V1.scn`.
2. Open the populated scenario in JGRPP 0.73.4 Scenario Editor.
3. Use **Town Generation → Load from file** and select the Sweden-only JSON.
4. Record the count of towns the importer could not found; review any failure signs.
5. Save to a new file, e.g. `Europe_1800_Sweden_V2.scn`. Do not re-import the original 600-town JSON.

## Limitations
- Coordinates use the same **unverified** 29-anchor projection as the original imported town file. This pack is a gameplay-first test, **not** GIS-accurate calibration.
- Names were checked against the existing 600-town JSON; none are exact case-insensitive duplicates.
- Some settlements are close together and may fail the game's founding-distance checks. Some may be placed on unsuitable terrain.
- Populations are **gameplay sizes, not 1800 census figures**.
- This pack prioritizes Sweden south of approximately 61°N. Northern Sweden remains sparse; no promise that the map contains its full northern extent.
- Existing Stockholm, Göteborg and Karlskrona are not included, so importing this file will not relocate them.
