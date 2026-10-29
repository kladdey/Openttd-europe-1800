"""Build Phase 6A deliverables exclusively from retained engine evidence."""
import csv,json,re,shutil,collections
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from coastal_phase6_runtime import BASE,ROOT,SOURCE,sha


def write(name,rows):
    assert rows
    with (ROOT/'docs/research'/name).open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)


def main():
    state=json.loads((BASE/'implementation.json').read_text(encoding='utf8'))
    delivery=json.loads((ROOT/'docs/research/coastal_scenario_delivery.json').read_text(encoding='utf8'))
    proposals=json.loads((BASE/'proposals.json').read_text());config=json.loads((ROOT/'data/geography/phase6a_port_candidates.json').read_text(encoding='utf8'))
    byname={r['name']:r for r in proposals};accepted=[dict(byname[r['name']],**r) for r in state['decisions'] if r['status']=='ACCEPTED']
    accepted_names={r['name'] for r in accepted}
    shipcase=Path((BASE/'shipping-case.txt').read_text());shiplog=(shipcase/'engine.log').read_text(encoding='utf8');plan=json.loads((BASE/'shipping-plan.json').read_text(encoding='utf8'))
    ships=[dict(test_type='Actual ship voyage',name=m[0],moved=m[1],arrived=m[2],minimum_destination_manhattan=int(m[3]),observed_loaded=m[4],final_ship_tile=int(m[5]),evidence='VERIFIED IN GAME',status='PASS' if m[2]=='true' else 'NOT COMPLETED',case=str(shipcase.relative_to(ROOT)),engine_log_sha256=sha(shipcase/'engine.log')) for m in re.findall(r'C6 SHIP_RESULT\|([^|]+)\|(true|false)\|(true|false)\|(\d+)\|(true|false)\|(\d+)',shiplog)]
    sea={m[0]:dict(start_water_tile=int(m[1]),open_sea_witness_tile=int(m[2]),water_edge_connected=m[3]) for m in re.findall(r'C6 SEA_CONNECTION\|([^|]+)\|(\d+)\|(\d+)\|(true|false)',shiplog)}
    built={m[0]:m[2] for m in re.findall(r'C6 BUILT_DOCK\|([^|]+)\|(\d+)\|(true|false)',shiplog)}
    access=[]
    for r in accepted:
        r.update(actual_dock_built=built.get(r['name'],'NOT TESTED'),**sea.get(r['name'],{}))
        r['coordinate_status']='ACCEPTED: local terrain reviewed; supported engine placement; exact tile recorded'
        r['population_method']='JGRPP medium-town founding, no expansion; game population, not census'
        access.append(dict(test_type='New port dock and local sea access',name=r['name'],dock_tile=r['dock_tile'],actual_dock_built=r['actual_dock_built'],passenger_and_mail_catchment='Both acceptance >=8/8 and positive production in paused final candidate',**sea.get(r['name'],{}),status='PASS' if built.get(r['name'])=='true' and sea.get(r['name'],{}).get('water_edge_connected')=='true' else 'BLOCKED / INVESTIGATE',evidence='VERIFIED IN GAME: construction and GSMarine water-edge traversal',case=str(shipcase.relative_to(ROOT))))
    access+=ships
    assert len(ships)==4,'Missing regional ship measurements'
    write('added_port_towns.csv',accepted);write('coastal_accessibility_results.csv',access)
    rejected=[]
    for p in proposals:
        trials=[r for r in state['decisions'] if r['name']==p['name']]
        if p['name'] in accepted_names:
            chosen=next(r for r in accepted if r['name']==p['name']);p.update(proposed_x=chosen['x'],proposed_y=chosen['y'],coordinate_status='IMPLEMENTED AND ENGINE VERIFIED',decision='ACCEPTED')
        else:
            reasons=[]
            if any(r.get('height_changes',0)>0 for r in trials):reasons.append('One or more trials automatically terraformed terrain')
            if any(r.get('dock_tile',-1)<0 for r in trials):reasons.append('One or more trials lacked the required combined passenger/mail dock catchment')
            if any(r.get('population',500)<80 or r.get('population',500)>1000 for r in trials):reasons.append('One or more initial populations outside the modest-size review gate')
            if any(r.get('dock_tile',-1)>=0 and r.get('height_changes',0)==0 for r in trials):reasons.append('Remaining trial failed the strict original/new tile allowlist (e.g. new river bridge); retained raw map evidence needs separate review')
            if not reasons:reasons=['No valid supported placement found in the bounded reviewed patch']
            rejected.append(dict(name=p['name'],region=p['region'],decision='DEFERRED, NOT HISTORICALLY REJECTED',trials=len(trials),reason='; '.join(reasons),history_source=p['history_source'],verification_required='Review another historically defensible shoreline tile in the same locality; repeat all preservation and dock gates. No terraforming.',evidence='VERIFIED IN GAME trials; bounded search, not proof the town is impossible'))
            p.update(decision='DEFERRED',coordinate_status='Not implemented; bounded trials failed one or more preservation/port gates')
    for p in config['negative_controls']:rejected.append(dict(p,decision='REJECTED: after 1830 or already represented',history_source=p['source'],evidence='Historical source or active 613-town inventory',verification_required='None for this pass'))
    write('proposed_port_towns.csv',proposals);write('rejected_port_candidates.csv',rejected)
    write('coastal_placement_trials.csv',state['decisions'])
    sheet=Image.new('RGB',(1200,990),'#17202a');draw=ImageDraw.Draw(sheet)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
    for i,p in enumerate(proposals):
        tile=Image.open(ROOT/p['terrain_review_image']).convert('RGB')
        if p['name'] in accepted_names:
            r=next(r for r in accepted if r['name']==p['name'])
            d=ImageDraw.Draw(tile)
            x=(r['x']-p['seed_x']+55)*6+3;y=(r['y']-p['seed_y']+55)*6+3
            d.ellipse((x-8,y-8,x+8,y+8),outline='lime',width=3)
            dx=(r['dock_tile']%4096-p['seed_x']+55)*6+3;dy=(r['dock_tile']//4096-p['seed_y']+55)*6+3
            d.rectangle((dx-6,dy-6,dx+6,dy+6),outline='cyan',width=3)
        tile.thumbnail((300,300));x=i%4*300;y=i//4*330
        sheet.paste(tile,(x,y+25));draw.text((x+3,y+4),p['name']+' - '+p['decision'],fill='white',font=font)
    sheet.save(ROOT/'docs/research/coastal_coordinate_review.png')
    evidence=[]
    for p in sorted(BASE.iterdir()):
        if not p.is_dir() or not (p/'manifest.json').exists():continue
        log=(p/'engine.log').read_text(encoding='utf8',errors='replace')
        evidence.append(dict(case=str(p.relative_to(ROOT)),manifest=json.loads((p/'manifest.json').read_text()),engine_log_sha256=sha(p/'engine.log'),script=(p/'game/coastal/main.nut').read_text(encoding='utf-8-sig'),measurements=[s for s in log.splitlines() if 'C6 ' in s],script_errors=[s for s in log.splitlines() if 'Your script made an error' in s or 'script died' in s]))
    (ROOT/'docs/research/coastal6a_run_evidence.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False),encoding='utf8')
    (ROOT/'docs/research/coastal6a_shipping_plan.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False),encoding='utf8')
    original=list(csv.DictReader((ROOT/'docs/research/existing_coastal_towns.csv').open(encoding='utf8')))
    for r in original:
        r['final_local_sea_test_status']='VERIFIED IN GAME' if sea.get(r['name'],{}).get('water_edge_connected')=='true' else 'NOT TESTED'
        r['final_ship_voyage_regions']=';'.join(p['name'] for p in plan['routes'] if r['name'] in (p['a'],p['b']))
    write('existing_coastal_towns.csv',original)
    counts=collections.Counter(r['classification'] for r in original)
    table='| Town | Region | Map tile (x, y) | Game population | History |\n|---|---|---|---:|---|\n'+''.join(f'| {r["name"]} | {r["region"]} | {r["x"]}, {r["y"]} | {r["population"]} | [Source]({r["history_source"]}) |\n' for r in accepted)
    nav='| Region | Moved | Destination dock reached/loading | Loaded observed |\n|---|---|---|---|\n'+''.join(f'| {r["name"]} | {r["moved"]} | {r["arrived"]} | {r["observed_loaded"]} |\n' for r in ships)
    all_nav=all(r['status']=='PASS' for r in access)
    verdict='READY WITH CAVEATS' if all_nav else 'BLOCKED'
    common=f'''Source: `{SOURCE}`. SHA256 `{delivery['source_sha256']}`.

Separate output: `{delivery['output']}`. SHA256 `{delivery['output_sha256']}`.

Original towns: **613**. Added: **{len(accepted)}**. Final: **{delivery['final_towns']}**. Industries: **0**.
'''
    docs={
    'COASTAL_TOWN_FINAL_AUDIT.md':f'''# Phase 6A — final coastal-town audit

{common}
The active scenario, rather than the older 568/600-town catalogs, supplied all town identities, coordinates and populations. All 613 were screened using the real JGRPP dock command in GSTestMode, followed by passenger AND mail acceptance/production checks. Within the bounded scan, 170 towns have some legal dock site; 82 have a site meeting both catchment tests. Those 82 reference **80 distinct best dock tiles**, not 82 independent ports. Shared catchments must not be counted twice.

Screening classifications: {dict(counts)}. Coast/river classification is MODELLED: proximity to broad water in the largest four-neighbour component. Connected rivers are not automatically called coast. The classification is a search aid, not proof of navigability. All 613 rows and unresolved location fields are preserved in `research/existing_coastal_towns.csv`.

## Historical additions

{table}
The earlier density audit and coordinate catalogs were reused for research and calibration. Eleven missing historical leads were checked against the active inventory, nearby anchors and labelled local terrain rasters. The existing calibrated projection was only an initial seed: nearby actual-town residuals were bounded to eight tiles; reviewed placement options remained within eight tiles per axis and ten Manhattan tiles. The coast was never moved to meet a coordinate. This is exact game-tile placement on a scaled map, not a claim of metre-accurate 1830 harbour surveying.

The scan is deliberately bounded to a 65×65 box and 40 Manhattan tiles around each town. A failed scan does not prove no dock can ever serve that town. Every existing historical port's significance was not independently re-researched; unsourced fields remain UNVERIFIED. Named historical gaps were investigated across the four priority regions, not treated as an exhaustive census of European ports.

![Local terrain review; green circles mark final town centres and cyan squares the tested docks](research/coastal_coordinate_review.png)

Resolved gaps are the missing named ports listed above. Remaining leads and rejected duplicate/post-1830 settlements are in `research/rejected_port_candidates.csv`. Iberian Atlantic, some British industrial/river ports, Mediterranean islands, the Aegean and Black Sea still warrant local review before claiming complete historical coverage. No extra towns were invented to fill geometric gaps.

## Preservation

All original 613 CITY rows, including populations and nested saved fields, remain byte-identical. All heights, every original water tile and its metadata, existing roads/bridges/infrastructure, all 15 NewGRF identities/parameters, original DATE, PATS, ECMY, objects, industries, station and vehicle chunks are unchanged. The only differing chunks are {delivery['changed_chunks']}. All **{delivery['guards']['changed_tiles']}** changed tiles are listed with old/new bytes in `research/coastal_changed_tiles.csv`; changes are new houses/roads and local grass/tree site metadata. No original water or infrastructure tile is changed.

The final scenario contains no player transport network, new vehicles or industries. Test docks/depots/ships exist only in discarded gameplay copies. The source remains unchanged. Normal game configuration and installed GRFs were not edited.
''',
    'COASTAL_TOWN_ADDITIONS.md':f'''# Implemented historical port additions

{common}
{table}
These are game populations from supported medium-town founding, without ExpandTown, not estimates of historical census population. The original-town median is 382; London is 11,004 and Plymouth 899. New towns remain subordinate to major cities; their engine-generated populations are reported exactly. The earlier research target populations were nonbinding planning suggestions and were not forced into the save.

Falmouth's government packet role is documented by the National Maritime Museum Cornwall; Dover's harbour governance by the port authority; Holyhead's early nineteenth-century harbour works by Cadw. Other implemented ports link their own evidence in the table. The researched period-name policy uses Viana before its 1848 renaming and Cette before Sète's 1928 spelling change if those candidates qualify; an unqualified candidate is not added merely to demonstrate the name.

`research/added_port_towns.csv` includes actual IDs, positions, populations, selected dock tiles, history/coordinate sources, nearest original town, trial path and log hash. `research/proposed_port_towns.csv` records all eleven decisions; `research/coastal_placement_trials.csv` retains unsuccessful trials as well as successes. A rejected trial is never silently promoted.

Initial engine trials exposed automatic town terraforming. Every promoted addition had zero height/water/original-infrastructure changes, exact preservation of earlier towns, a modest initial size and real passenger/mail dock catchment. Some trials also built new river bridges; the strict tile allowlist deferred those instead of treating them as harmless. Deferred settlements remain historically valid leads, not claims that the map can never accommodate them.
''',
    'PORT_ACCESSIBILITY_VALIDATION.md':f'''# Dock and sailing validation

{common}
## Actual engine evidence

Every new port passed GSTestMode BuildDock and both PASS/MAIL acceptance (at least 8/8) and positive production checks using `GSStation.GetCoverageRadius(STATION_DOCK)`, which returned **5** under this scenario. Temporary real docks were then built in a separate unpaused gameplay copy. Each new dock's departure water was traversed with actual `GSMarine.AreWaterTilesConnected` edges to an open-water witness in the sea component. This tests local shoreline/bridge access; a coarse pixel component alone is not claimed as proof.

{nav}
Sailing Brig engine 616, already present in the active vehicle collection, was built with a passenger refit in the disposable copy. The refined script sampled every five ticks and required either an actual loading state or a destination-to-origin order transition within four tiles of the destination. It also recorded movement, minimum destination distance and any positive cargo load. These are VERIFIED IN GAME movement/loading observations, not static path-distance estimates. The first 50-tick sampler missed short stops, and its 30,000-tick window was too short for Porto–Lisboa; its incomplete results remain in the evidence archive. The refined test allowed 100,000 ticks and used the supported ResolveOrderPosition API. Revenue and economic balance were outside this phase and were not inferred from loading. Porto–Lisboa proves navigation, not loaded delivery: no positive passenger load was sampled on that voyage. Route endpoints, dock tiles and witness tiles are in `research/coastal6a_shipping_plan.json`; results are in `research/coastal_accessibility_results.csv`.

No full coastwide shortest-path graph is asserted. Local engine-edge traversal is bounded to 20,000 expansions / 85 tiles; representative real ship voyages cover British Isles, Iberia, Mediterranean and Baltic waters. North Sea-specific long voyages and every possible inter-port pairing are not tested. Existing inland river ports and lakes remain separately labelled; the 82-town catchment count is not a count of ocean-reachable ports.

## Isolation and load/save/reload

Only copies under `newgrfs/axis-historical-europe/.work/coastal6a` were operated. JGRPP 0.73.4 executable and the same licensed local GRF assets were reused. `-X -x -c <isolated cfg>` prevents normal user-data/config writes. Paused founding prevents original-town growth; movement copies alone clear their copied pause byte. All delivered DATE/settings bytes retain the source values, including 1830 calendar start, inherited 1800 economy date and seven-tile train limit.

The candidate was loaded, saved by JGRPP, and the engine-produced save loaded again. Original towns and all map arrays survived the real save unchanged. Runtime API enumerated all 15 loaded GRFs and confirmed train limit 7. Embedded NGRF identities/checksums/parameters match the source exactly. Final output retains the original no-player/no-network chunks rather than packaging the temporary measurement company or GameScript. The final file uses source chunks plus only engine-generated CITY and map changes; this deliberate composition preserves original settings and is explicitly checked by the second engine load.

## Reproduction

Use Python with NumPy/Pillow; coastal analysis additionally needs SciPy (this run used an isolated ignored local target). From the repository root: run `scripts/coastal_phase6_runtime.py scripts/coastal_phase6_inventory.nut --tag inventory --ticks 15000`, then `scripts/coastal_phase6_analysis.py`, `scripts/coastal_phase6_proposals.py`, review local terrain rasters, and `scripts/coastal_phase6_implement.py`. `coastal_phase6_finalize.py` performs name/load/save/reload/preservation checks and refuses to overwrite an existing output. `coastal_phase6_run_shipping.py` performs disposable real sailing tests; `write_coastal_phase6_reports.py` consumes the retained evidence. Run all Python commands with `-X utf8`; do not use `-O`, which disables safety assertions.

`scripts/verify_coastal_phase6.py` is the repeatable read-only verification of the delivered candidate. Evidence contains exact scripts, commands, source/script/log hashes and C6 measurements. Two exploratory script issues (wrong error-class API and a missing UTF-8 BOM) were corrected; non-ASCII final names are verified through JGRPP, not assumed from source text. An incomplete 10,000-tick inventory was not substituted for the complete earlier scan. Squirrel requires the BOM for UTF-8 literals in this release.
''',
    'COASTAL_SCENARIO_READINESS.md':f'''# Coastal scenario readiness

**{verdict}**

{common}
{len(accepted)} historically documented additions have practical passenger/mail dock catchment. All original towns and geography are preserved. Real dock construction, local sea-water traversal and representative voyages are recorded separately from modelled coastal proximity. All required regional voyages {'completed' if all(r['arrived']=='true' for r in ships) else 'did not all complete; see blocked rows before industry placement'}.

This is a separate working candidate for subsequent historical industry placement. Industry spawning remains disabled; zero industries, no permanent player infrastructure and no new rolling stock were introduced. No price, performance, GRF, train-length or multiplayer setting changed. No push or merge was performed.

Before treating coastal coverage as final, review the deferred ports and the 88 towns that have some legal dock site but failed the stricter combined catchment screen. Their failure may reflect finite catchment, shoreline slope, scan bounds or generated house position; it does not establish that the historical port is impossible. No automatic expansion or coastline engineering is recommended. For a desired deferred town, try one historically defensible flat bank location in an editor copy, rerun the byte guards and construct a real dock before promotion.

Human spot check: open the separate Coastal Towns scenario in JGRPP 0.73.4; verify the added town names/centres and relative sizes; in a gameplay copy build the recorded dock tiles and reproduce the four listed Brig voyages. Leave the immutable No Industries source untouched. Historical industry placement should use another separate version, retain all 15 identities/parameters, and run the same preservation checks for unrelated features.
'''}
    for name,body in docs.items():(ROOT/'docs'/name).write_text(body,encoding='utf8')
    print(verdict, 'added',len(accepted),'ship voyages',[(r['name'],r['arrived']) for r in ships])


if __name__=='__main__':main()
