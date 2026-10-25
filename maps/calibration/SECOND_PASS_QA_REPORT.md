# Second-pass town spacing and integrity audit

Input: `data/towns/europe_1800_import_TEST.json` (600 towns).

- 600 entries inspected.
- 56 town pairs within 20 tiles on a 4096×4096 map.
- 0 normalized duplicate-name pairs.
- All coordinates are normalized within [0,1]: true.
- All entries have required JSON types: true.

## Close town pairs (under 20 tiles)
- DANZIG (GDANSK) / Gdańsk: 0 tiles
- ELBING (ELBLAG) / Elbląg: 0 tiles
- VIENNE / WIEN: 0 tiles
- BRNO (BRUNN) / Brno: 0.1 tiles
- STETTIN (SZCZECIN) / Szczecin: 0.1 tiles
- BRESLAU (WROCLAW) / Wrocław: 0.2 tiles
- MANCHESTER / SALFORD: 4.6 tiles
- BARMEN / ELBERFELD: 5.2 tiles
- ALTONA / HAMBURG: 7.3 tiles
- FURTH / NURNBERG: 7.3 tiles
- BERLIN / BRANDENBURG: 7.6 tiles
- BOULOGNE / PARIS: 8.3 tiles
- BAEZA / UBEDA: 8.6 tiles
- CALTANISSETA / CASTROGIOVANNI: 8.8 tiles
- AMSTERDAM / ZAANDAM: 10.1 tiles
- BOULOGNE / VERSAILLES: 10.3 tiles
- DELFT / DEN HAAG: 10.5 tiles
- LIER / MECHELEN: 10.7 tiles
- MANCHESTER / STOCKPORT: 11.3 tiles
- HALBERSTADT / QUEDLINBURG: 13.5 tiles
- ANTWERPEN / LIER: 13.6 tiles
- FOSSANO / SAVIGLIANO: 13.6 tiles
- MANCHESTER / OLDHAM: 13.7 tiles
- CREMA / LODI: 14.3 tiles
- Cetinje / Kotor: 14.3 tiles
- ACIREALE / CATANIA: 14.4 tiles
- LOKEREN / SINT NIKLAAS: 14.5 tiles
- CLERMONT-FERRAND / RIOM: 14.6 tiles
- TRIESTE / Koper: 14.6 tiles
- KRAKOW / Wieliczka: 14.7 tiles
- MESSINA / REGGIO DI CALABRIA: 14.7 tiles
- DELFT / ROTTERDAM: 14.8 tiles
- SALFORD / STOCKPORT: 14.9 tiles
- BOLTON / SALFORD: 16.2 tiles
- Sanok / Lesko: 16.2 tiles
- BADAJOZ / ELVAS: 16.4 tiles
- GREENWICH / LONDON: 16.6 tiles
- Jarosław / Przeworsk: 16.7 tiles
- MILANO / MONZA: 16.9 tiles
- HAARLEM / ZAANDAM: 17 tiles
- OLDHAM / SALFORD: 17.2 tiles
- NEWCASTLE / SUNDERLAND: 17.3 tiles
- ARNHEM / NIJMEGEN: 17.5 tiles
- GLASGOW / PAISLEY: 17.5 tiles
- OLDHAM / STOCKPORT: 18.1 tiles
- Wałbrzych / Świdnica: 18.2 tiles
- BOLTON / WIGAN: 18.3 tiles
- FRANKFURT AM / HANAU: 18.4 tiles
- PARIS / VERSAILLES: 18.6 tiles
- Zenica / Travnik: 18.8 tiles
- DEN HAAG / LEIDEN: 18.9 tiles
- Rzeszów / Łańcut: 18.9 tiles
- HEIDELBERG / MANNHEIM: 19 tiles
- ACIREALE / MASCALI: 19.1 tiles
- AALST / LOKEREN: 19.3 tiles
- LUCCA / PISA: 19.5 tiles


## Duplicate names
None

**Important limitation:** This is a geometric QA pass, not a coastline or elevation validation. The original heightmap is available in the working environment, but the existing 29 control points are approximate. No final terrain-safe corrected JSON is claimed here. Towns need coastline/heightmap overlay validation and rotation checks before release.
