"""Exhibit 1 — cross-sector exposure cliff.

Read-only on output/cbam_cross_sector_exposure.csv; plot only, no recompute.
"""

import pandas as pd

from viz.style import (
    GREY_DARK, GREY_LIGHT, GREY_MED, INK, PINE_GREEN,
    add_footer, add_header, new_exhibit, save_exhibit, style_axis,
)

SRC = "output/cbam_cross_sector_exposure.csv"

DISPLAY_NAME = {
    "Iron and steel": "Steel",
    "Cement": "Cement",
    "Aluminium": "Aluminium",
    "Fertilisers": "Fertilisers",
    "Hydrogen": "Hydrogen",
}
ACCENT_SECTORS = {"Iron and steel", "Cement"}


def build():
    df = pd.read_csv(SRC).sort_values("share_of_total", ascending=False).reset_index(drop=True)

    fig = new_exhibit(figsize=(9.2, 5.6))
    add_header(
        fig,
        eyebrow="CBAM exposure model · exhibit 1",
        title="Two sectors carry ~90.6% of exposure",
        subtitle="Share of total CBAM exposure across five direct-emissions goods, 2024 Türkiye-to-EU imports",
    )

    ax = fig.add_axes([0.30, 0.20, 0.62, 0.58])

    n = len(df)
    ypos = list(range(n))[::-1]  # steel at top
    colors = [PINE_GREEN if s in ACCENT_SECTORS else GREY_LIGHT for s in df["sector"]]

    bars = ax.barh(ypos, df["share_of_total"] * 100, color=colors, height=0.58, zorder=3)

    # short left-edge tick per category, echoing the PDF's tick-per-row treatment
    for y in ypos:
        ax.plot([0, 0], [y - 0.32, y + 0.32], color=GREY_MED, linewidth=1.0, zorder=2, clip_on=False)

    ax.set_yticks(ypos)
    labels = [DISPLAY_NAME[s] for s in df["sector"]]
    ax.set_yticklabels(labels, fontsize=11.5)
    for tick, sector in zip(ax.get_yticklabels(), df["sector"]):
        if sector in ACCENT_SECTORS:
            tick.set_color(INK)
            tick.set_fontweight("bold")
        else:
            tick.set_color(GREY_MED)

    # direct data labels at bar end
    for y, share, sector in zip(ypos, df["share_of_total"] * 100, df["sector"]):
        label_color = INK if sector in ACCENT_SECTORS else GREY_DARK
        weight = "bold" if sector in ACCENT_SECTORS else "normal"
        ax.text(
            share + 1.3, y, f"{share:.2f}%",
            va="center", ha="left", fontsize=11, color=label_color, weight=weight,
        )

    xmax = df["share_of_total"].max() * 100 * 1.18
    ax.set_xlim(0, xmax)
    ax.set_xticks([])
    style_axis(ax, left_spine=False, bottom_spine=False, hide_y_ticks=True)
    ax.tick_params(axis="y", length=0)

    # make the cliff after cement explicit: dashed separator (stops short of the
    # label — no stray trailing dashes) + annotation flush inside the right margin
    cliff_y = ypos[1] - 0.5  # boundary between cement (index 1) and aluminium (index 2)
    label_x = xmax * 0.995
    ax.plot([0, xmax * 0.74], [cliff_y, cliff_y], color=GREY_MED, linewidth=0.8,
            linestyle=(0, (3, 2)), zorder=1)
    top_two_total = df["share_of_total"].iloc[:2].sum() * 100
    ax.text(
        label_x, cliff_y,
        f"steel + cement = {top_two_total:.1f}%",
        va="center", ha="right", fontsize=9, color=GREY_MED, style="italic",
        zorder=2,
    )

    add_footer(
        fig,
        source_text=(
            "Source: output/cbam_cross_sector_exposure.csv (features/crossSectorExposure.py)\n"
            "Eurostat Comext DS-045409 (2024) x EU CBAM default direct-emissions values, Türkiye sheet, joined at HS4."
        ),
        footnote="Cement uses generic EU default direct values for 7 of 8 CN codes — the least Türkiye-specific sector figure of the five.",
    )
    return fig


if __name__ == "__main__":
    fig = build()
    png, svg = save_exhibit(fig, "exhibit1_cross_sector_cliff")
    print(png)
    print(svg)
