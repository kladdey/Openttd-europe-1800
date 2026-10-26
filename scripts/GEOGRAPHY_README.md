# Geography tooling entry point

Use the [tool guide](README.md), [active workflow](../docs/GEOGRAPHY_WORKFLOW.md)
and [project status](../docs/PROJECT_STATUS.md). V10 is the current placement
checkpoint; the complete original raster and two scenario binaries are available
under `source_assets/` and are hash-checked by the scripts.

The raster-to-import mapping has been established for JGRPP 0.73.4, including
counter-clockwise rotation and float32 rounding. Geographic projection is still
an empirical coastline registration, not a recovered original CRS. Automated
data and terrain tests run without OpenTTD; founding and town growth remain untested.
