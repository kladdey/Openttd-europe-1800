"""Build the test-only NARS running-cost compatibility GRF (test 3).

Writes a minimal GRF (container version 1, pseudo-sprites only) with:
  Action 8   GRF version 8, GRFID 'RV\x00\x01' (52 56 00 01), name/description
  Action 0   feature 08 (global), reserve-stage prop 0x11: engine-allocation override
             source = this GRFID, target = NARS 2.52 (44440302)
  Action 0   feature 08, prop 0x08: base-price multiplier for price 42
             (RunningTrainSteam) = 0x0B, i.e. exponent +3

It defines no vehicles, cargo or rail-type translation tables, sprites or callbacks.
Written only into a test directory given on the command line. Never install it into a
production content folder. Standard library only.
"""
import argparse, hashlib, struct
from pathlib import Path

GRFID = bytes.fromhex('52560001')          # own ID, chosen to avoid any installed GRF
NARS = bytes.fromhex('44440302')           # GRFID byte order as stored in GRF data
PRICE_STEAM_RUNNING = 42
EXPONENT_PLUS_3 = 8 + 3                    # prop 0x08 value: factor - 8 = exponent


def pseudo(data: bytes) -> bytes:
    return struct.pack('<HB', len(data), 0xFF) + data


def build() -> bytes:
    sprites = [
        # Action 8: version 08, GRFID, name, description
        b'\x08\x08' + GRFID + b'RV NARS running exponent compat (test only)\x00'
        + b'Runtime validation: price base 42 to +3 via override of 44440302\x00',
        # Action 0 feature 08: 1 property, 1 ID, first ID 0, prop 0x11, source+target GRFIDs
        b'\x00\x08\x01\x01\x00\x11' + GRFID + NARS,
        # Action 0 feature 08: 1 property, 1 ID, first ID 42 (price index), prop 0x08, value
        bytes([0x00, 0x08, 0x01, 0x01, PRICE_STEAM_RUNNING, 0x08, EXPONENT_PLUS_3]),
    ]
    body = b''.join(pseudo(s) for s in sprites)
    header = pseudo(struct.pack('<I', len(sprites)))     # sprite-count sprite
    return header + body + b'\x00\x00'


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('out', type=Path)
    a = ap.parse_args()
    data = build()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_bytes(data)
    print(a.out, len(data), 'bytes md5', hashlib.md5(data).hexdigest().upper())
