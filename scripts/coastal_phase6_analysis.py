"""Actual-town coastal screening; coarse water components are NOT ship paths."""
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'newgrfs/axis-historical-europe/.work/coastal6a'
sys.path.insert(0,str(BASE/'python-packages'))
from scipy import ndimage
from scenario_geography import read_terrain
from coastal_phase6_runtime import SOURCE, EXPECTED, sha


def key(s):return ''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if c.isalnum())


def write(name,rows):
    assert rows
    with (ROOT/'docs/research'/name).open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)


def main():
    assert sha(SOURCE)==EXPECTED
    case=max((p for p in BASE.glob('inventory-*') if p.is_dir() and 'C6 DONE towns=613 industries=0' in (p/'engine.log').read_text(encoding='utf8',errors='replace')),key=lambda p:p.stat().st_mtime)
    text=(case/'engine.log').read_text(encoding='utf8',errors='replace')
    assert 'C6 DONE towns=613 industries=0' in text
    towns={};docks={}
    for line in text.splitlines():
        if 'C6 TOWN|' in line:
            i,n,x,y,p=line.split('C6 TOWN|')[1].split('|');towns[int(i)]=dict(town_id=int(i),name=n,x=int(x),y=int(y),population=int(p))
        if 'C6 DOCK|' in line:
            values=list(map(int,line.split('C6 DOCK|')[1].split('|')));docks[values[0]]=values[1:]
    assert len(towns)==len(docks)==613
    types,heights=read_terrain(SOURCE)
    np.save(BASE/'types.npy',types);np.save(BASE/'heights.npy',heights)
    water=types==6
    labels,count=ndimage.label(water)
    sizes=np.bincount(labels.ravel());sizes[0]=0;sea=int(np.argmax(sizes))
    np.save(BASE/'water_components.npy',labels)
    distance=ndimage.distance_transform_edt(~water)
    # Connected rivers belong to the same component as the sea. Do not call
    # every Rhine-side town coastal: also measure distance to broad open water.
    interior=ndimage.distance_transform_edt(water)
    open_water=(labels==sea)&(interior>=6)
    del interior
    open_distance=ndimage.distance_transform_edt(~open_water)
    geos={}
    with (ROOT/'data/towns/europe_1800_towns_600_DRAFT.csv').open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f):geos[key(r['name'])]=r
    for file in ['gap_additions_v1.json','coverage_additions_v1.json']:
        d=json.loads((ROOT/'data/geography'/file).read_text())
        for r in d.get('records',[]):geos[key(r.get('export_name',r.get('name','')))]=r
    rows=[]
    for i,t in towns.items():
        attempted,legal,tile,dd,pp,mp=docks[i]
        geo=geos.get(key(t['name']),{})
        local=labels[max(0,t['y']-40):t['y']+41,max(0,t['x']-40):t['x']+41]
        near_sea=bool(np.any(local==sea))
        coastal=bool(open_distance[t['y'],t['x']]<=40)
        t.update(latitude=geo.get('latitude','UNVERIFIED'),longitude=geo.get('longitude','UNVERIFIED'),
                 region=geo.get('region','UNVERIFIED'),historical_location_source=geo.get('coordinate_source',geo.get('source','UNVERIFIED')),
                 nearest_water_euclidean_tiles=round(float(distance[t['y'],t['x']]),2),
                 coast_tiles_tested=attempted,legal_dock_sites=legal,practical_dock_tile=tile,
                 practical_dock_x=tile%4096 if tile>=0 else '',practical_dock_y=tile//4096 if tile>=0 else '',
                 dock_manhattan_distance=dd if tile>=0 else '',passenger_production=pp,mail_production=mp,
                 classification=('Coastal town with legal catchment dock' if coastal else 'Inland water town with legal catchment dock') if tile>=0 else
                                'Coastal town without tested practical dock' if coastal else 'Inland town without tested maritime access',
                 broad_sea_distance_tiles=round(float(open_distance[t['y'],t['x']]),2),
                 coast_river_classification_confidence='MODELLED screening: >=6-tile water interior and <=40-tile proximity, not historical shoreline proof',
                 coarse_sea_component_nearby=near_sea,
                 evidence='VERIFIED BY ENGINE TEST: dock command/catchment; MODELLED: water proximity/components',
                 shipping_path_status='NOT YET TESTED',scan_limit='40 Manhattan tiles, within 32-tile coordinate box; no terraforming',
                 maritime_significance='Existing settlement; historical port role requires individual review')
        rows.append(t)
    for t in rows:
        ports=[p for p in rows if p['town_id']!=t['town_id'] and p['practical_dock_tile']>=0]
        nearest=min(ports,key=lambda p:abs(p['x']-t['x'])+abs(p['y']-t['y']))
        t['nearest_other_tested_port']=nearest['name'];t['nearest_other_port_manhattan_tiles']=abs(nearest['x']-t['x'])+abs(nearest['y']-t['y'])
    write('existing_coastal_towns.csv',rows)
    (BASE/'towns.json').write_text(json.dumps(rows,indent=2))
    summary=dict(towns=len(rows),dock_command_catchment_usable=sum(r['practical_dock_tile']>=0 for r in rows),
                 legal_dock_somewhere_in_scan=sum(r['legal_dock_sites']>0 for r in rows),
                 water_components=count,largest_component_tiles=int(sizes[sea]),coarse_sea_id=sea,
                 inventory_log_sha256=sha(case/'engine.log'),source_sha256=sha(SOURCE))
    (ROOT/'docs/research/coastal6a_inventory_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
