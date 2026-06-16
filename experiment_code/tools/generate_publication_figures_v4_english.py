from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle


def find_repo_root(start: Path) -> Path:
    start = start.resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "input" / "Beijing.epw").exists() or (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


PROJECT_ROOT = find_repo_root(Path(__file__))
FIG_DIR = PROJECT_ROOT / "outputs_step1" / "figures"


COL = {
    "ink": "#243142",
    "muted": "#687385",
    "line": "#526173",
    "podium": "#F5DA78",
    "podium_side": "#D7B755",
    "wall": "#FFE7A5",
    "wall_side": "#E7C75E",
    "roof": "#9B111E",
    "room": "#A9C7E8",
    "room_edge": "#5B83B4",
    "service": "#E99AA5",
    "corridor": "#F4D35E",
    "thermal": "#FFF3CD",
    "energy": "#E6F2FF",
    "carbon": "#FDE7E7",
    "green": "#E7F3E8",
    "blue": "#4C78A8",
    "orange": "#F58518",
    "grey_bg": "#F3F5F8",
}


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "axes.unicode_minus": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 8.5,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def arrow(ax, start, end, color=COL["ink"], lw=1.25, ms=11, style="-|>", **kwargs):
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle=style,
        mutation_scale=ms,
        linewidth=lw,
        color=color,
        shrinkA=2,
        shrinkB=2,
        **kwargs,
    )
    ax.add_patch(patch)
    return patch


def label(ax, text, xy, size=8.5, weight="normal", color=None, ha="center", va="center", **kwargs):
    return ax.text(xy[0], xy[1], text, fontsize=size, fontweight=weight, color=color or COL["ink"], ha=ha, va=va, **kwargs)


def rect(ax, xy, w, h, text="", fc="white", ec=None, lw=0.9, size=8, weight="normal"):
    r = Rectangle(xy, w, h, facecolor=fc, edgecolor=ec or COL["line"], linewidth=lw)
    ax.add_patch(r)
    if text:
        label(ax, text, (xy[0] + w / 2, xy[1] + h / 2), size=size, weight=weight)
    return r


def poly(ax, points, fc, ec=None, lw=0.9, z=1):
    p = Polygon(points, closed=True, facecolor=fc, edgecolor=ec or COL["line"], linewidth=lw, zorder=z)
    ax.add_patch(p)
    return p


def panel(ax, letter):
    label(ax, letter, (0.02, 0.96), size=12, weight="bold", ha="left", va="top", transform=ax.transAxes)


def draw_isometric_hotel(ax):
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 12)
    ax.set_aspect("equal")
    ax.set_axis_off()
    panel(ax, "a")
    label(ax, "Parametric hotel prototype", (6.0, 11.55), size=11.5, weight="bold")

    # Podium.
    poly(ax, [(1.2, 1.35), (8.5, 1.35), (9.8, 2.55), (2.5, 2.55)], COL["podium"], z=2)
    poly(ax, [(8.5, 1.35), (9.8, 2.55), (9.8, 4.0), (8.5, 2.8)], COL["podium_side"], z=2)
    poly(ax, [(1.2, 2.8), (8.5, 2.8), (9.8, 4.0), (2.5, 4.0)], "#CFC8B8", z=3)
    poly(ax, [(1.2, 1.35), (8.5, 1.35), (8.5, 2.8), (1.2, 2.8)], "#F9E59C", z=2)

    # Tower: larger, more like the reference image.
    poly(ax, [(2.5, 2.8), (7.5, 2.8), (7.5, 10.0), (2.5, 10.0)], COL["wall"], z=5)
    poly(ax, [(7.5, 2.8), (8.35, 3.55), (8.35, 10.75), (7.5, 10.0)], COL["wall_side"], z=4)
    poly(ax, [(2.5, 10.0), (7.5, 10.0), (8.35, 10.75), (3.35, 10.75)], COL["roof"], z=6)

    # Facade grid and windows.
    for y in [3.25, 3.85, 4.45, 5.05, 5.65, 6.25, 6.85, 7.45, 8.05, 8.65, 9.25]:
        ax.plot([2.7, 7.25], [y, y], color="#B9952C", lw=0.42, zorder=7)
    for x in [3.0, 3.65, 4.3, 4.95, 5.6, 6.25, 6.9]:
        ax.plot([x, x], [3.05, 9.75], color="#B9952C", lw=0.42, zorder=7)
    for x in [1.7, 2.7, 3.7, 4.7, 5.7, 6.7, 7.7]:
        rect(ax, (x, 1.72), 0.55, 0.36, fc=COL["room"], ec=COL["room_edge"], lw=0.5)
    for x in [8.04, 8.04]:
        pass
    for y in [3.45, 4.35, 5.25, 6.15, 7.05, 7.95, 8.85, 9.55]:
        ax.plot([7.7, 8.18], [y, y + 0.43], color="#A4852F", lw=0.38, zorder=8)

    # Dimension guides.
    ax.annotate("", xy=(1.2, 0.65), xytext=(8.5, 0.65), arrowprops=dict(arrowstyle="<->", lw=0.9, color=COL["muted"]))
    label(ax, "Building length L", (4.85, 0.32), size=8, color=COL["muted"])
    ax.annotate("", xy=(10.35, 1.35), xytext=(10.35, 10.0), arrowprops=dict(arrowstyle="<->", lw=0.9, color=COL["muted"]))
    label(ax, "Number of floors N", (10.72, 5.65), size=8, color=COL["muted"], rotation=90)

    label(ax, "Geometry: L, W, N, floor height, aspect ratio", (0.75, 11.0), size=8.2, ha="left")
    label(ax, "Envelope: WWR, U-values, window type", (0.75, 10.6), size=8.2, ha="left")


def draw_floor_plan(ax):
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.85)
    ax.set_aspect("equal")
    ax.set_axis_off()
    panel(ax, "b")
    label(ax, "Typical guest-room floor plan", (6, 6.55), size=10.5, weight="bold")
    rect(ax, (0.65, 0.95), 10.75, 4.8, fc="white", ec=COL["line"], lw=1.0)
    rect(ax, (0.65, 2.85), 10.75, 0.85, "Corridor", COL["corridor"], "#B58B00", size=8.5)
    for i in range(8):
        rect(ax, (0.9 + i * 1.05, 4.02), 0.92, 1.35, "Room", COL["room"], COL["room_edge"], size=6.8)
        rect(ax, (0.9 + i * 1.05, 1.24), 0.92, 1.35, "Room", COL["room"], COL["room_edge"], size=6.8)
    rect(ax, (9.45, 1.24), 1.65, 4.13, "Core\nservice", COL["service"], "#B65F6A", size=8)

    ax.annotate("", xy=(0.65, 0.42), xytext=(11.4, 0.42), arrowprops=dict(arrowstyle="<->", lw=0.8, color=COL["muted"]))
    label(ax, "Building length L", (6.02, 0.12), size=7.6, color=COL["muted"])
    ax.annotate("", xy=(11.78, 0.95), xytext=(11.78, 5.75), arrowprops=dict(arrowstyle="<->", lw=0.8, color=COL["muted"]))
    label(ax, "Building width W", (12.02, 3.35), size=7.6, color=COL["muted"], rotation=90)

    legend_x = 0.9
    for name, color, edge in [("Guest rooms", COL["room"], COL["room_edge"]), ("Service/core", COL["service"], "#B65F6A"), ("Corridor", COL["corridor"], "#B58B00")]:
        rect(ax, (legend_x, 6.08), 0.2, 0.2, fc=color, ec=edge, lw=0.6)
        label(ax, name, (legend_x + 0.3, 6.18), size=7.0, ha="left")
        legend_x += 2.35


def draw_envelope_panel(ax):
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.set_axis_off()
    panel(ax, "c")
    label(ax, "Facade thermal boundary", (6, 5.62), size=10.5, weight="bold")
    rect(ax, (1.05, 0.9), 5.25, 3.9, fc=COL["wall"], ec="#9A7B2F", lw=1.0)
    for y in [1.25, 2.05, 2.85, 3.65]:
        for x in [1.45, 2.25, 3.05, 3.85, 4.65, 5.45]:
            rect(ax, (x, y), 0.42, 0.42, fc=COL["room"], ec=COL["room_edge"], lw=0.45)
    label(ax, "WWR = window area / facade area", (1.05, 5.05), size=8.2, ha="left")
    rect(ax, (7.05, 3.2), 3.55, 0.9, "Opaque envelope\nU_wall, U_roof", COL["thermal"], "#B58B00", size=8)
    rect(ax, (7.05, 1.65), 3.55, 0.9, "Glazing heat gain\nSHGC, U_win", COL["energy"], COL["blue"], size=8)
    arrow(ax, (6.35, 3.65), (7.05, 3.65), COL["orange"])
    arrow(ax, (6.35, 2.1), (7.05, 2.1), COL["blue"])


def draw_accounting_chain(ax):
    ax.set_xlim(0, 12.6)
    ax.set_ylim(0, 12)
    ax.set_axis_off()
    panel(ax, "d")
    label(ax, "Thermal-energy-carbon accounting chain", (6.3, 11.5), size=10.5, weight="bold")

    nodes = {
        "idf": ((0.45, 9.55), 2.9, 0.95, "Parametric IDF\ngeometry\nenvelope\nuse", COL["energy"]),
        "eplus": ((4.55, 9.55), 2.35, 0.95, "EnergyPlus\nIdealLoads", COL["energy"]),
        "loads": ((8.65, 9.55), 2.85, 0.95, "End-use loads\nheating\ncooling", COL["energy"]),
        "elec": ((0.6, 6.85), 2.75, 1.05, "Electricity\nlighting\nplug / fan\ncooling", COL["energy"]),
        "gas": ((4.65, 6.85), 2.25, 1.05, "Natural gas\nDHW", COL["thermal"]),
        "district": ((8.4, 6.85), 3.15, 1.05, "District energy\nheating / cooling\nscenarios", COL["thermal"]),
        "eui": ((1.05, 4.25), 2.55, 1.0, "EUI\nkWh/(m2.a)", COL["green"]),
        "ef": ((8.15, 4.25), 2.8, 1.0, "Emission factors\nkgCO2e/kWh", COL["carbon"]),
        "ocei": ((4.3, 1.72), 3.8, 1.08, "OCEI\nkgCO2e/(m2.a)", COL["green"]),
    }
    for xy, w, h, txt, fc in nodes.values():
        rect(ax, xy, w, h, txt, fc, COL["line"], lw=0.9, size=6.8, weight="bold" if "EUI" in txt or "OCEI" in txt else "normal")

    arrow(ax, (3.35, 10.02), (4.55, 10.02))
    arrow(ax, (6.9, 10.02), (8.65, 10.02))
    arrow(ax, (1.9, 9.55), (1.98, 7.9))
    arrow(ax, (5.72, 9.55), (5.78, 7.9))
    arrow(ax, (10.08, 9.55), (10.0, 7.9))
    arrow(ax, (1.98, 6.85), (2.08, 5.25))
    arrow(ax, (5.78, 6.85), (3.15, 5.25))
    arrow(ax, (10.0, 6.85), (9.55, 5.25))
    arrow(ax, (2.35, 4.25), (5.2, 2.8))
    arrow(ax, (9.55, 4.25), (7.25, 2.8))
    label(ax, "All indicators are normalized by gross floor area.", (6.3, 0.75), size=7.7, color=COL["muted"])


def generate_hotel_engineering_schematic_v4(out_dir: Path = FIG_DIR) -> dict[str, Path]:
    configure_style()
    out_dir.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(14.6, 7.8), dpi=190)
    gs = fig.add_gridspec(2, 3, width_ratios=[1.22, 1.08, 1.08], height_ratios=[1, 1], wspace=0.20, hspace=0.24)
    ax0 = fig.add_subplot(gs[:, 0])
    ax1 = fig.add_subplot(gs[0, 1])
    ax2 = fig.add_subplot(gs[1, 1])
    ax3 = fig.add_subplot(gs[:, 2])
    draw_isometric_hotel(ax0)
    draw_floor_plan(ax1)
    draw_envelope_panel(ax2)
    draw_accounting_chain(ax3)
    fig.suptitle("Hotel thermal-engineering schematic for the EUI-OCEI workflow", fontsize=14, fontweight="bold", y=0.992)

    base = out_dir / "hotel_thermal_engineering_schematic_v4_en"
    outputs = {}
    for ext, kwargs in {"png": {"dpi": 350}, "svg": {}, "pdf": {}}.items():
        path = base.with_suffix(f".{ext}")
        fig.savefig(path, bbox_inches="tight", **kwargs)
        outputs[ext] = path
    plt.close(fig)
    return outputs


def generate_research_workflow_v4(out_dir: Path = FIG_DIR) -> dict[str, Path]:
    configure_style()
    out_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(14.8, 7.6), dpi=190)
    ax.set_axis_off()
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8.3)

    label(ax, "Research pipeline for parametric simulation, surrogate modelling, and EUI-OCEI coupling", (7.5, 7.85), size=13.5, weight="bold")

    stages = [
        ((0.45, 6.2), 2.25, 0.82, "Inputs\nweather / parameter space\ncode constraints", COL["grey_bg"]),
        ((3.1, 6.2), 2.25, 0.82, "Sampling\nLHS + geometric\nfeasibility screen", COL["energy"]),
        ((5.75, 6.2), 2.25, 0.82, "Simulation\nEnergyPlus 25.2.0\nSQLite outputs", COL["energy"]),
        ((8.4, 6.2), 2.25, 0.82, "Dataset\nEUI labels +\nend-use energy", COL["green"]),
        ((11.05, 6.2), 2.8, 0.82, "Interpretation\nVIF + SRC bootstrap\nSHAP cross-check", COL["thermal"]),
        ((11.05, 3.9), 2.8, 0.82, "Surrogate modelling\n17 regressors\nsplit-safe pipelines", COL["carbon"]),
        ((8.4, 3.9), 2.25, 0.82, "Carbon accounting\nenergy carriers +\nemission factors", COL["carbon"]),
        ((5.75, 3.9), 2.25, 0.82, "Coupling analysis\ncorrelation / ranking\nfactor comparison", COL["green"]),
        ((3.1, 3.9), 2.25, 0.82, "Robustness\nscreening shifts\nfactor scenarios", COL["thermal"]),
        ((0.45, 3.9), 2.25, 0.82, "Outputs\nfigures / tables\nrevision evidence", COL["grey_bg"]),
    ]
    centers = []
    for xy, w, h, text, fc in stages:
        rect(ax, xy, w, h, text, fc, COL["line"], lw=1.0, size=7.8)
        centers.append((xy[0] + w / 2, xy[1] + h / 2))

    for i in range(4):
        arrow(ax, (centers[i][0] + 1.13, centers[i][1]), (centers[i + 1][0] - 1.13, centers[i + 1][1]), lw=1.5)
    arrow(ax, (centers[4][0], centers[4][1] - 0.42), (centers[5][0], centers[5][1] + 0.42), lw=1.5, connectionstyle="angle3,angleA=-90,angleB=180")
    for i in range(5, 9):
        arrow(ax, (centers[i][0] - 1.13, centers[i][1]), (centers[i + 1][0] + 1.13, centers[i + 1][1]), lw=1.5)

    qa = [
        ((0.9, 1.55), 2.55, 0.72, "Representativeness\nKS / Jensen-Shannon"),
        ((4.25, 1.55), 2.55, 0.72, "Leakage control\nimputer / scaler after split"),
        ((7.6, 1.55), 2.55, 0.72, "Figure QA\nno overlap / readable / accessible"),
        ((10.95, 1.55), 2.75, 0.72, "Reproducibility\nnotebooks + CSV + vector figures"),
    ]
    for xy, w, h, text in qa:
        rect(ax, xy, w, h, text, "white", COL["blue"], lw=1.1, size=7.8)
    for x in [3.45, 6.8, 10.15]:
        arrow(ax, (x, 1.91), (x + 0.75, 1.91), COL["blue"], lw=1.25)

    label(
        ax,
        "Straight and orthogonal connectors indicate data dependency; QA checks remain visible as reproducibility gates.",
        (7.5, 0.62),
        size=8.0,
        color=COL["muted"],
    )

    base = out_dir / "research_pipeline_workflow_v4_en"
    outputs = {}
    for ext, kwargs in {"png": {"dpi": 350}, "svg": {}, "pdf": {}}.items():
        path = base.with_suffix(f".{ext}")
        fig.savefig(path, bbox_inches="tight", **kwargs)
        outputs[ext] = path
    plt.close(fig)
    return outputs


def main() -> None:
    hotel = generate_hotel_engineering_schematic_v4()
    workflow = generate_research_workflow_v4()
    print("Generated English hotel thermal-engineering schematic:")
    for p in hotel.values():
        print(f"  {p}")
    print("Generated English research workflow:")
    for p in workflow.values():
        print(f"  {p}")


if __name__ == "__main__":
    main()
