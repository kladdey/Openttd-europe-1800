"""Extract trusted prepared Historical AXIS models without modifying the GRF."""
import hashlib,json,os,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FORK=ROOT/'newgrfs/axis-historical-europe'


def main():
    candidate='--candidate' in sys.argv
    active_fork=ROOT/'newgrfs/axis-historical-copper-salt' if candidate else FORK
    source=active_fork/'.work/source';sys.path.insert(0,str(source/'src'));os.chdir(source)
    import firs
    economy=next(e for e in firs.registered_economies if e.id=='BASIC_TEMPERATE')
    manifest=json.loads((FORK/'historical_manifest.json').read_text(encoding='utf8'))
    rows=[]
    for item in sorted(firs.registered_industries,key=lambda i:i.numeric_id):
        if not item.get_property('enabled',economy):continue
        rule=getattr(item,'historical_rule',manifest['industries'].get(item.id))
        assert rule is not None,item.id
        earliest=max(rule['earliest_year'],int(item.get_intro_year(economy)))
        row=dict(industry=item.id,local_id=item.numeric_id,model_class=type(item).__name__,earliest_year=earliest,upstream_expiry_year=int(item.get_expiry_year(economy)),historical_rule=rule,
                 available_1830=earliest<=1830<=int(item.get_expiry_year(economy)) and rule['allow_player_funding_and_prospecting'] and (rule['final_construction_year'] is None or 1830<=rule['final_construction_year']),
                 accepted=item.get_accept_cargo_types(economy),produced=item.get_prod_cargo_types(economy),
                 properties={k:item.get_property(k,economy) for k in vars(item.default_industry_properties)},
                 layouts=[vars(layout) for layout in item.industry_layouts],
                 industry_location_checks={k:v for k,v in vars(item.location_checks).items() if k!='industry'},
                 tile_location_checks=[dict(tile=t.id,checks={k:v for k,v in vars(t.location_checks).items() if not k.startswith('_')}) for t in item.tiles],
                 source_file='src/industries/'+item.id+'.py' if (source/'src/industries'/f'{item.id}.py').exists() else 'src/historical_copper_salt.py',source_sha256=hashlib.sha256(((source/'src/industries'/f'{item.id}.py') if (source/'src/industries'/f'{item.id}.py').exists() else source/'src/historical_copper_salt.py').read_bytes()).hexdigest())
        rows.append(row)
    assert len(rows)==(96 if candidate else 92)
    cargos={c.id:c for c in firs.registered_cargos}
    result=dict(source_commit=manifest['upstream_commit'],grfid=manifest['grfid'],version='0.3.0-candidate' if candidate else manifest['version'],economy=economy.id,
                cargo_slots=[dict(slot=i,id=c,cargo_label=cargos[c].cargo_label) for i,c in enumerate(economy.cargo_ids)],industries=rows)
    out=ROOT/('docs/research/industrial_1830_candidate_matrix.json' if candidate else 'docs/research/industrial_1830_source_matrix.json');out.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    print('Registered',len(rows),'available by source',sum(r['available_1830'] for r in rows))
    for r in rows:
        if r['available_1830']:print(r['local_id'],r['industry'],r['accepted'],'->',r['produced'])


if __name__=='__main__':main()
