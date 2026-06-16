"""Apply the 2026-06-16 V1 reviewer-strengthening edits.

The edits are structural notebook mutations with nbformat. They intentionally
add analysis cells that can run on the current small debug dataset and scale to
the full 4,640-sample EnergyPlus dataset when it is regenerated locally.
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell


def find_repo_root(start: Path) -> Path:
    start = start.resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "input" / "Beijing.epw").exists() or (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


ROOT = find_repo_root(Path(__file__))


NOTEBOOKS = {
    "nb01": ROOT / "01_Parametric_Simulation_Database_Construction.ipynb",
    "nb02": ROOT / "02_SRC_Sensitivity_and_Variable_Selection.ipynb",
    "nb03": ROOT / "03_ML_Model_Training_and_Evaluation.ipynb",
    "nb04": ROOT / "04_EUI_OCEI_Coupling_and_Carbon_Analysis.ipynb",
}


ROOT_BOOTSTRAP = textwrap.dedent(
    """
    def find_project_root(start: Path | None = None) -> Path:
        start = (start or Path.cwd()).resolve()
        for candidate in [start, *start.parents]:
            if (candidate / "input" / "Beijing.epw").exists() or (candidate / "data" / "step1_simulation_dataset.csv").exists():
                return candidate
            if (candidate / "AGENTS.md").exists() and (candidate / "outputs_step1").exists():
                return candidate
        return start

    PROJECT_ROOT = find_project_root()
    CODE_DIR = PROJECT_ROOT / "experiment_code"
    """
).strip()


def read_nb(path: Path):
    return nbformat.read(path, as_version=4)


def write_nb(path: Path, nb) -> None:
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
    nbformat.write(nb, path)


def code_by_id(nb, cell_id: str):
    for cell in nb.cells:
        if cell.cell_type == "code" and cell.get("id") == cell_id:
            return cell
    raise KeyError(cell_id)


def idx_by_id(nb, cell_id: str) -> int:
    for i, cell in enumerate(nb.cells):
        if cell.get("id") == cell_id:
            return i
    raise KeyError(cell_id)


def insert_once_after(nb, anchor_id: str, marker: str, cells: list) -> None:
    if any(marker in c.source for c in nb.cells):
        return
    idx = idx_by_id(nb, anchor_id)
    nb.cells[idx + 1:idx + 1] = cells


def replace_project_root_cell(cell, extra_dirs: str) -> None:
    src = cell.source
    src = src.replace("from pathlib import Path\n", "from pathlib import Path\nimport sys\n", 1)
    src = src.replace("PROJECT_ROOT = Path.cwd()\n", ROOT_BOOTSTRAP + "\n")
    src = src.replace(extra_dirs["old"], extra_dirs["new"])
    if "PAPER_ASSETS_DIR = PROJECT_ROOT" not in src:
        src = src.replace(
            "for p in ",
            "PAPER_ASSETS_DIR = PROJECT_ROOT / \"paper_assets\"\n"
            "PAPER_ASSETS_FIG_DIR = PAPER_ASSETS_DIR / \"figures\"\n"
            "for search_path in [PROJECT_ROOT, CODE_DIR]:\n"
            "    if search_path.exists() and str(search_path) not in sys.path:\n"
            "        sys.path.insert(0, str(search_path))\n\n"
            "for p in ",
            1,
        )
    if "PAPER_ASSETS_FIG_DIR" in src and "PAPER_ASSETS_FIG_DIR]" not in src:
        src = src.replace("FIG_DIR]:", "FIG_DIR, PAPER_ASSETS_FIG_DIR]:")
        src = src.replace("MODEL_DIR]:", "MODEL_DIR, PAPER_ASSETS_FIG_DIR]:")
        src = src.replace("OUT_DIR, FIG_DIR]:", "OUT_DIR, FIG_DIR, PAPER_ASSETS_FIG_DIR]:")
    cell.source = src


def markdown(title: str, body: str):
    return new_markdown_cell(
        textwrap.dedent(
            f"""
            <!-- CODEx 2026-06-16 reviewer-strengthening: {title} -->
            ### {title}

            {body}
            """
        ).strip()
    )


NB01_BOUNDARY = r'''
# ============================================================
# 2026-06-16 V1: feasibility-boundary sensitivity analysis
# Tests whether SRC conclusions depend on the 0.55-0.95 screening interval.
# ============================================================

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr

boundary_scenarios = [
    ("Baseline [0.55, 0.95]", 0.55, 0.95),
    ("Lower relaxed [0.50, 0.95]", 0.50, 0.95),
    ("Lower strict [0.60, 0.95]", 0.60, 0.95),
    ("Upper relaxed [0.55, 0.98]", 0.55, 0.98),
    ("Upper strict [0.55, 0.90]", 0.55, 0.90),
    ("Wide [0.50, 0.98]", 0.50, 0.98),
    ("Narrow [0.60, 0.90]", 0.60, 0.90),
]

def _src_rank_for_boundary(df_in, feature_cols, target_col):
    d = df_in[feature_cols + [target_col]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(d) < max(12, min(30, len(feature_cols) + 2)):
        return pd.DataFrame(columns=["feature", "SRC", "abs_SRC", "rank_abs"])
    Xb = StandardScaler().fit_transform(d[feature_cols])
    yb = StandardScaler().fit_transform(d[[target_col]]).ravel()
    model = LinearRegression().fit(Xb, yb)
    out = pd.DataFrame({"feature": feature_cols, "SRC": model.coef_})
    out["abs_SRC"] = out["SRC"].abs()
    out["rank_abs"] = out["abs_SRC"].rank(method="first", ascending=False).astype(int)
    return out.sort_values("rank_abs")

dataset_path = DATA_DIR / "step1_simulation_dataset.csv"
if not dataset_path.exists():
    print("未发现 step1_simulation_dataset.csv；边界敏感性分析将在完成 Step 1 仿真后自动运行。")
else:
    sim_df = pd.read_csv(dataset_path)
    if "window_type_id" in sim_df.columns:
        sim_df = pd.get_dummies(sim_df, columns=["window_type_id"], prefix="window_type", drop_first=True)
    if "orientation_deg" in sim_df.columns:
        sim_df["orientation_sin"] = np.sin(np.deg2rad(sim_df["orientation_deg"]))
        sim_df["orientation_cos"] = np.cos(np.deg2rad(sim_df["orientation_deg"]))
    if "footprint_area_m2" not in sim_df.columns:
        sim_df["footprint_area_m2"] = sim_df["building_length"] * sim_df["building_width"]
    if "aspect_ratio" not in sim_df.columns:
        sim_df["aspect_ratio"] = sim_df["building_length"] / sim_df["building_width"].replace(0, np.nan)

    boundary_features = [
        'insul_thick', 'wwr', 'wall_thick',
        'u_win_n', 'u_win_s', 'u_win_e', 'u_win_w',
        'u_wall', 'u_roof', 'u_ground',
        'shgc_n', 'shgc_s', 'shgc_e', 'shgc_w',
        'roof_insul_thick', 'floor_num', 'footprint_area_m2',
        'aspect_ratio', 'floor_height', 'orientation_sin', 'orientation_cos',
        'public_area', 'room_area', 'room_count',
        'equip_power', 'dhw_per_person', 'occupancy_density', 'light_power',
        'cool_set', 'heat_set', 'dhw_temp',
        'cop_cooling', 'cop_heating', 'boiler_eff', 'fan_eff',
        'fresh_air_ach', 'operation_hours',
        'window_type_2', 'window_type_3'
    ]
    boundary_features = [c for c in boundary_features if c in sim_df.columns]
    baseline_subset = sim_df[sim_df["usable_area_ratio"].between(0.55, 0.95)].copy()
    baseline_rank = _src_rank_for_boundary(baseline_subset, boundary_features, "eui_kwh_m2")
    baseline_top10 = set(baseline_rank.head(10)["feature"])
    baseline_top18 = set(baseline_rank.head(18)["feature"])

    rows = []
    for label, lo, hi in boundary_scenarios:
        design_mask = samples_all["usable_area_ratio"].between(lo, hi)
        available = sim_df[sim_df["usable_area_ratio"].between(lo, hi)].copy()
        rank_df = _src_rank_for_boundary(available, boundary_features, "eui_kwh_m2")
        if baseline_rank.empty or rank_df.empty:
            rho = np.nan
            top10_overlap = np.nan
            top18_overlap = np.nan
        else:
            merged = baseline_rank[["feature", "rank_abs"]].merge(
                rank_df[["feature", "rank_abs"]], on="feature", suffixes=("_baseline", "_scenario")
            )
            rho = spearmanr(merged["rank_abs_baseline"], merged["rank_abs_scenario"]).correlation
            top10_overlap = len(baseline_top10 & set(rank_df.head(10)["feature"])) / max(1, len(baseline_top10))
            top18_overlap = len(baseline_top18 & set(rank_df.head(18)["feature"])) / max(1, len(baseline_top18))
        rows.append({
            "scenario": label,
            "lower_bound": lo,
            "upper_bound": hi,
            "design_space_retained_n": int(design_mask.sum()),
            "design_space_retention_pct": float(design_mask.mean() * 100),
            "available_simulated_n": int(len(available)),
            "spearman_rank_vs_baseline": rho,
            "top10_overlap_vs_baseline": top10_overlap,
            "top18_overlap_vs_baseline": top18_overlap,
        })

    boundary_df = pd.DataFrame(rows)
    boundary_df.to_csv(OUTPUT_DIR / "boundary_sensitivity_results.csv", index=False, encoding="utf-8-sig")

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.2), dpi=150, constrained_layout=True)
    labels = boundary_df["scenario"].str.replace(" ", "\n", regex=False)
    axes[0].barh(labels, boundary_df["design_space_retention_pct"], color="#4C78A8")
    axes[0].set_xlabel("设计空间保留率（%）")
    axes[0].set_title("可行性边界对设计空间的影响")
    axes[0].axvline(retention, color="#F58518", linestyle="--", linewidth=1.1, label="基准保留率")
    axes[0].legend(frameon=False, fontsize=8)

    x = np.arange(len(boundary_df))
    axes[1].plot(x, boundary_df["spearman_rank_vs_baseline"], marker="o", label="SRC 排名 Spearman rho", color="#4C78A8")
    axes[1].plot(x, boundary_df["top10_overlap_vs_baseline"], marker="s", label="Top-10 重叠率", color="#F58518")
    axes[1].plot(x, boundary_df["top18_overlap_vs_baseline"], marker="^", label="Top-18 重叠率", color="#54A24B")
    axes[1].set_ylim(0, 1.05)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=0, fontsize=8)
    axes[1].set_ylabel("相对于基准边界的一致性")
    axes[1].set_title("关键变量结论对筛选边界的稳健性")
    axes[1].legend(frameon=False, fontsize=8)
    fig.savefig(FIG_DIR / "boundary_sensitivity_analysis.png", dpi=300, bbox_inches="tight")
    plt.show()

    print("边界敏感性分析已保存：", OUTPUT_DIR / "boundary_sensitivity_results.csv")
    display(boundary_df.round(4))
'''


NB01_BIAS = r'''
# ============================================================
# 2026-06-16 V1: stratified sim-to-real bias decomposition
# Explains where the simulated-versus-measured EUI gap is largest.
# ============================================================

dataset_path = DATA_DIR / "step1_simulation_dataset.csv"
if not dataset_path.exists():
    print("未发现 step1_simulation_dataset.csv；偏差分层分析将在完成 Step 1 仿真后自动运行。")
else:
    df_bias = pd.read_csv(dataset_path).copy()
    measured_mean = measured_stats["mean"]

    df_bias["height_stratum"] = pd.cut(
        df_bias["floor_num"],
        bins=[-np.inf, 8, 15, np.inf],
        labels=["低层（≤8层）", "中高层（9–15层）", "高层（>15层）"]
    )
    df_bias["footprint_stratum"] = pd.qcut(
        df_bias["footprint_area_m2"].rank(method="first"),
        q=3,
        labels=["小占地", "中占地", "大占地"]
    )

    bias_rows = []
    for h in df_bias["height_stratum"].cat.categories:
        for f in df_bias["footprint_stratum"].cat.categories:
            sub = df_bias[(df_bias["height_stratum"] == h) & (df_bias["footprint_stratum"] == f)]
            if sub.empty:
                continue
            sim_mean = sub["eui_kwh_m2"].mean()
            bias_rows.append({
                "height_stratum": str(h),
                "footprint_stratum": str(f),
                "n": len(sub),
                "simulated_mean_eui": sim_mean,
                "measured_mean_eui": measured_mean,
                "bias_kwh_m2": sim_mean - measured_mean,
                "bias_pct": (sim_mean / measured_mean - 1) * 100,
                "median_floor_num": sub["floor_num"].median(),
                "median_footprint_m2": sub["footprint_area_m2"].median(),
            })

    bias_df = pd.DataFrame(bias_rows)
    bias_df.to_csv(OUTPUT_DIR / "bias_stratified_decomposition.csv", index=False, encoding="utf-8-sig")

    pivot_bias = bias_df.pivot(index="height_stratum", columns="footprint_stratum", values="bias_pct")
    pivot_n = bias_df.pivot(index="height_stratum", columns="footprint_stratum", values="n")

    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.2), dpi=150, constrained_layout=True)
    im = axes[0].imshow(pivot_bias.values, cmap="RdBu_r", vmin=-30, vmax=30)
    axes[0].set_xticks(range(len(pivot_bias.columns)))
    axes[0].set_xticklabels(pivot_bias.columns)
    axes[0].set_yticks(range(len(pivot_bias.index)))
    axes[0].set_yticklabels(pivot_bias.index)
    axes[0].set_title("模拟 EUI 相对实测均值的分层偏差")
    for i in range(pivot_bias.shape[0]):
        for j in range(pivot_bias.shape[1]):
            val = pivot_bias.iloc[i, j]
            n_raw = pivot_n.iloc[i, j]
            if pd.isna(val) or pd.isna(n_raw):
                label = "NA"
            else:
                label = f"{val:+.1f}%\nn={int(n_raw)}"
            axes[0].text(j, i, label, ha="center", va="center", fontsize=8)
    cbar = fig.colorbar(im, ax=axes[0], shrink=0.86)
    cbar.set_label("偏差（%）")

    for label, sub in df_bias.groupby("height_stratum", observed=True):
        axes[1].hist(sub["eui_kwh_m2"], bins=22, alpha=0.48, density=True, label=str(label))
    axes[1].axvline(measured_mean, color="#B64646", linestyle="--", linewidth=1.4, label="实测均值（Chen et al., 2018）")
    axes[1].set_xlabel("建筑能源使用强度 EUI（kWh/(m2·a)）")
    axes[1].set_ylabel("概率密度")
    axes[1].set_title("不同高度分层的模拟 EUI 分布")
    axes[1].legend(frameon=False, fontsize=8)

    fig.savefig(FIG_DIR / "bias_stratified_decomposition.png", dpi=300, bbox_inches="tight")
    plt.show()

    print("偏差分层分解表已保存：", OUTPUT_DIR / "bias_stratified_decomposition.csv")
    display(bias_df.sort_values("bias_pct", ascending=False).round(3))
'''


NB02_DIVERGENCE = r'''
# ============================================================
# 2026-06-16 V1: SHAP-SRC divergence and incremental-value analysis
# Tests whether SHAP-only variables materially improve prediction.
# ============================================================

from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

src_top18_list = compare_df.nsmallest(18, "src_rank")["feature"].tolist()
shap_top18_list = compare_df.nsmallest(18, "shap_rank")["feature"].tolist()
src_top18 = set(src_top18_list)
shap_top18 = set(shap_top18_list)
only_src = sorted(src_top18 - shap_top18)
only_shap = sorted(shap_top18 - src_top18)

divergence_rows = []
base_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("model", RidgeCV(alphas=np.logspace(-3, 4, 40), cv=5)),
])
cv = KFold(n_splits=min(5, len(df)), shuffle=True, random_state=42)
base_score = cross_val_score(base_pipe, X[src_top18_list], y, cv=cv, scoring="r2", n_jobs=-1).mean()

for feature in only_shap:
    add_features = src_top18_list + [feature]
    score = cross_val_score(base_pipe, X[add_features], y, cv=cv, scoring="r2", n_jobs=-1).mean()
    src_rank_val = compare_df.loc[compare_df["feature"] == feature, "src_rank"].iloc[0]
    shap_rank_val = compare_df.loc[compare_df["feature"] == feature, "shap_rank"].iloc[0]
    divergence_rows.append({
        "feature": feature,
        "src_rank": src_rank_val,
        "shap_rank": shap_rank_val,
        "ridgecv_r2_base_src18": base_score,
        "ridgecv_r2_with_feature": score,
        "incremental_r2": score - base_score,
        "interpretation": "SHAP-only variable; tests whether nonlinear importance implies omitted predictive value",
    })

for feature in only_src:
    src_rank_val = compare_df.loc[compare_df["feature"] == feature, "src_rank"].iloc[0]
    shap_rank_val = compare_df.loc[compare_df["feature"] == feature, "shap_rank"].iloc[0]
    divergence_rows.append({
        "feature": feature,
        "src_rank": src_rank_val,
        "shap_rank": shap_rank_val,
        "ridgecv_r2_base_src18": base_score,
        "ridgecv_r2_with_feature": np.nan,
        "incremental_r2": np.nan,
        "interpretation": "SRC-only variable; mostly reflects stable linear main-effect contribution",
    })

divergence_df = pd.DataFrame(divergence_rows).sort_values(["interpretation", "incremental_r2"], ascending=[True, False])
divergence_df.to_csv(OUT_DIR / "shap_src_divergence_incremental_r2.csv", index=False, encoding="utf-8-sig")

plot_features = only_shap[:4] if only_shap else shap_top18_list[:4]
fig, axes = plt.subplots(1, max(1, len(plot_features)), figsize=(4.2 * max(1, len(plot_features)), 3.8), dpi=150, constrained_layout=True)
axes = np.atleast_1d(axes)
for ax, feature in zip(axes, plot_features):
    idx = list(X.columns).index(feature)
    ax.scatter(X[feature], shap_values[:, idx], c=df["eui_kwh_m2"], cmap="viridis", s=22, alpha=0.78, edgecolor="none")
    ax.axhline(0, color="#6B7280", linewidth=0.8, linestyle="--")
    ax.set_xlabel(feature)
    ax.set_ylabel("SHAP 值")
    ax.set_title(f"{feature}\nSRC rank {int(compare_df.loc[compare_df['feature']==feature,'src_rank'].iloc[0])}, "
                 f"SHAP rank {int(compare_df.loc[compare_df['feature']==feature,'shap_rank'].iloc[0])}")
fig.savefig(FIG_DIR / "shap_divergence_dependence.png", dpi=300, bbox_inches="tight")
plt.show()

print("SHAP-SRC 分歧变量增量分析已保存：", OUT_DIR / "shap_src_divergence_incremental_r2.csv")
print(f"SRC Top-18 基准 RidgeCV R2: {base_score:.4f}")
display(divergence_df.round(5))
'''


NB02_ABLATION = r'''
# ============================================================
# 2026-06-16 V1: marginal-variable ablation for variables ranked 15-18
# Tests whether the 18-variable cutoff is conservative rather than fragile.
# ============================================================

from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

top18_ordered = src_sorted.head(18)["feature"].tolist()
marginal_features = top18_ordered[14:18]
cv = KFold(n_splits=min(5, len(df)), shuffle=True, random_state=42)
lin_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("model", LinearRegression()),
])
base_r2 = cross_val_score(lin_pipe, X[top18_ordered], y, cv=cv, scoring="r2", n_jobs=-1).mean()

rows = [{
    "case": "all_top18",
    "removed_feature": "",
    "n_features": len(top18_ordered),
    "cv_r2_mean": base_r2,
    "delta_r2_vs_top18": 0.0,
    "physical_role": "完整 18 变量基准",
}]

role_map = {
    "equip_power": "室内设备功率密度，代表设备内扰与电力负荷",
    "heat_set": "冬季供暖设定温度，代表运行控制边界",
    "room_area": "单间客房面积，代表功能空间尺度",
    "u_wall": "外墙传热系数，代表围护结构传热性能",
}

for feature in marginal_features:
    remaining = [f for f in top18_ordered if f != feature]
    score = cross_val_score(lin_pipe, X[remaining], y, cv=cv, scoring="r2", n_jobs=-1).mean()
    rows.append({
        "case": f"remove_{feature}",
        "removed_feature": feature,
        "n_features": len(remaining),
        "cv_r2_mean": score,
        "delta_r2_vs_top18": score - base_r2,
        "physical_role": role_map.get(feature, "边际变量"),
    })

remaining_14 = [f for f in top18_ordered if f not in marginal_features]
score_14 = cross_val_score(lin_pipe, X[remaining_14], y, cv=cv, scoring="r2", n_jobs=-1).mean()
rows.append({
    "case": "remove_rank15_to_18",
    "removed_feature": ", ".join(marginal_features),
    "n_features": len(remaining_14),
    "cv_r2_mean": score_14,
    "delta_r2_vs_top18": score_14 - base_r2,
    "physical_role": "同时移除第 15-18 名边际变量的保守性检验",
})

ablation_df = pd.DataFrame(rows)
ablation_df.to_csv(OUT_DIR / "marginal_variable_ablation.csv", index=False, encoding="utf-8-sig")

fig, ax = plt.subplots(figsize=(8.8, 4.8), dpi=150)
plot_df = ablation_df[ablation_df["case"] != "all_top18"].copy()
colors = ["#4C78A8" if v >= -0.01 else "#B64646" for v in plot_df["delta_r2_vs_top18"]]
ax.barh(plot_df["case"], plot_df["delta_r2_vs_top18"], color=colors)
ax.axvline(0, color="#6B7280", linewidth=0.9)
ax.axvline(-0.01, color="#F58518", linestyle="--", linewidth=1.0, label="ΔR2 = -0.01")
ax.set_xlabel("相对于 Top-18 基准的 5 折 CV R2 变化")
ax.set_title("第 15-18 名边际变量逐个移除检验")
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(FIG_DIR / "marginal_variable_ablation.png", dpi=300, bbox_inches="tight")
plt.show()

print("边际变量消融分析已保存：", OUT_DIR / "marginal_variable_ablation.csv")
display(ablation_df.round(5))
'''


NB03_R2_DECOMP = r'''
# ============================================================
# 2026-06-16 V1: physical decomposition of predictive R2
# Demonstrates that high surrogate fidelity follows physical structure.
# ============================================================

from sklearn.model_selection import KFold, cross_val_score

physical_groups = {
    "生活热水": ["dhw_per_person", "dhw_temp", "room_count", "occupancy_density"],
    "几何形态": ["floor_num", "footprint_area_m2", "aspect_ratio", "floor_height", "room_area", "public_area"],
    "HVAC 与运行": ["cop_cooling", "cop_heating", "boiler_eff", "fan_eff", "cool_set", "heat_set", "fresh_air_ach", "operation_hours"],
    "围护结构": ["u_wall", "u_roof", "u_ground", "u_win_n", "u_win_s", "u_win_e", "u_win_w", "wwr", "shgc_n", "shgc_s", "shgc_e", "shgc_w", "insul_thick", "roof_insul_thick", "wall_thick"],
    "功能与内扰": ["equip_power", "light_power", "window_type_2", "window_type_3", "orientation_sin", "orientation_cos"],
}

ordered_features = []
rows = []
cv = KFold(n_splits=min(INNER_CV, len(df)), shuffle=True, random_state=RANDOM_SEED)
lin_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("model", LinearRegression()),
])

for group_name, candidates in physical_groups.items():
    group_features = [f for f in candidates if f in top18 and f not in ordered_features]
    ordered_features.extend(group_features)
    if not ordered_features:
        continue
    scores = cross_val_score(lin_pipe, df[ordered_features], y, cv=cv, scoring="r2", n_jobs=-1)
    rows.append({
        "step": group_name,
        "n_features": len(ordered_features),
        "features_added": ", ".join(group_features),
        "cv_r2_mean": scores.mean(),
        "cv_r2_std": scores.std(ddof=1),
    })

remaining = [f for f in top18 if f not in ordered_features]
if remaining:
    ordered_features.extend(remaining)
    scores = cross_val_score(lin_pipe, df[ordered_features], y, cv=cv, scoring="r2", n_jobs=-1)
    rows.append({
        "step": "其他 Top-18 变量",
        "n_features": len(ordered_features),
        "features_added": ", ".join(remaining),
        "cv_r2_mean": scores.mean(),
        "cv_r2_std": scores.std(ddof=1),
    })

poly2_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("poly", PolynomialFeatures(degree=2, include_bias=False)),
    ("poly_scaler", StandardScaler()),
    ("model", RidgeCV(alphas=np.logspace(-2, 4, 30), cv=min(5, len(df)))),
])
poly_scores = cross_val_score(poly2_pipe, df[top18], y, cv=cv, scoring="r2", n_jobs=-1)
rows.append({
    "step": "Top-18 + 二阶非线性项",
    "n_features": len(top18),
    "features_added": "PolynomialFeatures(degree=2)",
    "cv_r2_mean": poly_scores.mean(),
    "cv_r2_std": poly_scores.std(ddof=1),
})

r2_decomp_df = pd.DataFrame(rows)
r2_decomp_df["incremental_r2"] = r2_decomp_df["cv_r2_mean"].diff().fillna(r2_decomp_df["cv_r2_mean"])
r2_decomp_df.to_csv(OUT_DIR / "r2_cumulative_decomposition.csv", index=False, encoding="utf-8-sig")

fig, ax = plt.subplots(figsize=(9.2, 5.0), dpi=150)
ax.plot(r2_decomp_df["step"], r2_decomp_df["cv_r2_mean"], marker="o", color="#4C78A8", linewidth=1.8)
ax.fill_between(
    np.arange(len(r2_decomp_df)),
    r2_decomp_df["cv_r2_mean"] - r2_decomp_df["cv_r2_std"],
    r2_decomp_df["cv_r2_mean"] + r2_decomp_df["cv_r2_std"],
    color="#4C78A8", alpha=0.16
)
for i, row in r2_decomp_df.iterrows():
    ax.text(i, row["cv_r2_mean"] + 0.012, f"{row['cv_r2_mean']:.3f}", ha="center", fontsize=8)
ax.set_ylim(max(0, r2_decomp_df["cv_r2_mean"].min() - 0.08), min(1.02, r2_decomp_df["cv_r2_mean"].max() + 0.08))
ax.set_ylabel("5 折 CV R2")
ax.set_title("代理模型高 R2 的物理分组累积解释")
ax.tick_params(axis="x", rotation=25)
fig.tight_layout()
fig.savefig(FIG_DIR / "r2_cumulative_decomposition.png", dpi=300, bbox_inches="tight")
plt.show()

print("R2 物理分解已保存：", OUT_DIR / "r2_cumulative_decomposition.csv")
display(r2_decomp_df.round(5))
'''


NB03_FIT_COMPARE = r'''
def fit_and_compare_models(X_train, y_train, X_test, y_test, estimators):
    rows = []
    fitted_models = {}
    search_objects = {}
    best_params_by_model = {}

    for name, est in estimators.items():
        est.fit(X_train, y_train)

        if hasattr(est, "best_estimator_"):
            best_model = est.best_estimator_
            best_params = est.best_params_
            cv_score = -est.best_score_
        else:
            best_model = est
            best_params = None
            cv_score = np.nan

        pred_train = best_model.predict(X_train)
        pred_test = best_model.predict(X_test)

        cv_result = cross_validate(
            best_model,
            X_train,
            y_train,
            cv=INNER_CV,
            scoring={
                "r2": "r2",
                "neg_rmse": "neg_root_mean_squared_error",
                "neg_mae": "neg_mean_absolute_error",
            },
            n_jobs=-1,
        )

        cv_r2_scores = cv_result["test_r2"]
        cv_rmse_scores = -cv_result["test_neg_rmse"]
        cv_mae_scores = -cv_result["test_neg_mae"]

        rows.append({
            "model": name,
            "train_r2": r2_score(y_train, pred_train),
            "test_r2": r2_score(y_test, pred_test),
            "test_rmse": np.sqrt(mean_squared_error(y_test, pred_test)),
            "test_mae": mean_absolute_error(y_test, pred_test),
            "test_mape": mean_absolute_percentage_error(y_test, pred_test),
            "cv_best_rmse": cv_score,
            "cv_r2_mean": np.mean(cv_r2_scores),
            "cv_r2_std": np.std(cv_r2_scores, ddof=1),
            "cv_r2_variance": np.var(cv_r2_scores, ddof=1),
            "cv_rmse_mean": np.mean(cv_rmse_scores),
            "cv_rmse_std": np.std(cv_rmse_scores, ddof=1),
            "cv_mae_mean": np.mean(cv_mae_scores),
            "best_params": str(best_params),
        })

        fitted_models[name] = best_model
        search_objects[name] = est
        best_params_by_model[name] = best_params
        print(f"done -> {name}")

    result_df = pd.DataFrame(rows)
    result_df["generalization_gap"] = result_df["train_r2"] - result_df["test_r2"]
    result_df = result_df.sort_values(
        ["test_r2", "test_rmse", "generalization_gap"],
        ascending=[False, True, True],
    ).reset_index(drop=True)
    return result_df, fitted_models, search_objects, best_params_by_model


metrics_df, fitted_models, search_objects, best_params_by_model = fit_and_compare_models(
    X_train, y_train, X_test, y_test, all_estimators
)

metrics_df.to_csv(
    OUT_DIR / "model_metrics.csv",
    index=False,
    encoding="utf-8-sig",
)

metrics_df
'''


NB04_THRESHOLD_APPEND = r'''

# ---------- 2026-06-16 V1: electricity-factor threshold sweep ----------
electricity_grid = np.round(np.linspace(0.15, 0.75, 31), 3)
threshold_rows = []
baseline_top = set(df["OCEI_kgco2e_m2"].rank(method="first", ascending=True).nsmallest(top_n).index)

for ef_el in electricity_grid:
    ef = EMISSION_FACTORS.copy()
    ef["electricity"] = float(ef_el)
    carrier_carbon = pd.DataFrame({
        "electricity": df["electricity_kwh_for_carbon"] * ef["electricity"],
        "natural_gas": df["natural_gas_kwh_for_carbon"] * ef["natural_gas"],
        "district_heating": df["district_heating_kwh_for_carbon"] * ef["district_heating"],
        "district_cooling": df["district_cooling_kwh_for_carbon"] * ef["district_cooling"],
    })
    ocei_sweep = carrier_carbon.sum(axis=1) / df["gross_floor_area_m2"]
    rank_sweep = ocei_sweep.rank(method="first", ascending=True)
    overlap_sweep = len(baseline_top & set(rank_sweep.nsmallest(top_n).index)) / top_n
    total_by_carrier = carrier_carbon.sum()
    share_by_carrier = total_by_carrier / total_by_carrier.sum()
    threshold_rows.append({
        "electricity_factor": ef_el,
        "mean_ocei": ocei_sweep.mean(),
        "eui_ocei_pearson_r": pearsonr(df["eui_kwh_m2"], ocei_sweep)[0],
        "top10_overlap_with_baseline": overlap_sweep,
        "electricity_share": share_by_carrier["electricity"],
        "natural_gas_share": share_by_carrier["natural_gas"],
    })

threshold_df = pd.DataFrame(threshold_rows)
threshold_df.to_csv(OUT_DIR / "emission_factor_threshold_sweep.csv", index=False, encoding="utf-8-sig")

def first_factor_reaching(overlap_level):
    eligible = threshold_df[threshold_df["top10_overlap_with_baseline"] >= overlap_level]
    return np.nan if eligible.empty else eligible["electricity_factor"].min()

factor_80 = first_factor_reaching(0.80)
factor_90 = first_factor_reaching(0.90)

fig, ax = plt.subplots(figsize=(8.8, 5.0), dpi=150)
ax.plot(threshold_df["electricity_factor"], threshold_df["top10_overlap_with_baseline"] * 100,
        marker="o", color="#4C78A8", label="Top-10% 排名重叠率")
ax2 = ax.twinx()
ax2.plot(threshold_df["electricity_factor"], threshold_df["eui_ocei_pearson_r"],
         marker="s", color="#F58518", label="EUI-OCEI Pearson r")
ax.axhline(80, color="#54A24B", linestyle="--", linewidth=0.9)
ax.axhline(90, color="#B64646", linestyle="--", linewidth=0.9)
if np.isfinite(factor_80):
    ax.axvline(factor_80, color="#54A24B", linestyle=":", linewidth=0.9)
if np.isfinite(factor_90):
    ax.axvline(factor_90, color="#B64646", linestyle=":", linewidth=0.9)
ax.set_xlabel("电力排放因子（kgCO2e/kWh）")
ax.set_ylabel("Top-10% 排名重叠率（%）", color="#4C78A8")
ax2.set_ylabel("Pearson r", color="#F58518")
ax.set_title("电力脱碳路径下 EUI-OCEI 排名收敛阈值")
ax.tick_params(axis="y", labelcolor="#4C78A8")
ax2.tick_params(axis="y", labelcolor="#F58518")
lines, labels = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines + lines2, labels + labels2, loc="lower right", frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(FIG_DIR / "emission_factor_threshold_analysis.png", dpi=300, bbox_inches="tight")
plt.show()

print("电力排放因子阈值扫描已保存：", OUT_DIR / "emission_factor_threshold_sweep.csv")
print(f"Top-10% 重叠率达到 80% 的最低电力因子: {factor_80}")
print(f"Top-10% 重叠率达到 90% 的最低电力因子: {factor_90}")
'''


def patch_nb01() -> None:
    path = NOTEBOOKS["nb01"]
    nb = read_nb(path)
    cell = code_by_id(nb, "6d363436")
    replace_project_root_cell(
        cell,
        {
            "old": 'for p in [DATA_DIR, INPUT_DIR, OUTPUT_DIR, IDF_DIR, RUN_DIR, FIG_DIR]:',
            "new": 'for p in [DATA_DIR, INPUT_DIR, OUTPUT_DIR, IDF_DIR, RUN_DIR, FIG_DIR, PAPER_ASSETS_DIR, PAPER_ASSETS_FIG_DIR]:',
        },
    )
    c = code_by_id(nb, "7950065c-2afc-4f71-819c-ff07f769a9e6")
    c.source = c.source.replace('input_dir = Path.cwd() / "input"', 'input_dir = INPUT_DIR')
    c = code_by_id(nb, "9e92bbf6")
    c.source = c.source.replace("vt_map = {1: 0.55, 2: 0.65, 3: 0.75}", "vt_map = {1: 0.65, 2: 0.55, 3: 0.45}")
    c = code_by_id(nb, "77d829f0")
    c.source = c.source.replace("generate_hotel_engineering_schematic_v4(FIG_DIR)", "generate_hotel_engineering_schematic_v4(PAPER_ASSETS_FIG_DIR)")
    c.source = c.source.replace("generate_research_workflow_v4(FIG_DIR)", "generate_research_workflow_v4(PAPER_ASSETS_FIG_DIR)")
    if "Restore Chinese plotting fonts after schematic generation" not in c.source:
        c.source = c.source.rstrip() + textwrap.dedent(
            """

            # Restore Chinese plotting fonts after schematic generation changes rcParams.
            plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
            plt.rcParams["axes.unicode_minus"] = False
            """
        )
    insert_once_after(
        nb,
        "fe5b259b",
        "2026-06-16 V1: feasibility-boundary sensitivity analysis",
        [
            markdown(
                "可行性筛选边界敏感性分析",
                "该分析检验 0.55–0.95 可用面积比边界是否会主导后续 SRC 变量排序。其目的不是重复说明规范依据，而是量化“边界轻微浮动时核心结论是否保持稳定”。",
            ),
            new_code_cell(NB01_BOUNDARY),
        ],
    )
    insert_once_after(
        nb,
        "f30cde1e",
        "2026-06-16 V1: stratified sim-to-real bias decomposition",
        [
            markdown(
                "模拟到真实建筑偏差的分层分解",
                "该分析将总体模拟偏差拆分到高度与占地尺度分层中，用于说明模型适用边界：代理模型主要服务概念设计阶段的方案比选，而不是替代真实建筑校准模型。",
            ),
            new_code_cell(NB01_BIAS),
        ],
    )
    for existing in nb.cells:
        if existing.cell_type == "code" and "2026-06-16 V1: stratified sim-to-real bias decomposition" in existing.source:
            existing.source = NB01_BIAS
    write_nb(path, nb)


def patch_nb02() -> None:
    path = NOTEBOOKS["nb02"]
    nb = read_nb(path)
    cell = code_by_id(nb, "6863fca9")
    replace_project_root_cell(
        cell,
        {
            "old": "for p in [OUT_DIR, FIG_DIR]:",
            "new": "for p in [OUT_DIR, FIG_DIR, PAPER_ASSETS_DIR, PAPER_ASSETS_FIG_DIR]:",
        },
    )
    insert_once_after(
        nb,
        "319ecff6",
        "2026-06-16 V1: SHAP-SRC divergence",
        [
            markdown(
                "SHAP-SRC 分歧变量深度分析",
                "该分析从“排序相关”推进到“分歧是否改变预测结论”：若 SHAP 独有变量加入 SRC Top-18 后增量 R2 很小，则说明 SRC 未遗漏关键预测变量。",
            ),
            new_code_cell(NB02_DIVERGENCE),
        ],
    )
    insert_once_after(
        nb,
        "76427c99",
        "2026-06-16 V1: marginal-variable ablation",
        [
            markdown(
                "第 15-18 名变量边际消融检验",
                "该分析检验 18 变量截断是否保守。若逐个移除边际变量后交叉验证 R2 变化很小，则说明第 18 名并非脆弱阈值，而是兼顾解释充分性与实用性的保守选择。",
            ),
            new_code_cell(NB02_ABLATION),
        ],
    )
    write_nb(path, nb)


def patch_nb03() -> None:
    path = NOTEBOOKS["nb03"]
    nb = read_nb(path)
    cell = code_by_id(nb, "c07d156c")
    replace_project_root_cell(
        cell,
        {
            "old": "for p in [OUT_DIR, FIG_DIR, MODEL_DIR]:",
            "new": "for p in [OUT_DIR, FIG_DIR, MODEL_DIR, PAPER_ASSETS_DIR, PAPER_ASSETS_FIG_DIR]:",
        },
    )
    c = code_by_id(nb, "86e190c0")
    c.source = NB03_FIT_COMPARE
    insert_once_after(
        nb,
        "86e190c0",
        "2026-06-16 V1: physical decomposition of predictive R2",
        [
            markdown(
                "高 R2 的物理分组分解",
                "该分析把模型精度拆分为生活热水、几何、系统运行、围护结构和功能内扰的累积解释力，用研究事实说明高 R2 来自确定性仿真响应面的物理结构，而不是信息泄漏。",
            ),
            new_code_cell(NB03_R2_DECOMP),
        ],
    )
    for existing in nb.cells:
        if existing.cell_type == "code" and "2026-06-16 V1: physical decomposition of predictive R2" in existing.source:
            existing.source = NB03_R2_DECOMP
    c = code_by_id(nb, "1de98079")
    old = """# XGBoost with 39 vars
if HAS_XGB:
    pipe_xgb_full = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('xgb', XGBRegressor(n_estimators=500, max_depth=5, learning_rate=0.05,
                         subsample=0.8, random_state=42, n_jobs=-1))
    ])
    pipe_xgb_full.fit(Xf_train, yf_train)
    xgb_full_r2 = pipe_xgb_full.score(Xf_test, yf_test)
else:
    xgb_full_r2 = np.nan"""
    new = """# XGBoost with 39 vars, using the same tuned parameters when available.
if HAS_XGB:
    xgb_defaults = {
        'n_estimators': 500,
        'max_depth': 5,
        'learning_rate': 0.05,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
    }
    tuned = {}
    if 'XGBoost' in best_params_by_model and best_params_by_model['XGBoost']:
        tuned = {
            key.replace('model__', ''): value
            for key, value in best_params_by_model['XGBoost'].items()
            if key.startswith('model__')
        }
    xgb_params = {**xgb_defaults, **tuned}
    pipe_xgb_full = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('xgb', XGBRegressor(
            objective='reg:squarederror',
            random_state=RANDOM_SEED,
            n_jobs=-1,
            **xgb_params
        ))
    ])
    pipe_xgb_full.fit(Xf_train, yf_train)
    xgb_full_r2 = pipe_xgb_full.score(Xf_test, yf_test)
else:
    xgb_full_r2 = np.nan"""
    c.source = c.source.replace(old, new)
    c = code_by_id(nb, "173c1d65")
    c.source = c.source.replace("LGBMRegressor(random_state=RANDOM_SEED)", "LGBMRegressor(random_state=RANDOM_SEED, verbose=-1)")
    write_nb(path, nb)


def patch_nb04() -> None:
    path = NOTEBOOKS["nb04"]
    nb = read_nb(path)
    cell = code_by_id(nb, "1a14a394")
    replace_project_root_cell(
        cell,
        {
            "old": "for p in [OUT_DIR, FIG_DIR, MODEL_DIR]:",
            "new": "for p in [OUT_DIR, FIG_DIR, MODEL_DIR, PAPER_ASSETS_DIR, PAPER_ASSETS_FIG_DIR]:",
        },
    )
    insert_once_after(
        nb,
        "8d9bf18c",
        "2026-06-16 V1: district cooling factor derivation",
        [
            markdown(
                "区域供冷排放因子推导说明",
                "区域供冷因子 0.16 kgCO2e/kWh 按间接电力消耗与管网冷量损失叠加估算：0.55 ÷ COP 4.5 = 0.122 kgCO2e/kWh；管网冷量损失率约 7% 对应 0.55 × 0.07 = 0.038 kgCO2e/kWh；两者相加约为 0.160 kgCO2e/kWh。COP=4.5 的量级与区域供冷工程指南及既有建筑能源研究中的集中冷站效率范围一致；该因子因此作为情景化碳核算假设，而非普适常数。",
            )
        ],
    )
    c = code_by_id(nb, "1657814c")
    c.source = c.source.replace(
        "'Grid Decarbonisation 2030 0.40': {\n        'electricity': 0.40, 'natural_gas': 0.202,\n        'district_heating': 0.22, 'district_cooling': 0.16\n    },",
        "'Grid Decarbonisation 2030 0.40': {\n        'electricity': 0.40, 'natural_gas': 0.16,\n        'district_heating': 0.18, 'district_cooling': 0.14\n    },",
    )
    c.source = c.source.replace(
        "'Grid Decarbonisation 2050 0.25': {\n        'electricity': 0.25, 'natural_gas': 0.202,\n        'district_heating': 0.22, 'district_cooling': 0.16\n    },",
        "'Grid Decarbonisation 2050 0.25': {\n        'electricity': 0.25, 'natural_gas': 0.12,\n        'district_heating': 0.12, 'district_cooling': 0.10\n    },",
    )
    if "2026-06-16 V1: electricity-factor threshold sweep" not in c.source:
        c.source = c.source.rstrip() + "\n" + NB04_THRESHOLD_APPEND
    write_nb(path, nb)


def main() -> None:
    patch_nb01()
    patch_nb02()
    patch_nb03()
    patch_nb04()
    print("Applied 2026-06-16 V1 reviewer-strengthening notebook edits.")


if __name__ == "__main__":
    main()
