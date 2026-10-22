"""Add uniform, directly evaluated samples around the verified flux crossing."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='1'
import csv
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.teukolsky_scalar import KerrParams
from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics,fixed_incident_flux_coefficients
from scripts.run_kerr_scalar_nonlinear_diagnostics import require_memory_room
params=KerrParams(M=1,a=.999999)
kappa=(params.rp-params.rm)/(2*(params.rp**2+params.a**2))
path=ROOT/'results/kerr_scalar_flux_zero_20261014.csv'
with path.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h))
done={round(float(r['y']),12) for r in rows if r['N']=='448' and r['q']=='48' and r['r_match']=='12'}
for y in np.linspace(2.34,2.49,21):
    if round(float(y),12) in done:continue
    require_memory_room(900,'dense flux zero')
    result=compute_kerr_scalar_green_diagnostics(2,2,2*params.omega_h+y*kappa,a=params.a,
        N_inner=448,N_outer=448,r_match=12,quad_order=48,linear_solver='equilibrated',
        nonlinearity_order=3,inner_quadrature='log-horizon',inner_log_min=-34,tail_epsrel=1e-12)
    flux=fixed_incident_flux_coefficients(result)
    rho=result.A_hor_1/abs(result.B_inc)**6
    row=dict(y=y,N=448,q=48,r_match=12,chi=flux.horizon_response,phase=rho.imag,
             T0=flux.T0,T1=flux.T1,R1=flux.R1,balance=flux.nonlinear_balance,
             rss_mb=require_memory_room(900,'after dense zero'))
    rows.append(row)
    with path.open('w',newline='',encoding='utf8') as h:
        writer=csv.DictWriter(h,fieldnames=list(row));writer.writeheader();writer.writerows(rows)
    print(f'y={y:.6f} chi={row["chi"]:.9g} phase={row["phase"]:.9g}',flush=True)
