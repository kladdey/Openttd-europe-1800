"""Europe 1830 Balance v1: add to / remove from an OpenTTD (JGRPP) savegame's NewGRF list.

Standalone (Python 3 standard library only). Never edits in place: always writes a new file.

  python apply_balance.py apply    <in.sav> <out.sav>
  python apply_balance.py rollback <in.sav> <out.sav>
  python apply_balance.py check    <file.sav>

apply    : inserts the two balance GRF records directly after NARS 2.52 (44440302) and
           the NARS Add-On (4E4D0518). Every other chunk is re-encoded byte-identically
           (verified). The GameScript and its saved state are untouched.
rollback : removes the two records again; the result is content-identical to a save that
           never had them (verified against the decompressed chunk stream).
check    : lists the NewGRF list and whether the balance GRFs are present.

Only LZMA-compressed saves (header 'OTTX') are supported: set "savegame_format = lzma"
in [misc] of openttd.cfg before saving the game that you want to convert.
"""
import hashlib, json, lzma, struct, sys
from pathlib import Path

BALANCE = json.loads((Path(__file__).with_name('balance_grfs.json')).read_text())   # filename, grfid, md5, name, after
NGRF_HEADER = bytes.fromhex('1a0866696c656e616d65060b6964656e742e6772666964120c6964656e742e6d643573756d060776657273696f6e1605706172616d020770616c657474651a086772665f6e616d6500')


def gamma_read(data, pos):
    first = data[pos]; extra = 0
    while first & (0x80 >> extra):
        extra += 1
    value = first & (0x7f >> extra)
    for b in data[pos + 1:pos + 1 + extra]:
        value = (value << 8) | b
    return value, pos + 1 + extra


def gamma(n):
    if n < 128:
        return bytes([n])
    for extra in range(1, 5):
        if n < (1 << (7 + 7 * extra)):
            return bytes([(256 - (1 << (8 - extra))) | (n >> (8 * extra))]) + n.to_bytes(extra + 1, 'big')[1:]
    raise ValueError(n)


def chunks(data):
    pos = 0
    while True:
        tag = data[pos:pos + 4]; pos += 4
        if tag == b'\0\0\0\0':
            return
        mode = data[pos]; pos += 1; kind = mode & 15
        if kind == 0:
            size = ((mode >> 4) << 24) | int.from_bytes(data[pos:pos + 3], 'big'); pos += 3
            yield tag.decode(), kind, [data[pos:pos + size]]; pos += size
        elif kind in (1, 2, 3, 4):
            recs = []
            while True:
                n, pos = gamma_read(data, pos)
                if n == 0:
                    break
                recs.append(data[pos:pos + n - 1]); pos += n - 1
            yield tag.decode(), kind, recs
        else:
            raise ValueError('unsupported chunk mode %d in %s' % (kind, tag))


def encode(tag, kind, recs):
    out = tag.encode()
    if kind == 0:
        b = bytes(recs[0])
        return out + bytes([((len(b) >> 24) << 4) | kind]) + (len(b) & 0xffffff).to_bytes(3, 'big') + b
    return out + bytes([kind]) + b''.join(gamma(len(r) + 1) + bytes(r) for r in recs) + b'\0'


def sstr(s):
    b = s.encode(); return gamma(len(b)) + b


def record(g):
    # Same layout and palette byte (7) as records written by JGRPP itself for these GRFs.
    return (sstr(g['filename']) + bytes.fromhex(g['grfid'])[::-1] + gamma(16) + bytes.fromhex(g['md5']) + struct.pack('>I', 0)
            + gamma(0) + bytes([7]) + sstr(g['name']))


def grfid_of(rec):
    n, p = gamma_read(rec, 0); p += n
    return rec[p:p + 4][::-1].hex().upper()


def load(path):
    raw = Path(path).read_bytes()
    if raw[:4] != b'OTTX':
        sys.exit('Not an LZMA save (header %r). Set savegame_format = lzma and save again.' % raw[:4])
    return raw[:8], lzma.decompress(raw[8:])


def transform(src, dst, mode):
    if Path(src).resolve() == Path(dst).resolve():
        sys.exit('Refusing to overwrite the input file.')
    head, data = load(src)
    ours = {g['grfid'] for g in BALANCE}
    out, report = [], []
    for tag, kind, recs in chunks(data):
        before = encode(tag, kind, recs)
        if tag == 'NGRF':
            assert bytes(recs[0]) == NGRF_HEADER, 'unexpected NGRF layout (different OpenTTD build?)'
            present = {grfid_of(bytes(r)) for r in recs[1:]}
            if mode == 'apply':
                if ours & present:
                    sys.exit('Balance GRFs already present.')
                for g in BALANCE:
                    if g['after'] not in present:
                        sys.exit('Target GRF %s not in this save.' % g['after'])
            new = [recs[0]]
            for r in recs[1:]:
                gid = grfid_of(bytes(r))
                if mode == 'rollback' and gid in ours:
                    report.append('removed ' + gid); continue
                new.append(r)
                if mode == 'apply':
                    for g in BALANCE:
                        if g['after'] == gid:
                            new.append(record(g)); report.append('inserted %s after %s' % (g['grfid'], gid))
            recs = new
        elif encode(tag, kind, recs) != before:
            sys.exit('Chunk %s does not round-trip; aborting.' % tag)
        out.append(encode(tag, kind, recs))
    body = b''.join(out) + b'\0\0\0\0'
    Path(dst).write_bytes(head + lzma.compress(body))
    print('\n'.join(report))
    print('written', dst, hashlib.sha256(Path(dst).read_bytes()).hexdigest())


def check(path):
    head, data = load(path)
    for tag, kind, recs in chunks(data):
        if tag == 'NGRF':
            ids = [grfid_of(bytes(r)) for r in recs[1:]]
            print('NewGRFs:', ' '.join(ids))
            print('Balance v1 present:', all(g['grfid'] in ids for g in BALANCE))


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'check':
        check(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] in ('apply', 'rollback'):
        transform(sys.argv[2], sys.argv[3], sys.argv[1])
    else:
        sys.exit(__doc__)
