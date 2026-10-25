# De Vries 1800 urban population extraction

This is a sourced **historical estimate dataset**, not a literal Europe-wide census.

Source: Jan de Vries, *European Urbanization, 1500-1800* (1984), adapted by Matthew Lincoln, [europop](https://github.com/mdlincoln/europop), version 0.3.1. Data are published under CC0 by the package maintainer; cite the underlying scholarship.

Original data: https://github.com/mdlincoln/europop/blob/master/data-raw/europop.csv
Coordinate table: https://github.com/mdlincoln/europop/blob/master/data-raw/city_coords.csv

Files:
- `devries_1800_raw.csv`: 379 rows for reference year 1800, unmodified values from the source.
- `devries_city_coords_raw.csv`: source coordinate lookup for matching cities (not calibrated to OpenTTD tiles).

**Important**: Population values are in **thousands**, not people. `NA` means unknown. `0` denotes under 1,000 according to source documentation, **not zero inhabitants**. Geographic coverage follows the source's regional definitions and excludes many small towns. Some settlements appear under historical or alternate spellings. Do not assume this file alone covers our target 600 settlements.

Further work: normalize identifiers, check coordinate matches, document missing cities, compare 1801 British census and 19th-century regional sources, verify licensing for additional datasets, and calibrate to heightmap.
