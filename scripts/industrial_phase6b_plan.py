"""Calibrated, bounded regional chains. No industry or terrain is written here."""
import csv,json,math
from pathlib import Path
import numpy as np
from industrial_phase6b_runtime import ROOT,BASE,SOURCE,EXPECTED,sha
from coastal_phase6_proposals import project
from coastal_phase6_preservation import parts,maps


def write_csv(path,rows):
    with path.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)


def main(additions=False):
    assert sha(SOURCE)==EXPECTED;BASE.mkdir(exist_ok=True)
    cfg=json.loads((ROOT/'data/geography/industrial_1830_regions.json').read_text(encoding='utf8'))
    minerals=json.loads((ROOT/'data/geography/industrial_1830_minerals.json').read_text(encoding='utf8'))
    matrix=json.loads((ROOT/('docs/research/industrial_1830_candidate_matrix.json' if additions else 'docs/research/industrial_1830_source_matrix.json')).read_text(encoding='utf8'))
    rules={r['local_id']:r for r in matrix['industries']}
    with (ROOT/'docs/research/existing_coastal_towns.csv').open(encoding='utf8') as f:towns=list(csv.DictReader(f))
    with (ROOT/'docs/research/added_port_towns.csv').open(encoding='utf8') as f:towns+=list(csv.DictReader(f))
    for t in towns:
        t['x']=int(t['x']);t['y']=int(t['y']);t['town_id']=int(t['town_id'])
        if 'latitude' not in t:t['latitude']=t['lat'];t['longitude']=t['lon']
    m=maps(parts(SOURCE));terrain=np.frombuffer(m['MAPT'],dtype='u1').reshape(4096,4096)>>4;height=np.frombuffer(m['MAPH'],dtype='u1').reshape(4096,4096)
    np.save(BASE/'types.npy',terrain);np.save(BASE/'heights.npy',height)
    reserved=set()
    for t in towns:
        tile=int(t.get('practical_dock_tile',t.get('dock_tile',-1)))
        if tile<0:continue
        x=tile%4096;y=tile//4096
        for dx in range(-3,4):
            for dy in range(-3,4):reserved.add((x+dx,y+dy))
    def calibrate(lat,lon):
        raw=project(lat,lon);anchors=[]
        for t in towns:
            try:p=project(float(t['latitude']),float(t['longitude']))
            except (ValueError,KeyError):continue
            d=float(np.linalg.norm(p-raw))
            if d<180:anchors.append((d,t,np.array([t['x'],t['y']])-p))
        anchors.sort(key=lambda a:a[0]);anchors=anchors[:4]
        if anchors:
            weight=np.array([1/max(d,8)**2 for d,_,_ in anchors]);residual=np.average([r for _,_,r in anchors],axis=0,weights=weight);raw+=np.clip(residual,-8,8)
        return [int(round(x)) for x in raw],[t['name'] for _,t,_ in anchors]
    planned=[]
    def add(region,locality,lat,lon,typeid,source_key,offset=(0,0),radius=12,kind='REGIONAL REPRESENTATION'):
        r=rules[typeid];assert r['available_1830'],r['industry']
        (x,y),anchors=calibrate(lat,lon);x+=offset[0];y+=offset[1]
        if not(15<=x<4081 and 15<=y<4081):return
        nearest=min(towns,key=lambda t:abs(x-t['x'])+abs(y-t['y']))
        if typeid in [57,59,61] and abs(x-nearest['x'])+abs(y-nearest['y'])<=60:
            x,y=nearest['x'],nearest['y']
        sizes=[]
        for layout in r['layouts']:
            cells=[c for c in layout['layout'] if str(c[2])!='255']
            if cells:sizes.append((max(c[0] for c in cells)+1,max(c[1] for c in cells)+1))
        width=max(w for w,h in sizes);depth=max(h for w,h in sizes)
        water=typeid in [32,39,46,90,117]
        options=[]
        for dx in range(-radius,radius+1):
            for dy in range(-radius,radius+1):
                if abs(dx)+abs(dy)>radius:continue
                xx=x+dx;yy=y+dy
                if not(3<=xx<4093-width and 3<=yy<4093-depth):continue
                if any((xx+i,yy+j) in reserved for i in range(width) for j in range(depth)):continue
                block=terrain[yy:yy+depth,xx:xx+width]
                if water:
                    if not np.all(np.isin(block,[0,4,6])) or not np.any(block==6):continue
                    if typeid==32 and (not np.all(block==6) or not np.all(height[yy:yy+depth+1,xx:xx+width+1]==0)):continue
                    if typeid in [39,46,90,117]:
                        # These layouts require a sloping shoreline warehouse,
                        # not merely water somewhere in their bounding box.
                        coast_ids={t['tile'] for t in r['tile_location_checks'] if t['checks'].get('require_coast')}
                        possible=False
                        for layout in r['layouts']:
                            for cx,cy,tileid,_ in layout['layout']:
                                if tileid not in coast_ids:continue
                                h=height[yy+cy:yy+cy+2,xx+cx:xx+cx+2]
                                if terrain[yy+cy,xx+cx]==6 and int(h.max())>int(h.min()):possible=True
                        if not possible:continue
                else:
                    if not np.all(np.isin(block,[0,4])):continue
                    if typeid!=11 and not np.all(height[yy:yy+depth+1,xx:xx+width+1]==height[yy,xx]):continue
                    if typeid in [57,59,61] and not any(terrain[yy+dy2,xx+dx2]==2 for dx2,dy2 in [(1,0),(-1,0),(0,1),(0,-1)]):continue
                score=abs(dx)+abs(dy)
                options.append((score,yy*4096+xx))
        options.sort();tiles=[v for _,v in options[:200 if water else 60]]
        planned.append(dict(placement_id=len(planned),region=region,locality=locality,latitude=lat,longitude=lon,industry=r['industry'],local_id=typeid,seed_x=x,seed_y=y,search_radius_manhattan=radius,calibration_anchors=';'.join(anchors),nearest_baseline_town=nearest['name'],nearest_baseline_town_id=nearest['town_id'],historical_basis=kind,history_source=cfg['sources'][source_key],confidence='Locality-scale sourced district' if kind.startswith('SOURCED') else 'Inferred regional 1830 activity; not an identified individual business',accepted_labels=' '.join(r['accepted']),produced_labels=' '.join(c[0] for c in r['produced']),candidate_tiles=tiles,water_industry=water))
    if additions:
        extra=json.loads((ROOT/'data/geography/industrial_copper_salt_1830.json').read_text(encoding='utf8'))
        cfg['sources'].update(extra['sources'])
        for row in extra['records']:
            region,locality,lat,lon,ids,sourcekey=row
            for i,id_ in enumerate(ids):
                add(region,locality,lat,lon,id_,sourcekey,(i*10,0),38 if id_ in [39,46,117] else 18,'SOURCED DISTRICT; game layout and ancillary supply representation')
        for name in extra['wharf_towns']:
            for t in towns:
                if t['name']!=name:continue
                lat=float(t['latitude']);lon=float(t['longitude'])
                region='GB' if lon<-1 and lat>49 else 'IB' if lon<3 and lat<44 else 'SC' if lat>55 else 'PL' if lon>16 else 'FR' if lon<6 else 'DE'
                add(region,name+' regional export wharf representation',lat,lon,46,'PORTS',(0,0),38,'REGIONAL MARITIME REPRESENTATION; generic export sink, not a named business')
        # Preserve every completed base placement; this is a separate additions
        # plan. No existing candidate, result or scenario is overwritten.
        for i,row in enumerate(planned):row['placement_id']=10000+i
        (BASE/'additions-plan.json').write_text(json.dumps(planned,indent=2,ensure_ascii=False),encoding='utf8')
        write_csv(ROOT/'docs/research/copper_salt_industry_locations.csv',[{k:v for k,v in r.items() if k!='candidate_tiles'}|{'candidate_count':len(r['candidate_tiles'])} for r in planned])
        print('Additions',len(planned),'with candidate sites',sum(bool(r['candidate_tiles']) for r in planned));return
    offsets=[(-28,8),(24,-20),(-12,-7),(12,11),(-3,3),(4,-4)]
    for region,locality,lat,lon,profile,source_key in cfg['hubs']:
        for i,typeid in enumerate(cfg['profiles'][profile]):add(region,locality,lat,lon,typeid,source_key,offsets[i],18)
    for region,locality,lat,lon,source_key,types in minerals['districts']:
        for i,typeid in enumerate(types):
            # Only the first type marks the sourced resource/works locality;
            # ancillary pieces are bounded representations of its linked trades.
            off=(0,0) if i==0 else [(-10,-5),(10,5),(-5,10),(6,-9),(14,-3),(-14,5)][(i-1)%6]
            add(region,locality,lat,lon,typeid,source_key,off,12,'SOURCED DISTRICT; ancillary AXIS chain representation')
    # Secondary packaging/glass/beet support is concentrated, not repeated at
    # every market: players must trade among regions for optional efficiencies.
    for region,loc,lat,lon,source_key,types in [
        ('FR','Northern French beet processing',49.0,2.4,'SUGAR',[113,122]),
        ('DE','Central German beet and glass trades',51.8,11.6,'SUGAR',[113,22,99,86]),
        ('CE','Bohemian glass and paper trades',50.6,15.1,'EUROPE',[22,99,86,73]),
        ('GB','English glass and building trades',52.0,-0.5,'EUROPE',[22,99,86,73]),
        ('PL','Vistula oilseed processing',52.6,18.0,'BALTIC',[122,113]),
        ('IT','Venetian glass trade',45.45,12.32,'ITALY',[22,99,86]),
    ]:
        for i,t in enumerate(types):add(region,loc,lat,lon,t,source_key,(i*12-12,12),18)
    # Historic coasts: exact active-town anchors, existing tested catchments
    # protected above. Fishing grounds and processing are paired regionally.
    wanted=['PLYMOUTH','LIVERPOOL','HULL','SUNDERLAND','GREENOCK','DUBLIN','PORTO','LISBOA','BARCELONA','VALENCIA','MARSEILLE','DANZIG (GDANSK)','Świnoujście','Kołobrzeg','Kristiansand','Helsingborg','COPENHAGEN']
    for name in wanted:
        matches=[t for t in towns if t['name']==name]
        if not matches:continue
        t=matches[0]
        try:lat=float(t['latitude']);lon=float(t['longitude'])
        except ValueError:continue
        region='GB' if lon<-1 and lat>49 else 'IB' if lon<3 and lat<44 else 'SC' if lat>55 else 'PL' if lon>16 else 'FR' if lon<6 else 'DE'
        for typeid in [32,90,39]:add(region,name+' historic maritime district',lat,lon,typeid,'BALTIC' if region=='PL' else 'NORWAY' if region=='SC' else 'EUROPE',(0,0),38,'REGIONAL MARITIME REPRESENTATION')
    # Build raw/keystone industries first, dependent processors second, sinks last.
    def order(r):
        cls=rules[r['local_id']]['model_class']
        return (0 if 'Primary' in cls else 2 if not r['produced_labels'] else 1,r['local_id'],r['placement_id'])
    planned.sort(key=order)
    (BASE/'placement-plan.json').write_text(json.dumps(planned,indent=2,ensure_ascii=False),encoding='utf8')
    write_csv(ROOT/'docs/research/historical_industry_locations.csv',[{k:v for k,v in r.items() if k!='candidate_tiles'}|{'candidate_count':len(r['candidate_tiles'])} for r in planned])
    print('Planned',len(planned),'types',len(set(r['local_id'] for r in planned)),'nonempty sites',sum(bool(r['candidate_tiles']) for r in planned))


if __name__=='__main__':
    import sys
    main('--additions' in sys.argv)
