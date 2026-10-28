"""Read local GRFs/scenarios without running or changing OpenTTD.

Static extraction only: conditional Action 0 assignments are evidence, not an
emulated NewGRF runtime. No sprites or GRF binaries are written to the output.
"""
import argparse, csv, hashlib, json, lzma, struct, tarfile, ctypes
from pathlib import Path
from scenario_geography import chunks, gamma

def sha(data): return hashlib.sha256(data).hexdigest()
def text(data): return data.decode('utf-8', errors='replace')
def zstr(data, pos):
    end = data.index(0, pos)
    return text(data[pos:end]), end+1
def ext(data, pos):
    n=data[pos]; pos+=1
    if n==255: n=int.from_bytes(data[pos:pos+2], 'little'); pos+=2
    return n,pos

def actions(data):
    v2=data[:10]==b'\x00\x00GRF\x82\x0d\x0a\x1a\x0a'
    p=14 if v2 else 0
    if v2:
        compression=data[p]; p+=1
        if compression: raise ValueError('Compressed GRF stream unsupported')
    width=4 if v2 else 2
    while p+width<=len(data):
        offset=p; n=int.from_bytes(data[p:p+width], 'little'); p+=width
        if not n: return
        kind=data[p]; p+=1
        if kind==255:
            yield offset,data[p:p+n]
            p+=n
        elif v2:
            p+=n
        else:
            # V1 real sprites have a 7-byte header; compressed pixel stream
            # consumes variable input until its declared output size is reached.
            h=data[p:p+7]; p+=7
            target=n-8
            if kind & 2: target=h[0]*int.from_bytes(h[1:3],'little')
            produced=0
            while produced<target:
                c=data[p]; p+=1
                if c<128:
                    count=c or 128; p+=count; produced+=count
                else: p+=1; produced+=(-struct.unpack('b',bytes([c]))[0])>>3

SIZES={0:2,2:1,3:1,4:1,5:1,6:1,7:1,8:1,9:2,11:2,13:1,14:4,18:1,19:1,20:1,21:1,22:1,23:1,24:1,25:1,26:1,27:2,28:1,29:4,30:1,31:1,32:1,33:1,34:1,35:1,36:1,37:1,38:1,39:1,40:2,41:2,42:4,43:2,46:2,47:2,48:4,49:1,50:2}

def inspect(data):
    out={'sha256':sha(data),'size':len(data),'names':{},'train_assignments':[], 'errors':[], 'action_counts':{},'base_cost_actions':[]}
    try:
        for offset,a in actions(data):
            if not a: continue
            act=a[0]; out['action_counts'][str(act)]=out['action_counts'].get(str(act),0)+1
            if act==8:
                out['grf_format_version']=a[1]; out['grfid']=a[2:6].hex().upper()
                out['internal_name'],p=zstr(a,6); out['description'],p=zstr(a,p)
            if act==4 and a[1]==0:
                lang=a[2]; count=a[3]; vid,p=ext(a,4) if not lang&128 else (int.from_bytes(a[4:6],'little'),6)
                for i in range(count):
                    name,p=zstr(a,p)
                    out['names'].setdefault(str(vid+i),[]).append({'language':lang,'name':name,'offset':offset})
            if act==0 and len(a)>5:
                feature,nprops,count=a[1:4]; vid,p=ext(a,4)
                if feature==8: out['base_cost_actions'].append({'offset':offset,'hex':a.hex()})
                if feature!=0: continue
                for _ in range(nprops):
                    prop=a[p]; p+=1
                    for i in range(count):
                        start=p
                        if prop==26:
                            _,p=ext(a,p)
                        elif prop in (44,45,51,52):
                            n=a[p]; p+=1+n*(2 if prop==51 else 1)
                        elif prop in SIZES: p+=SIZES[prop]
                        else: raise ValueError(f'Unsupported train property {prop:02x} at {offset}')
                        if p>len(a): raise ValueError('Truncated Action 0')
                        out['train_assignments'].append({'id':vid+i,'property':f'{prop:02X}','value':int.from_bytes(a[start:p],'little'),'hex':a[start:p].hex(),'offset':offset})
    except Exception as e: out['errors'].append(str(e))
    return out

def scenario(path):
    raw=path.read_bytes()
    if raw[:4]==b'OTTX': data=lzma.decompress(raw[8:])
    elif raw[:4]==b'OTTS':
        # Use an already-installed native zstd library; no dependency install.
        dll=ctypes.CDLL(r'C:\Program Files\Git\mingw64\bin\libzstd.dll')
        dll.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];dll.ZSTD_decompress.restype=ctypes.c_size_t
        dll.ZSTD_isError.argtypes=[ctypes.c_size_t];dll.ZSTD_isError.restype=ctypes.c_uint
        dest=ctypes.create_string_buffer(300_000_000);src=raw[8:]
        size=dll.ZSTD_decompress(dest,len(dest),src,len(src))
        if dll.ZSTD_isError(size):raise ValueError('Zstd decompression failed or exceeds 300 MB limit')
        data=dest.raw[:size]
    else:raise ValueError('Unsupported save compression')
    result={'path':str(path),'sha256':sha(raw),'mtime':path.stat().st_mtime,'header':raw[:8].hex()}
    for tag,kind,records in chunks(data):
        if tag in ('NGRF','SLXI','MAPS','PATS','OPTS','DATE','ECMY'):
            result[tag]={'kind':kind,'records':[bytes(r).hex() for r in records]}
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--root',action='append',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    inventory=[]; scenarios=[]
    for root in args.root:
        if not root.exists(): continue
        for path in sorted(root.rglob('*')):
            if not path.is_file(): continue
            if path.suffix.lower()=='.grf': inventory.append(dict(path=str(path),**inspect(path.read_bytes())))
            elif path.suffix.lower()=='.tar':
                with tarfile.open(path) as tar:
                    for member in tar:
                        if member.isfile() and member.name.lower().endswith('.grf'):
                            inventory.append(dict(path=str(path),member=member.name,archive_sha256=sha(path.read_bytes()),**inspect(tar.extractfile(member).read())))
            elif path.suffix.lower()=='.scn':
                try: scenarios.append(scenario(path))
                except Exception as e: scenarios.append({'path':str(path),'error':str(e)})
    target=args.output/'newgrf_inventory.json'
    if target.exists(): raise SystemExit('Refusing to overwrite existing research; choose a new output directory')
    target.write_text(json.dumps({'method':'Static Action 8/4/0 decoding; conditional branches NOT evaluated','roots':list(map(str,args.root)),'newgrfs':inventory,'scenarios':scenarios},indent=2),encoding='utf-8')
    print('GRF instances',len(inventory),'scenarios',len(scenarios))
    for g in inventory:
        if g['train_assignments']: print(g.get('grfid'),ascii(g.get('internal_name')),len({a['id'] for a in g['train_assignments']}),g['errors'])
    for s in scenarios:
        if 'NGRF' in s: print(s['path'],s['NGRF']['records'][0],len(s['NGRF']['records'])-1)

if __name__=='__main__': main()
