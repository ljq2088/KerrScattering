"""Independent reconstructed sourced-field residual in the throat at a flux zero."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='1'
import csv
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from numpy.polynomial.chebyshev import chebval,chebder
from src.kerr_scalar_spectral import _cheb_interval
from src.kerr_scalar_nonlinear import (compute_kerr_scalar_green_diagnostics,_solve_matched_mode,
                                     _horizon_log_rule,_rstar_horizon_distance)
from src.teukolsky_scalar import KerrParams
from scripts.run_kerr_scalar_spectral_quality import _cheb_coeff
from scripts.validate_principal_expanded_20261014 import quality
from scripts.run_kerr_scalar_nonlinear_diagnostics import require_memory_room
params=KerrParams(M=1,a=.999999)
gap=params.rp-params.rm
kappa=gap/(2*(params.rp**2+params.a**2))
y=2.4195403604191505
omega=2*params.omega_h+y*kappa
result=compute_kerr_scalar_green_diagnostics(2,2,omega,a=params.a,N_outer=576,N_inner=576,
        r_match=12,quad_order=64,linear_solver='equilibrated',nonlinearity_order=3,
        inner_quadrature='log-horizon',inner_log_min=-34,tail_epsrel=1e-12)
mode=_solve_matched_mode(2,2,omega,params,result.radial_lambda,params.rp/12,576,576,
                         'linear',0,0,'equilibrated')
p=omega-2*params.omega_h
def fields(X):
    X=np.asarray(X)
    distance=gap*X; r=params.rp+distance
    phase=np.exp(-1j*p*_rstar_horizon_distance(distance,params))
    rin=phase*mode['inner_eval'].u(params.rp/r)
    rup=(-np.conj(mode['B_ref'])*rin+mode['B_inc']*np.conj(rin))/mode['flux_norm']
    source=(r*r*result.angular_coupling+params.a**2*result.angular_coupling_cos2)*abs(rin)**6*rin
    return rin,rup,source
distance,w,cutoff=_horizon_log_rule(params,params.rp+gap,64,-34)
rin,rup,Q=fields(distance/gap)
P=params.rp**2*result.angular_coupling+params.a**2*result.angular_coupling_cos2
osc=cutoff*np.exp(-2j*p*_rstar_horizon_distance(cutoff,params))/(1-1j*y)
Iin0=np.sum(w*rin*Q)+P*osc
Iup0=np.sum(w*rup*Q)+P*(-np.conj(mode['B_ref'])*osc+mode['B_inc']*cutoff)/mode['flux_norm']
lx,lw=np.polynomial.legendre.leggauss(96)
rows=[]
for degree in (16,24,32,48,64):
    nodes,_,_=_cheb_interval(degree,1,8)
    vals=[]
    for X in nodes:
        s=(X-1)*lx/2+(X+1)/2
        rin,rup,Q=fields(s)
        Iin=Iin0+gap*(X-1)/2*np.sum(lw*rin*Q)
        Iup=result.source_projection_hor-Iup0-gap*(X-1)/2*np.sum(lw*rup*Q)
        ri,ru,_=fields(X)
        vals.append(-(ru*Iin+ri*Iup)/result.wronskian)
    coeff=_cheb_coeff(np.asarray(vals))
    t=np.cos(np.pi*(np.arange(600)+.5)/600)
    X=4.5-3.5*t; r=params.rp+gap*X
    R=chebval(t,coeff); RX=-chebval(t,chebder(coeff))/3.5
    RXX=chebval(t,chebder(coeff,2))/3.5**2
    K=(r*r+params.a**2)*omega-2*params.a
    terms=(X*(X+1)*RXX,(2*X+1)*RX,(K*K/(gap*gap*X*(X+1))-result.radial_lambda)*R,fields(X)[2])
    residual=abs(sum(terms))/np.maximum(sum(abs(v) for v in terms),1e-300)
    row=dict(degree=degree,X_left=1,X_right=8,relative_residual_max=max(residual),
             relative_residual_median=np.median(residual),tail=max(abs(coeff[-8:]))/max(abs(coeff)),
             rss_mb=require_memory_room(900,'sourced flux-zero test'))
    rows.append(row);print(row,flush=True)
with (ROOT/'results/kerr_scalar_flux_zero_sourced_20261014.csv').open('w',newline='',encoding='utf8') as h:
    writer=csv.DictWriter(h,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
qq=quality(params.a,2,2,omega,576,12)
with (ROOT/'results/kerr_scalar_flux_zero_quality_20261014.csv').open('w',newline='',encoding='utf8') as h:
    writer=csv.DictWriter(h,fieldnames=list(qq[0]));writer.writeheader();writer.writerows(qq)
