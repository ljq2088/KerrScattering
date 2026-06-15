# Kerr s=0 标量 Teukolsky 散射主线说明

本文档只保留 Kerr 背景标量场，也就是 Teukolsky 方程的 `s=0` 主线。
此前混入的非标量 benchmark 内容已经移除；相关历史脚本暂不作为当前标量
非线性散射结论的一部分。

当前完整中文 PDF 说明见：

- `docs/kerr_scalar_current_work_zh.pdf`

当前 PRD 风格英文稿见：

- `docs/prd/kerr_scalar_scattering_prd.pdf`

## 已完成内容

1. 线性 Kerr 标量 Teukolsky 径向方程：

   \[
   \frac{d}{dr}\left(\Delta \frac{dR}{dr}\right)
   +\left(\frac{K^2}{\Delta}-\lambda\right)R=0,
   \quad
   K=(r^2+a^2)\omega-am .
   \]

2. 端点 Chebyshev 谱方法：

   \[
   z=\frac{r_+}{r},\qquad z=0\leftrightarrow r=\infty,\qquad
   z=1\leftrightarrow r=r_+ .
   \]

   相位剥离后，端点处二阶导系数退化，矩阵端点行自然给出一阶正则边界条件。
   因此当前方法不需要视界截断或无穷远截断。

3. 振幅提取：

   \[
   R_{\rm in}=B^{\rm inc}R_{\rm down}+B^{\rm ref}R_{\rm up}
   \]

   在匹配半径处同时匹配函数值和径向导数，求解 `B_inc` 和 `B_ref`。

4. 线性 benchmark：

   - 37 个 GSN 可用 benchmark 点全部通过；
   - 最坏幅值模误差：`1.485e-8`；
   - 最坏通量残差：`3.714e-9`；
   - 51 点频率扫描显示超辐射只出现在 `omega < m Omega_H`。

5. 弱三次非线性源项：

   对

   \[
   \Box\Phi+\epsilon|\Phi|^2\Phi=0
   \]

   一阶径向源为

   \[
   Q_{\ell'\ell m}(r)=
   \left[
   r^2 C^{(0)}_{\ell'\ell m}+a^2 C^{(2)}_{\ell'\ell m}
   \right]|R_{\ell m}^{(0)}|^2R_{\ell m}^{(0)} .
   \]

   其中

   \[
   C^{(p)}_{\ell'\ell m}
   =
   \int d\Omega\,
   \cos^p\theta\,
   S_{\ell'm}^* |S_{\ell m}|^2 S_{\ell m},
   \qquad p=0,2 .
   \]

6. 非线性 Green 函数：

   自通道结果使用

   \[
   A_{\rm ref}^{(1)}
   =
   -\frac{\epsilon}{W}
   \int_{r_+}^{\infty} R^{\rm in}(r)Q(r)\,dr,
   \]

   \[
   A_H^{(1)}
   =
   -\frac{\epsilon}{W}
   \int_{r_+}^{\infty} R^{\rm up}(r)Q(r)\,dr .
   \]

   外区积分已经改为相位通道 Fourier tail 积分，避免紧化端点 Gauss 积分的
   假收敛。

## 当前非线性结论

当前表格是单位三次耦合、单位视界透射归一化下的一阶响应系数。真正物理修正是

\[
\epsilon A^{(1)} .
\]

弱非线性展开要求

\[
\epsilon |A^{(1)}|\ll |A^{(0)}| .
\]

因此，大的 `A_ref_1` 不应直接解释为微扰失效；必须结合实际入射归一化和
耦合强度判断。

## 新增多通道结果

非线性 Green 函数现在已经支持源通道 `l` 和目标通道 `l_target` 不同的计算。
对代表性模式

```text
a = 0.5, l = m = 2, omega = 0.30
```

采用 `N=288, q=224, tail_epsrel=1e-11` 扫描 `l'=2,...,6` 得到：

| l' | \|C0\| | \|A_ref_1\| | \|A_H_1\| | status |
|---:|---:|---:|---:|:---|
| 2 | `1.136e-1` | `1.137e6` | `3.804e3` | self-channel |
| 3 | `0` | `0` | `0` | zero angular coupling |
| 4 | `3.578e-2` | `1.362e4` | `1.319` | active |
| 5 | `0` | `0` | `0` | zero angular coupling |
| 6 | `5.341e-3` | `2.265e3` | `5.383e-7` | active |

这说明当前实现已经从自通道推进到目标通道矩阵的第一步。奇数 `l'`
通道在该模式下由角向投影对称性消失；偶数高通道非零，但比自通道小。

对 active 通道进一步做 `q=224`、`N=224,256,288` 的收敛检查。相对
`N=288` 参考行，反射振幅的最大相对变化为 `1.140e-4`，其中 `N=256`
到 `N=288` 的最大相对变化为 `6.270e-7`。因此当前最坚实的非线性结论
是：反射端的多通道一阶响应已经数值稳定，主导通道仍是自通道 `l'=2`，
off-diagonal 的 `l'=4,6` 反射响应依次下降。

视界端 off-diagonal 振幅更弱并存在强抵消。`l'=4` 在 `N=256` 到 `N=288`
之间约为百分级稳定；`l'=6` 的 `A_H_1` 只有 `10^{-7}` 量级，相对误差会被
近零分母放大，目前只作为量级诊断，不作为高精度物理结论。

## 仍需继续完善

下一步主线工作只围绕 `s=0` 标量场：

1. 把多通道扫描从当前代表点扩展到更多 `(a,l,m,omega)`；
2. 建立固定入射幅归一化下的非线性修正；
3. 对非线性通道矩阵设置统一 acceptance gate；
4. 用独立 Levin/Filon 振荡积分器交叉验证 Fourier tail。
