"""Read Action 14 metadata only, without evaluating GRF code."""
import json,tarfile
from pathlib import Path
from audit_vehicle_newgrfs import actions,zstr

def nodes(a,p,path,out):
    while a[p]:
        kind=chr(a[p]);key=a[p+1:p+5];p+=5
        key=key.decode('ascii') if all(32<=c<127 for c in key) else str(int.from_bytes(key,'little'))
        dest=path+'/'+key
        if kind=='C':p=nodes(a,p,dest,out)
        elif kind=='B':
            n=int.from_bytes(a[p:p+2],'little');p+=2;b=a[p:p+n];p+=n
            out.append({'path':dest,'hex':b.hex(),'integer_le':int.from_bytes(b,'little')})
        elif kind=='T':
            lang=a[p];p+=1;s,p=zstr(a,p)
            if lang in (0,1,127):out.append({'path':dest,'language':lang,'text':s})
        else: raise ValueError(kind)
    return p+1

def main():
    inv=json.loads(Path('docs/research/vehicle_audit_v2/newgrf_inventory.json').read_text(encoding='utf8'));out=[]
    seen=set()
    for g in inv['newgrfs']:
        if g.get('grfid') not in ('44441000','44440302','4E4D0518','53410808','4D560103','4D560105','54574607','544D0101'):continue
        if g['sha256'] in seen:continue
        seen.add(g['sha256'])
        if 'member' in g:
            with tarfile.open(g['path']) as t:b=t.extractfile(g['member']).read()
        else:b=Path(g['path']).read_bytes()
        meta=[]
        for offset,a in actions(b):
            if a and a[0]==20:nodes(a,1,'',meta)
        out.append({'grfid':g['grfid'],'sha256':g['sha256'],'metadata':meta})
    Path('docs/research/vehicle_grf_parameters.json').write_text(json.dumps(out,indent=2),encoding='utf8')
    for g in out:
        print(g['grfid'])
        for m in g['metadata']:
            if '/PARA/' in m['path'] and 'text' in m:print(m['path'],ascii(m['text']))

if __name__=='__main__':main()
