# Review of the 17 V13 deferred towns

No import file or existing town coordinate is changed by this review. Two candidates merit a new import test, while all 17 remain excluded from V13.

Randers: St Martin’s Church, built 1494–1520 on an earlier church site. Published reference 56.46000, 10.03500; nine probes clear, non-flat target, nearest town Aarhus about 52.2 tiles. Source: https://en.wikipedia.org/wiki/St_Martin%27s_Church%2C_Randers

Sligo: the medieval abbey site in the historic town, used as a burial ground during the eighteenth century; not an operating monastery in 1800. Reference 54.270809, -8.470091; nine probes clear and flat target, nearest town Derry 169 tiles. History: https://heritageireland.ie/places-to-visit/sligo-abbey/ ; coordinate source in review.json.

Helsingør remains a spacing hold, about 9.2 tiles from Helsingborg. Faro, Lagos, Ajaccio, Alghero, Stirling, Dumfries, Lucerne, Constantine, Salerno and Corfu still fail the base target at the tested landmark. Setúbal, Bastia and Oban pass the base but fail sensitivity probes. Tralee needs a defensible earlier reference; its current courthouse is dated 1830–1835 by https://www.buildingsofireland.ie/buildings-search/building/21003276/court-house-ashe-street-tralee-tralee-county-kerry and was not substituted.

Lagos uses the diocese’s Santa Maria church coordinates (37°6′0.58″N, 8°40′14.52″W), with its history supported by https://turismo.diocese-algarve.pt/vigararias/item/157-paroquia-de-lagos-santa-maria . Dumfries uses the University of Glasgow’s medieval church-site reference https://saintsplaces.gla.ac.uk/place.php?id=1359555550 ; this grid-derived site point differs slightly from the listed building footprint, and neither implies survey precision. Lucerne uses St Leodegar’s church: history https://hofkirche-rundgang.kathluzern.ch/geschichte and coordinate source in review.json.

All alternative coordinates were chosen from named historic features, not a search for clear tiles. Frozen V6 calibration, exact float32/truncation conversion and both supplied scenario terrain arrays are reused. See review.json for base samples, probe counts, original statuses and reference displacement in raster pixels. Probe counts are deterministic sensitivity checks, not probabilities or true uncertainty bounds. These are source scenarios, not the user’s saved V13 map. Land clarity does not establish a historically correct bank or founding success.

The user confirmed 613 towns and supplied a matching count screenshot, plus a close view showing separate Braga and Guimarães buildings. This validates aggregate import count and visible separation, not every town’s exact geography or long-term growth.
