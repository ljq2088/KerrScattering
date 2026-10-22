"""Render parameter-free principal-response comparisons and manuscript tables."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]


def read(name):
    with (ROOT/'results'/name).open(newline='',encoding='utf8') as handle:
        return list(csv.DictReader(handle))


def main():
    rows=read('kerr_scalar_principal_expanded_comparison_20261014.csv')
    curves=read('kerr_scalar_principal_expanded_analytic_curves_20261014.csv')
    analytic_checks=read('kerr_scalar_principal_expanded_analytic_checks_20261014.csv')
    plt.rcParams.update({'font.family':'serif','font.size':9})
    fig,axes=plt.subplots(3,3,figsize=(7.1,6.1),constrained_layout=True)
    colors={1:'#0072b2',2:'#d55e00',3:'#009e73'}
    for i,m in enumerate((2,3,4)):
        for j,y in enumerate((-0.5,0.5,1.0)):
            ax=axes[i,j]
            for n in (1,2,3):
                line=[r for r in curves if int(r['m'])==m and int(r['n'])==n and float(r['y'])==y]
                points=[r for r in rows if int(r['m'])==m and int(r['n'])==n and float(r['y'])==y and r['accepted']=='True']
                ax.loglog([float(r['sigma']) for r in line],[float(r['F']) for r in line],color=colors[n],lw=1.2,label=f'$n={n}$')
                ax.scatter([float(r['sigma']) for r in points],[float(r['F_spectral']) for r in points],s=22,
                           edgecolors=colors[n],facecolors='white',marker='o',zorder=3)
            ax.set_title(rf'$(\ell,m)=({m},{m}),\ y={y:g}$',fontsize=9)
            ax.grid(alpha=.2,which='major')
            if i==2: ax.set_xlabel(r'$\sigma=(r_+-r_-)/M$')
            if j==0: ax.set_ylabel(r'$\sigma^n\widehat\chi_n$')
    handles, labels = axes[0,0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, fontsize=9, ncol=3,
               loc='upper center', bbox_to_anchor=(0.5, 1.055))
    fig.savefig(ROOT/'figures/kerr_scalar_principal_expanded_20261014.png',dpi=240,bbox_inches='tight')
    plt.close(fig)
    table=r'''\begin{table}[t]
\caption{Critical scalar angular eigenvalues and principal weights at
$a/M=1$, $M\omega=m/2$, with $h=1/2+i\beta$.}
\label{tab:principal-weights20261014}
\begin{ruledtabular}\begin{tabular}{ccc}
$(\ell,m)$ & $A_{\ell m}$ & $\beta$\\
'''
    from src.teukolsky_scalar import scalar_spheroidal_eigenvalue
    for m in (2,3,4):
        A=scalar_spheroidal_eigenvalue(m,m,m/2)
        beta=np.sqrt(7*m*m/4-A-.25)
        table+=f'$({m},{m})$ & {A:.10f} & {beta:.10f} '+r'\\'+'\n'
    table+=r'''\end{tabular}\end{ruledtabular}\end{table}
\begin{table*}[t]
\caption{Parameter-free leading matching at $a/M=0.999999$.
The three middle columns give relative differences between the spectral
response and the matched prediction, in percent.  $\delta_N$ is the maximum
paired spectral response change across the three spins and three interaction
orders at fixed $q=3072$; $\delta_q$ is the corresponding change at fixed
$N=448$ under $q=1536\to3072$.}
\label{tab:principal-verification20261014}
\begin{ruledtabular}\begin{tabular}{ccccccc}
$(\ell,m)$ & $y$ & $n=1$ (\%) & $n=2$ (\%) & $n=3$ (\%) & $\delta_N$ & $\delta_q$\\
'''
    def sci(value):
        mantissa,exponent=f'{value:.2e}'.split('e')
        return '$'+mantissa+r'\times10^{'+str(int(exponent))+'}$'
    for m in (2,3,4):
        for y in (-0.5,0.5,1.0):
            group=[r for r in rows if int(r['m'])==m and float(r['y'])==y]
            finest={int(r['n']):r for r in group if float(r['a'])==0.999999}
            values=[100*float(finest[n]['matched_relative_error']) for n in (1,2,3)]
            table+=f'$({m},{m})$ & {y:g} & '+' & '.join(f'{v:.3f}' for v in values)+' & '
            table+=' & '.join(sci(max(float(r[k]) for r in group)) for k in ('paired_chi_change','quadrature_change'))+r'\\'+'\n'
    table+=r'\end{tabular}\end{ruledtabular}\end{table*}'+'\n'
    maxes={key:max(float(r[key]) for r in rows) for key in ('paired_chi_change','paired_complex_change','quadrature_change',
               'radial_residual_max','coeff_tail_max','normalized_nonlinear_balance')}
    accepted=sum(r['accepted']=='True' for r in rows)
    absolute=sum(r['absolute_flux_gate']=='True' for r in rows)
    table+=f'All {accepted} of {len(rows)} points pass the stated principal-response criteria. '
    table+=f'The maximum spectral response change is {sci(maxes["paired_chi_change"])}, '
    table+=f'the maximum complex-response change is {sci(maxes["paired_complex_change"])}, '
    table+=f'and the maximum independent quadrature change is {sci(maxes["quadrature_change"])}. '
    table+=f'The maximum off-grid radial relative residual is {sci(maxes["radial_residual_max"])}, '
    table+=f'the maximum coefficient tail is {sci(maxes["coeff_tail_max"])}, '
    table+=f'and the maximum normalized interference-balance error is {sci(maxes["normalized_nonlinear_balance"])}. '
    table+=f'The original absolute flux gate is also met by {absolute} points; that flag is retained separately in the data.\n'
    table+=f'The maximum absolute interference-balance error is {sci(max(abs(float(r["nonlinear_balance"])) for r in rows))}. '
    table+=f'The two analytic integral settings differ by at most {sci(max(float(r["integral_relative_check"]) for r in analytic_checks))} in the recorded relative integral diagnostic. '
    table+=f'The analytic log-period test has a maximum relative difference of {sci(max(float(r["periodic_relative_check"]) for r in analytic_checks))}.\n'
    (ROOT/'docs/prd/principal_expanded_tables_20261014.tex').write_text(table,encoding='utf8')


if __name__=='__main__':
    import sys
    sys.path.insert(0,str(ROOT))
    main()
