"""Recompose the complete notebook as chapters with unscaled readable tables."""
from pathlib import Path
import re
import json

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'docs/notes/kerr_scalar_nonlinear_complete_notes_zh_20261005_v2.tex').read_text(encoding='utf8')
target = ROOT / 'docs/notes/kerr_scalar_nonlinear_complete_notes_zh_20261005_v3.tex'


def cells_and_rows(text):
    """Split TeX alignment tokens only outside brace groups."""
    rows, cells, chars = [], [], []
    depth, i = 0, 0
    while i < len(text):
        char = text[i]
        if char == '\\' and i + 1 < len(text):
            following = text[i + 1]
            if following == '\\' and depth == 0:
                cells.append(''.join(chars).strip())
                rows.append(cells)
                cells, chars = [], []
                i += 2
                continue
            if following in '{}&\\':
                chars.extend((char, following))
                i += 2
                continue
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
        elif char == '&' and depth == 0:
            cells.append(''.join(chars).strip())
            chars = []
            i += 1
            continue
        chars.append(char)
        i += 1
    assert depth == 0
    assert not ''.join(chars).strip(), ''.join(chars)
    return rows


def wrap_cell(cell):
    # Long parameter identifiers need a line break, not a smaller typeface.
    if cell.startswith('$') and cell.endswith('$') and ',\\ M\\omega' in cell:
        a, b = cell[1:-1].split(',\\ ', 1)
        return r'\shortstack{$' + a + r'$\\$' + b + '$}'
    return cell.replace('retained', '保留点数').replace('case', '参数点')


start = source.index(r'\section{阅读路线')
appendix_start = source.index(r'\appendix')
tables_start = source.index(r'\section{完整数值审计表的阅读方法}')
bib_start = source.index(r'\begin{thebibliography}')
body = source[start:appendix_start]
appendix = source[appendix_start:tables_start].replace(r'\appendix', '')
bibliography = source[bib_start:source.index(r'\end{thebibliography}') + len(r'\end{thebibliography}')]
body = re.sub(r'\\Needspace\{12\\baselineskip\}\\part\{[^\n]+\}\n', '', body)
body = re.sub(r'\\part\{[^\n]+\}\n', '', body)
body = body.replace(r'\clearpage', '')
chapters = {
    '阅读路线、结论等级与本次审计': '研究问题、约定与场论框架',
    'Schwarzschild 几何与线性变量分离': 'Schwarzschild：基准问题',
    'Kerr 几何和标量 Teukolsky 分离': 'Kerr：标量方程与能流',
    'Kerr 的端点包含两域 Chebyshev 方法': '端点谱方法与数值验证',
    '轴对称低频：静态解与波区解的完整匹配': '轴对称低频与有限频率谱',
    '超辐射阈值：能流与响应比值的不同极限': '超辐射阈值与近极端喉区',
    '更高局域幂次、有限带宽和响应峰迁移': '高阶响应与弱耦合层级',
    '文献背景、与原 Schwarzschild 工作的关系': '文献、实现与研究边界',
}
for section, chapter in chapters.items():
    key = r'\section{' + section + '}'
    assert body.count(key) == 1, section
    body = body.replace(key, '\\chapter{' + chapter + '}\n' + key)
body = body.replace('最后附上现稿全部 20 张数值表', '最后附上现稿全部 20 组数值审计表')
body = body.replace(r'\includegraphics[width=0.91\textwidth]',
                    r'\includegraphics[width=0.91\textwidth,height=0.40\textheight,keepaspectratio]')
body = body.replace(r'\begin{figure}[!htbp]', r'\begin{figure}[H]')
body = body.replace(r'\begin{table}[htbp]', r'\begin{table}[H]')
body = body.replace(
    '给出 $(2,2)$ 的 $y_{\\rm pk}=(0.887,0.980,1.027)$、$\\sigma_y=(0.307,0.236,0.205)$；$(3,3)$ 为 $(0.891,0.976,1.015)$、$(0.319,0.246,0.231)$。',
    r'''给出的峰位置和宽度为
\begin{equation}
\begin{aligned}
(2,2):\quad y_{\rm pk}&=(0.887,0.980,1.027),\\
\sigma_y&=(0.307,0.236,0.205),\\
(3,3):\quad y_{\rm pk}&=(0.891,0.976,1.015),\\
\sigma_y&=(0.319,0.246,0.231).
\end{aligned}
\end{equation}
''')
body = body.replace(
    '还要检查 $|\\epsilon_n||\\mathcal A_{\\rm in}|^{2n}|\\rho_H^{(n)}|\\ll1$、局域场修正和二阶余项；',
    r'''还要检查
\begin{equation}
|\epsilon_n||\mathcal A_{\rm in}|^{2n}|\rho_H^{(n)}|\ll1,
\end{equation}
以及局域场修正和二阶余项；''')
body = body.replace(
    '基本 QNM 为 $(0.1124-0.1022i,0.2979-0.0954i,0.4920-0.0946i)$。',
    r'''基本 QNM 依次为
\begin{align*}
\omega_{Q,0}&=0.1124-0.1022i,\\
\omega_{Q,1}&=0.2979-0.0954i,\\
\omega_{Q,2}&=0.4920-0.0946i.
\end{align*}
''')
body = re.sub(r'\$([^$\n]*)\$',
              lambda m: '$' + m.group(1).replace(',', r',\allowbreak ') + '$', body)

# Rebuild the audit appendix from its parsed rows, with explicit column groups.
original_tables = re.findall(
    r'\\captionof\{table\}\{([^\n]+)\}\\label\{([^}]+)\}.*?'
    r'\\begin\{tabular\}\{([^\n]+)\}\n(.*?)\\end\{tabular\}',
    source[tables_start:bib_start], re.S,
)
assert len(original_tables) == 20
table_blocks = []
audit_record = []
for index, (caption, label, spec, tabular) in enumerate(original_tables, 1):
    tabular = tabular.replace(r'\toprule', '').replace(r'\bottomrule', '')
    header, data = tabular.split(r'\midrule', 1)
    header_rows = cells_and_rows(header)
    rows = cells_and_rows(data)
    assert len(header_rows) == 1
    headers = header_rows[0]
    ncols = len(headers)
    assert all(len(row) == ncols for row in rows), (label, rows)
    identities = 3 if label.endswith('power-fit-quality') else 1
    if ncols >= 6:
        group_width = 2 if identities == 3 else 3
        groups = [list(range(identities)) + list(range(j, min(j + group_width, ncols)))
                  for j in range(identities, ncols, group_width)]
    else:
        groups = [list(range(ncols))]
    assert set(c for group in groups for c in group) == set(range(ncols))
    chunks = ['\\par\\addvspace{14pt}\\Needspace{14\\baselineskip}',
              '\\noindent\\begin{minipage}{\\linewidth}',
              '\\captionsetup{type=table}\\caption{' + caption + '}\\label{' + label + '}',
              '\\centering\\fontsize{10.5}{14}\\selectfont',
              '\\setlength{\\tabcolsep}{6pt}\\renewcommand{\\arraystretch}{1.2}']
    for group_index, columns in enumerate(groups):
        if len(groups) > 1:
            chunks.append('\\par\\smallskip{\\small\\color{ink} '
                          + chr(97 + group_index) + '：第 '
                          + '、'.join(str(c+1) for c in columns) + ' 列}\\par\\smallskip')
        chunks.append('\\begin{tabular}{' + 'c' * len(columns) + '}\\toprule')
        chunks.append(' & '.join(wrap_cell(headers[c]) for c in columns) + r'\\\midrule')
        for row in rows:
            chunks.append(' & '.join(wrap_cell(row[c]) for c in columns) + r'\\')
        chunks.append(r'\bottomrule\end{tabular}')
        if group_index + 1 < len(groups):
            chunks.append(r'\par\medskip')
    chunks.append(r'\end{minipage}\par\addvspace{10pt}')
    table_blocks.append('\n'.join(chunks))
    audit_record.append({'label': label, 'rows': len(rows), 'columns': ncols,
                         'column_groups': [[c+1 for c in group] for group in groups]})

preamble = r'''\documentclass[UTF8,fontset=fandol,12pt,a4paper,oneside,openany]{ctexrep}
\usepackage[left=24mm,right=24mm,top=23mm,bottom=23mm,headheight=16pt,headsep=8mm]{geometry}
\usepackage{amsmath,amssymb,bm,mathtools,booktabs,longtable,tabularx,array,multirow}
\usepackage{graphicx,xcolor,fancyhdr,enumitem,caption,float,xurl,needspace,placeins}
\usepackage[most]{tcolorbox}
\usepackage{hyperref,bookmark,etoolbox}
\definecolor{ink}{HTML}{18374B}\definecolor{pale}{HTML}{F0F5F8}
\hypersetup{colorlinks=true,linkcolor=ink,citecolor=ink,urlcolor=blue!45!black,
pdftitle={黑洞标量场非线性散射：从 Schwarzschild 到 Kerr},pdfauthor={}}
\setlength{\parindent}{2em}\setlength{\parskip}{3pt}
\linespread{1.15}\raggedbottom\emergencystretch=2em
\setlist{nosep,leftmargin=2em}
\setcounter{tocdepth}{1}\setcounter{secnumdepth}{2}
\ctexset{chapter={format=\LARGE\bfseries,beforeskip=0pt,afterskip=20pt},
section={format=\Large\bfseries,beforeskip=17pt,afterskip=8pt},
subsection={format=\large\bfseries,beforeskip=12pt,afterskip=6pt}}
\ctexset{chapter={break={\par\addvspace{22pt}\Needspace{10\baselineskip}},pagestyle=fancy}}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small 从 Schwarzschild 到 Kerr}
\fancyhead[R]{\small 标量场非线性散射}
\fancyfoot[C]{\small\thepage}\renewcommand{\headrulewidth}{0.3pt}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{\small\thepage}\renewcommand{\headrulewidth}{0pt}}
\newtcolorbox{note}{breakable,colback=pale,colframe=ink,boxrule=0.4pt,arc=0.8mm,
left=3mm,right=3mm,top=2mm,bottom=2mm,before skip=9pt,after skip=9pt}
\captionsetup{font={small},labelfont=bf,justification=raggedright,singlelinecheck=false,skip=8pt,hypcap=false}
\graphicspath{{../../figures/}}
\allowdisplaybreaks[2]
\AtBeginDocument{\setlength{\abovedisplayskip}{9pt plus 2pt minus 2pt}
\setlength{\belowdisplayskip}{9pt plus 2pt minus 2pt}
\setlength{\abovedisplayshortskip}{6pt plus 2pt minus 1pt}
\setlength{\belowdisplayshortskip}{6pt plus 2pt minus 1pt}}
\clubpenalty=10000\widowpenalty=10000
\setcounter{topnumber}{2}\setcounter{bottomnumber}{1}\setcounter{totalnumber}{3}
\renewcommand{\topfraction}{0.85}\renewcommand{\bottomfraction}{0.65}
\renewcommand{\textfraction}{0.13}\renewcommand{\floatpagefraction}{0.75}
\setlength{\textfloatsep}{16pt plus 2pt minus 2pt}
\setlength{\intextsep}{14pt plus 2pt minus 2pt}
\newcommand{\notefigure}[2]{\begin{figure}[H]\centering
\includegraphics[width=\textwidth,height=0.43\textheight,keepaspectratio]{#1}
\caption{#2}\end{figure}}
\newcommand{\calO}{\mathcal O}\newcommand{\DeltaK}{\Delta}\newcommand{\Res}{\mathcal R}
'''
macros = source[source.index(r'\newcommand{\dd}'):source.index(r'\begin{document}')]
cover = r'''\begin{document}
\hypersetup{pageanchor=false}
\begin{titlepage}\centering\vspace*{18mm}
{\small\color{ink} 完整研究笔记\par}\vspace{14mm}
{\Huge\bfseries 黑洞标量场\par}\vspace{5mm}
{\Huge\bfseries 非线性散射\par}\vspace{10mm}
{\LARGE 从 Schwarzschild 到 Kerr\par}\vspace{8mm}
{\large 解析推导、能流、谱方法与数值结果\par}\vspace{16mm}
\begin{minipage}{0.88\textwidth}\begin{note}
固定黑洞背景上的复标量场，$s=0$。从几何与作用量到散射振幅、Green 函数及边界能流，完整整理低频、有限频率和近极端问题。解析结论、数值记录与待复核结果分层标注。
\end{note}\end{minipage}
\vfill{\large 2026 年 10 月 5 日\par}\vspace{5mm}
{\small 第三版：分章重排、固定字号、宽表拆列\par}
\end{titlepage}
\hypersetup{pageanchor=true}\pagenumbering{Roman}
\tableofcontents\clearpage\pagenumbering{arabic}
'''
appendix_heading = r'''\appendix
\chapter{解析推导补充}
'''
table_heading = r'''\chapter{完整数值审计}
\section*{符号与阅读方式}
本附录保留原稿的全部 20 组数值。宽表拆成连续的列组，并重复参数标识；各组数据没有删列，也不通过缩小字体排入页面。$N$ 是每域谱阶数，$q$ 默认指内侧 Green 求积阶数。统计区间、分辨率差异与渐近模型误差须区别解释。所有非轴对称历史数据仍受正文端点一致性审计限制，不能因重排而提升结论等级。
'''
output = (preamble + macros + cover + body + appendix_heading + appendix
          + table_heading + '\n'.join(table_blocks)
          + '\\clearpage\\phantomsection\\addcontentsline{toc}{chapter}{参考文献}\n'
          + bibliography + '\n\\end{document}\n')
labels = re.findall(r'\\label\{([^}]+)\}', output)
assert len(labels) == len(set(labels))
refs = set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', output))
assert not refs - set(labels), refs - set(labels)
target.write_text(output, encoding='utf8')
(ROOT / 'tmp/pdfs/notes_v3_table_layout.json').write_text(
    json.dumps(audit_record, ensure_ascii=False, indent=2), encoding='utf8')
print(f'Wrote {target.name}; chapters={len(chapters)}; audit tables={len(table_blocks)}')
