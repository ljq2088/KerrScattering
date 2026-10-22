"""Copy immutable manuscript tables and bibliography into the new learning note."""
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'prd' / 'kerr_scalar_nonlinear_prd_review_20261007.tex'
text = SOURCE.read_text(encoding='utf-8')
captions = {
    'tab:angular-convergence': '角向离散审计：本征值和两个源投影相对于额外 24 个基与 512 点参考配置的最大相对变化。',
    'tab:axisymmetric-infrared': '三次轴对称红外解析系数及直接视界侧检验，$a/M=0.5$。最后一列比较两组谱阶和积分阶。',
    'tab:low-acceptance': '通过双边首阶能流门槛的低频展示区间、点数和最低点的实际结果。',
    'tab:low-convergence': '各多极最低展示点的独立参数审计：改变谱阶、积分阶或匹配半径，相对参考 $(256,256,40)$ 比较。',
    'tab:power-l0': '单极高次作用的解析常数、拟合指数、外推系数误差与双分辨率变化；固定 $y$ 为 $y=0.025$。',
    'tab:fit': '有限频率峰和指数尾的现象学拟合参数。QNM 为基本标量模，频率单位 $M=1$；$\\Delta T$ 是与 Hawking 温度的相对偏差。',
    'tab:tail-window': '移动指数尾拟合窗口后的有效温度范围、log 残差与温度偏差；不是无限高频误差界。',
    'tab:tail-models': '指数与幂律尾的同参数数目比较。正的 $\\Delta\\mathrm{AICc}$ 支持指数模型，LOO 为留一预测误差。',
    'tab:numerics': '轴对称扫描的保留点数和两种能流误差。低频及峰区 $q=192$，尾拟合 43 点 $q=2048$，谱阶均为 240。',
    'tab:production-convergence': '旧生产配置 $(224,160)$ 与当前峰区配置 $(240,192)$ 的相对变化。小守恒误差不代表两配置完全一致。',
    'tab:tail-convergence': '尾区独立积分阶及谱阶审计。积分阶比较 1792 与 2048；谱阶比较 224 与 240。',
    'tab:spin-limit': '固定 $(\\ell,m,M\\omega)=(2,0,0.52)$ 的 Kerr 到施瓦西连续性检查。',
    'tab:sourced20261008': '完整局域有源残差阶数扫描。A、B 为单极三次和五次作用，C 为非轴对称求解器探针；尾为最后八个重构系数的相对最大模。',
}
parts = []
for match in re.finditer(r'\\begin\{table\*?\}(.*?)\\end\{table\*?\}', text, re.S):
    block = match.group(1)
    label = re.search(r'\\label\{([^}]+)\}', block).group(1)
    body = re.search(r'(\\begin\{tabular\}.*?\\end\{tabular\})', block, re.S).group(1)
    caption = captions[label]
    parts.append('\\begin{table}[htbp]\n\\centering\n\\caption{' + caption + '}\n'
                 '\\label{note-' + label + '}\n'
                 '\\begin{adjustbox}{max width=\\textwidth}\n' + body + '\n\\end{adjustbox}\n\\end{table}\n')
assert len(parts) == len(captions) == 13
(HERE / 'kerr_scalar_learning_notes_zh_20261013_tables.tex').write_text('\n'.join(parts), encoding='utf-8')
bib = re.search(r'\\begin\{thebibliography\}.*?\\end\{thebibliography\}', text, re.S).group(0)
(HERE / 'kerr_scalar_learning_notes_zh_20261013_references.tex').write_text(bib + '\n', encoding='utf-8')
print(f'Extracted {len(parts)} unchanged numerical tables and {bib.count(chr(92) + "bibitem")} references.')
