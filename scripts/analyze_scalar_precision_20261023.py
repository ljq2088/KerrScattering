"""Verify archived inputs, compare resolutions, and typeset new scalar evidence."""
import csv
import hashlib
import json
from pathlib import Path, PureWindowsPath
import tomllib
import mpmath as mp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/precision_20261023'
mp.mp.dps = 150


def read(folder):
    manifest = json.loads((folder/'manifest.json').read_text(encoding='utf8'))
    assert manifest['status'] == 'completed'
    assert manifest['source_hashes_before'] == manifest['source_hashes_after']
    for path, sha in manifest['outputs'].items():
        path = Path(*PureWindowsPath(path).parts)
        assert hashlib.sha256((folder/path).read_bytes()).hexdigest() == sha, (folder, path)
    for path, sha in manifest['source_hashes_before'].items():
        path = Path(*PureWindowsPath(path).parts)
        candidates = [ROOT/path, *OUT.glob('source_*/'+Path(path).name)]
        assert any(p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==sha for p in candidates), path
    return tomllib.loads((folder/'solution/result.toml').read_text(encoding='utf8'))


def texnum(value, digits=7):
    value = mp.mpf(value)
    if value == 0:
        return '$0$'
    exponent = int(mp.floor(mp.log10(abs(value))))
    if -3 <= exponent <= 3:
        return '$'+mp.nstr(value,digits)+'$'
    return '$'+mp.nstr(value/mp.mpf(10)**exponent,digits)+r'\times10^{'+str(exponent)+'}$'


def main():
    all_data = {}
    for p in OUT.glob('*/manifest.json'):
        if json.loads(p.read_text(encoding='utf8'))['status'] == 'completed':
            all_data[p.parent.name] = read(p.parent)
    rows = []
    for name, coarse in sorted(all_data.items()):
        if not name.endswith('_coarse'):
            continue
        fine = all_data.get(name.replace('_coarse','_fine'))
        if name == 'power_l0_m0_w5_n2_coarse':
            fine = all_data.get('retry_power_l0_m0_w5_n2_fine', fine)
        if coarse['ell']==0 and coarse['omega'].startswith('10.') and coarse['n']==1:
            fine = all_data.get('integration_l0_m0_w10_n1_coarse', fine)
            fine = all_data.get('retry_l0_m0_w10_n1_fine', fine)
        if fine is None:
            continue
        f=lambda k:mp.mpf(fine[k])
        c=lambda k:mp.mpf(coarse[k])
        delta_chi=abs(f('chi')/c('chi')-1)
        delta_phase=abs(f('phase')/c('phase')-1)
        rho=mp.mpc(f('chi')/2,f('phase'));old=mp.mpc(c('chi')/2,c('phase'))
        delta_rho=abs(rho/old-1)
        linear=abs(f('T0')+f('R0')-1)
        jo=mp.mpc(fine['jo_re'],fine['jo_im'])
        saturation=f('bound_ratio')
        matching=fine['matching']
        br=[mp.mpc(r['br_re'],r['br_im']) for r in matching]
        spread=max(abs(v/br[2]-1) for v in br)
        accepted=(delta_chi<mp.mpf('1e-8') and delta_rho<mp.mpf('1e-10')
                  and f('radial_residual')<mp.mpf('1e-25')
                  and f('coefficient_tail')<mp.mpf('1e-20')
                  and spread<mp.mpf('1e-8')
                  and linear<mp.mpf('1e-25') and 0<=saturation<=1+mp.mpf('1e-10')
                  and abs(jo)<=f('jd')*(1+mp.mpf('1e-10')) and f('phase')>0)
        row=dict(case=name,ell=fine['ell'],m=fine['m'],n=fine['n'],omega=fine['omega'],
                 chi=fine['chi'],phase=fine['phase'],T0=fine['T0'],R0=fine['R0'],T1=fine['T1'],
                 paired_chi_change=str(delta_chi),paired_phase_change=str(delta_phase),paired_complex_change=str(delta_rho),
                 bound_ratio=str(saturation),linear_balance=str(linear),matching_Bref_spread=str(spread),
                 radial_residual=fine['radial_residual'],coefficient_tail=fine['coefficient_tail'],
                 rss_mb=fine['rss_mb'],accepted=accepted)
        rows.append(row)
    assert rows
    with (OUT/'comparison.csv').open('w',newline='',encoding='utf8') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary=dict(paired_cases=len(rows),accepted=sum(r['accepted'] for r in rows),
                 max_paired_chi_change=str(max(mp.mpf(r['paired_chi_change']) for r in rows)),
                 max_paired_phase_change=str(max(mp.mpf(r['paired_phase_change']) for r in rows)),
                 max_radial_residual=str(max(mp.mpf(r['radial_residual']) for r in rows)),
                 max_matching_Bref_spread=str(max(mp.mpf(r['matching_Bref_spread']) for r in rows)),
                 max_coefficient_tail=str(max(mp.mpf(r['coefficient_tail']) for r in rows)),
                 max_rss_mb=max(r['rss_mb'] for r in rows),
                 max_bound_ratio=str(max(mp.mpf(r['bound_ratio']) for r in rows)),
                 source_sha256=hashlib.sha256((ROOT/'src/kerr_scalar_precision.jl').read_bytes()).hexdigest(),
                 interpretation='Paired numerical convergence with original-equation residuals; external high-precision scalar benchmark pending.')
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
    text=[r'\subsection{参数、精度与证据范围}',
          '新计算统一采用 $a=0.5$、固定入射归一化。粗细两档分别使用 320/384 bit，',
          '内区阶数 64/80、外区阶数 48/64，积分阶数和 Levin 阶数独立提高。',
          f'当前共有 {len(rows)} 个配对参数点，其中 {summary["accepted"]} 个通过预设接受门槛。',
          '表中数字展示物理尺度；完整有效数字及逐项误差保存在 CSV 和 TOML 中。',
          r'\begin{longtable}{rrrrrr}',
          r'\caption{新标量非线性散射结果。$m=0$；$\mathcal S=|\chi|/[2\psi\sqrt{R^{(0)}/(1-R^{(0)})}]$。}\\',
          r'\toprule $\ell$ & $n$ & $\omega$ & $\chi_n$ & $\psi_n$ & $\mathcal S$\\\midrule\endfirsthead',
          r'\toprule $\ell$ & $n$ & $\omega$ & $\chi_n$ & $\psi_n$ & $\mathcal S$\\\midrule\endhead']
    for r in sorted(rows,key=lambda r:(float(r['omega']),r['ell'],r['n'])):
        text.append(' & '.join([str(r['ell']),str(r['n']),texnum(r['omega']),texnum(r['chi']),texnum(r['phase']),texnum(r['bound_ratio'],3)])+r'\\')
    text += [r'\bottomrule\end{longtable}',r'\subsection{数值质量}',
             '最大配对能流响应变化为 '+texnum(summary['max_paired_chi_change'])+'，',
             '最大配对相位变化为 '+texnum(summary['max_paired_phase_change'])+'。',
             '最高采样径向残差为 '+texnum(summary['max_radial_residual'])+'。',
             '最大谱尾指标为 '+texnum(summary['max_coefficient_tail'])+'，',
             '五点匹配半径下的最大反射振幅相对展宽为 '+texnum(summary['max_matching_Bref_spread'])+'。',
             f'成功配对运行记录中的最大进程峰值内存约为 {summary["max_rss_mb"]:.0f} MB。',
             '该组精度陈述对应独立加密的一致性和离节点原方程检查；外部高精度标量参考列为待完成检验。',
             r'\begin{figure}[htbp]\centering\includegraphics[width=.98\textwidth]{../../results/precision_20261023/response_summary.png}',
             r'\caption{新高精度标量结果。左：单极子三次响应的相位系数；右：各已配对点的不等式饱和比。}\end{figure}']
    (OUT/'note_tables.tex').write_text('\n'.join(text)+'\n',encoding='utf8')
    plt.rcParams.update({'font.size':10})
    fig,axes=plt.subplots(1,2,figsize=(10,3.8),layout='constrained')
    mono=sorted([r for r in rows if r['ell']==0 and r['n']==1 and float(r['omega'])>=1],key=lambda r:float(r['omega']))
    axes[0].plot([float(r['omega']) for r in mono],[float(r['phase']) for r in mono],'o-',label='spectral, paired')
    axes[0].axhline(1/96,color='k',ls='--',label='leading polar/WKB prediction')
    axes[0].set(xlabel=r'$M\omega$',ylabel=r'$\psi_1$',title=r'$a/M=0.5,\ \ell=m=0$');axes[0].legend(fontsize=8)
    axes[1].semilogy(range(len(rows)),[float(r['bound_ratio']) for r in rows],'o')
    axes[1].axhline(1,color='k',ls='--');axes[1].set(xlabel='paired case index',ylabel='bound saturation',title='Flux-phase inequality')
    for ax in axes:ax.grid(alpha=.25)
    fig.savefig(OUT/'response_summary.png',dpi=170);plt.close(fig)
    angular_path=OUT/'angular_wkb_refined.toml'
    if angular_path.exists():
        audit=json.loads(angular_path.with_suffix('.manifest.json').read_text())
        assert audit['status']=='completed' and audit['source_hashes_before']==audit['source_hashes_after']
        assert hashlib.sha256(angular_path.read_bytes()).hexdigest()==audit['output_sha256']
        angular=tomllib.loads(angular_path.read_text())['rows']
        angular_change=max(mp.mpf(v['angular_refinement_change']) for v in angular)
        wkb=[r'\begin{table}[htbp]\centering',r'\caption{$\omega=10$ 的完整谱相位与精确角积分加领先径向 WKB。}',
             r'\begin{tabular}{rrrr}\toprule $n$ & $\psi_n$ & $\psi_n^{\rm ang+WKB}$ & 相对差\\\midrule']
        for n in (1,2,3):
            matching=[r for r in rows if r['ell']==0 and r['n']==n and mp.mpf(r['omega'])==10]
            if matching:
                r=matching[0]; estimate=next(v for v in angular if v['n']==n and mp.mpf(v['omega'])==10)
                approx=mp.mpf(estimate['phase_finite_angular_wkb'])
                wkb.append(' & '.join([str(n),texnum(r['phase']),texnum(approx),texnum(abs(approx/mp.mpf(r['phase'])-1))])+r'\\')
        wkb += [r'\bottomrule\end{tabular}\end{table}',
                '角向独立检查取 $n=1,2,3$，频率依次为 $\\omega=1,2,3,5$ 及 $10,20,50,100$。',
                '球谐截断从 48 提至 64，最高两个频率从 96 提至 112；',
                '角向积分最大相对变化为 '+texnum(angular_change)+'。',
                '$\\omega=100$ 时，三个 $C_0^{(n)}$ 与领先极区近似之比分别为 $0.98987,0.97986,0.96996$。',
                '该延伸检查仅计算角向问题；完整径向非线性结果的最高频率为 $\\omega=10$。']
        (OUT/'wkb_tables.tex').write_text('\n'.join(wkb)+'\n',encoding='utf8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
