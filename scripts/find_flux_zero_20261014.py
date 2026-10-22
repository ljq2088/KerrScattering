"""Bracket a real flux-response zero and independently check its phase."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='1'
import csv
from pathlib import Path
import sys
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.teukolsky_scalar import KerrParams
from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics,fixed_incident_flux_coefficients
from scripts.run_kerr_scalar_nonlinear_diagnostics import require_memory_room
params=KerrParams(M=1,a=.999999)
kappa=(params.rp-params.rm)/(2*(params.rp**2+params.a**2))
rows=[]
def evaluate(y,N=448,q=48,rm=12):
    require_memory_room(900,'flux zero')
    result=compute_kerr_scalar_green_diagnostics(2,2,2*params.omega_h+y*kappa,a=params.a,
            N_inner=N,N_outer=N,r_match=rm,quad_order=q,linear_solver='equilibrated',
            nonlinearity_order=3,inner_quadrature='log-horizon',inner_log_min=-34,tail_epsrel=1e-12)
    flux=fixed_incident_flux_coefficients(result)
    rho=result.A_hor_1/abs(result.B_inc)**6
    row=dict(y=y,N=N,q=q,r_match=rm,chi=flux.horizon_response,phase=rho.imag,
             T0=flux.T0,T1=flux.T1,R1=flux.R1,balance=flux.nonlinear_balance,
             rss_mb=require_memory_room(900,'after flux zero'))
    rows.append(row)
    with (ROOT/'results/kerr_scalar_flux_zero_20261014.csv').open('w',newline='',encoding='utf8') as h:
        writer=csv.DictWriter(h,fieldnames=list(row));writer.writeheader();writer.writerows(rows)
    print(row,flush=True)
    return flux.horizon_response
root=brentq(evaluate,2,4,xtol=2e-7)
for N,q,rm in ((448,64,12),(576,64,12),(576,64,8),(576,64,16)):
    for y in (root-2e-4,root,root+2e-4):
        evaluate(y,N,q,rm)
print('root estimate:',root,flush=True)
