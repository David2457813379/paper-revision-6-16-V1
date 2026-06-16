"""Patch the four research notebooks for reviewer-response reproducibility.

This script uses nbformat so that notebook JSON is edited structurally rather
than by brittle text operations. It performs three tasks:

1. fix reviewer-critical reproducibility issues in selected code cells;
2. insert bilingual Chinese/English explanations before every code cell;
3. align chart labels with the project's Chinese interface requirement.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import nbformat
from nbformat.v4 import new_markdown_cell


def find_repo_root(start: Path) -> Path:
    start = start.resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "input" / "Beijing.epw").exists() or (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


ROOT = find_repo_root(Path(__file__))
MARKER_START = "<!-- CODEx bilingual cell explanation: start -->"
MARKER_END = "<!-- CODEx bilingual cell explanation: end -->"


NOTEBOOKS = {
    "01_Parametric_Simulation_Database_Construction.ipynb": [
        ("环境配置与全局参数", "Environment setup and global parameters",
         "导入数值计算、数据处理、SQLite、EnergyPlus 调用和绘图所需模块，建立项目目录结构，并集中定义采样规模、随机种子、EnergyPlus 路径、气象文件、生活热水和可行性筛选阈值。该 cell 是整个参数化仿真数据库的运行入口；后续所有采样、IDF 生成、仿真和后处理均读取这里的 CONFIG。为便于本地验证，代码支持通过环境变量切换小样本快速模式和是否真正运行 EnergyPlus。",
         "Imports the numerical, tabular, SQLite, EnergyPlus subprocess, and plotting dependencies, creates the project directory structure, and defines the central CONFIG object for sample size, random seed, EnergyPlus paths, weather data, domestic hot-water assumptions, and feasibility bounds. This cell is the execution entry point for the parametric simulation database; all downstream sampling, IDF generation, simulation, and post-processing read from this CONFIG. Environment variables are supported so that local smoke tests can run without launching the full EnergyPlus batch.",
         "对应 R1-MAJ-5、CODE-1、CODE-5：明确软件环境和可复现运行开关。"),
        ("本地路径与输入文件检查", "Local path and input-file check",
         "打印 Python 解释器、当前工作目录、EnergyPlus 可执行文件、ExpandObjects 和 Beijing.epw 的实际路径及存在性，帮助作者在运行正式仿真前发现路径配置错误。该检查不改变数据，只给出可复现性诊断信息。",
         "Prints the Python executable, working directory, EnergyPlus executable, ExpandObjects, and Beijing.epw paths with existence checks. It helps identify local configuration errors before the full simulation batch is launched. The cell is diagnostic only and does not mutate the dataset.",
         "对应 R1-MAJ-5：补充 EnergyPlus 和气象文件可复现性证据。"),
        ("参数空间定义", "Parameter-space definition",
         "以结构化表格定义酒店建筑的围护结构、几何形态、功能空间、人员与系统运行参数的采样范围、变量类型和默认值。该表是 LHS 抽样、IDF 生成、敏感性分析和机器学习建模的共同输入，保证论文表格与代码变量一致。",
         "Defines the sampled hotel-building parameter space as a structured table covering envelope, geometry, functional area, occupancy, and system-operation variables. This table is the common input to LHS sampling, IDF generation, sensitivity analysis, and machine-learning modelling, keeping manuscript tables and code variables aligned.",
         "对应 R1-MAJ-5、R1-MIN-7：完整记录可复现的模型参数。"),
        ("LHS 抽样与约束派生", "LHS sampling and dependency resolution",
         "使用 scipy.stats.qmc 的 Latin Hypercube Sampling 生成高维参数组合，并通过几何派生关系计算建筑宽度、总建筑面积、体积、可用面积比、估计人数、运行时段比例和等效热阻。筛选逻辑保留原始 LHS 索引，使后续筛选前后分布比较可准确追踪每个样本。",
         "Generates high-dimensional parameter combinations with scipy.stats.qmc Latin Hypercube Sampling and resolves derived geometry, gross floor area, volume, usable-area ratio, estimated occupancy, schedule fraction, and equivalent thermal resistance. The filtering logic preserves the original LHS index so that pre/post-screening distribution diagnostics can correctly track retained and rejected samples.",
         "对应 R1-MAJ-2、R2-1、R3-4：解释 20,000 到可行样本的筛选逻辑。"),
        ("可行性筛选分布诊断", "Feasibility-screening distribution diagnostics",
         "绘制筛选前可用面积比直方图、筛选前后密度对比和关键参数二维覆盖图，并输出每个输入变量筛选前后的 KS 统计量与 Jensen-Shannon 距离。该 cell 直接检验 77% 剔除率是否导致参数空间系统性偏移，是回应样本代表性和选择偏差质疑的核心证据。",
         "Plots the pre-filter usable-area-ratio histogram, the pre/post-filter density comparison, and a two-dimensional coverage check for key parameters. It also exports per-variable Kolmogorov-Smirnov statistics and Jensen-Shannon distances between pre- and post-filter distributions. This is the main code-level evidence for whether the 77% rejection rate introduces systematic sampling bias.",
         "对应 R1-MAJ-2、R2-1、R3-4：新增变量级分布偏移量化。"),
        ("IDF 文本辅助函数", "IDF text helper functions",
         "定义 IDF 对象格式化、数值格式化、窗洞顶点生成、顶点字段展开和日运行比例时间表生成函数。这些纯函数把参数表转换为 EnergyPlus 可读对象，是批量生成 IDF 的基础。",
         "Defines pure helper functions for IDF object formatting, numeric formatting, window-vertex generation, vertex-field expansion, and compact daily fraction schedules. These functions translate parameter-table rows into EnergyPlus-readable objects and form the basis of batch IDF generation.",
         "对应 R1-MAJ-5：使几何、窗墙比和时间表生成过程可复查。"),
        ("酒店原型 IDF 生成", "Hotel prototype IDF generation",
         "根据单行参数构建简化酒店 EnergyPlus IDF：包括单区矩形体量、四向窗、Material:NoMass 围护结构、人员/照明/设备内扰、渗透、新风、恒温器、IdealLoadsAirSystem 和年度输出变量。该 cell 只生成仿真输入文件，不直接运行 EnergyPlus。",
         "Builds a simplified hotel EnergyPlus IDF from each parameter row, including the single-zone rectangular massing, four-orientation windows, Material:NoMass envelope, people/lights/equipment internal gains, infiltration, outdoor air, thermostat schedules, IdealLoadsAirSystem, and annual output variables. This cell generates simulation input files only; it does not launch EnergyPlus.",
         "对应 R1-MAJ-5、CODE-5：公开基础几何模板、HVAC 类型和输出设置。"),
        ("单样本 EnergyPlus 调用", "Single-sample EnergyPlus execution",
         "把 IDF、Energy+.ini 和 Energy+.idd 复制到样本运行目录，先执行 ExpandObjects，再调用 EnergyPlus，并记录 stdout/stderr、错误文件、严重错误和运行状态。该函数为大批量仿真提供统一的失败诊断格式。",
         "Copies the IDF, Energy+.ini, and Energy+.idd into the sample run directory, executes ExpandObjects, launches EnergyPlus, and records stdout/stderr tails, error-file content flags, severe/fatal errors, and success status. The function provides a uniform failure-diagnostic record for large simulation batches.",
         "对应 R1-MAJ-5、CODE-1：保证仿真失败可追踪。"),
        ("SQLite 结果解析与工程后处理", "SQLite parsing and engineering post-processing",
         "从 EnergyPlus SQLite 文件读取建筑面积、理想供冷/供热负荷，并通过照明、设备、风机、COP 换算和生活热水公式计算电力、天然气、总能耗与 EUI。该 cell 明确把模拟负荷转换为工程能耗指标的计算边界。",
         "Reads conditioned area and ideal cooling/heating loads from the EnergyPlus SQLite output, then computes lighting, equipment, fan electricity, COP-adjusted cooling/heating electricity, domestic hot water, natural gas, total site energy, and EUI. It makes the engineering boundary from simulated loads to operational energy metrics explicit.",
         "对应 R1-MAJ-1、R1-MAJ-5、CROSS-1：区分仿真负荷、工程后处理和 EUI 标签。"),
        ("批量仿真与数据集写出", "Batch simulation and dataset export",
         "在 run_energyplus 为真时逐样本运行 EnergyPlus、解析结果并写出 simulation_log.csv 与 step1_simulation_dataset.csv；在调试模式下只提示已跳过仿真。该 cell 是生成后续三个 notebook 输入数据的唯一入口。",
         "When run_energyplus is true, iterates through all feasible samples, runs EnergyPlus, parses results, and writes simulation_log.csv plus step1_simulation_dataset.csv. In debug mode it reports that simulations were skipped. This cell is the sole producer of the dataset consumed by the next three notebooks.",
         "对应 CODE-1、R2-3：强调当前机器学习标签来自 EnergyPlus 仿真。"),
        ("Step 1 探索性图表", "Step 1 exploratory figures",
         "读取已生成的数据集并绘制 EUI 分布、总能耗分布、平均终端能耗组成和变量相关矩阵，用于检查仿真输出是否落在合理范围内并发现异常列。图表保存到 outputs_step1/figures。",
         "Reads the generated dataset and plots the EUI distribution, site-energy distribution, average end-use/load components, and selected-variable correlation matrix. These figures check whether simulation outputs are in a plausible range and help detect anomalous columns. The files are saved under outputs_step1/figures.",
         "对应 R3-6：输出高分辨率、可读性更好的诊断图。"),
        ("模拟 EUI 与实测基准对比", "Simulated EUI versus measured benchmark",
         "把模拟 EUI 分布与北京酒店实测 EUI 文献统计和 GB/T 51161 酒店能耗基准对比，输出均值差异和百分比偏差。该分析将模型性能表述限定为代理模型保真度，并明确模拟到真实建筑的迁移差距。",
         "Compares the simulated EUI distribution with published measured EUI statistics for Beijing hotels and GB/T 51161 hotel benchmarks, then reports the mean difference and percentage bias. This analysis reframes model performance as surrogate fidelity and makes the simulation-to-real-building transfer gap explicit.",
         "对应 R1-MAJ-1、R2-3、CROSS-1：补充真实建筑对标和局限性证据。"),
    ],
    "02_SRC_Sensitivity_and_Variable_Selection.ipynb": [
        ("环境、路径与 SRC 参数", "Environment, paths, and SRC settings",
         "导入 SRC、交叉验证、标准化和绘图所需库，建立 Step 2 输出目录，设置目标变量、随机种子和快速验证开关。BOOTSTRAP_N 控制 bootstrap 次数，默认用于论文级结果，快速模式用于本地 smoke test。",
         "Imports the libraries required for SRC, cross-validation, standardisation, and plotting; creates Step 2 output directories; and defines the target, random seed, and fast-validation switch. BOOTSTRAP_N controls bootstrap repetitions, with the default intended for manuscript-grade results and fast mode for local smoke tests.",
         "对应 R1-MAJ-3、R2-2、R3-5：建立敏感性分析的可复现入口。"),
        ("数据加载与特征工程", "Data loading and feature engineering",
         "读取 Step 1 仿真数据，构造朝向正弦/余弦、建筑占地面积、长宽比、窗型虚拟变量和 envelope_to_floor_ratio，并定义 39 个分析变量及其全称。该 cell 保证 SRC 输入与后续机器学习输入一致。",
         "Loads the Step 1 simulation dataset, constructs orientation sine/cosine terms, footprint area, aspect ratio, window-type dummies, and envelope_to_floor_ratio, and defines the 39 analysis features with full labels. This keeps the SRC inputs aligned with the downstream machine-learning inputs.",
         "对应 R1-MAJ-7、R3-7：明确模型变量、编码方式和工程含义。"),
        ("VIF 多重共线性检查", "VIF multicollinearity check",
         "逐变量用线性回归计算 VIF，并导出 vif_table.csv。该检查用于识别高度共线变量，避免 SRC 排名被冗余变量不合理放大或削弱。",
         "Computes the variance inflation factor for each feature using auxiliary linear regressions and exports vif_table.csv. This identifies collinearity that could distort SRC ranking by redundant predictors.",
         "对应 R1-MAJ-3、R2-2：说明线性 SRC 前的共线性诊断。"),
        ("SRC bootstrap 函数", "SRC bootstrap function",
         "封装 SRC 估计过程：对 X 和 y 分别标准化、拟合线性回归、重复 bootstrap 重采样并计算 95% 置信区间和符号稳定性。该函数用于 EUI、OCEI 和物理验证的重复敏感性分析。",
         "Wraps SRC estimation: standardises X and y, fits linear regression, performs bootstrap resampling, and computes 95% confidence intervals plus sign stability. The function is reused for EUI, OCEI, and physical-validation sensitivity analyses.",
         "对应 R1-MAJ-3、R3-5：为 SRC 不确定性提供统计证据。"),
        ("线性近似交叉验证", "Cross-validation of the linear approximation",
         "用 5 折交叉验证评估线性回归对 EUI 的拟合能力，输出 CV R2 和 RMSE。该结果界定 SRC 作为线性解释方法的适用边界。",
         "Evaluates the linear regression approximation for EUI using 5-fold cross-validation and reports CV R2 and RMSE. The result defines the validity boundary for using SRC as a linear interpretability method.",
         "对应 R1-MAJ-3、R2-2：承认并量化 SRC 线性假设。"),
        ("全变量 SRC 与置信区间", "Full-feature SRC with confidence intervals",
         "对 39 个输入变量计算 bootstrap SRC、绝对 SRC、95% 置信区间和符号稳定性，并保存 src_indices_bootstrap.csv。该表是变量筛选和后续 18 变量建模的主证据。",
         "Computes bootstrap SRC, absolute SRC, 95% confidence intervals, and sign stability for all 39 input variables, then saves src_indices_bootstrap.csv. This table is the primary evidence for variable selection and downstream 18-feature modelling.",
         "对应 R1-MAJ-8、R3-5：为关键变量截断提供基础排序。"),
        ("SHAP 非线性敏感性补充", "SHAP nonlinear sensitivity supplement",
         "训练 XGBoost 并计算 SHAP 平均绝对贡献，将非线性重要性排序与 SRC 排序比较，输出 Spearman 秩相关、Top-18 Jaccard 重叠、并排图和 beeswarm 图。该 cell 用非线性解释方法验证 SRC 排名的稳健性。",
         "Trains XGBoost, computes mean absolute SHAP values, and compares nonlinear importance ranking with SRC ranking. It reports Spearman rank correlation, Top-18 Jaccard overlap, side-by-side importance plots, and a SHAP beeswarm plot. This cell validates the robustness of SRC ranking using a nonlinear interpretability method.",
         "对应 R1-MAJ-3、R2-2、CROSS-3：补充 SHAP 以回应 Sobol/SHAP 方法质疑。"),
        ("18 变量截断阈值分析", "Eighteen-variable cutoff analysis",
         "绘制 SRC 碎石图、累计贡献曲线和交叉验证 R2 随变量数变化曲线，并导出 cv_r2_by_variable_count.csv。该 cell 用三条独立证据线说明为什么选 18 个变量而不是任意截断。",
         "Plots the SRC scree curve, cumulative contribution curve, and cross-validated R2 as a function of feature count, then exports cv_r2_by_variable_count.csv. It provides three independent lines of evidence for choosing 18 variables rather than an arbitrary cutoff.",
         "对应 R1-MAJ-8、R3-5、CROSS-4：量化变量筛选标准。"),
        ("SRC 分组汇总", "Group-level SRC summary",
         "按围护结构、几何形态、功能分区和运行/HVAC 分组汇总绝对 SRC、平均绝对 SRC 和符号稳定变量数量。该结果帮助把单变量排序转化为论文讨论中的系统层面解释。",
         "Aggregates absolute SRC, mean absolute SRC, and sign-stable counts by envelope, geometry/form, program/zoning, and operation/HVAC groups. This translates feature-level ranking into system-level interpretation for the manuscript discussion.",
         "对应 R3-9：增强工程意义解释。"),
        ("全输入变量 Top-18 标记图", "All-input SRC plot with Top-18 markers",
         "重新计算当前输入变量 SRC 并用颜色标记 Top-18 变量，保存全变量横向条形图。该图用于直观看到第 18 名之后 SRC 是否趋于平缓。",
         "Recomputes SRC for the current input set and marks the Top-18 variables in a horizontal bar plot. The figure visually checks whether SRC magnitudes flatten after the 18th variable.",
         "对应 R1-MAJ-8、R3-5：补充碎石图可读性证据。"),
        ("Top-18 SRC 方向图", "Top-18 SRC direction plot",
         "绘制前 18 个变量的有符号 SRC，展示变量对 EUI 的正向或负向影响。该图支撑论文中关于 DHW、楼层数、房间数等关键变量作用方向的解释。",
         "Plots signed SRC values for the top 18 variables, showing whether each feature increases or decreases EUI. The figure supports manuscript interpretation of key variables such as DHW, floor number, and room count.",
         "对应 R3-9：强化工程解释和设计含义。"),
        ("SRC 符号稳定性图", "SRC sign-stability plot",
         "用颜色区分 bootstrap 置信区间是否跨越 0，展示 Top-18 变量的符号稳定性。该结果防止把统计不稳定的弱变量解释为可靠结论。",
         "Uses colour to indicate whether bootstrap confidence intervals cross zero for the Top-18 variables. This prevents statistically unstable weak predictors from being overinterpreted as robust findings.",
         "对应 R1-MAJ-3、R1-MAJ-8：量化排名可靠性。"),
        ("几何物理关系散点检查", "Geometry-physics scatter checks",
         "绘制 envelope_to_floor_ratio、floor_num 与 EUI/site energy 的关系，用物理直觉检查几何变量对面积归一化指标和总能耗指标的不同影响。",
         "Plots relationships between envelope_to_floor_ratio, floor_num, and EUI/site energy to check whether geometry variables behave consistently with physical intuition for area-normalised and total-energy metrics.",
         "对应 R1-MAJ-3、R3-9：增加物理合理性审查。"),
        ("EUI 与总能耗 SRC 对比", "SRC comparison for EUI and site energy",
         "分别以 EUI 和 site_energy_kwh 为目标重新计算 SRC，并重点展示几何与功能变量的差异。该对比说明面积归一化会改变变量作用方向和大小。",
         "Recomputes SRC using EUI and site_energy_kwh as separate targets and highlights differences for geometry and program variables. The comparison shows how area normalisation changes effect direction and magnitude.",
         "对应 R1-MAJ-3、R3-9：避免把 EUI 与总能耗解释混淆。"),
        ("物理扩展变量验证", "Physics-extended variable validation",
         "把 envelope_to_floor_ratio 纳入物理扩展变量集重新运行 SRC，验证主要结论是否依赖原始几何变量表达方式。结果导出为 src_physical_validation.csv。",
         "Adds envelope_to_floor_ratio to a physics-extended feature set and reruns SRC to test whether the main conclusions depend on the original geometry representation. Results are exported as src_physical_validation.csv.",
         "对应 R1-MAJ-3、R3-5：增强变量筛选稳健性。"),
    ],
    "03_ML_Model_Training_and_Evaluation.ipynb": [
        ("环境、模型库与验证参数", "Environment, model libraries, and validation settings",
         "导入 scikit-learn、XGBoost、LightGBM、joblib 和绘图库，建立 Step 3 输出目录，设置目标变量、随机种子、内层交叉验证折数和快速验证开关。所有预处理均在 Pipeline 内完成，避免训练/测试信息泄漏。",
         "Imports scikit-learn, XGBoost, LightGBM, joblib, and plotting libraries; creates Step 3 output directories; and defines the target, random seed, inner cross-validation folds, and fast-validation switch. All preprocessing is placed inside Pipelines to avoid train/test information leakage.",
         "对应 R1-MAJ-7、R2-3、R3-7：明确建模环境和防泄漏策略。"),
        ("数据加载、Top-18 特征和训练测试划分", "Data loading, Top-18 features, and train/test split",
         "读取 Step 1 数据和 Step 2 SRC 排序，复用相同特征工程，选取 SRC 前 18 个变量，固定 80/20 随机训练测试划分，并导出变量范围和非核心变量中位数表。该 cell 是所有模型公平比较的数据基础。",
         "Loads Step 1 data and Step 2 SRC ranking, applies the same feature engineering, selects the top 18 SRC variables, fixes an 80/20 random train/test split, and exports feature ranges plus non-core-feature medians. This cell is the common data basis for fair model comparison.",
         "对应 R1-MAJ-8、R2-3、R2-4：明确变量选择和划分流程。"),
        ("样本量快速核对", "Sample-count sanity check",
         "打印当前仿真数据集样本量，用于提醒作者当前是否仍处于 116 个样本的调试数据状态，还是已经完成 4,640 个可行样本的完整仿真。",
         "Prints the current simulation-dataset sample count to remind the author whether the notebook is still using the 116-sample debug dataset or the completed 4,640-feasible-sample simulation dataset.",
         "对应 CODE-1：显式暴露数据集完整性。"),
        ("EUI 标签分布与统计", "EUI-label distribution and statistics",
         "绘制机器学习标签 EUI 的分布、均值和中位数，并导出摘要统计 CSV。该图用于判断模型训练目标是否存在异常偏态或离群值。",
         "Plots the machine-learning target EUI distribution with mean and median markers and exports summary statistics. The figure checks whether the training label has unusual skewness or outliers.",
         "对应 R2-3、R3-6：检查高 R2 是否来自异常标签结构。"),
        ("候选模型与超参数搜索空间", "Candidate models and hyperparameter search spaces",
         "定义线性、正则化、多项式、KNN、SVR、树模型、集成模型、XGBoost、LightGBM 和 MLP 的 Pipeline 与搜索空间。线性模型使用带标准化的 Pipeline，树模型使用中位数插补 Pipeline；搜索均在训练集内进行。",
         "Defines Pipelines and search spaces for linear, regularised, polynomial, KNN, SVR, tree, ensemble, XGBoost, LightGBM, and MLP regressors. Linear models use imputation and scaling, tree models use imputation only, and all searches are performed within the training set.",
         "对应 R1-MAJ-7、R3-7：补充超参数调优策略和模型假设。"),
        ("模型训练、交叉验证与测试集评估", "Model fitting, cross-validation, and test-set evaluation",
         "逐模型拟合训练集，提取最优估计器，在独立测试集上计算 R2、RMSE、MAE、MAPE，并在训练集内做交叉验证估计均值和方差。结果保存为 model_metrics.csv。",
         "Fits each model on the training set, extracts the best estimator, evaluates R2, RMSE, MAE, and MAPE on the independent test set, and computes cross-validation means and variances within the training set. Results are saved as model_metrics.csv.",
         "对应 R2-3：用独立测试集、CV 方差和泛化间隙回应信息泄漏风险。"),
        ("超参数报告生成", "Hyperparameter report generation",
         "从搜索器、Pipeline 和交叉验证模型中稳健提取最终超参数、搜索方式、CV 折数和评分函数，导出全模型超参数表，并打印前 5 名模型的详细配置。该 cell 修复了旧版提取逻辑对 fitted_models 结构的错误假设。",
         "Robustly extracts final hyperparameters, search method, CV folds, and scoring function from search objects, Pipelines, and cross-validated estimators; exports the full hyperparameter table; and prints detailed settings for the top five models. This cell fixes the earlier incorrect assumption about the structure of fitted_models.",
         "对应 R1-MAJ-7、R3-7：使模型比较可复现。"),
        ("非核心变量影响分析", "Impact of non-core variables",
         "比较 18 变量模型与全 39 变量模型在 Poly3-RidgeCV 和 XGBoost 上的测试集表现，量化排除低 SRC 变量是否人为抬高模型精度。结果保存为 noncore_variable_impact.csv。",
         "Compares 18-feature and full 39-feature models for Poly3-RidgeCV and XGBoost on the test set, quantifying whether excluding low-SRC variables artificially inflates performance. Results are saved as noncore_variable_impact.csv.",
         "对应 R2-4、R1-MAJ-8：验证变量简化策略的泛化影响。"),
        ("模型指标条形图", "Model-metric bar charts",
         "绘制测试 R2、RMSE 和 MAPE 横向条形图，直观比较候选模型性能。图中排序规则按指标优劣设置，避免读者误判。",
         "Plots horizontal bar charts for test R2, RMSE, and MAPE to compare candidate-model performance. Sorting follows the direction of each metric so the best models are visually clear.",
         "对应 R3-6、R1-MAJ-7：提高模型比较图可读性。"),
        ("CV R2 方差图", "CV R2 variance chart",
         "绘制各模型 10 折交叉验证 R2 方差，评估模型稳定性而不仅仅关注测试集均值表现。该图可解释为什么某些模型虽然精度高但稳定性较差。",
         "Plots the variance of cross-validated R2 across models, evaluating stability rather than only mean test performance. The figure helps explain models that are accurate but less stable.",
         "对应 R2-3：补充泛化稳定性证据。"),
        ("最佳模型保存", "Best-model persistence",
         "选择测试集表现最好的两个模型，保存 joblib 文件、最佳参数和模型名称，为 Step 4 的 OCEI 模型重建和后续复现提供输入。",
         "Selects the top two test-set models, saves joblib files, best-parameter records, and model names, providing inputs for Step 4 carbon-intensity modelling and later reproduction.",
         "对应 R1-MAJ-7、R3-7：确保最佳模型可追踪和复用。"),
        ("泛化间隙图", "Generalization-gap chart",
         "计算并绘制 train R2 - test R2，识别过拟合风险。该图直接回应高精度结果是否可能由训练集记忆或信息泄漏造成。",
         "Computes and plots train R2 minus test R2 to identify overfitting risk. The chart directly addresses whether high predictive performance could result from memorisation or leakage.",
         "对应 R2-3：补充信息泄漏与过拟合审查。"),
        ("预测值与仿真值对比图", "Predicted-versus-simulated plots",
         "为前两名模型绘制测试集预测 EUI 与 EnergyPlus 仿真 EUI 的散点图，并标注 R2、CV 方差、RMSE 和 MAPE。该图表述为代理模型对仿真标签的保真度，而非真实建筑预测精度。",
         "Plots predicted EUI against EnergyPlus-simulated EUI for the top two models and annotates R2, CV variance, RMSE, and MAPE. The plot is framed as surrogate fidelity to simulation labels, not real-building prediction accuracy.",
         "对应 R1-MAJ-1、R2-3、CROSS-1：避免过度声称真实预测能力。"),
    ],
    "04_EUI_OCEI_Coupling_and_Carbon_Analysis.ipynb": [
        ("环境、路径与碳分析依赖", "Environment, paths, and carbon-analysis dependencies",
         "导入碳排放计算、模型重建、交叉验证和绘图所需库，建立 Step 4 输出目录，并定义 Step 1-3 的输入文件路径。该 cell 是 EUI-OCEI 耦合分析的运行入口。",
         "Imports the dependencies for carbon accounting, model reconstruction, cross-validation, and plotting; creates Step 4 output directories; and defines input paths from Steps 1-3. This cell is the entry point for the EUI-OCEI coupling analysis.",
         "对应 R1-MAJ-4、R2-5：建立碳分析可复现入口。"),
        ("碳排放因子与核算边界", "Emission factors and accounting boundary",
         "定义电力、天然气、区域供热和区域供冷的基准碳排放因子，并固定能源载体映射边界：采暖对应区域供热，供冷对应区域供冷，生活热水对应天然气，照明/设备/风机对应电力。",
         "Defines baseline emission factors for electricity, natural gas, district heating, and district cooling, and fixes the carrier-mapping boundary: heating to district heating, cooling to district cooling, domestic hot water to natural gas, and lighting/equipment/fans to electricity.",
         "对应 R1-MAJ-4：明确表 5 因子和核算边界。"),
        ("数据加载与 OCEI 标签构建", "Data loading and OCEI-label construction",
         "读取 Step 1 数据、SRC 排序和 Step 3 最佳模型，补齐特征工程，按固定能源边界计算分载体碳排放、总碳排放、OCEI 和单位能耗碳强度。该 cell 生成后续敏感性、排名和模型分析所需的 df。",
         "Loads Step 1 data, SRC ranking, and Step 3 best-model names; completes feature engineering; and computes carrier-specific emissions, total emissions, OCEI, and carbon per unit energy under the fixed accounting boundary. This cell creates df for downstream sensitivity, ranking, and modelling analyses.",
         "对应 R1-MAJ-4、R2-5：保证敏感性分析运行前已有 OCEI 标签。"),
        ("排放因子敏感性分析", "Emission-factor sensitivity analysis",
         "在基准、电力 0.40/0.70、2030/2050 电网脱碳和区域冷热高碳强度情景下重新计算 OCEI，报告均值、方差、EUI-OCEI 相关性、Top-10% 排名重叠和各能源载体碳贡献占比。该 cell 是回应碳因子不确定性的核心分析。",
         "Recomputes OCEI under baseline, electricity 0.40/0.70, 2030/2050 grid-decarbonisation, and high district thermal-factor scenarios. It reports mean, variance, EUI-OCEI correlation, Top-10% ranking overlap, and carrier contribution shares. This is the core analysis addressing uncertainty in emission factors.",
         "对应 R1-MAJ-4、R2-5、CROSS-5：量化电网脱碳对耦合结构的影响。"),
        ("OCEI 分布统计", "OCEI distribution statistics",
         "汇总 OCEI 的均值、中位数、标准差、最小值和最大值，并绘制分布图。该图检查碳强度标签是否稳定、是否存在异常样本。",
         "Summarises the mean, median, standard deviation, minimum, and maximum of OCEI and plots its distribution. The figure checks whether the carbon-intensity label is stable and whether anomalous samples exist.",
         "对应 R3-6：提高 OCEI 结果呈现质量。"),
        ("多情景碳数据函数", "Multi-scenario carbon-dataset function",
         "封装碳数据集构建函数，可在基准情景和区域能源情景之间切换，并按指定排放因子重新生成 OCEI。该函数提高不同核算边界下复算的可维护性。",
         "Wraps carbon-dataset construction so OCEI can be rebuilt under baseline and district-energy scenarios with specified emission factors. The function improves maintainability for recomputation under different accounting boundaries.",
         "对应 R1-MAJ-4、R2-5：支持碳边界敏感性扩展。"),
        ("OCEI 预测模型重建", "OCEI prediction-model reconstruction",
         "根据 Step 3 的最佳模型名称重建相同候选模型结构，并选择可用于 OCEI 标签的前两名模型。该 cell 避免直接复用 EUI 标签训练结果，而是在碳强度目标上重新评估。",
         "Reconstructs candidate-model structures based on the best model names from Step 3 and selects the top models available for OCEI labels. It avoids directly reusing EUI-trained outputs and instead evaluates models on the carbon-intensity target.",
         "对应 R2-3、R1-MAJ-7：保持 EUI 与 OCEI 建模边界清晰。"),
        ("OCEI 模型交叉验证", "OCEI model cross-validation",
         "用 10 折交叉验证生成 OCEI 的 out-of-fold 预测，计算 R2、RMSE、MAE、MAPE 和 CV 方差，并导出 carbon_model_metrics.csv。",
         "Generates out-of-fold OCEI predictions with 10-fold cross-validation, computes R2, RMSE, MAE, MAPE, and CV variance, and exports carbon_model_metrics.csv.",
         "对应 R2-3、R2-5：提供碳强度代理模型稳定性证据。"),
        ("碳贡献合并双视图图", "Consolidated dual-view carbon contribution figure",
         "合并原绝对值和归一化贡献图：左图显示各能源载体总碳排放贡献，右图显示平均 OCEI 贡献及占比，并导出 carbon_breakdown_by_carrier.csv。该 cell 替代原先重复的 Figure 15/16。",
         "Consolidates the former absolute and normalised contribution figures: the left panel shows total carbon contribution by carrier, and the right panel shows average OCEI contribution with shares. It exports carbon_breakdown_by_carrier.csv and replaces the previously redundant Figures 15/16.",
         "对应 R1-MIN-5、R3-6：消除图表冗余并提高可读性。"),
        ("碳贡献表展示", "Carbon-contribution table display",
         "显示按能源载体汇总的总碳排放、样本平均碳排放、平均 OCEI 和占比，供论文表格或补充材料引用。",
         "Displays total carbon, average carbon per sample, average OCEI, and contribution share by carrier for use in manuscript tables or supplementary materials.",
         "对应 R1-MAJ-4、R2-5：给出因子核算结果的表格证据。"),
        ("归一化 OCEI 贡献核对", "Normalised OCEI contribution check",
         "复用合并图中计算的 carrier_ocei_avg，输出归一化 OCEI 贡献表，确保读者无需查看两张重复图也能获得百分比解释。",
         "Reuses carrier_ocei_avg from the consolidated figure and outputs the normalised OCEI contribution table so readers can obtain percentage interpretation without separate duplicate figures.",
         "对应 R1-MIN-5：保留信息但不重复作图。"),
        ("EUI-OCEI 相关性", "EUI-OCEI correlation",
         "计算 EUI 与 OCEI 的 Pearson 相关，以及单位能耗碳强度与 OCEI 的相关，并绘制 EUI-OCEI 散点图。该分析检验能耗强度和碳强度是否可以相互替代。",
         "Computes Pearson correlations between EUI and OCEI, and between carbon per kWh and OCEI, then plots the EUI-OCEI scatter. The analysis tests whether energy intensity and carbon intensity can be treated as interchangeable.",
         "对应 R2-5、R3-9：支撑 EUI-only 评价不足的工程讨论。"),
        ("EUI 与 OCEI 排名偏移", "Ranking shift between EUI and OCEI",
         "比较按 EUI 和 OCEI 排序的样本名次，计算 Top-10% 重叠率、平均绝对名次偏移和最大偏移，并绘制排名散点图。",
         "Compares sample rankings by EUI and OCEI, computes Top-10% overlap, mean absolute rank shift, and maximum shift, and plots the ranking scatter.",
         "对应 R2-5、R3-9：说明单一 EUI 指标不能完全代表碳绩效。"),
        ("EUI-OCEI 对比变量集", "Feature set for EUI-OCEI comparison",
         "定义用于 EUI 与 OCEI SRC 对比的前 20 个候选变量，覆盖生活热水、几何、系统效率、运行时间和围护结构变量。",
         "Defines the top 20 candidate features for SRC comparison between EUI and OCEI, covering domestic hot water, geometry, system efficiency, operating hours, and envelope variables.",
         "对应 R1-MAJ-3、R2-5：准备能碳耦合驱动因素比较。"),
        ("EUI 与 OCEI bootstrap SRC 对比", "Bootstrap SRC comparison for EUI and OCEI",
         "分别对 EUI 和 OCEI 运行 bootstrap SRC，合并得到变量重要性差值和符号稳定性表，导出 eui_ocei_factor_compare_bootstrap_src.csv。",
         "Runs bootstrap SRC separately for EUI and OCEI, merges variable-importance differences and sign-stability information, and exports eui_ocei_factor_compare_bootstrap_src.csv.",
         "对应 R1-MAJ-3、R2-5：比较能耗驱动与碳排放驱动是否一致。"),
        ("EUI-OCEI 关键因素对比图", "EUI-OCEI key-factor comparison plot",
         "绘制 EUI 和 OCEI 的绝对 SRC 并列条形图，展示哪些变量在碳指标下权重增强或减弱。",
         "Plots side-by-side absolute SRC bars for EUI and OCEI, showing which variables gain or lose importance under the carbon metric.",
         "对应 R3-9：增强实践和政策含义讨论。"),
        ("OCEI 预测值与仿真值对比", "Predicted-versus-simulated OCEI plots",
         "对 OCEI 代理模型绘制 out-of-fold 预测值与仿真计算值对比图，标注 R2、CV 方差、RMSE、MAE 和 MAPE。",
         "Plots out-of-fold predicted versus calculated OCEI for the carbon surrogate models and annotates R2, CV variance, RMSE, MAE, and MAPE.",
         "对应 R2-3、R2-5：限定为碳标签代理模型保真度。"),
    ],
}


TRANSLATIONS = {
    "Distribution of Hotel EUI": "酒店建筑 EUI 分布",
    "EUI (kWh/m²·year)": "EUI（kWh/m2·a）",
    "EUI (kWh/m²·a)": "EUI（kWh/m2·a）",
    "Frequency": "频数",
    "Distribution of Hotel energy consumption": "酒店建筑总能耗分布",
    "Energy consumption (kWh)": "能耗（kWh）",
    "Average End-use / Load Components": "平均终端能耗/负荷组成",
    "kWh/year": "kWh/a",
    "Selected Variable Correlation Matrix": "选定变量相关矩阵",
    "Usable Area / Gross Floor Area Ratio": "可用面积/总建筑面积比",
    "Sample Count": "样本数",
    "Density": "密度",
    "DHW per Person (m3/person-d)": "人均生活热水量（m3/(人·d)）",
    "Floor Number": "楼层数",
    "2D Parameter Coverage Check": "二维参数覆盖检验",
    "Simulated EUI vs Published Beijing Hotel Measured Data": "模拟 EUI 与北京酒店实测数据对比",
    "Energy Use Intensity [kWh/(m2.a)]": "建筑能源使用强度 EUI（kWh/(m2·a)）",
    "Probability Density": "概率密度",
    "SRC Magnitude Scree Plot": "SRC 绝对值碎石图",
    "Variable Rank (by |SRC|)": "变量排序（按 |SRC|）",
    "Cumulative SRC Contribution": "SRC 累计贡献",
    "Number of Variables Included": "纳入变量数量",
    "Cumulative |SRC| (%)": "累计 |SRC|（%）",
    "Predictive Power vs Variable Count": "预测能力随变量数量变化",
    "Top 20 Variables by SRC (Linear)": "按 SRC 排序的前 20 个变量（线性）",
    "Top 20 Variables by SHAP (Nonlinear)": "按 SHAP 排序的前 20 个变量（非线性）",
    "Top 18 Standardized Regression Coefficients (SRC)": "前 18 个标准化回归系数（SRC）",
    "Top 18 |SRC| (red = sign-stable, blue = sign-unstable)": "前 18 个 |SRC|（红色=符号稳定，蓝色=符号不稳定）",
    "Envelope-to-floor ratio vs EUI": "围护结构面积比与 EUI",
    "Floor number vs EUI": "楼层数与 EUI",
    "Floor number vs Site Energy": "楼层数与总能耗",
    "Distribution of EUI Labels for Model Training Samples": "模型训练样本 EUI 标签分布",
    "Mean =": "均值 =",
    "Median =": "中位数 =",
    "Model Comparison by Test R²": "模型测试集 R2 对比",
    "Model Comparison by Test RMSE": "模型测试集 RMSE 对比",
    "Model Comparison by Test MAPE": "模型测试集 MAPE 对比",
    "Model Comparison by 10-fold CV R² Variance": "模型 10 折 CV R2 方差对比",
    "CV R² Variance (lower is better)": "CV R2 方差（越低越好）",
    "Generalization Gap (Train R² - Test R²)": "泛化间隙（训练 R2 - 测试 R2）",
    "Predicted vs Simulated EUI (Test Set)": "预测 EUI 与仿真 EUI 对比（测试集）",
    "Simulated EUI (kWh/m²·year)": "仿真 EUI（kWh/m2·a）",
    "Predicted EUI (kWh/m²·year)": "预测 EUI（kWh/m2·a）",
    "Distribution of OCEI": "OCEI 分布",
    "OCEI (kgCO2e/m²·year)": "OCEI（kgCO2e/m2·a）",
    "Contribution of carbon emissions by Energy Carrier": "按能源载体划分的碳排放贡献",
    "Annual carbon contribution (kgCO2e.year)": "年碳排放贡献（kgCO2e/a）",
    "Contribution of average OCEI by Energy Carrier": "按能源载体划分的平均 OCEI 贡献",
    "Cross-analysis of EUI and OCEI": "EUI 与 OCEI 交叉分析",
    "Ranking Shift between EUI and OCEI": "EUI 与 OCEI 排名偏移",
    "Rank by EUI": "按 EUI 排名",
    "Rank by OCEI": "按 OCEI 排名",
    "Comparison of Key Factors for EUI and OCEI": "EUI 与 OCEI 关键因素对比",
    "Absolute standardized regression coefficient (|SRC|)": "标准化回归系数绝对值（|SRC|）",
    "Predicted vs Simulated Carbon Intensity": "预测碳强度与计算碳强度对比",
    "Simulated carbon intensity (kgCO2e/m²·year)": "计算碳强度（kgCO2e/m2·a）",
    "Predicted carbon intensity (kgCO2e/m²·year)": "预测碳强度（kgCO2e/m2·a）",
}


NB01_CELL4 = r'''
# ============================================================
# [IMPROVEMENT P0-2] Feasibility Screening Distribution Analysis
# Quantifies pre/post-filter shifts and visualises retained coverage.
# ============================================================

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy.stats import ks_2samp

rng = np.random.default_rng(CONFIG["random_seed"])

# Use the resolved full sample table so retained/rejected samples are tracked
# by the original LHS row rather than by a reset index.
all_resolved = samples_all.copy()
raw_ratio = all_resolved["usable_area_ratio"].copy()
retained_mask = all_resolved["geometry_feasible"].to_numpy()
filtered_ratio = all_resolved.loc[retained_mask, "usable_area_ratio"].copy()

fig, axes = plt.subplots(1, 3, figsize=(18, 5), dpi=150)

# Panel 1: Raw ratio histogram with filter bounds.
ax = axes[0]
ax.hist(raw_ratio, bins=80, color='steelblue', edgecolor='white', alpha=0.8,
        label=f'全部 LHS 样本 (n={len(raw_ratio):,})')
ax.axvline(CONFIG["min_usable_ratio"], color='red', linestyle='--', linewidth=2,
           label=f'下界 {CONFIG["min_usable_ratio"]}')
ax.axvline(CONFIG["max_usable_ratio"], color='darkred', linestyle='--', linewidth=2,
           label=f'上界 {CONFIG["max_usable_ratio"]}')
retention = len(filtered_ratio) / len(raw_ratio) * 100
ax.set_xlabel('可用面积/总建筑面积比')
ax.set_ylabel('样本数')
ax.set_title(f'筛选前分布 | 保留率 {retention:.1f}% ({len(filtered_ratio):,}/{len(raw_ratio):,})')
ax.legend(fontsize=9)
ax.grid(axis='y', alpha=0.3)

# Panel 2: Pre vs post density comparison.
ax = axes[1]
ax.hist(raw_ratio, bins=80, color='steelblue', edgecolor='white', alpha=0.5,
        density=True, label=f'筛选前 (n={len(raw_ratio):,})')
ax.hist(filtered_ratio, bins=40, color='darkorange', edgecolor='white', alpha=0.7,
        density=True, label=f'筛选后 (n={len(filtered_ratio):,})')
ax.set_xlabel('可用面积/总建筑面积比')
ax.set_ylabel('密度')
ax.set_title('筛选前后分布对比（归一化）')
ax.legend(fontsize=9)
ax.grid(axis='y', alpha=0.3)

# Panel 3: 2D parameter coverage check using true retained/rejected masks.
ax = axes[2]
rejected_index = np.flatnonzero(~retained_mask)
retained_index = np.flatnonzero(retained_mask)
rej_show = rng.choice(rejected_index, size=min(2500, len(rejected_index)), replace=False)
ret_show = rng.choice(retained_index, size=min(2500, len(retained_index)), replace=False)
ax.scatter(all_resolved.iloc[rej_show]['dhw_per_person'],
           all_resolved.iloc[rej_show]['floor_num'],
           c='grey', s=4, alpha=0.18, label='剔除样本')
ax.scatter(all_resolved.iloc[ret_show]['dhw_per_person'],
           all_resolved.iloc[ret_show]['floor_num'],
           c='darkorange', s=6, alpha=0.50, label='保留样本')
ax.set_xlabel('人均生活热水量（m3/(人·d)）')
ax.set_ylabel('楼层数')
ax.set_title('二维参数覆盖检验')
ax.legend(fontsize=9, markerscale=3)
ax.grid(alpha=0.3)

plt.tight_layout()
out_dir = PROJECT_ROOT / 'outputs_step1' / 'figures'
out_dir.mkdir(parents=True, exist_ok=True)
fig.savefig(out_dir / 'feasibility_screening_analysis.png', dpi=300, bbox_inches='tight')
plt.show()


def js_distance_continuous(a, b, bins=40):
    """Jensen-Shannon distance on common histogram bins."""
    a = pd.Series(a).dropna().astype(float)
    b = pd.Series(b).dropna().astype(float)
    lo = min(a.min(), b.min())
    hi = max(a.max(), b.max())
    if np.isclose(lo, hi):
        return 0.0
    counts_a, edges = np.histogram(a, bins=bins, range=(lo, hi), density=False)
    counts_b, _ = np.histogram(b, bins=edges, density=False)
    pa = counts_a + 1e-12
    pb = counts_b + 1e-12
    pa = pa / pa.sum()
    pb = pb / pb.sum()
    return float(jensenshannon(pa, pb, base=2.0))


shift_rows = []
for feature in [f["name"] for f in FEATURES]:
    pre = all_resolved[feature]
    post = all_resolved.loc[retained_mask, feature]
    if pd.api.types.is_numeric_dtype(pre):
        ks_stat, ks_p = ks_2samp(pre.dropna(), post.dropna())
        js_dist = js_distance_continuous(pre, post)
        shift_rows.append({
            "feature": feature,
            "pre_mean": pre.mean(),
            "post_mean": post.mean(),
            "mean_shift_pct": (post.mean() / pre.mean() - 1) * 100 if pre.mean() != 0 else np.nan,
            "pre_std": pre.std(),
            "post_std": post.std(),
            "ks_statistic": ks_stat,
            "ks_p_value": ks_p,
            "jensen_shannon_distance": js_dist,
        })

screening_shift_df = pd.DataFrame(shift_rows).sort_values(
    ["ks_statistic", "jensen_shannon_distance"], ascending=False
)
screening_shift_df.to_csv(
    OUTPUT_DIR / "feasibility_screening_variable_distribution_shift.csv",
    index=False,
    encoding="utf-8-sig"
)

print("=" * 60)
print("可行性筛选分析 / FEASIBILITY SCREENING ANALYSIS")
print("=" * 60)
print(f"筛选前样本数 / Pre-filter samples:  {len(raw_ratio):,}")
print(f"筛选后样本数 / Post-filter samples: {len(filtered_ratio):,}")
print(f"剔除率 / Rejection rate: {(1 - retention/100) * 100:.1f}%")
print(f"筛选前面积比: mean={raw_ratio.mean():.3f}, std={raw_ratio.std():.3f}, "
      f"min={raw_ratio.min():.3f}, max={raw_ratio.max():.3f}")
print(f"筛选后面积比: mean={filtered_ratio.mean():.3f}, std={filtered_ratio.std():.3f}, "
      f"min={filtered_ratio.min():.3f}, max={filtered_ratio.max():.3f}")
ks_stat, ks_p = ks_2samp(raw_ratio, filtered_ratio)
print(f"面积比两样本 KS 检验: D={ks_stat:.4f}, p={ks_p:.4g}")
print("\n变量级分布偏移最大的前 10 项：")
display(screening_shift_df.head(10).round(4))
print(f"\n变量分布偏移表已保存: {OUTPUT_DIR / 'feasibility_screening_variable_distribution_shift.csv'}")
'''


NB03_CELL6 = r'''
# ============================================================
# [IMPROVEMENT P1-6] Hyperparameter Tuning Report
# Robustly extract final hyperparameters and search settings.
# ============================================================

from sklearn.model_selection import GridSearchCV, RandomizedSearchCV


def clean_param_dict(params):
    """Remove Pipeline prefixes and convert values to readable strings."""
    cleaned = {}
    if not params:
        return cleaned
    for key, value in params.items():
        clean_key = key.replace("model__", "").replace("prep__", "")
        if isinstance(value, (list, tuple)):
            cleaned[clean_key] = str(value)
        elif hasattr(value, "item"):
            cleaned[clean_key] = value.item()
        else:
            cleaned[clean_key] = value
    return cleaned


def extract_pipeline_model_params(best_model):
    """Extract final estimator parameters from an already fitted Pipeline."""
    params = {}
    estimator = best_model
    if hasattr(best_model, "named_steps"):
        estimator = best_model.named_steps.get("model", best_model)
        if "poly" in best_model.named_steps:
            poly = best_model.named_steps["poly"]
            params["polynomial_degree"] = getattr(poly, "degree", None)
            params["interaction_only"] = getattr(poly, "interaction_only", None)
            params["include_bias"] = getattr(poly, "include_bias", None)
            params["n_polynomial_features"] = getattr(poly, "n_output_features_", None)
    if hasattr(estimator, "alpha_"):
        params["alpha"] = float(estimator.alpha_)
    if hasattr(estimator, "l1_ratio_"):
        params["l1_ratio"] = float(estimator.l1_ratio_)
    for attr in [
        "n_neighbors", "weights", "p", "C", "epsilon", "gamma", "n_estimators",
        "max_depth", "min_samples_split", "min_samples_leaf", "max_features",
        "learning_rate", "subsample", "colsample_bytree", "num_leaves",
        "hidden_layer_sizes", "activation"
    ]:
        if hasattr(estimator, attr):
            params[attr] = getattr(estimator, attr)
    return params


hp_rows = []
for model_name in metrics_df["model"]:
    best_model = fitted_models[model_name]
    search_obj = search_objects.get(model_name)
    row = {
        "model": model_name,
        "search_method": "none",
        "cv_folds": INNER_CV,
        "scoring": "not_applicable",
    }

    if isinstance(search_obj, GridSearchCV):
        row["search_method"] = "GridSearchCV"
        row["scoring"] = search_obj.scoring
        row.update(clean_param_dict(search_obj.best_params_))
        row["best_cv_rmse"] = -float(search_obj.best_score_)
    elif isinstance(search_obj, RandomizedSearchCV):
        row["search_method"] = "RandomizedSearchCV"
        row["n_iter"] = search_obj.n_iter
        row["scoring"] = search_obj.scoring
        row.update(clean_param_dict(search_obj.best_params_))
        row["best_cv_rmse"] = -float(search_obj.best_score_)
    else:
        row["search_method"] = "embedded_cv_or_fixed"
        row.update(extract_pipeline_model_params(best_model))

    hp_rows.append(row)

hp_df = pd.DataFrame(hp_rows)
hp_df.to_csv(OUT_DIR / "model_hyperparameters.csv", index=False, encoding="utf-8-sig")

print("=" * 70)
print("模型超参数报告 / MODEL HYPERPARAMETER REPORT")
print("=" * 70)
display(hp_df)

print("\n" + "=" * 70)
print("前 5 名模型详细配置 / TOP 5 MODELS — DETAILED HYPERPARAMETERS")
print("=" * 70)
top5_names = metrics_df.head(5)["model"].tolist()
for name in top5_names:
    print(f"\n--- {name} ---")
    print(hp_df.loc[hp_df["model"] == name].dropna(axis=1).to_string(index=False))
    if name in search_spaces:
        print(f"搜索空间 / Search space: {search_spaces[name]}")
'''


NB04_SENSITIVITY = r'''
# ============================================================
# [IMPROVEMENT P0-3] Carbon Emission Factor Sensitivity Analysis
# Tests robustness of EUI-OCEI coupling under alternative factors.
# ============================================================

from scipy.stats import pearsonr

scenarios = {
    'Baseline': {
        'electricity': 0.55, 'natural_gas': 0.202,
        'district_heating': 0.22, 'district_cooling': 0.16
    },
    'Electricity Low 0.40': {
        'electricity': 0.40, 'natural_gas': 0.202,
        'district_heating': 0.22, 'district_cooling': 0.16
    },
    'Electricity High 0.70': {
        'electricity': 0.70, 'natural_gas': 0.202,
        'district_heating': 0.22, 'district_cooling': 0.16
    },
    'Grid Decarbonisation 2030 0.40': {
        'electricity': 0.40, 'natural_gas': 0.202,
        'district_heating': 0.22, 'district_cooling': 0.16
    },
    'Grid Decarbonisation 2050 0.25': {
        'electricity': 0.25, 'natural_gas': 0.202,
        'district_heating': 0.22, 'district_cooling': 0.16
    },
    'High District Thermal Factors': {
        'electricity': 0.55, 'natural_gas': 0.202,
        'district_heating': 0.30, 'district_cooling': 0.20
    },
}

scenario_results = []
scenario_ocei = {}

for sc_name, ef in scenarios.items():
    carrier_carbon = pd.DataFrame({
        'electricity': df['electricity_kwh_for_carbon'] * ef['electricity'],
        'natural_gas': df['natural_gas_kwh_for_carbon'] * ef['natural_gas'],
        'district_heating': df['district_heating_kwh_for_carbon'] * ef['district_heating'],
        'district_cooling': df['district_cooling_kwh_for_carbon'] * ef['district_cooling'],
    })
    ocei_sc = carrier_carbon.sum(axis=1) / df['gross_floor_area_m2']
    scenario_ocei[sc_name] = ocei_sc

    r_eui, p_eui = pearsonr(df['eui_kwh_m2'], ocei_sc)
    rank_base = df['OCEI_kgco2e_m2'].rank(method='first', ascending=True)
    rank_sc = ocei_sc.rank(method='first', ascending=True)
    top_n = max(1, int(len(df) * 0.10))
    overlap = len(set(rank_base.nsmallest(top_n).index) & set(rank_sc.nsmallest(top_n).index)) / top_n

    total_by_carrier = carrier_carbon.sum()
    share_by_carrier = total_by_carrier / total_by_carrier.sum()

    scenario_results.append({
        'scenario': sc_name,
        'mean_ocei': ocei_sc.mean(),
        'std_ocei': ocei_sc.std(),
        'corr_with_baseline_ocei': ocei_sc.corr(df['OCEI_kgco2e_m2']),
        'eui_ocei_pearson_r': r_eui,
        'eui_ocei_pearson_p': p_eui,
        'top10_overlap_with_baseline': overlap,
        'electricity_share': share_by_carrier['electricity'],
        'natural_gas_share': share_by_carrier['natural_gas'],
        'district_heating_share': share_by_carrier['district_heating'],
        'district_cooling_share': share_by_carrier['district_cooling'],
    })

scenario_df = pd.DataFrame(scenario_results)

fig, axes = plt.subplots(1, 2, figsize=(16, 6), dpi=150)

ax = axes[0]
baseline_mean = scenario_df.loc[scenario_df['scenario'] == 'Baseline', 'mean_ocei'].values[0]
colors = ['steelblue' if s == 'Baseline' else 'darkorange' if 'Low' in s or '2030' in s or '2050' in s
          else 'darkred' if 'High' in s else 'grey' for s in scenario_df['scenario']]
bars = ax.barh(scenario_df['scenario'], scenario_df['mean_ocei'], color=colors)
ax.axvline(baseline_mean, color='grey', linestyle='--', linewidth=1, alpha=0.7)
ax.set_xlabel('平均 OCEI（kgCO2e/(m2·a)）')
ax.set_title('不同排放因子情景下的平均 OCEI')
for bar, val in zip(bars, scenario_df['mean_ocei']):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}', va='center', fontsize=9)
ax.grid(axis='x', alpha=0.3)

ax = axes[1]
x = np.arange(len(scenario_df))
width = 0.35
ax.bar(x - width/2, scenario_df['eui_ocei_pearson_r'], width,
       label='EUI-OCEI Pearson r', color='steelblue')
ax.set_ylabel('Pearson r', color='steelblue')
ax.tick_params(axis='y', labelcolor='steelblue')

ax2 = ax.twinx()
ax2.bar(x + width/2, scenario_df['top10_overlap_with_baseline'] * 100, width,
        label='Top-10% 重叠率（%）', color='darkorange')
ax2.set_ylabel('Top-10% 重叠率（%）', color='darkorange')
ax2.tick_params(axis='y', labelcolor='darkorange')

ax.set_xticks(x)
ax.set_xticklabels([s.replace(' ', '\n') for s in scenario_df['scenario']], rotation=0, ha='center', fontsize=8)
ax.set_title('EUI-OCEI 耦合指标稳定性')
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc='lower left')

plt.tight_layout()
fig.savefig(FIG_DIR / 'emission_factor_sensitivity.png', dpi=300, bbox_inches='tight')
plt.show()

scenario_df.to_csv(OUT_DIR / 'emission_factor_sensitivity.csv', index=False, encoding='utf-8-sig')

print("=" * 70)
print("排放因子敏感性分析 / EMISSION FACTOR SENSITIVITY ANALYSIS")
print("=" * 70)
display(scenario_df.round(4))
print(f"\n基准 OCEI: {baseline_mean:.2f} ± "
      f"{scenario_df.loc[scenario_df['scenario']=='Baseline','std_ocei'].values[0]:.2f}")
print(f"EUI-OCEI 相关系数范围: "
      f"[{scenario_df['eui_ocei_pearson_r'].min():.4f}, {scenario_df['eui_ocei_pearson_r'].max():.4f}]")
print(f"电力贡献占比范围: "
      f"[{scenario_df['electricity_share'].min()*100:.1f}%, {scenario_df['electricity_share'].max()*100:.1f}%]")
print(f"天然气贡献占比范围: "
      f"[{scenario_df['natural_gas_share'].min()*100:.1f}%, {scenario_df['natural_gas_share'].max()*100:.1f}%]")
'''


NB04_DUAL_CARBON = r'''
# ---------- 5) Consolidated dual-view carbon contribution figure ----------
carrier_carbon_total = pd.Series({
    "electricity": (df["electricity_kwh_for_carbon"] * EMISSION_FACTORS["electricity"]).sum(),
    "natural_gas": (df["natural_gas_kwh_for_carbon"] * EMISSION_FACTORS["natural_gas"]).sum(),
    "district_heating": (df["district_heating_kwh_for_carbon"] * EMISSION_FACTORS["district_heating"]).sum(),
    "district_cooling": (df["district_cooling_kwh_for_carbon"] * EMISSION_FACTORS["district_cooling"]).sum(),
}, dtype=float).reindex(["electricity", "natural_gas", "district_heating", "district_cooling"]).fillna(0.0)

carrier_labels_zh = {
    "electricity": "电力",
    "natural_gas": "天然气",
    "district_heating": "区域供热",
    "district_cooling": "区域供冷",
}

carrier_ocei_avg = pd.Series({
    carrier: (df[f"{carrier}_kwh_for_carbon"] * EMISSION_FACTORS[carrier] / df["gross_floor_area_m2"]).mean()
    for carrier in carrier_carbon_total.index
}, dtype=float)
carrier_share = carrier_carbon_total / carrier_carbon_total.sum()

carbon_breakdown_df = pd.DataFrame({
    "carrier": carrier_carbon_total.index,
    "carrier_zh": [carrier_labels_zh[c] for c in carrier_carbon_total.index],
    "total_carbon_kgco2e": carrier_carbon_total.values,
    "avg_carbon_kgco2e_per_sample": (carrier_carbon_total / len(df)).values,
    "avg_ocei_kgco2e_m2": carrier_ocei_avg.values,
    "share": carrier_share.values,
})
carbon_breakdown_df.to_csv(OUT_DIR / "carbon_breakdown_by_carrier.csv", index=False, encoding="utf-8-sig")

fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.2), dpi=150)

ax = axes[0]
bars = ax.bar(carbon_breakdown_df["carrier_zh"], carbon_breakdown_df["total_carbon_kgco2e"], color="#4C72B0")
ax.set_title("各能源载体总碳排放贡献")
ax.set_ylabel("年碳排放贡献（kgCO2e/a）")
ax.tick_params(axis="x", rotation=20)
for bar, share in zip(bars, carbon_breakdown_df["share"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
            f"{share*100:.1f}%", ha="center", va="bottom", fontsize=9)

ax = axes[1]
bars = ax.bar(carbon_breakdown_df["carrier_zh"], carbon_breakdown_df["avg_ocei_kgco2e_m2"], color="#DD8452")
ax.set_title("各能源载体平均 OCEI 贡献")
ax.set_ylabel("OCEI 贡献（kgCO2e/(m2·a)）")
ax.tick_params(axis="x", rotation=20)
for bar, val in zip(bars, carbon_breakdown_df["avg_ocei_kgco2e_m2"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
            f"{val:.1f}", ha="center", va="bottom", fontsize=9)

fig.tight_layout()
fig.savefig(FIG_DIR / "carbon_contribution_dual_view.png", dpi=300, bbox_inches="tight")
plt.show()

display(carbon_breakdown_df.round(4))
'''


NB04_NORMALIZED_CHECK = r'''
# ---------- 5A) Normalised OCEI contribution check ----------
if "carbon_breakdown_df" not in globals():
    raise RuntimeError("Please run the consolidated carbon-contribution cell first.")

normalized_ocei_contribution = carbon_breakdown_df[[
    "carrier", "carrier_zh", "avg_ocei_kgco2e_m2", "share"
]].copy()
normalized_ocei_contribution["share_percent"] = normalized_ocei_contribution["share"] * 100
normalized_ocei_contribution.to_csv(
    OUT_DIR / "normalized_ocei_contribution_by_carrier.csv",
    index=False,
    encoding="utf-8-sig"
)
display(normalized_ocei_contribution.round(4))
print("归一化 OCEI 贡献已并入 carbon_contribution_dual_view.png，不再生成重复的单独图。")
'''


NB04_CARBON_TABLE_DISPLAY = r'''
# ---------- 5-Table) Carbon-contribution table display ----------
if "carbon_breakdown_df" not in globals():
    raise RuntimeError("请先运行合并双视图碳贡献图 cell。")

display_cols = [
    "carrier", "carrier_zh", "total_carbon_kgco2e",
    "avg_carbon_kgco2e_per_sample", "avg_ocei_kgco2e_m2", "share"
]
display(carbon_breakdown_df[display_cols].round(4))
'''


def dedent(s: str) -> str:
    return textwrap.dedent(s).strip() + "\n"


def load_nb(name: str):
    return nbformat.read(ROOT / name, as_version=4)


def write_nb(name: str, nb) -> None:
    nbformat.write(nb, ROOT / name)


def remove_generated_explanations(nb) -> None:
    nb.cells = [
        cell for cell in nb.cells
        if not (cell.cell_type == "markdown" and MARKER_START in cell.source and MARKER_END in cell.source)
    ]


def code_cells(nb):
    return [cell for cell in nb.cells if cell.cell_type == "code"]


def find_code_cell(nb, cell_id: str):
    for cell in nb.cells:
        if cell.cell_type == "code" and cell.get("id") == cell_id:
            return cell
    raise KeyError(cell_id)


def apply_common_plot_translations(nb) -> None:
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        source = cell.source
        for old, new in TRANSLATIONS.items():
            source = source.replace(old, new)
        cell.source = source


def ensure_chinese_font(cell0) -> None:
    if "font.sans-serif" in cell0.source:
        return
    needle = 'plt.rcParams.update({'
    insert = (
        'plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]\n'
        'plt.rcParams["axes.unicode_minus"] = False\n\n'
    )
    cell0.source = cell0.source.replace(needle, insert + needle, 1)


def patch_nb01(nb) -> None:
    c0 = find_code_cell(nb, "6d363436")
    c0.source = c0.source.replace("import os\n", "import os\n")
    c0.source = c0.source.replace('"n_samples": 20000,', '"n_samples": int(os.environ.get("EUI_N_SAMPLES", "20000")),')
    c0.source = c0.source.replace('"run_energyplus": True,', '"run_energyplus": os.environ.get("EUI_RUN_ENERGYPLUS", "0") == "1",')
    if '"clean_idf_dir"' not in c0.source:
        c0.source = c0.source.replace(
            '"timeout_seconds": 900,',
            '"timeout_seconds": int(os.environ.get("EUI_TIMEOUT_SECONDS", "900")),\n'
            '    "clean_idf_dir": os.environ.get("EUI_CLEAN_IDF_DIR", "0") == "1",\n'
            '    "clean_run_dir": os.environ.get("EUI_CLEAN_RUN_DIR", "0") == "1",'
        )
    ensure_chinese_font(c0)

    c3 = find_code_cell(nb, "9e92bbf6")
    c3.source = c3.source.replace(
        'samples_raw = lhs_sample(feature_df, CONFIG["n_samples"], CONFIG["random_seed"])\n'
        'samples = resolve_dependencies(samples_raw)\n'
        'samples = samples.loc[samples["geometry_feasible"]].reset_index(drop=True)\n',
        'samples_raw = lhs_sample(feature_df, CONFIG["n_samples"], CONFIG["random_seed"])\n'
        'samples_raw["source_lhs_index"] = np.arange(len(samples_raw))\n'
        'samples_all = resolve_dependencies(samples_raw)\n'
        'samples = samples_all.loc[samples_all["geometry_feasible"]].copy().reset_index(drop=True)\n'
    )

    find_code_cell(nb, "fe5b259b").source = dedent(NB01_CELL4)

    c8 = find_code_cell(nb, "48c2e3f9")
    c8.source = c8.source.replace(
        'if IDF_DIR.exists():\n    shutil.rmtree(IDF_DIR)\nif RUN_DIR.exists():\n    shutil.rmtree(RUN_DIR)\n\nIDF_DIR.mkdir(parents=True, exist_ok=True)\nRUN_DIR.mkdir(parents=True, exist_ok=True)\n\nimport shutil\n',
        'if CONFIG.get("clean_idf_dir", False) and IDF_DIR.exists():\n    shutil.rmtree(IDF_DIR)\nif CONFIG.get("clean_run_dir", False) and RUN_DIR.exists():\n    shutil.rmtree(RUN_DIR)\n\nIDF_DIR.mkdir(parents=True, exist_ok=True)\nRUN_DIR.mkdir(parents=True, exist_ok=True)\n\n'
    )


def patch_nb02(nb) -> None:
    c0 = code_cells(nb)[0]
    if "import os" not in c0.source:
        c0.source = c0.source.replace("from pathlib import Path\n", "from pathlib import Path\nimport os\n")
    if "FAST_MODE" not in c0.source:
        c0.source += '\nFAST_MODE = os.environ.get("EUI_FAST_MODE", "0") == "1"\nBOOTSTRAP_N = 100 if FAST_MODE else 1000\n'
    ensure_chinese_font(c0)
    for cell in code_cells(nb):
        cell.source = cell.source.replace("B=1000", "B=BOOTSTRAP_N")
        cell.source = cell.source.replace("B = 1000", "B = BOOTSTRAP_N")
    c6 = find_code_cell(nb, "319ecff6")
    c6.source = c6.source.replace(
        "n_estimators=500, max_depth=5, learning_rate=0.05,",
        "n_estimators=(200 if FAST_MODE else 500), max_depth=5, learning_rate=0.05,"
    )


def patch_nb03(nb) -> None:
    c0 = code_cells(nb)[0]
    if "import os" not in c0.source:
        c0.source = c0.source.replace("import warnings\n", "import warnings\nimport os\n")
    c0.source = c0.source.replace("INNER_CV = 10", 'FAST_MODE = os.environ.get("EUI_FAST_MODE", "0") == "1"\nINNER_CV = 3 if FAST_MODE else 10\nSEARCH_N_ITER = 3 if FAST_MODE else 20')
    ensure_chinese_font(c0)

    c4 = find_code_cell(nb, "173c1d65")
    c4.source = c4.source.replace("n_iter=20", "n_iter=SEARCH_N_ITER")
    if "search_spaces =" not in c4.source:
        c4.source = c4.source.replace("print(\"Total models:\", len(all_estimators))", "search_spaces = {name: getattr(searcher, 'param_distributions', getattr(searcher, 'param_grid', None)) for name, searcher in searchers.items()}\nif HAS_XGB:\n    search_spaces['XGBoost'] = all_estimators['XGBoost'].param_distributions\nif HAS_LGBM:\n    search_spaces['LightGBM'] = all_estimators['LightGBM'].param_distributions\n\nprint(\"Total models:\", len(all_estimators))")

    c5 = find_code_cell(nb, "86e190c0")
    c5.source = c5.source.replace(
        "    fitted_models = {}\n",
        "    fitted_models = {}\n    search_objects = {}\n    best_params_by_model = {}\n"
    )
    c5.source = c5.source.replace(
        "        fitted_models[name] = best_model\n",
        "        fitted_models[name] = best_model\n        search_objects[name] = est\n        best_params_by_model[name] = best_params\n"
    )
    c5.source = c5.source.replace(
        "    return result_df, fitted_models\n",
        "    return result_df, fitted_models, search_objects, best_params_by_model\n"
    )
    c5.source = c5.source.replace(
        "metrics_df, fitted_models = fit_and_compare_models(\n    X_train, y_train, X_test, y_test, all_estimators\n)\n",
        "metrics_df, fitted_models, search_objects, best_params_by_model = fit_and_compare_models(\n    X_train, y_train, X_test, y_test, all_estimators\n)\n"
    )

    find_code_cell(nb, "23c3095c").source = dedent(NB03_CELL6)

    c7 = find_code_cell(nb, "1de98079")
    guarded = "if HAS_XGB:\n    pipe_xgb_full = Pipeline(["
    if guarded not in c7.source:
        c7.source = c7.source.replace(
            "# XGBoost with 39 vars\npipe_xgb_full = Pipeline([",
            "# XGBoost with 39 vars\nif HAS_XGB:\n    pipe_xgb_full = Pipeline(["
        )
        c7.source = c7.source.replace(
            "])\npipe_xgb_full.fit(Xf_train, yf_train)\nxgb_full_r2 = pipe_xgb_full.score(Xf_test, yf_test)\n",
            "    ])\n    pipe_xgb_full.fit(Xf_train, yf_train)\n    xgb_full_r2 = pipe_xgb_full.score(Xf_test, yf_test)\nelse:\n    xgb_full_r2 = np.nan\n"
        )


def patch_nb04(nb) -> None:
    c0 = code_cells(nb)[0]
    if "import os" not in c0.source:
        c0.source = c0.source.replace("from pathlib import Path\n", "from pathlib import Path\nimport os\n")
    if "FAST_MODE" not in c0.source:
        c0.source += '\nFAST_MODE = os.environ.get("EUI_FAST_MODE", "0") == "1"\nBOOTSTRAP_N = 100 if FAST_MODE else 1000\nCARBON_CV_SPLITS = 3 if FAST_MODE else 10\n'
    ensure_chinese_font(c0)

    sensitivity = find_code_cell(nb, "1657814c")
    sensitivity.source = dedent(NB04_SENSITIVITY)
    # Move sensitivity analysis after the data/OCEI construction cell.
    nb.cells.remove(sensitivity)
    data_cell_index = next(i for i, cell in enumerate(nb.cells) if cell.get("id") == "613eaf47")
    nb.cells.insert(data_cell_index + 1, sensitivity)

    c8 = find_code_cell(nb, "1de8d2b7")
    c8.source = c8.source.replace("KFold(n_splits=10", "KFold(n_splits=CARBON_CV_SPLITS")

    c4 = find_code_cell(nb, "613eaf47")
    c4.source = c4.source.replace(
        '    if col not in df.columns:\n        df[col] = 0.0\n\n# Fixed boundary:',
        '    if col not in df.columns:\n        df[col] = 0.0\n    df[col] = pd.to_numeric(df[col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)\n\n# Fixed boundary:'
    )

    c6 = find_code_cell(nb, "cd30db53-a48c-473f-91bb-2422530256b1")
    c6.source = c6.source.replace(
        '        if col not in d.columns:\n            d[col] = 0.0\n\n    if scenario == "baseline":',
        '        if col not in d.columns:\n            d[col] = 0.0\n        d[col] = pd.to_numeric(d[col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)\n\n    if scenario == "baseline":'
    )

    c7 = find_code_cell(nb, "5143689c")
    if "valid_ocei_mask" not in c7.source:
        c7.source = c7.source.replace(
            'X = df[top18].copy()\ny = df["OCEI_kgco2e_m2"].copy()\n',
            'X = df[top18].copy()\ny = pd.to_numeric(df["OCEI_kgco2e_m2"], errors="coerce").replace([np.inf, -np.inf], np.nan)\nvalid_ocei_mask = np.isfinite(y.to_numpy())\nif not valid_ocei_mask.all():\n    print(f"剔除 OCEI 缺失或非有限样本 / Dropping invalid OCEI rows: {(~valid_ocei_mask).sum()}")\nX = X.loc[valid_ocei_mask].reset_index(drop=True)\ny = y.loc[valid_ocei_mask].reset_index(drop=True)\n'
        )

    c15 = find_code_cell(nb, "706e1472-d02a-429c-a699-9c444858dbb8")
    c15.source = c15.source.replace("B=1000", "B=BOOTSTRAP_N")
    c15.source = c15.source.replace("B=1000)", "B=BOOTSTRAP_N)")
    c15.source = c15.source.replace("B=1000", "B=BOOTSTRAP_N")

    find_code_cell(nb, "4d0bec80").source = dedent(NB04_DUAL_CARBON)
    find_code_cell(nb, "dba3169d-b78f-4c69-a278-a4da521d6921").source = dedent(NB04_CARBON_TABLE_DISPLAY)
    find_code_cell(nb, "6de5d219-82cc-44e0-ba36-7c7526663cbf").source = dedent(NB04_NORMALIZED_CHECK)


def explanation_cell(index: int, item) -> str:
    zh_title, en_title, zh, en, review = item
    return dedent(f"""
    {MARKER_START}
    ### Cell {index:02d} — {zh_title} / {en_title}

    **中文说明**：{zh}

    **输入与依赖**：本 cell 依赖前序 cell 中已经定义的数据对象、配置参数、路径或模型；若为第一个代码 cell，则依赖本地 Python/Jupyter 环境和项目目录结构。

    **输出与复现作用**：本 cell 会生成内存对象、CSV 文件、图像文件、模型文件或诊断打印信息，作为后续 notebook 步骤和论文修订证据链的一部分。

    **审稿意见对应**：{review}

    **English explanation**: {en}

    **Inputs and dependencies**: This cell depends on data objects, configuration values, paths, or models defined in previous cells; if it is the first code cell, it depends on the local Python/Jupyter environment and project directory structure.

    **Outputs and reproducibility role**: This cell generates in-memory objects, CSV files, figure files, model files, or diagnostic printouts that become part of the downstream notebook workflow and the manuscript-revision evidence chain.

    **Reviewer-response link**: {review}
    {MARKER_END}
    """)


def insert_explanations(nb, name: str) -> None:
    explanations = NOTEBOOKS[name]
    code_count = sum(1 for cell in nb.cells if cell.cell_type == "code")
    if len(explanations) != code_count:
        raise ValueError(f"{name}: explanation count {len(explanations)} != code cells {code_count}")
    new_cells = []
    code_idx = 0
    for cell in nb.cells:
        if cell.cell_type == "code":
            code_idx += 1
            new_cells.append(new_markdown_cell(explanation_cell(code_idx, explanations[code_idx - 1])))
        new_cells.append(cell)
    nb.cells = new_cells


def patch_notebook(name: str) -> None:
    nb = load_nb(name)
    remove_generated_explanations(nb)
    if name.startswith("01_"):
        patch_nb01(nb)
    elif name.startswith("02_"):
        patch_nb02(nb)
    elif name.startswith("03_"):
        patch_nb03(nb)
    elif name.startswith("04_"):
        patch_nb04(nb)
    apply_common_plot_translations(nb)
    insert_explanations(nb, name)
    write_nb(name, nb)
    print(f"patched {name}")


def main() -> None:
    for name in NOTEBOOKS:
        patch_notebook(name)


if __name__ == "__main__":
    main()
