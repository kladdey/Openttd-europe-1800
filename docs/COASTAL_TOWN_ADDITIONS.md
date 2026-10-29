# Implemented historical port additions

Source: `C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.2.0 - No Industries.scn`. SHA256 `9b4dbd70e27653fcb72d5778993988d257d5f83adcaf4a394c01af110d366735`.

Separate output: `C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.2.0 - Coastal Towns.scn`. SHA256 `6c7a7b8ccbf72a744102ab06df755d119d692ca435e397e1bbbac3267ee1b60d`.

Original towns: **613**. Added: **4**. Final: **617**. Industries: **0**.

| Town | Region | Map tile (x, y) | Game population | History |
|---|---|---|---:|---|
| Falmouth | British Isles / Cornwall | 3248, 1502 | 511 | [Source](https://nmmc.co.uk/object/cornish_maritime_collection/a-packet-captains-telescope/) |
| Dover | British Isles / Channel | 2579, 1334 | 825 | [Source](https://www.portofdover.com/corporate/about/history-heritage/) |
| Holyhead | British Isles / Wales | 3193, 983 | 413 | [Source](https://cadw.gov.wales/sites/default/files/2019-05/Holyhead-%20Understanding%20Urban%20Character_0.pdf) |
| Tarragona | Iberia / Mediterranean Spain | 2581, 2974 | 887 | [Source](https://www.porttarragona.cat/en/port-city/port-archive) |

These are game populations from supported medium-town founding, without ExpandTown, not estimates of historical census population. The original-town median is 382; London is 11,004 and Plymouth 899. New towns remain subordinate to major cities; their engine-generated populations are reported exactly. The earlier research target populations were nonbinding planning suggestions and were not forced into the save.

Falmouth's government packet role is documented by the National Maritime Museum Cornwall; Dover's harbour governance by the port authority; Holyhead's early nineteenth-century harbour works by Cadw. Other implemented ports link their own evidence in the table. The researched period-name policy uses Viana before its 1848 renaming and Cette before Sète's 1928 spelling change if those candidates qualify; an unqualified candidate is not added merely to demonstrate the name.

`research/added_port_towns.csv` includes actual IDs, positions, populations, selected dock tiles, history/coordinate sources, nearest original town, trial path and log hash. `research/proposed_port_towns.csv` records all eleven decisions; `research/coastal_placement_trials.csv` retains unsuccessful trials as well as successes. A rejected trial is never silently promoted.

Initial engine trials exposed automatic town terraforming. Every promoted addition had zero height/water/original-infrastructure changes, exact preservation of earlier towns, a modest initial size and real passenger/mail dock catchment. Some trials also built new river bridges; the strict tile allowlist deferred those instead of treating them as harmless. Deferred settlements remain historically valid leads, not claims that the map can never accommodate them.
