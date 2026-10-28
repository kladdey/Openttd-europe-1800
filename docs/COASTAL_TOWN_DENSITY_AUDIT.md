# Coastal town density and 1830 maritime playtest — audit proposal

Status: **observations and candidates only; no map or scenario changes authorized**. Recorded 2026-10-28.

## Player observations and motivation

- In the current Europe 1830 scenario, the Iberian Peninsula appears sparse; the player will inspect it again before deciding where to add towns.
- Britain has too few obvious coastal town-to-town shipping connections for satisfying early gameplay.
- The campaign starts in **1830**; the first approximately **two years** are intended to emphasize ships and horse-drawn transport before trains become available in the chosen vehicle setup.
- The project uses a **4096×4096 Europe map**. The last user-verified **V12 baseline has 568 towns**; an offline **V13 613-town candidate** is not yet verified as the active scenario. Do not confuse either with the latest local scenario.
- Hypothesis, **not yet demonstrated by a spatial audit**: coastal settlement coverage may be too sparse for the intended maritime economy. Do not automatically add towns uniformly across Europe.

## Recommended scope

Prioritize a **historically grounded coastal-town and port-access audit** for Great Britain, Ireland, Iberia, Scandinavia, the Baltic, northern France/Low Countries, and the Mediterranean. Check inland settlement gaps separately, especially central Iberia. Preserve genuine differences in historical settlement density between regions.

### British candidate settlements to compare against the actual scenario

These are **audit candidates, not confirmed missing towns**. Verify 1830 settlement relevance, map placement and existing entries before adding anything.

- English Channel / south: Dover, Folkestone, Hastings, Brighton, Portsmouth, Southampton, Weymouth, Plymouth, Falmouth.
- East coast: Harwich, Great Yarmouth, Lowestoft, King's Lynn, Hull, Whitby, Scarborough, Newcastle, Sunderland.
- West coast / Bristol Channel: Bristol, Gloucester, Cardiff, Swansea, Liverpool, Lancaster, Barrow, Whitehaven.
- Scotland: Aberdeen, Dundee, Leith, Greenock, Ayr, Oban, Inverness, Wick.
- Wales: Holyhead, Caernarfon, Aberystwyth, Milford Haven, Pembroke.

Note: Some listed settlements are river/estuary ports, not strictly open-coast towns; assess navigability and usable water tiles. Some place names or settlement significance may need period-specific review.

### Iberian candidate settlements to compare

- Galicia: Lugo, Ourense, Pontevedra, Ferrol, Santiago de Compostela.
- Asturias/Cantabria: Oviedo, Gijón, Avilés, Santander, Torrelavega.
- Castile/León: Burgos, León, Palencia, Zamora, Salamanca, Valladolid, Segovia.
- Aragón/Navarra: Huesca, Teruel, Calatayud, Tudela.
- Extremadura: Cáceres, Badajoz, Mérida, Plasencia, Trujillo.
- Castilla-La Mancha: Toledo, Cuenca, Ciudad Real, Albacete, Talavera.
- Andalusia: Córdoba, Jaén, Úbeda, Linares, Jerez, Cádiz, Algeciras, Ronda.
- Portugal: Braga, Guimarães, Viana do Castelo, Vila Real, Bragança, Viseu, Guarda, Castelo Branco, Évora, Beja, Portalegre, Faro.

Many Iberian candidates are inland; use them for a separate regional-coverage review, not as maritime-port candidates. In particular, verify mining/industrial significance for AXIS freight routes.

## Required audit method before editing

1. Extract the **actual active scenario's** town names, coordinates and populations. Do not infer missing towns from an older V12/V13 list.
2. Plot existing coastal/estuarine settlements and measure practical shipping gaps, considering sea access and navigable rivers.
3. Cross-check candidate settlements against historical existence and relevance around 1830, not just modern population.
4. Check map-coordinate calibration against established landmarks; never invent tile coordinates.
5. Check that a dock can actually be placed nearby: accessible water, shore geometry, buildable tiles and realistic approach without major terraforming.
6. Prioritize useful short/medium coastal routes and industry connections, rather than filling every gap with a town.
7. Propose a ranked, deduplicated addition list with rationale and before/after maps, including likely gameplay benefits and any terrain conflicts.
8. Review the proposal with the user **before** editing towns, terrain or scenario files.

## Guardrails

- No automatic mass additions, no invented coordinates and no assumption that all candidates are missing.
- Keep the working scenario, verified V12 baseline and historical town catalogues intact.
- Prefer small historically appropriate ports where justified; towns do not need to be large to support coastal shipping.
- Validate map access in JGRPP, not merely apparent proximity to coastline.
- Do not modify the 1830 start, industry system, NewGRF configuration or multiplayer settings as part of this audit.

## Next action

After the player's next visual inspection, compare the current scenario against these candidates, beginning with Britain and Iberian coastal gaps. Produce a proposed change set only; await approval for town placement.
