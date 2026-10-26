# V11 — source review and bank-alignment holds

V11 follows up **all 28 V10 terrain deferrals**. It adds 25 specific historic-site
references, rejects nine misleading or insufficient source attempts, and
reinstates **Namur** at a documented citadel-site target. The other 27 cases
remain deferred. Every existing V10 retained town and its coordinates are preserved.
No game platform is available, and no OpenTTD session was run.

| Import | Records | Purpose |
|---|---:|---|
| [Clear-target candidate](Europe_1800_V11_CLEAR_TARGET_CANDIDATE_TEST.json) | 537 | Existing V10 candidate plus Namur |
| [Retained comparison](Europe_1800_V11_RETAINED_COMPARISON_TEST.json) | 564 | All previously retained towns, including unresolved targets |
| [Full in-bounds comparison](Europe_1800_V11_ALL_IN_BOUNDS_COMPARISON_TEST.json) | 576 | Includes earlier spacing and identity holds |

All 600 master records remain accounted for. The clear candidate has **63 deferrals**:
27 terrain, 11 previous spacing, 24 outside the map and one combined-identity hold.
Original catalogue, populations, city flags, heightmap, scenarios, earlier outputs
and NewGRF configuration remain unchanged. These imports overlap; do not combine them.

- [Interactive evidence map](visualization/evidence_map.html) — download and open locally
- [Static map](visualization/evidence_overview.png)
- [Terrain contact sheet](terrain_resolution_contact_sheet.png)
- [28-case follow-up register](remaining_case_review.csv)
- [Only change since V10](v10_to_v11_changes.csv)
- [All 600 decisions](all_600_decisions.csv) and [all deferrals](deferred_towns.csv)
- [All 92 historic references and sampled outcomes](historic_reference_audit.csv)
- [Excluded source attempts](source_exclusions.csv)
- [Spacing audit](spacing_audit.csv), [nearest neighbours](candidate_nearest_neighbours.csv),
  [regional balance](regional_balance.csv) and [summary/hashes](summary.json)

## Namur: a supported alternative, with limits

The [citadel's official history](https://citadelle.namur.be/en/history) describes
the medieval castle and later defensive complex on the hill at the Sambre-Meuse
confluence. The published citadel reference is 50.4605 N, 4.8640 E, from the
[specific citadel article](https://en.wikipedia.org/wiki/Citadel_of_Namur).

This projects to source pixel **1888,1448** and game target **2207,1448** using
the unchanged V6 mapping and exact counter-clockwise importer arithmetic. It is
nonzero source land and clear ground in both supplied scenarios. Its displacement
from V10 is **1.110911 normalized map tiles**. Rising ground at the saved junction
is compatible with the documented fort-site context; the saved channels have not
been independently surveyed or identified as named rivers.

This is a historically justified defensive-site founding-target choice. It does
not claim that the north-bank civic centre moved into the citadel, establish
survey-grade riverbank alignment, or prove founding success. Its saved corners
are non-flat in both-map diagnostics, so it specifically needs a later slope and
founding check. Game population and city flag are preserved.

## Clear ground alone does not approve a reference

Saint-Leonard's church site in Alençon and the former Grands-Augustins church
(later called Saint-Cesaire) in Arles project to clear ground. Both are explicitly
held as **HOLD_BANK_ALIGNMENT**. Their relationship to the saved channels and the
real historic-bank context has not been established sufficiently to approve a
move. No claim is made that those saved channels have proven names.

The new `placement_review` field separates historic/positional review from the
sampled tile type. A clear point with a bank, identity, coordinate-source or
context hold is **ineligible** for export selection. Unknown review-state values
are rejected. This prevents a superficially successful land check from silently
removing a geographic concern. Existing V10 references retain their documented
review status and model limitations; they are not retrospectively certified.

The [Alençon tourism record](https://www.alencontourisme.com/decouvrez/nos-incontournables/le-quartier-saint-leonard/)
and [church-specific architectural record](https://www.pss-archi.eu/immeubles/FR-61001-79970.html)
identify the historic church site, with substantial later rebuilding. An event's
tourist-office meeting point is not used as the church coordinate. The
[Arles municipal heritage record](https://patrimoine.ville-arles.fr/index.php?idx=22&obj=edifice&quartier=26&site=0)
dates the Augustinian building to 1450, records its revolutionary sale, and places
its return to worship under the Saint-Cesaire name in 1839. It is not represented
as an operating Saint-Cesaire parish in 1800 or confused with the separate abbey.

## Source exclusions and coarse-grid limits

The exclusion register documents the evidence issue and the unused source:

- A nominal English Place Garibaldi lookup returned **general Nice city coordinates**.
  The square-specific French record and restoration history were used instead.
- A Saint-Leonard lookup produced coordinates inconsistent with the specific
  architectural record; the conflicting point was not adopted.
- A Bourges palace identity was found, but an aggregator coordinate was not confirmed
  against the precise site; no numeric alternative was invented.
- A Dębica market webcam is not established as the historic square centre.
- A San Pietro Apostolo church west of Modena is a homonym, not the central abbey.
- Taranto's municipality distinguishes old San Domenico from later use of the
  name Maggiore/Monteoliveto. Similar names do not justify substituting a state
  inventory coordinate without a site join.
- The Minčeta tower at **Ston** is not the tower at Dubrovnik.
- A Palia tower at **Monemvasia** is not Kastro-Palia in Volos.
- The Volos neighbourhood-area reference remains insufficient for a building target.

The [source reference input](../../../data/geography/historic_centre_references_v11.csv)
records specific URLs, interpretation, access date and review state. Several
coordinates are secondary map/Wikimedia references; they are approximate modern
site locations, not measured 1800 boundaries. Sources were reviewed online, but
live websites are not needed to reproduce the committed numerical exports.

Nine of the 25 new site references collapse onto **importer pixels already sampled
for the same town**. More decimal places or alternative street addresses therefore
do not necessarily provide a new placement opportunity at this scale. The case
register reports pixel aliasing explicitly. Twenty-two cases have newly researched
points that remain unsuitable; three lack a confirmed new precise point; two
have clear points held for review; one is reinstated.

## Geographic and gameplay limitations

No geographic model is changed in V11. The accepted V10 regional translations
remain applied consistently to all neighbouring catalogue towns in their boxes.
See [V10 methodology](../geography_v10/README.md) for their coastline-only fit,
held-out diagnostics, rejection gates and inland-extrapolation limitations.
The original DEM CRS/crop and exact named-river registration remain unknown.
No nearest-land search, coordinate clamping or desired town count is used.

The 27 remaining terrain holds need stronger old-town/channel or historical
shoreline registration. Further address-level substitution alone has diminishing
value where multiple references hit the same pixel. The 24 outside-map records
and Modica/Pozzallo identity hold remain unchanged. Regional balance is documented
without quotas or an arbitrary final settlement count.

The clear candidate has no sub-15 pair in normalized or quantized target checks;
minimum normalized spacing remains **16.221519 tiles**, Manchester/Oldham.
The added Namur target creates no new close pair. Previous close-pair decisions
remain documented; the existing Brzozów/Sanok review is carried forward.

**132 retained clear targets have non-flat corners in at least one supplied
scenario.** Clear means source red-channel elevation >0 and clear tile type in
both supplied saves. It does not prove flatness, historical pixel accuracy or
founding. Generated channels/roads on a fresh map may differ from those saves.
The map's white landmarks remain V9 global-model context, not independent
validation of the V10 regional corrections or V11 site choices.

## Reproduce offline

From the repository root, with Python 3.10+:

```powershell
python -m pip install -r requirements-visualization.txt
python scripts/review_remaining_terrain.py --out scratch/v11-candidate
python scripts/visualize_evidence.py --report scratch/v11-candidate --out scratch/v11-map --version V11
python -W error::ResourceWarning -m unittest discover -s tests -v
node tests/test_evidence_map.js scratch/v11-map/evidence_map.html scratch/v11-candidate/summary.json
```

Use new output paths. To inspect only the versioned reference inputs:

```powershell
python scripts/resolve_terrain_flags.py --profile data/geography/placement_profile_v11.json --preview --out scratch/v11-reference-preview.csv
```

The profile selects explicit reference/decision tables and safe versioned filenames;
it does not change the master or previous experiments. Omitting `--profile` from
the shared resolver intentionally reproduces V10, preserving the earlier workflow.
The follow-up script adds the V10-to-V11 delta, 28-case review, source exclusions
and regional balance to the shared export. Source hashes are checked before reads.

Validation: **46 Python tests**, including V10 snapshot reproduction, review-hold
protection, profile validation, all-600 accounting, source preservation, land and
spacing checks, and V11 byte-for-byte regeneration. The map-logic smoke test also
covers V11. It is a minimal-DOM check, not a browser rendering/accessibility test.
No in-game tests are claimed. Contact sheet and static map are visually reviewed.

## When a game platform is available

In JGRPP 0.73.4 create a fresh empty 4096×4096 editor map from the original
heightmap using **counter-clockwise** rotation and the intended unchanged NewGRF
setup. Choose Town Generation → Load from file and load:

```text
maps/calibration/geography_v11/Europe_1800_V11_CLEAR_TARGET_CANDIDATE_TEST.json
```

It requests 537 towns. Record founding failures, any shifted actual locations and
settings. Check Namur, non-flat targets and close neighbours. Save to a new
scenario filename. Use separate fresh maps for the 564/576 comparisons; never
combine overlapping imports or overwrite original scenarios. Unavailable game
access does not block further geographic/source review.
