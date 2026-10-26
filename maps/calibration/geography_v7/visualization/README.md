# V7 town visualizations

- `Europe_1800_V7_TOWNS_OVERVIEW.png`: full-map high-resolution overview.
- `Europe_1800_V7_REGIONAL_ATLAS.png`: six labelled, overlapping regional zooms.
- `Europe_1800_V7_INTERACTIVE_MAP.html`: self-contained offline interactive map.
  Download this file and open it locally in a browser; GitHub's source viewer
  does not run HTML applications.

All **576** in-bounds V7 targets are plotted at the audited source-raster
column/row resulting from importer quantization. Green marks **520** direct
clear-land targets; amber marks **56** terrain-review targets. Circle size
reflects requested game population, not an independently verified 1800 census.
No town coordinates, population values, JSON imports or original assets changed.

The interactive map supports town/region search, drag-to-pan, zoom, labels,
selection details, terrain filtering, and the **70** close-pair links. Its
sidebar also lists the **24** out-of-map towns without inventing map positions.
All names remain searchable even where static atlas labels do not fit.
Search can use plain Latin characters for most accented names. Regional
panels overlap and include towns from adjacent regions; panel counts are not
country totals. Plotting a point does not validate its historical location.

The background is a display-only relief palette made from the original
heightmap's red channel. The overview and atlas use the full 4096-square
raster; the HTML embeds an 1800-square display image but preserves the full
4096-square coordinate space and target positions. No external network
request, map service or JavaScript library is needed to open the HTML.

Reproduce from the repository root:

```powershell
python -m pip install -r requirements-visualization.txt
python scripts/visualize_europe_towns.py --out scratch/v7-visualization
```

Use a new output directory. Existing outputs are never overwritten.
The static graphics were visually inspected. Embedded data counts and
offline dependencies were checked, JavaScript passed Node's syntax check,
and controller checks exercised search, selection, filters, deferred listing
and zoom limits with a minimal DOM. A full Chromium check could not run
because the execution workspace blocks required socket operations; these
checks do not substitute for browser rendering validation.
