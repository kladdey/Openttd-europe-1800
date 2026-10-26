# Historic river-bank research: Alençon and Arles

Research checkpoint: 2026-10-26. Two V11 held sites reviewed; **no hold lifted and no
town coordinate changed**. The current candidate remains 537 towns with 27 terrain
cases unresolved. This adds historical constraints and exact-target sensitivity
checks, not a new import or a calibrated historic-bank polygon.

## What the sources establish

### Arles: historic centre on the left bank, Trinquetaille on the right

The regional Inventaire général describes the modern-era boat bridge as linking
the historic centre in the Roquette area on the Rhône's left bank with Trinquetaille
on the right. It records destruction in **1792** and replacement in **1805**.
Consequently, the boat bridge must not be represented as continuously present at
an **1800** start. This does not by itself establish the precise ferry service or
landing coordinates in that year. The inventory's fixed Trinquetaille bridge is
nineteenth century, with a recorded work date of **1867**, not an 1800 structure.
The latter date is not treated here as a separately verified opening date.

The inventory dates the Roquette lock bridge to **1828**. Its right/left-bank
labels refer to the **Arles–Bouc canal**, not the Rhône: those descriptions must
not be substituted for river-bank evidence. The city's heritage record dates the
Grands-Augustins church site to **1450**, but its Saint-Césaire name and restored
worship to **1839**. The existing held site is historically meaningful without
assuming its later name, fabric or parish use applied in 1800.

Sources: [boat bridge, IA13004098](https://dossiersinventaire.maregionsud.fr/dossier/IA13004098),
[fixed bridge, IA13004062](https://dossiersinventaire.maregionsud.fr/dossier/IA13004062),
[lock bridge, IA13004142](https://dossiersinventaire.maregionsud.fr/dossier/IA13004142),
and [municipal church record](https://patrimoine.ville-arles.fr/index.php?idx=22&obj=edifice&quartier=26&site=0).
Regional inventory facts were available in indexed primary records; direct access
was intermittently blocked by a JavaScript challenge. The municipal record was
read directly. These access distinctions are retained in the manifest.

An acquisition lead is the **1786 boat-bridge drawing, Médiathèque d'Arles Ms 500**,
identified by the inventory. It was not retrieved or measured. A historical drawing
would still need orientation and landmark checks before supplying a geometric control.

### Alençon: right-bank historic-centre context, two different bridge dates

The official tourism brochure places the historic town on the **right bank of the
Sarthe**, and includes Saint-Léonard among the centre's monuments. This supports
neighbourhood context; it is not a surveyed bank polygon at the church site.
The CAUE de l'Orne booklet dates **Pont Neuf's opening to 1781**. Its reproduced
plan is captioned **1770**, so that plan must not be assumed to show the later
bridge configuration relevant to 1800. A dated opening does not prove uninterrupted
service in every later year. Reports disagree about the older Pont de Sarthe's
construction century; this research leaves that question open rather than choosing
one unsupported chronology.

The official Saint-Léonard page dates the church's foundation to **1489**, its
vault collapse to **1645**, and rebuilding of the present Gothic vault to **1836**.
The site predates 1800; current architectural fabric is not an unchanged 1800 reference.
The broader bank statement does not establish which saved channel is the Sarthe,
which is a tributary or artificial channel, or on which historic-bank polygon a
particular importer pixel falls.

Sources: [tourism brochure](https://www.alencontourisme.com/app/uploads/alencon/2025/11/Brochure-groupes_seminaires_2026_web.pdf),
PDF page index 3 (printed pages 4–5);
[CAUE/Canopé booklet](https://prim61.ac-normandie.fr/IMG/pdf/livret_enseignants_edp_2019_compressed.pdf),
printed pages **25** and **52** (PDF indices 24 and 51);
and [Saint-Léonard heritage page](https://www.alencontourisme.com/decouvrez/nos-incontournables/le-quartier-saint-leonard/).
The PDF text was readable. No usable screenshot image content was available for
visual inspection, and **no historical map was digitized or georeferenced**.

## What the exact targets show

[Local saved-terrain diagrams](held_target_neighbourhoods.png) display a 7×7
source-pixel window around each held target in both supplied scenarios. `H` marks
the held importer pixel. These are newly generated diagrams of existing terrain,
not edits to either scenario, and do not assign names to the water channels.

| Held reference | Exact source column, row | Base terrain in both scenarios | Half-pixel probes reaching saved water |
|---|---|---|---:|
| Saint-Léonard church, Alençon | 1389, 1782 | Clear, source elevation 33 | 3 of 9 |
| Grands-Augustins / later Saint-Césaire site, Arles | 1863, 2562 | Clear, source elevation 24 | 2 of 9 |

The nine probes apply every combination of **−0.5, 0, +0.5 source pixels** on each
axis to the frozen normalized input before exact float32 parsing and truncation.
They produce only **four unique importer targets** per site: repeated aliases are
retained and must not be treated as independent observations. The samples are
sensitivity examples, **not probabilities, confidence levels, a measured local
registration error bound, or proposed alternative town sites**. No clear neighbour
is selected and no region is translated to avoid water.

For Alençon, saved water occupies column 1389 at row 1781 immediately north of the
held point. For Arles, the held point at 1863,2562 is next to water at 1864,2562;
1863,2561 is also water. These are repeatable terrain observations, not proof of
a particular named river or of the historic bank. They explain why clear-at-one-
pixel alone is insufficient to release either hold.

## Remaining requirements

Both cases retain `HOLD_BANK_ALIGNMENT`. Historical left/right banks are defined
**looking downstream**, not by a fixed compass direction or the importer's x/y axes.
To release a hold we need a dated, interpretable historic-bank or landmark map;
a defensible match to the named channel in the supplied terrain; and enough
registration precision to establish the site's bank after quantization. No such
local error bound or site-to-bank margin has been measured here. Broad city-bank
context, generalized Natural Earth centerlines and a clear sampled tile are insufficient.

Next acquisition targets:

1. **Alençon:** inspect the 1770 plan and a dated post-1781 plan/cadastral sheet,
   checking Pont Neuf, Pont de Sarthe, the castle and Saint-Léonard before tracing
   banks. The BnF locator is [btv1b8441697v](https://gallica.bnf.fr/ark:/12148/btv1b8441697v).
2. **Arles:** inspect the inventory's Ms 500 drawing and a suitably detailed map
   near 1800; distinguish Rhône banks from later canal banks and bridge configurations.

No source has been contacted by email or other messaging. No OpenTTD tests ran.
No master, population, candidate, earlier experiment, source PNG, scenario or NewGRF
configuration was modified.

## Reproducible files and access failures

- [Research manifest](../../../data/geography/historic_river_bank_research_v1.json):
  nine source records, six chronological constraints, bank context and exact access failures.
- [Case review CSV](bank_case_review.csv), [probe CSV](half_pixel_sensitivity.csv),
  [1800 chronology CSV](historical_context_1800.csv), [source-access CSV](source_access.csv),
  and [summary with input hashes](summary.json).
- [Offline generator](../../../scripts/research_river_banks.py) and
  [regression tests](../../../tests/test_river_bank_research.py).

Direct download retry used `--connect-timeout 10 --max-time 25` and failed
immediately with **curl exit 7: proxy unavailable**. No extra-permission request or
unbounded retry was made. Web access to Gallica returned **403**; the indexed
Alençon PLUi reproduction URL returned **404**. A PDF screenshot attempt returned
`TimeoutError`; later screenshot responses supplied text placeholders, not image
content for inspection. These are acquisition failures, not missing-bank findings.
The two inaccessible map locators cannot support geometric claims.

Run from the repository root, choosing a new output directory:

```powershell
python -m pip install -r requirements-visualization.txt
python scripts/research_river_banks.py --out scratch/river-bank-research
python -W error::ResourceWarning -m unittest discover -s tests -v
```

The generator needs **no network access**. It verifies the frozen model, source
PNG/scenarios, V11 references, audit and all-source decisions, then recreates the
CSVs and diagram. It will not overwrite an output directory. Five new tests check
bridge-gap boundary years, later names versus older sites, unusable source locators,
unsupported bank/registration claims, half-pixel fragility and input-preserving
reproduction. The full suite passes **72 Python tests**.

For a future optional direct image retry, keep explicit limits and zero retries:

```powershell
curl.exe -fL --connect-timeout 10 --max-time 25 --retry 0 "https://gallica.bnf.fr/iiif/ark:/12148/btv1b8441697v/f1/full/2500,/0/native.jpg" -o scratch/alencon-1770.jpg
```

A failed download must not be treated as an inspected or georeferenced map.
