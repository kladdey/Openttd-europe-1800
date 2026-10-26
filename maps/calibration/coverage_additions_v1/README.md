# Coverage additions V1 — import into the saved 537-town checkpoint

**31 additions-only test towns:** 20 Sweden, 7 North Africa, 4 Balearic Islands.
Expected combined count is **568**, if all additions found and no other towns were
added manually. The existing V11 537-town JSON is unchanged. No new final-town-count
quota is imposed; this is the outcome of the geographic, terrain and spacing review.

## Test in OpenTTD now

1. Open your saved **537-town checkpoint** in JGRPP 0.73.4. Save another copy first.
2. Download [Europe_1800_ALL_COVERAGE_ADDITIONS_V1_TEST.json](Europe_1800_ALL_COVERAGE_ADDITIONS_V1_TEST.json)
   using GitHub's **Download raw file**. Keep its `.json` extension.
3. Use **Town Generation → Load from file** and import it **once** into the populated
   map. Do not reimport the 537-town file or the old Sweden V1 experiment.
4. Record any importer failures and check the Town Directory. Full success means
   **568 towns**. Inspect the additions on their expected landmasses, particularly
   ports and Södertälje near the northern map edge. Leave town expansion untouched
   during this first placement check.
5. Save under a new name, for example `Europe_1800_V11_plus_31_TEST.scn`.

There are also [Sweden-only, 20 towns](Europe_1800_SWEDEN_ADDITIONS_V2_TEST.json)
and [Mediterranean-only, 11 towns](Europe_1800_MEDITERRANEAN_ADDITIONS_V1_TEST.json)
files for separate tests. **Choose the combined file OR the two regional files.**
They contain the same additions; importing all three would duplicate towns.
No merged 568-town full import is provided, to avoid accidental reimport of the baseline.

## Towns included

| Region | Additions |
|---|---|
| Sweden | Malmö, Lund, Helsingborg, Landskrona, Ystad, Kristianstad, Halmstad, Jönköping, Växjö, Kalmar, Linköping, Norrköping, Motala, Södertälje, Mariestad, Uddevalla, Trollhättan, Borås, Skara, Döderhultsvik |
| North Africa | Tangier, Tétouan, Melilla, Algiers, Béjaïa, Tunis, Bizerte |
| Balearics | Mahón, Alcúdia, Manacor, Sóller |

Döderhultsvik is the pre-1856 name of Oskarshamn. Its source identity is preserved
in the audit. It already had trading rights before 1800; no later industrial port
is assumed. Motala remains a modest village/manor reference, and Trollhättan a
falls/canal-era settlement, rather than modern industrial cities.

## What was checked

The review accounts for **all 35** entries in the old Swedish supplement, **16**
new Mediterranean candidates and the **existing Palma hold**: 52 review records.
Of the 21 deferred records, **20 are proposed new settlements**; Palma is already
one of the master catalogue's 63 deferrals and is not counted twice. The original
600-town master and all prior experiments remain intact.

Published geographic coordinates were obtained from cited city articles and
named historic-core/site references. The historic-core choices include Tangier's
seventeenth-century Kasbah palace, Helsingborg's medieval Kärnan, Algiers's Kasbah,
Tunis's medina, and Norrköping's Sankt Olai church. City-reference coordinates are
approximate, and UNESCO property labels are not surveyed founding points. Coordinates
superseded by specific historic references remain documented in their own CSV.
No image coordinates from the rejected Swedish projection were reused. No nearest-
land search, coordinate clamping or new regional translation was applied.

Every retained town:

- Has a documented pre-1800 settlement/site basis, with later names and fabric
  distinguished from older settlement existence.
- Projects inside the original PNG using the unchanged V6 global model and exact
  float32/truncated importer mapping.
- Samples nonzero source elevation and clear terrain in **both supplied scenarios**.
- Remains clear at all nine deterministic half-pixel probes. These may alias to
  repeated tiles; they are not independent observations, probabilities or an error bound.
- Has no duplicate identity among the original master or existing imported towns.
- Has been checked against all 537 baseline towns and other retained additions for
  actual and normalized spacing. The only new 15–30-tile pair is **Malmö–Lund**,
  at **25.612497 actual tiles**, explicitly retained for their distinct historic roles.

There are **11 non-flat addition targets**. Nonzero elevation and clear ground do
not establish flatness, exact historic banks or successful founding. These are
still test imports. The two supplied scenario terrain arrays are **not your newly
saved 537-town scenario**, which has not been uploaded or decoded; its rivers,
roads and occupied tiles may differ. Your in-game test remains decisive.

## Deferrals remain visible

| Reason | Records |
|---|---:|
| Outside this map's northern extent | 8 |
| Exact target on unsuitable terrain | 8 |
| Central target clear but half-pixel probes unstable | 3 |
| Map-edge founding/growth-space review: Örebro, only 2 tiles from edge | 1 |
| Existing Palma shoreline/terrain hold | 1 |

The eight outside-map Swedish entries are Västerås, Uppsala, Eskilstuna, Norrtälje,
Falun, Gävle, Karlstad and Kristinehamn. Stockholm remains a separate existing
master deferral outside this map. Södertälje is included but only **15 tiles from
the northern edge**, so inspect its founding and room for growth carefully.

Important deferred centres include Visby, Oran, Palma, Ibiza and Ciutadella. They
are not deleted or automatically replaced by less important towns. Clear nearby
pixels are not evidence for moving their historic centres. Their source records,
base samples and failed probes stay in the audit for a later local review.

## Populations, identities and evidence

All 35 old Swedish gameplay population values and city flags are preserved in the
review, including deferred entries. New Mediterranean sizes are **provisional game
settings, not 1800 census figures**: 800 for Algiers/Tunis, 400 for Tangier/Oran,
and 150–250 for other centres. New city flags are false. Population policy and each
record's basis are explicit in the input manifest. No original master population,
name or flag changes. In-game populations may differ from the requested settings.

Selected institutional sources supplement the city-reference articles:

- [Skåne coastal towns, Länsstyrelsen](https://www.lansstyrelsen.se/skane/besoksmal/kulturmiljoprogram/kulturmiljoprogram-skanes-historia-och-utveckling/kulturmiljoprogram-kustens-landskap/kuststader.html).
- [Västervik medieval history, Kalmar county museum](https://medeltiden.kalmarlansmuseum.se/mot-medeltiden-i-kalmar-lan/tjust-under-medeltiden/vastervik-stad/).
- [Sankt Olai history, Church of Sweden](https://www.svenskakyrkan.se/norrkoping/las-mer-om-st-olai-kyrka).
- [Tangier palace inventory, IRCICA](https://www.islamicarchitecturalheritage.com/listings/dar-el-makzhen).
- [Algiers Kasbah](https://whc.unesco.org/en/list/565/), [Tunis medina](https://whc.unesco.org/en/list/36),
  [Tétouan medina](https://whc.unesco.org/en/list/837/), [Visby](https://whc.unesco.org/en/list/731/) — UNESCO.
- [Alcúdia municipal history](https://www.alcudia.net/ajuntament/es/Municipi/historia/).

Per-town coordinate and history URLs and short factual paraphrases are recorded
in the [input manifest](../../../data/geography/coverage_additions_v1.json).
Follow Wikipedia sources for full articles, references and revision history;
no article text or third-party map image is copied into this supplement.

## Files and reproduction

- [All candidate decisions](all_candidate_decisions.csv), [deferrals](deferred_towns.csv),
  [nearest combined neighbours](nearest_neighbours.csv), [close-pair review](spacing_review.csv).
- [Probe samples](sensitivity_probes.csv), [superseded references](superseded_geographic_references.csv),
  [regional atlas](coverage_atlas.png), [summary and original-input hashes](summary.json).
- [Generator](../../../scripts/build_coverage_additions.py) and
  [tests](../../../tests/test_coverage_additions.py).

```powershell
python -m pip install -r requirements-visualization.txt
python scripts/build_coverage_additions.py --out scratch/coverage-additions
python -W error::ResourceWarning -m unittest discover -s tests -v
```

Choose a new output directory. Generation runs without network access and refuses
to overwrite existing outputs. Hash checks preserve the baseline, master, old
Swedish file, all-source decisions, heightmap and supplied scenarios. No `.scn`
file or NewGRF configuration is written. The full suite passes **78 Python tests**.

The user's screenshot confirmed **537 towns** and they confirmed saving a checkpoint;
this is recorded as [user-reported validation](../../../data/geography/user_validation_v11_20261026.json).
It verifies a count match and regional visual acceptance, not every town's exact
actual tile, historical population, growth or multiplayer behaviour. This new
31-town supplement has not yet received an in-game test.
