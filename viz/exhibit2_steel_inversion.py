"""Exhibit 2 — steel volume/intensity inversion.

Read-only on output/steel_clusters.csv; plot only, no recompute. The design
PDF has no scatter mockup — this extends the system by rule: accent on the
one cluster that carries the bulk-exposure story, greys for the rest, same
type/chrome treatment as the other exhibits.
"""

import pandas as pd

from viz.style import (
    GREY_DARK, GREY_LIGHT, GREY_MED, INK, PINE_GREEN,
    add_footer, add_header, new_exhibit, save_exhibit, style_axis,
)

SRC = "output/steel_clusters.csv"

MODERATE_GREY = "#A8A8A8"  # distinct mid grey — specialty-intensity's dark grey and this must not read as the same value
SPECIALTY_GREY = "#4D4D4D"  # darker than before, for max separation from MODERATE_GREY

CLUSTER_COLOR = {
    "commodity-volume": PINE_GREEN,
    "specialty-intensity": SPECIALTY_GREY,
    "moderate-middle": MODERATE_GREY,
}
# No white edges: at this density (esp. the commodity-volume cluster on the
# right) white rings around every bubble read as "stacked coins" instead of a
# single mass. Overlap is communicated by alpha blending instead.
CLUSTER_EDGE = {
    "commodity-volume": "none",
    "specialty-intensity": "none",
    "moderate-middle": GREY_DARK,  # this fill is pale enough to need a boundary against a white plot background
}
# Everything here recedes relative to the single fully-opaque 7308 marker —
# that recession is what makes 7308 read as the exception, not a fourth cluster.
CLUSTER_ALPHA = {
    "commodity-volume": 0.55,
    "specialty-intensity": 0.55,
    "moderate-middle": 0.75,
}
CLUSTER_LABEL = {
    "commodity-volume": "Commodity-volume (bulk steel)",
    "specialty-intensity": "Specialty-intensity (stainless/alloy)",
    "moderate-middle": "Moderate-middle",
}
CLUSTER_ORDER = ["commodity-volume", "specialty-intensity", "moderate-middle"]

CALLOUT_HS4 = 7308
MAX_MARKER_AREA = 3200  # points^2, at max exposure


def build():
    df = pd.read_csv(SRC)

    fig = new_exhibit(figsize=(9.2, 6.2))
    add_header(
        fig,
        eyebrow="CBAM exposure model · exhibit 2",
        title="Exposure tracks volume, not carbon intensity",
        subtitle="Steel HS4 headings — bubble area = exposure (tCO₂); color = frozen k-means cluster (k=3, silhouette 0.508)",
    )

    ax = fig.add_axes([0.09, 0.235, 0.87, 0.485])

    sizes = df["exposure"] / df["exposure"].max() * MAX_MARKER_AREA
    is_callout = df["hs4"] == CALLOUT_HS4

    for cluster in CLUSTER_ORDER:
        # 7308 is drawn separately, at full opacity, below — every other bubble
        # (including its own cluster-mates) recedes so it reads as the one exception
        mask = (df["cluster_label"] == cluster) & ~is_callout
        ax.scatter(
            df.loc[mask, "tonnes"], df.loc[mask, "direct_intensity"],
            s=sizes[mask], color=CLUSTER_COLOR[cluster],
            alpha=CLUSTER_ALPHA[cluster],
            edgecolors=CLUSTER_EDGE[cluster], linewidths=0.7, zorder=3,
            label=CLUSTER_LABEL[cluster],
        )

    ax.set_xscale("log")
    ax.set_xlabel("Tonnes traded, Türkiye-to-EU 2024 (log scale)", fontsize=10, color=GREY_MED)
    ax.set_ylabel("Direct emissions intensity (tCO₂ / tonne)", fontsize=10, color=GREY_MED)
    ax.set_ylim(-0.3, df["direct_intensity"].max() * 1.28)

    from matplotlib.ticker import FuncFormatter

    def _fmt_tonnes(x, _pos):
        if x >= 1_000_000:
            return f"{x / 1_000_000:g}M"
        if x >= 1_000:
            return f"{x / 1_000:g}k"
        return f"{x:g}"

    ax.xaxis.set_major_formatter(FuncFormatter(_fmt_tonnes))
    style_axis(ax)

    # x dominant, y subordinate — reinforces reading the story left-to-right
    # (volume), not top-to-bottom (intensity)
    ax.spines["bottom"].set_color(GREY_DARK)
    ax.spines["bottom"].set_linewidth(1.3)
    ax.tick_params(axis="x", labelsize=10.5, colors=GREY_DARK)

    # 7308 — the single high-contrast element: full-opacity fill (unlike every
    # other bubble, which recedes at reduced alpha) plus a black ring, so it
    # reads as THE exception rather than just another commodity-volume dot
    row = df.loc[df["hs4"] == CALLOUT_HS4].iloc[0]
    callout_size = sizes[is_callout].iloc[0]
    ax.scatter(
        [row["tonnes"]], [row["direct_intensity"]],
        s=[callout_size], color=PINE_GREEN, alpha=1.0, zorder=4,
    )
    ax.scatter(
        [row["tonnes"]], [row["direct_intensity"]],
        s=[callout_size],
        facecolors="none", edgecolors=INK, linewidths=1.6, zorder=5,
    )
    ax.annotate(
        "HS4 7308 — structures & parts (bridges, towers, frames):\nhigh intensity despite bulk volume",
        xy=(row["tonnes"], row["direct_intensity"]),
        xytext=(-190, 46), textcoords="offset points",
        fontsize=9, color=INK, ha="left", va="bottom",
        arrowprops=dict(arrowstyle="-", color=GREY_DARK, linewidth=0.9),
    )

    fig.legend(
        *ax.get_legend_handles_labels(),
        loc="lower center", bbox_to_anchor=(0.52, 0.1), frameon=False, fontsize=9.5,
        labelcolor=GREY_MED, handletextpad=0.5, columnspacing=1.4, ncol=3, markerscale=0.4,
    )

    add_footer(
        fig,
        source_text=(
            "Source: output/steel_clusters.csv (features/steelClusterFrozen.py)\n"
            "Canonical 35-heading set (7 near-zero exporters dropped); feature space = direct intensity + log1p(tonnes), z-scored."
        ),
        rule_y=0.075,
    )
    return fig


if __name__ == "__main__":
    fig = build()
    png, svg = save_exhibit(fig, "exhibit2_steel_inversion")
    print(png)
    print(svg)
