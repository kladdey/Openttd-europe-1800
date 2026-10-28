"""Run only the disposable runtime with explicit no-save options."""
from pathlib import Path
import subprocess, argparse
ap=argparse.ArgumentParser();ap.add_argument('--exe',type=Path,required=True);ap.add_argument('--ticks',type=int,default=20000);ap.add_argument('--scenario',type=Path);ap.add_argument('--log',default='probe-runtime.log');ap.add_argument('--year',type=int);args=ap.parse_args()
run=Path('.vehicle-audit-runtime').resolve()
config='probe.cfg'
if args.year:
    import re
    config=f'probe-{args.year}.cfg'
    contents=(run/'probe.cfg').read_text(encoding='utf8')
    contents=re.sub(r'(?m)^starting_year = .*$',f'starting_year = {args.year}',contents)
    (run/config).write_text(contents,encoding='utf8')
with (run/args.log).open('wb') as log:
    command=[str(args.exe.resolve()),'-c',config,'-x','-v',f'null:ticks={args.ticks}','-s','null','-m','null','-d','script=4,grf=5,misc=1','-G','1830','-g']
    if args.scenario: command.append(str(args.scenario.resolve()))
    proc=subprocess.Popen(command,cwd=run,stdout=log,stderr=log)
    try: print('Exit',proc.wait(timeout=120))
    except subprocess.TimeoutExpired:
        proc.kill();proc.wait();print('Probe time limit reached; inspect log for AUDIT_DONE')
print(run/'probe-runtime.log')
