# Settlement inventory

The master is `europe_1800_import_AUDIT_FIXED_TEST.json`: **600 preserved records**
with names, integer game populations, city flags and original normalized coordinates.
The original positions are geographically unreliable. JSON integrity is not evidence
of correct landmass, coastline or historical centre.

The current candidate and comparisons are under
[maps/calibration/geography_v10](../../maps/calibration/geography_v10/README.md).
Use the [600-record decision audit](../../maps/calibration/geography_v10/all_600_decisions.csv)
to track retained/deferred outcomes; do not overwrite or silently prune the master.
The draft CSV is not an exact row-for-row geographic companion, and reviewed
source/alias overrides remain necessary.

Population values in import JSONs are game sizes, not unmodified historical counts.
They are preserved in V10. Historical source tables, units and caveats live in
[historical populations](../historical-populations/README.md).

The [Sweden add-on](SWEDEN_ADDONS_README.md) and legacy town exports are historical
experiments, not extra rows to append to the current candidate. Map bounds and
projection uncertainty must be respected; do not clamp out-of-map towns.
