#!/usr/bin/env python3
"""Standalone V9 evidence map (HTML and PNG); evidence classes are not probabilities."""
import argparse
import base64
import io
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

import geography as g
from review_europe_placements import rows
from scenario_geography import source_pixel
from visualize_europe_towns import basemap

V8 = g.ROOT/'maps/calibration/geography_v8'
COLORS = {'CONDITIONAL_CLEAR_TARGET':'#70d9b0', 'TERRAIN_REVIEW_OPEN':'#ffb454',
          'BOUNDARY_REVIEW_OPEN':'#cfa1ff', 'DEFERRED':'#fa7686'}
LABELS = {'CONDITIONAL_CLEAR_TARGET':'Conditional clear target', 'TERRAIN_REVIEW_OPEN':'Terrain review open',
          'BOUNDARY_REVIEW_OPEN':'Boundary review open', 'DEFERRED':'Deferred (in-bounds shown)'}


def render(report, out, version='V9'):
    if out.exists():
        raise FileExistsError('Use a new output directory')
    statuses = rows(report/'all_600_evidence_status.csv')
    if not version.startswith('V') or not version[1:].isdigit():
        raise ValueError('Version label must be V followed by digits')
    retained=sum(r['evidence_status']!='DEFERRED' for r in statuses)
    deferred=len(statuses)-retained
    terrain=sum(r['evidence_status']=='TERRAIN_REVIEW_OPEN' for r in statuses)
    outside=sum(not r['x'] for r in statuses)
    points = []
    for r in statuses:
        if r['x'] and r['y']:
            col, row = source_pixel(float(r['x']), float(r['y']))
            points.append(dict(r, col=col, row=row))
    landmarks = rows(report/'landmark_vector_audit.csv')
    rgb = basemap()
    out.mkdir(parents=True)
    fig, ax = plt.subplots(figsize=(14, 15), facecolor='#0b1523')
    ax.imshow(rgb)
    for category, color in COLORS.items():
        group = [p for p in points if p['evidence_status'] == category]
        ax.scatter([p['col'] for p in group], [p['row'] for p in group], s=12 if category!='DEFERRED' else 24,
                   c=color, marker='o' if category!='DEFERRED' else 'x', linewidths=.6,
                   label=f'{LABELS[category]} ({len(group)})')
    measured = [r for r in landmarks if r['observed_column']]
    for r in measured:
        x, y = float(r['observed_column']), float(r['observed_row'])
        px, py = float(r['projected_column']), float(r['projected_row'])
        ax.plot([x, px], [y, py], color='#ffffff', lw=.7, alpha=.8)
    ax.scatter([float(r['observed_column']) for r in measured], [float(r['observed_row']) for r in measured],
               marker='+', s=35, c='white', label=f'Global-model landmark observations ({len(measured)})')
    ax.set_xlim(0,4095); ax.set_ylim(4095,0); ax.set_xticks([]); ax.set_yticks([])
    ax.legend(loc='lower right', fontsize=8, facecolor='#172735', labelcolor='white', framealpha=.95)
    ax.set_title(f'EUROPE 1800 / {version} evidence status', color='white', loc='left', fontsize=19, pad=18)
    fig.text(.07,.025,f'{retained} retained · {deferred} deferred ({outside} outside raster) · {terrain} retained water/occupancy flags · Founding untested\nEmpirical transforms; white landmarks show earlier global-model checks. Colours are evidence classes, not accuracy scores.',color='#d1dbe5',fontsize=9)
    fig.subplots_adjust(left=.06,right=.98,bottom=.07,top=.95)
    fig.savefig(out/'evidence_overview.png',dpi=140,facecolor=fig.get_facecolor()); plt.close(fig)
    buf=io.BytesIO(); Image.fromarray(rgb).resize((1536,1536),Image.Resampling.LANCZOS).save(buf,format='PNG')
    encoded=base64.b64encode(buf.getvalue()).decode('ascii')
    data=dict(points=points,all= statuses,landmarks=landmarks,colors=COLORS,labels=LABELS)
    template=(Path(__file__).with_name('evidence_map_template.html')).read_text(encoding='utf-8')
    html=template.replace('__BASEMAP__',encoded).replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('<','\\u003c'))
    html=html.replace('__VERSION__',version).replace('__RETAINED__',str(retained)).replace('__DEFERRED__',str(deferred)).replace('__OUTSIDE__',str(outside))
    (out/'evidence_map.html').write_text(html,encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report',type=Path,default=g.ROOT/'maps/calibration/geography_v9')
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--version',default='V9')
    a=p.parse_args();render(a.report,a.out,a.version)
