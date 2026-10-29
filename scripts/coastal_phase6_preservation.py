"""Map normalization and strict source/candidate guards for coastal additions."""
import numpy as np
from coastal_phase6_runtime import decode, chunks


def parts(path):
    return {t:(k,list(map(bytes,r))) for t,k,r in chunks(decode(path.read_bytes()))}


def maps(p):
    if 'WMAP' not in p:
        return {t:r[0] for t,(k,r) in p.items() if k==0 and (t.startswith('MAP') or t in ('M3LO','M3HI'))}
    n=4096**2
    raw=np.frombuffer(p['WMAP'][1][0],dtype='u1')
    a=raw[:n*8].reshape(n,8);e=raw[n*8:].reshape(n,4)
    m={t:a[:,i].tobytes() for t,i in [('MAPT',0),('MAPH',1),('MAPO',4),('M3LO',5),('M3HI',6),('MAP5',7)]}
    m.update(MAP2=a[:,[3,2]].tobytes(),MAPE=e[:,0].tobytes(),MAP7=e[:,1].tobytes(),MAP8=e[:,[3,2]].tobytes())
    return m


def differences(source,candidate):
    a,b=maps(parts(source)),maps(parts(candidate));n=4096**2
    changed=np.zeros(n,dtype=bool)
    for t in a:
        stride=len(a[t])//n
        changed|=np.any(np.frombuffer(a[t],dtype='u1').reshape(n,stride)!=np.frombuffer(b[t],dtype='u1').reshape(n,stride),axis=1)
    at=np.frombuffer(a['MAPT'],dtype='u1')>>4;bt=np.frombuffer(b['MAPT'],dtype='u1')>>4
    height=np.frombuffer(a['MAPH'],dtype='u1')!=np.frombuffer(b['MAPH'],dtype='u1')
    return a,b,changed,dict(changed_tiles=int(changed.sum()),height_changes=int(height.sum()),water_type_changes=int(np.count_nonzero((at==6)!=(bt==6))),existing_infrastructure_changes=int(np.count_nonzero(changed & np.isin(at,[1,2,5,9]))))
