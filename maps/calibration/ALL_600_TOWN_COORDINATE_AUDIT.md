# Europe 1800 - all 600 towns: coordinate integrity audit

This is an exhaustive **coordinate integrity and proximity audit**, not a certified geographic placement audit. All 600 original records have been examined. The source coordinates are normalized as `x = map row`, `y = map column` (not geographic longitude/latitude). A full terrain-based and city-by-city geographic verification remains outstanding.

- Town records: **600**
- Duplicate names: **0**
- Coordinates outside [0,1]: **0**
- Pairs closer than 12 tiles: **13** (may be legitimate urban neighbours)
- Priority coastline review: Lisbon, Porto, Barcelona, Cadiz, Malaga, Szczecin, Rostock, Stralsund, Stockholm, Gothenburg, Oslo, Copenhagen, Karlskrona, Marseille, Hamburg, Bordeaux.

**Do not apply global southward shift or replace the existing scenario based on this audit.** The CSV lists all 600, their exact existing map coordinates, nearest other town and manual review priority. `NOT_GEOGRAPHICALLY_VERIFIED` means the placement has not been checked against its actual geographical location.

Source: `data/towns/europe_1800_import_AUDIT_FIXED_TEST.json`. This does not directly inspect which 524 towns JGRPP successfully placed in the saved scenario.
