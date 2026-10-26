#!/usr/bin/env python3
"""Screen geographic coverage of V12 without generating or changing town imports."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.spatial import cKDTree

from build_coverage_additions import key
from calibrate_heightmap import HASHES, project
from reverse_audit import independent_target
from scenario_geography import read_terrain
from validate_inland_features import MODEL, load_frozen_model

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'data/geography/coverage_gap_research_v1.json'


def rows(path):
    with path.open(encoding='utf-8',newline='') as stream:return list(csv.DictReader(stream))


def target_points(towns):
    return np.array([(4095-tx,ty) for tx,ty in (independent_target(t['x'],t['y']) for t in towns)],dtype=float)


def distance_samples(raw,points,step=8):
    if type(step) is not int or step<1:raise ValueError('Invalid sampling step')
    if len(points)==0:raise ValueError('No town targets')
    yy,xx=np.mgrid[0:raw.shape[0]:step,0:raw.shape[1]:step]
    distances,_=cKDTree(points).query(np.c_[xx.ravel(),yy.ravel()])
    return xx,yy,raw[::step,::step]>0,distances.reshape(xx.shape)


def candidate_audit(candidates,towns,raw,terrain,coefficients):
    points=target_points(towns);tree=cKDTree(points);known={key(t['name']):i for i,t in enumerate(towns)}
    result=[]
    for r in candidates:
        if not (np.isfinite(r['latitude']) and np.isfinite(r['longitude']) and -90<=r['latitude']<=90 and -180<=r['longitude']<=180):raise ValueError('Invalid geographic research coordinate')
        if not r['coordinate_source'].startswith('https://') or not r['historical_role'].strip():raise ValueError('Candidate lacks research evidence')
        col,row=map(float,project([[r['longitude'],r['latitude']]],coefficients)[0])
        out=dict(r,projected_column=round(col,3),projected_row=round(row,3),research_only=True)
        if not(0<col<4095 and 0<row<4095):
            out.update(stage='OUTSIDE_MAP',nearest_town='',distance_to_nearest_target_tiles='',point_terrain='NOT_SAMPLED')
        else:
            tx,ty=independent_target(round(row/4095,9),round(col/4095,9));sc,sr=4095-tx,ty
            d,index=tree.query([sc,sr]);nearest=towns[int(index)]['name']
            same_name=key(r['name']) in known
            same_place=same_name and np.linalg.norm(points[known[key(r['name'])]]-[sc,sr])<30
            stage=('ALREADY_PRESENT' if same_place else 'NAME_COLLISION_REQUIRES_IDENTITY_REVIEW' if same_name else
                   'SUB_15_IMPORTANCE_EXCEPTION_REVIEW' if d<15 else '15_TO_30_INDIVIDUAL_REVIEW' if d<=30 else 'GAP_RESEARCH_CANDIDATE')
            elevation=int(raw[sr,sc]);a,b=(int(t[ty,tx]) for t in terrain)
            relief=raw[max(0,sr-16):min(4096,sr+17),max(0,sc-16):min(4096,sc+17)];positive=relief[relief>0]
            out.update(stage=stage,source_column=sc,source_row=sr,nearest_town=nearest,distance_to_nearest_target_tiles=round(float(d),3),
                       raw_elevation=elevation,v1_tile_type=a,industries_tile_type=b,
                       point_terrain='SOURCE_AND_SAVED_CLEAR' if elevation>0 and a==b==0 else 'REFERENCE_NEEDS_TERRAIN_OR_HISTORIC_CORE_REVIEW',
                       local_nonzero_elevation_range=int(np.ptp(positive)) if len(positive) else '',
                       requires_qualified_name=key(r['name'].split(' (')[0]) in known and not same_name)
        result.append(out)
    return result


def deferred_audit(towns):
    tree=cKDTree(target_points(towns));records=[];seen=set()
    for path,flag in [(ROOT/'maps/calibration/geography_v11/all_600_decisions.csv','master'),(ROOT/'maps/calibration/coverage_additions_v1/all_candidate_decisions.csv','supplement')]:
        for r in rows(path):
            state=r['state'] if flag=='master' else r['status']
            if not state.startswith('DEFER'):continue
            name=r['name'] if flag=='master' else r['export_name']
            if key(name) in seen:continue
            seen.add(key(name));item=dict(name=name,origin=flag,state=state,reason=r['reason'],nearest_town='',distance_to_nearest_target_tiles='')
            if r.get('source_column','')!='' and r.get('source_row','')!='':
                col,row=float(r['source_column']),float(r['source_row'])
                d,i=tree.query([col,row]);item.update(source_column=col,source_row=row,nearest_town=towns[int(i)]['name'],distance_to_nearest_target_tiles=round(float(d),3))
            records.append(item)
    return records


def grid_audit(xx,yy,land,distance,cell):
    result=[]
    for top in range(0,4096,cell):
        for left in range(0,4096,cell):
            mask=(xx>=left)&(xx<left+cell)&(yy>=top)&(yy<top+cell)
            sampled=land[mask];values=distance[mask&land]
            if not len(values):continue
            result.append(dict(left_column=left,top_row=top,cell_size=cell,positive_elevation_sample_fraction=round(float(sampled.mean()),4),land_samples=len(values),median_nearest_target_tiles=round(float(np.median(values)),2),p90_nearest_target_tiles=round(float(np.percentile(values,90)),2),max_nearest_target_tiles=round(float(values.max()),2)))
    return sorted(result,key=lambda r:r['median_nearest_target_tiles'],reverse=True)


def regional_audit(windows,xx,yy,land,distance,points,coefficients):
    a,b,c,d=coefficients;lon=(xx-b)/a;lat=(yy-d)/c
    result=[]
    for r in windows:
        west,east,south,north=r['bounds_west_east_south_north'];mask=land&(lon>=west)&(lon<=east)&(lat>=south)&(lat<=north)
        values=distance[mask]
        plon=(points[:,0]-b)/a;plat=(points[:,1]-d)/c
        inside=(plon>=west)&(plon<=east)&(plat>=south)&(plat<=north)
        result.append(dict(window=r['name'],nearby_existing_targets_in_window=int(inside.sum()),nonzero_source_samples=len(values),median_distance_tiles=round(float(np.median(values)),2) if len(values) else '',p90_distance_tiles=round(float(np.percentile(values,90)),2) if len(values) else '',fraction_samples_over_100_tiles=round(float((values>100).mean()),4) if len(values) else '',interpretation='Overlapping approximate study window; not a country boundary, catchment, population estimate or required density.'))
    return result


def coverage_image(land,distance,points,candidates,deferred,out):
    # Colours express distance alone, not suitability or a required town density.
    stops=np.array([0,30,60,100,200,350,650]);colors=np.array([[32,90,64],[55,115,63],[112,137,57],[195,159,58],[207,103,58],[171,68,110],[104,48,130]])
    rgb=np.stack([np.interp(distance,stops,colors[:,i]) for i in range(3)],axis=-1).astype('uint8');rgb[~land]=[15,40,70]
    sheet=Image.new('RGB',(1500,1660),'white');base=Image.fromarray(rgb).resize((1500,1500),Image.Resampling.NEAREST);sheet.paste(base,(0,100));pen=ImageDraw.Draw(sheet)
    try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
    except OSError:font=ImageFont.load_default()
    pen.text((8,5),'V12 coverage screening — 568 planned import targets; north up; source pixels',fill='black',font=font)
    pen.text((8,26),'Green: nearer towns; gold/orange: larger gaps; purple: most distant. Distance is across water/mountains.',fill='black',font=font)
    pen.text((8,47),'White dots: current targets. Gold rings/IDs: research candidates. Red squares: mapped existing deferrals.',fill='black',font=font)
    pen.text((8,68),'Sparse terrain is not automatically a settlement omission. Candidate IDs refer to the CSV; no new import is generated.',fill='black',font=font)
    scale=1500/4096
    for col,row in points:
        x,y=col*scale,100+row*scale;pen.ellipse((x-1,y-1,x+1,y+1),fill='white')
    for r in deferred:
        if 'source_column' not in r:continue
        x,y=r['source_column']*scale,100+r['source_row']*scale
        if 0<=x<1500 and 100<=y<1600:pen.rectangle((x-2,y-2,x+2,y+2),outline='#ff7777')
    for r in candidates:
        if r['stage']=='OUTSIDE_MAP':continue
        x,y=r['source_column']*scale,100+r['source_row']*scale
        pen.ellipse((x-4,y-4,x+4,y+4),outline='yellow',width=2)
        pen.text((min(x+5,1440),max(100,y-12)),r['id'],fill='yellow',font=font)
    for i,(start,end) in enumerate(zip(stops[:-1],stops[1:])):
        x=8+i*240;pen.rectangle((x,1612,x+30,1632),fill=tuple(colors[i]));pen.text((x+35,1612),f'{start}–{end} tiles',fill='black',font=font)
    sheet.save(out)


def write_csv(path,records):
    fields=list(dict.fromkeys(k for r in records for k in r))
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(records)


def run(out):
    config=json.loads(CONFIG.read_bytes());path=ROOT/config['input_import']
    if hashlib.sha256(path.read_bytes()).hexdigest()!=config['import_sha256']:raise ValueError('V12 import changed')
    if config['schema_version']!=1:raise ValueError('Unsupported gap-research schema')
    for filename,expected in config['preserved_input_sha256'].items():
        if hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()!=expected:raise ValueError('Deferral input changed: '+filename)
    ids=[r['id'] for r in config['candidates']]
    names=[key(r['name']) for r in config['candidates']]
    if len(ids)!=len(set(ids)) or len(names)!=len(set(names)):raise ValueError('Duplicate research candidate')
    towns=json.loads(path.read_bytes());coefficients,model=load_frozen_model(MODEL)
    for name,sha in HASHES.items():
        if hashlib.sha256((ROOT/'source_assets'/name).read_bytes()).hexdigest()!=sha:raise ValueError('Original asset hash mismatch')
    with Image.open(ROOT/'source_assets/heightmaps/Europe_heightmap_original.png') as im:raw=np.array(im)[:,:,0]
    terrain=[read_terrain(ROOT/'source_assets/scenarios'/n)[0] for n in ('Europe_1800_V1.scn','Europe_1800_Industries_Original.scn')]
    points=target_points(towns);xx,yy,land,distance=distance_samples(raw,points,config['sample_step_source_pixels'])
    candidates=candidate_audit(config['candidates'],towns,raw,terrain,coefficients);deferred=deferred_audit(towns)
    grid=grid_audit(xx,yy,land,distance,config['cell_size_source_pixels']);regions=regional_audit(config['regional_windows'],xx,yy,land,distance,points,coefficients)
    collisions=[]
    for i,a in enumerate(candidates):
        for b in candidates[i+1:]:
            if 'source_column' not in a or 'source_column' not in b:continue
            d=float(np.hypot(a['source_column']-b['source_column'],a['source_row']-b['source_row']))
            if d<=30:collisions.append(dict(candidate_a=a['name'],candidate_b=b['name'],nominal_distance_tiles=round(d,3),review='Future candidates require joint importance/spacing review; not an approval.'))
    out.mkdir(parents=True,exist_ok=False)
    write_csv(out/'candidate_research_queue.csv',candidates);write_csv(out/'existing_deferral_recovery.csv',deferred);write_csv(out/'coverage_grid.csv',grid);write_csv(out/'regional_windows.csv',regions);write_csv(out/'candidate_pair_reviews.csv',collisions)
    coverage_image(land,distance,points,candidates,deferred,out/'coverage_gap_map.png')
    summary=dict(schema_version=1,current_towns=len(towns),research_candidates=len(candidates),candidate_stages=dict(Counter(r['stage'] for r in candidates)),known_deferrals=len(deferred),new_imports_generated=0,town_coordinate_changes=0,source_grid_step=config['sample_step_source_pixels'],grid_cell_size=config['cell_size_source_pixels'],nonzero_source_samples=int(land.sum()),fraction_nonzero_samples_over_100_tiles=round(float((distance[land]>100).mean()),4),fraction_nonzero_samples_over_200_tiles=round(float((distance[land]>200).mean()),4),preserved_input_sha256=config['preserved_input_sha256'],input_import_sha256=config['import_sha256'],research_sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest(),model_sha256=hashlib.sha256(model).hexdigest(),limitations=config['limitations'])
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    print(json.dumps(run(parser.parse_args().out),indent=2))
