"""Apply the user-confirmed A4 article notebook style without changing results."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
old = (ROOT / 'docs/notes/kerr_scalar_nonlinear_complete_notes_zh_20261005_v3.tex').read_text(encoding='utf8')
header = old[:old.index(r'\begin{document}')]
header = header.replace('12pt,a4paper,oneside,openany]{ctexrep}', '11pt,a4paper,oneside]{ctexart}')
header = header.replace('left=24mm,right=24mm,top=23mm,bottom=23mm',
                        'left=23mm,right=23mm,top=22mm,bottom=22mm')
header = header.replace(r'\linespread{1.15}', r'\linespread{1.30}')
header = header.replace(r'\setlength{\parskip}{3pt}', r'\setlength{\parskip}{2pt}')
header = header.replace(r'\setcounter{tocdepth}{1}', r'\setcounter{tocdepth}{2}')
start = header.index(r'\ctexset{chapter=')
end = header.index(r'\pagestyle{fancy}', start)
header = header[:start] + r'''\ctexset{section={format=\centering\Large\bfseries,beforeskip=18pt,afterskip=10pt},
subsection={format=\normalsize\bfseries,beforeskip=12pt,afterskip=7pt}}
\numberwithin{equation}{section}
''' + header[end:]
header = header.replace(r'\fancyhead[L]{\small 从 Schwarzschild 到 Kerr}',
                        r'\fancyhead[L]{\small 黑洞标量场非线性散射}')
header = header.replace(r'\fancyhead[R]{\small 标量场非线性散射}',
                        r'\fancyhead[R]{\small 理论与数值笔记}')
header = header.replace('linkcolor=ink,citecolor=ink', 'linkcolor=blue!45!black,citecolor=blue!45!black')
cover = r'''\begin{document}
\hypersetup{pageanchor=false}
\begin{titlepage}\centering\vspace*{28mm}
{\small\color{ink} KERR SCATTERING NOTES\par}\vspace{18mm}
{\LARGE\bfseries 黑洞标量场的\par}\vspace{9mm}
{\LARGE\bfseries 非线性散射\par}\vspace{13mm}
{\large 从 Schwarzschild 到 Kerr\par}\vspace{8mm}
{\normalsize 解析推导、能流、谱方法与数值结果\par}\vspace{16mm}
\begin{minipage}{0.86\textwidth}\begin{note}
从作用量和背景几何出发，推导变量分离、散射基、非线性源投影、Green 函数及边界能流；整理低频、有限频率与近极端响应。解析恒等式、历史数值记录和待复核结果分别标明。本文只研究固定背景上的 $s=0$ 复标量场。
\end{note}\end{minipage}
\vfill{\normalsize 2026 年 10 月 5 日\par}\vspace{4mm}
{\small 样式版 4.0\quad 按用户确认的研究笔记版式重排\par}\vspace{2mm}
{\small 内容与数据沿用已有工作；本次仅调整编排\par}
\end{titlepage}
\hypersetup{pageanchor=true}\pagenumbering{arabic}
\section*{阅读说明与主要结论}
\addcontentsline{toc}{section}{阅读说明与主要结论}
本笔记完整整理 Schwarzschild 基准问题及其向 Kerr 标量场非线性散射的推广。正文沿着背景几何、线性散射、源投影、Green 函数、一阶能流和谱方法的逻辑展开，并补充低频匹配、高阶局域相互作用、超辐射阈值及近极端喉区分析。所有公式在本文件中编译显示，数值记录及原稿参考文献保留于正文和附录。
\begin{note}
\textbf{主要结论与适用边界。} 轴对称三次自通道的低频 $T^{(0)}$ 与 $T^{(1)}$ 同阶；单极相对响应趋于 $\ln2/\pi$，更高局域幂次在红外被压低。近极端非轴对称响应必须同时分析线性喉区强度和非线性 Green 核，不能由共形权重单独断言任意模态的幂律。现有非轴对称数据仍受正文无穷远端点一致性审计限制，保留历史证据身份，不能当作已复核的最终结论。
\end{note}
版式以用户新提供的中文研究笔记为准，仅参考其封面、标题层级、正文密度、页眉、目录和公式编号方式；该参考文件中的 EMRI 环境扰动物理不属于本项目，不作内容移植。正文先交代结果等级与审计，再逐步给出完整推导。
\tableofcontents
\clearpage
'''
body = old[old.index(r'\chapter{研究问题'):]
body = re.sub(r'\\chapter\{[^\n]*\}\n', '', body)
body = body.replace(r'\section*{符号与阅读方式}',
                    r'\section{完整数值审计}\label{sec:all-numerical-audits}' + '\n' + r'\subsection*{符号与阅读方式}')
body = body.replace(r'\addcontentsline{toc}{chapter}{参考文献}', r'\addcontentsline{toc}{section}{参考文献}')
body = body.replace(r'\fontsize{10.5}{14}', r'\fontsize{10}{13.5}')
body = body.replace('排版参照所提供的中文场论笔记；参考文件中的 Maxwell 场、带电标量与 Abelian--Higgs 模型不属于本项目，不能将其结果移植过来。',
                    '排版参照用户最终确认的中文研究笔记；参考文件中的 EMRI 环境扰动物理不属于本项目，不能将其结果移植过来。')
result = header + cover + body
assert r'\chapter' not in result
old_labels = set(re.findall(r'\\label\{([^}]+)\}', old))
new_labels = re.findall(r'\\label\{([^}]+)\}', result)
assert old_labels <= set(new_labels)
assert len(new_labels) == len(set(new_labels))
for token in [r'\bibitem', r'\includegraphics', r'\caption{']:
    assert old.count(token) == result.count(token)
target = ROOT / 'docs/notes/kerr_scalar_nonlinear_complete_notes_zh_20261005_v4.tex'
target.write_text(result, encoding='utf8')
print(target)
