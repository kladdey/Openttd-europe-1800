"""Clone-only savegame editing for the Phase 4 compatibility tests.

Reads an OTTX (LZMA) save, re-frames its chunks and changes only:
  NGRF : insert / remove NewGRF records (balance GRFs after their targets),
  GSDT : attach the RVProbe measurement GameScript (drops the campaign GS state in the clone).
Every other chunk is re-encoded byte-identically (checked). Production saves are only read.
Standard library only (numpy stub for the repo decoders).
"""
import hashlib, lzma, struct, sys, types
from pathlib import Path
sys.modules.setdefault('numpy', types.ModuleType('numpy'))
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from scenario_geography import chunks          # noqa: E402
from transport_phase3 import encode, gamma     # noqa: E402
from prepare_vehicle_probe import string       # noqa: E402
from audit_vehicle_newgrfs import gamma as rgamma   # noqa: E402

NGRF_HEADER = bytes.fromhex('1a0866696c656e616d65060b6964656e742e6772666964120c6964656e742e6d643573756d060776657273696f6e1605706172616d020770616c657474651a086772665f6e616d6500')


def sstr(s):
    b = s.encode('utf8')
    return gamma(len(b)) + b


def ngrf_record(filename, grfid, md5hex, version, params, palette, name):
    return (sstr(filename) + bytes.fromhex(grfid)[::-1] + gamma(16) + bytes.fromhex(md5hex) + struct.pack('>I', version)
            + gamma(len(params)) + b''.join(struct.pack('>I', p) for p in params) + bytes([palette]) + sstr(name))


def ngrf_parse(rec):
    b = bytes(rec)
    fn, p = string(b, 0)
    grfid = b[p:p + 4][::-1].hex().upper()
    return fn, grfid


def load(path):
    raw = Path(path).read_bytes()
    assert raw[:4] == b'OTTX', 'only LZMA saves supported'
    return raw[:8], lzma.decompress(raw[8:])


def rewrite(src, dst, *, insert=(), remove=(), gs_name=None):
    """insert = [(after_grfid, record_bytes)], remove = {grfid}. Returns a change report."""
    head, data = load(src)
    out, report = [], []
    for tag, kind, records in chunks(data):
        before = encode(tag, kind, records)
        recs = [bytes(r) for r in records]
        if tag == 'NGRF':
            assert recs[0] == NGRF_HEADER, 'unexpected NGRF schema'
            new = [recs[0]]
            for r in recs[1:]:
                fn, g = ngrf_parse(r)
                if g in remove:
                    report.append(('NGRF', 'removed', g))
                    continue
                new.append(r)
                for after, rec in insert:
                    if g == after:
                        new.append(rec)
                        report.append(('NGRF', 'inserted after', after, ngrf_parse(rec)[1]))
            recs = new
        if tag == 'GSDT' and gs_name:
            name = gs_name.encode()
            recs = [recs[0], gamma(len(name)) + name + b'\0' + (1).to_bytes(4, 'big') + b'\0']
            report.append(('GSDT', 'attached', gs_name))
        after = encode(tag, kind, recs)
        if tag not in ('NGRF', 'GSDT'):
            assert after == before, f'chunk {tag} did not round-trip'
        out.append(after)
    blob = head + lzma.compress(b''.join(out) + b'\0\0\0\0')
    Path(dst).write_bytes(blob)
    return dict(src=str(src), src_sha256=hashlib.sha256(Path(src).read_bytes()).hexdigest(), dst=str(dst),
                dst_sha256=hashlib.sha256(blob).hexdigest(), changes=report)


def grf_list(path):
    head, data = load(path)
    for tag, kind, records in chunks(data):
        if tag == 'NGRF':
            return [ngrf_parse(r) for r in records[1:]]
