"""Reproducibly build the Phase 4 experimental balance GRFs for every variant.

  python -B build_balance_grfs.py [--out DIR]

Writes, per variant, the GRF files plus a manifest (SHA-256, MD5, load position, exact property
payload). Output defaults to docs/research/fleet_phase4/grf_build/. Building twice must give
byte-identical files (checked). Nothing is installed anywhere.
"""
import argparse, hashlib, json
from pathlib import Path
import balance_grf as bg
import phase4 as P4
import variants as V

LOAD_AFTER = {P4.NARS: '44440302 (NARS 2.52)', P4.ADDON: '4E4D0518 (NARS Add-On 2cc)', P4.UKRS2: '44441000 (UKRS2 1.05)'}


def build(out):
    out = Path(out)
    manifest = {}
    for v in V.VARIANTS:
        files = []
        for s in V.spec(v):
            spec = dict(grfid=P4.OWN[s['target']], target=s['target'], tag=s['tag'], name=f"RV P4 {s['tag']}",
                        prices=s.get('prices', {}), engines=s.get('engines', []))
            data = bg.build(spec)
            again = bg.build(spec)
            assert data == again, 'non-deterministic build'
            name = f"europe1830_balance_{v}_{s['target'].lower()}.grf"
            (out / v).mkdir(parents=True, exist_ok=True)
            (out / v / name).write_bytes(data)
            files.append(dict(file=f'{v}/{name}', grfid=spec['grfid'], overrides=s['target'], load_directly_after=LOAD_AFTER[s['target']],
                              bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), md5=hashlib.md5(data).hexdigest().upper(),
                              prices={str(k): f'{e:+d}' for k, e in spec['prices'].items()},
                              engines=[dict(local_id=e['id'], factor=e.get('factor'), running_cost_class=e.get('cls')) for e in spec['engines']]))
        manifest[v] = files
    (out / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2))
    lines = [f"{f['sha256']}  {f['file']}" for fs in manifest.values() for f in fs]
    (out / 'SHA256SUMS').write_text('\n'.join(lines) + '\n')
    return manifest


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(P4.OUT / 'grf_build'))
    a = ap.parse_args()
    m = build(a.out)
    for v, fs in m.items():
        for f in fs:
            print(v, f['file'], f['bytes'], 'bytes', f['sha256'][:16])
