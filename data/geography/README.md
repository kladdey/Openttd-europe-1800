# Geographic calibration evidence

`ne_50m_europe_coastline.geojson` is a derived subset of Natural Earth's
1:50m coastline, not a town gazetteer or exact historic coastline.

- Repository: `nvkelso/natural-earth-vector`.
- Source path: `geojson/ne_50m_coastline.geojson`.
- Retrieved source blob: `4ead47f5323a3a71495a12442ba936c969b6fae2`.
- Repository head at retrieval: `ca96624a56bd078437bca8184e78163e5039ad19`.
- [Pinned source](https://github.com/nvkelso/natural-earth-vector/blob/ca96624a56bd078437bca8184e78163e5039ad19/geojson/ne_50m_coastline.geojson).
- [Public-domain terms](https://www.naturalearthdata.com/about/terms-of-use/).
- Subset SHA-256: `f5d53fa83d12ee15a5e56e081651ec72ec45a29a30b7340e7250c8af6c83cc3f`.

Subset procedure: retain contiguous LineString coordinate runs with longitude
in [-13,36] and latitude in [30,65], discard runs shorter than two vertices,
and do not connect disconnected runs across the crop. Preserve original
vertex order and coordinates; replace descriptive feature properties with
`source: Natural Earth 1:50m coastline`. The committed file contains 153
LineStrings (151038 bytes), so reproduction needs no network request.

`regional_coordinate_overrides.csv` explicitly corrects Brandenburg to the
published approximate coordinate for Brandenburg an der Havel (52.417N,
12.533E), instead of the draft's Berlin-adjacent location. This is a regional
coordinate correction, not a population change or a training control.
The original catalogue and draft CSV remain untouched. Other draft town
coordinates are carried through provisionally, not silently declared surveyed.

Boulogne remains deferred. The draft position describes a Paris suburb, but
the source de Vries entry has 12,000 people in 1800. That estimate is confirmed
by [World City Populations' source index](https://worldcitypop.com/data_source.asp?disp_city=Boulogne&disp_time=1800).
Historical series list 2,481 for Boulogne-Billancourt in 1800 versus 10,685
for Boulogne-sur-Mer, supporting the coastal-town interpretation:
[Billancourt series](https://fr.wikipedia.org/wiki/Boulogne-Billancourt),
[sur-Mer series](https://commons.wikimedia.org/wiki/Data:Population_%E2%80%93_Boulogne-sur-Mer_%E2%80%93_Pas-de-Calais_%E2%80%93_INSEE_62160.tab).
This is a strong inference, not a completed primary-source identity join;
the workflow does not silently substitute another town.
