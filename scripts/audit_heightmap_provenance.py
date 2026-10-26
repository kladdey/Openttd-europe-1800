#!/usr/bin/env python3
"""Fingerprint PNGs and compare a heightmap with an archive, without extracting it."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import struct
import tarfile
import zlib

import numpy as np
from PIL import Image

SIGNATURE = b'\x89PNG\r\n\x1a\n'
MAX_MEMBER = 64 * 1024 * 1024


def png_chunks(data):
    """Validate PNG framing and CRCs; report chunk types, not compressed data."""
    if not data.startswith(SIGNATURE):
        raise ValueError('Not a PNG')
    chunks, offset = [], 8
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError('Truncated PNG chunk')
        size = struct.unpack_from('>I', data, offset)[0]
        end = offset + 12 + size
        if end > len(data):
            raise ValueError('Truncated PNG payload')
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + size]
        crc = struct.unpack_from('>I', data, offset + 8 + size)[0]
        if zlib.crc32(kind + payload) & 0xffffffff != crc:
            raise ValueError('PNG CRC mismatch')
        chunks.append(kind.decode('ascii'))
        offset = end
        if kind == b'IEND':
            if offset != len(data):
                raise ValueError('Trailing bytes after PNG IEND')
            return chunks
    raise ValueError('Missing PNG IEND')


def fingerprint(data):
    chunks = png_chunks(data)
    with Image.open(io.BytesIO(data)) as image:
        mode = image.mode
        rgba = np.array(image.convert('RGBA'), dtype=np.uint8)
    return {
        'bytes': len(data),
        'sha256': hashlib.sha256(data).hexdigest(),
        'md5': hashlib.md5(data).hexdigest(),
        'width': int(rgba.shape[1]), 'height': int(rgba.shape[0]),
        'original_mode': mode,
        'chunk_counts': {kind: chunks.count(kind) for kind in sorted(set(chunks))},
        'rgba_sha256': hashlib.sha256(rgba.tobytes()).hexdigest(),
        'red_sha256': hashlib.sha256(rgba[:, :, 0].tobytes()).hexdigest(),
        'non_grey_pixels': int(np.count_nonzero(np.any(rgba[:, :, :3] != rgba[:, :, :1], axis=2))),
        'opaque': bool(np.all(rgba[:, :, 3] == 255)),
    }, rgba


def compare_pngs(source, candidate):
    left, a = fingerprint(source)
    right, b = fingerprint(candidate)
    same_shape = a.shape == b.shape
    return {
        'source': left, 'candidate': right,
        'encoded_bytes_equal': source == candidate,
        'dimensions_equal': same_shape,
        'rgba_pixels_equal': bool(same_shape and np.array_equal(a, b)),
        'different_rgba_pixels': int(np.count_nonzero(np.any(a != b, axis=2))) if same_shape else None,
        'different_red_pixels': int(np.count_nonzero(a[:, :, 0] != b[:, :, 0])) if same_shape else None,
    }


def audit_archive(source_path, archive_path):
    source = Path(source_path).read_bytes()
    archive_bytes = Path(archive_path).read_bytes()
    results = []
    # Never extract members to disk: paths, symlinks and traversal cannot write files.
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode='r:*') as archive:
        for member in archive:
            if member.isfile() and member.name.lower().endswith('.png'):
                if member.size > MAX_MEMBER:
                    raise ValueError('PNG archive member exceeds 64 MiB limit')
                result = compare_pngs(source, archive.extractfile(member).read())
                result['member'] = member.name
                results.append(result)
    if not results:
        raise ValueError('Archive contains no regular PNG files')
    return {'schema_version': 1, 'archive_sha256': hashlib.sha256(archive_bytes).hexdigest(),
            'archive_bytes': len(archive_bytes), 'comparisons': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = audit_archive(args.source, args.archive)
    encoded = json.dumps(report, indent=2) + '\n'
    if args.output:
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(encoded)
    else:
        print(encoded, end='')
    if not any(item['rgba_pixels_equal'] for item in report['comparisons']):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
