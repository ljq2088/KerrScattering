"""Archive improved principal data and the phase/flux candidate diagnostics."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT/'results'/name).open(newline='',encoding='utf8') as h:
        return list(csv.DictReader(h))
def key(r):
    if 'nonlinearity_order' in r:
        return (float(r['a']),int(r['l']),int(r['m']),float(r['detuning_over_kappa']),int(r['nonlinearity_order']))
    return (float(r['a']),int(r['l']),int(r['m']),float(r['y']),int(r['n']))
def save(name,rows):
    with (ROOT/'results'/name).open('w',newline='',encoding='utf8') as h:
        writer=csv.DictWriter(h,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
fine=read('kerr_scalar_principal_log_20261014_N448_q48.csv')
coarse={key(r):r for r in read('kerr_scalar_principal_log_20261014_N384_q32.csv')}
old={key(r):r for r in read('kerr_scalar_principal_expanded_comparison_20261014.csv')}
assert len(fine)==len(coarse)==81
rows=[]
for r in fine:
    a,l,m,y,n=key(r); c=coarse[key(r)]; previous=old[key(r)]
    chi=float(r['horizon_response']);sigma=2*np.sqrt(1-a*a)
    rho=complex(float(r['A_hor_1_real']),float(r['A_hor_1_imag']))/float(r['B_inc_abs'])**(2*n)
    crho=complex(float(c['A_hor_1_real']),float(c['A_hor_1_imag']))/float(c['B_inc_abs'])**(2*n)
    row=dict(a=a,l=l,m=m,y=y,n=n,sigma=sigma,chi=chi,F_spectral=sigma**n*chi,
             chi_matched=float(previous['chi_matched']),matched_relative_error=abs(chi-float(previous['chi_matched']))/abs(chi),
             paired_change=abs(chi-float(c['horizon_response']))/abs(chi),
             complex_paired_change=abs(rho-crho)/abs(rho),legacy_quadrature_difference=abs(chi-float(previous['chi']))/abs(chi))
    rows.append(row)
save('kerr_scalar_principal_log_comparison_20261014.csv',rows)
phase=read('kerr_scalar_phase_dominance_20261014.csv')
cp={(r['a'],r['n'],r['y']):r for r in phase if r['N']=='384'}
pf=[r for r in phase if r['N']=='448']
for r in pf:
    c=cp[(r['a'],r['n'],r['y'])]
    r['paired_chi_change']=abs(float(r['chi'])-float(c['chi']))/max(abs(float(r['chi'])),1e-300)
    r['paired_phase_change']=abs(float(r['phase'])-float(c['phase']))/abs(float(r['phase']))
save('kerr_scalar_phase_dominance_summary_20261014.csv',pf)
zero=read('kerr_scalar_flux_zero_20261014.csv')
root=2.4195403604191505
atroot=[r for r in zero if abs(float(r['y'])-root)<1e-12]
left=[r for r in zero if abs(float(r['y'])-(root-2e-4))<1e-12]
right=[r for r in zero if abs(float(r['y'])-(root+2e-4))<1e-12]
assert all(float(r['chi'])>0 for r in left)
assert all(float(r['chi'])<0 for r in right)
assert max(abs(float(r['chi'])) for r in atroot)<1e-7
plt.rcParams.update({'font.family':'serif','font.size':10})
fig,ax=plt.subplots(1,2,figsize=(7.1,3.0),constrained_layout=True)
colors=['#0072b2','#d55e00','#009e73']
for n,color in zip((1,2,3),colors):
    group=sorted([r for r in pf if r['n']==str(n) and r['y']=='2'],key=lambda r:float(r['kappa']))
    ax[0].loglog([float(r['kappa']) for r in group],[float(r['phase']) for r in group],
                'o-',color=color,label=rf'$n={n}$')
ax[0].set_xlabel(r'$M\kappa$');ax[0].set_ylabel(r'$\mathrm{Im}\,\widehat\rho_n$')
ax[0].set_title(r'$(\ell,m)=(2,2),\ y=2$');ax[0].legend(frameon=False)
points={float(r['y']):r for r in zero if r['N']=='448' and r['q']=='48' and r['r_match']=='12'}
group=[r for y,r in sorted(points.items()) if 2.34<=y<=2.49]
ax[1].plot([float(r['y']) for r in group],[float(r['chi']) for r in group],
           'o-',color=colors[0],label=r'$\widehat\chi_3$')
ax[1].axhline(0,color='#555555',lw=.7)
ax[1].axvline(root,color='#555555',lw=.7,ls=':')
ax[1].set_xlabel(r'$y=p/\kappa$');ax[1].set_ylabel(r'$\widehat\chi_3$')
ax[1].set_title(r'$a/M=0.999999,\ n=3$')
ax[1].text(.52,.91,r'$y_\star\simeq2.41954$',transform=ax[1].transAxes,fontsize=9)
ax[1].text(.52,.81,r'$\mathrm{Im}\,\widehat\rho_3\simeq1.03\times10^4$',transform=ax[1].transAxes,fontsize=9)
for a in ax:a.grid(alpha=.2)
fig.savefig(ROOT/'figures/kerr_scalar_phase_flux_separation_20261014.png',dpi=240)
plt.close(fig)
report=dict(principal_points=81,max_paired_change=max(r['paired_change'] for r in rows),
    max_complex_paired_change=max(r['complex_paired_change'] for r in rows),
    max_legacy_difference=max(r['legacy_quadrature_difference'] for r in rows),
    phase_points=len(pf),max_phase_paired_change=max(r['paired_phase_change'] for r in pf),
    max_phase_grid_chi_change=max(r['paired_chi_change'] for r in pf),
    flux_zero_root_estimate=root,flux_zero_verified_bracket=[root-2e-4,root+2e-4],
    max_abs_chi_at_root=max(abs(float(r['chi'])) for r in atroot),
    phase_at_root=float(atroot[0]['phase']),sources={})
for path in [ROOT/'src/kerr_scalar_nonlinear.py',Path(__file__).resolve(),
             ROOT/'results/kerr_scalar_principal_log_comparison_20261014.csv',
             ROOT/'results/kerr_scalar_phase_dominance_summary_20261014.csv',
             ROOT/'results/kerr_scalar_flux_zero_20261014.csv',
             ROOT/'results/kerr_scalar_flux_zero_sourced_20261014.csv']:
    report['sources'][str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
(ROOT/'results/kerr_scalar_letter_refinement_20261014.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
