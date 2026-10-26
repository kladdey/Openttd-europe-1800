# V10 — historic-centre corrections and explicit terrain deferrals

**27 of the original 54 terrain flags now have source-backed clear targets.**
The other 27 remain unresolved. Applying regional registration consistently also
exposed one additional conflict at Orihuela, which remains unresolved. These
28 towns are explicitly deferred from a separate **536-town clear-target import**;
all remain in the comparison files and the complete 600-record accounting.
No OpenTTD session was run. Clear terrain does not establish founding success.

## Files to use

| File | Towns | Purpose |
|---|---:|---|
| [Clear-target candidate](Europe_1800_V10_CLEAR_TARGET_CANDIDATE_TEST.json) | 536 | Nonzero source land and clear tiles in both supplied scenarios |
| [Retained comparison](Europe_1800_V10_RETAINED_COMPARISON_TEST.json) | 564 | Preserves every V8 candidate town, including unresolved terrain targets |
| [All in-bounds comparison](Europe_1800_V10_ALL_IN_BOUNDS_COMPARISON_TEST.json) | 576 | Also preserves the earlier spacing/identity deferrals for comparison |

These are overlapping **test imports**, not three lists to combine.

- [Interactive evidence map](visualization/evidence_map.html): download the HTML
  and open it locally; search all 600 names, pan/zoom, toggle layers, click towns.
- [Static overview](visualization/evidence_overview.png)
- [Before/after terrain contact sheet](terrain_resolution_contact_sheet.png)
- [55 explicit terrain decisions](terrain_resolution.csv)
- [67 researched historic-site references and sampled outcomes](historic_reference_audit.csv)
- [50 changed placements](coordinate_changes.csv)
- [Complete 600-record accounting](all_600_decisions.csv)
- [All 64 temporary/previous deferrals](deferred_towns.csv)
- [Spacing audit](spacing_audit.csv) and [nearest neighbours](candidate_nearest_neighbours.csv)
- [Summary, limitations and hashes](summary.json)

Original source assets, the master catalogue, populations, city flags, earlier
experiments, playable scenarios and NewGRF configuration remain unchanged.
The existing Modica/Pozzallo identity hold remains in force.

## What was corrected

The following 27 flagged towns now use explicitly selected historic-site targets:

Bamberg, Béziers, Brescia, Brussels, Cartagena, Catania, Gdańsk, Douai, Exeter,
Frankfurt am Main, Glasgow, Le Havre, London, Marsala, Messina, Novara, Padova,
Preston, Regensburg, Saint-Étienne, Torino, Olsztyn, Sanok, Maribor, Pleven,
Serres and Głogów.

The [reference input](../../../data/geography/historic_centre_references_v10.csv)
records each landmark, published coordinates, historical basis, source URLs and
access date. Most geographic references are Wikipedia building/site coordinates;
several historical checks use municipal, diocesan or heritage sources. These
are modern coordinates for historic sites, not surveyed 1800 town-centre pixels.
The exporter does not invent accuracy from their decimal precision.

A few choices require explanation:

- **London:** the medieval Tower at the City/port edge supplies a documented
  founding-target alternative. The Saint Paul's reference still samples saved
  water. This is a placement choice, not proof that London's historic centre
  was inside the fortress. The original V2 anchor remains preserved.
- **Brescia and Exeter:** the civic Loggia and medieval guildhall respectively
  provide clear historic alternatives to church references still on saved water.
- **Glasgow:** the medieval cathedral quarter supplies a historic target away
  from the previous river point. No rejected Glasgow-area coast fit is used.
- **Cartagena:** the theatre coordinate identifies the old-city/cathedral area.
  The theatre was buried in 1800; it is not treated as an operating historic venue.
- **Preston and Pleven:** the historic church sites predate 1800 even though
  the current buildings are nineteenth century. This distinction is recorded.
- **Novara:** the precise basilica infobox coordinate is used. The church began
  in 1577; its nineteenth-century dome is not evidence of its 1800 appearance.
- **Głogów:** the precise Italian-article coordinate supersedes the unusably
  rounded English header coordinate during reference research.

Examples of stronger historical sources are the
[Le Havre municipal archives](https://archives.lehavre.fr/religion-et-edifices-cultuels),
[Pleven municipality](https://www.pleven.bg/bg/zabelezhitelnosti-pametnitsi-i-muzei/tsarkva-sveti-nikolay/),
[Dębica's diocesan history](https://diecezjatarnow.pl/parafie/swietej-jadwigi-slaskiej/74)
and [Racibórz municipality](https://www.raciborz.pl/turystyka_raciborz_zabytki/kosciol_wnmp_farny).
Historical evidence alone does not make a projected pixel clear: Dębica and
Racibórz remain deferred because their researched sites still conflict with saved
terrain. Every attempted reference, including rejected alternatives, is retained.

The [explicit decisions CSV](../../../data/geography/terrain_decisions_v10.csv)
names the selected reference. The exporter never chooses the nearest land tile,
optimizes a town's position for land, silently switches reference, or splits a
population. It rejects a selected water/occupied/area-only reference.

## Regional registration and neighbouring towns

The unchanged V6 global approximation remains:

```text
column = 104.42263446189997 * longitude + 1379.7176323206816
row    = -164.09816527178702 * latitude + 9729.142746398953
```

V10 independently fits a bounded **translation** to the Natural Earth coastline
and actual source-raster coastline in 15 declared geographic boxes. Town land,
population, town count and founding outcomes are not inputs to this fit.
The global scale, axes and orientation are not refitted.

Only three regions pass all declared diagnostic gates:

| Region | Column shift | Row shift | Held-out median | Held-out p90 |
|---|---:|---:|---:|---:|
| Southeastern Spain | +4.819 px | -3.964 px | 0.890 px | 1.871 px |
| Sicily / adjacent Strait coast | -0.779 px | -4.699 px | 1.186 px | 2.898 px |
| Durrës coast | -3.852 px | -0.561 px | 1.324 px | 3.436 px |

The [declared regions and gates](../../../data/geography/coastal_regions_v10.json)
and [complete fitted results, including every rejection](../../../data/geography/coastal_registration_v10.json)
are committed. Bounds are longitude/latitude boxes. The `towns` lists identify
researched terrain cases, not the full set receiving the translation.

For a point inside an accepted box, add the regional shifts to the global
column and row. Apply that same mapping to **every in-bounds catalogue town in
the box**, including comparison-only entries. This avoids correcting Catania
while leaving Acireale in a displaced coordinate frame. The change does not
resolve the identity of the held Modica/Pozzallo record; only its existing
geographic input is rebased in the comparison file.

There are 27 regional registration changes and 27 selected historic-site changes;
four towns belong to both groups, giving **50 unique changed placements**.
The final exporter rechecks every resulting town, not only the original flags.
That check found Orihuela's new conflict and required an explicit supplemental
review and deferral. No previously clear regression was silently included.

The fit samples the existing generalized line segments at up to 3-pixel spacing,
thins repeated samples, and withholds 24-pixel spatial blocks. It uses robust
least squares from three starts and four spatial leave-group-out fits. Gates
require sufficient training/held-out samples, a held-out p90 no greater than
5 pixels and no worse than before, median improvement of at least 0.2 pixels,
jackknife shift disagreement no greater than 2 pixels, directional conditioning
ratio at least 0.15, and a shift inside the ±12-pixel fitting bound. Rejected
fits are not applied. In particular, the code rejects an artificially accepted
model that fails these gates.

**Limits:** these are coast-normal diagnostic errors, not two-dimensional town
accuracy. Densified source segments may cross the held-out blocks. The regional
fits are not independently surveyed or blinded. They do not identify real rivers,
prove historic shoreline positions, or validate inland extrapolation. Extending
a coastal translation inland assumes locally constant registration error.
Box boundaries introduce transformation seams; affected proximity is audited.
The original heightmap's DEM source and CRS are still unknown.

Source-image row/4095 is importer JSON `x`, and column/4095 is JSON `y`. The
importer uses float32 arithmetic with counter-clockwise rotation for these maps.
Exact target pixels are sampled using `scripts/scenario_geography.py`, preserving
the established mapping rather than assuming that JSON axes mean east/north.
See [V6 evidence](../geography_v6/README.md) for the code and scenario verification.

## Remaining terrain deferrals

The original unresolved 27 are:

Alençon, Alicante, Arles, Bourges, Brno, Cádiz, Cagliari, Derby, Hanau, Lucca,
Modena, Namur, Napoli, Nice, Palma, Rostock, Taranto, Troyes, Dębica,
Biała Podlaska, Racibórz, Rijeka, Split, Dubrovnik, Durrës, Volos and Kavala.

**Orihuela** is the additional deferred case found by consistent regional
registration. All 28 have individual reasons and sampled references in the CSVs.
Coastal cases need better historic shoreline/harbour registration. Inland cases
need named-channel/old-town registration or occupancy evidence. Volos's Palia
quarter is historically identified, but its area reference is insufficiently
precise for an exact building target. No nearby pixel is selected merely for
being land. These are temporary omissions, not judgments of historical importance.

The 64 total deferrals comprise **28 terrain + 11 prior spacing + 24 outside-map
+ 1 prior identity** cases. Every one remains in the 600-town accounting, and all
in-bounds records remain in the full comparison import.

## Spacing and founding limits

Geographic updates precede proximity checks. All corrected close pairs are
reported; affected existing decisions are refreshed for the new geometry. The
new Brzozów/Sanok pair at 29.47 tiles is explicitly retained: they are distinct
historic towns with separate roles, documented in the
[historical geographical dictionary](https://wikisource.org/wiki/S%C5%82ownik_geograficzny_Kr%C3%B3lestwa_Polskiego/Brzoz%C3%B3w).
The updated [V10 spacing decisions](../../../data/geography/spacing_decisions_v10.csv)
record this and the changed existing-pair reviews.

The clear candidate has **no sub-15 pair** in normalized-distance or actual
quantized-target checks. Its minimum normalized spacing is 16.221519 tiles
(Manchester/Oldham, the existing industrial-neighbour exception). Acireale/Catania
remain 18.79 tiles apart after consistent registration, rather than the distorted
15.08-tile separation obtained by shifting Catania alone.

**131 clear candidate targets have non-flat corners in at least one supplied
scenario.** Clear means nonzero source elevation and clear tile type in both
saves; it does not mean flat or guaranteed town founding. The importer can search
nearby, and its eventual result also depends on town-distance and height settings,
existing towns and roads. None of those outcomes is claimed here. Original saved
channels/roads can differ from those generated on a fresh map.

The contact sheet shows saved water in blue, roads in brown, houses in purple,
old targets with red crosses, researched references in yellow and selected
clear targets in green. The interactive map shows 536 retained targets and
40 in-bounds deferrals; 24 out-of-map deferrals appear in search only. Its white
landmarks are the earlier V9 global-model checks, not independent validation of
the new regional translations. Colours describe evidence classes, not accuracy
probabilities. The map and contact sheet were visually inspected.

## Reproduce without launching OpenTTD

From the repository root, with Python 3.10+:

```powershell
python -m pip install -r requirements-visualization.txt
python scripts/register_coastal_regions.py --out scratch/v10-registration.json
python scripts/resolve_terrain_flags.py --preview --out scratch/v10-reference-preview.csv
python scripts/resolve_terrain_flags.py --out scratch/v10-candidate
python scripts/visualize_evidence.py --report scratch/v10-candidate --out scratch/v10-map --version V10
python -W error::ResourceWarning -m unittest discover -s tests -v
node tests/test_evidence_map.js scratch/v10-map/evidence_map.html scratch/v10-candidate/summary.json
```

All output paths must be new. The resolver uses the committed, hash-checked
regional registration artifact by default; the first command independently
reproduces that artifact. All supplied scenarios and the original heightmap are
read-only inputs. JSON/CSV outputs and contact sheets reproduce exactly in the
tested environment; numerical fitting, image compression and fonts can differ
slightly across library/platform versions. The new synthetic regression tests
check recovery of a known shift and rejection of an unconstrained straight coast.

Validation: **39 Python tests passed**, including actual-raster land checks,
source preservation, all-600 accounting, rejected-model protection, neighbour
registration consistency, spacing/quantization and byte-for-byte candidate
regeneration. Node map-logic smoke tests passed for both V9 and V10. The Node
test uses a minimal DOM, not a browser rendering or touch/accessibility test.

## Later in-game check, when ready

In **JGRPP 0.73.4**, create a **fresh empty 4096×4096 scenario-editor map** from
`source_assets/heightmaps/Europe_heightmap_original.png` using **counter-clockwise
rotation** and the existing intended NewGRF setup. Use **Town Generation → Load
from file** and choose:

```text
maps/calibration/geography_v10/Europe_1800_V10_CLEAR_TARGET_CANDIDATE_TEST.json
```

It requests 536 towns; founding may fail or shift. Check the 27 corrected sites,
regional neighbours, the 131 non-flat targets, and close industrial/border-town
pairs. Save only under a new scenario filename. For comparison, import the
564-town or 576-town alternative onto separate fresh maps. Never combine the
imports or overwrite the original playable scenarios.
