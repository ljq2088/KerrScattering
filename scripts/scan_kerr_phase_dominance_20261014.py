"""Paired stationary phase/flux responses at near-transparent detunings."""
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

rows=[]
for a in (.9999,.99999,.999999):
    params=KerrParams(M=1,a=a)
    kappa=(params.rp-params.rm)/(2*(params.rp**2+a*a))
    for n in (1,2,3):
        for y in (1,2,4):
            omega=2*params.omega_h+y*kappa
            for N,q in ((384,32),(448,48)):
                require_memory_room(900,'phase/flux scan')
                result=compute_kerr_scalar_green_diagnostics(2,2,omega,a=a,N_inner=N,N_outer=N,
                    r_match=12,quad_order=q,linear_solver='equilibrated',nonlinearity_order=n,
                    inner_quadrature='log-horizon',inner_log_min=-34,tail_epsrel=1e-11)
                flux=fixed_incident_flux_coefficients(result)
                rho=result.A_hor_1/abs(result.B_inc)**(2*n)
                ref_fix=result.A_ref_1/(abs(result.B_inc)**(2*n)*result.B_inc)
                sigma=params.rp-params.rm
                row=dict(a=a,l=2,m=2,n=n,y=y,N=N,q=q,kappa=kappa,sigma=sigma,
                    chi=flux.horizon_response,phase=rho.imag,phase_flux_ratio=abs(rho.imag)/max(abs(flux.horizon_response),1e-300),
                    scaled_phase=sigma**n*rho.imag,scaled_chi=sigma**n*flux.horizon_response,
                    T0=flux.T0,R0=abs(result.B_ref/result.B_inc)**2,T1=flux.T1,R1=flux.R1,
                    born_reflected_square=abs(ref_fix)**2,
                    normalized_balance=abs(flux.nonlinear_balance)/max(abs(flux.T1)+abs(flux.R1),1e-300),
                    rss_mb=require_memory_room(900,'after phase/flux scan'))
                rows.append(row)
                with (ROOT/'results/kerr_scalar_phase_dominance_20261014.csv').open('w',newline='',encoding='utf8') as h:
                    writer=csv.DictWriter(h,fieldnames=list(row));writer.writeheader();writer.writerows(rows)
                print(f'a={a} n={n} y={y} N={N} chi={row["chi"]:.6e} phase={rho.imag:.6e} ratio={row["phase_flux_ratio"]:.3e}',flush=True)
