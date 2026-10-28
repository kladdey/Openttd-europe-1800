"""Inspect and stage an industry-free scenario; never patch its saved GRF list.

Replacement and resaving must be performed by JGRPP's scenario editor. This
utility fingerprints the supplied file and compares engine-generated outputs.
"""
import argparse
import collections
import ctypes
import hashlib
import json
import lzma
from pathlib import Path
import shutil
import struct
import numpy as np
from scenario_geography import chunks
from audit_vehicle_newgrfs import scenario
from prepare_vehicle_probe import ngrf

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'newgrfs/axis-historical-europe/.work/europe-migration'


def digest(data):return hashlib.sha256(data).hexdigest()


def decode(raw):
    if raw[:4]==b'OTTX':return lzma.decompress(raw[8:])
    if raw[:4]==b'OTTS':
        dll=ctypes.CDLL(r'C:\Program Files\Git\mingw64\bin\libzstd.dll')
        dll.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t]
        dll.ZSTD_decompress.restype=ctypes.c_size_t
        dll.ZSTD_isError.argtypes=[ctypes.c_size_t];dll.ZSTD_isError.restype=ctypes.c_uint
        dest=ctypes.create_string_buffer(300_000_000);source=raw[8:]
        size=dll.ZSTD_decompress(dest,len(dest),source,len(source))
        if dll.ZSTD_isError(size):raise ValueError('Invalid/oversized Zstd scenario')
        return dest.raw[:size]
    raise ValueError('Unsupported scenario compression')


def inspect(path):
    raw=path.read_bytes();data=decode(raw)
    parts={tag:(kind,[bytes(r) for r in records]) for tag,kind,records in chunks(data)}
    refs=ngrf(scenario(path))
    result=dict(path=str(path.resolve()),sha256=digest(raw),bytes=len(raw),header=raw[:8].hex(),
                newgrfs=refs,chunks={tag:dict(kind=kind,records=len(records),
                  payload_bytes=sum(map(len,records)),sha256=digest(b''.join(len(r).to_bytes(8,'big')+r for r in records)))
                  for tag,(kind,records) in parts.items()})
    width,height=struct.unpack('>II',parts['MAPS'][1][1]);count=width*height
    if 'MAPT' in parts:
        maps={tag:records[0] for tag,(kind,records) in parts.items() if tag.startswith(('MAP','M3')) and kind==0}
    else:
        # JGRPP Save_WMAP writes Tile[8] then TileExtended[4], little-endian.
        # Normalize to the ordinary per-field, big-endian MAP* save representation.
        whole=parts['WMAP'][1][0];assert len(whole)==count*12
        raw_map=np.frombuffer(whole,dtype=np.uint8)
        primary=raw_map[:count*8].reshape(count,8);extra=raw_map[count*8:].reshape(count,4)
        maps={tag:primary[:,offset].tobytes() for tag,offset in [('MAPT',0),('MAPH',1),('MAPO',4),('M3LO',5),('M3HI',6),('MAP5',7)]}
        maps.update(MAP2=primary[:,[3,2]].tobytes(),MAPE=extra[:,0].tobytes(),MAP7=extra[:,1].tobytes(),MAP8=extra[:,[3,2]].tobytes())
    result['map_array_sha256']={tag:digest(value) for tag,value in maps.items()}
    map_type=maps['MAPT']
    result['tile_type_counts']=dict(collections.Counter(v>>4 for v in map_type))
    result['industry_tiles']=result['tile_type_counts'].get(8,0)
    result['industry_records']=len(parts['INDY'][1])-1
    result['town_records']=len(parts['CITY'][1])-1
    result['map_dimensions']=list(struct.unpack('>II',parts['MAPS'][1][1]))
    result['date_records_hex']=[r.hex() for r in parts['DATE'][1]]
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',type=Path);ap.add_argument('--compare',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();before=inspect(args.source)
    result={'source':before}
    if args.compare:
        after=inspect(args.compare);result['candidate']=after
        result['changed_chunks']=[tag for tag in set(before['chunks'])|set(after['chunks']) if before['chunks'].get(tag)!=after['chunks'].get(tag)]
        result['source_only_grfs']=[r for r in before['newgrfs'] if r not in after['newgrfs']]
        result['candidate_only_grfs']=[r for r in after['newgrfs'] if r not in before['newgrfs']]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists():raise SystemExit('Refusing to overwrite inspection evidence')
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in before.items() if k not in ['chunks','date_records_hex']},indent=2))
    if args.compare:print('Changed chunks:',result['changed_chunks'])


if __name__=='__main__':main()
