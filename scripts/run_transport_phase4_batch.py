"""Run a bounded list in independent interpreters; no shared mutable runner state."""
import argparse,concurrent.futures,ctypes,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def alive(pid):
    k=ctypes.windll.kernel32;h=k.OpenProcess(0x1000,False,pid)
    if not h:return False
    code=ctypes.c_ulong();k.GetExitCodeProcess(h,ctypes.byref(code));k.CloseHandle(h);return code.value==259
def main():
    p=argparse.ArgumentParser();p.add_argument('cases',nargs='+');p.add_argument('--wait-pids',nargs='*',type=int,default=[]);p.add_argument('--workers',type=int,default=3);p.add_argument('--prefix',default='final-');p.add_argument('--years',type=int);a=p.parse_args()
    while any(alive(pid) for pid in a.wait_pids):time.sleep(2)
    def execute(case):
        cmd=[sys.executable,str(ROOT/'scripts/transport_phase4.py'),case,'--tag',a.prefix+case]
        if a.years:cmd+=['--years',str(a.years)]
        r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        print(case,r.returncode,r.stdout.strip(),r.stderr[-1000:],flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:list(pool.map(execute,a.cases))
if __name__=='__main__':main()
