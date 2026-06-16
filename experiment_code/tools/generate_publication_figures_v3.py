from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle


def find_repo_root(start: Path) -> Path:
    start = start.resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "input" / "Beijing.epw").exists() or (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


PROJECT_ROOT = find_repo_root(Path(__file__))
FIG_DIR = PROJECT_ROOT / "outputs_step1" / "figures"


PALETTE = {
    "blue": "#4C78A8",
    "blue_light": "#A9C7E8",
    "teal": "#54A24B",
    "gold": "#F2CF5B",
    "rose": "#ECA0A6",
    "red": "#B64646",
    "orange": "#F58518",
    "grey": "#6B7280",
    "grey_light": "#E5E7EB",
    "ink": "#1F2937",
}


def _available_font(names: list[str]) -> str:
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in names:
        if name in installed:
            return name
    return "DejaVu Sans"


def configure_style() -> None:
    font = _available_font(["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Arial Unicode MS", "DejaVu Sans"])
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [font, "Arial", "DejaVu Sans", "sans-serif"],
            "axes.unicode_minus": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 9,
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def _panel_label(ax, label: str) -> None:
    ax.text(0.01, 0.98, label, transform=ax.transAxes, ha="left", va="top", fontsize=11, fontweight="bold", color=PALETTE["ink"])


def _arrow(ax, xy1, xy2, color=None, lw=1.4, style="-|>", connectionstyle="arc3,rad=0"):
    patch = FancyArrowPatch(
        xy1,
        xy2,
        arrowstyle=style,
        mutation_scale=12,
        linewidth=lw,
        color=color or PALETTE["ink"],
        connectionstyle=connectionstyle,
        shrinkA=2,
        shrinkB=2,
    )
    ax.add_patch(patch)
    return patch


def _box(ax, xy, w, h, text, fc, ec=None, fontsize=8.5, weight="normal"):
    rect = Rectangle(xy, w, h, facecolor=fc, edgecolor=ec or PALETTE["ink"], linewidth=0.9)
    ax.add_patch(rect)
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center", fontsize=fontsize, color=PALETTE["ink"], fontweight=weight)
    return rect


def generate_hotel_engineering_schematic(out_dir: Path = FIG_DIR) -> dict[str, Path]:
    """Generate a compact, manuscript-ready hotel thermal-engineering schematic."""
    configure_style()
    out_dir.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(13.6, 7.2), dpi=180)
    gs = fig.add_gridspec(2, 3, width_ratios=[1.08, 1.02, 1.22], height_ratios=[1.0, 0.92], wspace=0.22, hspace=0.24)
    ax_mass = fig.add_subplot(gs[:, 0])
    ax_plan = fig.add_subplot(gs[0, 1])
    ax_facade = fig.add_subplot(gs[1, 1])
    ax_system = fig.add_subplot(gs[:, 2])

    for ax in [ax_mass, ax_plan, ax_facade, ax_system]:
        ax.set_axis_off()

    _panel_label(ax_mass, "a")
    ax_mass.set_title("参数化酒店原型体量", loc="center", pad=8, fontsize=11, fontweight="bold")
    ax_mass.set_xlim(0, 10)
    ax_mass.set_ylim(0, 12)

    # Simple axonometric massing: podium + tower, with facade grid.
    podium_front = Polygon([(1.0, 1.0), (7.6, 1.0), (8.6, 2.0), (2.0, 2.0)], closed=True, fc="#F6E3A0", ec=PALETTE["ink"], lw=0.9)
    podium_side = Polygon([(7.6, 1.0), (8.6, 2.0), (8.6, 3.5), (7.6, 2.5)], closed=True, fc="#E9C96A", ec=PALETTE["ink"], lw=0.9)
    podium_top = Polygon([(1.0, 2.5), (7.6, 2.5), (8.6, 3.5), (2.0, 3.5)], closed=True, fc="#CFC7B7", ec=PALETTE["ink"], lw=0.9)
    tower_front = Polygon([(2.0, 2.5), (6.4, 2.5), (6.4, 10.2), (2.0, 10.2)], closed=True, fc="#FFE8A3", ec=PALETTE["ink"], lw=0.9)
    tower_side = Polygon([(6.4, 2.5), (7.1, 3.2), (7.1, 10.9), (6.4, 10.2)], closed=True, fc="#EBC75B", ec=PALETTE["ink"], lw=0.9)
    tower_top = Polygon([(2.0, 10.2), (6.4, 10.2), (7.1, 10.9), (2.7, 10.9)], closed=True, fc="#9E1B1B", ec=PALETTE["ink"], lw=0.9)
    for patch in [podium_front, podium_side, podium_top, tower_front, tower_side, tower_top]:
        ax_mass.add_patch(patch)

    for x in [2.4, 3.1, 3.8, 4.5, 5.2, 5.9]:
        ax_mass.plot([x, x], [2.7, 9.8], color="#B9942F", lw=0.45)
    for y in [3.1, 3.7, 4.3, 4.9, 5.5, 6.1, 6.7, 7.3, 7.9, 8.5, 9.1, 9.7]:
        ax_mass.plot([2.2, 6.2], [y, y], color="#B9942F", lw=0.45)
    for x in [1.6, 2.7, 3.8, 4.9, 6.0]:
        ax_mass.add_patch(Rectangle((x, 1.28), 0.75, 0.34, fc=PALETTE["blue_light"], ec=PALETTE["blue"], lw=0.5))
    ax_mass.annotate("", xy=(2.0, 0.48), xytext=(7.6, 0.48), arrowprops=dict(arrowstyle="<->", lw=0.9, color=PALETTE["grey"]))
    ax_mass.text(4.8, 0.18, "建筑长度 L", ha="center", fontsize=8, color=PALETTE["grey"])
    ax_mass.annotate("", xy=(8.95, 1.0), xytext=(8.95, 10.4), arrowprops=dict(arrowstyle="<->", lw=0.9, color=PALETTE["grey"]))
    ax_mass.text(9.15, 5.7, "楼层数 N", rotation=90, va="center", fontsize=8, color=PALETTE["grey"])
    ax_mass.text(1.1, 11.35, "几何变量：L, W, N, 层高, 长宽比", fontsize=8.5, color=PALETTE["ink"])
    ax_mass.text(1.1, 10.95, "围护结构：U值、窗墙比（WWR）、窗型", fontsize=8.5, color=PALETTE["ink"])

    _panel_label(ax_plan, "b")
    ax_plan.set_title("标准层平面与功能分区", pad=7, fontsize=11, fontweight="bold")
    ax_plan.set_xlim(0, 12)
    ax_plan.set_ylim(0, 7)
    ax_plan.set_aspect("equal")
    _box(ax_plan, (0.7, 1.0), 10.6, 5.0, "", "white", PALETTE["ink"])
    _box(ax_plan, (0.7, 3.0), 10.6, 1.0, "走廊", PALETTE["gold"], "#B58B00", fontsize=8.2)
    for i in range(8):
        _box(ax_plan, (0.9 + i * 1.05, 4.15), 0.95, 1.55, "客房", PALETTE["blue_light"], PALETTE["blue"], fontsize=7)
        _box(ax_plan, (0.9 + i * 1.05, 1.25), 0.95, 1.55, "客房", PALETTE["blue_light"], PALETTE["blue"], fontsize=7)
    _box(ax_plan, (9.4, 1.25), 1.55, 4.45, "核心筒\n服务区", PALETTE["rose"], "#B65F6A", fontsize=8)
    ax_plan.annotate("", xy=(0.7, 0.42), xytext=(11.3, 0.42), arrowprops=dict(arrowstyle="<->", lw=0.9, color=PALETTE["grey"]))
    ax_plan.text(6.0, 0.1, "建筑长度 L", ha="center", fontsize=8, color=PALETTE["grey"])
    ax_plan.annotate("", xy=(11.75, 1.0), xytext=(11.75, 6.0), arrowprops=dict(arrowstyle="<->", lw=0.9, color=PALETTE["grey"]))
    ax_plan.text(11.95, 3.5, "建筑宽度 W", rotation=90, va="center", fontsize=8, color=PALETTE["grey"])
    ax_plan.text(0.75, 6.45, "可用面积比 = 客房/公共/服务面积约束后的有效面积 / 总建筑面积", fontsize=7.9, color=PALETTE["ink"])

    _panel_label(ax_facade, "c")
    ax_facade.set_title("立面窗墙比与传热边界", pad=7, fontsize=11, fontweight="bold")
    ax_facade.set_xlim(0, 12)
    ax_facade.set_ylim(0, 5.2)
    _box(ax_facade, (0.9, 0.7), 5.4, 3.8, "", "#FFE6A7", "#9A7B2F")
    for y in [1.15, 1.85, 2.55, 3.25]:
        for x in [1.25, 2.1, 2.95, 3.8, 4.65, 5.5]:
            ax_facade.add_patch(Rectangle((x, y), 0.48, 0.36, fc=PALETTE["blue_light"], ec=PALETTE["blue"], lw=0.45))
    _box(ax_facade, (7.0, 0.9), 3.8, 1.15, "窗户得热\nSHGC, U_win", PALETTE["blue_light"], PALETTE["blue"], fontsize=8)
    _box(ax_facade, (7.0, 2.55), 3.8, 1.15, "非透明围护\nU_wall, U_roof", "#F6E3A0", "#9A7B2F", fontsize=8)
    _arrow(ax_facade, (6.35, 3.1), (7.0, 3.1), PALETTE["orange"])
    _arrow(ax_facade, (6.35, 1.45), (7.0, 1.45), PALETTE["blue"])
    ax_facade.text(0.9, 4.85, "WWR = 窗面积 / 外墙面积；四向窗参数分别进入 IDF", fontsize=8.2, color=PALETTE["ink"])

    _panel_label(ax_system, "d")
    ax_system.set_title("热工系统与 EUI-OCEI 核算链", pad=8, fontsize=11, fontweight="bold")
    ax_system.set_xlim(0, 10)
    ax_system.set_ylim(0, 12)
    boxes = {
        "idf": ((0.45, 9.8), 2.65, 1.0, "参数化 IDF\n几何/围护/运行"),
        "eplus": ((4.0, 9.8), 2.45, 1.0, "EnergyPlus\nIdealLoads"),
        "loads": ((7.25, 9.8), 2.35, 1.0, "冷热负荷\nHeating/Cooling"),
        "elec": ((0.45, 7.25), 2.65, 1.0, "电力\n照明/设备/风机/制冷"),
        "gas": ((4.0, 7.25), 2.45, 1.0, "天然气\n生活热水"),
        "district": ((7.25, 7.25), 2.35, 1.0, "区域能源\n供热/供冷情景"),
        "eui": ((1.2, 4.65), 2.85, 1.08, "EUI\nkWh/(m2·a)"),
        "factor": ((5.85, 4.65), 2.9, 1.08, "排放因子\nkgCO2e/kWh"),
        "ocei": ((3.45, 2.0), 3.45, 1.2, "OCEI\nkgCO2e/(m2·a)"),
    }
    for key, (xy, w, h, txt) in boxes.items():
        fc = "#EAF2FB"
        if key in {"gas", "district"}:
            fc = "#FFF4D6"
        if key in {"eui", "ocei"}:
            fc = "#E8F5E9"
        if key == "factor":
            fc = "#FDECEA"
        _box(ax_system, xy, w, h, txt, fc, "#4B5563", fontsize=8.3, weight="bold" if key in {"eui", "ocei"} else "normal")
    _arrow(ax_system, (3.1, 10.3), (4.0, 10.3))
    _arrow(ax_system, (6.45, 10.3), (7.25, 10.3))
    _arrow(ax_system, (8.4, 9.8), (8.4, 8.25))
    _arrow(ax_system, (1.8, 9.8), (1.8, 8.25))
    _arrow(ax_system, (5.2, 9.8), (5.2, 8.25))
    _arrow(ax_system, (1.8, 7.25), (2.6, 5.73))
    _arrow(ax_system, (5.2, 7.25), (3.3, 5.73))
    _arrow(ax_system, (8.4, 7.25), (7.15, 5.73))
    _arrow(ax_system, (7.3, 4.65), (5.45, 3.2))
    _arrow(ax_system, (2.65, 4.65), (4.55, 3.2))
    ax_system.text(0.55, 0.7, "说明：EUI 由终端能耗归一化得到；OCEI 在相同样本上叠加能源载体排放因子。", fontsize=8.1, color=PALETTE["grey"])

    fig.suptitle("北京酒店建筑参数化仿真与热工-碳核算示意图", fontsize=14, fontweight="bold", y=0.985)
    outputs = {}
    base = out_dir / "hotel_thermal_engineering_schematic_v3"
    for ext, kwargs in {"png": {"dpi": 300}, "svg": {}, "pdf": {}}.items():
        path = base.with_suffix(f".{ext}")
        fig.savefig(path, bbox_inches="tight", **kwargs)
        outputs[ext] = path
    plt.close(fig)
    return outputs


def generate_research_workflow(out_dir: Path = FIG_DIR) -> dict[str, Path]:
    """Generate an orthogonal, review-ready research-linkage diagram."""
    configure_style()
    out_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(14.2, 7.4), dpi=180)
    ax.set_axis_off()
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8.2)

    ax.text(7, 7.85, "研究链路图：参数化模拟、机器学习与 EUI-OCEI 耦合分析", ha="center", va="center", fontsize=14, fontweight="bold", color=PALETTE["ink"])

    stages = [
        ((0.45, 6.15), 2.1, 0.85, "输入层\n气象/参数空间/规范约束", PALETTE["grey_light"]),
        ((3.05, 6.15), 2.1, 0.85, "抽样层\nLHS + 几何可行性筛选", "#EAF2FB"),
        ((5.65, 6.15), 2.1, 0.85, "仿真层\nEnergyPlus 25.2.0", "#EAF2FB"),
        ((8.25, 6.15), 2.1, 0.85, "数据层\nEUI 数据集与终端能耗", "#E8F5E9"),
        ((10.85, 6.15), 2.55, 0.85, "解释层\nSRC + SHAP 变量筛选", "#FFF4D6"),
        ((10.85, 3.95), 2.55, 0.85, "代理模型层\n17 类模型与交叉验证", "#FDECEA"),
        ((8.25, 3.95), 2.1, 0.85, "碳核算层\n能源载体与排放因子", "#FDECEA"),
        ((5.65, 3.95), 2.1, 0.85, "耦合层\nEUI-OCEI 相关/排名偏移", "#E8F5E9"),
        ((3.05, 3.95), 2.1, 0.85, "稳健性层\n因子情景敏感性", "#FFF4D6"),
        ((0.45, 3.95), 2.1, 0.85, "输出层\n图表/表格/修订证据", PALETTE["grey_light"]),
    ]
    centers = []
    for xy, w, h, txt, fc in stages:
        _box(ax, xy, w, h, txt, fc, "#4B5563", fontsize=8.6)
        centers.append((xy[0] + w / 2, xy[1] + h / 2))

    for i in range(4):
        _arrow(ax, (centers[i][0] + 1.06, centers[i][1]), (centers[i + 1][0] - 1.06, centers[i + 1][1]))
    _arrow(ax, (centers[4][0], centers[4][1] - 0.43), (centers[5][0], centers[5][1] + 0.43), connectionstyle="angle3,angleA=-90,angleB=180")
    for i in range(5, 9):
        _arrow(ax, (centers[i][0] - 1.06, centers[i][1]), (centers[i + 1][0] + 1.06, centers[i + 1][1]))

    # Evidence strands beneath the main workflow.
    strand_y = 1.65
    strand_boxes = [
        ((0.75, strand_y), 2.5, 0.72, "代表性检查\nKS/Jensen-Shannon"),
        ((3.95, strand_y), 2.5, 0.72, "防泄漏检查\nsplit 后 Pipeline"),
        ((7.15, strand_y), 2.5, 0.72, "图件 QA\n无遮挡/可读/色盲友好"),
        ((10.35, strand_y), 2.7, 0.72, "复现包\nnotebook + CSV + 图像"),
    ]
    for xy, w, h, txt in strand_boxes:
        _box(ax, xy, w, h, txt, "white", PALETTE["blue"], fontsize=8.2)
    for x in [3.25, 6.45, 9.65]:
        _arrow(ax, (x, strand_y + 0.36), (x + 0.7, strand_y + 0.36), PALETTE["blue"], lw=1.2)

    ax.text(
        7,
        0.65,
        "直线/折线表示数据依赖；上行链路生成 EUI 代理模型，下行链路叠加碳排放核算并检验能碳耦合稳健性。",
        ha="center",
        fontsize=8.5,
        color=PALETTE["grey"],
    )

    outputs = {}
    base = out_dir / "research_pipeline_workflow_v3"
    for ext, kwargs in {"png": {"dpi": 300}, "svg": {}, "pdf": {}}.items():
        path = base.with_suffix(f".{ext}")
        fig.savefig(path, bbox_inches="tight", **kwargs)
        outputs[ext] = path
    plt.close(fig)
    return outputs


def main() -> None:
    hotel = generate_hotel_engineering_schematic()
    workflow = generate_research_workflow()
    print("Generated hotel schematic:")
    for path in hotel.values():
        print(f"  {path}")
    print("Generated research workflow:")
    for path in workflow.values():
        print(f"  {path}")


if __name__ == "__main__":
    main()
