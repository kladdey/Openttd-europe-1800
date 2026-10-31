"""Launch the pinned Phase 7C profile; normal OpenTTD settings are untouched."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(m):
 for key in ['candidate','engine','grf','script']:assert sha(m[key])==m[key+'_sha256'],key+' changed since validation'
 for name,field in [('legacy_policy.nut','policy_sha256'),('expansion_policy.nut','expansion_policy_sha256'),('schedule.nut','schedule_sha256'),('info.nut','info_sha256')]:assert sha(Path(m['script']).with_name(name))==m[field],name
 for r in m['required_asset_files']:assert sha(r['path'])==r['sha256'],r['path']
 assert m['test_dates'] is False and m['baseline_towns']==617 and m['baseline_industries']==542
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--editor',action='store_true');ap.add_argument('--verify-only',action='store_true');a=ap.parse_args()
 m=json.loads((ROOT/'docs/research/phase7c_candidate_delivery.json').read_text());verify(m)
 cmd=[m['engine'],'-X','-x','-c',m['configuration']]+(['-e'] if a.editor else [])+['-g',m['candidate'],'-r','1280x800']
 if a.verify_only:print('Verified isolated Phase 7C candidate and all pinned assets')
 else:
  p=subprocess.Popen(cmd,cwd=m['profile'],creationflags=subprocess.CREATE_NO_WINDOW);print('Phase 7C isolated process:',p.pid)
