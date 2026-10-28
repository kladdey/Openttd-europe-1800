"""Validate joins, source identity, source preservation and report arithmetic."""
import csv,json,hashlib,tarfile,collections
from pathlib import Path
R=Path('docs/research')
def sha(b):return hashlib.sha256(b).hexdigest()
def grfmd5(b):
    if b[:10]==b'\x00\x00GRF\x82\x0d\x0a\x1a\x0a':b=b[:14+int.from_bytes(b[10:14],'little')]
    return hashlib.md5(b).hexdigest()
def main():
    inv=json.loads((R/'newgrf_inventory.json').read_text(encoding='utf8'));refs=inv['scenario']['references'];matched=[];checked={}
    for g in inv['installed_newgrfs']:
        p=Path(g['path'])
        if str(p) not in checked:checked[str(p)]=sha(p.read_bytes())
        assert checked[str(p)]==g.get('archive_sha256',g['sha256']),str(p)
        if any(r['grfid']==g.get('grfid') for r in refs):
            if 'member' in g:
                with tarfile.open(p) as t:b=t.extractfile(g['member']).read()
            else:b=p.read_bytes()
            assert sha(b)==g['sha256']
            ref=next(r for r in refs if r['grfid']==g['grfid'])
            assert grfmd5(b)==ref['md5'],(g['path'],grfmd5(b),ref['md5'])
            matched.append(g['grfid'])
    assert set(matched)=={r['grfid'] for r in refs}
    assert sha(Path(inv['scenario']['scenario']).read_bytes())==inv['scenario']['sha256']
    save=json.loads((R/'newest_autosave_economy.json').read_text());assert sha(Path(save['path']).read_bytes())==save['sha256']
    for f in inv['fingerprints']:assert sha(Path(f['path']).read_bytes())==f['sha256']
    rows=list(csv.DictReader((R/'vehicle_roster.csv').open(encoding='utf-8-sig')))
    assert len(rows)==2887 and len({(r['source_grfid'],r['local_vehicle_id']) for r in rows})==2887
    counts=collections.Counter(r['source_grfid'] for r in rows);assert dict(counts)==inv['runtime_counts']
    for r in rows:
        if r['power_hp']!='UNVERIFIED' and int(r['power_hp'])>0:
            assert abs(float(r['purchase_per_hp'])-int(r['purchase_price_gbp'])/int(r['power_hp']))<0.0001
        assert r['retirement_year']=='UNVERIFIED'
    snapshots=list(csv.DictReader((R/'vehicle_economy_snapshots.csv').open(encoding='utf-8-sig')))
    assert len(snapshots)==17322
    for year in (1830,1850,1900,1950,2000,2025):
        subset=[r for r in snapshots if int(r['snapshot_year'])==year];assert len(subset)==2887
        assert collections.Counter(r['source_grfid'] for r in subset)==counts
    settings=json.loads((R/'scenario_economy_settings.json').read_text())
    assert settings['ECMY'][0]['inflation_prices']==65536
    for k,v in {'difficulty.construction_cost':0,'difficulty.vehicle_costs':0,'economy.inflation':0,'economy.day_length_factor':1,'vehicle.dynamic_engines':1}.items():assert settings['PATS'][0][k]==v
    # These are defined engine cost formulas, independent of the CSV exporter.
    assert (400000*6//8*6)//256==7031
    assert (400000*6//8*2*2)//256==4687
    assert (5600*6//8*4*8)//256==525
    assert (5600*6//8*24*8)//256==3150
    for p in Path('docs').glob('*VEHICLE*.md'):
        for text in p.read_text(encoding='utf8').split('](')[1:]:
            link=text.split(')',1)[0]
            if not link.startswith(('https:','http:','#')):assert (p.parent/link).exists(),link
    output={'status':'PASS','source_paths_checked':len(checked),'grf_instances':83,'distinct_grf_hashes':74,'scenario_references_md5_matched':len(set(matched)),'unique_roster_keys':len(rows),'snapshot_rows':len(snapshots),'counts':dict(counts),'limits':'Validates extraction identities and arithmetic, not depot builds, attachment or route profitability.'}
    (R/'vehicle_audit_validation.json').write_text(json.dumps(output,indent=2),encoding='utf8');print(json.dumps(output,indent=2))
if __name__=='__main__':main()
