# Kerr 背景 s=0 Teukolsky 标量场散射：解析推导、谱方法与数值验证

## 0. 摘要

本文档给出当前 Schwarzschild Green-function 谱方法向 Kerr 背景的
`s=0` 标量 Teukolsky 方程推广时需要的解析结构。目标不是只写出一条
径向方程，而是把解析推导、边界归一化、谱离散、散射振幅提取、
外部 benchmark 和非线性 Green-function 诊断统一成一套可复现实验流程。
本文已经对应当前分支中的实际代码和结果文件，而不再只是算法建议。

1. Kerr 几何、tortoise 坐标和视界角速度。
2. 复标量场 Klein-Gordon 方程的分离变量。
3. scalar spheroidal angular equation 与角向本征值 `A_lm`。
4. `s=0` 径向 Teukolsky 方程和径向分离常数 `lambda`。
5. `in/up/down/out` 四个齐次解、Wronskian 与散射振幅。
6. 能流归一化、superradiance 条件和 Schwarzschild 极限。
7. 弱非线性 `|Phi|^2 Phi` 源项在 Kerr spheroidal basis 下的角向投影。
8. 端点直接配点的两域 Chebyshev 谱方法。
9. GeneralizedSasakiNakamura.jl benchmark、频率扫描和三次角向投影结果。
10. 非线性径向 Green-function 诊断及当前尚未定标的物理部分。

本文采用 `G=c=M=1` 时可令 `M=1`，但公式中保留 `M`，便于和
Schwarzschild 代码对照。

## 1. Kerr 几何与坐标

Boyer-Lindquist 坐标下 Kerr 度规为

```text
ds^2 = -(1 - 2 M r/Sigma) dt^2
       - 4 M a r sin^2(theta)/Sigma dt dphi
       + Sigma/Delta dr^2 + Sigma dtheta^2
       + A sin^2(theta)/Sigma dphi^2
```

其中

```text
Sigma = r^2 + a^2 cos^2(theta)
Delta = r^2 - 2 M r + a^2 = (r-r_+)(r-r_-)
A = (r^2+a^2)^2 - a^2 Delta sin^2(theta)
```

内外视界为

```text
r_+ = M + sqrt(M^2-a^2)
r_- = M - sqrt(M^2-a^2)
```

视界角速度为

```text
Omega_H = a/(r_+^2+a^2) = a/(2 M r_+)
```

Kerr tortoise 坐标取

```text
dr*/dr = (r^2+a^2)/Delta
```

积分得到

```text
r* = r
   + 2 M r_+/(r_+-r_-) log(r-r_+)
   - 2 M r_-/(r_+-r_-) log(r-r_-)
```

加性常数无物理意义。Schwarzschild 极限 `a -> 0` 给出

```text
r* = r + 2 M log(r/2M - 1)
```

后续相位因子都用 `exp(+- i omega r*)` 或
`exp(+- i (omega-m Omega_H) r*)` 表示。

## 2. 标量场方程与分离变量

线性复无质量标量场满足

```text
box Phi = 0
```

若保留弱非线性自相互作用，则模型为

```text
box Phi + eps |Phi|^2 Phi = 0
Phi = Phi^(0) + eps Phi^(1) + O(eps^2)
```

这里 `eps` 是非线性耦合的小参数。为了避免和 Teukolsky 径向分离常数
混淆，项目代码中非线性耦合仍称为 `Cl` 或 `epsilon_nl`，而径向分离常数
称为 `lambda`.

Kerr 背景只有轴对称而非球对称，因此分离变量采用

```text
Phi^(0)(t,r,theta,phi)
  = R_lmomega(r) S_lm(theta; a omega)
    exp(i m phi - i omega t)
```

其中 `m` 是方位角量子数，`l >= |m|`。把该 ansatz 代入
Klein-Gordon 方程后，可分成角向 spheroidal 方程和径向 Teukolsky 方程。

## 3. s=0 spheroidal angular equation

本文采用的 scalar spheroidal equation 为

```text
1/sin(theta) d_theta[ sin(theta) d_theta S ]
+ [ a^2 omega^2 cos^2(theta)
    - m^2/sin^2(theta)
    + A_lm(a omega) ] S = 0
```

当 `c = a omega -> 0` 时，

```text
S_lm(theta;c) -> Y_lm(theta,phi)/exp(i m phi)
A_lm(c) -> l(l+1)
```

一种稳定的计算方式是把 `S_lm` 展开在球谐基底上：

```text
S_lm(theta;c) = sum_L b_L Y_Lm(theta,phi)/exp(i m phi)
```

利用

```text
cos(theta) Y_Lm
 = alpha_{L+1,m} Y_{L+1,m} + alpha_{L,m} Y_{L-1,m}
```

其中

```text
alpha_{L,m} = sqrt((L^2-m^2)/[(2L-1)(2L+1)])
```

可得 `cos^2(theta)` 只耦合 `L` 到 `L`、`L+2`、`L-2`。角向本征值问题化为

```text
[ diag(L(L+1)) - c^2 <L m|cos^2(theta)|L' m> ] b = A_lm b
```

这给出代码里的 fallback 计算。生产环境中建议把该计算抽象为
`lambda_provider`，可以调用：

```text
1. 本地矩阵方法：适合 s=0、低中等 c 的快速 fallback。
2. WSL/Python helper:
   /home/ljq/code/PINN/SolvingTeukolskyEq_autoencoder/utils/compute_lambda_usage.py
3. GSN/SpinWeightedSpheroidalHarmonics.jl:
   高频和 s=-2 benchmark。
4. Mathematica BHPT:
   低频 MST benchmark。
```

## 4. s=0 径向 Teukolsky 方程

定义

```text
K(r) = (r^2+a^2) omega - a m
```

`s=0` Teukolsky 径向方程为

```text
d/dr [ Delta dR/dr ] + [ K^2/Delta - lambda ] R = 0
```

本文采用的径向分离常数为

```text
lambda = A_lm(a omega) + a^2 omega^2 - 2 a m omega
```

注意：不同软件包对 angular eigenvalue 和 radial separation constant 的
命名并不完全一致。有些包返回 `A_lm`，有些包返回上式中的 `lambda`。
因此代码必须显式记录 provider convention。

一阶系统形式：

```text
y_1 = R
y_2 = dR/dr

d y_1/dr = y_2
d y_2/dr = -[ Delta' y_2 + (K^2/Delta - lambda) y_1 ]/Delta
```

这正是 `radial_rhs_s0` 的数学含义。

## 5. 视界与无穷远边界行为

### 5.1 视界附近

在 `r -> r_+` 时

```text
r* ~ alpha_+ log(r-r_+)
alpha_+ = (r_+^2+a^2)/(r_+-r_-)
```

协转视界频率为

```text
p = omega - m Omega_H
```

`in` 解在未来视界正则，对应

```text
R_in ~ B_trans Delta^0 exp(-i p r*)          (s=0)
```

若取单位视界透射振幅：

```text
B_trans = 1
R_in ~ exp(-i p r*) ~ (r-r_+)^(-i alpha_+ p)
```

`out` 解则为

```text
R_out ~ exp(+i p r*)
```

### 5.2 无穷远附近

`r -> infinity` 时 `Delta ~ r^2`，径向方程的两个独立行为为

```text
R ~ Z_in  exp(-i omega r*)/r
  + Z_out exp(+i omega r*)/r
```

因此 `in` 解的无穷远展开写作

```text
R_in ~ B_inc exp(-i omega r*)/r
     + B_ref exp(+i omega r*)/r
```

`up` 解满足无穷远纯出射：

```text
R_up ~ C_trans exp(+i omega r*)/r
```

在视界附近它是入射/出射的线性组合。

项目变量建议：

```text
B_trans = transmission_amplitude
B_inc   = incidence_amplitude
B_ref   = reflection_amplitude
```

GSN 的 `UNIT_TEUKOLSKY_TRANS` 约定正是 `B_trans = 1`。

## 6. Wronskian、散射系数与能流

s=0 径向方程可写成 Sturm-Liouville 型：

```text
(Delta R')' + V(r) R = 0
```

因此两个齐次解 `R1, R2` 的径向 Wronskian

```text
W_r[R1,R2] = Delta (R1 R2' - R2 R1')
```

为常数。对实频率、实势，`R_up` 可与共轭解相关联。用 Wronskian 在两端
求值，可得到能流守恒。

对 scalar 场，径向能流与相位群速度成正比。注意 Kerr 视界端

```text
Delta d_r exp(-i p r*) -> -i p (r_+^2+a^2) exp(-i p r*)
```

因此视界通量带有 `r_+^2+a^2 = 2 M r_+` 因子。若 `B_trans=1`，则形式上

```text
F_H ~ p (r_+^2+a^2) |B_trans|^2
F_infty,in  ~ omega |B_inc|^2
F_infty,out ~ omega |B_ref|^2
```

于是线性反射率和透射率可写成

```text
R0 = |B_ref|^2 / |B_inc|^2
T0 = [p (r_+^2+a^2)/omega] |B_trans|^2 / |B_inc|^2
```

并满足

```text
R0 + T0 = 1
```

若 `p < 0`，即

```text
omega < m Omega_H
```

则 `T0 < 0`，从而 `R0 > 1`，这就是 superradiance。这个符号结构在 Kerr
中必须保留，不能像 Schwarzschild 那样简单假设 `0 <= R <= 1`。

## 7. Schwarzschild 极限

当 `a -> 0` 时：

```text
r_+ = 2M
r_- = 0
Omega_H = 0
K = r^2 omega
A_lm = l(l+1)
lambda = l(l+1)
```

s=0 径向 Teukolsky 方程变为

```text
d/dr[(r^2-2Mr)dR/dr]
+ [r^4 omega^2/(r^2-2Mr) - l(l+1)] R = 0
```

若定义 Schwarzschild 项目中的 Regge-Wheeler radial variable

```text
psi = r R
```

并使用 Schwarzschild tortoise 坐标，则可化为

```text
d_x^2 psi + [omega^2 - f(l(l+1)/r^2 + 2M/r^3)] psi = 0
```

这正是当前 Schwarzschild 复现项目的线性方程。

## 8. Kerr 版 Green 函数

令 `R_in` 和 `R_up` 分别满足：

```text
R_in:  horizon 纯入射
R_up:  infinity 纯出射
```

则径向 Green 函数为

```text
G(r,r') =
  R_in(r_<) R_up(r_>) / W
```

其中

```text
W = Delta [ R_in d_r R_up - R_up d_r R_in ]
```

若一阶非线性径向方程写为

```text
L_l'[R_l'^(1)] = S_l'(r)
```

则解为

```text
R_l'^(1)(r) =
  R_up(r)/W  int_{r_+}^{r}     R_in(r') S_l'(r') dr'
 +R_in(r)/W  int_{r}^{infty}  R_up(r') S_l'(r') dr'
```

从 `r -> infinity` 和 `r -> r_+` 的渐近式可以读出非线性出射振幅与视界
入射振幅修正。这个结构与 Schwarzschild 版代码的 `A1out/A1in` 完全平行，
但有两个额外复杂性：

```text
1. 角向 spheroidal harmonics 导致 l-channel mixing。
2. 视界相位使用 p = omega - m Omega_H，而不是 omega。
```

## 9. 弱非线性源项与角向耦合

考虑复标量自相互作用：

```text
box Phi + eps |Phi|^2 Phi = 0
```

若线性入射模式为单一 `(l,m,omega)`：

```text
Phi^(0) = R_lm(r) S_lm(theta) exp(i m phi - i omega t)
```

则三次源为

```text
|Phi^(0)|^2 Phi^(0)
 = |R_lm|^2 R_lm |S_lm|^2 S_lm
   exp(i m phi - i omega t)
```

频率和方位数仍为 `(omega,m)`，但角向函数

```text
|S_lm|^2 S_lm
```

一般不是单一 spheroidal harmonic，需要展开为

```text
|S_lm|^2 S_lm = sum_{l'} C_{l' l m}(a omega) S_l'm(theta)
```

其中

```text
C_{l' l m}
 = int dOmega conjugate(S_l'm) |S_lm|^2 S_lm
```

于是每个 `l'` 的径向源为

```text
S_l'(r) = - C_{l' l m} * radial_weight(r) * |R_lm(r)|^2 R_lm(r)
```

`radial_weight(r)` 取决于径向函数定义。如果使用 `Phi = R S e^{...}`，
则权重直接来自 `box` 的径向分离形式；如果使用 `psi = r R` 或其他
重标定变量，则会出现额外的 `r` 因子。代码实现前必须固定变量约定。

## 10. 数值方案建议

当前 Schwarzschild 代码采用：

```text
z = 2M/r
phi = phitilde exp(-i omega x)
```

Kerr s=0 推荐采用两域方案：

```text
z = r_+/r
near horizon:   R = H(z) exp(-i p r*)
near infinity:  R = F(z) exp(-i omega r*)/r
```

齐次解求法：

```text
1. 先通过 lambda_provider 得到 lambda。
2. 在 horizon domain 求 R_in 或相位剥离后的 H(z)。
3. 在 infinity domain 求 R_down/R_up 或相位剥离后的 F(z)。
4. 在 matching point 同时匹配 R 和 dR/dr。
5. 用 Wronskian 检查匹配误差。
```

当前代码采用端点直接配点，而不是在视界或无穷远附近做有限截断。令

```text
R = F(z) u(z),    z = r_+/r
```

则剥离后的方程可写为

```text
B2(z) u'' + B1(z) u' + B0(z) u = 0
```

在 `z=0` 和 `z=1` 处二阶导系数 `B2` 退化为零；矩阵中保留该退化
ODE 行作为正则一阶条件，并用相邻一行加入归一化 `u(endpoint)=1`。无穷
远端对 `F = exp(i sigma omega r*)/r`，`sigma=-1` 为 down、`sigma=+1`
为 up，有

```text
B2(0) = 0
B1(0) = -2 i sigma r_+ omega
B0(0) = -lambda
```

视界端对 `F = exp(-i p r*)` 有

```text
B2(1) = 0
B1(1) = r_-/r_+ - 1 + 2 i p (r_+ + r_-)
B0(1) =
  4 r_+^2 (r_+ + r_-) p (omega-p)/(r_+-r_-)
  - 2 i r_+ p - lambda
```

这正是 Schwarzschild 谱方法中“端点退化给导数条件、另加 `u=1` 归一化”
的 Kerr `s=0` 对应物。

非线性积分建议：

```text
1. 近视界区间使用 z 或 r 的有限区间积分。
2. 无穷远区间把快振荡相位 exp(i k omega r*) 显式拆出。
3. 对 Fourier tail 使用带权振荡积分或 GSN/MST 给出的渐近展开。
```

## 11. lambda-provider 接口约定

建议的统一接口：

```text
lambda_provider(s,l,m,a,omega, convention)
```

返回结构：

```text
{
  "A_lm": angular eigenvalue, if available,
  "lambda": radial separation constant,
  "provider": "local|wsl-python|gsn|mathematica",
  "convention": text description,
  "status": "ok|failed"
}
```

对 `s=0`，本项目采用：

```text
lambda = A_lm + a^2 omega^2 - 2 a m omega
```

对 `s=-2`，优先直接使用外部包返回的 Teukolsky radial lambda，并在结果
文件中保留 provider 名称，避免跨包约定混淆。

## 12. 代码实现现状

当前分支已经把上面的解析结构落实为以下模块：

```text
src/teukolsky_scalar.py
  s=0 spheroidal eigenvalue, radial lambda, angular mode, cubic coupling.

src/kerr_scalar_spectral.py
  Kerr s=0 in-mode spectral solver, direct endpoint rows, B_inc/B_ref extraction.

src/kerr_scalar_nonlinear.py
  Prototype Green-function source diagnostics using validated homogeneous modes.

scripts/adaptive_kerr_scalar_gsn_validation.py
  GSN benchmark comparison with adaptive spectral order.

scripts/run_kerr_scalar_frequency_sweep.py
  Frequency sweep and superradiance sampling.

scripts/run_kerr_scalar_cubic_projector.py
  Cubic spheroidal projector C_{l'lm}.

scripts/run_kerr_scalar_nonlinear_diagnostics.py
  Nonlinear radial Green-function diagnostics with RSS memory guard.
```

线性求解器采用的基本数值路线是：

```text
1. 先由 local scalar spheroidal matrix 得到 lambda。
2. 在外域 [0,z_m] 分别求 down/up 解。
3. 在内域 [z_m,1] 求 horizon-normalized in 解。
4. 在 z_m 同时匹配 R 与 dR/dr。
5. 解 2x2 线性系统得到 B_inc 与 B_ref。
6. 用 Kerr flux identity 检查散射概率守恒。
```

这里最重要的实现约束是直接把 `z=0` 和 `z=1` 放进谱节点。边界不需要
截断，因为剥离相位后的二阶方程在端点退化为一阶正则条件。矩阵中保留
退化 ODE 行，并用相邻一行给出 `u(endpoint)=1` 的归一化。这一点使 Kerr
实现保持了 Schwarzschild 谱方法的核心路线。

## 13. 线性 benchmark 与频率扫描

外部 benchmark 使用 GeneralizedSasakiNakamura.jl 的
`UNIT_TEUKOLSKY_TRANS` 约定，即视界透射振幅取 `B_trans=1`。由于不同包的
`r*` 加性常数不同，复振幅本身允许有常相位差；pass/fail 只使用
`|B_inc|`、`|B_ref|` 和 flux balance。

当前 validation gate 为：

```text
rel_abs_B_inc <= 1e-7
rel_abs_B_ref <= 1e-7
flux_balance_error <= 1e-8
```

当前 GSN benchmark 摘要为：

```text
GSN requested cases:          37
usable GSN cases:             37
excluded GSN cases:           0
all cases passed:             true
worst invariant score:        1.485e-08
worst flux-balance residual:  3.714e-09
```

测试网格覆盖：

```text
Schwarzschild limit:
  a=0, l=0,1, omega=0.01,0.1,0.5

moderate Kerr:
  a=0.5, l=0,1,2, m=0,1,2,
  omega across low-frequency, near-threshold, and high-frequency regimes

high spin Kerr:
  a=0.9, l=2,3, m=2,
  omega below and above omega=m Omega_H
```

最困难的线性 benchmark 是 `a=0.5, l=m=2, omega=1.0`。该点的
`B_ref` 很小，因此相对误差对条件数和 phase convention 更敏感，但仍满足
`1e-7` 的振幅模长目标。

额外的 frequency sweep 包含 51 个点：

```text
schwarzschild_l0:
  a=0, l=m=0, omega=0.01 ... 1.0, 11 points

kerr_a05_l2m2:
  a=0.5, l=m=2, omega=0.01 ... 1.0, 20 points

kerr_a09_l2m2:
  a=0.9, l=m=2, omega=0.02 ... 1.1, 20 points
```

扫描结果为：

```text
all sweep points passed:             true
worst sweep score:                   9.467e-08
worst sweep flux-balance residual:   7.351e-09
maximum sampled amplification R-1:   4.970e-04
location of maximum amplification:   a=0.9, l=m=2, omega=0.58
```

在旋转黑洞样本中，`R>1` 只出现在 `omega < m Omega_H` 的区域；越过阈值
后反射率回到 `R<1`。这与第 6 节的 flux identity 一致，是当前代码
捕捉 Kerr superradiance 的主要物理检查。

## 14. 三次角向投影与非线性径向诊断

弱非线性源项要求计算

```text
C_{l'lm}(a omega)
  = int dOmega conjugate(S_l'm) |S_lm|^2 S_lm
```

当前代码已经对所有 37 个线性验证源模式计算 `|m| <= l' <= l+4` 的
目标通道，结果写入 `results/kerr_scalar_cubic_couplings.csv`：

```text
source modes projected:       37
coupling rows:                199
self-channel coefficient min: 7.958e-02
self-channel coefficient max: 1.705e-01
largest off-diagonal:         8.318e-02
largest off-diagonal case:    l=2, m=0, a=0.5, omega=0.1, l'=4
```

球对称极限已经用解析值检查：

```text
l=m=0:
  C_000 = 1/(4 pi)

l=1,m=0,a omega=0:
  C_110 = 9/(20 pi)
```

非线性径向部分目前是 Green-function 诊断，而不是最终 Kerr 自相互作用
归一化。它使用已经验证的齐次解和三次角向投影，计算

```text
source_projection_ref = int R_test_ref |R_in|^2 R_in dz/r_+
source_projection_hor = int R_test_hor |R_in|^2 R_in dz/r_+
A_ref_1 = -Cl source_projection_ref/W
A_hor_1 = -Cl source_projection_hor/W
```

这里的径向权重被明确标记为

```text
legacy-bondi-dr-over-r2
```

即它是从 Schwarzschild/Bondi 代码迁移来的诊断权重，不是最终由 Kerr
协变 Klein-Gordon 方程完全定标后的非线性源。当前诊断结果为：

```text
diagnostic cases:                         4
quadrature rows:                          16
worst Wronskian consistency error:        3.094e-16
worst consecutive A_ref_1 quad change:    7.011e-05
worst consecutive A_hor_1 quad change:    8.331e-05
peak recorded process RSS:                83.0 MB
slowest diagnostic row:                   0.20 s
```

这些数字说明齐次 Green-function 骨架和 Wronskian 归一化已经稳定，但径向
源积分的尾部处理还没有达到线性散射 benchmark 的精度层级。下一步要把
`legacy-bondi-dr-over-r2` 替换为从 Kerr 协变方程严格导出的源权重，并对
无穷远振荡尾积分使用专门的 oscillatory quadrature 或渐近展开。

## 15. s=-2 支线 benchmark 状态

用户指定的支线 benchmark 为：

```text
s = -2
a = 0.5
l = m = 2
omega = 1e-4, 0.1, 10.0
quantity: homogeneous R_in amplitude coefficients
```

当前分工：

```text
omega = 10.0:
  使用 WSL Ubuntu-22.04-D 中的 GeneralizedSasakiNakamura.jl。

omega = 1e-4:
  使用 Windows Mathematica kernel，路径 F:\mma，
  加载 F:\EMRI\Radial_flow\Radial_Function.wl，
  调用 ComputeAmplitudesMST。

omega = 0.1:
  使用 Mathematica MST 作为中频 benchmark。
```

当前结果摘要为：

```text
omega=1e-4, Mathematica MST:
  B_inc = -1.5435347274666643e20 + 3.416432242244572e20 i
  B_ref =  1.0210782613860754e4  - 2.281376866596801e4 i

omega=0.1, Mathematica MST:
  lambda = 3.667320713846837
  B_inc = -1.1422820427e5 + 2.3264531432e5 i
  B_ref = -4.2729694283   - 17.946405113 i

omega=10.0, GSN:
  lambda = -26.85215496939334
  B_inc =  2.4675049712429978e1 - 5.0001332607188900e0 i
  B_ref = -6.4579566171517927e-9 - 8.1445991065750824e-9 i
```

直接 Teukolsky 变量中的 Python 对比状态为：

```text
omega=1e-4:
  B_inc relative error = 2.5e-8
  B_ref relative error = 9.1e-12

omega=0.1:
  B_inc relative error = 2.7e-10
  B_ref relative error = 5.3e-12

omega=10.0:
  B_inc relative error = 4.0e-7
  B_ref relative error = 3.4e-1
```

高频 `omega=10.0` 的 `B_ref` 约为 `1e-8`，已经接近直接 Teukolsky 变量
双精度匹配的有效地板；要把该行继续推到 benchmark 精度，稳定路线是演化
Sasaki-Nakamura 变量，再用 Teukolsky-Sasaki-Nakamura 转换因子恢复振幅。
因此 `s=-2` 支线目前作为 benchmark 接口和算法风险说明保留，不与
`s=0` 标量求解器混合。

## 16. 当前结论与文章状态

本推导已经完成 `s=0` 标量 Teukolsky 方程从 Kerr Klein-Gordon 方程到径向
散射振幅的主线，也完成了与 Schwarzschild 谱方法对应的数值实现。核心
结果可以概括为：

```text
1. 使用 z=r_+/r 的两域 Chebyshev 谱方法可以直接包含 z=0 与 z=1。
2. 端点二阶导系数退化给出正则导数条件，端点归一化取 u=1。
3. B_inc/B_ref 通过 in 解与 down/up 解在中间点匹配得到。
4. Kerr flux identity 给出 superradiance 条件 omega < m Omega_H。
5. 37 个 GSN benchmark 全部通过，最坏 invariant error 为 1.485e-08。
6. 51 个频率扫描点全部通过，且正确解析 Kerr scalar superradiance。
7. 三次 spheroidal angular projector 已实现并通过球极限解析检查。
8. Green-function 非线性径向骨架已实现，Wronskian 稳定到机器精度。
```

因此，对线性 `s=0` Kerr 标量散射问题，当前文章和代码已经形成闭环：

```text
解析方程 -> 边界条件 -> 谱离散 -> 振幅提取 -> flux 检查 -> GSN benchmark
```

如果目标是 PRD 级文章，线性部分已经具备核心数值证据。剩余需要补强的是
非线性物理部分：

```text
1. 从 covariant scalar field equation 固定 Kerr cubic source 的径向权重。
2. 把诊断用有限阶 quadrature 升级为可控的振荡尾积分。
3. 给 A_ref_1/A_hor_1 设置和线性振幅同等级的收敛 gate。
4. 若纳入 s=-2 支线，高频小反射振幅应改用 Sasaki-Nakamura 变量。
```

当前 PDF 因此应理解为 Kerr `s=0` 线性散射与非线性 Green-function 框架的
完整项目文章草稿；线性散射部分可作为论文主体，非线性部分作为下一阶段
物理定标和数值尾积分的明确路线图。
