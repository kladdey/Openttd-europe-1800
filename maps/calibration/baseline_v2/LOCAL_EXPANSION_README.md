# V2 local expansion - 15-town test

**STATUS: EXPERIMENTAL / UNVERIFIED.** The five original V2 baseline anchors are unchanged. Ten nearby towns are placed by applying the displacement of their nearest chosen baseline anchor to their original normalized OpenTTD coordinates. This is a **local translation hypothesis**, not a georeferenced projection or a verified fix. In particular, cities can be misplaced even if the anchor is broadly in the right region.

Original five: London, Dublin, Paris, Berlin, Stockholm. New test cities: OXFORD, CAMBRIDGE, READING, KILKENNY, WATERFORD, VERSAILLES, BOULOGNE, POTSDAM, BRANDENBURG, MAGDEBURG.

**How to test:** In a *fresh empty* scenario using the same original 4096x4096 heightmap, load the JSON through JGRPP Town Generation > Load from file. Do not import on top of the five-town test or the playable scenario. Inspect every new town's landmass and position, especially coastal towns. Report failures before expanding.

No changes were made to the master 600-town dataset or playable .scn.
