# Kerr 背景 s=0 Teukolsky 标量场散射：解析推导与项目约定

## 0. 摘要

本文档给出当前 Schwarzschild Green-function 谱方法向 Kerr 背景的
`s=0` 标量 Teukolsky 方程推广时需要的解析结构。目标不是只写出一条
径向方程，而是把后续代码需要固定的所有约定连起来：

1. Kerr 几何、tortoise 坐标和视界角速度。
2. 复标量场 Klein-Gordon 方程的分离变量。
3. scalar spheroidal angular equation 与角向本征值 `A_lm`。
4. `s=0` 径向 Teukolsky 方程和径向分离常数 `lambda`。
5. `in/up/down/out` 四个齐次解、Wronskian 与散射振幅。
6. 能流归一化、superradiance 条件和 Schwarzschild 极限。
7. 弱非线性 `|Phi|^2 Phi` 源项在 Kerr spheroidal basis 下的角向投影。
8. 项目代码中的 lambda-provider 接口和 Mathematica/GSN benchmark 分工。

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

对 scalar 场，径向能流与相位群速度成正比。若 `B_trans=1`，则形式上

```text
F_H ~ p |B_trans|^2
F_infty,in  ~ omega |B_inc|^2
F_infty,out ~ omega |B_ref|^2
```

于是线性反射率和透射率可写成

```text
R0 = |B_ref|^2 / |B_inc|^2
T0 = (p/omega) |B_trans|^2 / |B_inc|^2
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

## 12. benchmark 分工

用户指定的支线 benchmark 为：

```text
s = -2
a = 0.5
l = m = 2
omega = 1e-4, 10.0
```

当前分工：

```text
omega = 10.0:
  使用 WSL Ubuntu-22.04-D 中的 GeneralizedSasakiNakamura.jl。

omega = 1e-4:
  使用 Windows Mathematica kernel，路径 F:\mma，
  加载 F:\EMRI\Radial_flow\Radial_Function.wl，
  调用 ComputeAmplitudesMST。
```

高频 GSN 给出 lambda 与 Teukolsky 振幅系数；低频 Mathematica/MST 给出
`Incidence`、`Reflection`、`Transmission` 和 `Reflection/Incidence`。

## 13. 当前结论

本推导已经完成 `s=0` 标量 Teukolsky 方程从 Kerr Klein-Gordon 方程到径向
散射振幅的主线。代码层面下一步不是重写所有 Schwarzschild 逻辑，而是先
完成三个接口：

```text
1. lambda_provider: 统一 local/GSN/Mathematica/WSL helper 的本征值约定。
2. scalar radial solver: 返回 R_in/R_up 及 B_inc/B_ref/B_trans。
3. nonlinear source projector: 计算 spheroidal harmonic 的 C_{l'l m}。
```

完成这三件事后，Schwarzschild 的 Green-function 非线性修正才能自然迁移到
Kerr。
