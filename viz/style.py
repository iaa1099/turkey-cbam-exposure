"""Shared style module for the CBAM Implications exhibits.

Extracted from Report_Design_System.pdf: pine-green accent used sparingly on
the one element each chart wants the eye to land on, everything else
greyscale; sans-serif, left-aligned type; minimal chrome (no borders, no
gridlines unless load-bearing, direct labels over legends, thin single axis
lines). Define once here, reuse across all four exhibits.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# --- Palette -----------------------------------------------------------
PINE_GREEN = "#1F4632"       # accent — sparingly, one element-group per chart
PINE_GREEN_PALE = "#DCE6E1"  # accent tint, for shaded regions under the accent line/bar
INK = "#1A1A1A"              # near-black text (titles)
GREY_DARK = "#595959"        # secondary text needing more weight (bold grey labels)
GREY_MED = "#8C8C8C"         # subtitle / source / axis tick text
GREY_LIGHT = "#D3D3D3"       # non-accent bars / secondary marks
GREY_PALE = "#E8E8E8"        # chrome: baselines, faint fills
GREY_AXIS = "#BFBFBF"        # thin axis lines

FONT_STACK = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": FONT_STACK,
        "text.color": INK,
        "axes.edgecolor": GREY_AXIS,
        "axes.labelcolor": GREY_MED,
        "xtick.color": GREY_MED,
        "ytick.color": GREY_MED,
        "svg.fonttype": "none",
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    }
)

OUTDIR = "output/exhibits"


def _tracked(text):
    """Approximate letter-spacing (no native support in matplotlib) for
    small-caps eyebrow text, e.g. 'CBAM EXPOSURE MODEL'."""
    return " ".join(text.upper())


def new_exhibit(figsize=(9.2, 5.8)):
    fig = plt.figure(figsize=figsize, dpi=300)
    return fig


def add_header(fig, eyebrow, title, subtitle, header_top=0.965, left=0.07, right=0.96):
    """Overline / title / subtitle block, matching the PDF's masthead."""
    fig.text(
        left, header_top, _tracked(eyebrow),
        fontsize=8.5, color=GREY_MED, weight="bold", ha="left", va="top",
    )
    fig.text(
        left, header_top - 0.045, title,
        fontsize=15.5, color=INK, weight="bold", ha="left", va="top",
        wrap=True,
    )
    fig.text(
        left, header_top - 0.115, subtitle,
        fontsize=10, color=GREY_MED, ha="left", va="top",
    )
    return left, right


def add_footer(fig, source_text, footnote=None, left=0.07, right=0.96, rule_y=0.11):
    """Thin rule + source line (+ optional footnote above it), matching the
    PDF's footer treatment. Reserves vertical room per text line so multi-line
    source/footnote strings never clip past the figure's bottom edge."""
    fig.add_artist(
        Line2D([left, right], [rule_y, rule_y], transform=fig.transFigure,
               color=GREY_PALE, linewidth=1.0)
    )
    line_h = 0.028
    y = rule_y - 0.032
    if footnote:
        fig.text(left, y, footnote, fontsize=8, color=GREY_MED, ha="left", va="top", style="italic")
        y -= line_h * (footnote.count("\n") + 1) + 0.014
    fig.text(left, y, source_text, fontsize=8, color=GREY_MED, ha="left", va="top")


def style_axis(ax, left_spine=True, bottom_spine=True, hide_y_ticks=False):
    """Minimal chrome: no top/right spines, thin remaining spines, recessive
    tick text, no gridlines by default."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(left_spine)
    ax.spines["bottom"].set_visible(bottom_spine)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GREY_AXIS)
        ax.spines[s].set_linewidth(0.9)
    ax.tick_params(colors=GREY_MED, labelsize=9.5, length=3)
    if hide_y_ticks:
        ax.tick_params(axis="y", length=0)
    ax.grid(False)


def save_exhibit(fig, name):
    """Export 300 dpi PNG and SVG to output/exhibits/."""
    import os

    os.makedirs(OUTDIR, exist_ok=True)
    png_path = os.path.join(OUTDIR, f"{name}.png")
    svg_path = os.path.join(OUTDIR, f"{name}.svg")
    fig.savefig(png_path, dpi=300)
    fig.savefig(svg_path)
    plt.close(fig)
    return png_path, svg_path
