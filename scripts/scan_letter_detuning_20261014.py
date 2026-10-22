"""Real-weight controls and broader principal detuning with paired settings."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='1'
import csv
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.teukolsky_scalar import KerrParams
from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics,fixed_incident_flux_coefficients
from scripts.run_kerr_scalar_nonlinear_diagnostics import require_memory_room

cases=[(a,1,n,.5) for a in (.9999,.99999,.999999) for n in (1,2,3)]
cases += [(.999999,2,n,y) for n in (1,3) for y in (-2,-1,.25,2)]
rows=[]
for a,m,n,y in cases:
    params=KerrParams(M=1,a=a)
    kappa=(params.rp-params.rm)/(2*(params.rp**2+a*a))
    omega=m*params.omega_h+y*kappa
    for N,q in ((384,32),(448,48)):
        require_memory_room(900,'detuning pilot')
        result=compute_kerr_scalar_green_diagnostics(m,m,omega,a=a,N_inner=N,N_outer=N,
                    r_match=12,quad_order=q,linear_solver='equilibrated',nonlinearity_order=n,
                    inner_quadrature='log-horizon',inner_log_min=-30,tail_epsrel=1e-11)
        flux=fixed_incident_flux_coefficients(result)
        rho=result.A_hor_1/abs(result.B_inc)**(2*n)
        row=dict(a=a,l=m,m=m,n=n,y=y,N=N,q=q,chi=flux.horizon_response,
                 rho_real=rho.real,rho_imag=rho.imag,T0=flux.T0,T1=flux.T1,R1=flux.R1,
                 normalized_balance=abs(flux.nonlinear_balance)/max(abs(flux.T1)+abs(flux.R1),1e-300),
                 rss_mb=require_memory_room(900,'after detuning pilot'))
        rows.append(row)
        with (ROOT/'results/kerr_scalar_letter_detuning_20261014.csv').open('w',newline='',encoding='utf8') as h:
            writer=csv.DictWriter(h,fieldnames=list(row)); writer.writeheader(); writer.writerows(rows)
        print(row,flush=True)
