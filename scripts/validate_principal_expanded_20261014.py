"""Expanded principal-mode prediction, convergence and off-grid diagnostics."""
import csv
import gc
import hashlib
import json
import os
from pathlib import Path
import sys

for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='1'
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from scripts.analyze_principal_matching_20261013 import near_data
from scripts.run_kerr_scalar_nonlinear_diagnostics import require_memory_room
from scripts.run_kerr_scalar_spectral_quality import _offgrid_residuals,_cheb_coeff
from src.kerr_scalar_spectral import _solve_branch,_transformed_coefficients
from src.teukolsky_scalar import KerrParams,teukolsky_lambda_s0,scalar_power_coupling


def read_csv(path):
    with path.open(newline='',encoding='utf8') as handle:
        return list(csv.DictReader(handle))


def save_csv(path,rows):
    temporary=path.with_suffix('.csv.tmp')
    with temporary.open('w',newline='',encoding='utf8') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    temporary.replace(path)


def integrals(data,order,limit):
    gx,gw=np.polynomial.legendre.leggauss(order)
    total={n:[0j,0.0] for n in (1,2,3)}
    for left in range(-limit,limit):
        x=np.exp(left+0.5+gx/2)
        f=np.asarray([complex(data['f'](float(v))) for v in x])
        for n in total:
            total[n][0]+=np.sum(gw*x/2*f*f*abs(f)**(2*n))
            total[n][1]+=float(np.sum(gw*x/2*abs(f)**(2*n+2)))
    return total


def coefficients(data,ios,iabs,C,m,y,sigma,n):
    phase=np.exp(1j*data['h'].imag*np.log(sigma))
    D=data['cp']*data['up']/phase+data['cm']*data['um']*phase
    gp,gm=data['gp']*phase,data['gm']/phase
    det=abs(data['cp'])**2-abs(data['cm'])**2
    aa=(gp*data['cp'].conjugate()-gm*data['cm'].conjugate())/det
    bb=(-gp*data['cm']+gm*data['cp'])/det
    AH=1j*C/y*(aa/bb*ios+iabs)
    F=2*AH.real/abs(D)**(2*n)
    return F/sigma**n,F,y/(m*abs(D)**2),AH


def quality(a,l,m,omega,N,rmatch):
    params=KerrParams(M=1,a=a)
    zm=params.rp/rmatch
    lam=teukolsky_lambda_s0(l,m,a,omega)
    out=[]
    for branch,left,right,boundary in [('down',0,zm,'left'),('up',0,zm,'left'),('in',zm,1,'right')]:
        require_memory_room(900,'principal quality')
        data=_solve_branch(N,left,right,branch,boundary,params,'linear',0,l,m,omega,lam,'equilibrated')
        res=_offgrid_residuals(data,left,right,branch,params,'linear',0,l,m,omega,lam,600)
        coeff=abs(_cheb_coeff(data['u']))
        idx=-1 if branch=='in' else 0
        B2,B1,B0=_transformed_coefficients(data['z'][idx],branch,params,l,m,omega,lam)
        boundary_terms=(B1*data['uz'][idx],B0*data['u'][idx])
        out.append(dict(a=a,l=l,m=m,omega=omega,N=N,branch=branch,r_match=rmatch,
                        radial_residual_max=float(max(res[5])),
                        amplitude_residual_max=float(max(res[2])),
                        coeff_tail=float(max(coeff[-16:])/max(coeff)),
                        boundary_residual=float(abs(sum(boundary_terms))/max(sum(abs(v) for v in boundary_terms),1e-300)),
                        normalization_error=float(abs(data['u'][idx]-1)),
                        rss_mb=require_memory_room(900,'after principal quality')))
    return out


def key(r):
    return (float(r['a']),int(r['l']),int(r['m']),float(r['detuning_over_kappa']),int(r['nonlinearity_order']))


def main():
    paths=[ROOT/f'results/kerr_scalar_principal_expanded_20261014_N{N}_q3072.csv' for N in (384,448)]
    coarse={key(r):r for r in read_csv(paths[0])}
    fine=read_csv(paths[1])
    intermediate_path=ROOT/'results/kerr_scalar_principal_expanded_20261014_N448.csv'
    intermediate={key(r):r for r in read_csv(intermediate_path)}
    assert len(coarse)==len(fine)==81
    analytic={}; checks=[]; curves=[]
    for l,m in ((2,2),(3,3),(4,4)):
        for y in (-0.5,0.5,1.0):
            print(f'Analytic matching l=m={m} y={y}',flush=True)
            data=near_data(l,m,y)
            low=integrals(data,12,30); high=integrals(data,20,36)
            for n in (1,2,3):
                C=float(np.real(sum(scalar_power_coupling(l,m,1,m/2,n,cos_power=j) for j in (0,2))))
                err=max(abs(v-w)/max(abs(w),1e-300) for v,w in zip(low[n],high[n]))
                assert err<1e-9, (l,m,y,n,err)
                analytic[(l,m,y,n)]=(data,high[n],C)
                beta=data['h'].imag
                F0=coefficients(data,*high[n],C,m,y,0.01,n)[1]
                F1=coefficients(data,*high[n],C,m,y,0.01*np.exp(np.pi/beta),n)[1]
                assert abs(F0-F1)/max(abs(F0),1e-300)<1e-10
                checks.append(dict(l=l,m=m,y=y,n=n,h_real=data['h'].real,beta=beta,
                                   integral_relative_check=float(err),periodic_relative_check=float(abs(F0-F1)/abs(F0)),
                                   ode_residual_max=max(data['ode_residuals'])))
                for sigma in np.geomspace(0.0028,0.0285,180):
                    predicted,F,T0,AH=coefficients(data,*high[n],C,m,y,sigma,n)
                    curves.append(dict(l=l,m=m,y=y,n=n,sigma=float(sigma),F=F,chi=predicted))
    rows=[]; qualities=[]; quality_index={}
    for raw in fine:
        k=key(raw); a,l,m,y,n=k
        old=coarse[k]
        omega=float(raw['omega']); sigma=2*np.sqrt(1-a*a)
        if (a,l,m,y) not in quality_index:
            qq=quality(a,l,m,omega,448,float(raw['r_match']))
            qualities.extend(qq); quality_index[(a,l,m,y)]=qq
            save_csv(ROOT/'results/kerr_scalar_principal_expanded_quality_20261014.csv',qualities)
        qq=quality_index[(a,l,m,y)]
        data,source,C=analytic[(l,m,y,n)]
        predicted,F,T0,AH=coefficients(data,*source,C,m,y,sigma,n)
        chi=float(raw['horizon_response']); oldchi=float(old['horizon_response'])
        change=abs(chi-oldchi)/max(abs(chi),1e-300)
        rho=complex(float(raw['A_hor_1_real']),float(raw['A_hor_1_imag']))/float(raw['B_inc_abs'])**(2*n)
        oldrho=complex(float(old['A_hor_1_real']),float(old['A_hor_1_imag']))/float(old['B_inc_abs'])**(2*n)
        vector_change=abs(rho-oldrho)/max(abs(rho),1e-300)
        quadrature_change=abs(chi-float(intermediate[k]['horizon_response']))/max(abs(chi),1e-300)
        normalized_balance=abs(float(raw['nonlinear_balance']))/max(abs(float(raw['T1']))+abs(float(raw['R1'])),1e-300)
        max_res=max(q['radial_residual_max'] for q in qq)
        tail=max(q['coeff_tail'] for q in qq)
        accepted=(change<1e-5 and vector_change<1e-5 and quadrature_change<1e-4 and max_res<1e-6 and tail<1e-8 and normalized_balance<1e-6)
        row=dict(a=a,l=l,m=m,y=y,n=n,N=448,q=3072,sigma=sigma,kappa=float(raw['surface_gravity']),
                 beta=data['h'].imag,chi=chi,chi_matched=predicted,F_spectral=sigma**n*chi,F_matched=F,
                 matched_relative_error=abs(chi-predicted)/max(abs(chi),1e-300),
                 paired_chi_change=change,paired_complex_change=vector_change,quadrature_change=quadrature_change,T0=float(raw['T0']),T0_matched=T0,
                 nonlinear_balance=float(raw['nonlinear_balance']),normalized_nonlinear_balance=normalized_balance,
                 radial_residual_max=max_res,coeff_tail_max=tail,accepted=accepted,
                 absolute_flux_gate=abs(float(raw['nonlinear_balance']))<=1e-8)
        rows.append(row)
        print(f'{l},{m} y={y} n={n} a={a} match={row["matched_relative_error"]:.3e} refine={change:.3e} accepted={accepted}',flush=True)
        gc.collect()
    save_csv(ROOT/'results/kerr_scalar_principal_expanded_comparison_20261014.csv',rows)
    save_csv(ROOT/'results/kerr_scalar_principal_expanded_analytic_curves_20261014.csv',curves)
    save_csv(ROOT/'results/kerr_scalar_principal_expanded_analytic_checks_20261014.csv',checks)
    summary=[]
    for l,m,y,n in analytic:
        group=[r for r in rows if (r['l'],r['m'],r['y'],r['n'])==(l,m,y,n)]
        finest=min(group,key=lambda r:r['sigma'])
        slope=np.polyfit(np.log([r['sigma'] for r in group]),np.log([abs(r['chi']) for r in group]),1)[0]
        summary.append(dict(l=l,m=m,y=y,n=n,beta=finest['beta'],accepted=sum(r['accepted'] for r in group),
                            finest_a=finest['a'],finest_match_error=finest['matched_relative_error'],
                            max_refinement=max(r['paired_chi_change'] for r in group),
                            max_quadrature_change=max(r['quadrature_change'] for r in group),
                            apparent_three_point_slope=float(slope),predicted_envelope_power=-n))
    save_csv(ROOT/'results/kerr_scalar_principal_expanded_summary_20261014.csv',summary)
    record=dict(points=len(rows),accepted=sum(r['accepted'] for r in rows),analytic_fitted_parameters=0,
                acceptance=dict(paired_response=1e-5,paired_complex_response=1e-5,quadrature_change=1e-4,radial_residual=1e-6,coeff_tail=1e-8,
                                normalized_flux_balance=1e-6),
                analytic_cases=len(checks),log_X_checks=[[-30,30],[-36,36]],gauss_orders=[12,20],
                files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths+[intermediate_path,Path(__file__).resolve(),
                    ROOT/'scripts/analyze_principal_matching_20261013.py',ROOT/'src/kerr_scalar_spectral.py',ROOT/'src/kerr_scalar_nonlinear.py']})
    (ROOT/'results/kerr_scalar_principal_expanded_manifest_20261014.json').write_text(json.dumps(record,indent=2),encoding='utf8')
    print(record,flush=True)


if __name__=='__main__':
    main()
