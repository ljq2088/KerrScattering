# Principal 模态与非线性近极端幂律

## 命题与适用范围

研究对象为固定 Kerr 背景上的复标量场，方程为

\[
\Box\Phi+\epsilon_n|\Phi|^{2n}\Phi=0,\qquad n\ge1.
\]

保持入射振幅、\(m>0\) 和 \(y=(\omega-m\Omega_H)/\kappa\ne0\) 固定，并取近极端极限。径向解采用单位视界入射归一化，角函数采用单位积分归一化。本文讨论自通道的一阶响应系数

\[
\widehat\chi_n=M^{2n-2}\frac{T_n^{(1)}}{T^{(0)}}.
\]

定义 \(\sigma=(r_+-r_-)/M\)。当 \(M\kappa\to0\) 时，\(\sigma=4M\kappa[1+o(1)]\)。若临界频率处的喉部权重为 \(h=1/2+i\beta\)，\(\beta>0\)，则首阶匹配给出

\[
\widehat\chi_n=\sigma^{-n}\mathcal F_n(y,\beta\ln\sigma)+o(\sigma^{-n}).
\]

结论覆盖连接分母有界离零的参数区间。\(\mathcal F_n\) 为下述收敛 Green 积分和解析连接系数确定的函数。其零点决定领先能流干涉项的消失位置。领先包络的指数为 \(-n\)，对数相位依赖来自两条复权重支解的干涉。

## 喉部方程与权重

本节取 \(M=1\)，设 \(\delta=r_+-r_-\)、\(X=(r-r_+)/\delta\)、\(p=y\kappa\)。径向方程为

\[
\frac{d}{dr}\left(\Delta\frac{dR}{dr}\right)+\left(\frac{K^2}{\Delta}-\lambda\right)R=0,
\quad K=(r^2+a^2)\omega-am.
\]

由于 \(\Delta=\delta^2X(X+1)\) 且 \((r_+^2+a^2)p=\delta y/2\)，极限方程为

\[
\mathcal L_{\rm NH}f\equiv\frac{d}{dX}\left[X(X+1)\frac{df}{dX}\right]
+\left[\frac{(mX+y/2)^2}{X(X+1)}-\lambda_*\right]f=0.
\]

临界频率为 \(\omega_*=m/2\)，\(\lambda_*=A_{\ell m}(m/2)-3m^2/4\)。重叠区指标满足

\[
h(h-1)+m^2-\lambda_*=0,
\qquad h=\frac12+\sqrt{\frac14+A_{\ell m}(m/2)-\frac{7m^2}{4}}.
\]

本文的 \(h\) 是喉部方程的指标。MST 的重整化角动量 \(\nu\) 由全频率三项递推决定；本计算实施近极端首阶的超几何与 Whittaker 连接。

## 解析近区解与连接系数

单位视界近区解为

\[
f_y(X)=X^{-iy/2}(1+X)^{i(y/2-m)}
{}_2F_1(h-im,1-h-im;1-iy;-X).
\]

其重叠区行为为 \(f_y\sim c_+X^{h-1}+c_-X^{-h}\)，其中

\[
c_+=\frac{\Gamma(1-iy)\Gamma(2h-1)}
{\Gamma(h-im)\Gamma[h-i(y-m)]},\qquad
c_-=\frac{\Gamma(1-iy)\Gamma(1-2h)}
{\Gamma(1-h-im)\Gamma[1-h-i(y-m)]}.
\]

极端外区令 \(u=r-1\)，径向方程为

\[
u^2R''+2uR'+[m^2(1+u/2)^2-\lambda_*]R=0.
\]

归一化为 \(u^{h-1}\)、\(u^{-h}\) 的两支 Whittaker 解具有入射系数

\[
U_+=\frac{\Gamma(2h)}{\Gamma(h-im)}(-im)^{-h-im},\qquad
U_-=\frac{\Gamma(2-2h)}{\Gamma(1-h-im)}(-im)^{h-1-im}.
\]

两式共享一个模为一的 tortoise 坐标相位。该相位在本研究的模平方及响应系数中消去。近远区连接给出

\[
B^{\rm inc}=c_+U_+\delta^{1-h}+c_-U_-\delta^h+o(\delta^{1/2})
=\delta^{1/2}\mathcal D(\theta)+o(\delta^{1/2}),
\]
\[
\theta=\beta\ln\delta,\qquad
\mathcal D(\theta)=c_+U_+e^{-i\theta}+c_-U_-e^{i\theta}.
\]

因此固定入射的视界振幅平方具有 \(\delta^{-1}|\mathcal D|^{-2}\) 标度。principal 条件 \(\operatorname{Re}h=1/2\) 决定这一实幂次，\(\operatorname{Im}h=\beta\) 决定相位周期。

## 非线性 Green 积分与指数

记 \(\psi_+\sim X^{h-1}\)、\(\psi_-\sim X^{-h}\) 为近区两支解。外区单位出射解的重叠系数为

\[
g_+=\frac{\Gamma(1-2h)}{\Gamma(1-h-im)}(-im)^h,\qquad
g_-=\frac{\Gamma(2h-1)}{\Gamma(h-im)}(-im)^{1-h}.
\]

对 principal 模态，出射解的近区形式为 \(R_{\rm up}\sim\delta^{-1/2}\gamma_\theta(X)\)，其中

\[
\gamma_\theta=g_+e^{i\theta}\psi_++g_-e^{-i\theta}\psi_-.
\]

物理 Wronskian 为 \(W\sim\delta^{1/2}w_\theta\)，且
\(w_\theta=X(X+1)(f_y\gamma_\theta'-\gamma_\theta f_y')\)。源权重在视界极限为 \(C_H^{(n)}=C^{(0,n)}+C^{(2,n)}\)。由于 \(dr=\delta\,dX\)，单位视界一阶系数的首项为

\[
\mathcal A_n(\theta)=-\frac{C_H^{(n)}}{w_\theta}
\int_0^\infty\gamma_\theta(X)|f_y(X)|^{2n}f_y(X)\,dX.
\]

在大 \(X\) 区间，\(|f_y|\) 与 \(|\gamma_\theta|\) 的包络均为 \(X^{-1/2}\)，故被积函数包络为 \(X^{-n-1}\)。对每个正整数 \(n\)，积分在无穷上限收敛；视界端的振幅包络有限，积分同样收敛。

结合固定入射归一化，得到显式系数函数

\[
\widehat\chi_n=\delta^{-n}
\frac{2\operatorname{Re}\mathcal A_n(\theta)}{|\mathcal D(\theta)|^{2n}}
+o(\delta^{-n}).
\]

变换 \(\theta\mapsto\theta+\pi\) 同时改变 \(\gamma\)、\(w\) 和 \(\mathcal D\) 的符号，保留 \(\mathcal A_n\) 与 \(|\mathcal D|\)。因此领先系数对 \(\ln\delta\) 的周期为 \(\pi/\beta\)。

## 实权重模态的匹配条件

对实 \(h>1/2\) 且非退化的主连接系数，固定入射近区场具有 \(\delta^{h-1}\) 标度。领先 Green 核的下降支在重叠区给出积分包络

\[
X^{2n(h-1)-1}.
\]

当 \(1/2<h<1\) 时，这一积分在大 \(X\) 收敛，喉部响应的候选领先幂为 \(\delta^{2n(h-1)}\)。当 \(h>1\) 时，匹配上限 \(X_{\rm match}\sim\delta^{-1}\) 贡献一个 \(\delta^{-2n(h-1)}\) 因子，抵消局部计数中的正幂；完整外区匹配决定量级为一的贡献。临界 \(h=1\) 的上端积分产生对数结构。各类完整首项系数的判定需要保留相应连接项与积分项。

本次角本征值计算给出 \(h_{11}=1.1706059743\)、\(h_{22}=1/2+0.9459584692i\)、\(h_{33}=1/2+1.9378354020i\)。实权重对照采用 \((1,1)\)，principal 数值验证采用 \((2,2)\)。

## 独立数值验证

完整 Kerr 谱求解采用修正后的无穷远端点和代数分解系数。参数为 \(y=0.5\)、\(n=1,2\)，自旋覆盖 0.99 至 0.9999999。两组主扫描采用 \((N,q)=(256,1024),(320,1536)\)；高自旋加密采用 \((384,2048),(448,3072)\)。解析预测的拟合参数数目为零。

| a/M | n | 谱响应 | 解析首阶响应 | 相对差异 |
|---|---:|---:|---:|---:|
| 0.999999 | 1 | 76.277602 | 76.906770 | 0.825% |
| 0.999999 | 2 | 1967.775232 | 1986.739546 | 0.964% |

表中谱值来自 N=320 的主扫描，两个点均满足双边界绝对能流平衡误差小于 1e-8。a/M=0.9999999 的视界响应检查中，两阶解析差异降至约 0.281%、0.327%，分辨率响应变化分别约 9.0e-6、1.7e-6；这些加密点的双边界绝对误差另行记录。

在 a/M=0.999999、N=320 处，齐次解 600 个离网格点的最大径向相对残差约为 3.2e-9，外区相对系数尾部约为 2.1e-14。近区超几何解和临界外区 Whittaker 解分别通过独立 ODE 检查。每次完整求解后的工作集内存约为 79 MB。

## 物理含义与后续检验

principal 模态的固定入射视界场密度具有 \((M\kappa)^{-1}\) 包络。\(|\Phi|^{2n}\) 将这一增强提升至第 n 次幂，产生 \((M\kappa)^{-n}\) 的相对非线性响应。固定实幂由 Re h 决定，对数调制由 Im h 和近远区连接共同决定。

定义无量纲耦合 \(g_n=\epsilon_n/M^{2n-2}\)。微扰适用条件为

\[
|g_n|\,|\mathcal A_{\rm in}|^{2n}\,|\widehat\chi_n|\ll1.
\]

在领先系数有界且具有非零典型幅值的参数区间，近极端微扰控制参数具有 \(|g_n||\mathcal A_{\rm in}|^{2n}(M\kappa)^{-n}\) 标度。

目前系数级数值检验覆盖一个 principal 模态、两个相互作用阶次和一个固定失谐。扩展到多个 principal 模态、n=3、正负失谐及系数零点附近需要追加计算。高阶 MST 连接项可用于计算有限表面引力的次领先误差。

## 复现入口

- `scripts/analyze_principal_matching_20261013.py`：近远连接和源积分，生成无拟合参数预测。
- `tests/test_principal_matching.py`：近区 ODE、流守恒与外区 ODE 的独立检查。
- `results/kerr_scalar_principal_relation_20261013_N256.csv`、N320、N384、N448：完整 Kerr 数据。
- `results/kerr_scalar_principal_matched_prediction_20261013.csv`：解析与谱结果逐点对照，含双边界验收标志。
- `results/kerr_scalar_principal_matching_checks_20261013.json`：积分阶数检查、双分辨率变化和输入/代码 SHA-256。
- `results/kerr_scalar_principal_quality_summary_20261013.csv`：代表点谱系数和含场相对残差。

线性连接背景采用 Mano、Suzuki、Takasugi 的 [MST 原文](https://arxiv.org/abs/gr-qc/9603020)，近极端超几何与远区连接参照 Bredberg 等的 [近超辐射标量散射推导](https://arxiv.org/abs/0907.3477)。本文的非线性源积分及与完整 Kerr 谱结果的对照由上述新脚本计算。
