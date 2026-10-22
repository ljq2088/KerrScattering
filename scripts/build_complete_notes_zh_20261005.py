"""Compose the dated Chinese notebook without modifying the source manuscripts."""
from pathlib import Path
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--revised-layout', action='store_true')
args = parser.parse_args()

ROOT = Path(__file__).resolve().parents[1]
old = (ROOT / 'docs/notes/schwarzschild_to_kerr_nonlinear_scattering_zh.tex').read_text(encoding='utf-8')
paper = (ROOT / 'docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex').read_text(encoding='utf-8')
additions = (ROOT / 'docs/notes/complete_notes_20261005_additions.tex').read_text(encoding='utf-8')
macros = old[old.index('\\newcommand{\\dd}'):old.index('\\title{')]
core = old[old.index('\\section{问题、目标与逻辑链}'):old.index('\\part{当前数值实验与物理解读}')]
core = core.replace('B_1(0)=-2\\ii\\sigma r_+\\omega,\n\\qquad B_0(0)=-\\lambda.',
                    'B_1(0)=-2\\ii\\sigma r_+\\omega,\n\\qquad B_0(0)=-(\\lambda+2am\\omega).')
core = core.replace('u_z(0)-\\lambda u(0)=0.', 'u_z(0)-(\\lambda+2am\\omega)u(0)=0.')
core = core.replace('高频生产计算将远区尾阶数推进到 $q=2048$', '高频生产计算将紧致视界侧求积阶数推进到 $q=2048$')
core = core.replace('这说明当前主要误差预算来自远区积分，而不是齐次谱解。',
                    '这说明该频段的主要误差预算来自紧致视界侧 Green 求积，而不是齐次谱解。')
core = core.replace('显式矩阵逆在两端频率尤其差，原因包括：',
                    '显式矩阵逆和直接求解都面临两端频率的病态，数值差异应结合以下因素分析：')
intro, rest = additions.split('\\clearpage\n\\section{轴对称低频', 1)
rest = '\\clearpage\n\\part{低频、完整数值结果与近极端解释}\n\\section{轴对称低频' + rest

preamble = r'''\documentclass[UTF8,fontset=fandol,11pt,a4paper]{ctexart}
\usepackage[margin=23mm,headheight=15pt]{geometry}
\usepackage{amsmath,amssymb,bm,mathtools,booktabs,longtable,tabularx,array,multirow}
\usepackage{xcolor,graphicx,fancyhdr,enumitem,hyperref,tcolorbox,xurl,caption,float}
\definecolor{ink}{HTML}{18374B}
\definecolor{pale}{HTML}{F0F5F8}
\hypersetup{colorlinks=true,linkcolor=blue!45!black,urlcolor=blue!50!black,citecolor=green!35!black,
pdftitle={从 Schwarzschild 到 Kerr：标量场非线性散射完整研究笔记},pdfauthor={}}
\setlength{\parindent}{2em}\setlength{\parskip}{4pt}
\setlist{nosep,leftmargin=2em}\numberwithin{equation}{section}
\setcounter{tocdepth}{2}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small Schwarzschild 与 Kerr 标量非线性散射}
\fancyhead[R]{\small 理论与数值笔记}
\fancyfoot[C]{\small\thepage}\renewcommand{\headrulewidth}{0.3pt}
\newtcolorbox{note}{colback=pale,colframe=ink,boxrule=0.4pt,arc=1mm,left=3mm,right=3mm,top=2mm,bottom=2mm}
\allowdisplaybreaks[2]\emergencystretch=2em
\graphicspath{{../../figures/}}
\captionsetup{font=small,labelfont=bf}
\newcommand{\notefigure}[2]{\begin{figure}[htbp]\centering
\includegraphics[width=0.98\textwidth,height=0.64\textheight,keepaspectratio]{#1}\caption{#2}\end{figure}\FloatBarrier}
\usepackage{placeins}
\newcommand{\calO}{\mathcal O}\newcommand{\DeltaK}{\Delta}\newcommand{\Res}{\mathcal R}
'''
cover = r'''\begin{document}
\begin{titlepage}\centering\vspace*{21mm}
{\small\color{ink} KERRSCATTERING RESEARCH NOTES\par}
\vspace{12mm}
{\Huge\bfseries 从 Schwarzschild 到 Kerr\par}
\vspace{7mm}
{\Huge\bfseries 标量场非线性散射\par}
\vspace{9mm}
{\Large 完整解析推导、能流与谱方法\par}
\vspace{6mm}
{\large 低频匹配、局域幂次与近极端喉区\par}
\vspace{17mm}
\begin{minipage}{0.88\textwidth}\begin{note}
从作用量和黑洞几何出发，推导齐次散射基、非线性源、Green 函数与固定入射能流；记录全部主要数值工作及精度审计。物理范围仅为固定背景上的复标量 $s=0$。近极端非轴对称历史结果同时标注本次发现的端点一致性复核要求。
\end{note}\end{minipage}
\vfill{\large 2026 年 10 月 5 日\par}
\vspace{6mm}{\small 基于当前英文稿件与项目产物整理；不覆盖原稿\par}
\end{titlepage}
\tableofcontents\clearpage
'''
captions = [
 '轴对称红外解析系数与复视界振幅检验。',
 '不同可观测量的最低接受频率和精度门槛。',
 '轴对称低频的配对分辨率检验。',
 '单极高阶局域非线性的低频幂和解析系数。',
 '轴对称共振峰、QNM 比较及描述性宽度。',
 '高频有限窗指数拟合与缩窗漂移。',
 '指数模型、幂律模型及固定热斜率的比较。',
 '代表性谱尾、离网残差和能流误差。',
 '生产分辨率的谱阶数与匹配半径稳定性。',
 '高频 Green 求积阶数和谱阶数的独立比较。',
 '配对分辨率及算符残差的汇总。',
 '角向球谐截断与 Gauss 求积的独立检验。',
 '非线性目标角通道及选择定则结果。',
 '历史超辐射阈值响应与能流斜率，待端点修正重算。',
 '历史近极端三次阈值响应，待端点修正重算。',
 '历史线性强度、非线性 Green 核和总响应的有效幂分解，待复核。',
 '历史高阶局域幂的模态层级和路径比较，待复核。',
 '历史 principal 模七点幂律拟合审计，待复核。',
 '轴对称单极零频外推及解析常数的跨自旋检验。',
 '旋转趋零与 Schwarzschild 的归一化连续性比较。',
]
tables = re.findall(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', paper, flags=re.S)
assert len(tables) == len(captions), len(tables)
audit = []
for idx, (table, caption) in enumerate(zip(tables, captions), 1):
    body = re.search(r'\\begin\{tabular\}.*?\\end\{tabular\}', table, re.S)
    if not body:
        raise ValueError(f'No tabular in {idx}')
    label = re.search(r'\\label\{([^}]+)\}', table).group(1)
    # Preserve numerical rows verbatim; adapt only the surrounding layout.
    audit.append('\\begin{table}[htbp]\n\\centering\\small\n'
                 + '\\caption{' + caption + '}\\label{audit:' + label + '}\n'
                 + '\\resizebox{\\textwidth}{!}{%\n' + body.group(0) + '}\n'
                 + '\\end{table}\n\\FloatBarrier\n')
    if idx % 3 == 0:
        audit.append('\\clearpage\n')
bib = paper[paper.index('\\begin{thebibliography}'):paper.index('\\end{thebibliography}') + len('\\end{thebibliography}')]
text = preamble + macros + cover + intro + '\\clearpage\n' + core + rest + '\n'.join(audit) + '\\clearpage\n' + bib + '\n\\end{document}\n'
labels = set(re.findall(r'\\label\{([^}]+)\}', text))
references = set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', text))
keys = set(re.findall(r'\\bibitem\{([^}]+)\}', text))
cites = set(k for group in re.findall(r'\\cite\{([^}]+)\}', text) for k in group.split(','))
assert not references - labels, sorted(references - labels)
assert not cites - keys, sorted(cites - keys)
target = ROOT / 'docs/notes/kerr_scalar_nonlinear_complete_notes_zh_20261005.tex'
if args.revised_layout:
    # Keep the original edition intact while correcting its layout defaults.
    target = target.with_name(target.stem + '_v2.tex')
    text = text.replace(r'\setcounter{tocdepth}{2}', r'\setcounter{tocdepth}{1}')
    text = text.replace(r'\usepackage{placeins}', r'''\usepackage{placeins,adjustbox,needspace}
\raggedbottom
\setcounter{topnumber}{3}\setcounter{bottomnumber}{2}\setcounter{totalnumber}{5}
\renewcommand{\topfraction}{0.92}\renewcommand{\bottomfraction}{0.85}
\renewcommand{\textfraction}{0.08}\renewcommand{\floatpagefraction}{0.78}
\setlength{\textfloatsep}{14pt plus 2pt minus 2pt}
\setlength{\intextsep}{12pt plus 2pt minus 2pt}
\captionsetup{justification=raggedright,singlelinecheck=false,skip=6pt,hypcap=false}
\ctexset{section={format=\Large\bfseries,beforeskip=18pt,afterskip=9pt},
subsection={format=\large\bfseries,beforeskip=13pt,afterskip=6pt}}
''')
    text = text.replace(r'\end{figure}\FloatBarrier}', r'\end{figure}}')
    text = text.replace(r'\begin{figure}[htbp]', r'\begin{figure}[!htbp]')
    text = text.replace('height=0.64\\textheight', 'height=0.49\\textheight')
    # Clear pages belong to major divisions, not every third audit table.
    start = text.index(r'\section{完整数值审计表的阅读方法}')
    end = text.index(r'\begin{thebibliography}')
    tablepart = text[start:end]
    tablepart = tablepart.replace('原始表头保留英文便于对照', '表头统一为中文，物理符号与数值保留原始约定')
    tablepart = tablepart.replace(r'\FloatBarrier', '').replace(r'\clearpage', '')
    tablepart = tablepart.replace(r'\begin{table}[htbp]',
        r'\par\addvspace{12pt}\Needspace{11\baselineskip}\noindent\begin{minipage}{\linewidth}')
    tablepart = tablepart.replace(r'\centering\small',
        r'\centering\fontsize{9.5}{12}\selectfont\setlength{\tabcolsep}{3pt}\renewcommand{\arraystretch}{1.18}')
    tablepart = tablepart.replace(r'\caption{', r'\captionof{table}{')
    tablepart = tablepart.replace('\\resizebox{\\textwidth}{!}{%\n',
        '\\begin{adjustbox}{max width=\\linewidth}\n')
    tablepart = tablepart.replace(r'\end{tabular}}', r'\end{tabular}\end{adjustbox}')
    tablepart = tablepart.replace(r'\end{table}', r'\end{minipage}\par\addvspace{9pt}')
    header_translations = {
        'fixed-$\\omega$ fitted power': r'\shortstack{固定 $\omega$\\拟合幂}',
        'fixed-$y$ $\\kappa$ power': r'\shortstack{固定 $y$\\$\kappa$ 幂}',
        'max. coefficient error': r'\shortstack{最大系数\\相对偏差}',
        'max. $\\delta_N\\chi_H$': r'$\max\delta_N\chi_H$',
        'predicted power': '解析幂',
        'displayed $M\\omega$ range': r'$M\omega$ 展示窗',
        'lowest $M\\omega$': r'最低 $M\omega$',
        'relative analytic error': '解析相对偏差',
        'maximum resolution change': '最大阶数变化',
        'numerical class': '数值分类',
        'drifting slope': '漂移斜率',
        'weak crossover': '弱交叉',
        'locked envelope': '锁定包络',
        '95\\% interval': r'95\% 区间',
        'LOO max': '留一误差',
        'baseline ': '基准 ',
        'range of ': '范围：',
        'points': '点数',
        'path': '路径',
        'setting': '设置',
        'active ': '生产 ',
        'basis ': '基底 ',
        'quadrature ': '求积 ',
        'control': '对照',
        'enhanced crossover': '增强交叉',
        'near-flat crossover': '近平台交叉',
        'numerical trend': '数值趋势',
        'drifting crossover': '漂移交叉',
        'finite-limit favored': '偏向有限极限',
        ' envelope': ' 包络',
        '(envelope)': '(包络)',
        'max. ': '最大 ',
    }
    for source, translation in header_translations.items():
        tablepart = tablepart.replace(source, translation)
    # Restore three-line rules removed with the original revtex wrapper.
    tablepart = re.sub(r'(\\begin\{tabular\}\{[^\n]+\}\n)',
                       r'\1\\toprule\n', tablepart)
    tablepart = tablepart.replace(r'\hline', r'\midrule')
    tablepart = tablepart.replace(r'\end{tabular}', r'\bottomrule\end{tabular}')
    text = text[:start] + tablepart + '\\clearpage\n' + text[end:]
    text = text.replace(r'\tableofcontents\clearpage',
        r'\pagenumbering{Roman}\tableofcontents\clearpage\pagenumbering{arabic}')
    # Keep each major division visually anchored to its opening material.
    text = re.sub(r'\\part\{([^}]+)\}',
        r'\\Needspace{12\\baselineskip}\\part{\1}', text)
target.write_text(text, encoding='utf-8')
print(f'Wrote {target}; {len(text)} characters; {len(tables)} source tables; {len(keys)} bibliography entries')
