"""Build an isolated, reference-style full notebook and its visual audit."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
NAME = 'kerr_scalar_complete_notes_zh_reference_verified_20261005'
SOURCE = ROOT / 'docs/notes/kerr_scalar_nonlinear_complete_notes_zh_20261005_v4.tex'
TARGET = ROOT / f'docs/notes/{NAME}.tex'
OUT = ROOT / 'output/pdf'
QA = ROOT / f'tmp/pdfs/{NAME}'
LATEX = Path(r'F:\texlive\texlive\2026\bin\windows\xelatex.exe')
REFERENCE = Path('F:/WechatFile/xwechat_files/wxid_3rjx22mjt1ka32_14c4/temp/'
                 'RWTemp/2026-10/458d4a8dbeb8d42b76b462e3130ef8e7/'
                 'Kerr_EMRI_解析与数值研究笔记_样式版_v3.pdf')


SUPPLEMENT = r'''
\section{关键解析步骤的逐项核算}
\label{sec:explicit-checks}
\subsection{径向能流：从张量到边界振幅}
令角函数包含 $e^{im\phi}$，并采用 $\int |S|^2\dd\Omega=1$。
在 Boyer--Lindquist 坐标中 $g^{rr}=\Delta/\Sigma$，
$g^{rt}=g^{r\phi}=0$。场取 $\Phi=R(r)S(\theta,\phi)e^{-i\omega t}$，故
\begin{align}
 \partial_t\Phi&=-i\omega\Phi,&
 \nabla^r\Phi&=\frac{\Delta}{\Sigma}R'Se^{-i\omega t},\\
 T^r{}_t
 &=\frac{i\omega\Delta}{\Sigma}|S|^2
       (R^*R'-R'^*R)
 =-\frac{2\omega\Delta}{\Sigma}|S|^2\Imm(R^*R').
\end{align}
由于 $\sqrt{-g}=\Sigma\sin\theta$，$\Sigma$ 恰好在角积分中抵消，得到
\begin{equation}
 \mathcal F_E^{\rm out}=\int\sqrt{-g}(-T^r{}_t)\dd\theta\dd\phi
 =2\omega\Delta\Imm(R^*R').
\end{equation}
无穷远取 $R=r^{-1}(C_{\rm in}e^{-i\omega r_*}
+C_{\rm ref}e^{i\omega r_*})+o(r^{-1})$。
入出波交叉项对 $\Imm(R^*R')$ 不贡献净流，且 $\Delta/r^2\to1$，因此
\begin{equation}
 \mathcal F_{E,\infty}^{\rm out}
 =2\omega^2(|C_{\rm ref}|^2-|C_{\rm in}|^2).
\end{equation}
视界取 $R=C_He^{-ipr_*}[1+O(r-r_+)]$，用 $\dd r_*/\dd r=H/\Delta$，得
\begin{equation}
 \mathcal F_{E,H}^{\rm out}=-2\omega pH_+|C_H|^2,
 \qquad \mathcal F_E^H=2\omega pH_+|C_H|^2.
\end{equation}
负的 $p$ 对应负的视界 Killing 能流，不是负概率。

三次相互作用下固定 $C_{\rm in}=\mathcal A_{\rm in}$，并使用
单位视界的齐次解及其源积分系数，有
\begin{align}
 C_H&=\frac{\mathcal A_{\rm in}}{B^{\rm inc}}
 \left[1+\epsilon|\mathcal A_{\rm in}|^2
       \frac{A_H^{(1)}}{|B^{\rm inc}|^2}\right]+O(\epsilon^2),\\
 C_{\rm ref}&=\frac{\mathcal A_{\rm in}}{B^{\rm inc}}
 \left[B^{\rm ref}+\epsilon|\mathcal A_{\rm in}|^2
       \frac{A_{\rm ref}^{(1)}}{|B^{\rm inc}|^2}\right]+O(\epsilon^2).
\end{align}
逐项展开平方模，再除以正入射流 $2\omega^2|\mathcal A_{\rm in}|^2$，即得
\begin{align}
 T^{(0)}&=\frac{pH_+}{\omega|B^{\rm inc}|^2},&
 T^{(1)}&=\frac{2pH_+}{\omega|B^{\rm inc}|^4}\Ree A_H^{(1)},\\
 R^{(0)}&=\frac{|B^{\rm ref}|^2}{|B^{\rm inc}|^2},&
 R^{(1)}&=\frac{2\Ree[(B^{\rm ref})^*A_{\rm ref}^{(1)}]}
 {|B^{\rm inc}|^4}.
\end{align}
实际修正还须乘 $\epsilon|\mathcal A_{\rm in}|^2$。
这四个式子的分母并非经验拟合，而是源的三次齐次性与边界模平方共同决定。
\textbf{一阶能流是干涉项；$|A_H^{(1)}|^2$ 属于二阶。}

\subsection{单极常数的积分：保留抵消再取极限}
低频单极的两个实积分为
\begin{equation}
 I_0=\int_0^\infty\frac{\sin^3x\cos x}{x^2}\dd x,
 \qquad J_0=\int_0^\infty\frac{\sin^4x}{x^2}\dd x.
\end{equation}
三角恒等式给出 $\sin^3x\cos x=\frac14\sin2x-\frac18\sin4x$。
先对完整组合分部积分，零点和无穷远边界项都消失：
\begin{align}
 I_0&=\frac12\int_0^\infty\frac{\cos2x-\cos4x}{x}\dd x,\\
 J_0&=\int_0^\infty\frac{\sin2x-\frac12\sin4x}{x}\dd x.
\end{align}
第一式不可拆成两个分别发散的余弦积分。
插入共同调节因子 $e^{-\eta x}$，$\eta>0$，并用
\begin{align}
 \int_0^\infty e^{-\eta x}\frac{\cos bx-\cos cx}{x}\dd x
 &=\frac12\ln\frac{\eta^2+c^2}{\eta^2+b^2},\\
 \int_0^\infty e^{-\eta x}\frac{\sin bx}{x}\dd x
 &=\arctan(b/\eta),\quad b>0,
\end{align}
随后令 $\eta\to0^+$，得到 $I_0=\ln2/2$、$J_0=\pi/4$。
从 $C_0=1/(4\pi)$ 和 $\rho_H=4C_0(I_0+iJ_0)$ 得到
\begin{equation}
 \rho_{H,00}(0)=\frac{\ln2}{2\pi}+\frac i4,
 \qquad \frac{T^{(1)}}{T^{(0)}}\longrightarrow\frac{\ln2}{\pi}.
\end{equation}
实部控制能流修正，虚部控制相位修正。以上极限固定 $|a|<M$、$m=0$；
不能直接作为固定 $p/\kappa$ 的近极端非轴对称结论。

\subsection{矩阵求解与精度：算法和物理端点不可混淆}
谱配点给出复线性系统 $\mathsf L\boldsymbol u=\boldsymbol b$。
精确算术中 $\mathsf L^{-1}\boldsymbol b$ 与分解后的线性求解相同，
两者不会改变微分方程、正则分支、视界归一化或能流定义。
有限精度下，应记录后向残差
\begin{equation}
 \eta_{\rm lin}=
 \frac{\|\mathsf L\boldsymbol u-\boldsymbol b\|}
 {\|\mathsf L\|\|\boldsymbol u\|+\|\boldsymbol b\|}.
\end{equation}
当 $\operatorname{cond}(\mathsf L)\eta_{\rm lin}\ll1$ 时，
线性代数的前向误差通常受 $O(\operatorname{cond}(\mathsf L)\eta_{\rm lin})$
控制；这并不包含微分方程的离散误差和 Green 求积误差。
直接 LU 或 QR 求解避免构造全部逆矩阵，便于行缩放和残差检查。
但不能只凭“曾经求逆”就认定低频或高频失败的唯一原因。

低频需要同时排查波区尺度 $r\sim\omega^{-1}$ 的解析度、
入射归一化的大幅度以及反射干涉的相消；高频需要排查剥离相位后的剩余函数、
导数矩阵误差和源积分的振荡解析度。中频往往没有极端尺度分离，
但是否准确仍须由独立残差、谱尾和求积扫描决定。
增加 $N$、显式求逆或更换匹配点，都不能修复错误的端点系数。
本笔记保留这些诊断层次，不把一个较小的代数残差当成完整物理误差。
'''


def build():
    old = SOURCE.read_text(encoding='utf8')
    new = old.replace(r'\LARGE\bfseries 黑洞标量场的',
                      r'\Huge\bfseries 黑洞标量场的')
    new = new.replace(r'\LARGE\bfseries 非线性散射',
                      r'\Huge\bfseries 非线性散射')
    new = new.replace(r'\large 从 Schwarzschild 到 Kerr',
                      r'\Large 从 Schwarzschild 到 Kerr')
    new = new.replace(r'\normalsize 解析推导、能流、谱方法与数值结果',
                      r'\large 解析推导、能流、谱方法与数值结果')
    new = new.replace('format=\\centering\\Large\\bfseries',
                      'format=\\centering\\large\\bfseries')
    new = new.replace('样式版 4.0\\quad 按用户确认的研究笔记版式重排',
                      '完整研究笔记\\quad 参考版式核验版')
    new = new.replace('内容与数据沿用已有工作；本次仅调整编排',
                      '补全关键解析步骤；数值沿用已有记录并保留验证边界')
    new = new.replace('正文先交代结果等级与审计，再逐步给出完整推导。',
                      '正文先交代结果等级与审计，再逐步给出完整推导。'
                      '本版保留 11 幅研究图、20 组数值审计表和 61 条参考文献；'
                      '额外展开能流交叉项、单极调节积分以及矩阵求解误差。')
    new = new.replace(r'\hypersetup{colorlinks=true,',
                      r'\hypersetup{pdfstartview=Fit,pdfpagemode=UseNone,'
                      r'pdfpagelayout=SinglePage,colorlinks=true,', 1)
    new = new.replace('\n\\appendix\n', SUPPLEMENT + '\n\\appendix\n', 1)
    for token in [r'\bibitem', r'\includegraphics', r'\caption{']:
        assert old.count(token) == new.count(token)
    labels = re.findall(r'\\label\{([^}]+)\}', new)
    assert len(labels) == len(set(labels))
    assert set(re.findall(r'\\label\{([^}]+)\}', old)) <= set(labels)
    TARGET.write_text(new, encoding='utf8')
    OUT.mkdir(exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    for run in range(3):
        result = subprocess.run(
            [str(LATEX), '-interaction=nonstopmode', '-halt-on-error',
             '-file-line-error', f'-output-directory={OUT}', str(TARGET)],
            cwd=TARGET.parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (QA / f'compile_{run + 1}.txt').write_bytes(result.stdout)
        if result.returncode:
            raise RuntimeError(result.stdout.decode('utf8', errors='replace')[-4000:])
    log = (OUT / f'{NAME}.log').read_text(encoding='utf8', errors='replace')
    bad = re.findall(r'(?:Overfull[^\n]*|Missing character[^\n]*|'
                     r'LaTeX Warning: (?:Reference|Citation)[^\n]*|'
                     r'There were undefined references[^\n]*)', log)
    assert not bad, bad
    print('Compiled:', OUT / f'{NAME}.pdf')
    audit(old, new)


def audit(old, new):
    doc = fitz.open(OUT / f'{NAME}.pdf')
    report = {'pages': len(doc), 'blank_pages': [], 'outside_page': [],
              'replacement_glyph_pages': [], 'unembedded_fonts': [],
              'figure_instances': 0, 'bibitems': new.count(r'\bibitem'),
              'audit_groups': len(re.findall(r'\\label\{audit:', new)),
              'source_sha256': hashlib.sha256(old.encode('utf8')).hexdigest()}
    seen = set()
    for i, page in enumerate(doc):
        text = page.get_text()
        if len(text.strip()) < 40:
            report['blank_pages'].append(i + 1)
        if '\ufffd' in text:
            report['replacement_glyph_pages'].append(i + 1)
        report['figure_instances'] += len(page.get_images())
        for font in page.get_fonts():
            if font[0] not in seen:
                seen.add(font[0])
                if not doc.extract_font(font[0])[3]:
                    report['unembedded_fonts'].append(font[3])
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    x0, y0, x1, y1 = span['bbox']
                    if min(x0, y0) < 0 or x1 > page.rect.width or y1 > page.rect.height:
                        report['outside_page'].append([i + 1, span['text']])
        page.get_pixmap(matrix=fitz.Matrix(0.6, 0.6)).save(QA / f'page_{i + 1}.png')
    for group in range((len(doc) + 11) // 12):
        sheet = Image.new('RGB', (1200, 1380), '#e6e6e6')
        draw = ImageDraw.Draw(sheet)
        for j in range(12):
            i = group * 12 + j
            if i >= len(doc):
                break
            im = Image.open(QA / f'page_{i + 1}.png')
            im.thumbnail((280, 410))
            x, y = (j % 4) * 300 + 10, (j // 4) * 460 + 24
            sheet.paste(im, (x, y))
            draw.text((x, y - 17), f'PDF {i + 1}', fill='black')
        sheet.save(QA / f'montage_{group + 1}.png')
    selected = {0, 1, 4, 16, 25, 34, 36, len(doc) - 2}
    for i, page in enumerate(doc):
        if '关键解析步骤的逐项核算' in page.get_text():
            selected.update(range(i, min(i + 4, len(doc))))
    for i in selected:
        doc[i].get_pixmap(matrix=fitz.Matrix(1.4, 1.4)).save(QA / f'detail_{i + 1}.png')
    ref = fitz.open(REFERENCE)
    for i in [0, 1, 4]:
        ref[i].get_pixmap(matrix=fitz.Matrix(1.2, 1.2)).save(QA / f'reference_{i + 1}.png')
    report['font_count'] = len(seen)
    for key in ['blank_pages', 'outside_page', 'replacement_glyph_pages', 'unembedded_fonts']:
        assert not report[key], (key, report[key])
    assert report['figure_instances'] == 11
    assert report['bibitems'] == 61
    assert report['audit_groups'] == 20
    (QA / 'qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf8')
    build()
