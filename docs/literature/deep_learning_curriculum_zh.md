# 引力理论深度学习课程

这是一份面向当前 KerrScattering 项目的研究课程。目标不是收集尽可能多的
论文，而是把每个理论层次读到可以写出约定块、复现核心方程、设计数值检验的
程度。原始 arXiv 标识和摘要元数据由 `seed_arxiv_ids.txt` 与
`results/literature/arxiv_catalog.json` 管理；论文卡片是证据摘要，不替代原文。

## 0. 先建立总框架

必须把以下四个层次分开：

1. **固定背景黑洞微扰**：在给定 Schwarzschild/Kerr 上求场；当前代码属于这里的
   标量 `s=0`。
2. **固定背景的指定场非线性**：例如 `Box Phi + epsilon |Phi|^2 Phi = 0`，求
   Green-function 的响应系数；这不是度规或轨道的自力。
3. **引力自力**：以 `eta=mu/M` 展开度规和世界线，进行奇异/正则场分解，处理
   规范与正则化，并修正运动方程。
4. **EMRI 波形**：把 Kerr 轨道、源模态、耗散和保守自力、共振及慢时间相位演化
   组合起来。

任何新论文都必须先标注它属于哪一层。

## 1. 八个学习模块

每个模块的方程、实现目标和验收条件由 `learning_gates.json` 管理。阅读顺序
必须从固定背景和辐射反作用的概念基础开始，再进入正则化、EMRI 源格点和波形
相位；不能从一个高精度径向振幅直接跳到自力结论。

### A. 广义相对论和黑洞几何

目标：熟练使用 Kerr 的 `Delta`、`Sigma`、视界生成元、Killing 向量和守恒量，
并能从 `j_E^mu=-T^mu{}_t` 推出固定 `r` 面的能流。输出是本项目使用的约定块，
不是泛泛的背景介绍。

验收：从度规独立推导视界通量的符号、`p=omega-m Omega_H` 和超辐射阈值。

### B. Teukolsky 与 Sasaki--Nakamura

重点阅读 `gr-qc/0306120`、`gr-qc/9603020` 和 `2306.16469`。记录自旋权、
Fourier 号、角本征值、径向变量、视界/无穷远基底以及 `B_inc/B_ref` 的归一化。
MST 主要用于低频连接系数和相位审计，GSN 主要用于稳定的独立 benchmark。

验收：在 `omega=1e-4, 0.1, 10` 这样的不同频段，比较物理振幅比和通量，而不
直接比较未经转换的径向数组。

### C. Kerr 测地线与 EMRI 源格点

重点阅读 `gr-qc/0202090`、`0906.1420` 和 `0904.3810`。掌握
`Omega_r, Omega_theta, Omega_phi` 以及

```text
omega_mkn = m Omega_phi + k Omega_theta + n Omega_r
```

源不是任意单频，而是离散的 `(l,m,k,n)` 模式格点。当前径向 solver 只应被视为
这个未来接口的 mode backend。

验收：给定一条固定 Kerr 轨道，独立用 Mino-time 公式和数值积分得到频率，并把
同一个 `(m,k,n)` 映射到径向代码的 `omega`。

### D. Green 函数、辐射反作用和通量

阅读 `1102.0529`、`gr-qc/0701069` 和 `1805.10385`。理解 Wronskian、无穷远/视界
通量、耗散量和局部保守量各自验证什么。通量平衡不能替代局部场的正则化，也不
能替代长时间相位误差。

验收：每个实验分开报告场残差、振幅误差、通量平衡和匹配半径依赖。

### E. 引力自力与正则化

先阅读 `gr-qc/9712056` 和 `gr-qc/0202086`，再阅读 `gr-qc/9912010`、
`0908.1664`、`1305.1789`、`1506.06245`、`1711.09607`、`2209.05450`。
掌握 `h_ret=h_S+h_R`、Detweiler--Whiting 分解、mode-sum 大 `l` 渐近、puncture、
规范依赖，以及耗散/保守自力的区别。

验收：能解释为什么当前平滑的标量三次源不需要 mode-sum subtraction，并且不把
`A^(1)` 写成 self-force。

### F. EMRI 多尺度与波形

阅读 `2101.04592`、`2109.00056`、`2310.08438`、`2410.17310` 和
`2507.06923`。把质量比阶数、绝热和 post-adiabatic 阶数、near-identity
transformation、共振跳变以及累积相位预算连起来。

验收：画出误差树，把径向离散误差、模式截断、轨道积分误差和相位误差分开。

### G. 二阶 Teukolsky、非线性和 ringdown

阅读 `2305.19332`、`2210.15935`、`2410.23950` 以及非线性散射的相关论文。区分
实时频率驱动响应、二阶引力扰动、QNM 极点投影和长时间 memory。Kerr QNM 不能
未经处理就使用普通 Hilbert 空间投影。

验收：当前 PRD 只把 Lorentzian fit 写成描述性拟合，不称为 QNM excitation
coefficient。

### H. 数值方法与科学软件

把 Schwarzschild 的端点 Chebyshev 路线迁移到 Kerr：包括端点关系、条件数、复数
线性求解、谱系数尾、场依赖相对残差、低频抵消和高频相位分辨率。再用 MATLAB、
Python、WSL/Julia 和 Mathematica 做交叉验证。

验收：所有长任务有内存上限、分块频率循环、日志和可重复命令；论文构建两次结果
一致。

## 2. 文献卡片的最小内容

每篇 A 级论文必须补齐：

- 问题、背景、扰动参数和展开阶数；
- metric/signature/Fourier/gauge/tetrad/radial/angular conventions；
- 核心方程和精确边界条件；
- Green function、Wronskian 或 regularization 的归一化；
- 数值方法、精度控制和独立验证；
- 能迁移到本仓库的结论；
- 与当前固定背景标量问题不相容的假设；
- 一个可以验证迁移结论的新实验。

## 3. 当前阶段和下一阶段

当前已经具备 A、B、D、H 的固定频率实现，以及 C、E、F 的文献接口层。尚未
实现的是：真正的 EMRI 轨道/源生成、自力正则化、度规重构、慢时间演化和累积
引力波相位。因此后续开发应先建立 `orbit -> source modes -> radial response`
接口，再谈 EMRI waveform；不要从单个 Kerr 标量散射振幅直接跳到自力结论。

每次阅读后的结果写入 `docs/literature/study_log_YYYY-MM-DD.md`，并运行：

```powershell
python scripts/build_literature_manifest.py
python scripts/check_literature_catalog.py
python scripts/check_research_setup.py
```

更细的执行顺序和每周验收循环见
`docs/literature/advanced_learning_protocol_zh.md`；MCP 可以通过
`get_learning_gate` 返回单个模块的机器可读门槛。
