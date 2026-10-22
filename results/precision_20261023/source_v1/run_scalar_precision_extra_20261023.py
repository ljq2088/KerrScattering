"""Additional high-power and isolated integration checks; bounded immutable runs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
from run_scalar_precision_campaign_20261023 import ROOT, RUNTIME, DISTRO


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--group', choices=['power', 'integration', 'deep'], required=True)
    p.add_argument('--resolution', choices=['coarse', 'fine'], default='coarse')
    a = p.parse_args()
    cases = {
        'power': [(0, w, n) for w in ('5', '10') for n in (2, 3)],
        'integration': [(0, '0.1', 1), (2, '0.00001', 1), (0, '10', 1)],
        'deep': [(0, '0.000001', n) for n in (1, 2, 3)] + [(2, '0.000001', 1)],
    }[a.group]
    settings = (320, 48, 64, 80, 64) if a.resolution == 'coarse' else (384, 64, 80, 112, 88)
    if a.group == 'integration':
        settings = (384, 64, 80, 144, 112)
    linux = subprocess.check_output(['wsl.exe','-d',DISTRO,'-e','wslpath','-a',str(ROOT)],encoding='utf8').strip()
    sources = [ROOT/'src/kerr_scalar_precision.jl', ROOT/'scripts/run_scalar_precision_20261023.jl', Path(__file__), ROOT/'scripts/run_scalar_precision_campaign_20261023.py']
    for l, w, n in cases:
        name = f'{a.group}_l{l}_m0_w{w}_n{n}_{a.resolution}'
        folder = ROOT/'results/precision_20261023'/name
        if folder.exists():
            print('Preserve',name,flush=True)
            continue
        folder.mkdir(parents=True)
        before = {str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in sources}
        cmd = ['wsl.exe','-d',DISTRO,'-e','env','OPENBLAS_NUM_THREADS=1','JULIA_NUM_THREADS=1','timeout','--kill-after=10','300',RUNTIME,'--startup-file=no','--threads=1',linux+'/scripts/run_scalar_precision_20261023.jl',linux+'/results/precision_20261023/'+name+'/solution','0.5',w,str(l),'0',str(n),*map(str,settings)]
        print('RUN',name,flush=True);started=time.time()
        with (folder/'stdout.txt').open('w',encoding='utf8') as out,(folder/'stderr.txt').open('w',encoding='utf8') as err:
            r=subprocess.run(cmd,stdout=out,stderr=err,timeout=330)
        after={str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in sources}
        status='completed' if r.returncode==0 else 'failed'
        if before!=after:status='inputs-changed'
        outputs={str(q.relative_to(folder)):hashlib.sha256(q.read_bytes()).hexdigest() for q in folder.rglob('*') if q.is_file()}
        record=dict(status=status,returncode=r.returncode,command=cmd,source_hashes_before=before,source_hashes_after=after,outputs=outputs,seconds=time.time()-started,precision=settings,assertion_tested=f's=0,a=0.5,l={l},m=0,omega={w},n={n}',timeout_seconds=300,memory_guard_bytes=1500000000)
        (folder/'manifest.json').write_text(json.dumps(record,indent=2),encoding='utf8')
        print(status,record['seconds'],flush=True)
        print((folder/'stdout.txt').read_text(encoding='utf8')[-950:],flush=True)
        if status!='completed':
            print((folder/'stderr.txt').read_text(encoding='utf8')[-2000:],flush=True)
            raise SystemExit(1)


if __name__=='__main__':
    main()
