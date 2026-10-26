#!/usr/bin/env python3
"""Evidence-backed V10 target corrections and explicit unresolved-town deferrals.

No nearest-land snapping, scenario writes, population changes or implicit point
selection. The decisions CSV names every selected historical reference explicitly.
"""
import argparse
import collections
import itertools
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import label

import geography as g
from calibrate_heightmap import HASHES, project
from scenario_geography import read_terrain, import_target, source_pixel
from review_europe_placements import rows, close_pairs, pair_key
from register_coastal_regions import CONFIG

V8 = g.ROOT/'maps/calibration/geography_v8'
V9 = g.ROOT/'maps/calibration/geography_v9'
REFERENCES = g.ROOT/'data/geography/historic_centre_references_v10.csv'
REGISTRATION = g.ROOT/'data/geography/coastal_registration_v10.json'
DECISIONS = g.ROOT/'data/geography/terrain_decisions_v10.csv'
EXTRA_PAIRS = g.ROOT/'data/geography/spacing_decisions_v10.csv'
MODEL = g.ROOT/'maps/calibration/geography_v6/coastline_models.json'
SUPPLEMENTAL = g.ROOT/'data/geography/supplemental_terrain_flags_v10.csv'
CORE = 'Europe_1800_V10_CLEAR_TARGET_CANDIDATE_TEST.json'
COMPARISON = 'Europe_1800_V10_RETAINED_COMPARISON_TEST.json'
FULL = 'Europe_1800_V10_ALL_IN_BOUNDS_COMPARISON_TEST.json'


def write_csv(path, records, fields=None):
    g.write_csv(path, records, fields or list(records[0]))


def inputs(assets):
    for relative, expected in HASHES.items():
        if g.digest(assets/relative) != expected:
            raise ValueError('Original asset hash mismatch: '+relative)
    with Image.open(assets/'heightmaps/Europe_heightmap_original.png') as im:
        raw = np.array(im)[:, :, 0]
    types, heights = read_terrain(assets/'scenarios/Europe_1800_V1.scn')
    industry, iheights = read_terrain(assets/'scenarios/Europe_1800_Industries_Original.scn')
    return raw, types, heights, industry, iheights


def sample(town, arrays):
    raw, types, heights, industry, iheights = arrays
    tx, ty = import_target(town['x'], town['y'])
    col, row = source_pixel(town['x'], town['y'])
    elevation, a, b = int(raw[row,col]), int(types[ty,tx]), int(industry[ty,tx])
    flat = all(np.all(h[ty:ty+2,tx:tx+2] == h[ty,tx]) for h in (heights, iheights))
    return dict(source_column=col, source_row=row, tile_x=tx, tile_y=ty, raw_elevation=elevation,
        v1_tile_type=a, industries_tile_type=b, direct_clear_land=bool(elevation > 0 and a == b == 0),
        both_saved_flat_corners=bool(flat))


def registered_regions():
    registration = g.read_json(REGISTRATION)
    # Fitted results are evidence inputs, not instructions to trust arbitrary blobs.
    for path, expected in registration['input_sha256'].items():
        if g.digest(g.ROOT/path) != expected: raise ValueError('Stale coastline registration: '+path)
    regions = {r['id']:r for r in registration['regions']}
    config = g.read_json(CONFIG)
    declared = {r['id']:r for r in config['regions']}
    if set(regions) != set(declared): raise ValueError('Regional model coverage changed')
    for name, region in regions.items():
        if any(region[k] != declared[name][k] for k in ('bounds_west_east_south_north','towns')):
            raise ValueError('Regional model does not match declared geographic extent')
        if not region['accepted']: continue
        values = [region[k] for k in ('shift_column','shift_row','holdout_median_pixels','holdout_p90_pixels',
            'before_holdout_median_pixels','before_holdout_p90_pixels','maximum_jackknife_difference_pixels','jacobian_eigenvalue_ratio')]
        valid = (all(math.isfinite(v) for v in values) and not region['rejection_reasons'] and
            region['train_samples'] >= config['minimum_train_samples'] and
            region['holdout_samples'] >= config['minimum_holdout_samples'] and
            max(abs(region['shift_column']),abs(region['shift_row'])) < config['max_shift_pixels']-.1 and
            region['holdout_p90_pixels'] <= config['maximum_holdout_p90_pixels'] and
            region['holdout_p90_pixels'] <= region['before_holdout_p90_pixels'] and
            region['before_holdout_median_pixels']-region['holdout_median_pixels'] >= config['minimum_holdout_median_improvement'] and
            region['maximum_jackknife_difference_pixels'] <= config['maximum_jackknife_shift_pixels'] and
            region['jacobian_eigenvalue_ratio'] >= config['minimum_jacobian_eigenvalue_ratio'])
        if not valid: raise ValueError('Accepted regional model fails its evidence gates: '+name)
    return regions


def regional_rebase(towns):
    """Apply each accepted translation consistently to every town in its box."""
    regions = registered_regions()
    coefficients = g.read_json(MODEL)['axis_affine']['coefficients']
    geo = {r['name']:(float(r['latitude']),float(r['longitude'])) for r in rows(g.ROOT/'maps/calibration/geography_v7/all_600_placement_audit.csv')}
    for r in rows(g.ROOT/'data/geography/coordinate_overrides_v8.csv'):
        geo[r['name']] = float(r['latitude']),float(r['longitude'])
    rebased, changes = [], {}
    for old in towns:
        town = dict(old); lat,lon = geo[town['name']]
        matches = [r for r in regions.values() if r['accepted'] and
            r['bounds_west_east_south_north'][0] <= lon <= r['bounds_west_east_south_north'][1] and
            r['bounds_west_east_south_north'][2] <= lat <= r['bounds_west_east_south_north'][3]]
        if len(matches)>1: raise ValueError('Overlapping accepted coastal regions')
        if matches:
            r=matches[0];col,row=project([[lon,lat]],coefficients)[0]
            town.update(x=round(float((row+r['shift_row'])/4095),9),y=round(float((col+r['shift_column'])/4095),9))
            changes[town['name']]=dict(name=town['name'],reference_id='',feature='Unchanged V8 geographic input; coherent regional registration',
                latitude=lat,longitude=lon,x=town['x'],y=town['y'],applied_model=r['id'],
                displacement_from_v8_tiles=round(g.distance(old,town),6),
                coordinate_source='maps/calibration/geography_v7/all_600_placement_audit.csv; coordinate_overrides_v8.csv',
                history_source='',historical_basis='Registration-only change; no historic-centre or identity reassignment.')
        rebased.append(town)
    return rebased,changes


def reference_audit(arrays):
    coefficients = g.read_json(MODEL)['axis_affine']['coefficients']
    regions = registered_regions()
    old = {t['name']:t for t in g.read_json(V8/'Europe_1800_V8_DESK_REVIEWED_CANDIDATE_TEST.json')}
    flags = {r['name'] for r in rows(V9/'retained_terrain_diagnostics.csv')}
    flags |= {r['name'] for r in rows(SUPPLEMENTAL)}
    references = rows(REFERENCES)
    if {r['name'] for r in references} != flags: raise ValueError('Reference coverage must match original and supplemental flags')
    result, seen = [], set()
    for r in references:
        if r['reference_id'] in seen: raise ValueError('Duplicate reference ID')
        seen.add(r['reference_id'])
        if not all(r[k].strip() for k in ('coordinate_source','history_source','historical_basis','feature')):
            raise ValueError('Reference lacks historical or geographic evidence')
        lat, lon = float(r['latitude']), float(r['longitude'])
        if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError('Invalid reference coordinates')
        col, row = project([[lon, lat]], coefficients)[0]
        model = 'GLOBAL_V6'; dx = dy = 0.
        if r['region_model'] != 'GLOBAL':
            region = regions[r['region_model']]
            if r['name'] not in region['towns']: raise ValueError('Town outside assigned coastal region')
            west, east, south, north = region['bounds_west_east_south_north']
            if not (west <= lon <= east and south <= lat <= north): raise ValueError('Reference outside regional bounds')
            if region['accepted']:
                dx, dy = region['shift_column'], region['shift_row']
                model = r['region_model']
        t = dict(old[r['name']], x=round(float((row+dy)/4095),9), y=round(float((col+dx)/4095),9))
        g.validate([t])
        datum = dict(r, applied_model=model, shift_column=dx, shift_row=dy, x=t['x'], y=t['y'],
            displacement_from_v8_tiles=round(g.distance(old[r['name']],t),6), **sample(t,arrays))
        datum['eligible'] = bool(datum['direct_clear_land'] and r['reference_scope']=='BUILDING_SITE')
        result.append(datum)
    return result


def checked_decisions(audit):
    by_id = {r['reference_id']:r for r in audit}
    flags = {r['name'] for r in audit}
    decisions = rows(DECISIONS)
    if len(decisions)!=len(flags) or {r['name'] for r in decisions} != flags:
        raise ValueError('Every flagged town requires exactly one explicit decision')
    seen, selected, deferred = set(), {}, {}
    for r in decisions:
        if r['name'] in seen: raise ValueError('Duplicate town decision')
        seen.add(r['name'])
        if not r['reason'].strip(): raise ValueError('Missing decision reason')
        if r['decision']=='CORRECT_TO_REFERENCE':
            target = by_id.get(r['reference_id'])
            if not target or target['name']!=r['name']: raise ValueError('Wrong-town or unknown reference')
            if not target['eligible']: raise ValueError('Selected historic reference is not a clear eligible target: '+r['name'])
            selected[r['name']]=target
        elif r['decision']=='TEMPORARILY_DEFER_TERRAIN':
            if r['reference_id']: raise ValueError('Deferred town must not silently select a coordinate')
            deferred[r['name']]=r
        else: raise ValueError('Unknown terrain decision')
    return selected, deferred, decisions


def spacing_review(before, after, core):
    prior={pair_key(r['town_a'],r['town_b']):r for r in rows(g.ROOT/'data/geography/spacing_decisions_v8.csv')}
    extra={pair_key(r['town_a'],r['town_b']):r for r in rows(EXTRA_PAIRS)}
    old, new = close_pairs(before), close_pairs(after)
    safe={t['name'] for t in core}; by_name={t['name']:t for t in after}
    result=[]
    for k in sorted(set(old)|set(new)):
        policy=extra.get(k,prior.get(k))
        if policy is None: raise ValueError('New close pair requires explicit review: '+str(k))
        a,b=(by_name[n] for n in k)
        distance=g.distance(a,b)
        ta,tb=import_target(a['x'],a['y']),import_target(b['x'],b['y'])
        actual=math.dist(ta,tb)
        retained=set(k)<=safe
        if retained and (distance<15 or actual<15): raise ValueError('Unreviewed sub-15 conflict: '+str(k))
        result.append(dict(town_a=k[0],town_b=k[1],v8_distance_tiles=round(old[k],6) if k in old else '',
            v10_distance_tiles=round(distance,6),actual_target_distance_tiles=round(actual,6),band=g.band(distance),
            near_policy_boundary=min(abs(distance-15),abs(distance-30))<=2,
            both_in_clear_candidate=retained,new_pair=k not in old,reason=policy['reason'],
            inherited_or_new_review='V10' if k in extra else 'V8',
            evidence_source=policy.get('source','data/geography/spacing_decisions_v8.csv')))
    return result


def contact_sheet(arrays, decisions, references, before, after, out):
    raw, types, _, industry, _ = arrays
    base=np.stack([raw*.55+65]*3,axis=-1).clip(0,255).astype('uint8');base[raw==0]=[12,28,50]
    # Saved terrain layers in source-image orientation; source pixels stay unchanged.
    base[(types[:,::-1]==6)|(industry[:,::-1]==6)]=[30,105,175]
    base[(types[:,::-1]==2)|(industry[:,::-1]==2)]=[145,95,50]
    base[(types[:,::-1]==3)|(industry[:,::-1]==3)]=[135,70,105]
    image=Image.fromarray(base)
    cols=6; sheet=Image.new('RGB',(cols*230,math.ceil(len(decisions)/cols)*260),'white');draw=ImageDraw.Draw(sheet)
    for i,r in enumerate(decisions):
        name=r['name']; x,y=i%cols*230,i//cols*260
        oc,orr=source_pixel(before[name]['x'],before[name]['y']);left,top=oc-25,orr-25
        sheet.paste(image.crop((left,top,left+51,top+51)).resize((204,204),Image.Resampling.NEAREST),(x,y+22))
        draw.text((x,y),name,fill='black')
        draw.line((x+94,y+124,x+110,y+124),fill='red',width=2);draw.line((x+102,y+116,x+102,y+132),fill='red',width=2)
        for ref in references:
            if ref['name']!=name:continue
            px,py=x+(ref['source_column']-left)*4+2,y+22+(ref['source_row']-top)*4+2
            draw.ellipse((px-3,py-3,px+3,py+3),outline='yellow',width=1)
        if r['decision']=='CORRECT_TO_REFERENCE':
            nc,nr=source_pixel(after[name]['x'],after[name]['y']);px,py=x+(nc-left)*4+2,y+22+(nr-top)*4+2
            draw.ellipse((px-5,py-5,px+5,py+5),outline='lime',width=2)
            draw.text((x,y+230),'CORRECTED: clear target',fill='darkgreen')
        else:draw.text((x,y+230),'TEMPORARILY DEFERRED',fill='darkred')
        draw.text((x,y+246),f'Source origin {left},{top}; 51px',fill='black')
    sheet.save(out/'terrain_resolution_contact_sheet.png')


def generate(assets,out):
    if out.exists(): raise FileExistsError('Use a new output directory')
    arrays=inputs(assets)
    references=reference_audit(arrays)
    selected,terrain_deferred,decisions=checked_decisions(references)
    old_core=g.read_json(V8/'Europe_1800_V8_DESK_REVIEWED_CANDIDATE_TEST.json')
    old_full=g.read_json(V8/'Europe_1800_V8_CORRECTED_ALL_IN_BOUNDS_TEST.json')
    old_by_name={t['name']:t for t in old_full}
    rebased, regional_changes=regional_rebase(old_full)
    full=[]
    for town in rebased:
        t=dict(town)
        if t['name'] in selected:
            r=selected[t['name']];t.update(x=r['x'],y=r['y'])
        full.append(t)
    by_name={t['name']:t for t in full}
    comparison=[by_name[t['name']] for t in old_core]
    core=[t for t in comparison if t['name'] not in terrain_deferred]
    master={t['name']:t for t in g.read_json(g.MASTER)}
    for data in (core,comparison,full):
        g.validate(data)
        for t in data:
            if any(t[k]!=master[t['name']][k] for k in ('name','population','city')):raise ValueError('Master metadata changed')
    samples={t['name']:sample(t,arrays) for t in full}
    if not all(samples[t['name']]['direct_clear_land'] for t in core):raise ValueError('Clear candidate contains a terrain flag')
    pairs=spacing_review(old_full,full,core)
    # Verify continental / island identity with independent raster landmass seeds.
    components,_=label(arrays[0]>0)
    seeds={'Great Britain':(1181,1117),'continental Europe':(1625,1712),
           'Sicily':(2850,3550),'Sardinia':(2340,3090),'Mallorca':(1670,3200)}
    seed_ids={name:int(components[row,col]) for name,(col,row) in seeds.items()}
    if 0 in seed_ids.values() or len(set(seed_ids.values()))!=len(seed_ids):raise ValueError('Landmass seed invalid')
    changes=[]
    all_changes=dict(regional_changes,**selected)
    for name,r in all_changes.items():
        expected=('Great Britain' if name in ('DERBY','EXETER','GLASGOW','LONDON','PRESTON') else
                  'Sicily' if name in ('CATANIA','MARSALA','MESSINA') else
                  'Sardinia' if name=='CAGLIARI' else 'Mallorca' if name=='PALMA' else 'continental Europe')
        if name not in selected:
            old_sample=sample(old_by_name[name],arrays)
            old_component=int(components[old_sample['source_row'],old_sample['source_column']])
            expected=next((key for key,value in seed_ids.items() if value==old_component),'unverified or source-water')
        new_sample=samples[name]
        actual=int(components[new_sample['source_row'],new_sample['source_column']])
        if actual and expected in seed_ids and actual!=seed_ids[expected]:raise ValueError('Wrong landmass: '+name)
        changes.append(dict(name=name,reference_id=r['reference_id'],feature=r['feature'],old_x=old_by_name[name]['x'],
            old_y=old_by_name[name]['y'],new_x=r['x'],new_y=r['y'],latitude=r['latitude'],longitude=r['longitude'],
            displacement_tiles=r['displacement_from_v8_tiles'],applied_model=r['applied_model'],landmass=expected,
            coordinate_source=r['coordinate_source'],history_source=r['history_source'],historical_basis=r['historical_basis'],**samples[name]))
    decision_by_name={r['name']:r for r in decisions}; safe={t['name'] for t in core}
    all_rows=[]
    for r in rows(V8/'all_600_decisions.csv'):
        name=r['name'];outcome=dict(r)
        if name in by_name:
            t=by_name[name];outcome.update(x=t['x'],y=t['y'],**samples[name])
        if name in selected:
            outcome.update(state='RETAINED_CLEAR_TARGET_CANDIDATE',reason=decision_by_name[name]['reason'],terrain_review_open=False,input_coordinate_corrected=True)
        elif name in terrain_deferred:
            outcome.update(state='DEFERRED_TERRAIN',reason=terrain_deferred[name]['reason'],terrain_review_open=True)
        elif name in safe:outcome['state']='RETAINED_CLEAR_TARGET_CANDIDATE'
        if name in regional_changes and name not in selected:
            outcome['reason']+=' Same geographic input rebased with accepted regional coastline translation: '+regional_changes[name]['applied_model']+'.'
        outcome['placement_changed']=name in all_changes
        outcome['registration_changed']=name in regional_changes
        outcome['placement_model']=selected.get(name,regional_changes.get(name,{})).get('applied_model','GLOBAL_V6')
        # Homogeneous columns, including outside-map records with no target.
        for key in ('source_column','source_row','tile_x','tile_y','both_saved_flat_corners'):
            outcome.setdefault(key,'')
        all_rows.append(outcome)
    resolution=[]
    for d in decisions:
        item=dict(d,terrain_flag_resolved=d['name'] in selected,founding='UNTESTED')
        item.update(**samples[d['name']])
        resolution.append(item)
    deferred=[r for r in all_rows if r['state'].startswith('DEFERRED')]
    neighbours=[]
    for a in core:
        b=min((b for b in core if b['name']!=a['name']),key=lambda b:g.distance(a,b))
        neighbours.append(dict(name=a['name'],nearest_town=b['name'],distance_tiles=round(g.distance(a,b),6),band=g.band(g.distance(a,b))))
    summary=dict(status='DESK EVIDENCE; clear target is not survey accuracy or founding success',
        original_flags_reviewed=54,supplemental_flags_reviewed=len(rows(SUPPLEMENTAL)),
        original_flags_resolved=sum(name in selected for name in {r['name'] for r in rows(V9/'retained_terrain_diagnostics.csv')}),
        flags_reviewed=len(decisions),flags_resolved_clear_target=len(selected),flags_temporarily_deferred=len(terrain_deferred),
        catalogue_entries=600,clear_target_candidate=len(core),retained_comparison=len(comparison),all_in_bounds_comparison=len(full),
        total_deferred=len(deferred),deferred_categories=dict(collections.Counter(r['state'] for r in deferred)),
        accepted_coast_regions=[r['id'] for r in g.read_json(REGISTRATION)['regions'] if r['accepted']],
        clear_candidate_nonflat_targets=sum(not samples[t['name']]['both_saved_flat_corners'] for t in core),
        candidate_pairs_under_15=sum(p['both_in_clear_candidate'] and p['v10_distance_tiles']<15 for p in pairs),
        minimum_spacing_tiles=min(r['distance_tiles'] for r in neighbours),new_close_pairs=sum(p['new_pair'] for p in pairs),
        coordinate_changes=len(changes),historic_site_corrections=len(selected),regional_registration_changes=len(regional_changes),
        population_changes=0,in_game_tests=0,scenario_changes=0,
        input_sha256={str(p.relative_to(g.ROOT)):g.digest(p) for p in (REFERENCES,REGISTRATION,DECISIONS,EXTRA_PAIRS,SUPPLEMENTAL,MODEL,
            V8/'Europe_1800_V8_DESK_REVIEWED_CANDIDATE_TEST.json',V8/'Europe_1800_V8_CORRECTED_ALL_IN_BOUNDS_TEST.json')},
        original_assets_sha256=HASHES,
        limitations='Historic sites use modern reference coordinates. Regional coast-normal checks do not prove 2D town or riverbank accuracy. No nearest-land snap. Remaining targets are explicitly deferred from the clear candidate and preserved in comparison imports. Flatness, town-distance settings and founding remain separate.')
    out.mkdir(parents=True)
    for filename,data in ((CORE,core),(COMPARISON,comparison),(FULL,full)):
        (out/filename).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for filename,data in (('historic_reference_audit.csv',references),('terrain_resolution.csv',resolution),
        ('coordinate_changes.csv',changes),('all_600_decisions.csv',all_rows),('deferred_towns.csv',deferred),
        ('spacing_audit.csv',pairs),('candidate_nearest_neighbours.csv',neighbours)):
        write_csv(out/filename,data)
    statuses=[dict(name=r['name'],evidence_status='DEFERRED' if r['state'].startswith('DEFERRED') else
        'BOUNDARY_REVIEW_OPEN' if str(r['boundary_review_open'])=='True' else 'CONDITIONAL_CLEAR_TARGET',
        decision=r['state'],x=r['x'],y=r['y'],population=r['population'],reason=r['reason'],
        terrain_review_open=r['terrain_review_open'],boundary_review_open=r['boundary_review_open'],
        geographic_accuracy='EMPIRICAL_TRANSFORM_UNCERTAIN',founding='UNTESTED') for r in all_rows]
    write_csv(out/'all_600_evidence_status.csv',statuses)
    # Original global-model landmark checks retained for map context, not presented
    # as independent validation of the new regional coastline translations.
    (out/'landmark_vector_audit.csv').write_bytes((V9/'landmark_vector_audit.csv').read_bytes())
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    contact_sheet(arrays,decisions,references,old_by_name,by_name,out)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets',type=Path,default=g.ROOT/'source_assets')
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--preview',action='store_true',help='Write reference samples only; no town decisions or files changed')
    a=parser.parse_args()
    if a.preview:
        if a.out.exists():raise FileExistsError('Use a new CSV')
        write_csv(a.out,reference_audit(inputs(a.assets)))
    else:print(json.dumps(generate(a.assets,a.out),indent=2))
