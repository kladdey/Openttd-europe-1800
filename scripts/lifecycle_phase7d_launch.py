"""Hash-checked isolated Phase 7D launch; no live-save substitution."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--verify-only',action='store_true');ap.add_argument('--editor',action='store_true');a=ap.parse_args()
 m=json.loads((ROOT/'docs/research/phase7d_candidate_delivery.json').read_text())
 for key in ['candidate','engine','grf','script']:assert sha(m[key])==m[key+'_sha256'],key
 for r in m['script_files']+m['asset_files']:assert sha(r['path'])==r['sha256'],r['path']
 assert not m['test_dates'] and m['gs_version']==4
 cmd=[m['engine'],'-X','-x','-c',m['configuration']]+(['-e'] if a.editor else [])+['-g',m['candidate'],'-r','1280x800']
 if a.verify_only:print('Phase 7D candidate and isolated assets verified')
 else:print('Isolated Phase 7D PID:',subprocess.Popen(cmd,cwd=m['profile'],creationflags=subprocess.CREATE_NO_WINDOW).pid)
