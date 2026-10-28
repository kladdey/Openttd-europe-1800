"""Read-only identity, copy and financial reconciliation checks for Phase 3."""
import csv,hashlib,json,lzma,tarfile
from pathlib import Path
from transport_phase3 import encode
from scenario_geography import chunks
from validate_vehicle_audit import grfmd5
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs/research';R=ROOT/'.vehicle-audit-runtime/phase3'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    refs=json.loads((D/'scenario_vehicle_references.json').read_text());original=Path(refs['scenario']).read_bytes();assert sha(original)==refs['sha256']
    original_raw=lzma.decompress(original[8:]); parts=list(chunks(original_raw))
    assert b''.join(encode(*c) for c in parts)+b'\0'*4==original_raw,'Original encoder roundtrip differs'
    copy=(R/'scenario-test.scn').read_bytes();newparts=list(chunks(lzma.decompress(copy[8:])))
    assert len(parts)==len(newparts)
    changed=[a[0] for a,b in zip(parts,newparts) if a!=b];assert changed==['GSDT'],changed
    checked=[]
    for ref in refs['references']:
        name=ref['filename'].replace('\\','/');outer,sep,member=name.partition('.tar/')
        if sep:
            archive=R/'newgrf'/(outer+'.tar')
            with tarfile.open(archive) as tf:
                matches=[m for m in tf.getmembers() if m.name.replace('\\','/').lstrip('./').lower()==member.lower()]
                assert len(matches)==1,(member,[m.name for m in tf.getmembers()])
                data=tf.extractfile(matches[0]).read()
        else:data=(R/'newgrf'/name).read_bytes()
        assert grfmd5(data)==ref['md5'],name
        checked.append(ref['grfid'])
    prior=json.loads((D/'transport_phase3_inputs.json').read_text());mismatches=[]
    for p,h in prior['prior_research_sha256'].items():
        if sha((ROOT/p).read_bytes())!=h:mismatches.append(p)
    assert not mismatches,mismatches
    rows=list(csv.DictReader((D/'transport_route_results.csv').open(encoding='utf8')))
    discrepancies=[]
    for r in rows:
        if r['expense_method']=='Annual finance ledger':
            delta=int(r['ledger_net_gbp'])-int(r['net_cash_change_gbp'])
            if delta:discrepancies.append([r['tag'],r['economy_year'],delta])
        assert int(r['initial_capital_investment_gbp'])>=0 if 'initial_capital_investment_gbp' in r else int(r['infrastructure_capital_gbp'])>=0
    result={'status':'PASS: identities and preservation; different finance windows reported explicitly','original_encoder_byte_roundtrip':True,'changed_chunks':changed,'matched_grf_md5_identities':checked,'prior_research_files_unchanged':len(prior['prior_research_sha256']),'annual_rows':len(rows),'ledger_minus_cash_window_differences_gbp':discrepancies,'note':'Bank sampled about one day after year-end; cash and full-year ledger cover different windows. Discrepancies are retained, not silently forced to balance. Use the annual ledger for exact full-year expenses; cash changes establish actual company liquidity.'}
    (D/'transport_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
