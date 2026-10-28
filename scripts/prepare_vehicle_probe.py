"""Prepare an isolated, disposable runtime probe. Never writes original files.

Copies GRFs for local use only into ignored .vehicle-audit-runtime. Does not
alter or load a scenario: rebuilds its GRF list on a small generated test map.
"""
import json, shutil, re
from pathlib import Path
from audit_vehicle_newgrfs import gamma

def string(b,p):
    n,p=gamma(b,p); return b[p:p+n].decode('utf8',errors='replace'),p+n

def ngrf(s):
    expected='1a0866696c656e616d65060b6964656e742e6772666964120c6964656e742e6d643573756d060776657273696f6e1605706172616d020770616c657474651a086772665f6e616d6500'
    assert s['NGRF']['records'][0]==expected, 'Unexpected scenario GRF schema'
    result=[]
    for record in s['NGRF']['records'][1:]:
        b=bytes.fromhex(record); filename,p=string(b,0)
        grfid=b[p:p+4][::-1].hex().upper();p+=4
        n,p=gamma(b,p);assert n==16;md5=b[p:p+16].hex();p+=16
        version=int.from_bytes(b[p:p+4],'big');p+=4
        n,p=gamma(b,p);params=[int.from_bytes(b[p+i*4:p+i*4+4],'big') for i in range(n)];p+=4*n
        palette=b[p];p+=1;name,p=string(b,p);assert p==len(b)
        result.append(dict(filename=filename,grfid=grfid,md5=md5,version=version,params=params,palette=palette,name=name))
    return result

def main():
    d=json.loads(Path('docs/research/vehicle_audit_v2/newgrf_inventory.json').read_text(encoding='utf8'))
    s=max(d['scenarios'],key=lambda s:s.get('mtime',0)); refs=ngrf(s)
    Path('docs/research/scenario_vehicle_references.json').write_text(json.dumps({'scenario':s['path'],'sha256':s['sha256'],'references':refs},indent=2),encoding='utf8')
    run=Path('.vehicle-audit-runtime');run.mkdir(exist_ok=True);(run/'newgrf').mkdir(exist_ok=True)
    config=Path(r'C:\Users\Kladd\Documents\OpenTTD\openttd.cfg').read_text(encoding='utf8')
    config=re.sub(r'\[newgrf\][\s\S]*?(?=\n\[)', lambda m: '[newgrf]\n'+'\n'.join(f"{r['grfid']}|{r['md5'].upper()}|{r['filename']} = "+' '.join(map(str,r['params'])) for r in refs)+'\n',config)
    for r in refs:
        filename=r['filename'].split('\\')[0]
        candidates=[g for g in d['newgrfs'] if g.get('grfid')==r['grfid'] and Path(g['path']).name.lower()==filename.lower()]
        assert candidates,r
        src=Path(candidates[0]['path']);dst=run/'newgrf'/src.name
        if not dst.exists():shutil.copyfile(src,dst)
    for key,value in {'map_x':'6','map_y':'6','generation_seed':'1830','starting_year':'1830','autosave_interval':'0','autosave':'off','max_no_competitors':'0','server_advertise':'false','survey_participation':'false','network_id':'','server_password':''}.items():
        config=re.sub(r'(?m)^'+key+r' = .*$',key+' = '+value,config)
    config=re.sub(r'\[game_scripts\][\s\S]*?(?=\n\[|\Z)','[game_scripts]\nVehicleAuditProbe = \n',config)
    (run/'probe.cfg').write_text(config,encoding='utf8')
    gs=run/'game'/'vehicle_audit';gs.mkdir(parents=True,exist_ok=True)
    for filename in ('info.nut','main.nut'):shutil.copyfile(Path('scripts/vehicle_audit_probe')/filename,gs/filename)
    print(s['path']);print('\n'.join(r['name'] for r in refs));print('Prepared',run)

if __name__=='__main__':main()
