from __future__ import annotations

import re
from pathlib import Path

import nbformat


def find_repo_root(start: Path) -> Path:
    start = start.resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "input" / "Beijing.epw").exists() or (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


ROOT = find_repo_root(Path(__file__))


INTRO_START = "<!-- CODEx bilingual cell explanation: start -->"
INTRO_END = "<!-- CODEx bilingual cell explanation: end -->"


NEW_NB01_MD = f"""{INTRO_START}
### Cell 06 — 论文级工程示意图与研究链路图 / Publication engineering and workflow schematics

**中文说明**：调用 `tools/generate_publication_figures_v3.py` 中的绘图函数，生成第三版酒店热工程示意图和研究链路图。酒店图把参数化体量、标准层平面、窗墙比传热边界、HVAC/生活热水和 EUI-OCEI 核算边界放在同一张多面板图中；研究链路图用直线和折线展示从参数空间、LHS、EnergyPlus、SRC/SHAP、机器学习到 OCEI 敏感性分析的数据依赖关系。

**输入与依赖**：依赖本 notebook 已建立的 `PROJECT_ROOT` 和 `FIG_DIR`，并依赖项目内绘图脚本。脚本只使用 matplotlib 与标准路径对象，不依赖 EnergyPlus 运行结果，因此可在调试模式下快速复现。

**主要输出**：在 `outputs_step1/figures/` 下写出 `hotel_thermal_engineering_schematic_v3` 和 `research_pipeline_workflow_v3` 的 PNG、SVG、PDF 三种格式。PNG 用于快速预览，SVG/PDF 用于论文排版与后期编辑。

**复现提示**：若中文字体不可用，脚本会回退到 matplotlib 可用字体；正式投稿前应打开 PNG 或 PDF 检查文字是否完整、箭头是否交叉、图例是否遮挡关键信息。

**English explanation**: Calls the plotting functions in `tools/generate_publication_figures_v3.py` to create the third-version hotel thermal-engineering schematic and research workflow diagram. The hotel figure combines parameterised massing, typical floor zoning, window-to-wall and heat-transfer boundaries, HVAC/domestic-hot-water processing, and the EUI-OCEI accounting chain. The workflow diagram uses straight and orthogonal connectors to show dependencies from the parameter space and LHS sampling to EnergyPlus, SRC/SHAP interpretation, machine learning, and OCEI sensitivity analysis.

**Inputs and dependencies**: Uses `PROJECT_ROOT` and `FIG_DIR` defined in this notebook plus the project plotting script. The script only requires matplotlib and path handling, so it can be rerun in debug mode without launching EnergyPlus.

**Main outputs**: Writes PNG, SVG, and PDF versions of `hotel_thermal_engineering_schematic_v3` and `research_pipeline_workflow_v3` under `outputs_step1/figures/`. PNG supports quick visual review, while SVG/PDF preserve editable vector content for manuscript layout.

**Reproducibility note**: If Chinese fonts are unavailable, the script falls back to an available matplotlib font. Before submission, inspect the PNG or PDF to confirm that labels are complete, connectors remain clean, and no legend or annotation overlaps the scientific content.
{INTRO_END}
"""


NEW_NB01_CODE = """# ---------- 3) Publication-grade engineering and research-workflow schematics ----------
from tools.generate_publication_figures_v3 import (
    generate_hotel_engineering_schematic,
    generate_research_workflow,
)

schematic_outputs = generate_hotel_engineering_schematic(FIG_DIR)
workflow_outputs = generate_research_workflow(FIG_DIR)

print("第三版酒店热工程示意图 / Third-version hotel thermal-engineering schematic")
for fmt, path in schematic_outputs.items():
    print(f"  {fmt}: {path}")

print("\\n第三版研究链路图 / Third-version research workflow diagram")
for fmt, path in workflow_outputs.items():
    print(f"  {fmt}: {path}")
"""


def extract_field(src: str, label: str) -> str:
    pat = rf"\*\*{re.escape(label)}\*\*[：:]\s*(.*?)(?=\n\n\*\*|\n{INTRO_END}|\Z)"
    m = re.search(pat, src, flags=re.S)
    if not m:
        return ""
    return " ".join(line.strip() for line in m.group(1).strip().splitlines())


def clean_text(text: str) -> str:
    text = re.sub(r"该 cell 直接检验 .*?核心证据。", "该 cell 定量检查可行性筛选对参数空间覆盖的影响。", text)
    text = text.replace("是回应样本代表性和选择偏差质疑的核心证据", "用于量化样本代表性和潜在选择偏差")
    text = text.replace("是回应碳因子不确定性的核心分析", "用于量化碳因子不确定性对结论的影响")
    text = text.replace("This is the main code-level evidence for whether the 77% rejection rate introduces systematic sampling bias.", "It quantifies how feasibility screening changes parameter-space coverage and potential selection bias.")
    text = text.replace("This is the core analysis addressing uncertainty in emission factors.", "It quantifies how emission-factor uncertainty affects the main EUI-OCEI conclusions.")
    return text


def rewrite_intro(src: str) -> str:
    if INTRO_START not in src:
        return src
    lines = src.splitlines()
    title = next((ln.strip() for ln in lines if ln.strip().startswith("### ")), "### Cell — Notebook step / Notebook step")
    zh = clean_text(extract_field(src, "中文说明") or "本 cell 执行当前 notebook 工作流中的一个可复现计算步骤。")
    en = clean_text(extract_field(src, "English explanation") or "This cell performs one reproducible computational step in the notebook workflow.")

    title_lower = title.lower()
    if any(key in title_lower for key in ["环境", "environment"]):
        zh_in = "依赖本地 Python/Jupyter 环境、项目根目录和后续单元需要共享的配置参数。"
        zh_out = "建立路径、随机种子、绘图样式、配置字典或输出目录等基础对象。"
        en_in = "Depends on the local Python/Jupyter environment, the project root, and shared configuration values used by later cells."
        en_out = "Creates paths, random seeds, plotting defaults, configuration dictionaries, or output directories."
    elif any(key in title_lower for key in ["加载", "data loading", "读取"]):
        zh_in = "读取上游步骤生成的 CSV、模型清单或配置对象，并检查必要字段是否存在。"
        zh_out = "生成清洗后的 DataFrame、特征列表、训练测试划分或供后续单元复用的中间变量。"
        en_in = "Reads CSV files, model lists, or configuration objects produced by previous steps and validates required fields."
        en_out = "Creates cleaned DataFrames, feature lists, train/test splits, or intermediate objects reused downstream."
    elif any(key in title_lower for key in ["图", "plot", "figure", "visual", "示意"]):
        zh_in = "读取当前工作流已经生成的数据表或内存对象，并使用统一的绘图样式。"
        zh_out = "导出论文或复核用图像文件，并在必要时同步导出支撑图表的数据表。"
        en_in = "Uses data tables or in-memory objects already produced in the workflow with a consistent plotting style."
        en_out = "Exports manuscript or audit figures and, when needed, the source tables behind the figure."
    elif any(key in title_lower for key in ["模型", "model", "training", "cross-validation"]):
        zh_in = "依赖上游特征矩阵、目标变量、候选模型或交叉验证设置。"
        zh_out = "输出拟合模型、评价指标、交叉验证结果、预测值或模型参数表。"
        en_in = "Depends on upstream feature matrices, target values, candidate models, or cross-validation settings."
        en_out = "Produces fitted models, evaluation metrics, cross-validation results, predictions, or parameter tables."
    else:
        zh_in = "依赖前序 cell 已经建立的配置、数据对象或函数，请按 notebook 顺序运行。"
        zh_out = "生成后续分析所需的中间对象、诊断表、图件或本地输出文件。"
        en_in = "Depends on configuration, data objects, or functions defined by previous cells; run the notebook sequentially."
        en_out = "Produces intermediate objects, diagnostic tables, figures, or local output files required downstream."

    return f"""{INTRO_START}
{title}

**中文说明**：{zh}

**输入与依赖**：{zh_in}

**主要输出**：{zh_out}

**复现提示**：运行前确认上游输出路径存在；若当前单元生成图件，需同时检查 PNG 预览和 SVG/PDF 矢量文件的文字完整性、标签间距和图例位置。

**English explanation**: {en}

**Inputs and dependencies**: {en_in}

**Main outputs**: {en_out}

**Reproducibility note**: Confirm upstream output paths before running. For figure-producing cells, inspect both PNG previews and SVG/PDF vector exports for complete text, label spacing, and legend placement.
{INTRO_END}
"""


def neutralize_review_language(src: str) -> str:
    replacements = {
        "**针对审稿人关于77%剔除率可能引入选择偏差的回应：**": "**可行性筛选的研究依据与偏差诊断：**",
        "**针对审稿人关于模型描述不足以复现的回应（P1-5）：**": "**EnergyPlus 原型模型可复现性说明：**",
        "**窗户构造类型定义（审稿人要求补充）：**": "**窗户构造类型定义：**",
        "# [IMPROVEMENT P0-1] Real-Building EUI Benchmark Comparison": "# Real-building EUI benchmark comparison",
        "# [IMPROVEMENT P0-2] Feasibility Screening Distribution Analysis": "# Feasibility-screening distribution analysis",
        "# [IMPROVEMENT P0-3] Carbon Emission Factor Sensitivity Analysis": "# Carbon emission-factor sensitivity analysis",
        "# [IMPROVEMENT P0-4 & P1-7] SHAP-Based Sensitivity Analysis": "# SHAP-based sensitivity analysis",
        "# [IMPROVEMENT P1-6] Hyperparameter Tuning Report": "# Hyperparameter tuning report",
        "# [IMPROVEMENT P1-7] Variable Selection Cutoff Analysis": "# Variable-selection cutoff analysis",
        "# [IMPROVEMENT P1-8] Impact of Fixing Non-Core Variables": "# Impact of fixing non-core variables",
    }
    for old, new in replacements.items():
        src = src.replace(old, new)
    src = src.replace("Reviewers", "Readers")
    return src


def insert_nb01_schematic_cell(nb) -> None:
    if any("generate_hotel_engineering_schematic" in "".join(c.get("source", "")) for c in nb.cells if c.cell_type == "code"):
        return
    insert_at = 10
    nb.cells.insert(insert_at, nbformat.v4.new_markdown_cell(NEW_NB01_MD))
    nb.cells.insert(insert_at + 1, nbformat.v4.new_code_cell(NEW_NB01_CODE))


def improve_nb04_sensitivity_plot(nb) -> None:
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        src = cell.source
        if "emission_factor_sensitivity.png" not in src or "scenario_df = pd.DataFrame(scenario_results)" not in src:
            continue

        new_block = """scenario_df = pd.DataFrame(scenario_results)

scenario_labels = {
    'Baseline': '基准情景',
    'Electricity Low 0.40': '电力低因子\\\\n0.40 kgCO2e/kWh',
    'Electricity High 0.70': '电力高因子\\\\n0.70 kgCO2e/kWh',
    'Grid Decarbonisation 2030 0.40': '2030 电网脱碳\\\\n0.40 kgCO2e/kWh',
    'Grid Decarbonisation 2050 0.25': '2050 电网脱碳\\\\n0.25 kgCO2e/kWh',
    'High District Thermal Factors': '区域冷热高因子',
}
plot_labels = scenario_df['scenario'].map(scenario_labels).fillna(scenario_df['scenario'])

fig, axes = plt.subplots(1, 2, figsize=(17.2, 6.4), dpi=150, constrained_layout=True)

ax = axes[0]
baseline_mean = scenario_df.loc[scenario_df['scenario'] == 'Baseline', 'mean_ocei'].values[0]
colors = ['#4C78A8' if s == 'Baseline' else '#F58518' if 'Low' in s or '2030' in s or '2050' in s
          else '#B64646' if 'High' in s else '#6B7280' for s in scenario_df['scenario']]
bars = ax.barh(plot_labels, scenario_df['mean_ocei'], color=colors, edgecolor='white', linewidth=0.8)
ax.axvline(baseline_mean, color='#6B7280', linestyle='--', linewidth=1.1, alpha=0.85)
ax.set_xlabel('平均 OCEI（kgCO2e/(m2·a)）')
ax.set_title('不同排放因子情景下的平均 OCEI', pad=10)
ax.set_xlim(0, max(scenario_df['mean_ocei']) * 1.12)
for bar, val in zip(bars, scenario_df['mean_ocei']):
    ax.text(bar.get_width() + max(scenario_df['mean_ocei']) * 0.012,
            bar.get_y() + bar.get_height()/2,
            f'{val:.1f}', va='center', fontsize=9)
ax.grid(axis='x', alpha=0.22, linewidth=0.8)
ax.set_axisbelow(True)

ax = axes[1]
x = np.arange(len(scenario_df))
width = 0.34
r_bars = ax.bar(x - width/2, scenario_df['eui_ocei_pearson_r'], width,
                label='EUI-OCEI Pearson r', color='#4C78A8', edgecolor='white', linewidth=0.8)
ax.set_ylabel('Pearson r', color='#4C78A8')
ax.tick_params(axis='y', labelcolor='#4C78A8')
ax.set_ylim(0, 1.05)
ax.grid(axis='y', alpha=0.18, linewidth=0.8)
ax.set_axisbelow(True)

ax2 = ax.twinx()
o_bars = ax2.bar(x + width/2, scenario_df['top10_overlap_with_baseline'] * 100, width,
                 label='Top-10% 重叠率（%）', color='#F58518', edgecolor='white', linewidth=0.8)
ax2.set_ylabel('Top-10% 重叠率（%）', color='#F58518')
ax2.tick_params(axis='y', labelcolor='#F58518')
ax2.set_ylim(0, 105)

ax.set_xticks(x)
ax.set_xticklabels(plot_labels, rotation=0, ha='center', fontsize=8)
ax.set_title('EUI-OCEI 耦合指标稳定性', pad=10)
handles = [r_bars, o_bars]
labels = [h.get_label() for h in handles]
fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.75, 1.04),
           ncol=2, frameon=False, fontsize=9)

fig.savefig(FIG_DIR / 'emission_factor_sensitivity.png', dpi=300, bbox_inches='tight')
fig.savefig(FIG_DIR / 'emission_factor_sensitivity.svg', bbox_inches='tight')
fig.savefig(FIG_DIR / 'emission_factor_sensitivity.pdf', bbox_inches='tight')
plt.show()

scenario_df.to_csv(OUT_DIR / 'emission_factor_sensitivity.csv', index=False, encoding='utf-8-sig')"""
        src = re.sub(
            r"scenario_df = pd\.DataFrame\(scenario_results\).*?scenario_df\.to_csv\(OUT_DIR / 'emission_factor_sensitivity\.csv', index=False, encoding='utf-8-sig'\)",
            new_block,
            src,
            flags=re.S,
        )
        cell.source = src
        return


def update_notebook(path: Path) -> None:
    nb = nbformat.read(path, as_version=4)
    if path.name.startswith("01_"):
        insert_nb01_schematic_cell(nb)
    if path.name.startswith("04_"):
        improve_nb04_sensitivity_plot(nb)

    for cell in nb.cells:
        if cell.cell_type == "markdown":
            cell.source = neutralize_review_language(rewrite_intro(cell.source))
        elif cell.cell_type == "code":
            cell.source = neutralize_review_language(cell.source)

    nbformat.write(nb, path)


def main() -> None:
    for path in sorted(ROOT.glob("0[1-4]_*.ipynb")):
        update_notebook(path)
        print(f"updated {path.name}")


if __name__ == "__main__":
    main()
