"""Bounded log-horizon quadrature pilot with independent order/radius checks."""
import os
for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[name] = '1'
import csv
import hashlib
import json
from pathlib import Path
import sys
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.teukolsky_scalar import KerrParams
from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics, fixed_incident_flux_coefficients
from scripts.run_kerr_scalar_nonlinear_diagnostics import require_memory_room

params = KerrParams(M=1, a=0.999999)
kappa = (params.rp-params.rm)/(2*(params.rp**2+params.a**2))
cases = [(2,1,1), (2,3,-0.5), (3,1,1), (3,3,1), (4,1,1), (4,3,1)]
settings = [(384,32,-26,12),(448,48,-30,12),(448,64,-34,12),
            (448,64,-34,8),(448,64,-34,16)]
output = ROOT/'results/kerr_scalar_log_horizon_pilot_20261014.csv'
rows = []
for m,n,y in cases:
    omega = m*params.omega_h+y*kappa
    for N,q,tmin,rm in settings:
        start = time.perf_counter()
        require_memory_room(900,'log horizon pilot')
        result = compute_kerr_scalar_green_diagnostics(m,m,omega,a=params.a,
                    N_outer=N,N_inner=N,r_match=rm,quad_order=q,linear_solver='equilibrated',
                    nonlinearity_order=n,inner_quadrature='log-horizon',inner_log_min=tmin,
                    tail_epsrel=1e-11)
        flux = fixed_incident_flux_coefficients(result)
        rho = result.A_hor_1/abs(result.B_inc)**(2*n)
        row = dict(a=params.a,l=m,m=m,n=n,y=y,omega=omega,N=N,q=q,tmin=tmin,
                   r_match=rm,chi=flux.horizon_response,rho_real=rho.real,rho_imag=rho.imag,
                   T0=flux.T0,T1=flux.T1,R1=flux.R1,balance=flux.nonlinear_balance,
                   normalized_balance=abs(flux.nonlinear_balance)/max(abs(flux.T1)+abs(flux.R1),1e-300),
                   rss_mb=require_memory_room(900,'after log horizon pilot'),elapsed_s=time.perf_counter()-start)
        rows.append(row)
        with output.open('w',newline='',encoding='utf8') as handle:
            writer=csv.DictWriter(handle,fieldnames=list(row))
            writer.writeheader(); writer.writerows(rows)
        print(row,flush=True)
report=dict(cases=cases,settings=settings,source_sha256=hashlib.sha256(
            (ROOT/'src/kerr_scalar_nonlinear.py').read_bytes()).hexdigest(),
            maximum_rss_mb=max(r['rss_mb'] for r in rows),calls=len(rows))
output.with_suffix('.json').write_text(json.dumps(report,indent=2),encoding='utf8')
