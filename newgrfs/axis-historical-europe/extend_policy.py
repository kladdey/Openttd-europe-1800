# SPDX-License-Identifier: GPL-2.0-only
"""Expand the reviewed Classic matrix into an explicit, editable 92-type policy.

Run once when reviewing policy, not as an automatic build step. Dates without a
specific historical citation are campaign design choices, never discovered facts.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    path = ROOT / 'historical_manifest.json'
    manifest = json.loads(path.read_text())
    matrix = json.loads((ROOT.parents[1] / 'docs/research/axis-2.3.1-extreme-classic.json').read_text())
    text = (ROOT.parents[1] / 'docs/AXIS_INDUSTRY_MATRIX.md').read_text()
    bands = dict(re.findall(r'\| \d+ \| \[([^]]+)\].*?\| (P\d\*?|Exclude/import) \|', text))
    assert len(bands) == 91
    # Broad draft bands are refined for technologies with stronger evidence.
    defaults = {'P1': 0, 'P1*': 0, 'P2': 1850, 'P3': 1880,
                'P4': 1914, 'P5': 1945, 'P6': 1970, 'P7': 2000, 'Exclude/import': 0}
    refined = {
        'aluminium_plant': (1888, 'https://www.aluminum.org/primary-production-101'),
        'ammonia_plant': (1913, 'https://www.basf.com/global/en/who-we-are/history/chronology/1902-1924/1913'),
        'solvay_plant': (1863, 'https://www.solvay.com/en/our-company/history/1863-1885'),
        'electric_arc_furnace': (1906, 'docs/AXIS_HISTORICAL_IMPLEMENTATION.md#historical-basis-and-choices'),
        'basic_oxygen_furnace': (1952, 'docs/AXIS_HISTORICAL_IMPLEMENTATION.md#historical-basis-and-choices'),
        # Deliberately provisional adoption dates pending process/site review.
        'oil_wells': (1859, None), 'oil_refinery': (1859, None),
        'power_plant': (1882, None), 'polyethylene_plant': (1939, None),
        'fischer_tropsch_plant': (1936, None), 'chlor_alkali_plant': (1892, None),
        'tyre_plant': (1888, None), 'petrol_pump': (1888, None),
        'paper_mill': (0, None), 'copper_mine': (0, None),
        'pyrite_mine': (0, None), 'sulphuric_acid_plant': (0, None),
        'sugar_refinery': (0, None),
    }
    old = manifest['industries']
    rules = {}
    for item in matrix['industries']:
        name = item['id']; band = bands[name]
        year, citation = refined.get(name, (defaults[band], None))
        year = max(year, int(item['intro_year']))
        excluded = band == 'Exclude/import'
        rule = dict(earliest_year=year, final_construction_year=None,
                    allow_map_generation=not excluded, allow_natural_and_gs=not excluded,
                    allow_player_funding_and_prospecting=not excluded,
                    local_id=item['local_id'], source_band=band,
                    historical_evidence=citation,
                    date_status='SOURCED ADOPTION POLICY' if citation else 'PROVISIONAL CAMPAIGN POLICY',
                    prerequisites='Original AXIS location/keystone rules and cargo recipe retained',
                    existing_industries='Continue operating; no forced closure or conversion',
                    justification=('European resource policy exclusion; not a technology invention date' if excluded
                                   else 'Pre-1830 activity or declared AXIS proxy' if year == 0
                                   else 'Commercial-era gate; not a universal regional adoption date'))
        rules[name] = rule
    rules['steel_mill'] = old['steel_mill']
    rules['steel_mill'].update(local_id=2, date_status='SOURCED ADOPTION POLICY',
                              historical_evidence='docs/AXIS_HISTORICAL_IMPLEMENTATION.md#historical-basis-and-choices')
    manifest.update(version='0.2.0', grf_version=2, industries=rules)
    manifest['limitations'] = ['Provisional dates require sector review before a historically certified release',
                              'Early ports/machine shops retain modern cargo proxies; cargo IDs unchanged',
                              'No regional calendar or forced obsolescence; existing industries are grandfathered']
    path.write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
