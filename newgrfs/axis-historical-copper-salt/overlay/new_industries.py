# SPDX-License-Identifier: GPL-2.0-only
"""Append-only Classic industry additions; reuse existing licensed tile graphics."""
import copy
import json
from pathlib import Path
import global_constants
from industry import IndustrySecondary
from industries import registered_industries,copper_refinery,stockyard,salt_mine
from historical_availability import condition_for_rule

M=json.loads(Path(__file__).with_name('copper_salt_manifest.json').read_text(encoding='utf8'))


def rule(name):
    r=M['additions'][name]
    return dict(earliest_year=r['earliest_year'],final_construction_year=None,allow_map_generation=True,allow_natural_and_gs=True,allow_player_funding_and_prospecting=True,recipe=dict(inputs=r.get('inputs',{}),outputs=r['outputs']))


def add(name,original,label):
    data=M['additions'][name];global_constants.industry_numeric_ids[name]=data['local_id']
    industry=IndustrySecondary(id=name,accept_cargos_with_input_ratios=list(data['inputs'].items()),
        prod_cargo_types_with_output_ratios=list(data['outputs'].items()),combined_cargos_boost_prod=False,
        prob_in_game='2',prob_map_gen='3',map_colour='64' if name.startswith('traditional') else '177',
        name='string('+label+')',nearby_station_name='string(STR_STATION_SMELTER)' if name.startswith('traditional') else 'string(STR_STATION_INDUSTRY_HARBOUR_2)',
        fund_cost_multiplier='120',intro_year=data['earliest_year'])
    industry.economy_variations['BASIC_TEMPERATE'].enabled=True
    industry.template='industry_historical_batch.pynml'
    industry.historical_rule=rule(name)
    industry.historical_condition=condition_for_rule(industry.historical_rule)
    terms=[f'incoming_cargo_waiting("{k}") / {v}' for k,v in data['inputs'].items()]
    expression=terms[0]
    for term in terms[1:]:expression=f'min({expression}, {term})'
    industry.historical_batch_expression=expression
    # Reuse original tile definitions without registering duplicate tile IDs or
    # changing their graphics/callbacks. New layout names are unique.
    for i,layout in enumerate(original.industry_layouts):
        industry.add_industry_layout(id=name+'_layout_'+str(i),layout=copy.deepcopy(layout.layout))
    industry.register()


add('traditional_copper_smelter',copper_refinery.industry,'STR_IND_TRADITIONAL_COPPER_SMELTER')
add('fish_saltery',stockyard.industry,'STR_IND_FISH_SALTERY')
add('meat_saltery',stockyard.industry,'STR_IND_MEAT_SALTERY')
salt=salt_mine.industry
salt.economy_variations['BASIC_TEMPERATE'].enabled=True
salt.economy_variations['BASIC_TEMPERATE'].prod_cargo_types_with_multipliers=[('SALT',20)]
salt.historical_rule=rule('salt_mine');salt.historical_condition=condition_for_rule(salt.historical_rule)
