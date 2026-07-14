# 引力理论深度学习执行协议

本协议把“阅读文献”变成可以审计的研究动作。每个模块都必须经过
**约定提取 -> 方程复现 -> 数值迁移 -> 独立检验 -> 适用范围声明**五步，
不能因为摘要或二手综述中出现相同关键词就把两个理论层次合并。

## 1. 文献阅读卡片

每篇 A 级论文读完后，记录以下内容：

1. 研究对象、背景度规、扰动参数和展开阶数；
2. metric signature、Fourier sign、tetrad、gauge、径向和角向变量；
3. 核心方程、源项、视界与无穷远边界条件；
4. Green function、Wronskian、正则化参数或双线性投影的归一化；
5. 数值方法、条件数、误差指标和独立 benchmark；
6. 能够迁移到 KerrScattering 的公式或接口；
7. 与当前固定背景 `s=0` 标量模型不兼容的假设；
8. 一个可以实际运行的迁移实验。

## 2. 四条主线及其传递关系

### 固定背景 BHPT

从 Kerr 几何和 Teukolsky 分离开始，先得到角本征值、径向端点指数、
`B_inc/B_ref` 和 Wronskian 的同一套 convention。当前 Chebyshev 求解器属于
这一层，MST 和 GSN 是外部校验层。

### 自力与正则化

从匹配渐近展开理解 `eta=mu/M` 的来源，再用 Detweiler--Whiting 分解区分
奇异场和正则场，最后理解 mode-sum 或 effective-source 的大 `l` 渐近。当前
三次标量源是光滑的、指定的固定背景响应，不含点粒子奇异场、规范自由度或
世界线修正，因此不能把其 `A^(1)` 改称 self-force。

### EMRI 与引力波

从 Kerr 测地线的 `Omega_r, Omega_theta, Omega_phi` 开始，把源组织成

```text
omega_mkn = m Omega_phi + k Omega_theta + n Omega_r
```

然后才连接 Teukolsky 模态、通量、耗散/保守自力、绝热和 post-adiabatic 演化。
最终验收量是累积相位，而不是单个径向点的残差。

### 后牛顿、二阶引力与非线性 ringdown

EFT/PN 负责远场慢速展开，二阶 BHPT 负责强场固定背景上的非线性源，
ringdown 还需要正确的 Kerr QNM 双线性投影。实频 Lorentzian 峰拟合只能作为
响应的描述性诊断，不能自动解释为 QNM excitation coefficient。

## 3. 每周可执行的验收循环

```text
1 篇主论文 -> 1 个 convention ledger 条目 -> 1 个核心方程复现
-> 1 个代码/伪代码接口 -> 1 个独立数值检验 -> 1 段适用范围声明
```

当前仓库每轮至少执行：

```powershell
python scripts/build_literature_manifest.py
python scripts/check_literature_catalog.py
python scripts/check_mcp_server.py
python scripts/check_research_setup.py
```

对于当前标量项目，还要运行 PRD 的谱尾、场依赖残差、Wronskian、能流和双重
PDF 构建检查。只有当轨道、源模态、正则化和慢时间相位模块实际实现后，才能
把结果称为 EMRI waveform 或 gravitational self-force。

## 4. 迁移到当前项目的优先顺序

1. 完成 `RadialConvention`，锁定 `lambda`、Fourier sign 和径向变量；
2. 完成 `HomogeneousSolution`，统一 `R_in/R_up`、连接系数和通量；
3. 接入 `OrbitConstants -> Frequencies -> ModeLabel`，先做固定轨道；
4. 在标量模型中区分光滑源响应与真正的奇异点源；
5. 单独建立 `s=-2` 分支，再考虑度规重构和二阶引力源；
6. 最后才把模式误差传播到轨道和累积引力波相位。

机器可检查的门槛见 `learning_gates.json`；论文元数据与当前 PRD 稿件保持分离。
