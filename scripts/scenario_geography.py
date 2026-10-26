"""Read-only, deliberately narrow JGRPP 0.73.4 OTTX terrain inspection.

Never writes a scenario. Layout references are pinned in geography_v6/README.md.
"""
import lzma
import struct
from pathlib import Path

import numpy as np


def gamma(data, offset):
    first = data[offset]
    extra = 0
    while first & (0x80 >> extra):
        extra += 1
        if extra > 4:
            raise ValueError('Unsupported gamma length')
    end = offset + 1 + extra
    if end > len(data):
        raise ValueError('Truncated gamma length')
    value = first & (0x7f >> extra)
    for byte in data[offset+1:end]:
        value = (value << 8) | byte
    return value, end


def chunks(data):
    """Yield framed chunks; never search arbitrary payload bytes for tags."""
    pos = 0
    while pos + 4 <= len(data):
        name = bytes(data[pos:pos+4])
        pos += 4
        if name == b'\0\0\0\0':
            if pos != len(data):
                raise ValueError('Trailing save data')
            return
        if any(c < 32 or c > 126 for c in name) or pos >= len(data):
            raise ValueError('Invalid chunk tag')
        mode = data[pos]
        pos += 1
        kind = mode & 15
        # Extended headers and other JGR versions are intentionally unsupported.
        if kind == 0:
            if pos + 3 > len(data):
                raise ValueError('Truncated RIFF header')
            size = ((mode >> 4) << 24) | int.from_bytes(data[pos:pos+3], 'big')
            pos += 3
            end = pos + size
            if end > len(data):
                raise ValueError('Truncated RIFF payload')
            yield name.decode('ascii'), kind, [memoryview(data)[pos:end]]
            pos = end
        elif kind in (1, 2, 3, 4):
            records = []
            while True:
                if pos >= len(data):
                    raise ValueError('Unterminated array')
                length, pos = gamma(data, pos)
                if length == 0:
                    break
                end = pos + length - 1
                if end > len(data):
                    raise ValueError('Truncated array payload')
                records.append(memoryview(data)[pos:end])
                pos = end
            yield name.decode('ascii'), kind, records
        else:
            raise ValueError(f'Unsupported chunk mode {kind}')
    raise ValueError('Missing save terminator')


def read_terrain(path):
    encoded = Path(path).read_bytes()
    if encoded[:8] != b'OTTX\x81\x24\0\0':
        raise ValueError('Only the supplied JGRPP 0.73.4 OTTX header is supported')
    dec = lzma.LZMADecompressor()
    data = dec.decompress(encoded[8:], max_length=300_000_000)
    if not dec.eof or dec.unused_data:
        raise ValueError('Oversized, truncated or concatenated scenario')
    saved = {}
    all_names = set()
    for name, kind, records in chunks(data):
        if name in all_names:
            raise ValueError('Duplicate chunk tag')
        all_names.add(name)
        if name in ('SLXI', 'MAPS', 'MAPT', 'MAPH'):
            saved[name] = (kind, records)
    if b'jgrpp-0.73.4' not in bytes(saved['SLXI'][1][0]):
        raise ValueError('Unexpected JGRPP version')
    kind, records = saved['MAPS']
    if kind != 3 or len(records) != 2 or bytes(records[0]) != b'\x06\x05dim_x\x06\x05dim_y\0':
        raise ValueError('Unexpected map dimension table schema')
    width, height = struct.unpack('>II', records[1])
    if (width, height) != (4096, 4096):
        raise ValueError('This audit supports the supplied 4096-square scenario only')
    arrays = []
    for tag in ('MAPT', 'MAPH'):
        kind, records = saved[tag]
        if kind != 0 or len(records) != 1 or len(records[0]) != width * height:
            raise ValueError('Unexpected terrain array length or mode')
        arrays.append(np.frombuffer(records[0], dtype=np.uint8).reshape(height, width))
    return arrays[0] >> 4, arrays[1]


def import_target(x, y, rotation='counter_clockwise', size=4096):
    """Emulate target-version float32 parsing, arithmetic and uint truncation."""
    x, y = np.float32(x), np.float32(y)
    if not (0 < x < 1 and 0 < y < 1):
        raise ValueError('Importer requires strict interior coordinates')
    maximum = np.float32(size - 1)
    if rotation == 'clockwise':
        return int(x * maximum), int(y * maximum)
    if rotation == 'counter_clockwise':
        return int(np.float32(np.float32(1) - y) * maximum), int(x * maximum)
    raise ValueError('Unknown rotation')


def source_pixel(x, y, rotation='counter_clockwise', size=4096):
    tx, ty = import_target(x, y, rotation, size)
    return (ty, tx) if rotation == 'clockwise' else (size-1-tx, ty)
