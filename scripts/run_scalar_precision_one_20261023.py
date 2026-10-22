"""One additional bounded case, preserving all previous successful/failed runs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
from run_scalar_precision_campaign_20261023 import ROOT, RUNTIME, DISTRO

p=argparse.ArgumentParser()
p.add_argument('name');p.add_argument('omega');p.add_argument('--ell',type=int,default=0)
p.add_argument('--n',type=int,default=1);p.add_argument('--spin',default='0.5')
p.add_argument('--quad',type=int,default=112);p.add_argument('--levin',type=int,default=88)
a=p.parse_args()
assert Path(a.name).name==a.name
folder=ROOT/'results/precision_20261023'/a.name
assert not folder.exists()
folder.mkdir(parents=True)
linux=subprocess.check_output(['wsl.exe','-d',DISTRO,'-e','wslpath','-a',str(ROOT)],encoding='utf8').strip()
sources=[ROOT/'src/kerr_scalar_precision.jl',ROOT/'scripts/run_scalar_precision_20261023.jl',Path(__file__)]
before={str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in sources}
settings=(384,64,80,a.quad,a.levin)
cmd=['wsl.exe','-d',DISTRO,'-e','env','OPENBLAS_NUM_THREADS=1','JULIA_NUM_THREADS=1','timeout','--kill-after=10','300',RUNTIME,'--startup-file=no','--threads=1',linux+'/scripts/run_scalar_precision_20261023.jl',linux+'/results/precision_20261023/'+a.name+'/solution',a.spin,a.omega,str(a.ell),'0',str(a.n),*map(str,settings)]
started=time.time();print('RUN',a.name,flush=True)
with (folder/'stdout.txt').open('w',encoding='utf8') as out,(folder/'stderr.txt').open('w',encoding='utf8') as err:
    r=subprocess.run(cmd,stdout=out,stderr=err,timeout=330)
after={str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in sources}
outputs={str(q.relative_to(folder)):hashlib.sha256(q.read_bytes()).hexdigest() for q in folder.rglob('*') if q.is_file()}
status=('completed' if r.returncode==0 else 'failed') if before==after else 'inputs-changed'
(folder/'manifest.json').write_text(json.dumps(dict(status=status,returncode=r.returncode,command=cmd,source_hashes_before=before,source_hashes_after=after,outputs=outputs,seconds=time.time()-started,precision=settings,timeout_seconds=300,memory_guard_bytes=1500000000),indent=2),encoding='utf8')
print(status,flush=True);print((folder/'stdout.txt').read_text(encoding='utf8'),flush=True)
if status!='completed':
    print((folder/'stderr.txt').read_text(encoding='utf8'),flush=True)
    raise SystemExit(1)
