"""Exhibit 3 — renewable-share floor.

Read-only on output/electricity_renewable_sweep.csv; plot only, no recompute.
"""

import pandas as pd

from viz.style import (
    GREY_DARK, GREY_MED, GREY_PALE, INK, PINE_GREEN, PINE_GREEN_PALE,
    add_footer, add_header, new_exhibit, save_exhibit, style_axis,
)

SRC = "output/electricity_renewable_sweep.csv"


def build():
    df = pd.read_csv(SRC).sort_values("renewable_share")
    floor = df["intensity"].iloc[-1]  # value at renewable_share = 1.0 — the geothermal residual

    fig = new_exhibit(figsize=(9.2, 5.8))
    add_header(
        fig,
        eyebrow="CBAM exposure model · exhibit 3",
        title="100% renewable share still leaves a non-zero floor",
        subtitle="Grid carbon intensity under a renewable-share sweep (2024 generation mix, fuel-group proportions held fixed)",
    )

    ax = fig.add_axes([0.10, 0.20, 0.85, 0.56])

    x = df["renewable_share"] * 100
    y = df["intensity"]

    # shade the residual: the band the curve never crosses below
    ax.fill_between(x, 0, floor, color=PINE_GREEN_PALE, zorder=1)

    ax.plot(x, y, color=GREY_DARK, linewidth=2.2, zorder=3, solid_capstyle="round")
    ax.axhline(0, color=GREY_PALE, linewidth=1.2, zorder=0)
    ax.axhline(floor, color=PINE_GREEN, linewidth=1.4, linestyle=(0, (4, 2)), zorder=2)

    ax.scatter([100], [floor], color=PINE_GREEN, s=45, zorder=4)
    ax.annotate(
        f"geothermal floor ≈ {floor:.3f} tCO₂/MWh",
        xy=(100, floor), xytext=(-14, 46), textcoords="offset points",
        fontsize=10, color=PINE_GREEN, ha="right", va="bottom", weight="bold",
        bbox=dict(facecolor="white", edgecolor="none", pad=2.0),
    )

    ax.set_xlim(0, 100)
    ax.set_ylim(-0.02, y.max() * 1.08)
    ax.set_xlabel("Renewable generation share (%)", fontsize=10, color=GREY_MED)
    ax.set_ylabel("Grid carbon intensity (tCO₂ / MWh)", fontsize=10, color=GREY_MED)
    style_axis(ax)

    add_footer(
        fig,
        source_text=(
            "Source: output/electricity_renewable_sweep.csv (features/electricityGood.py, renewable_share_sweep)\n"
            "Geothermal costed at its real 0.887 tCO₂/MWh factor at every scenario point — its share of the renewable mix scales with the sweep."
        ),
        footnote="A larger renewable buildout is not automatically a proportionally cleaner grid if geothermal is a growing part of it.",
    )
    return fig


if __name__ == "__main__":
    fig = build()
    png, svg = save_exhibit(fig, "exhibit3_renewable_floor")
    print(png)
    print(svg)
