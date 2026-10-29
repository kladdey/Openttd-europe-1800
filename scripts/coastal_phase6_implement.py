"""Promote only terrain-preserving engine-generated town additions.

Outputs remain disposable; no campaign file is written by this script.
Rejected trials are retained with their exact manifests and engine logs.
"""
import json,lzma,re
import numpy as np
from coastal_phase6_runtime import BASE,ROOT,SOURCE,EXPECTED,sha,run,encode
from coastal_phase6_place import script
from coastal_phase6_preservation import parts,maps,differences


def clean(source,engine_save,dest):
    before=parts(source);after=parts(engine_save);out=[];m=maps(after)
    assert before['CITY'][1]==after['CITY'][1][:len(before['CITY'][1])]
    for t,(k,rows) in before.items():
        if t=='CITY':rows=after[t][1]
        elif t in m:rows=[m[t]]
        out.append(encode(t,k,rows))
    dest.write_bytes(source.read_bytes()[:8]+lzma.compress(b''.join(out)+b'\0'*4))


def main():
    rows=json.loads((BASE/'proposals.json').read_text());current=SOURCE
    decisions=[]
    inventory=(ROOT/'scripts/coastal_phase6_inventory.nut').read_text(encoding='utf-8-sig')
    body=inventory[inventory.index('  local passengers='):inventory.index('  GSLog.Info("C6 DONE')]
    for r in rows:
        accepted=False
        for attempt in range(4):
            n=len(parts(current)['CITY'][1])-1
            s=script([r],attempt)
            s=s[:s.index('foreach(t,_ in GSTownList())')]+body.replace('foreach(town,_ in GSTownList()){',f'foreach(town,_ in GSTownList()){{if(town<{n})continue;')+'GSLog.Info("C6 DONE");while(true)Sleep(365);}}'
            home=run(s,'place-'+re.sub('[^a-z]','',r['name'].lower())+'-'+str(attempt),800,source=current)
            saved=home/'save/autosave/exit.sav'
            log=(home/'engine.log').read_text(encoding='utf8',errors='replace')
            if not saved.exists() or 'C6 DONE' not in log:raise RuntimeError('Incomplete engine run '+str(home))
            found=re.search(r'C6 TOWN\|(\d+)\|([^|]+)\|(\d+)\|(\d+)\|(\d+)',log)
            row=dict(name=r['name'],attempt=attempt,case=str(home.relative_to(ROOT)),evidence='VERIFIED IN GAME')
            if not found:row.update(status='REJECTED TRIAL',reason='No supported FoundTown placement succeeded in bounded reviewed patch');decisions.append(row);continue
            _,_,changed,guards=differences(current,saved)
            dock=re.search(r'C6 DOCK\|(\d+)\|(\d+)\|(\d+)\|(-?\d+)\|(\d+)\|(\d+)\|(\d+)',log)
            row.update(guards,town_id=int(found[1]),x=int(found[3]),y=int(found[4]),population=int(found[5]),dock_tile=int(dock[4]) if dock else -1)
            checks=all(guards[k]==0 for k in ('height_changes','water_type_changes','existing_infrastructure_changes'))
            checks &= 80<=row['population']<=1000 and row['dock_tile']>=0
            checks &= parts(current)['CITY'][1]==parts(saved)['CITY'][1][:n+1]
            # Houses may clear grass/trees; no persistent changes beyond new
            # houses/roads, their metadata and their immediate site clearing.
            old=maps(parts(current));new=maps(parts(saved))
            at=np.frombuffer(old['MAPT'],dtype='u1')>>4;bt=np.frombuffer(new['MAPT'],dtype='u1')>>4
            ids=np.flatnonzero(changed)
            checks &= bool(np.all(np.isin(at[ids],[0,4])))
            checks &= bool(np.all(np.isin(bt[ids],[0,2,3,4])))
            checks &= bool(np.all(np.abs(ids%4096-row['x'])+np.abs(ids//4096-row['y'])<=35))
            row.update(status='ACCEPTED' if checks else 'REJECTED TRIAL',reason='All preservation, population and actual dock-command/catchment gates passed' if checks else 'Preservation, population or practical dock-catchment gate failed',engine_log_sha256=sha(home/'engine.log'))
            decisions.append(row)
            (BASE/'placement-decisions.json').write_text(json.dumps(decisions,indent=2,ensure_ascii=False),encoding='utf8')
            print(json.dumps(row,ensure_ascii=False),flush=True)
            if checks:
                dest=home/'accepted.scn';clean(current,saved,dest);current=dest;accepted=True;break
        if not accepted:print('DEFERRED '+r['name'],flush=True)
    result=dict(source_sha256=EXPECTED,candidate=str(current),candidate_sha256=sha(current),decisions=decisions)
    (BASE/'implementation.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    assert sha(SOURCE)==EXPECTED


if __name__=='__main__':main()
