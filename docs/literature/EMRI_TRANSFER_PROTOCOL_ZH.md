# 从 Kerr 径向响应到 EMRI 波形：迁移协议

这份笔记把当前 KerrScattering 的单频径向求解器放在 EMRI 的完整计算
链中。它的目的不是把固定背景标量结果改名为 EMRI，而是明确哪些量可以
复用、哪些量必须新增，以及每一步怎样验收。

## 1. 轨道层

在单位 (G=c=1) 下，给定 Kerr 参数 (M,a)，用粒子四速度的三个守恒量

\[
E=-u_t,\qquad L_z=u_\phi,\qquad Q
\]

定义径向和极向势。采用 Mino 参数 (lambda)，令

\[
 d\lambda=d\tau/\Sigma,
 \qquad
 \Sigma=r^2+a^2\cos^2\theta .
\]

径向、极向和方位运动分别是周期项加线性漂移。对一个非共振有界轨道，
先从周期运动得到 Mino 频率

\[
\Upsilon_r,\qquad \Upsilon_\theta,\qquad \Upsilon_\phi,
\]

再由时间漂移量 (Gamma=\langle dt/d\lambda\rangle) 转成坐标时间频率：

\[
\Omega_r=\Upsilon_r/\Gamma,\qquad
\Omega_\theta=\Upsilon_\theta/\Gamma,\qquad
\Omega_\phi=\Upsilon_\phi/\Gamma .
\]

验收不是只看一个轨道积分图，而是比较 Mino 积分与直接数值积分得到的三
个频率，并记录轨道参数、转折点、积分容差和共振距离。

## 2. 源模态层

对傅里叶约定

\[
\Phi\sim e^{-i\omega t+im\phi},
\]

有界 Kerr 轨道的离散源频率是

\[
\omega_{mkn}=m\Omega_\phi+k\Omega_\theta+n\Omega_r,
\qquad k,n\in\mathbb Z .
\]

因此未来的接口应当传递带约定的对象

```text
OrbitConstants -> Frequencies -> ModeLabel(l,m,k,n,omega)
              -> AngularSourceProjection -> RadialResponse
```

这里的 ((l,m,k,n)) 不能被一个任意的连续频率扫描替代。模态总和必须有
单独的 (l)、(k)、(n) 截断误差；当

\[
 n\Omega_r+k\Omega_\theta\simeq0
\]

时要设置共振标志，不能继续套用远离共振的普通平均化公式。

## 3. 径向 Green 函数层

对每个带约定的 ((l,m,k,n,\omega))，令 (R^{\rm in}) 在视界纯入射、
(R^{\rm up}) 在无穷远纯出射。源解的结构是

\[
R_{\rm part}(r)=R^{\rm up}(r)
\int_{r_+}^{r}\frac{R^{\rm in}(r')S(r')}{W(r')}dr'
+R^{\rm in}(r)
\int_{r}^{\infty}\frac{R^{\rm up}(r')S(r')}{W(r')}dr',
\]

其中 (W) 必须带上当前径向变量和自伴权重的精确定义。无穷远和视界的
源振幅分别来自源投影除以同一个 Wronskian。当前项目可以复用：

- 端点包含的 Chebyshev 离散化；
- 视界正则奇点给出的矩阵边界关系；
- 场依赖相对残差、谱尾、端点残差和通量检查。

但不能直接复用为 EMRI 结果的部分包括：点粒子源的分布意义、角向源投影、
模态格点截断和轨道随慢时间的演化。

## 4. 通量层

Teukolsky 或标量约定下，必须先把径向振幅转换为物理归一化，再计算无穷
远和视界通量。对引力 EMRI，通量一般写成各模态贡献之和

\[
\mathcal F^\infty=\sum_{l m k n}\mathcal F^\infty_{lmkn},
\qquad
\mathcal F^H=\sum_{l m k n}\mathcal F^H_{lmkn} .
\]

视界项的符号必须保留 (omega-m\Omega_H) 的信息；在超辐射区它可能表现
为从黑洞抽取能量。验收需要分别报告无穷远、视界和总通量，不能只给一个
正数总和。

对当前固定背景标量非线性文章，这一层只表示局部的守恒通量和响应系数；
它没有 (E,L_z,Q) 的轨道演化含义。

## 5. 绝热演化与相位预算

引入慢时间 (T=\eta t)，轨道作用量的层级结构可写成

\[
\frac{dJ_A}{dT}=F_A^{(0)}(J)+\eta F_A^{(1)}(J,q)+O(\eta^2),
\]

而波形相位对频率误差的响应是

\[
\delta\Phi(t)=\int_0^t\delta\Omega[J(t')]\,dt'
+\delta\Phi_{\rm source}(t).
\]

这说明径向谱残差 (delta R) 不是最终的波形误差。最少要建立如下误差
预算：径向离散化、角向特征值、(lkn) 模态截断、轨道积分、近似阶次和
累积相位。只有在这些误差分别收敛后，才可讨论 LISA 参数估计或 Kerr 检验。

## 6. 与 self-force 的边界

引力自力还需要小质量比展开

\[
g_{\mu\nu}=g^{(0)}_{\mu\nu}+\eta h^{(1)}_{\mu\nu}
+\eta^2h^{(2)}_{\mu\nu}+\cdots,
\]

以及点粒子奇异场、正则场、规范选择、mode-sum 或 effective-source 正则
化和自洽世界线。当前的

\[
\Box\Phi+\epsilon|\Phi|^2\Phi=0
\]

是在固定 Kerr 背景上的光滑标量源问题；它的 (T^{(1)})、(R^{(1)}) 是对
(epsilon=0) 的响应导数，不是 (h^{(1)}) 或 gravitational self-force。

## 7. 迁移验收清单

1. Mino-time 频率与直接积分一致；
2. ((l,m,k,n)) 模态和源投影具有独立截断收敛；
3. 径向解在阶数、匹配半径、求积阶数下稳定；
4. 无穷远/视界通量和守恒关系分别闭合；
5. 绝热积分的步长收敛，且报告累积相位而非只报告瞬时误差；
6. 共振、规范、正则化和扰动阶次均显式标注；
7. 与当前固定背景标量论文的结论边界保持分离。

这份协议对应机器可读门槛 `emri-waveform-transfer`，并不声称仓库已经
实现轨道积分器或引力自力求解器。
