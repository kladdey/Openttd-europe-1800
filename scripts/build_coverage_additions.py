#!/usr/bin/env python3
"""Rebuild additions-only coverage tests; preserve V11, original master and old add-on."""
import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import unicodedata

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from calibrate_heightmap import HASHES, project
from reverse_audit import independent_target
from scenario_geography import read_terrain
from validate_inland_features import MODEL, load_frozen_model

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'data/geography/coverage_additions_v1.json'
ALL='Europe_1800_ALL_COVERAGE_ADDITIONS_V1_TEST.json'
SWEDEN='Europe_1800_SWEDEN_ADDITIONS_V2_TEST.json'
MED='Europe_1800_MEDITERRANEAN_ADDITIONS_V1_TEST.json'


def key(name):
    # Accent-insensitive identity check also catches GOTEBORG/Göteborg-style aliases.
    return ' '.join(''.join(c for c in unicodedata.normalize('NFKD',name).casefold() if not unicodedata.combining(c)).split())


def source_sample(x,y,raw,terrains):
    tx,ty=independent_target(x,y);col,row=4095-tx,ty
    v1,h1=terrains[0];v2,h2=terrains[1]
    elevation=int(raw[row,col]);a,b=int(v1[ty,tx]),int(v2[ty,tx])
    return dict(source_column=col,source_row=row,tile_x=tx,tile_y=ty,raw_elevation=elevation,
                v1_tile_type=a,industries_tile_type=b,direct_clear_land=elevation>0 and a==b==0,
                both_saved_flat_corners=bool(np.ptp(h1[ty:ty+2,tx:tx+2])==0 and np.ptp(h2[ty:ty+2,tx:tx+2])==0),
                edge_margin_tiles=min(tx,ty,4095-tx,4095-ty))


def validate_inputs(config, baseline, master, old):
    if config['schema_version']!=1 or config['coordinate_model']!='FROZEN_GLOBAL_V6_ONLY':raise ValueError('Unsupported coverage schema/model')
    ids=set();names=set();prior={t['name']:t for t in old}
    master_names={key(t['name']) for t in master};baseline_names={key(t['name']) for t in baseline}
    for r in config['records']:
        if r['town_id'] in ids or key(r['export_name']) in names:raise ValueError('Duplicate candidate identity')
        ids.add(r['town_id']);names.add(key(r['export_name']))
        if key(r['export_name']) in baseline_names:raise ValueError('Candidate duplicates an existing imported town')
        if key(r['export_name']) in master_names and not r['prior_master_name']:raise ValueError('Existing master town must remain on its recorded hold')
        if type(r['population']) is not int or r['population']<=0 or type(r['city']) is not bool:raise ValueError('Invalid population/city flag')
        if not (-90<=r['latitude']<=90 and -180<=r['longitude']<=180):raise ValueError('Invalid geographic coordinate')
        if not all(r[k].strip() for k in ('coordinate_source','history_source','historical_basis','feature')):raise ValueError('Missing geographic or historical evidence')
        if r['region']=='Sweden' and (r['population']!=prior[r['town_id']]['population'] or r['city']!=prior[r['town_id']]['city']):raise ValueError('Old Swedish population changed')
    if {r['town_id'] for r in config['records'] if r['region']=='Sweden'}!=set(prior):raise ValueError('Every old Swedish add-on town must be accounted for')


def audit(config, baseline, master, old, raw, terrains, coefficients):
    validate_inputs(config,baseline,master,old)
    results=[];probes=[]
    for r in config['records']:
        col,row=map(float,project([[r['longitude'],r['latitude']]],coefficients)[0])
        item=dict(r,projected_column=round(col,6),projected_row=round(row,6),x='',y='',status='',reason='')
        if r['prior_master_name']:
            item.update(status='DEFER_EXISTING_MASTER_HOLD',reason='Preserve the existing Palma terrain/shoreline hold. This additions-only workflow cannot restore or relocate a master settlement.')
        elif not (0<col<4095 and 0<row<4095):
            item.update(status='DEFER_OUTSIDE_MAP',reason='Corrected geographic reference projects outside the original heightmap. Do not clamp it to an edge.')
        else:
            x,y=round(row/4095,9),round(col/4095,9);sample=source_sample(x,y,raw,terrains)
            item.update(x=x,y=y,**sample)
            if sample['edge_margin_tiles']<8:
                item.update(status='DEFER_MAP_EDGE_REVIEW',reason='Reference is within seven tiles of the map edge; retain for individual founding/growth-space review rather than placing an edge-constrained town.')
            elif not sample['direct_clear_land']:
                item.update(status='DEFER_TERRAIN_REVIEW',reason='Exact published historic/city reference maps to zero source elevation or occupied/water terrain in a supplied scenario. No nearest-land correction is made.')
            else:
                tests=[]
                for dx in (-.5,0,.5):
                    for dy in (-.5,0,.5):
                        s=source_sample(x+dy/4095,y+dx/4095,raw,terrains)
                        probes.append(dict(town_id=r['town_id'],offset_column=dx,offset_row=dy,**s));tests.append(s)
                item.update(half_pixel_probes_clear=sum(t['direct_clear_land'] for t in tests),unique_probe_targets=len({(t['tile_x'],t['tile_y']) for t in tests}))
                if not all(t['direct_clear_land'] for t in tests):
                    item.update(status='DEFER_REGISTRATION_SENSITIVITY',reason='The central reference is clear, but at least one deterministic half-pixel probe reaches unsuitable terrain. Important settlement remains documented for geographic/channel review; this is not a probability or measured registration error bound.')
                else:
                    item.update(status='RETAIN_ADDITION_TEST',reason='Published geographic reference is in bounds, nonzero source land and clear in both supplied scenarios at the base target and all nine half-pixel probes. Historic role reviewed; geographic accuracy and in-game founding remain unverified.')
        results.append(item)
    preliminary=[r for r in results if r['status']=='RETAIN_ADDITION_TEST']
    reviews={frozenset((r['town_a'],r['town_b'])):r for r in config['spacing_reviews']}
    pairs=[];held=set()
    # Include every baseline/new and new/new pair needing review under either metric.
    for i,a in enumerate(preliminary):
        for b,is_base in [(b,True) for b in baseline]+[(b,False) for b in preliminary[i+1:]]:
            bname=b['name'] if is_base else b['export_name'];aname=a['export_name']
            tx,ty=independent_target(b['x'],b['y'])
            actual=math.hypot(a['tile_x']-tx,a['tile_y']-ty)
            normal=4095*math.hypot(a['x']-b['x'],a['y']-b['y'])
            if min(actual,normal)>30:continue
            review=reviews.get(frozenset((aname,bname)))
            approved=min(actual,normal)>=15 and review is not None and review['decision']=='RETAIN_BOTH'
            if not approved:
                held.add(a['town_id'])
                if not is_base:held.add(b['town_id'])
            pairs.append(dict(town_a=aname,town_b=bname,other_is_baseline=is_base,actual_target_distance=round(actual,6),normalized_4095_distance=round(normal,6),decision='RETAIN_BOTH' if approved else 'DEFER_FOR_INDIVIDUAL_SPACING_REVIEW',reason=review['reason'] if review else 'No individual importance/growth-space review supports this close pair; do not impose a population-based automatic cull.',source=review['source'] if review else ''))
    for r in results:
        if r['town_id'] in held:r.update(status='DEFER_SPACING_REVIEW',reason='A corrected close pair requires an individual historical/importance review. Preserve existing imported towns and document the proposed additions without choosing a population-only winner.')
    retained=[r for r in results if r['status']=='RETAIN_ADDITION_TEST']
    combined=[dict(t,name=t['name']) for t in baseline]+[dict(name=r['export_name'],x=r['x'],y=r['y']) for r in retained]
    for r in retained:
        others=[]
        for t in combined:
            if t['name']==r['export_name']:continue
            u,v=independent_target(t['x'],t['y']);others.append((math.hypot(r['tile_x']-u,r['tile_y']-v),t['name']))
        d,n=min(others);r.update(nearest_combined_town=n,nearest_combined_actual_tiles=round(d,6))
    return results,probes,pairs


def write_csv(path,records):
    fields=list(dict.fromkeys(k for r in records for k in r))
    with path.open('w',encoding='utf-8',newline='') as stream:
        w=csv.DictWriter(stream,fieldnames=fields);w.writeheader();w.writerows(records)


def atlas(raw,results,baseline,out):
    panels=[('Sweden',(2500,0,3400,760)),('North African coast',(650,3550,2500,4096)),('Balearic Islands',(1450,3080,1900,3400))]
    sheet=Image.new('RGB',(1400,1800),'white');pen=ImageDraw.Draw(sheet)
    try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
    except OSError:font=ImageFont.load_default()
    for i,(title,(left,top,right,bottom)) in enumerate(panels):
        a=raw[top:bottom,left:right];g=np.clip(a.astype(float)*1.7+40,40,220).astype('uint8');rgb=np.repeat(g[:,:,None],3,2);rgb[a==0]=[17,48,85]
        scale=min(1380/(right-left),530/(bottom-top));w,h=round((right-left)*scale),round((bottom-top)*scale)
        x0,y0=10,i*600+55;sheet.paste(Image.fromarray(rgb).resize((w,h)),(x0,y0))
        pen.text((10,i*600),title+' — source raster coordinates, north up',fill='black',font=font)
        pen.text((10,i*600+22),'Gold: additions test; red: deferred; white cross: existing baseline. Off-map entries are in the audit CSV.',fill='black',font=font)
        for t in baseline:
            tx,ty=independent_target(t['x'],t['y']);col,row=4095-tx,ty
            if left<=col<right and top<=row<bottom:
                xx,yy=x0+(col-left)*scale,y0+(row-top)*scale;pen.line((xx-4,yy,xx+4,yy),fill='white');pen.line((xx,yy-4,xx,yy+4),fill='white')
        for j,r in enumerate(results):
            col,row=r['projected_column'],r['projected_row']
            if not(left<=col<right and top<=row<bottom):continue
            xx,yy=x0+(col-left)*scale,y0+(row-top)*scale;color='gold' if r['status']=='RETAIN_ADDITION_TEST' else '#ff8888'
            pen.ellipse((xx-3,yy-3,xx+3,yy+3),fill=color)
            pen.text((xx+5,yy+(-17 if j%2 else 3)),r['export_name'],fill=color,font=font)
    sheet.save(out)


def run(out):
    config=json.loads(CONFIG.read_bytes())
    inputs=dict(config['preserved_input_sha256']);inputs.update({'source_assets/'+p:s for p,s in HASHES.items()})
    for path,sha in inputs.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=sha:raise ValueError('Preserved input changed: '+path)
    coefficients,model_bytes=load_frozen_model(MODEL)
    baseline=json.loads((ROOT/config['baseline_candidate']).read_bytes())
    master=json.loads((ROOT/'data/towns/europe_1800_import_AUDIT_FIXED_TEST.json').read_bytes());old=json.loads((ROOT/'data/towns/sweden_additions_V1_TEST.json').read_bytes())
    with Image.open(ROOT/'source_assets/heightmaps/Europe_heightmap_original.png') as im:raw=np.array(im)[:,:,0]
    terrains=[read_terrain(ROOT/'source_assets/scenarios'/n) for n in ('Europe_1800_V1.scn','Europe_1800_Industries_Original.scn')]
    results,probes,pairs=audit(config,baseline,master,old,raw,terrains,coefficients)
    retained=[r for r in results if r['status']=='RETAIN_ADDITION_TEST'];deferred=[r for r in results if r['status']!='RETAIN_ADDITION_TEST']
    def export(rs):return [dict(name=r['export_name'],population=r['population'],city=r['city'],x=r['x'],y=r['y']) for r in rs]
    out.mkdir(parents=True,exist_ok=False)
    for name,rs in [(ALL,retained),(SWEDEN,[r for r in retained if r['region']=='Sweden']),(MED,[r for r in retained if r['region']!='Sweden'])]:
        (out/name).write_text(json.dumps(export(rs),indent=2,ensure_ascii=False)+'\n')
    for name,rs in [('all_candidate_decisions.csv',results),('deferred_towns.csv',deferred),('nearest_neighbours.csv',retained),('spacing_review.csv',pairs),('sensitivity_probes.csv',probes),('superseded_geographic_references.csv',config['superseded_geographic_references'])]:write_csv(out/name,rs)
    atlas(raw,results,baseline,out/'coverage_atlas.png')
    summary=dict(schema_version=1,baseline_towns=len(baseline),records_reviewed=len(results),retained_additions=len(retained),deferred=len(deferred),retained_by_region=dict(Counter(r['region'] for r in retained)),deferred_by_reason=dict(Counter(r['status'] for r in deferred)),combined_expected_towns=len(baseline)+len(retained),candidate_nonflat_targets=sum(not r['both_saved_flat_corners'] for r in retained),model_changed=False,baseline_changed=False,in_game_tests=0,input_sha256=inputs,model_sha256=hashlib.sha256(model_bytes).hexdigest(),research_sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest(),limitations='Offline test additions only. City and property references are approximate; half-pixel probes do not bound true error. Terrain arrays are the supplied sources, not the user’s newly saved 537-town scenario. Founding, actual banks, population realization and growth need in-game checks.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    print(json.dumps(run(parser.parse_args().out),indent=2))
