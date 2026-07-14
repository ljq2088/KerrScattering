# 引力理论研究代理能力矩阵

本矩阵把“理论物理学家”拆成可以检查的工作能力。它不是把模型训练成一个
固定知识库，而是规定每次研究任务如何调用本地规则、原始文献、数值代码和
独立验证。

## 能力层

| 层 | 当前能力 | 证据或入口 | 验收标准 |
|---|---|---|---|
| 几何与约定 | Kerr 度规、视界、Killing 能流、Fourier 和 Teukolsky 约定 | `docs/literature/convention_ledger.md`、`docs/prd/` | 写出公式前先声明 signature、单位、频率号、径向变量和通量方向 |
| 黑洞微扰 | `s=0` 标量分离、端点关系、Green 函数和 Wronskian | `src/teukolsky_scalar.py`、`src/kerr_scalar_spectral.py` | 端点残差、场依赖相对残差、谱尾和振幅稳定性同时收敛 |
| Kerr/EMRI 轨道 | 三个基本频率和 `(l,m,k,n)` 模式格点 | `docs/literature/paper_cards.md`、`docs/literature/research_knowledge_graph.md` | 不把单频散射振幅误称为 EMRI 波形；频率映射有独立测试 |
| 辐射反作用 | 无穷远与视界通量、耗散/保守量的区分 | `docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex` | 通量平衡和局部场误差分别报告 |
| 引力自力 | 奇异/正则场分解、规范、mode-sum、puncture 和二阶阶次 | `docs/literature/deep_learning_curriculum.md` | 任何 self-force 结论都标出质量比、规范和正则化方案 |
| 引力波建模 | 绝热、post-adiabatic、多尺度相位和共振 | `docs/literature/gravity_literature_map.md` | 将径向误差、源模态截断、轨道积分误差和累积相位误差分开 |
| 科学软件 | MATLAB、Python、WSL、Wolfram 和 Julia 的可复现实验 | `AGENTS.md`、`tools/mcp/`、`scripts/` | 记录命令、版本、内存峰值、输出路径和 git 提交 |
| 文献研究 | arXiv 元数据、原始论文证据、Zotero 读库、文献卡片 | `scripts/build_literature_manifest.py`、本地 MCP | 每张卡片写清可迁移结论和不相容假设 |
| 论文生产 | REVTeX/PRD、图表、引用、数值和提交门槛 | `scripts/check_prd_*.py` | 两次构建相同，PDF 可视检查通过，作者元数据齐全才称 submission-ready |

## 三条硬边界

1. 固定 Kerr 背景上的标量非线性响应不是引力自力；它没有小质量体、度规扰动、
   奇异场减法或自洽世界线。
2. 单个 Teukolsky 模式的 `B_inc`、`B_ref` 或通量不是 EMRI 波形；EMRI 还需要
   Kerr 轨道、源的 `(l,m,k,n)` 格点、慢时间演化、共振和累积相位。
3. 一个漂亮的谱尾或一个 benchmark 一致性不能单独证明高精度；必须同时检查
   方程残差、端点关系、匹配半径、振幅和物理通量。

## 每次研究任务的闭环

```text
问题定义
  -> 约定块
  -> 原始文献证据
  -> 解析推导
  -> 最小数值实验
  -> 独立验证与误差预算
  -> 研究日志/文献卡片
  -> 论文或下一项实验
```

官方 Codex 结构的依据记录在仓库根目录的 `AGENTS.md`：项目指令使用
`AGENTS.md` 分层，重复工作使用 skill，外部能力通过 MCP 注册。当前项目的
本地实现和运行检查由 `scripts/check_research_setup.py` 统一审计。
