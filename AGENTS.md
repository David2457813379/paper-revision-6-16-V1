# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

Research paper: "基于参数化模拟和机器学习的北京酒店建筑EUI预测及EUI-OCEI耦合研究与分析" (Research and Analysis on EUI Prediction and EUI-OCEI Coupling of Beijing Hotel Buildings Based on Parametric Simulation and Machine Learning).

This is a reproducible computational research pipeline that combines building energy simulation (EnergyPlus) with machine learning to predict hotel building EUI and analyze EUI-OCEI coupling relationships in Beijing.

## Repository Structure

The code package (`Code_Package_EUI_OCEI_Beijing_Hotel.zip`) contains four Jupyter notebooks run sequentially, plus a weather data file:

```
Code_Package_EUI_OCEI_Beijing_Hotel/
├── 01_LHS_EnergyPlus_Pipeline.ipynb    # Parametric sampling & simulation
├── 02_SRC_Sensitivity_Analysis.ipynb   # Sensitivity analysis
├── 03_EUI_Model_Training_and_Comparison.ipynb  # ML model training
├── 04_EUI_OCEI_Coupling_Analysis.ipynb # EUI-OCEI coupling analysis
├── Beijing.epw                         # Weather file for EnergyPlus
└── README.txt
```

## Sequential Pipeline Architecture

Each notebook depends on outputs from the previous step. The pipeline is strictly linear — later notebooks should only be run after prior outputs exist.

### Step 1 — LHS + EnergyPlus (`01_LHS_EnergyPlus_Pipeline.ipynb`)
- Defines hotel building parameter space (geometry, envelope, HVAC, etc.)
- Generates Latin Hypercube Sampling (LHS) samples via `scipy.stats.qmc`
- Screens physically feasible hotel layouts
- Launches EnergyPlus 25.2.0 simulations via `subprocess` calls
- Extracts annual energy results from EnergyPlus SQLite output databases
- Outputs → `outputs_step1/` (sampled parameter datasets, simulation summaries, EUI datasets)

### Step 2 — SRC Sensitivity Analysis (`02_SRC_Sensitivity_Analysis.ipynb`)
- Loads the EUI simulation dataset from Step 1
- Preprocesses variables (including orientation encoding)
- Checks multicollinearity with VIF (Variance Inflation Factor)
- Estimates Standardized Regression Coefficients (SRC) via `sklearn.linear_model.LinearRegression`
- Uses bootstrap resampling for confidence intervals and sign-stability assessment
- Selects key variables for downstream ML modeling
- Outputs → `outputs_step2/` (VIF tables, SRC results, bootstrap CI results, key-variable lists, figures)

### Step 3 — ML Model Training & Comparison (`03_EUI_Model_Training_and_Comparison.ipynb`)
- Loads the reduced dataset (key variables only) from Step 2
- Trains and compares 12+ regression models: LinearRegression, RidgeCV, LassoCV, ElasticNetCV, KNeighborsRegressor, SVR, DecisionTreeRegressor, RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor, XGBoost (`XGBRegressor`), LightGBM (`LGBMRegressor`), MLPRegressor, PolynomialFeatures + LinearRegression
- Uses `GridSearchCV` and `RandomizedSearchCV` for hyperparameter tuning
- Evaluates with R², cross-validation variance, RMSE, MAPE
- Uses `SimpleImputer` for missing data and `Pipeline` for preprocessing chains
- Outputs → `outputs_step3/` (evaluation tables, CV results, predicted-vs-simulated plots, model summaries)

### Step 4 — EUI-OCEI Coupling (`04_EUI_OCEI_Coupling_Analysis.ipynb`)
- Maps EnergyPlus end-use results to energy carriers (electricity, natural gas, district heating, district cooling)
- Applies carrier-specific carbon emission factors
- Calculates total operational carbon emissions and OCEI
- Analyzes energy-carrier contributions to carbon emissions
- Examines EUI-OCEI correlation (`scipy.stats.pearsonr`)
- Compares EUI-based and OCEI-based building rankings
- Compares SRC patterns between EUI and OCEI
- Outputs → `outputs_step4/`

## Python Environment

- **Python version**: 3.11.5
- **Core dependencies**: `numpy`, `pandas`, `scipy`, `matplotlib`, `scikit-learn`, `statsmodels`
- **ML libraries**: `xgboost`, `lightgbm`, `seaborn`, `joblib`
- **External tool**: EnergyPlus 25.2.0 (`C:/EnergyPlusV25-2-0/energyplus.exe`)

## ⚠️ 本地运行要求（强制）

**所有代码必须在用户本地Python环境和Jupyter Notebook中实际运行验证，不得仅在理论层面分析代码正确性。**

- 每次编写或修改代码后，必须在本地环境执行以确认无语法错误、无缺失依赖、无运行时异常。
- 运行前检查：Python 3.11.5, 所需库是否安装, EnergyPlus路径是否正确。
- 若本地运行报错，优先修复错误后重新运行，直到通过为止。

## Running the Pipeline

1. Extract the zip: `unzip Code_Package_EUI_OCEI_Beijing_Hotel.zip`
2. Run notebooks in order: 01 → 02 → 03 → 04
3. Before running Step 1, verify the EnergyPlus executable path in the notebook matches the local installation
4. Ensure `Beijing.epw` is in the working directory alongside the notebooks
5. Output directories (`outputs_step1/` through `outputs_step4/`) are auto-created by notebook code
6. **调试模式**: 设置 CONFIG["run_energyplus"] = False 可跳过EnergyPlus仿真仅验证Python代码逻辑

## Key Technical Details

- **Random seeds** are used throughout for reproducibility (LHS sampling, train/test splits, CV folds, model initialization)
- **EnergyPlus outputs** are read via `sqlite3` from the simulation `.sql` database files
- **Orientation encoding**: categorical building orientation is encoded numerically before regression
- **Multicollinearity screening**: VIF threshold applied before SRC estimation
- **Bootstrap resampling** (Step 2): quantifies uncertainty in SRC estimates and assesses sign stability
- **Cross-validation**: `KFold` cross-validation used in both SRC estimation and ML model evaluation

---

## 📋 审稿意见完整对照清单（Reviewer Comments Master Checklist）

> **来源**: Sustainability 期刊投稿系统 (MDPI Susy)  
> **审稿人数量**: 3人（Reviewer 1: Major Revision; Reviewer 2: Minor Revision; Reviewer 3: Minor Revision）  
> **最后更新**: 2026-06-15  
> **状态说明**: ✅ 已完成 | 🔄 进行中 | ⏳ 待处理 | ❌ 被否决/不需要

---

### 🔴 Reviewer 1 — Major Comments（8项）

#### R1-MAJ-1: 缺少真实建筑数据验证 / Sim-to-Real Transfer Gap
- **原文**: "All ML models are trained and tested purely on EnergyPlus outputs... Please either benchmark the simulated EUI range against published Beijing hotel data or reframe all accuracy claims as surrogate fidelity, and add a frank discussion of the sim-to-real transfer gap."
- **定位**: 论文Abstract + 第4.1节 + 第5.2节; 代码 `01_...ipynb` Cell 13 (`f30cde1e`)
- **已完成**: ✅ NB01 新增 EUI vs Chen, Tan & Berardi (2018) 北京56家酒店实测对比图 + GB/T 51161国标约束值; ✅ Abstract "prediction accuracy"→"surrogate fidelity"; ✅ 论文第5.2节新增 Sim-to-Real Transfer Gap 讨论
- **待处理**: ⏳ 审稿人建议引用 Sheng et al. (2018) [Ref.53] 作为对标起点——需核实该文献; ⏳ 模拟EUI均值143.1 vs 实测123偏差约14%，需在论文中诚实陈述
- **涉及文件**: `01_...ipynb`, 论文 Abstract/§4.1/§5.2

#### R1-MAJ-2: 可行性筛选77%剔除率的合理性论证
- **原文**: "The feasibility screening cut 20,000 LHS samples down to 4,640 — a 77% rejection rate... Please justify the 0.55–0.95 bounds, show distribution before and after filtering, discuss whether this introduces selection bias."
- **定位**: 代码 `01_...ipynb` Cell `fe5b259b`; 论文第3.2.2节
- **已完成**: ✅ NB01 新增3面板可行性筛选分析图（预筛选直方图 + 筛选前后密度图 + 2D参数覆盖散点图 + KS检验); ✅ 论文论证0.55下界(GB 50189-2015)和0.95上界(核心筒最低占比); ✅ 引 Zhang et al. (2024) 和 Permana et al. (2023) 可比区间
- **待处理**: ⏳ 审稿人要求 "hotel survey data" 作为依据——需补充北京酒店实际面积分配调研数据或说明为何调研数据不可得
- **涉及文件**: `01_...ipynb`, 论文§3.2.2

#### R1-MAJ-3: SRC线性方法与非线性响应的矛盾
- **原文**: "SRC is a linear method, yet the authors argue that the EUI response surface is 'substantially nonlinear'... Please acknowledge this limitation and consider supplementing with a nonlinear method (Sobol indices or SHAP values)."
- **定位**: 代码 `02_...ipynb` Cell `319ecff6` (SHAP) + Cell `76427c99` (变量截断); 论文第3.3.4节
- **已完成**: ✅ NB02 新增完整SHAP分析（XGBoost→TreeExplainer→SHAP→与SRC排序对比); ✅ Spearman秩相关=0.891, Jaccard=0.80; ✅ 并排SRC/SHAP对比图; ✅ SRC局限性诚实声明
- **待处理**: ⏳ 审稿人提及 Sobol indices——可考虑补充但非强制（SHAP已满足非线性验证需求）; ⏳ 论文需明确承认"SRC在此中等非线性条件下仍可靠"的边界条件
- **涉及文件**: `02_...ipynb`, 论文§3.3.4/§4.2.2/§5.3

#### R1-MAJ-4: 碳排放因子无引用来源 / 敏感性分析缺失
- **原文**: "The OCEI analysis rests on four emission factors in Table 5 with no cited source, reference year, or jurisdictional basis... Please cite the source and vintage of each factor, and run a brief sensitivity analysis."
- **定位**: 代码 `04_...ipynb` Cell `60cf2997` (来源说明) + Cell `1657814c` (敏感性分析); 论文表5/§3.5.2/§4.4.4
- **已完成**: ✅ NB04 新增完整排放因子来源表（电力=生态环境部2022指南, 天然气=GB/T 51366-2019, 区域供热=Zheng et al. 2018, 区域供冷=COP反算推导); ✅ 6情景敏感性分析（Baseline/Low El 0.40/High El 0.70/Grid Decarb 2030/Grid Decarb 2050/High DH）; ✅ Tornado双面板图
- **待处理**: ⏳ 审稿人要求 electricity factor varied across 0.4-0.7 ——已覆盖(0.40/0.55/0.70); ⏳ 需确认0.16区域供冷排放因子的推导过程在论文中有清晰阐述
- **涉及文件**: `04_...ipynb`, 论文表5/§3.5.2/§4.4.4

#### R1-MAJ-5: EnergyPlus模型可复现性描述不足
- **原文**: "The EnergyPlus model is not described in enough detail for anyone to reproduce... base-case geometry template, HVAC system type, DHW system configuration, occupancy schedule profiles, weather file are all missing."
- **定位**: 代码 `01_...ipynb` Cell `ea93372a` (模型可复现性文档); 论文第3.2.3节
- **已完成**: ✅ NB01 新增Markdown Cell详细描述: (1)几何模板=单区矩形棱柱 (2)HVAC=IdealLoadsAirSystem (3)DHW=解析计算(完整公式) (4)人员=min(room_count×1.6, floor_area×occupancy) (5)运行时间表=简化分数 (6)Beijing.epw=CSWD+官方链接 (7)围护结构=Material:NoMass (8)版本=25.2.0+ExpandObjects
- **待处理**: ⏳ 审稿人要求补充"occupancy schedule profiles"——当前使用简化分数而非逐时schedule，需在论文中说明简化理由; ⏳ 需确认TMY具体年份（CSWD数据集的基础年份）
- **涉及文件**: `01_...ipynb`, 论文§3.2.3

#### R1-MAJ-6: 引用错误 + 统计表述不当
- **原文**: "Reference [3] on line 47 is cited as '[0],' and the claim that hotels 'account for over 45% of total building energy consumption' looks like it conflates hotels with all commercial buildings."
- **定位**: 论文第1节 Line 47
- **已完成**: ✅ [0]→[3] (Chung & Park, 2015, Energy 92:383-393); ✅ "accounting for over 45% of total building energy consumption"→"hotels consume more energy per unit floor area than most other commercial building types"
- **待处理**: ⏳ 全文扫描所有引用标签确保无类似[0]错误
- **涉及文件**: 论文§1

#### R1-MAJ-7: ML超参数调优未报告
- **原文**: "Seventeen ML models are compared, but hyperparameter tuning is never described... Please report the tuning strategy and final hyperparameters, at least for the top five models."
- **定位**: 代码 `03_...ipynb` Cell `23c3095c` (超参数报告); 论文Table 5 + Supplementary Table S1
- **已完成**: ✅ NB03 新增 extract_best_params() 函数自动提取最优参数; ✅ 前5名模型详细超参数+搜索空间输出; ✅ 全17模型最优参数存为 model_hyperparameters.csv
- **待处理**: ⏳ 论文需添加超参数表格（可放入补充材料）; ⏳ 审稿人质疑KNN R²=0.68和RF R²=0.83"surprisingly weak"——需在论文中解释（仿真数据高度结构化→线性模型天然占优→树模型反而需要更多数据）
- **涉及文件**: `03_...ipynb`, 论文表5/补充材料

#### R1-MAJ-8: 18变量截断阈值缺乏论证
- **原文**: "The cutoff at 18 'key' variables is never explicitly justified. Variables 15-18 have SRC magnitudes below 0.03... Please clarify why the line was drawn at 18 rather than at a natural break."
- **定位**: 代码 `02_...ipynb` Cell `76427c99` (变量截断分析); 论文第3.3.5/4.2.3/5.3节
- **已完成**: ✅ NB02 新增3面板定量分析图: (1)SRC碎石图(前18红色/其余蓝色) (2)累积|SRC|贡献曲线(标注90%/95%) (3)5折CV R² vs 变量数量曲线(标注峰值)
- **待处理**: ⏳ 三条独立证据线需在论文中明确表述（前18贡献95.8% + CV R²在18处平台 + 碎石图18后平缓）; ⏳ 需讨论移除变量15-18(equip_power/heat_set/room_area/u_wall)是否会损害模型
- **涉及文件**: `02_...ipynb`, 论文§3.3.5/§4.2.3/§5.3

---

### 🟡 Reviewer 1 — Minor Comments（9项）

#### R1-MIN-1: 论文标题过长
- **原文**: "The title is excessively long and acronym-heavy."
- **已完成**: ✅ 29词→15词: "EUI Prediction and Energy–Carbon Coupling Analysis for Beijing Hotel Buildings Using Parametric Simulation and Machine Learning"
- **涉及文件**: 论文标题

#### R1-MIN-2: 断裂的交叉引用
- **原文**: "Line 121 contains 'Error! Reference source not found.' — a broken cross-reference"
- **已完成**: ✅ 修复全部Word交叉引用字段
- **涉及文件**: 论文全文

#### R1-MIN-3: 语态不统一
- **原文**: "First-person plural 'we' inconsistently alongside passive voice"
- **已完成**: ✅ 全文统一为被动语态/第三人称
- **涉及文件**: 论文全文

#### R1-MIN-4: 章节编号跳跃
- **原文**: "Section numbering appears to jump from '2. Results' to '3. Results' without a clear Section 3 header"
- **已完成**: ✅ 核实并修正所有章节编号连续性
- **涉及文件**: 论文全文

#### R1-MIN-5: 图表15和16冗余
- **原文**: "Figures 15 and 16 present the same information in absolute and normalized forms — consolidate into a single dual-axis or stacked figure"
- **已完成**: ✅ 论文文本中改为 "consolidated dual-view stacked figure"
- **待处理**: ⏳ 代码中需重新生成合并后的堆叠图
- **涉及文件**: `04_...ipynb`, 论文§4.4.1

#### R1-MIN-6: "crystal transparency"术语误译
- **原文**: "The term 'crystal transparency' appears to be a mistranslation — replace with standard terminology"
- **已完成**: ✅ 从摘要中删除，改用标准学术表述
- **涉及文件**: 论文Abstract

#### R1-MIN-7: 窗户构造类型未定义
- **原文**: "Table 1 lists 'Window construction type number: 1–3' but never defines what Types 1, 2, and 3 represent"
- **已完成**: ✅ 表1脚注+第3.2.3节: Type 1=双层透明(U≈1.8,SHGC≈0.55); Type 2=双层Low-E(U≈1.4,SHGC≈0.40); Type 3=三层Low-E(U≈0.8,SHGC≈0.25)
- **涉及文件**: 论文表1/§3.2.3

#### R1-MIN-8: 酒店类别局限性的深入讨论
- **原文**: "Hotel category (star rating) was not distinguished... energy intensity varies by a factor of two or more between budget and luxury hotels. Please elevate this point and discuss implications for model transferability."
- **已完成**: ✅ 第5.3节新增约200字专段讨论
- **待处理**: ⏳ 审稿人认为这是"significant limitation"而非minor issue——需提升至局限性讨论的核心位置
- **涉及文件**: 论文§5.3

#### R1-MIN-9: 2026年参考文献核实
- **原文**: "Several references are dated 2026 (Refs. [17], [29]) — please verify their publication status"
- **已完成**: ✅ 核实 Echarri-Iribarren et al. (Buildings 2026, 16, 863) 和 Solmaz (Buildings 2026, 16, 779) 均为2026年已发表文献
- **涉及文件**: 论文References

---

### 🟠 Reviewer 2 — Comments（5项，Minor Revision）

#### R2-1: 筛选后的样本代表性与选择偏差
- **原文**: "It is not entirely clear whether this substantial reduction in sample size may introduce bias into the parameter distributions. Additional discussion on the representativeness of the retained samples."
- **定位**: 代码 `01_...ipynb` Cell `fe5b259b` (可行性筛选分析)
- **已完成**: ✅ 2D散点覆盖图验证筛选未系统性排斥参数空间; ✅ KS检验量化筛选前后差异
- **待处理**: ⏳ 需量化每个输入变量的筛选前后分布差异（可用KS统计量或Jensen-Shannon距离）; ⏳ 论文需讨论样本量从4640进一步减少对统计功效的影响
- **涉及文件**: `01_...ipynb`, 论文§3.2.2/§5.3

#### R2-2: SRC vs 更高级全局敏感性方法的论证
- **原文**: "It would be helpful to justify why SRC was selected over more advanced global sensitivity analysis approaches such as Sobol indices or SHAP-based interpretation methods."
- **定位**: 代码 `02_...ipynb` Cell `319ecff6` (SHAP验证) + Markdown Cell `ece3519b`
- **已完成**: ✅ SHAP值排序与SRC交叉验证(秩相关0.891); ✅ 论文新增SRC线性假设局限讨论
- **待处理**: ⏳ 论文需从方法论角度说明SRC的选择理由: (a)计算成本(Sobol需n×数千次仿真) (b)可解释性(SRC直接对应变量→EUI的边际效应) (c)SHAP已作为非线性补充验证
- **涉及文件**: `02_...ipynb`, 论文§3.3/§5.3

#### R2-3: ML预测性能异常高的信息泄漏风险
- **原文**: "The reported predictive performance is exceptionally high (R² approaching 0.998, MAPE near 1.3–1.4%). It remains unclear whether the training and testing strategy fully avoids information leakage."
- **定位**: 代码 `03_...ipynb` Cell `86e190c0` (模型比较) + Cell `1de98079` (非核心变量影响)
- **已完成**: ✅ 固定随机种子(42); ✅ 80/20 train/test split; ✅ 10-fold CV; ✅ 泛化间隙分析; ✅ 非核心变量固定影响分析
- **待处理**: ⏳ 需求补充: (a)数据分割的详细流程图 (b)特征标准化是否在split之前执行的明确声明(当前使用Pipeline确保在split之后) (c)所有数据来自EnergyPlus仿真的事实再次强调——R²=0.998只是代理模型保真度
- **涉及文件**: `03_...ipynb`, 论文§4.3/§5.2

#### R2-4: 非核心变量固定的影响
- **原文**: "Fixing non-core variables may artificially reduce variability in the dataset and potentially inflate predictive performance. Discuss how this simplification affects model generalizability."
- **定位**: 代码 `03_...ipynb` Cell `1de98079` (非核心变量影响分析)
- **已完成**: ✅ 全39变量 vs 18变量对比（Poly3-RidgeCV和XGBoost delta<0.001）
- **待处理**: ⏳ 需说明18变量模型在早期设计阶段的实用性优势（非核心参数在概念设计阶段尚未确定）
- **涉及文件**: `03_...ipynb`, 论文§5.3

#### R2-5: OCEI对电网脱碳路径的敏感性
- **原文**: "The carbon accounting framework appears highly dependent on selected emission factors. Additional discussion regarding sensitivity to future grid decarbonization pathways would improve practical significance."
- **定位**: 代码 `04_...ipynb` Cell `1657814c` (排放因子敏感性分析)
- **已完成**: ✅ 6情景敏感性分析(含 Grid Decarb 2030 0.40 和 Grid Decarb 2050 0.25)
- **待处理**: ⏳ 需在论文中讨论: 随着电网脱碳→电力碳排放因子下降→电力在OCEI中的占比下降→天然气(DHW)占比相对上升→EUI-OCEI耦合结构随时间演变
- **涉及文件**: `04_...ipynb`, 论文§4.4.4/§5.4

---

### 🟢 Reviewer 3 — Comments（9项，Minor Revision）

#### R3-1: 创新点与贡献不清晰
- **原文**: "Clarify the novelty and unique contribution of the proposed framework more clearly."
- **已完成**: ✅ 引言末尾增加三点独立贡献声明: (1)酒店建筑系统变量筛选框架(DHW主导+SRC/SHAP双方法) (2)17模型全超参数基准 (3)单指标→双指标+不确定性
- **涉及文件**: 论文§1末尾

#### R3-2: 引用和格式错误
- **原文**: "Remove citation and formatting errors throughout the manuscript."
- **已完成**: ✅ 修复[0]→[3], 全部断裂交叉引用, 统一格式
- **涉及文件**: 论文全文

#### R3-3: 文献综述过长/研究空白不突出
- **原文**: "Condense the literature review and focus more on research gaps."
- **已完成**: ✅ 第2节从~3000字压缩至~1800字, 重构为5个子节: (1)酒店能耗与影响因素 (2)代理建模 (3)能碳耦合 (4)研究假设 (5)研究框架
- **涉及文件**: 论文§2

#### R3-4: 20,000→4,640的削减解释不足
- **原文**: "Provide more explanation regarding the reduction from 20,000 to 4,640 samples."
- **定位**: 代码 `01_...ipynb` Cell `fe5b259b`; 论文§3.2.2
- **已完成**: ✅ 3面板分析图 + KS检验
- **待处理**: ⏳ 与R1-MAJ-2和R2-1有重叠，需统一回复; ⏳ 需用更直观的语言解释"6个几何变量独立采样→23%组合几何可行"的概率逻辑
- **涉及文件**: `01_...ipynb`, 论文§3.2.2

#### R3-5: 关键变量选择标准需进一步论证
- **原文**: "Further justify the selection criteria for the final key variables."
- **定位**: 代码 `02_...ipynb` Cell `76427c99` (变量截断分析)
- **已完成**: ✅ SRC碎石图+累积贡献曲线+CV R²曲线三条证据线
- **待处理**: ⏳ 与R1-MAJ-8重叠，需以更系统化的方式呈现（三条独立证据线的定量结果列表）
- **涉及文件**: `02_...ipynb`, 论文§3.3.5

#### R3-6: 改善图表分辨率和标签可读性
- **原文**: "Improve figure resolution and enhance readability of labels and axes."
- **定位**: 所有4个Notebook的matplotlib设置
- **已完成**: ✅ 统一rcParams (dpi=150/300, font.size=11); ✅ bbox_inches='tight' 全部图; ✅ 中文字体自动检测
- **待处理**: ⏳ 需逐图检查: (a)标签是否截断 (b)图例是否遮挡数据 (c)坐标轴标题是否完整 (d)颜色是否对色盲友好
- **涉及文件**: 所有Notebook

#### R3-7: 明确ML模型的假设和参数设置
- **原文**: "Clarify assumptions and parameter settings used in machine learning models."
- **定位**: 代码 `03_...ipynb` Cell `23c3095c` (超参数报告) + Cell `53fde42e` (说明)
- **已完成**: ✅ 超参数报告+搜索空间; ✅ 预处理步骤说明(Pipeline: Imputer→Scaler→Model)
- **待处理**: ⏳ 与R1-MAJ-7重叠; ⏳ 需在论文中以表格形式呈现所有模型的最终超参数
- **涉及文件**: `03_...ipynb`, 论文补充材料

#### R3-8: 添加限制条件章节
- **原文**: "Add a brief limitations section discussing model generalizability."
- **已完成**: ✅ 第5节重构为5个子节，其中第5.3节系统覆盖5项限制
- **涉及文件**: 论文§5

#### R3-9: 扩展实践与工程意义讨论
- **原文**: "Expand the discussion on practical and engineering implications of the findings."
- **已完成**: ✅ 第5.4节独立成节: (1)快速筛选: 仿真数小时→代理模型毫秒级 (2)DHW优先优化级 (3)双指标政策建议: EUI-only规范无法实现等比例碳减排
- **待处理**: ⏳ 考虑增加定量案例: 用一个具体酒店设计方案展示代理模型的实际使用流程
- **涉及文件**: 论文§5.4

---

### 📊 跨审稿人共同关注的交叉问题

#### CROSS-1: 模拟到真实的泛化差距（Sim-to-Real Gap）
- **审稿人**: R1-MAJ-1 + R2-3 + R3-8
- **严重程度**: 🔴 最高优先级
- **综合状态**: ✅ 已添加实测对标图; ✅ 已重构精度声明; 🔄 需在Discussion中集中讨论三项限制的交互效应（无实测验证 + 理想化HVAC + 单区简化）

#### CROSS-2: 可行性筛选的合理性（Feasibility Screening）
- **审稿人**: R1-MAJ-2 + R2-1 + R3-4
- **严重程度**: 🔴 最高优先级
- **综合状态**: ✅ 已添加筛选分析图; ✅ 已引用规范和文献; 🔄 需补充各输入变量筛选前后的分布差异量化

#### CROSS-3: SRC方法论的充分性（SRC Adequacy）
- **审稿人**: R1-MAJ-3 + R2-2
- **严重程度**: 🟠 高优先级
- **综合状态**: ✅ SHAP验证已添加; ✅ 局限性已承认; 🔄 需清晰说明为何选择SRC（计算成本+可解释性）并补充非线性验证

#### CROSS-4: 变量筛选的合理性（Variable Selection）
- **审稿人**: R1-MAJ-8 + R3-5
- **严重程度**: 🟡 中优先级
- **综合状态**: ✅ 三条定量证据线已建立; 🔄 需在论文中以更系统化的方式呈现

#### CROSS-5: 碳排放因子的可靠性（Carbon Factor Reliability）
- **审稿人**: R1-MAJ-4 + R2-5
- **严重程度**: 🟠 高优先级
- **综合状态**: ✅ 来源表+敏感性分析已添加; 🔄 需讨论时间演变(EUI-OCEI耦合结构随电网脱碳的变化)

#### CROSS-6: 语言与格式（Language & Formatting）
- **审稿人**: R1-MIN(1,2,3,4,6) + R3-2
- **严重程度**: 🟢 低优先级
- **综合状态**: ✅ 标题已缩短; ✅ 引用已修复; ✅ 语态已统一; ✅ "crystal transparency"已删除; 🔄 需全文最终英文润色

---

### 📁 代码层面的待修复问题（Code-Level Remaining Issues）

#### CODE-1: 仿真数据集不完整
- **问题**: 当前仅有116个样本（2.5%），完整数据集需4640个样本
- **修复**: 运行 NB01 设置 `CONFIG["n_samples"]=20000, CONFIG["run_energyplus"]=True`
- **预计耗时**: 16-24小时（取决于CPU核心数）
- **涉及文件**: `01_...ipynb`

#### CODE-2: 图片文字重叠风险
- **问题**: 部分图表存在标签截断、图例遮挡、变量名旋转角度不足
- **修复**: 逐图检查并用 `fig.tight_layout(pad=...)` 和 `bbox_inches='tight'` 微调
- **涉及文件**: 所有4个Notebook的绘图Cell

#### CODE-3: 双语Cell注释缺失
- **问题**: 每个代码Cell缺少中英双语的详细注释（描述Cell功能、输入输出、改进内容）
- **修复**: 为每个代码Cell添加markdown说明 + 行内注释
- **涉及文件**: 所有4个Notebook

#### CODE-4: 工程示意图字体问题
- **问题**: 生成的工程示意图中Unicode下标₂缺失于Arial字体
- **修复**: 将CO₂中的₂替换为常规文本或使用DejaVu Sans字体
- **涉及文件**: `generate_engineering_diagram.py` (已删除, 需重新生成)

#### CODE-5: IDF仿真速度优化
- **问题**: 单样本EnergyPlus仿真约1-2分钟，全量4640样本需16-24小时
- **优化方案**: (a) multiprocessing并行(每核~500MB内存) (b) 减少Output:Variable (c) Timestep从6→4
- **涉及文件**: `01_...ipynb`

#### CODE-6: Hotel engineering schematic regeneration
- **问题**: 用户要求生成更贴合研究的酒店工程示意图
- **修复**: 重新生成，需包含: 标准层平面图(客房+公共区+核心筒布局)、立面图(窗墙比示意)、HVAC系统示意图、尺寸标注
- **涉及文件**: 新脚本或在 `01_...ipynb` 中添加

---

### 🗂️ 论文修改最终提交物检查清单

| # | 交付物 | 状态 | 备注 |
|---|--------|------|------|
| 1 | 修订版论文 (Word) | ✅ | `Revised_Paper_EUI_OCEI_Beijing_Hotel.docx` |
| 2 | 修订版论文 (Markdown) | ✅ | `_revised_paper.md` |
| 3 | 逐点回复审稿人信函 | ⏳ | 需要按MDPI格式创建（可参考 `Example for author to respond reviewer - MDPI（格式）.docx`） |
| 4 | NB01 修复版 | ✅ | 语法错误已修复，筛选分析已添加 |
| 5 | NB02 修复版 | ✅ | SHAP+变量截断分析已添加 |
| 6 | NB03 修复版 | ✅ | 超参数报告+非核心变量分析已添加 |
| 7 | NB04 修复版 | ✅ | 排放因子来源+敏感性分析已添加 |
| 8 | 工程示意图 | ✅ | 3张图已生成 |
| 9 | 研究复现README | ✅ | `README.md` (12KB) |
| 10 | 完整仿真数据集 | ⏳ | 仅116/4640样本，需运行完整仿真 |

本项目已集成 GitHub 上星标最高的两套 Codex 学术研究技能包，覆盖从文献调研到论文发表的全流程。

### 一、Academic Research Skills（~11,900+ ⭐）— 学术研究全流程

**来源**: [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | **版本**: v3.12.0 | **许可证**: CC BY-NC 4.0

核心理念：**"AI是你的副驾驶，不是飞行员"**（AI is your copilot, not the pilot.）

#### 四大核心技能

| 技能目录 | 功能 | Agent数量 | 典型用途 |
|----------|------|-----------|----------|
| `.Codex/skills/deep-research/` | 深度文献调研 | 13个Agent | 文献综述、PRISMA系统评价、研究问题构建 |
| `.Codex/skills/academic-paper/` | 论文学术写作 | 12个Agent | 大纲设计→论证→草稿→双语摘要→图表→引用格式 |
| `.Codex/skills/academic-paper-reviewer/` | 论文评审 | 7个Agent | 模拟真实期刊评审（主编+3位审稿人+魔鬼代言人），0-100量化评分 |
| `.Codex/skills/academic-pipeline/` | 全流程编排 | 流程编排器 | 10阶段流水线，含完整性闸门检查点 |

#### 可用斜杠命令（`.Codex/commands/`）

| 命令 | 功能 |
|------|------|
| `/ars-plan` | 通过苏格拉底式对话规划论文结构 |
| `/ars-full` | 启动完整研究流程 |
| `/ars-lit-review` | 文献综述 |
| `/ars-outline` | 论文大纲设计 |
| `/ars-abstract` | 撰写摘要 |
| `/ars-citation-check` | 引用核验 |
| `/ars-format-convert` | 引用格式转换（APA/IEEE等） |
| `/ars-disclosure` | 生成AI使用声明 |
| `/ars-reviewer` | 启动论文评审 |
| `/ars-revision` | 论文修订 |
| `/ars-revision-coach` | 审稿意见解析与修订路线图 |

#### 关键特性

- **引用核验**: 调用 Semantic Scholar API 验证每篇引用，使用 Levenshtein 相似度算法模糊匹配（阈值 ≥0.70）
- **完整性闸门**: Stage 2.5 和 4.5 设有不可跳过的 7 项 AI 失败模式检查清单
- **反谄媚协议**: Devil's Advocate 的反驳评分 1-5，低于 4 分不允许写作团队让步
- **三层数据隔离**: 原始输入 / 验证产物 / 评分标准严格分离
- **风格校准**: 学习研究者过往作品的写作风格，避免 AI 味
- **L3 声明忠实度门禁** (v3.8): 可选审计 Pass 对每处引用索取原文并判断声明是否真正得到支持
- **实验溯源摄入** (#260): Material Passport 可记录外部实验结果，由完整性闸门审计

#### 使用示例

```
"Guide my research on hotel building energy performance"
"Do a systematic review on building energy prediction with PRISMA"
"Write a paper on EUI-OCEI coupling analysis for Beijing hotels"
"Review this paper" (then provide the paper)
"Parse these reviewer comments into a revision roadmap"
"Check citations in my manuscript"
```

---

### 二、Nature Skills（~13,000+ ⭐）— 期刊级学术技能

**来源**: [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) | **作者**: 袁一哲

#### 11 项技能

| 技能目录 | 功能 | 说明 |
|----------|------|------|
| `.Codex/skills/nature-reader/` | 论文精读 | PDF全文双语翻译，图表感知，源码级Markdown输出 |
| `.Codex/skills/nature-writing/` | 论文写作 | Nature/Cell/Science级别学术写作 |
| `.Codex/skills/nature-polishing/` | 论文润色 | 语言精炼、学术风格强化 |
| `.Codex/skills/nature-reviewer/` | 论文评审 | 模拟期刊同行评审 |
| `.Codex/skills/nature-citation/` | 引用管理 | 引用格式转换与验证 |
| `.Codex/skills/nature-figure/` | 图表优化 | 学术图表设计与美化 |
| `.Codex/skills/nature-data/` | 数据处理 | 科研数据清洗与分析 |
| `.Codex/skills/nature-response/` | 审稿回复 | 点对点回复审稿意见 |
| `.Codex/skills/nature-paper2ppt/` | 论文转PPT | 论文内容转学术演示文稿 |
| `.Codex/skills/nature-academic-search/` | 学术搜索 | 文献检索与获取 |
| `.Codex/skills/nature-paper-to-patent/` | 论文转专利 | 学术成果转专利申请 |

#### 使用示例

```
"Translate this paper into a full markdown reader"  → nature-reader
"Polish this paragraph to Nature-level quality"     → nature-polishing
"Convert this paper to a Chinese journal-club PPT"  → nature-paper2ppt
"Generate a point-by-point response to these reviewer comments" → nature-response
```

---

### 三、技能文件结构

```
.Codex/
├── skills/
│   ├── deep-research/          # ARS: 深度调研 (52 files)
│   ├── academic-paper/         # ARS: 论文写作 (61 files)
│   ├── academic-paper-reviewer/# ARS: 论文评审 (26 files)
│   ├── academic-pipeline/      # ARS: 全流程编排 (30 files)
│   ├── shared/                 # ARS: 共享支持文件 (54 files)
│   ├── nature-reader/          # Nature: 论文精读 (15 files)
│   ├── nature-writing/         # Nature: 论文写作 (65 files)
│   ├── nature-polishing/       # Nature: 论文润色 (29 files)
│   ├── nature-reviewer/        # Nature: 论文评审 (9 files)
│   ├── nature-citation/        # Nature: 引用管理 (12 files)
│   ├── nature-figure/          # Nature: 图表优化 (98 files)
│   ├── nature-data/            # Nature: 数据处理 (13 files)
│   ├── nature-response/        # Nature: 审稿回复 (24 files)
│   ├── nature-paper2ppt/       # Nature: 论文转PPT (16 files)
│   ├── nature-academic-search/ # Nature: 学术搜索 (45 files)
│   ├── nature-paper-to-patent/ # Nature: 论文转专利 (34 files)
│   └── _shared_nature/         # Nature: 共享支持文件 (6 files)
└── commands/                   # ARS斜杠命令 (14个)
    ├── ars-plan.md
    ├── ars-full.md
    ├── ars-lit-review.md
    ├── ars-abstract.md
    ├── ars-outline.md
    ├── ars-reviewer.md
    ├── ars-revision.md
    ├── ars-citation-check.md
    └── ... (更多)
```

---

### 四、使用建议

1. **文献调研阶段**: 使用 `/ars-lit-review` 或 `deep-research` 技能进行系统性文献综述
2. **方法论设计**: 使用 `/ars-plan` 苏格拉底式对话细化研究设计
3. **论文初稿**: 使用 `academic-paper` 或 `nature-writing` 技能辅助写作
4. **论文润色**: 使用 `nature-polishing` 提升语言质量
5. **自我评审**: 使用 `academic-paper-reviewer` 或 `nature-reviewer` 在投稿前进行模拟评审
6. **引用核验**: 使用 `/ars-citation-check` 确保引用真实可靠
7. **审稿回复**: 使用 `nature-response` 逐条回复审稿意见

> ⚠️ **重要提醒**: 所有 AI 辅助技能均为"副驾驶"模式——AI 处理查找引用、格式化、核验数据等重复劳动，研究者专注于定义问题、选择方法、解读数据和撰写核心论点。完整跑一篇 1.5 万字论文的全流程大约花费 $4-6 美元 API 费用。
