#!/usr/bin/env python3
"""Offline interactive V7 town map, full-map PNG and labelled regional atlas."""
import argparse
import base64
import csv
import io
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
V7 = ROOT/'maps/calibration/geography_v7'
CLEAR, REVIEW, OCEAN = '#67e6bd', '#ffbd69', '#0b1523'


def csv_rows(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def load_points():
    towns = json.loads((V7/'Europe_1800_V7_ALL_IN_BOUNDS_TEST.json').read_text())
    master = {t['name']: t for t in json.loads((ROOT/'data/towns/europe_1800_import_AUDIT_FIXED_TEST.json').read_text())}
    audits = csv_rows(V7/'all_600_placement_audit.csv')
    nearest = {r['name']: r for r in csv_rows(V7/'all_town_nearest_neighbours.csv')}
    by_name = {r['name']: r for r in audits}
    points = []
    for t in towns:
        r = by_name[t['name']]
        points.append(dict(name=t['name'], region=r['region'], population=t['population'], city=t['city'],
                           col=int(r['sampled_column']), row=int(r['sampled_row']),
                           lat=float(r['latitude']), lon=float(r['longitude']),
                           clear=r['direct_clear_land'] == 'True',
                           near=nearest[t['name']]['nearest_town'],
                           distance=float(nearest[t['name']]['distance_tiles']),
                           issue=r['override_reason'], boundary=r['boundary_review'] == 'True'))
    deferred = [dict(name=r['name'], region=r['region'], population=master[r['name']]['population'],
                     lat=float(r['latitude']), lon=float(r['longitude']), reason=r['reason'])
                for r in audits if r['coverage_status'] == 'DEFERRED_OUTSIDE_MAP']
    if len(points) != 576 or len(deferred) != 24 or sum(p['clear'] for p in points) != 520:
        raise ValueError('V7 counts changed; update visualisation labels deliberately')
    return points, deferred, csv_rows(V7/'close_pairs_review.csv')


def basemap():
    with Image.open(ROOT/'source_assets/heightmaps/Europe_heightmap_original.png') as im:
        raw = np.array(im)[:, :, 0]
    # Display-only relief palette. Coordinates and source raster remain untouched.
    z = np.clip((raw.astype(float)-23)/232, 0, 1)**.55
    low = np.array([37, 57, 63]); high = np.array([202, 214, 210])
    rgb = low[None, None, :] + z[:, :, None]*(high-low)
    rgb[raw == 0] = [11, 21, 35]
    return rgb.astype('uint8')


def panel(ax, image, points, bounds, title, labels):
    left, right, top, bottom = bounds
    ax.imshow(image, extent=(0, 4096, 4096, 0), interpolation='nearest')
    visible = [p for p in points if left <= p['col'] <= right and top <= p['row'] <= bottom]
    for clear, color in [(True, CLEAR), (False, REVIEW)]:
        group = [p for p in visible if p['clear'] == clear]
        ax.scatter([p['col'] for p in group], [p['row'] for p in group],
                   s=[10+np.sqrt(p['population'])*.45 for p in group],
                   c=color, edgecolors=OCEAN, linewidths=.5, alpha=.96, zorder=3)
    occupied = []
    for p in sorted(visible, key=lambda p: p['population'], reverse=True):
        if not labels and p['population'] < 1200:
            continue
        # Greedy display-label placement: labels never alter marker coordinates.
        w = min(160, len(p['name'])*5.2)*(right-left)/900
        h = (bottom-top)/70
        for dx, dy in [(7, -7), (7, 10), (-w-7, -7), (-w-7, 10), (10, -22)]:
            dx *= (right-left)/900 if dx >= 0 else 1
            dy *= (bottom-top)/900
            x, y = p['col']+dx, p['row']+dy
            rect = (x-1, x+w+1, y-h, y+h/3)
            if rect[0] < left or rect[1] > right or rect[2] < top or rect[3] > bottom:
                continue
            if any(not(rect[1] < r[0] or rect[0] > r[1] or rect[3] < r[2] or rect[2] > r[3]) for r in occupied):
                continue
            ax.text(x, y, p['name'], color='#e6f1f5', fontsize=5.6 if labels else 7.1,
                    va='center', zorder=5, path_effects=[pe.withStroke(linewidth=2.1, foreground=OCEAN)])
            occupied.append(rect)
            break
    ax.set_xlim(left, right); ax.set_ylim(bottom, top)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(f'{title} · {len(visible)} targets', color='#e6f1f5', loc='left', fontsize=12, pad=9)
    for spine in ax.spines.values():
        spine.set_edgecolor('#344554')


def render(out):
    if out.exists():
        raise FileExistsError('Use a new output directory')
    points, deferred, pairs = load_points()
    image = basemap()
    out.mkdir(parents=True)
    fig, ax = plt.subplots(figsize=(15, 16), facecolor=OCEAN)
    panel(ax, image, points, (0, 4096, 0, 4096), 'EUROPE 1800 / V7', False)
    fig.suptitle('576 towns on the original Europe heightmap', color='#f2f7f8', fontsize=21, x=.07, ha='left', y=.973)
    fig.text(.07, .939, '520 clear-land targets', color=CLEAR, fontsize=11)
    fig.text(.36, .939, '56 terrain-review targets', color=REVIEW, fontsize=11)
    fig.text(.07, .027, 'Projection estimate · Founding untested · 24 towns outside the fitted map are not plotted', color='#aebdca', fontsize=10)
    fig.subplots_adjust(left=.055, right=.975, top=.916, bottom=.055)
    fig.savefig(out/'Europe_1800_V7_TOWNS_OVERVIEW.png', dpi=190, facecolor=OCEAN)
    plt.close(fig)
    regions = [('British Isles', (200, 1620, 0, 1650)),
               ('France, Benelux & western Germany', (850, 2550, 1150, 2420)),
               ('Iberia', (250, 1900, 2480, 3890)),
               ('Italy & the Alps', (1900, 3300, 1770, 3670)),
               ('Central Europe & Baltic coast', (2250, 4096, 550, 2200)),
               ('Balkans & southeastern Europe', (2700, 4096, 2000, 3860))]
    fig, axes = plt.subplots(2, 3, figsize=(21, 16), facecolor=OCEAN)
    for ax, (title, bounds) in zip(axes.ravel(), regions):
        panel(ax, image, points, bounds, title, True)
    fig.suptitle('Europe 1800 / V7 — regional town placement atlas', color='#f2f7f8', fontsize=22, x=.04, ha='left', y=.97)
    fig.text(.04, .935, 'Green: clear-land target     Amber: terrain review     Labels shown where space permits; every town is searchable in the interactive map.', color='#c9d7df', fontsize=11)
    fig.text(.04, .027, 'Panels overlap. Geographic calibration is approximate; positions are import targets, not verified founding locations.', color='#aebdca', fontsize=11)
    fig.subplots_adjust(left=.035, right=.98, top=.905, bottom=.06, wspace=.08, hspace=.14)
    fig.savefig(out/'Europe_1800_V7_REGIONAL_ATLAS.png', dpi=160, facecolor=OCEAN)
    plt.close(fig)
    # Single offline HTML file: no network requests, external scripts or map services.
    small = Image.fromarray(image).resize((1800, 1800), Image.Resampling.LANCZOS)
    buffer = io.BytesIO(); small.save(buffer, format='PNG', optimize=True)
    data = dict(points=points, deferred=deferred, pairs=pairs)
    template = (Path(__file__).with_name('town_map_template.html')).read_text(encoding='utf-8')
    html = template.replace('__BASEMAP__', base64.b64encode(buffer.getvalue()).decode())
    html = html.replace('__TOWN_DATA__', json.dumps(data, ensure_ascii=False).replace('<', '\\u003c'))
    (out/'Europe_1800_V7_INTERACTIVE_MAP.html').write_text(html, encoding='utf-8')
    return dict(plotted=len(points), deferred=len(deferred), terrain_review=sum(not p['clear'] for p in points), output=str(out))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(render(args.out), indent=2))
