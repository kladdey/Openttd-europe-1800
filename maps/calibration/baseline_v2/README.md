# Europe 1800 - BASELINE V2 (PROVISIONAL)

**Status:** PROVISIONAL VISUAL BASELINE - user accepted on 2026-10-25 after testing in OpenTTD JGRPP 0.73.4 Scenario Editor on the original 4096 x 4096 Europe heightmap.

**Scope:** Five control towns only: London, Dublin, Paris, Berlin, Stockholm. The JSON is directly importable with JGRPP Town Generation > Load from file. Its `x` and `y` are normalized OpenTTD map coordinates (not latitude/longitude or isometric screen pixels). Keep the original 4096 x 4096 heightmap and orientation unchanged.

**Observed:** Screenshots from the user's V2 test show London in southeastern Great Britain, Dublin on Ireland, Paris inland on continental Europe, Berlin inland, and Stockholm on Sweden's Baltic-facing side. These are coarse visual assessments, **not** accurate geographic registration or independent geodetic validation. Exact town positions, waterways, and full map projection remain unverified.

**Do not:** Extrapolate the five manually selected points into a global coordinate formula, overwrite the existing 600-town file, or modify the playable industry scenario on this evidence alone.

**Next:** Test independent holdouts (Lisbon, Madrid, Barcelona, Amsterdam, Hamburg, Copenhagen, Oslo, Szczecin, Rome, Vienna), then validate region/shoreline and derive a reproducible georeferencing method before producing the 600-town rebuild.

**Files:** `Europe_1800_5_city_CONTROL_V2_TEST.json` (import), `Europe_1800_5_city_CONTROL_V2_AUDIT.csv` (point details).

Earlier 5-city V1 and 10-city samples are superseded; keep them only for diagnostics.
