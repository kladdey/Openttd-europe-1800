"""Decode flat, typed OpenTTD table records; fail on unsupported schemas."""
from audit_vehicle_newgrfs import gamma

def decode_table(table):
    assert table['kind']==3
    schema=bytes.fromhex(table['records'][0]);p=0;fields=[]
    while schema[p]:
        t=schema[p];p+=1;n,p=gamma(schema,p);name=schema[p:p+n].decode();p+=n;fields.append((name,t))
    assert p+1==len(schema)
    result=[]
    for raw in table['records'][1:]:
        b=bytes.fromhex(raw);p=0;row={}
        for name,t in fields:
            base=t&15; count=1
            if t&16:count,p=gamma(b,p)
            if base==10:
                value=b[p:p+count].decode('utf8',errors='replace');p+=count
            else:
                size={1:1,2:1,3:2,4:2,5:4,6:4,7:8,8:8}[base]
                vals=[]
                for i in range(count):vals.append(int.from_bytes(b[p:p+size],'big',signed=base in (1,3,5,7)));p+=size
                value=vals if t&16 else vals[0]
            row[name]=value
        assert p==len(b),(p,len(b))
        result.append(row)
    return result

if __name__=='__main__':
    import json
    from pathlib import Path
    d=json.loads(Path('docs/research/vehicle_audit_v2/newgrf_inventory.json').read_text(encoding='utf8'));s=max(d['scenarios'],key=lambda s:s.get('mtime',0))
    out={key:decode_table(s[key]) for key in ('PATS','DATE','ECMY','MAPS')}
    Path('docs/research/scenario_economy_settings.json').write_text(json.dumps(out,indent=2),encoding='utf8')
    for k,v in out['PATS'][0].items():
        if any(x in k for x in ('cost','inflation','day_length','timekeeping','dynamic_engines','year')):print(k,v)
    print(out['ECMY'],out['DATE'][0]['date'],out['MAPS'])
