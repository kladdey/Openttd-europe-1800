# IBS Polish city population dataset - acquisition status

> Current project context: [status and limitations](../../docs/PROJECT_STATUS.md). Population-source research is separate from the 600-record game catalogue; Placement work changes no populations. Earlier acquisition statements below retain their original scope.

**Status: source located; raw workbook not yet imported.**

Publisher: Instytut Badań Strukturalnych (IBS), Jan Frankowski, published 3 December 2024.

Official landing page: https://ibs.org.pl/en/resources/historical-data-on-the-population-of-polish-cities/

Direct XLSX: https://ibs.org.pl/wp-content/uploads/2024/12/baza_danych_dane_historyczne_o_liczbie_ludnosci_polskich_miast.xlsx

The publisher describes population histories for 974 Polish cities, 1810-2023, derived from digitized IGiPZ PAN / Statistics Poland tables, GUS BDL, and scattered sources. **974 is the count of cities in the workbook, not the count of observations in 1810**.

The official workbook link resolves but the retrieval environment could not download XLSX bytes. No data rows have been extracted or matched; do not treat this source as imported.

Historical geographic caveats:
- These are cities of present-day Poland, not all cities within Polish political borders in 1800.
- Historical Przemyśl was in Habsburg Galicia; Polish border changes and city-boundary changes need handling.
- Source begins in 1810, not 1800. Keep actual observation years; never relabel them as 1800 census.

Next:
1. Download the workbook from the official link.
2. Inspect its sheets, headers, city identifiers, population units, and blank-cell conventions.
3. Extract a long-form city/year/population table while preserving original workbook and source attribution.
4. Normalize names and join to the scenario's town inventory; review ambiguous matches manually.
5. Cross-check historical year and territory before producing gameplay populations.

Underlying reference: Adam Jelonek, *Liczba ludności miast i osiedli w Polsce w latach 1810-1955* (1956), https://www.rcin.org.pl/dlibra/publication/50580/edition/47399. Source is marked copyright-protected; do not redistribute the original scan.
