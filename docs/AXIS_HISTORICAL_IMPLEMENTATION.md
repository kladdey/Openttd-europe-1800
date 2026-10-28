# AXIS Historical Europe 0.1.0 — steelmaking implementation

2026-10-28. **Compiled and loaded in JGRPP 0.73.4; 16 automated headless
construction cases passed.** This is a limited steelmaking milestone, not a
complete historical economy. The campaign scenario and other NewGRFs are untouched.

## Identity, source and reproducibility

The fork starts from AXIS 2.3.1 commit
`11c8353ccf7444b143e57080b1aa2b5e38839a23`, exported with `git archive`.
The original checkout and installed AXIS are never edited. The project directory
is [newgrfs/axis-historical-europe](../newgrfs/axis-historical-europe/README.md).

| Item | Implemented value |
|---|---|
| Display name | AXIS Historical Europe 0.1.0 (AXIS 2.3.1 base) |
| GRFID | `4B484531`, literal `KHE1`; provisional/unregistered project identifier |
| Numeric version / minimum compatible | 1 / 1, scoped to this new GRFID |
| Baseline economy | Extreme Classic, internal `BASIC_TEMPERATE`, economy 0 |
| Source delivery | Pinned export + project overlay, generated review/apply patch, full local corresponding-source ZIP |
| Binary | `newgrfs/axis-historical-europe/dist/axis-historical-europe-0.1.0.grf` |
| Binary size / SHA256 | 7,786,646 bytes / `cd1d5a5a704613469207d726b15c1bec02afff8cb0c2c70b2877c8fe429ecd09` |

The ID is deliberately distinct from AXIS `4A4B8808`. An inherited incompatibility
check now rejects original AXIS alongside the fork. **Use exactly one industry
set.** The new identity prevents an accidental claim of save compatibility:
do not substitute it into the working campaign or hot-swap NewGRFs. Build a new
1830 test scenario with this fork from the outset. No map coordinates are added.

The wrapper runs AXIS `render_lang.py`, `render_nml.py` and NML directly;
HTML documentation generation is unnecessary for the GRF. Tested toolchain:
Python **3.12.14**, NML **0.9.0**, Chameleon **4.6.0**, Pillow **13.0.0**.
Build instructions and pinned requirements are in the directory README.
Both the modified fork and a pristine AXIS export compiled successfully.
The build fixes `PYTHONHASHSEED=0` and sorts upstream's unordered set of
incompatible-industry siting checks by local industry ID. Without this, repeated
builds can differ in byte ordering. This shared one-line ordering change does
not change the check predicates, recipes, cargoes, IDs or layouts in any economy.
A clean extraction of the corresponding-source ZIP rebuilt to **exactly the
same GRF SHA256** with the tested toolchain. See
[bundle rebuild proof](../newgrfs/axis-historical-europe/bundle-rebuild-result.json).

## Implemented industry changes

| Industry | AXIS local ID | Historical new-construction window | Recipe change |
|---|---|---|---|
| Nineteenth-century Steelworks, source `steel_mill` | 2 | From 1860; no final year | Both stockpiled inputs required: 3 `IRON` + 1 `COKE` → 3 `STEL` + 1 `SLAG` |
| Electric Arc Furnace | 79 | From 1906; no final year | None; original Classic recipe preserved |
| Basic Oxygen Furnace | 77 | From 1952; no final year | None; original Classic recipe preserved |

The source `steel_mill.py` and its ID/graphics/layouts already existed, but its
registration was commented out globally. It was therefore absent from the
91-type Classic extraction. This implementation registers it **only in Classic**,
bringing that economy to 92 types without allocating new industry or tile IDs.
Its original oxygen/acetic-acid/ore recipe was unsuitable and never enabled in
Classic. The new recipe uses existing labels and upstream source graphics.

A custom production callback stockpiles the two inputs and processes only
complete batches on cargo arrival and the periodic callback. Unlike ordinary
AXIS secondary recipes, it cannot turn coke alone into steel. Remainders remain
in stock. Its GUI text describes the batch instead of showing the unused generic
secondary supply-bonus counters. No new cargo label, train refit or engine
production/closure command is introduced.

This recipe is a **gameplay abstraction**, not a metallurgical mass balance.
Pig iron stands in for suitable iron feedstock; coke represents fuel/reductant;
air, refractory maintenance and process-specific fluxes are implicit. Real
Bessemer conversion uses air and oxidation heat rather than a literal coke-fed
converter recipe. Output slag is retained to integrate AXIS's byproduct chain.
Separate processes/grades, oxygen and additional cargoes are deliberately avoided.
Reused graphics are not an accurate model of an individual nineteenth-century works.

### Historical basis and choices

* Crucible steel predates the campaign: Huntsman's process was developed in the
  eighteenth century. It refined blister steel in crucibles, not the literal
  pig-iron recipe above. [Museums Sheffield's history](https://www.sheffieldcutlerymap.org.uk/history-of-the-cutlery-industry/)
  and [Historic England's Sheffield metal-trades study](https://historicengland.org.uk/images-books/publications/one-great-workshop/one-great-workshop/)
  support this distinction. A dedicated pre-1860 crucible chain is **not** implemented.
* Bessemer patented his process in **1856**;
  [Sheffield Museums' converter account](https://sheffieldmuseums.org.uk/whats-on/bessemer-converter/)
  documents the process and subsequent production. **1860** is a deliberate
  campaign date for a generic commercial steelworks, not a claim that steel
  was invented then. The same site serves later open-hearth production as an
  abstraction, avoiding three new industry categories.
* Open-hearth/Siemens–Martin development belongs to the 1860s. A contemporary
  [1880 US census account](https://www2.census.gov/prod2/decennial/documents/1880a_v2-18.pdf)
  records an American Siemens–Martin furnace operating in December 1868.
  The reused works does not distinguish this process from Bessemer steel.
* Electric-arc steelmaking was practical in the first decade of the twentieth
  century, with earlier experiments and installations before 1906. The
  [Science Museum's Héroult furnace record](https://collection.sciencemuseumgroup.org.uk/objects/co19601/heroult-electric-steel-making-furnace)
  associates its example with 1906–1914; a contemporary technical account,
  [Electric Furnaces for Making Iron and Steel](https://digital.library.unt.edu/ark:/67531/metadc12279/m1/65/),
  reports the 1904 commission's findings on successful electric steelmaking.
  **1906** is a conservative gameplay adoption date, not the first experimental
  use or a universal European industrial threshold. EAFs remain unavailable in 1900.
* [voestalpine's LD-process history](https://www.voestalpine.com/group/en/media/press-releases/2012-11-27-voestalpine-celebrates-60-years-of-the-ld-process/)
  dates the first operating LD plant to November **1952**. The fork uses
  **1952-01-01** as its year-resolution gameplay gate; it does not claim an
  exact January historical commissioning date.

## Availability architecture and actual callback categories

[historical_manifest.json](../newgrfs/axis-historical-europe/historical_manifest.json)
is the central policy store: earliest year, optional inclusive final construction
year, map-generation permission, shared natural/deity permission, and shared
player-funding/prospecting permission. There is no fabricated independent GS
permission. Regional restrictions are omitted because no reliable custom-map
geography is available to the callback in this milestone.

The model overlay creates guard expressions from that manifest. Availability
wrappers reject disallowed construction, then delegate to AXIS's original
availability callback. Location wrappers repeat the guard, then delegate to
the original location callback. This second layer matters because editor
construction bypasses ordinary probability checks. Terrain, layouts, distances,
keystones and existing AXIS date gates continue to apply.

Source verification:
[JGRPP call-type enum and callback signature](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/newgrf_industries.h),
[probability and location callbacks](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/newgrf_industries.cpp),
[industry commands](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/industry_cmd.cpp),
[script construction implementation](https://github.com/JGRennison/OpenTTD-patches/blob/cd2235f78365bad1dc6769f3b8f8b1e66b24fdf8/src/script/api/script_industrytype.cpp),
and [NML industry callback documentation](https://newgrf-specs.tt-wiki.net/wiki/NML:Industries).

| Route | Callback `extra_callback_info2` | Policy behavior |
|---|---|---|
| Map generation | `IND_CREATION_GENERATION` = 0 | Date + manifest generation permission |
| Natural gameplay opening | `IND_CREATION_RANDOM` = 1 | Date + shared natural/GS permission + AXIS allow-spawning parameter |
| Deity GS BuildIndustry/ProspectIndustry | Same RANDOM = 1 | Same as natural gameplay, plus engine/NewGRF location rules |
| Player/company funding | `IND_CREATION_FUND` = 2 | Date + funding permission; independent of AXIS random-spawning switch |
| Player prospecting | `IND_CREATION_PROSPECT` = 3 | Date + funding/prospecting permission, with existing engine raw-industry rules |

Parameter **10** (`historical_europe_mode`) defaults **on** and applies added
restrictions only to Classic. Off preserves the fork identity and added
steelworks but bypasses its added date/route restrictions. It does **not** remove
AXIS's pre-existing dates/permissions or restore byte-for-byte original AXIS.
Select parameters before creating a new game; runtime parameter hot-swapping
is not supported or proposed.

For later GS control: enable AXIS **Allow industries spawning during gameplay**
(parameter 2, bit 2 = 1; raw parameter value 4) and set engine industry density
to **Funding only** (0). This combination was exercised in the headless tests:
GS creates eligible industries while density suppresses natural openings.
Turning AXIS spawning off blocks deity construction even after dates; company
funding still works. BOF deity placement retains its nearby-blast-furnace rule.

No construction callbacks alter existing industry's production. Final-year
support is inclusive and concerns new construction only; all three current
manifest final years are null. No forced closure, conversion or retirement exists.

## Build, automated validation and actual runtime evidence

* Both GRFs compile with NML 0.9.0. The fork compilation reports 64/64 cargo
  items, 117/128 industry items across all economies and 176/255 industry tiles.
* The emitted GRF Action8 identity/name and Action14 numeric version were read
  back from the binary. All **320 emitted cargo slot/label records**, spanning
  all economy branches, match the unmodified compiled baseline.
* All original 91 Classic industry model records are unchanged; only the
  reused steelworks is added. Enabled industry models and cargo ordering in
  the other five economy definitions compare equal. This is model equality,
  not an assertion that incomplete upstream economies have 64 cargoes.
* Generated-NML conditions passed **720** mode/economy/year/route checks;
  a synthetic final-year/permission mask passed **16** checks. Six stockpile
  recipe tests cover missing inputs, complete batches and remainders.
* JGRPP **0.73.4** actually loaded the fork with OpenGFX **8.0** in separate
  fresh **256×256** headless worlds. All **16** runtime cases passed: the
  requested years plus exact gate boundaries, unrestricted 1830, AXIS-spawning
  disabled at 2000, and naturally generated 1830/2000 worlds.
* Runtime tests query and execute both deity and company-mode funding commands.
  A tiny idle AI provides the funded-company identity; no human campaign company
  or transport operation is involved. Before-date builds reject; eligible builds
  succeed. Generated 1830 has zero gated plants; generated 2000 has all three.

Exact reports:
[source/binary validation](../newgrfs/axis-historical-europe/validation-result.json),
[JGRPP runtime results](../newgrfs/axis-historical-europe/runtime-result.json).
The latter records engine and GRF hashes and test output. Local complete logs
are under `.work/runtime-results/`; those logs and engine/base graphics are ignored.

The compiler emitted **724 warnings**, versus **450** for the pristine build.
They include upstream missing/stale translations, optimized identical switch
ranges and unreferenced blocks; the added wrappers and unused generic steelworks
callbacks add optimization/unreferenced warnings. These were not disguised as
a warning-free build. No compiler error occurred. Upstream rendering also reports
existing map-colour and recycling-keystone diagnostics; no ID was renumbered to
silence them.

**Not tested:** actual cargo delivery and steel tonnage in the engine, the
funding-window UI, editor interaction, human three-player join/rejoin,
save/reload/long-term production, 4096² performance or the installed transport
NewGRF stack. Natural gameplay openings over elapsed years were not soaked;
world generation and the shared RANDOM construction path were exercised.
Do not describe this as campaign-ready or fully verified steel production.

## License, remaining scope and next milestone

Pinned AXIS README states all content is GPL v2; its GPL text and original
notices are preserved. The project commits small overlay/patch source, not
third-party artwork or a large GRF. Local `dist/` includes the compiled file
and complete matching corresponding-source ZIP for compliant paired delivery.
No public release was created. See [attribution and distribution instructions](../newgrfs/axis-historical-europe/ATTRIBUTION.md).

Modern aluminium, chemicals, vehicle factories and other non-steel sectors
retain original AXIS availability. This milestone does not claim to make all
1830 industries historically appropriate. Next: test an actual pig-iron/coke
transport route into the new works, verify output/GUI/save-reload in JGRPP,
then extend the manifest sector-by-sector after recipe and historical review.
