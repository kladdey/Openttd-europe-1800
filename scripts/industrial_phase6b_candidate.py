"""Preserve source state and promote only actual engine-created industries.

INDY/PSAC/ANIT and industry-neutral STNN changes come from JGRPP. Founder is
the sole per-industry metadata edit: named U8 'founder' -> OWNER_NONE (16),
matching engine-generated neutral industries, rather than the fixture company.
No production/cargo/vehicle properties or dates are edited.
"""
import json,lzma
from pathlib import Path
import numpy as np
from industrial_phase6b_runtime import ROOT,BASE,SOURCE,EXPECTED,sha
from coastal_phase6_preservation import parts,maps,differences
from scenario_geography import gamma
from transport_phase3 import encode


def field_offset(schema,row,target):
    p=q=0
    while schema[p]:
        typ=schema[p];p+=1;n,p=gamma(schema,p);name=schema[p:p+n].decode();p+=n
        count=1
        if typ&16:count,q=gamma(row,q)
        base=typ&15
        if base not in range(1,9):raise ValueError('Unsupported field before '+target+': '+name)
        width={1:1,2:1,3:2,4:2,5:4,6:4,7:8,8:8}[base]
        if name==target:return q,width,count
        q+=width*count
    raise ValueError('Missing '+target)


def neutral_industries(records):
    rows=[records[0]]
    for row in records[1:]:
        if not row:rows.append(row);continue
        q,width,count=field_offset(records[0],row,'founder');assert (width,count)==(1,1)
        value=bytearray(row);assert value[q] in [0,16,18,255],value[q];value[q]=16;rows.append(bytes(value))
    return rows


def clean(engine_save,dest,allow_upgrade=False):
    source=parts(SOURCE);candidate=parts(engine_save);m=maps(candidate)
    assert source['CITY']==candidate['CITY'],'Original town records changed'
    if allow_upgrade:verify_grfs(engine_save)
    else:assert source['NGRF']==candidate['NGRF'],'Engine substituted a NewGRF'
    assert source['VEHS']==candidate['VEHS'],'Construction copy contains vehicles'
    out=[]
    for tag,(kind,rows) in source.items():
        if tag in m:rows=[m[tag]]
        elif tag=='INDY':rows=neutral_industries(candidate[tag][1])
        elif tag in ['PSAC','ANIT','STNN'] or (allow_upgrade and tag in ['NGRF','GLOG','IIDS','TIDS']):rows=candidate[tag][1]
        out.append(encode(tag,kind,rows))
    with dest.open('xb') as f:f.write(SOURCE.read_bytes()[:8]+lzma.compress(b''.join(out)+b'\0'*4))
    guard=verify(dest,allow_upgrade)
    return guard


def verify_grfs(path):
    from historical_scenario_migration import inspect
    a=inspect(SOURCE)['newgrfs'];b=inspect(path)['newgrfs']
    assert len(a)==len(b)==15
    for old,new in zip(a,b):
        if old['grfid']=='4B484531':
            assert new['grfid']==old['grfid'] and new['version']==3
            assert new['params']==old['params'] and new['palette']==old['palette']
        else:assert new==old,(old,new)


def verify(path,allow_upgrade=False):
    assert sha(SOURCE)==EXPECTED
    a,b,c,guard=differences(SOURCE,path);original=parts(SOURCE);candidate=parts(path)
    assert original['CITY']==candidate['CITY'] and len(candidate['CITY'][1])==618
    assert guard['height_changes']==guard['existing_infrastructure_changes']==0
    n=4096**2;at=np.frombuffer(a['MAPT'],dtype='u1')>>4;bt=np.frombuffer(b['MAPT'],dtype='u1')>>4
    assert not np.any(c & np.isin(at,[1,2,3,5,7,9,10])),'Protected road/house/object changed'
    assert np.all(np.isin(bt[(at==6)&c],[6,8,5])),'Water converted to non-industry land'
    assert np.all(np.isin(bt[c & np.isin(at,[0,4])],[0,4,8,5])),'Unexpected new infrastructure'
    for tag in original:
        if tag in set(a)|{'INDY','PSAC','ANIT','STNN'}|(set(['NGRF','GLOG','IIDS','TIDS']) if allow_upgrade else set()):continue
        assert original[tag]==candidate[tag],tag
    if allow_upgrade:verify_grfs(path)
    guard.update(original_towns=617,original_town_rows_bit_identical=True,industry_instances=len(candidate['INDY'][1])-1,
                 water_tiles_occupied_by_industry=int(np.count_nonzero((at==6)&(bt==8))),
                 protected_house_and_object_changes=int(np.count_nonzero(c & np.isin(at,[3,10]))),
                 source_sha256=EXPECTED,candidate_sha256=sha(path),candidate=str(path))
    return guard


if __name__=='__main__':
    r=json.loads((BASE/'placement-result.json').read_text(encoding='utf8'))
    dest=Path(r['case'])/'industry-candidate.scn'
    result=clean(Path(r['case'])/'save/autosave/exit.sav',dest)
    (BASE/'candidate.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result,indent=2))
