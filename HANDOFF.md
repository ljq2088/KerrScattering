# Kerr 标量非线性散射：跨设备交接

交接日期：2026-10-23。仓库为公开仓库 `ljq2088/KerrScattering`。
完整工作位于分支 `prd-kerr-scalar-submission`。
用户提供的施瓦西参考稿 `nonlinear_GF.pdf` 保留在原设备；本次上传排除该文件及其内容相同的副本。

## 在新设备上开始

```bash
git clone --branch prd-kerr-scalar-submission https://github.com/ljq2088/KerrScattering.git
cd KerrScattering
python scripts/verify_handoff.py
python -m venv .venv
```

Linux/macOS 用 `source .venv/bin/activate` 激活；Windows PowerShell 用
`.venv\Scripts\Activate.ps1`。完整分析环境使用 Python 3.11 或更新版本：

```bash
python -m pip install -r requirements-research.txt
python -m pytest -q
python scripts/analyze_scalar_precision_20261023.py
```

`verify_handoff.py` 仅使用标准库，核对文件 SHA256、TeX 图表依赖、历史运行记录以及
21 个接受点。它保留失败运行的状态。字节级校验依赖 `.gitattributes` 中的换行规则。
数值汇总重新生成时，图像元数据或字体可能随绘图库和平台变化；交接原件的校验应首先运行。

## 稿件和笔记入口

| 用途 | 文件 |
|---|---|
| 当前完整 PRD 主稿 | [现有 TeX](docs/prd/kerr_scalar_nonlinear_prd_review_20261007.tex) |
| 10 月 23 日 Overleaf 编译的主稿 PDF，26 页 | [PDF](output/overleaf_20261023/prd_narrative_20261023.pdf) |
| 新物理问题的 10 月 17 日草稿 | [TeX](docs/prd/kerr_phase_flux_research_draft_20261017.tex) |
| 10 月 23 日高精度研究增补，9 页 | [PDF](output/pdf/kerr_precision_flux_phase_20261023.pdf)、[TeX](docs/notes/kerr_precision_flux_phase_20261023.tex) |
| 既有完整中文学习笔记 | [PDF](output/pdf/kerr_scalar_learning_notes_zh_20261014_v3.pdf)、[TeX](docs/notes/kerr_scalar_learning_notes_zh_20261014_v3.tex) |
| 施瓦西到 Kerr 的项目推导笔记 | [PDF](output/pdf/schwarzschild_to_kerr_nonlinear_scattering_zh.pdf)、[TeX](docs/notes/schwarzschild_to_kerr_nonlinear_scattering_zh.tex) |
| 历史稿及审阅记录 | [docs/prd](docs/prd/README.md) |

原论文主线为：固定入射条件下的复 Green 响应，连接源加权共振与频率尾部、固定自旋红外极限、
近极端固定失谐下的 principal 模态增强。10 月 23 日修改了引言、极限之间的过渡和结论开头。
摘要及 154 个显示公式、图表环境保持一致，记录见
[editorial_audit.json](output/overleaf_20261023/editorial_audit.json)。
新高精度结果和能流--相位不等式收录在增补笔记中，后续整合由用户审阅决定。

Overleaf 主稿：https://cn.overleaf.com/project/6ad2ac1310f26580d0a7464e

Overleaf 新问题草稿：https://cn.overleaf.com/project/6ad2ac2779800136f13d0172

两个项目需使用有权限的账号登录。GitHub 中的现有主稿源是本轮交接版本。

## 已有结果与新结果

当前物理对象是固定 Kerr 背景上的复标量场，`s=0`，局域非线性为 `|Phi|^(2n) Phi`。
约定为 `G=c=M=1`、`exp(-i omega t+i m phi)`、单位角向范数以及固定渐近入射振幅。
视界和无穷远属于紧化谱网格的精确端点。

既有主稿的主要证据包括：

- `a=0.5,m=0,ell=0,1,2` 的共振峰和频率尾部；有限窗口拟合及窗口敏感性单独报告。
- 固定次极端自旋的红外响应，单极子三次响应趋向 `ln(2)/pi`，高次相互作用具有不同低频幂次。
- 近极端固定 `p/kappa` 的 principal 模态匹配与非线性响应，81 个参数点及零拟合参数的解析比较。
- 27 个精细相位样本以及选定失谐下的能流零点、局部受迫方程残差。

对应数据是 `results/kerr_scalar_*.csv`、`results/kerr_scalar_*20261014.json`，
生成和分析脚本在 `scripts/`；旧稿完整来源与检查记录在 `docs/prd/`。

10 月 23 日新增结果位于 [results/precision_20261023](results/precision_20261023/README.md)：

- 原生 Julia 多子域谱求解器重新构造了标量算子和源投影；采用 BigFloat 残差迭代修正、
  三支独立基底、等龟坐标相位分域及逐单元 Levin 积分。
- 21 个粗细配对点，`a=0.5,m=0`，频率从 `1e-5` 至 `10`；模态和非线性阶数组合见 CSV。
- 粗细位数为 320/384 bit。全部点通过收敛和能流--相位约束，最大配对能流响应相对变化约
  `1.36e-19`，最大采样原方程残差约 `4.51e-62`。
- `omega=10,ell=m=0,n=1` 得到 `R0=2.96352916e-110`、
  `chi=5.49332942e-111`、`phase=9.10841931e-3`。

定义 `rho=chi/2+i*phase`。实际能流分数改变量和相位改变量还要乘小耦合及入射振幅因子。
在实正频率、`p>0`、实局域耦合和正权重自通道下，解析推导给出
`abs(chi)/(2*phase) <= sqrt(R0/T0)`。超辐射区域另行处理符号与约束。
新数据中的 `R1` 由同一积分分解重建，能流平衡属于代数检查。
外部高精度标量参考仍是后续验证项目。

条件性高频预测：固定正自旋的单极子角向极区局域化结合径向 WKB，给出
`phase_n ~ omega^(n-1)`；三次情形在 `a=0.5` 的领先极限为 `1/96`。
保留精确角向积分后，`omega=10,n=1,2,3` 的 WKB 相位与完整计算相差约 `0.21%-0.44%`。
角向独立检查延伸至 `omega=100`，完整径向计算目前止于 `omega=10`。

## 运行高精度代码

新设备安装 Julia 1.10.7 可与原运行时对齐；核心求解器只用 Julia 标准库。
新入口自动使用 PATH 中的 Julia，也接受 `--julia` 或环境变量 `JULIA`。

```bash
julia --startup-file=no --threads=1 scripts/test_scalar_precision_20261023.jl
python scripts/run_scalar_precision.py --case smoke_w01 --omega 0.1 --resolution coarse
python scripts/run_scalar_precision.py --case low_l2_fine --omega 0.00001 --ell 2 --resolution fine
python scripts/run_scalar_precision.py --case high_n3_fine --omega 10 --n 3 --resolution fine --quad 96 --levin 72
```

输出默认在 `results/precision_runs/`，每次使用新目录名。
支持 `--spin --ell --m --n --bits --outer-order --inner-order --quad --levin --timeout --output-root`。
`--dry-run` 显示完整命令，保留已有文件。
每次运行保存参数、运行时版本、输入前后哈希、源码快照、日志和输出哈希。

Windows 调用 WSL 时显式配置发行版和其中的 Julia 路径：

```powershell
python scripts/run_scalar_precision.py --case smoke_wsl --omega 0.1 --wsl-distro Ubuntu-22.04-D --julia /path/to/julia
```

历史日期命名的启动器保留原设备配置用于溯源。跨设备执行使用新入口。
单次默认限时 300 秒、单线程、1.5 GB 内存保护。Linux 检查当前 RSS；其他系统使用 Julia
提供的峰值 RSS。内存保护在求解步骤间检查，较大配置仍应同步观察操作系统内存。
先完成单点，再逐个运行高阶扫描。

全部 21 点复算的参数可从各目录 `manifest.json` 的 `command` 和 `precision` 读取。
旧的 `high_l0_m0_w10_n1_fine` 为内存保护失败记录，对应成功目录是 `retry_l0_m0_w10_n1_fine`。
`power_l0_m0_w5_n2_fine` 为输入变更记录，对应成功目录是 `retry_power_l0_m0_w5_n2_fine`。
这些状态和失败日志均随交接保存。

## 编译现有 TeX

英文主稿依赖 TeX Live 的 REVTeX 4.2；中文笔记使用 XeLaTeX、CTeX 和 Fandol 字体。
仓库已包含本轮审阅使用的 PDF，编译命令如下：

```bash
cd docs/prd
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../../output/pdf kerr_scalar_nonlinear_prd_review_20261007.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../../output/pdf kerr_scalar_nonlinear_prd_review_20261007.tex
cd ../notes
xelatex -interaction=nonstopmode -halt-on-error -output-directory=../../output/pdf kerr_precision_flux_phase_20261023.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=../../output/pdf kerr_precision_flux_phase_20261023.tex
```

历史 `build_prd_review_20261007.py` 和部分笔记生成器会重建旧版本；当前稿直接编译现有源文件。
`nonlinear_GF.pdf` 仅作为文献背景引用，现有 Kerr 主稿的编译依赖已随仓库提供。
Mathematica、MATLAB、GSN、BHPT 及本地 Zotero/MCP 配置属于可选外部参考工具，安装路径需按新设备配置。

## 接下来优先处理

1. 为 `s=0` 极端频率补充外部高精度参考，以及不同积分表示下的独立源投影比较。
2. 加密高频连续采样，区分线性反射、振荡源积分和干涉项的衰减规律；扩大完整径向频率范围，检验 WKB 相位系数。
3. 定位固定 `a=0.5,ell=m=0,n=3` 从低频正响应到高频负响应之间的能流零点。
4. 扩展新高精度方法到近极端非轴对称模态，重新检查固定 `p/kappa` 的相消预算。
5. 有限耦合结论需要二阶受迫场和新增角通道；波包结论需要频率卷积及入射能量归一化。
6. 用户审阅增补笔记后，再决定主稿的物理内容整合和投稿定位。

交接不包含 Julia 安装包、虚拟环境、个人密钥或临时浏览器文件。
源文件与数据的可追溯范围见 [file_manifest_20261023.json](docs/handoff/file_manifest_20261023.json)。
本轮运行与独立检出检查见 [VALIDATION_20261023.md](docs/handoff/VALIDATION_20261023.md)。
