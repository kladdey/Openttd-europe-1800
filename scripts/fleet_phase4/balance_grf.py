"""Experimental Europe-1830 balance GRF builder (test directories only).

One GRF targets exactly one vehicle set (OpenTTD allows one engine-allocation override
target per source GRFID). It contains only pseudo-sprites:

  Action 8   GRF version 8, own GRFID, name, description
  Action 0   feature 08 (global) prop 0x11: engine-allocation override, own GRFID -> target
  Action 0   feature 08 prop 0x08: price-base multipliers (local to the target, via the
             override; see FinalisePriceBaseMultipliers in src/newgrf.cpp)
  Action 0   feature 00 (trains), per target-local engine ID:
               prop 0x0D running-cost factor (byte), and/or
               prop 0x0E running-cost base class (dword magic 0x4B34 + 6 * price index)

No vehicles are created, no sprites, Action 2/3, callbacks, cargo or rail-type tables.
Standard library only.
"""
import hashlib, json, struct
from pathlib import Path

PRICE = {'steam': 42, 'diesel': 43, 'electric': 44}


def pseudo(data):
    return struct.pack('<HB', len(data), 0xFF) + data


def ext_byte(v):
    return bytes([v]) if v < 0xFF else b'\xff' + struct.pack('<H', v)


def build(spec):
    """spec = {grfid:'52560010', target:'44440302', name:str,
               prices:{42:+3,...}  (exponent, -8..+8),
               engines:[{id:local, factor:int|None, cls:'steam'|'diesel'|'electric'|int|None}]}"""
    own = bytes.fromhex(spec['grfid'])
    tgt = bytes.fromhex(spec['target'])
    sprites = [b'\x08\x08' + own + spec['name'].encode() + b'\x00' + b'Europe 1830 Phase 4 experimental balance (test only)\x00',
               b'\x00\x08\x01\x01\x00\x11' + own + tgt]
    for p, e in sorted(spec.get('prices', {}).items()):
        assert -8 <= e <= 8
        sprites.append(bytes([0x00, 0x08, 0x01, 0x01, int(p), 0x08, e + 8]))
    for e in spec.get('engines', []):
        props = b''
        n = 0
        if e.get('factor') is not None:
            assert 0 <= e['factor'] <= 255
            props += b'\x0d' + bytes([e['factor']])
            n += 1
        if e.get('cls') is not None:
            idx = PRICE.get(e['cls'], e['cls'])
            props += b'\x0e' + struct.pack('<I', 0x4B34 + 6 * idx)
            n += 1
        if n:
            sprites.append(b'\x00\x00' + bytes([n, 1]) + ext_byte(e['id']) + props)
    body = b''.join(pseudo(s) for s in sprites)
    return pseudo(struct.pack('<I', len(sprites))) + body + b'\x00\x00'


def write(spec, folder):
    data = build(spec)
    path = Path(folder) / f"rv_{spec['grfid'].lower()}_{spec['tag']}.grf"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    meta = dict(spec, file=path.name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), md5=hashlib.md5(data).hexdigest().upper())
    path.with_suffix('.json').write_text(json.dumps(meta, indent=2))
    return path, meta
