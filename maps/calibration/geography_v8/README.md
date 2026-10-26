# V8: geographic-input and spacing desk review

**564-town proposed candidate, plus a separate corrected full 576-town import.**
This review was completed without launching OpenTTD. It is a documented
recommendation, not a proven playable layout or an assertion that founding
will succeed.

| Result | Count |
|---|---:|
| Master records preserved and accounted for | 600 |
| Corrected full in-bounds comparison import | 576 |
| Proposed desk-reviewed candidate | 564 |
| Spacing deferrals | 11 |
| Unresolved combined-identity deferral | 1 |
| Existing out-of-map deferrals | 24 |
| Geographic input points corrected | 2 |
| External reference comparisons / distinct master entries | 31 / 30 |
| Original close pairs / corrected close pairs | 70 / 71 |
| Explicit pair decisions covering both sets | 72 |
| Candidate pairs under 15 tiles | 0 |
| Candidate pairs from 15 through 30 tiles | 51 |
| Minimum candidate target separation | 16.221519 tiles |
| Retained candidate targets with unresolved terrain flags | 54 |

No arbitrary final town count was selected. The 564 entries result from
explicit, consistent recommendations in
[`spacing_decisions_v8.csv`](../../../data/geography/spacing_decisions_v8.csv)
and a separate combined-identity hold. The master, its populations/city flags,
the V2/V3/V4/V6/V7 experiments, heightmap, scenarios and NewGRFs remain intact.
The complete V7 import is still available unchanged.

## Files to use

- [`Europe_1800_V8_DESK_REVIEWED_CANDIDATE_TEST.json`](Europe_1800_V8_DESK_REVIEWED_CANDIDATE_TEST.json):
  the proposed 564-town layout, including documented historical close-neighbour
  exceptions and unresolved terrain targets.
- [`Europe_1800_V8_CORRECTED_ALL_IN_BOUNDS_TEST.json`](Europe_1800_V8_CORRECTED_ALL_IN_BOUNDS_TEST.json):
  all 576 in-bounds entries with only the two supported geographic input
  corrections. This preserves a full comparison option without silently
  removing any close town or choosing an identity for Modica/Pozzallo.
- [`all_600_decisions.csv`](all_600_decisions.csv): complete retained/deferred
  accounting, original metadata, sampled terrain and unresolved boundary flags.
- [`spacing_review.csv`](spacing_review.csv): all 72 pair recommendations,
  before/after distances, quantized target distances and evidence references.
- [`deferred_towns.csv`](deferred_towns.csv): all 36 deferred master entries,
  including the existing 24 boundary cases.
- [`historical_exceptions.csv`](historical_exceptions.csv): sourced exception
  decisions and deferred historically important neighbours.
- [`coordinate_reference_audit.csv`](coordinate_reference_audit.csv) and
  [`coordinate_changes.csv`](coordinate_changes.csv): geographic input evidence.
- [`terrain_review_refined.csv`](terrain_review_refined.csv) and
  [`terrain_review_contact_sheet.png`](terrain_review_contact_sheet.png):
  the 56 originally flagged terrain targets, refined and illustrated.
- [`regional_balance.csv`](regional_balance.csv): source-region counts before
  and after the decisions, without country quotas or invented replacements.

Do not import both JSONs into one scenario; the 564-town file is a subset
of the corrected 576-town comparison file.

## Geography before proximity

This pass compared 30 distinct catalogue entries against 31 externally
published approximate settlement points. The references and source URLs are
preserved in
[`coordinate_checks_v8.csv`](../../../data/geography/coordinate_checks_v8.csv).
The two large unambiguous input discrepancies were corrected separately:

| Master name | Finding | Consequence |
|---|---|---|
| CASTROGIOVANNI | The historical name refers to Enna; the V7 geographic input was about 13.9 km west of its published reference. | Correct the input to 37.56333N, 14.27611E. Separation from Caltanissetta rises from 11.65 to 25.33 tiles; both are retained. |
| PIAZZA (ENNA) | This refers to Piazza Armerina in Enna province, not a point near Enna itself. The V7 input differed by about 23.0 km. | Correct to 37.383N, 14.367E. The old Nicosia/Piazza flag disappears; two newly close pairs with Caltagirone and Mazzarino are explicitly reviewed. |
| MODICA/POZZALLO | The label combines two distinct settlements. Its position resembles coastal Pozzallo, while Modica lies inland. | Defer from the proposed candidate until the historical population/identity join is resolved. Do not silently move it inland, split its population or create two towns. |

Coordinate references: [Enna](https://en.wikipedia.org/wiki/Enna),
[Piazza Armerina](https://en.wikipedia.org/wiki/Piazza_Armerina),
[Modica](https://en.wikipedia.org/wiki/Modica),
[Pozzallo](https://en.wikipedia.org/wiki/Pozzallo).
Original names and populations remain unchanged in all imports.

The other reference comparisons generally agree at settlement scale. A
3-km comparison band is a **screen for large source-join problems**, not a
claim that an input is accurate enough for tight spacing. Rounded city points,
municipal centres, historic centres and the palace of Versailles are not
interchangeable: the Versailles city reference was deliberately used rather
than the palace point returned by the generic article redirect.

These checks are **not independent raster landmark holdouts**. They do not
recover the original heightmap's CRS, establish exact town-centre pixels or
independently measure geographic positional accuracy. The V6 coastline fit,
its source generalization and its 86.67-pixel worst held-out normal residual
remain unchanged. Published gazetteers may also share underlying data.
No apparently more precise reference is blindly substituted into a source
point that is already a plausible settlement representative.

## Spacing decisions and historical significance

Eleven entries are deferred from the proposed candidate for crowding:
**Altona, Baeza, Barmen, Delft, Fossano, Fürth, Greenwich, Lier, Salford,
Stockport and Zaandam**. Their original master spellings remain in the CSVs.

- Hamburg, Amsterdam, Nurnberg, London and Manchester remain the main anchors
  of their tight clusters. The choice to represent the Wupper cluster with
  Elberfeld is a spatial recommendation, not a claim that Barmen was unimportant.
- Altona's independent Danish-port role, Zaandam's industrial/shipbuilding
  heritage and Stockport's industrial role are explicitly recorded as
  historically important exceptions for possible reinstatement. They are
  not marked as duplicates or historically insignificant.
- Both Baeza and Ubeda are important distinct towns. Ubeda's larger catalogue
  estimate is a tie-breaker for this spatial compromise; UNESCO does not
  endorse suppressing Baeza. Its ecclesiastical/educational exception remains
  documented.
- Lier is deferred in the Antwerp/Mechelen cluster, and Fossano in the
  Cuneo/Mondovi/Savigliano cluster. These are stated corridor-space trade-offs,
  not mistakes inferred from name similarity or fixed-count pruning.

Important close neighbours are deliberately retained:

| Pair | Desk-review basis |
|---|---|
| Krakow / Wieliczka | A distinct salt-mining origin with medieval roots merits retention despite proximity. |
| Badajoz / Elvas | The historic fortified border crossing provides a separate role for each town. |
| Messina / Reggio Calabria | Opposite sides of the strait and different landmasses create a crossing opportunity. |
| Trieste / Koper | Preserve separate Adriatic coastal origins; harbour growth still needs review. |
| Cetinje / Kotor | The historic inland centre and mountain-enclosed harbour have distinct contexts. Cetinje's later urban expansion is not projected backward into 1800. |
| Manchester / Oldham | Retain a documented industrial neighbour at about 16.2 tiles, with an explicit future growth-space caveat. Evidence of cotton mechanisation by 1819 supports campaign progression, not a fabricated 1800 factory census. |
| Paris / Versailles | Retain the separate town at about 24.2 tiles; the royal court left in 1789, so it is not described as an active royal residence in 1800. |
| Caltanissetta / Castrogiovanni | Corrected geography removes the false under-15 conflict; no settlement is omitted because of the old wrong coordinate. |

The full decision table covers all 70 V7 pairs plus the two newly exposed
Sicilian pairs. One V7 pair is no longer close, leaving 71 current pairs;
51 remain in the proposed candidate. The exporter refuses missing, duplicate
or contradictory recommendations rather than selecting winners by population.

Spacing remains a guideline. `near_policy_boundary` flags distances within
two tiles of 15 or 30; that flag is a sensitivity reminder, not an error bound.
Stockport is particularly borderline: a different reasonable centre point can
change its band. Its deferral is a conservative Manchester-cluster decision,
not a claim that the 15-tile number alone settles its importance. Source and
projection uncertainty also affect distances farther from those thresholds.

Historical evidence and its limits are listed in
[`review_sources_v8.csv`](../../../data/geography/review_sources_v8.csv).
Sources include UNESCO, the Port of Hamburg, Wuppertal's municipal archive,
the Palace of Versailles, heritage institutions and published research.
They support historical context; **none endorses this scenario's selection
decisions**. Rows citing only `CATALOGUE` use settlement inventory evidence
and an explicitly stated layout judgement, not a newly established detailed
historical priority ranking. Generic gameplay populations are not treated as
verified census observations.

## Refining the 56 terrain flags

| Refined classification | Count | What it establishes |
|---|---:|---|
| Saved water over nonzero original elevation | 39 | Compatible with inland/generated water features. It does not identify a real river by name or prove the point is wrong. |
| Zero original elevation connected to the image edge, plus saved water | 14 | A likely coast/harbour context requiring inspection; frame connectivity is not a surveyed real-world shoreline. |
| Saved road/tram occupancy over nonzero elevation | 3 | Bourges, Saint-Etienne and Raciborz are not offshore solely because their saved target is occupied. A fresh empty map may differ. |

The updated positions of the two corrected towns were re-sampled in both
original scenarios and are clear land. Every corrected in-bounds town has
fresh target samples in `all_600_decisions.csv`; new risks cannot be hidden
by only reusing the V7 flags. Of the original 56 flags, 54 remain in the
candidate. Altona is spacing-deferred and Modica/Pozzallo identity-deferred.

All 56 have at least one common clear-and-flat pixel in a ±16-tile square
of both saved scenarios; the furthest nearest such pixel is about 7.81 tiles
away. **This does not establish successful founding.** It does not emulate
the importer's exact search order, current town-minimum-distance setting,
edge restrictions, permitted height, neighbouring towns, road layouts or
subsequent growth. Clear-only sampling is also more restrictive than the
game's allowance for some tree tiles. No target has been moved to any of
these pixels and no bank position is silently recommended.

[The contact sheet](terrain_review_contact_sheet.png) shows 80×80-source-pixel
neighbourhoods at two display pixels per source pixel. Red crosses mark the
unchanged targets, blue marks saved water, brown saved road/tram and grey the
source relief. It is a review aid, not a substitute for named-channel or
founding verification. No original raster was edited.

## Regional balance and unresolved work

`regional_balance.csv` accounts for every source-region entry. There are no
new spacing deferrals in Iberia outside the single Baeza choice, no Scandinavian
or eastern towns moved into the crop, and no country replacement quotas.
The regional labels are inherited source categories, sometimes historical;
they are not modern political boundary verification.

The candidate still needs exact historic-centre/landmark verification,
coast/river inspection, close-pair growth review and eventual founding tests.
The original 24 outside-map towns remain deferred, with near-boundary
uncertainty carried forward separately. No wider heightmap, industry layout,
population rebalance or NewGRF change is part of this pass.

## Reproduce without running OpenTTD

From the repository root, Python 3.10+:

```powershell
python -m pip install -r requirements-geography.txt
python scripts/review_europe_placements.py --out scratch/v8-reproduction
python -W error::ResourceWarning -m unittest discover -s tests -v
```

Use a new output directory. The workflow reads only preserved datasets and
source assets, verifies hashes before/after and records input hashes. The
coordinate and pair decisions are explicit versioned inputs; reproducibility
does not require querying changing websites at runtime. Source references
were consulted on 2026-10-26.

Automated checks cover full accounting, unchanged metadata, exactly two
coordinate changes, consistent coverage of old/new close pairs, the false
Enna conflict, missing/contradictory-decision rejection, terrain categories
and byte-identical regeneration. These are code/data checks; **no OpenTTD
or gameplay testing was performed**.

Validation on 2026-10-26: **24 automated tests passed with no skips**, using
the preserved real source assets. Regeneration matched every generated V8
artifact byte for byte; source hashes remained unchanged.

## When an in-game check is eventually wanted

Use JGRPP 0.73.4 with the existing NewGRF configuration. Generate a fresh
empty 4096×4096 editor map from the original heightmap using counter-clockwise
rotation. Load **one** V8 JSON through Town Generation → Load from file.
The candidate requests 564 towns; the corrected full comparison requests
576. Actual successful counts may be lower. Save only to a new filename,
such as `Europe_1800_V8_DESK_CANDIDATE_TEST.scn`; never overwrite the original
industry scenario. This pass deliberately stops before that game check.
