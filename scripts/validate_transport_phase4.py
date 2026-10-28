"""Read-only preservation, accounting and experimental-boundary validation."""
import csv,hashlib,json,os,tarfile
from pathlib import Path
from validate_vehicle_audit import grfmd5
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs/research';BASE=ROOT/'.vehicle-audit-runtime/phase4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    baseline=json.loads((D/'transport_phase4_inputs.json').read_text())
    for p,h in baseline['prior_research_sha256'].items():assert sha(ROOT/p)==h,p
    inv=json.loads((D/'newgrf_inventory.json').read_text())
    for f in inv['fingerprints']:assert sha(Path(f['path']))==f['sha256'],f['path']
    checked={}
    for g in inv['installed_newgrfs']:
        p=Path(g['path']);checked.setdefault(str(p),sha(p));assert checked[str(p)]==g.get('archive_sha256',g['sha256'])
    ref=json.loads((D/'scenario_vehicle_references.json').read_text());assert sha(Path(ref['scenario']))==ref['sha256']
    first=BASE/'three-final/newgrf';matched=[]
    for r in ref['references']:
        n=r['filename'].replace('\\','/');outer,sep,member=n.partition('.tar/')
        if sep:
            p=first/(outer+'.tar')
            with tarfile.open(p) as tf:
                found=[m for m in tf.getmembers() if m.name.replace('\\','/').lstrip('./').lower()==member.lower()];assert len(found)==1
                data=tf.extractfile(found[0]).read()
        else:p=first/n;data=p.read_bytes()
        assert grfmd5(data)==r['md5'];matched.append(r['grfid'])
        for home in BASE.iterdir():
            if (home/'manifest.json').exists():assert os.path.samefile(home/'newgrf'/p.name,p)
    copy=json.loads((D/'transport_scenario_copy_manifest.json').read_text())['test_copy_sha256']
    configs=json.loads((D/'transport_phase4_run_configs.json').read_text())
    for m in configs:
        assert m['scenario_sha256']==copy
        assert m['exe_sha256']==next(f['sha256'] for f in inv['fingerprints'] if f['path']==m['arguments'][0])
        code=(BASE/m['tag']/'game/p3/main.nut').read_text()
        for prohibited in ['ChangeBankBalance','GSGameSettings.SetValue','SetCurrentDate']:assert prohibited not in code
    with (D/'three_company_simulation.csv').open(encoding='utf8') as f:rows=list(csv.DictReader(f))
    assert len(rows)==120
    residual={}
    for tag,c in [(tag,c) for tag in ['three-final','three-credit-matched'] for c in range(3)]:
        company=[r for r in rows if int(r['company_id'])==c and r['tag']==tag];assert [int(r['economy_year']) for r in company]==list(range(1800,1820))
        assert all(int(r['cash_gbp'])>0 for r in company)
        ledgers=[json.loads(r['ledger_json']) for r in company]
        expected=100000+sum(int(r['annual_operating_profit_gbp'])-int(r['annual_capex_gbp']) for r in company)+int(company[-1]['loan_gbp'])-100000
        residual[tag+'/'+str(c)]=int(company[-1]['cash_gbp'])-expected
        assert sum(l[12] for l in ledgers)==6000
    early=[]
    for r in rows:
        if int(r['economy_year'])<1810:
            peer=next(x for x in rows if x['tag']!=r['tag'] and x['company_id']==r['company_id'] and x['economy_year']==r['economy_year'])
            for field in ['cash_gbp','loan_gbp','ledger_json','company_value_gbp','delivered_units']:assert peer[field]==r[field],(field,r)
            early.append(r)
    result={'status':'PASS','protected_prior_research_files':len(baseline['prior_research_sha256']),'original_installed_asset_paths_checked':len(checked),'newgrf_identities':matched,'test_assets_same_file_across_cases':True,'only_disposable_GSDT_copy_used':True,'main_company_years':len(rows),'matched_pre_intervention_company_year_pairs':len(early)//2,'full_horizon_cash_ledger_residuals_gbp':residual,'residual_note':'Finance-year ledgers and year-end bank observations differ by approximately one day; residuals are retained, not forced to match.','no_artificial_cash_or_settings_mutations_in_harness':True}
    (D/'transport_phase4_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
