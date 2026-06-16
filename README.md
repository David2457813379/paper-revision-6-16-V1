# 研究复现指南 — Reproducibility Guide

## 论文信息

**标题**: 基于参数化模拟和机器学习的北京酒店建筑EUI预测及EUI-OCEI耦合研究与分析  
**英文标题**: EUI Prediction and Energy–Carbon Coupling Analysis for Beijing Hotel Buildings Using Parametric Simulation and Machine Learning

---

## 目录

1. [系统要求](#1-系统要求)
2. [环境配置](#2-环境配置)
3. [仓库结构](#3-仓库结构)
4. [复现流程](#4-复现流程)
5. [预期输出](#5-预期输出)
6. [常见问题](#6-常见问题)
7. [引用声明](#7-引用声明)
8. [2026-06-15审稿修订验证补充](#8-2026-06-15审稿修订验证补充)
9. [2026-06-16 V1 目录与证据增强](#9-2026-06-16-v1-目录与证据增强)
10. [可选质量检查工具](#10-可选质量检查工具)

---

## 1. 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|---------|---------|
| 操作系统 | Windows 10/11 (64-bit) | Windows 11 (64-bit) |
| Python | 3.11.x | 3.11.5 |
| 内存 | 16 GB | 32 GB |
| 磁盘空间 | 10 GB (含仿真结果) | 50 GB (全量仿真) |
| EnergyPlus | 25.2.0 | 25.2.0 |
| Git | 2.x (可选) | 最新版 |

## 2. 环境配置

### 2.1 Python 环境

```bash
# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows

# 安装核心依赖
pip install numpy==1.26.4 pandas==2.2.2 scipy==1.13.1
pip install matplotlib==3.9.2 seaborn==0.13.2
pip install scikit-learn==1.5.2 statsmodels==0.14.2
pip install xgboost==2.1.1 lightgbm==4.5.0
pip install shap==0.45.0 joblib==1.4.2
pip install jupyter==1.0.0
```

### 2.2 EnergyPlus 安装

1. 从 [EnergyPlus 官方网站](https://energyplus.net/downloads) 下载 EnergyPlus 25.2.0 Windows 安装包
2. 安装至 `C:\EnergyPlusV25-2-0\`
3. 验证安装：
```bash
C:\EnergyPlusV25-2-0\energyplus.exe --version
```
输出应为 `EnergyPlus, Version 25.2.0`

### 2.3 气象文件

- 文件: `input/Beijing.epw`
- 来源: [EnergyPlus Weather Database](https://energyplus.net/weather)
- 数据集: CSWD (Chinese Standard Weather Data)
- 位置: 北京 (WMO Station 545110)

### 2.4 验证环境

```bash
python -c "
import numpy, pandas, scipy, matplotlib, sklearn, xgboost, lightgbm, shap
print('All imports OK')
print(f'Python {numpy.__version__}')
"
```

## 3. 仓库结构

```
论文修改/
├── README.md                                    ← 本文件
├── AGENTS.md                                    ← 项目级工作规范
├── CLAUDE.md                                    ← AI 辅助配置（兼容保留）
│
├── experiment_code/
│   ├── notebooks/
│   │   ├── 01_Parametric_Simulation_Database_Construction.ipynb  ← 步骤1
│   │   ├── 02_SRC_Sensitivity_and_Variable_Selection.ipynb       ← 步骤2
│   │   ├── 03_ML_Model_Training_and_Evaluation.ipynb             ← 步骤3
│   │   └── 04_EUI_OCEI_Coupling_and_Carbon_Analysis.ipynb        ← 步骤4
│   └── original_package/                           ← 原始代码压缩包与解压副本
│
├── input/
│   └── Beijing.epw                              ← 北京气象文件
│
├── data/
│   └── step1_simulation_dataset.csv             ← 步骤1输出（仿真后生成）
│
├── outputs_step1/                               ← 步骤1输出
│   ├── generated_idf/                           ←   自动生成的IDF文件
│   ├── runs/                                    ←   EnergyPlus运行目录
│   └── figures/                                 ←   步骤1图表
│
├── outputs_step2/                               ← 步骤2输出
│   ├── figures/
│   ├── vif_table.csv
│   ├── src_indices_bootstrap.csv
│   └── src_shap_ranking_comparison.csv
│
├── outputs_step3/                               ← 步骤3输出
│   ├── figures/
│   ├── models/                                  ←   训练好的模型文件(.joblib)
│   ├── model_metrics.csv
│   ├── model_hyperparameters.csv
│   └── best_model_params.csv
│
├── outputs_step4/                               ← 步骤4输出
│   ├── figures/
│   ├── ocei_summary_statistics.csv
│   ├── carbon_model_metrics.csv
│   ├── emission_factor_sensitivity.csv
│   └── eui_ocei_factor_compare_bootstrap_src.csv
│
├── paper_assets/
│   ├── figures/                                 ← 论文素材图（工程示意图、流程链路图等）
│   └── previews/                                ← 历史预览图
│
├── reviewer_comments/                           ← 审稿意见、修订方案、回复信和审计记录
│   ├── original_comments/
│   ├── revision_plans/
│   ├── response_letters/
│   ├── audits/
│   └── templates/
│
├── tools/                                       ← 可选质量检查工具，不属于主复现依赖
│   ├── check_repository_quality.py              ← 静态检查代码、图文和输出文件
│   ├── validate_notebooks.py                    ← 按 01→04 顺序执行 Notebook
│   └── README.md                                ← tools 详细说明
│
└── manuscript/                                  ← 修订版论文 Word/Markdown 文件
```

## 4. 复现流程

### ⚠️ 重要提示

- 四个 Notebook 必须**按顺序**运行（01 → 02 → 03 → 04）
- 每个 Notebook 依赖前一步的输出文件
- **随机种子已固定为 42**，保证可复现性
- 复现主流程只依赖 `experiment_code/notebooks/` 中的四个 Notebook；`tools/` 只用于可选质量检查和自动化验证，不会被 Notebook 导入。

### 步骤 1: 参数化仿真数据库构建

**Notebook**: `experiment_code/notebooks/01_Parametric_Simulation_Database_Construction.ipynb`

**功能**:
- 定义 38 个酒店建筑设计参数空间
- 拉丁超立方采样 (LHS) 生成 20000 个设计方案
- 几何可行性筛选（可用面积比 0.55–0.95）
- 自动生成 EnergyPlus IDF 文件
- 调用 EnergyPlus 进行全年能耗仿真
- 工程后处理：理想负荷 → 终端能耗 + EUI 计算

**运行方式**:
```python
# 在 Notebook Cell 1 中修改配置：
CONFIG = {
    "n_samples": 20000,           # LHS 采样数量
    "run_energyplus": True,       # 是否运行 EnergyPlus（首次运行设为 True）
    "energyplus_exe": r"C:/EnergyPlusV25-2-0/energyplus.exe",
    "expandobjects_exe": r"C:\EnergyPlusV25-2-0\ExpandObjects.exe",
}
```

**调试模式**: 设置 `CONFIG["run_energyplus"] = False` 可仅验证 Python 代码逻辑，跳过仿真。

**预期耗时**:
- IDF 生成: ~2 分钟
- 仿真（20000→4640 样本）: ~16–24 小时（取决于 CPU 核心数）
- 建议先用 `n_samples=100` 验证流程通过后再扩大规模

**输出文件**:
- `data/step1_simulation_dataset.csv` — 主数据集（4640行 × 多列）
- `outputs_step1/simulation_log.csv` — 仿真日志
- `outputs_step1/figures/` — 筛选、偏差分解和敏感性分析图
- `paper_assets/figures/` — 工程示意图、研究流程链路图等论文素材图

### 步骤 2: SRC 敏感性分析与变量筛选

**Notebook**: `experiment_code/notebooks/02_SRC_Sensitivity_and_Variable_Selection.ipynb`

**功能**:
- 方向编码（sin/cos 循环特征）
- 多重共线性诊断（VIF）
- 标准化回归系数 (SRC) 估计（1000 次 Bootstrap）
- SHAP 值非线性验证（XGBoost）
- 变量截断阈值分析（累积 |SRC| + CV R² 曲线）
- 选取前 18 个关键变量

**前置条件**: `data/step1_simulation_dataset.csv` 必须存在

**预期耗时**: ~5–10 分钟

**输出文件**:
- `outputs_step2/src_indices_bootstrap.csv` — SRC 排序结果
- `outputs_step2/vif_table.csv` — VIF 共线性诊断
- `outputs_step2/src_shap_ranking_comparison.csv` — SRC vs SHAP 对比
- `outputs_step2/cv_r2_by_variable_count.csv` — 变量数量 vs 预测能力

### 步骤 3: ML 模型训练与比较

**Notebook**: `experiment_code/notebooks/03_ML_Model_Training_and_Evaluation.ipynb`

**功能**:
- 17 种回归模型训练与比较
- 超参数调优（GridSearchCV / RandomizedSearchCV, 10-fold）
- 多项式特征扩展（Poly2, Poly3）
- 泛化能力评估（R², RMSE, MAPE, CV 方差, 泛化间隙）
- 非核心变量固定的影响分析

**前置条件**: 步骤 1 和步骤 2 输出文件必须存在

**预期耗时**: ~ 15–30 分钟（含超参数搜索）

**输出文件**:
- `outputs_step3/model_metrics.csv` — 17 模型性能汇总
- `outputs_step3/model_hyperparameters.csv` — 超参数报告
- `outputs_step3/models/*.joblib` — 训练好的最优模型
- `outputs_step3/best_model_params.csv` — 最佳模型参数

### 步骤 4: EUI-OCEI 耦合与碳分析

**Notebook**: `experiment_code/notebooks/04_EUI_OCEI_Coupling_and_Carbon_Analysis.ipynb`

**功能**:
- 碳排放核算边界定义（电力/天然气/区域供热/区域供冷）
- OCEI 计算与分布分析
- 排放因子敏感性分析（6 情景）
- EUI vs OCEI 排名偏移分析
- EUI 和 OCEI 关键因素对比（SRC）
- 碳强度预测模型训练

**前置条件**: 步骤 1、2、3 输出文件必须存在

**预期耗时**: ~ 5–10 分钟

**输出文件**:
- `outputs_step4/ocei_summary_statistics.csv`
- `outputs_step4/carbon_model_metrics.csv`
- `outputs_step4/emission_factor_sensitivity.csv`
- `outputs_step4/eui_ocei_factor_compare_bootstrap_src.csv`
- `outputs_step4/eui_ocei_rank_shift_summary.csv`

## 5. 预期输出

### 5.1 关键数值结果

| 指标 | 预期值 | 说明 |
|------|--------|------|
| LHS 筛选保留率 | ~23.2% (4640/20000) | 几何可行性筛选 |
| 模拟 EUI 均值 | ~140 kWh/(m²·a) | 与北京实测均值 123 偏差 ~14% |
| SRC 线性模型 R² | ~0.944 | 5-fold CV |
| SRC-SHAP 秩相关 | ~0.89 | Spearman |
| 前18变量累积 |SRC| ~95.8% | |
| 最佳 ML 模型 R² | ~0.997 | Poly3-RidgeCV, test set |
| EUI-OCEI Pearson r | ~0.95 | 强正相关 |
| 排放因子稳健性 | r ∈ [0.938, 0.958] | 6 情景 |

### 5.2 图表清单

| 图号 | 文件 | 内容 |
|------|------|------|
| Fig 1 | `paper_assets/figures/hotel_thermal_engineering_schematic_v4_en.png` | 酒店工程示意图（标准层、立面、系统） |
| Fig 2 | `paper_assets/figures/research_pipeline_workflow_v4_en.png` | 参数化仿真—机器学习—能碳耦合流程链路图 |
| — | `outputs_step1/figures/boundary_sensitivity_analysis.png` | 可行性边界敏感性分析 |
| — | `outputs_step1/figures/bias_stratified_decomposition.png` | 模拟—实测偏差分层分解 |
| — | `feasibility_screening_analysis.png` | 可行性筛选分析（3面板） |
| — | `src_vs_shap_comparison.png` | SRC vs SHAP 排序对比 |
| — | `variable_selection_analysis.png` | 变量筛选截断分析 |
| — | `outputs_step2/figures/shap_divergence_dependence.png` | SRC-SHAP 分歧变量依赖图 |
| — | `outputs_step2/figures/marginal_variable_ablation.png` | 边际变量消融分析 |
| — | `model_test_r2.png` | 模型 R² 比较 |
| — | `outputs_step3/figures/r2_cumulative_decomposition.png` | 代理模型解释度累积贡献分解 |
| — | `emission_factor_sensitivity.png` | 排放因子敏感性 |
| — | `outputs_step4/figures/emission_factor_threshold_analysis.png` | 电力排放因子阈值扫描 |
| — | `eui_ocei_factor_compare.png` | EUI vs OCEI 因素对比 |

## 6. 常见问题

### Q1: EnergyPlus 运行报错 "No thermal mass"
**A**: 这是警告 (Warning) 而非错误。本研究采用 `Material:NoMass` 简化围护结构建模，适用于参数化研究中对成千上万个设计变体进行热负荷比较。该警告不影响能量平衡计算结果。

### Q2: 仿真速度过慢
**A**: 
1. 降低 `n_samples`（建议首次运行用 5-10 个样本验证）
2. 设置 `run_energyplus=False` 仅验证代码逻辑
3. 每个样本的 EnergyPlus 进程独立运行，可利用多核并行（每核约 500MB 内存）

### Q3: 某些样本仿真失败
**A**: 查看 `outputs_step1/simulation_log.csv` 中的 `success` 和 `has_severe_error` 列。常见原因：
- IDF 几何定义错误（ExpandObjects 预处理失败）
- 极度参数组合导致收敛失败
- 磁盘空间不足

### Q4: 模型 R² 异常高（>0.99）
**A**: Poly3-RidgeCV 的 R²=0.997 是在仿真数据上的**代理模型保真度**（Surrogate Fidelity），不代表对真实建筑的预测精度。论文中已将"预测精度"重构为"代理模型保真度"，并包含完整的 Sim-to-Real Transfer Gap 讨论（第 5.2 节）。

### Q5: 如何使用不同的气象文件？
**A**: 替换 `input/Beijing.epw`，并在 Notebook 01 Cell 1 中更新 `CONFIG["weather_epw"]` 路径。

## 7. 引用声明

### 数据来源

| 数据 | 来源 | 引用 |
|------|------|------|
| 北京气象数据 (Beijing.epw) | EnergyPlus Weather Database, CSWD dataset | https://energyplus.net/weather |
| 北京酒店实测能耗 | Chen, Tan & Berardi (2018) | 56 家北京酒店 |
| 国家建筑能耗约束值 | GB/T 51161-2016 | 中国建筑工业出版社 |
| 碳排放因子 — 电力 | 生态环境部 (2022) | 企业温室气体排放核算方法与报告指南 |
| 碳排放因子 — 天然气 | GB/T 51366-2019 | 建筑碳排放计算标准 |
| 碳排放因子 — 区域供热 | Zheng et al. (2018) | Energy and Buildings 179:1-14 |

### 软件引用

- EnergyPlus™ 25.2.0 — U.S. Department of Energy
- Python 3.11.5 — Python Software Foundation
- scikit-learn 1.5.2 — Pedregosa et al. (2011), JMLR 12:2825-2830
- XGBoost 2.1.1 — Chen & Guestrin (2016), KDD 2016
- LightGBM 4.5.0 — Ke et al. (2017), NeurIPS 2017
- SHAP 0.45.0 — Lundberg & Lee (2017), NeurIPS 2017

### 可复现性声明

本研究采用以下措施确保计算可复现性：
1. **固定随机种子**: 所有随机过程（LHS 采样、train/test 分割、交叉验证、模型初始化）均使用 `random_state=42`
2. **版本锁定**: Python 3.11.5、EnergyPlus 25.2.0，依赖库版本记录于 `requirements.txt`
3. **确定性工作流**: 四步 Notebook 按固定顺序执行，每步输出为下一步输入
4. **配置透明**: 所有参数、假设和核算边界在 Notebook markdown cell 中明确记录
5. **诚实声明**: LLM 辅助输出不可逐字节复现；本研究所有定量结果均来自确定性计算代码，不依赖 LLM 生成

---

**最后更新**: 2026-06-16  
**联系**: 详见论文作者信息  
**许可证**: 本代码包仅供学术评审和研究复现使用

---

## 8. 2026-06-15审稿修订验证补充

本次修订针对 MDPI Sustainability 审稿意见，对四个 Notebook 做了逐 Cell 检查、代码修复和本地快速复现实验。每个代码 Cell 前均已新增一段中文说明和一段英文说明，说明内容覆盖该 Cell 的研究目的、输入数据、核心计算、输出文件以及对应审稿意见。

### 8.1 快速验证模式

为避免每次复现实验都触发 20,000 个 LHS 样本和 EnergyPlus 全量仿真，Notebook 现在支持环境变量控制：

```powershell
$env:EUI_FAST_MODE = "1"
$env:EUI_N_SAMPLES = "120"
$env:EUI_RUN_ENERGYPLUS = "0"
jupyter notebook
```

其中：

- `EUI_FAST_MODE=1`：降低 bootstrap、交叉验证和随机搜索的计算量，仅用于代码逻辑和复现流程验证。
- `EUI_N_SAMPLES=120`：设置 Notebook 01 的 LHS 快速样本量。
- `EUI_RUN_ENERGYPLUS=0`：跳过 EnergyPlus 调用，用可复现的代理数据验证 Python 管道。
- `EUI_RUN_ENERGYPLUS=1`：启动真实 EnergyPlus 仿真，仅建议在确认环境无误后运行。

### 8.2 全量仿真模式

正式论文结果仍应使用全量仿真设置：

```powershell
$env:EUI_FAST_MODE = "0"
$env:EUI_N_SAMPLES = "20000"
$env:EUI_RUN_ENERGYPLUS = "1"
jupyter notebook
```

全量模式将产生约 4,640 个几何可行样本，预计需要 16-24 小时，具体取决于 CPU 核数、磁盘速度和 EnergyPlus 并发设置。当前仓库中保留的 116 样本数据用于代码审阅和快速复现，不应替代正式全量仿真数据。

### 8.3 本地验证记录

本次验证环境：

- Python 3.11.5
- NumPy 2.4.3, pandas 3.0.1, SciPy 1.17.1
- scikit-learn 1.8.0, statsmodels 0.14.6
- Matplotlib 3.10.8, seaborn 0.13.2
- SHAP 0.51.0, XGBoost 3.2.0, LightGBM 4.6.0
- Jupyter 内核：Python 3.11

验证方式：使用 `nbclient` 在干净内核中顺序执行四个 Notebook，环境变量为 `EUI_FAST_MODE=1`、`EUI_N_SAMPLES=120`、`EUI_RUN_ENERGYPLUS=0`。四个 Notebook 均已通过执行验证。由于本地 `jupyter nbconvert` 被 `jupyter_contrib_nbextensions` 的旧版依赖阻断，本次采用 `nbclient` 执行验证；该问题属于本地 Jupyter 插件兼容性问题，不影响 Notebook 代码本身。

### 8.4 审稿意见对应的新增输出

本次修订新增或强化的关键输出包括：

- `outputs_step1/feasibility_screening_variable_distribution_shift.csv`：逐变量筛选前后 KS 统计量和 Jensen-Shannon 距离，用于回应可行性筛选选择偏差问题。
- `outputs_step2/src_shap_rank_comparison.csv` 与 `outputs_step2/figures/src_vs_shap_comparison.png`：SRC 与 SHAP 排序一致性验证，用于回应 SRC 线性方法局限。
- `outputs_step2/figures/variable_selection_analysis.png`：18 个关键变量截断的碎石图、累计贡献和 CV 平台证据。
- `outputs_step3/model_hyperparameters.csv`：全部模型最终超参数和搜索策略记录。
- `outputs_step3/noncore_variable_impact.csv`：18 变量与全变量模型性能对比，用于回应非核心变量固定问题。
- `outputs_step4/emission_factor_sensitivity.csv` 与 `outputs_step4/figures/emission_factor_sensitivity.png`：排放因子和电网脱碳情景敏感性分析。
- `outputs_step4/figures/carbon_contribution_dual_view.png`：将原绝对值与归一化碳贡献图合并为双视图图件，回应图表冗余问题。

### 8.5 仍需在论文正文中诚实保留的边界

本代码包已经补足审稿人要求的大部分计算证据，但论文正文和回复信仍应明确承认三项边界：

1. 高 R² 表示 EnergyPlus 仿真数据上的代理模型保真度，不等同于真实酒店建筑预测精度。
2. 当前模型尚无逐栋真实酒店运行数据校准，Sim-to-Real Transfer Gap 仍是最重要限制。
3. 酒店星级、运营水平、入住率行为和设备管理策略未被显式分类，模型外推到不同酒店档次时需要谨慎。

## 9. 2026-06-16 V1 目录与证据增强

本版本将工作区整理为五类核心材料：`experiment_code/` 存放四个实验 Notebook，`reviewer_comments/` 存放审稿意见与回复材料，`manuscript/` 存放论文正文，`paper_assets/` 存放非中间计算输出的论文素材图，`outputs_step1/` 至 `outputs_step4/` 保持为四步实验输出目录。Notebook 已加入项目根目录自动识别逻辑，因此从仓库根目录或 `experiment_code/notebooks/` 中启动均会把输出写回根目录下的标准输出文件夹。

为保持评审复现路径简洁，GitHub 提交版的主流程不依赖任何外部 `tools` 脚本。工程示意图和研究流程链路图的生成函数已经内嵌在 `01_Parametric_Simulation_Database_Construction.ipynb` 中；四个 Notebook 按 01 → 02 → 03 → 04 顺序运行即可完成主流程。根目录 `tools/` 仅作为可选质量检查工具箱，用于修改代码后快速发现语法、英文图文、输出文件和跨 Notebook 依赖问题。

本版本进一步加入面向审稿说服力的补充分析：

- `outputs_step1/boundary_sensitivity_results.csv` 与 `outputs_step1/figures/boundary_sensitivity_analysis.png`：检验可行面积比边界从 0.50–0.97 到 0.60–0.90 时样本保留率、EUI 均值和分布漂移，回应筛选阈值是否任意的问题。
- `outputs_step1/bias_stratified_decomposition.csv` 与 `outputs_step1/figures/bias_stratified_decomposition.png`：按 DHW、窗墙比、建筑层数和 HVAC 效率分层展示模拟—实测 EUI 偏差，避免只用总体均值回应 Sim-to-Real Gap。
- `outputs_step2/shap_src_divergence_incremental_r2.csv` 与 `outputs_step2/figures/shap_divergence_dependence.png`：识别 SRC 与 SHAP 排名分歧最大的变量，并用增量 R² 解释非线性补充价值。
- `outputs_step2/marginal_variable_ablation.csv` 与 `outputs_step2/figures/marginal_variable_ablation.png`：逐一移除第 15–18 个边际变量，检验 18 变量截断是否只是机械阈值。
- `outputs_step3/r2_cumulative_decomposition.csv` 与 `outputs_step3/figures/r2_cumulative_decomposition.png`：按物理变量组分解代理模型 R² 累积贡献，说明高 R² 主要来自仿真机制的结构化可解释性，而不是信息泄漏。
- `outputs_step4/emission_factor_threshold_sweep.csv` 与 `outputs_step4/figures/emission_factor_threshold_analysis.png`：扫描电力排放因子从 0.15 到 0.75 kgCO2e/kWh 的变化，识别电网脱碳路径下 EUI-OCEI 耦合结构的稳定区间和转折风险。

快速验证命令如下：

```powershell
$env:EUI_FAST_MODE = "1"
$env:EUI_N_SAMPLES = "200"
$env:EUI_RUN_ENERGYPLUS = "0"
python -m jupyter notebook experiment_code/notebooks
```

正式复现实验仍应使用 `EUI_FAST_MODE=0`、`EUI_N_SAMPLES=20000`、`EUI_RUN_ENERGYPLUS=1`，并确认 `C:/EnergyPlusV25-2-0/energyplus.exe` 可用。

## 10. 可选质量检查工具

`tools/` 的定位是“投稿前自检”和“代码修改后回归验证”，不是论文代码的第五部分。评审或读者复现论文时仍只需运行四个 Notebook。

### 10.1 静态质量检查

```powershell
python tools/check_repository_quality.py
```

该脚本检查四类问题：

1. 四个 Notebook 代码单元是否存在 Python 语法错误。
2. 代码单元是否残留中文图表文本、全角符号、特殊 dash、上标字符或中点单位符号。
3. 四个 Notebook 是否错误依赖可选 `tools/`。
4. `outputs_step1/` 至 `outputs_step4/` 和 `paper_assets/` 中的 CSV、TXT、SVG、JSON、MD 是否残留中文字符。

### 10.2 快速执行验证

```powershell
python tools/validate_notebooks.py --fast --samples 200
```

该脚本会设置 `EUI_FAST_MODE=1`、`EUI_N_SAMPLES=200`、`EUI_RUN_ENERGYPLUS=0`，然后按 `01 → 02 → 03 → 04` 顺序执行四个 Notebook。它适合用于确认 Python 逻辑、绘图、文件读写、跨 Notebook 依赖和空结果分支均不报错。

如需在小样本验证中允许 EnergyPlus 参与运行，可使用：

```powershell
python tools/validate_notebooks.py --fast --samples 200 --run-energyplus
```

验证日志保存在：

```text
archive/validation/
```

该目录默认不提交到 GitHub，仅作为本地调试证据。
