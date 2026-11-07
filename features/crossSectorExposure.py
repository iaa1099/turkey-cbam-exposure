"""Cross-sector CBAM exposure table: all five direct-emissions goods.

Backs the locked "steel 68.97% / steel+cement 90.59%" headline (CLAUDE.md,
"Locked decisions" -- adopted 2026-07-18, superseding the prior 68%/91% prose
figure) with a persisted CSV. Reuses the existing CN->sector mapping
(item1CleanUp.parse_turkiye_defaults's `sector` column) and the existing HS4
trade join (item2CleanUp.load_trade) -- the identical method steelFeatures.py
already uses for steel, applied to every sector so shares are computed on a
like-for-like basis. Electricity is excluded: it is a separate good scored in
tCO2/MWh against export volume, not direct x tonnes, and is not part of this
goods table (see features/electricityGood.py).
"""
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cleanUp.item1CleanUp import parse_turkiye_defaults
from cleanUp.item2CleanUp import load_trade

SECTORS = ["Iron and steel", "Cement", "Aluminium", "Fertilisers", "Hydrogen"]

# The pre-2026-07-18 prose figure (CLAUDE.md, no backing CSV) -- kept only as
# a historical divergence record, NOT the current locked source of truth.
# The computed shares in this module's output ARE now locked (see CLAUDE.md).
PRIOR_PROSE_SHARES = {
    "Iron and steel": 0.68,
    "Cement": 0.23,
    "Aluminium": 0.07,
    "Fertilisers": 0.02,
    "Hydrogen": 0.00,
}

METHOD = (
    "direct_default (mean of matching CN8/CN6 rows, item1CleanUp.parse_turkiye_defaults) "
    "x comext_tonnes (item2CleanUp.load_trade), joined at HS4 -- identical method to "
    "features/steelFeatures.py's steel exposure, applied per-sector"
)
CEMENT_FALLBACK_NOTE = (
    " -- cement fallback: 7 of 8 Turkiye-sheet CN codes showed '-' for direct emissions "
    "and were filled from the _Other Countries and Territorie sheet's generic EU default "
    "(item1CleanUp.parse_turkiye_defaults, is_fallback flag); only CN 25233000 (Aluminous "
    "cement) has a Turkiye-specific direct value. Both HS4 headings (2507, 2523) contain "
    "at least one fallback-sourced row. Cement is therefore the least Turkiye-specific "
    "sector figure of the five -- flagged for a paper footnote."
)


def build_sector_features(item1_df: pd.DataFrame, item2_df: pd.DataFrame, sector: str) -> pd.DataFrame:
    """One row per HS4 heading in `sector`: direct, tonnes, value_eur, exposure.

    Same method as steelFeatures.build_steel_features (mean direct per HS4,
    left-merge onto trade, tonnes/value fillna 0, exposure = direct x tonnes),
    generalized to any sector in item1_df['sector'].
    """
    rows = item1_df[item1_df["sector"] == sector].copy()
    rows["hs4"] = rows["cn_code"].str[:4]

    agg = rows.groupby("hs4").agg(
        direct=("direct", "mean"),
        is_fallback=("is_fallback", "any"),
    ).reset_index()

    features = agg.merge(item2_df, on="hs4", how="left")
    features[["tonnes", "value_eur"]] = features[["tonnes", "value_eur"]].fillna(0.0)
    features["exposure"] = features["direct"] * features["tonnes"]
    features["sector"] = sector

    return features[["sector", "hs4", "direct", "tonnes", "value_eur", "exposure", "is_fallback"]]


def build_cross_sector_table(item1_df: pd.DataFrame, item2_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (per_heading, per_sector_summary) across all five direct-emissions goods."""
    per_heading = pd.concat(
        [build_sector_features(item1_df, item2_df, s) for s in SECTORS],
        ignore_index=True,
    )

    summary = per_heading.groupby("sector").agg(
        n_headings=("hs4", "count"),
        total_tonnes=("tonnes", "sum"),
        exposure_tco2=("exposure", "sum"),
        n_fallback_headings=("is_fallback", "sum"),
    ).reindex(SECTORS).reset_index()

    total_exposure = summary["exposure_tco2"].sum()
    summary["share_of_total"] = summary["exposure_tco2"] / total_exposure
    summary["method"] = METHOD
    summary.loc[summary["sector"] == "Cement", "method"] += CEMENT_FALLBACK_NOTE

    return per_heading, summary


def reconcile_steel(per_heading: pd.DataFrame, frozen_path: Path) -> dict:
    """Full-book (all HS4 headings) steel exposure vs the frozen 35-heading
    clustered book persisted in output/steel_clusters.csv. The 7 dropped
    headings are near-zero exporters (tonnes <= 1000), so the two totals
    should reconcile within rounding -- verified, not assumed."""
    full_steel_total = per_heading.loc[per_heading["sector"] == "Iron and steel", "exposure"].sum()
    frozen_total = pd.read_csv(frozen_path)["exposure"].sum()
    diff = full_steel_total - frozen_total
    return {
        "full_steel_total": full_steel_total,
        "frozen_cleaned35_total": frozen_total,
        "diff_tco2": diff,
        "diff_pct": 100 * diff / full_steel_total,
    }


def compare_to_prior_prose(summary: pd.DataFrame, tolerance_pp: float = 1.0) -> pd.DataFrame:
    """Historical record: computed shares vs. the pre-2026-07-18 prose figure
    that had no backing CSV. Not a validation against a current locked value --
    the computed shares here are themselves now the locked figure."""
    comparison = summary[["sector", "share_of_total"]].copy()
    comparison["prior_prose_share"] = comparison["sector"].map(PRIOR_PROSE_SHARES)
    comparison["computed_pct"] = (comparison["share_of_total"] * 100).round(2)
    comparison["prior_prose_pct"] = (comparison["prior_prose_share"] * 100).round(2)
    comparison["delta_pp"] = (comparison["computed_pct"] - comparison["prior_prose_pct"]).round(2)
    comparison["diverges"] = comparison["delta_pp"].abs() > tolerance_pp
    return comparison[["sector", "prior_prose_pct", "computed_pct", "delta_pp", "diverges"]]


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    item1_df = parse_turkiye_defaults(str(base_dir / "data" / "item1.xlsx"))
    item2_df = load_trade(str(base_dir / "data" / "item2.csv"), year=2024)

    per_heading, summary = build_cross_sector_table(item1_df, item2_df)

    print("=== Cross-sector CBAM exposure (direct-emissions only, full per-sector book) ===")
    print(summary.to_string(index=False))

    steel_and_cement = summary.loc[summary["sector"].isin(["Iron and steel", "Cement"]), "share_of_total"].sum()
    print(f"\nsteel + cement share of total: {steel_and_cement * 100:.2f}%")

    print("\n=== Steel reconciliation: full book vs frozen cleaned-35 ===")
    recon = reconcile_steel(per_heading, base_dir / "output" / "steel_clusters.csv")
    for k, v in recon.items():
        print(f"{k}: {v}")

    print("\n=== Computed vs. prior (pre-2026-07-18) prose figure -- historical record ===")
    comparison = compare_to_prior_prose(summary)
    print(comparison.to_string(index=False))

    if comparison["diverges"].any():
        diverged = comparison.loc[comparison["diverges"], "sector"].tolist()
        print(f"\n{diverged} moved by more than 1pp against the prior prose figure. "
              "ADOPTED: the computed shares in this table are now the locked figure "
              "in CLAUDE.md (prior prose figure superseded, kept only as a divergence record).")
    else:
        print("\nEvery sector matches the prior prose figure within ~1pp.")

    output_path = base_dir / "output" / "cbam_cross_sector_exposure.csv"
    summary.to_csv(output_path, index=False)
    print(f"\nWritten: {output_path}")


if __name__ == "__main__":
    main()
