# Census research log

> Current project context: [status and limitations](PROJECT_STATUS.md). Population-source research is separate from the 600-record game catalogue; V10 changes no populations. Earlier acquisition statements below retain their original scope.

## Status: first regional source pass (2026-10-25)

### Britain
- 1801 census taken 10 March 1801, with historical report abstracts catalogued by Vision of Britain: https://www.visionofbritain.org.uk/census/1801
- The site's historical statistics are **not currently directly downloadable**. It directs researchers to UK Data Service, searching `gbhd`: https://www.visionofbritain.org.uk/data/
- Next: obtain GBHD access and extract 1801 figures by appropriate historical administrative unit. Do not equate modern cities with historical parishes without checking boundaries.

### Polish lands
- IBS published a dataset covering **974 Polish cities, 1810-2023**, based on archival statistical compilations and additional sources: https://ibs.org.pl/en/resources/historical-data-on-the-population-of-polish-cities/
- Next: download source workbook, check licensing and year coverage for each settlement, import historical observations with exact reference years.

### Prussia / German lands
- ifo iPEHD begins with a **1816 county-level** population census, covering 308 Prussian counties: https://www.ifo.de/en/welcome-ipehd-ifo-prussian-economic-history-database
- Do not mislabel county populations as city populations. Seek city-level observations separately.

### Przemyśl
Two historical secondary sources conflict near our start date:
- Virtual Shtetl reports **6,481 in 1785**, citing G. Karnas, *Przemyśl* (2012): https://sztetl.org.pl/pl/miejscowosci/p/167-przemysl/100-demografia/21611-demografia
- JewishGen's translated Przemyśl Yizkor book reports **2,842 in 1798**, attributed to Kramarz: https://www.jewishgen.org/yizkor/przemysl/prz069.html

**Do not choose an 1800 population yet.** Differences could reflect geographic scope, source methodology, or an error; investigate primary citations and historical boundaries. The original figures and provenance are preserved in `data/historical-populations/przemysl_observations.csv`.

### Data quality rules
- Preserve observation year, geographic unit, source, and observation type.
- Distinguish census counts, reconstructed estimates, and interpolation.
- Keep raw historical numbers separate from game-scaled populations.
- Do not redistribute datasets without checking terms.
