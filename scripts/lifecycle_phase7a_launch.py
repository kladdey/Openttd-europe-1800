"""Launch the separately validated local profile, preserving normal user data."""
import argparse,json,subprocess
from lifecycle_phase7a_runtime import BASE,sha,guards
from pathlib import Path

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--editor',action='store_true');a=p.parse_args();guards()
    manifest=json.loads((BASE/'candidate-delivery.json').read_text())
    for key in ['candidate','engine','grf','script']:
        assert sha(Path(manifest[key]))==manifest[key+'_sha256'],key+' changed since validation'
    assert sha(Path(manifest['script']).parent/'schedule.nut')==manifest['schedule_sha256'],'Schedule changed since validation'
    command=[manifest['engine'],'-X','-x','-c',manifest['configuration']]
    if a.editor:command.append('-e')
    command+=['-g',manifest['candidate'],'-r','1280x800']
    print('Launching isolated experimental profile:',manifest['profile'])
    process=subprocess.Popen(command,cwd=manifest['profile'])
    (BASE/'last-launch.json').write_text(json.dumps(dict(pid=process.pid,profile=manifest['profile'],command=command,editor=a.editor),indent=2))
    print('Process ID:',process.pid)
