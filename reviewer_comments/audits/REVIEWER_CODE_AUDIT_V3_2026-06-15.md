# 第三版代码研究层面审稿意见核对表

更新时间：2026-06-15  
范围：四个主 Jupyter Notebook、`outputs_step*/` 输出目录、第三版新增图件和项目说明文件。

## 总体结论

代码研究层面的主要补强已经落实到四个 notebook：可行性筛选分布诊断、SRC-SHAP 双方法敏感性分析、变量截断依据、超参数报告、非核心变量固定影响分析、排放因子来源和情景敏感性分析均已有对应代码入口。第三版进一步修正了 notebook 说明 cell 的重复审稿语气，并新增两张可复现科研示意图。

仍需诚实保留的限制：当前本地数据集为 116 个样本，尚不是 `n_samples=20000` 后筛选得到的约 4640 个完整仿真样本。因此所有需要全量统计稳定性的结果仍需在长时 EnergyPlus 仿真完成后重新执行 01->04 全流程。

## Reviewer 1 Major Comments

| ID | 代码层状态 | 核查结论 |
|---|---|---|
| R1-MAJ-1 Sim-to-Real Gap | 基本完成，需全量数据复算 | NB01 已有模拟 EUI 与北京酒店实测/标准基准对比代码；精度表述应继续限定为 surrogate fidelity。116 样本结果只能作为快速验证，完整偏差需全量 4640 样本复算。 |
| R1-MAJ-2 Feasibility Screening | 基本完成 | NB01 已有筛选前后分布、二维覆盖、KS/Jensen-Shannon 诊断。仍建议论文文字说明缺少真实酒店面积分配调查数据时的边界。 |
| R1-MAJ-3 SRC vs Nonlinearity | 基本完成 | NB02 已加入 SHAP 与 SRC 排序对比，可作为非线性补充解释。Sobol 未做，但 SHAP 已能回应“线性 SRC 单独不足”的核心问题。 |
| R1-MAJ-4 Carbon Factors | 基本完成 | NB04 已加入排放因子来源表和 6 情景敏感性分析；第三版修复了敏感性图的图例和标签拥挤风险，并导出 SVG/PDF。 |
| R1-MAJ-5 EnergyPlus Reproducibility | 基本完成 | NB01 已记录几何模板、IdealLoadsAirSystem、DHW 后处理、气象文件、版本和 IDF 生成逻辑；第三版新增酒店热工程示意图。 |
| R1-MAJ-6 Citation/statistical wording | 非代码项 | 需在 manuscript 文本中最终核查引用标签；代码层面无直接动作。 |
| R1-MAJ-7 Hyperparameters | 基本完成 | NB03 已自动提取最优超参数、搜索空间和模型参数表。论文/补充材料需同步引用输出表。 |
| R1-MAJ-8 18-variable cutoff | 基本完成 | NB02 已有 SRC 碎石图、累积贡献、CV R2 曲线。完整结论需在全量数据后确认阈值是否仍稳定。 |

## Reviewer 1 Minor Comments

| ID | 代码层状态 | 核查结论 |
|---|---|---|
| R1-MIN-1 to R1-MIN-4 | 非代码项 | 标题、交叉引用、语态和章节编号主要在 manuscript 中完成，代码层无需进一步修改。 |
| R1-MIN-5 Figures 15/16 redundancy | 完成 | NB04 已合并为 `carbon_contribution_dual_view` 逻辑；第三版保留合并图思路并继续要求无重复图。 |
| R1-MIN-6 | 非代码项 | “crystal transparency” 属论文文字项。 |
| R1-MIN-7 Window construction type | 基本完成 | NB01 参数和说明中已有窗型定义；建议论文表 1 脚注同步。 |
| R1-MIN-8 Hotel category limitation | 论文讨论项 | 代码无法替代星级/类别实测数据；应在局限性中突出。 |
| R1-MIN-9 2026 references | 文献核查项 | 需最终人工核查 references。 |

## Reviewer 2 Comments

| ID | 代码层状态 | 核查结论 |
|---|---|---|
| R2-1 Screening representativeness | 基本完成 | NB01 已量化筛选前后分布差异。仍需全量样本复算 KS/JSD 表。 |
| R2-2 Why SRC | 基本完成 | NB02 通过 SHAP 补充验证；论文方法中需说明选择 SRC 的计算成本与解释性理由。 |
| R2-3 Leakage risk | 基本完成 | NB03 使用 train/test split 和 Pipeline；需在论文中明确标准化、插补、模型拟合均在 split 后流程内完成。 |
| R2-4 Fixed non-core variables | 基本完成 | NB03 已比较 18 变量与全变量模型表现；需在 Discussion 解释概念设计阶段实用性。 |
| R2-5 Grid decarbonization | 基本完成 | NB04 已覆盖 2030/2050 电网脱碳情景；需在论文中讨论电力占比下降后天然气/DHW 相对重要性上升。 |

## Reviewer 3 Comments

| ID | 代码层状态 | 核查结论 |
|---|---|---|
| R3-1 to R3-3 | 论文结构项 | 创新点、引用格式、文献综述压缩主要属于 manuscript。 |
| R3-4 20000 to 4640 reduction | 基本完成 | NB01 可行性筛选分析已覆盖；建议论文以“独立几何变量组合导致约 23% 可行保留率”的概率逻辑解释。 |
| R3-5 Key-variable criteria | 基本完成 | NB02 三条证据线已具备。 |
| R3-6 Figure readability | 第三版加强 | 已新增项目级图件 QA 标准，重做酒店工程示意图和研究链路图，修复 NB04 敏感性图布局。仍需逐图人工终审。 |
| R3-7 ML assumptions/parameters | 基本完成 | NB03 已有模型假设、Pipeline、超参数输出。 |
| R3-8 Limitations | 论文讨论项 | 代码层提供证据，最终仍需 manuscript 局限性文字承接。 |
| R3-9 Practical implications | 部分完成 | 研究链路图和 EUI-OCEI 分析支持实践意义；若需要更强，可进一步新增具体设计方案示例。 |

## 第三版新增代码与图件

- `tools/generate_publication_figures_v3.py`
- `tools/update_notebooks_for_third_version.py`
- `outputs_step1/figures/hotel_thermal_engineering_schematic_v3.png`
- `outputs_step1/figures/hotel_thermal_engineering_schematic_v3.svg`
- `outputs_step1/figures/hotel_thermal_engineering_schematic_v3.pdf`
- `outputs_step1/figures/research_pipeline_workflow_v3.png`
- `outputs_step1/figures/research_pipeline_workflow_v3.svg`
- `outputs_step1/figures/research_pipeline_workflow_v3.pdf`

## 本地快速验证记录

2026-06-15 已在本地 Python/Jupyter 环境执行快速验证：

- `01_Parametric_Simulation_Database_Construction.ipynb`：通过，`EUI_RUN_ENERGYPLUS=0`，未触发长时 EnergyPlus 仿真。
- `02_SRC_Sensitivity_and_Variable_Selection.ipynb`：通过。
- `03_ML_Model_Training_and_Evaluation.ipynb`：通过；日志中出现 joblib/loky 临时内存映射清理 warning，但进程退出码为 0，结果已写出。
- `04_EUI_OCEI_Coupling_and_Carbon_Analysis.ipynb`：通过；新版 `emission_factor_sensitivity.png|svg|pdf` 已重新生成。

额外说明：`jupyter nbconvert --execute` 在本机因旧版 `jupyter_contrib_nbextensions` 依赖 `notebook.services` 失败，随后改用 `nbclient` 直接执行 notebook，绕开 nbconvert 插件链。该问题属于本地 Jupyter 插件环境问题，不是 notebook 代码错误。

## 尚未完成或不可由快速验证替代的事项

1. 完整 EnergyPlus 数据集仍需运行：`EUI_N_SAMPLES=20000` 且 `EUI_RUN_ENERGYPLUS=1`。
2. 116 样本调试输出不能作为最终论文统计结果。
3. 真实酒店类别、星级、面积分配调查数据若无外部来源，必须作为局限性诚实说明。
4. manuscript 中的表格、图号、补充材料编号和参考文献编号仍需最终同步。
