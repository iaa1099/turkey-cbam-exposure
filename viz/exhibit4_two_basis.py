"""Exhibit 4 — two-basis understatement.

Read-only on output/electricity_grid_intensity_bases.csv; plot only, no
recompute of the two named bases. The geothermal-zero validation marker
(0.4399) is not a CSV column — it is the existing, already-tested result of
features/electricityGood.validate_against_benchmark() (frozen model code,
confirmed passing within +/-2% tolerance); it is read here for annotation,
not recomputed or re-derived.
"""

import pandas as pd

from viz.style import (
    GREY_DARK, GREY_LIGHT, GREY_MED, INK, PINE_GREEN,
    add_footer, add_header, new_exhibit, save_exhibit, style_axis,
)

SRC = "output/electricity_grid_intensity_bases.csv"
VALIDATION_GEOTHERMAL_ZERO = 0.4399  # features/electricityGood.validate_against_benchmark()


def build():
    df = pd.read_csv(SRC).set_index("basis")
    benchmark = df.loc["ember_iea_benchmark", "intensity_tco2_per_mwh"]
    adjusted = df.loc["grid_intensity_ncg_adjusted", "intensity_tco2_per_mwh"]
    delta_relative = adjusted / benchmark - 1

    fig = new_exhibit(figsize=(9.2, 6.0))
    add_header(
        fig,
        eyebrow="CBAM exposure model · exhibit 4",
        title="Standard accounting understates grid carbon by 5.8%",
        subtitle="Türkiye grid carbon intensity, tCO₂/MWh — two accounting bases, same generation mix",
    )

    ax = fig.add_axes([0.14, 0.22, 0.74, 0.52])

    xs = [0, 1]
    heights = [benchmark, adjusted]
    colors = [GREY_LIGHT, PINE_GREEN]
    bars = ax.bar(xs, heights, width=0.5, color=colors, zorder=3)

    # value labels mid-bar — kept well clear of both the bar top (bracket) and
    # the validation diamond, which sits right at the benchmark bar's top edge
    for x, h, c in zip(xs, heights, [GREY_DARK, "white"]):
        ax.text(x, h * 0.5, f"{h:.4f}", ha="center", va="center", fontsize=12, color=c, weight="bold")

    ax.set_xticks(xs)
    ax.set_xticklabels(
        ["Ember/IEA benchmark\n(geothermal ~0)", "NCG-adjusted\n(operative figure)"],
        fontsize=10.5,
    )
    ax.get_xticklabels()[1].set_color(INK)
    ax.get_xticklabels()[1].set_fontweight("bold")
    ax.get_xticklabels()[0].set_color(GREY_MED)

    ax.set_ylabel("tCO₂ / MWh", fontsize=10, color=GREY_MED)
    ax.set_ylim(0, adjusted * 1.34)
    ax.set_xlim(-1.5, 1.55)  # wide left margin — dedicated whitespace for the validation callout
    style_axis(ax, bottom_spine=False)
    ax.tick_params(axis="x", length=0)

    # delta bracket between the two bars, well clear of the in-bar value labels
    bracket_y = adjusted + 0.09
    ax.plot([0, 0, 1, 1], [benchmark + 0.02, bracket_y, bracket_y, adjusted + 0.02],
            color=INK, linewidth=1.0, zorder=4)
    ax.text(0.5, bracket_y + 0.008, f"+{delta_relative:.1%}", ha="center", va="bottom",
            fontsize=12, color=INK, weight="bold")

    # geothermal-zero validation marker, landing on the benchmark bar; callout
    # lives entirely in the whitespace to the left, clear of the bar and the
    # 0.4425 label (now mid-bar, not top-of-bar)
    ax.scatter([0], [VALIDATION_GEOTHERMAL_ZERO], marker="D", s=55, color=INK, zorder=5)
    ax.annotate(
        f"geothermal forced to 0: {VALIDATION_GEOTHERMAL_ZERO:.4f}\n(−0.6% vs. benchmark —\nisolates the gap)",
        xy=(0, VALIDATION_GEOTHERMAL_ZERO), xytext=(-1.44, 0.40), textcoords="data",
        fontsize=8.5, color=GREY_DARK, ha="left", va="center",
        arrowprops=dict(arrowstyle="-", color=GREY_DARK, linewidth=0.8),
    )

    add_footer(
        fig,
        source_text=(
            "Source: output/electricity_grid_intensity_bases.csv (features/electricityGood.py)\n"
            "Validation marker: validate_against_benchmark(), geothermal forced to 0, checked within +/-2% tolerance (passes)."
        ),
        footnote="Delta is 5.8% vs. the Ember/IEA benchmark — the operative figure for electricity-good exposure and the renewable-share sweep.",
    )
    return fig


if __name__ == "__main__":
    fig = build()
    png, svg = save_exhibit(fig, "exhibit4_two_basis")
    print(png)
    print(svg)
