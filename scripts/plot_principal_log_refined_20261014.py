"""Use refined log-horizon data in the principal-mode manuscript figure."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT/'results'/name).open(newline='',encoding='utf8') as h:return list(csv.DictReader(h))
rows=read('kerr_scalar_principal_log_comparison_20261014.csv')
curves=read('kerr_scalar_principal_expanded_analytic_curves_20261014.csv')
plt.rcParams.update({'font.family':'serif','font.size':9})
fig,axes=plt.subplots(3,3,figsize=(7.1,6.1),constrained_layout=True)
colors={1:'#0072b2',2:'#d55e00',3:'#009e73'}
for i,m in enumerate((2,3,4)):
    for j,y in enumerate((-.5,.5,1)):
        ax=axes[i,j]
        for n in (1,2,3):
            line=[r for r in curves if int(r['m'])==m and int(r['n'])==n and float(r['y'])==y]
            points=[r for r in rows if int(r['m'])==m and int(r['n'])==n and float(r['y'])==y]
            ax.loglog([float(r['sigma']) for r in line],[float(r['F']) for r in line],color=colors[n],label=f'$n={n}$')
            ax.scatter([float(r['sigma']) for r in points],[float(r['F_spectral']) for r in points],s=22,edgecolors=colors[n],facecolors='white')
        ax.set_title(rf'$(\ell,m)=({m},{m}),\ y={y:g}$',fontsize=9)
        ax.grid(alpha=.2)
        if i==2:ax.set_xlabel(r'$\sigma=(r_+-r_-)/M$')
        if j==0:ax.set_ylabel(r'$\sigma^n\widehat\chi_n$')
handles,labels=axes[0,0].get_legend_handles_labels()
fig.legend(handles,labels,frameon=False,ncol=3,loc='upper center',bbox_to_anchor=(.5,1.055))
fig.savefig(ROOT/'figures/kerr_scalar_principal_log_refined_20261014.png',dpi=240,bbox_inches='tight')
plt.close(fig)
