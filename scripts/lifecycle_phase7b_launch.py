"""Launch the verified separate Phase 7B profile; never writes normal cfg."""
import argparse,json,subprocess
from pathlib import Path
from lifecycle_phase7b_runtime import ROOT,BASE,guards,sha

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--editor',action='store_true');a=ap.parse_args();guards()
    m=json.loads((ROOT/'docs/research/phase7b_candidate_delivery.json').read_text())
    for key in ['candidate','engine','grf','script']:assert sha(Path(m[key]))==m[key+'_sha256'],key+' changed since validation'
    for name,field in [('legacy_policy.nut','policy_sha256'),('schedule.nut','schedule_sha256'),('info.nut','info_sha256')]:assert sha(Path(m['script']).with_name(name))==m[field]
    for r in m['required_asset_files']:assert sha(Path(r['path']))==r['sha256']
    command=[m['engine'],'-X','-x','-c',m['configuration']]
    if a.editor:command+=['-e']
    command+=['-g',m['candidate'],'-r','1280x800']
    p=subprocess.Popen(command,cwd=m['profile'],creationflags=subprocess.CREATE_NO_WINDOW)
    (BASE/'last-launch.json').write_text(json.dumps(dict(pid=p.pid,command=command,editor=a.editor),indent=2));print('Isolated Phase 7B process:',p.pid)
