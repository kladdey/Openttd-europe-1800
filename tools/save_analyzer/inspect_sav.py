#!/usr/bin/env python3
"""Read-only JGRPP save container inspection. Not a full game-state decoder."""
import argparse
import json
import lzma
from pathlib import Path

def inspect(path: Path):
    with path.open("rb") as stream:
        header = stream.read(8)
        if len(header) != 8 or header[:4] != b"OTTX":
            raise ValueError("Expected OTTX JGRPP save header")
        raw = lzma.decompress(stream.read())
    if raw[:4] != b"SLXI":
        raise ValueError("Expected SLXI extension metadata as first chunk")
    pos = raw.find(b"jgrpp-", 0, 4096)
    version = None
    if pos >= 0:
        end = raw.find(b"\x00", pos, pos + 100)
        if end >= 0:
            version = raw[pos:end].decode("ascii", "replace")
    return {"file": path.name, "container": "OTTX", "header_hex": header.hex(),
            "decompressed_bytes": len(raw), "first_chunk": "SLXI",
            "version_label": version, "record_data_decoded": False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("saves", nargs="+", type=Path)
    args = parser.parse_args()
    print(json.dumps([inspect(p) for p in args.saves], indent=2))

if __name__ == "__main__":
    main()
