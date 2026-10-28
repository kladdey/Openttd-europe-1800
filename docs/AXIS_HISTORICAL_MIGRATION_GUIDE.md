# Historical AXIS migration guide

**Do not replace stock AXIS in the working Europe scenario.** No validated direct conversion exists. The current fork uses a distinct GRFID, and 463 existing instances conflict with its draft 1830 policy. Availability gates intentionally leave existing industries operating.

## Safe procedure available now

1. Keep the original scenario, saves, installed AXIS and normal configuration unchanged. Build the historical binary into the fork's ignored `dist/` directory. Retain the matching source ZIP and attribution.
2. Use a separate portable JGRPP 0.73.4 installation beneath `.work`, with its own config/user-data path. Copy the exact 14 other campaign NewGRFs into this isolated library. Enable **Historical Europe instead of stock AXIS**, Extreme Classic, history on; retain their recorded vehicle parameters and the seven-tile limit.
3. Start a **new** small 1830 map with this list from the outset. This path has actually passed engine tests and loaded deliveries. It is the usable independent prototype; it is not the converted Europe campaign.
4. For Europe, create a **new editor scenario from the authoritative original heightmap/geography assets** with the historical list selected before industry placement. Recreate or import towns using the project's supported geography workflow. Place historically eligible industries through supported editor/game construction, validating producer/consumer geography. Preserve the original map as the fallback, and save under a new candidate name.
5. Check at least coal→coke, ore/coke→pig iron→iron works, forest→sawmill, farms→food/textiles/construction, town passenger/mail services and coastal access. Account for optional modern-input concessions. Keep enough independent opportunities for all three players; 924 potentially eligible old sites do not automatically constitute a validated new distribution.
6. Verify all 15 identities (14 original plus historical AXIS), 64 cargo slots/refits, complete industry and tile inventory, graphics, station acceptance, funding restrictions, save/load and three-player join/rejoin. Only then consider promoting the new candidate in a separately approved deployment task.

No disposable Europe scenario was fabricated by changing a saved `NGRF` chunk or by relabeling a save file. The fresh 256² runtime worlds and their saves are disposable test assets, not a Europe migration deliverable. A clean Europe editor rebuild is a recommended supported workflow; it has **not** been executed or certified in this phase.

## Before deciding on direct conversion

A proposed converter would need to prove stock-to-fork industry **and industry-tile** mapping, preserve cargo mappings and all original IDs/layouts, handle the new industry and existing future-dated sites, then pass engine round-trip and real production tests. A successful file load alone is insufficient. There is no ordinary GameScript API here that can safely replace all existing industries and their identity mappings. Do not bypass loader warnings, patch the engine or write an ad-hoc binary identity substitution to avoid the rebuild.

The smallest next step is a tiny editor candidate and manual construction checks, followed by one geographically limited Europe candidate. Keep full-continent regional scheduling and detailed process differentiation separate until these compatibility gates pass.
