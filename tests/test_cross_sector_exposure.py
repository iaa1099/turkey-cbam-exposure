from pathlib import Path

from cleanUp.item1CleanUp import parse_turkiye_defaults
from cleanUp.item2CleanUp import load_trade
from features.crossSectorExposure import (
    SECTORS,
    build_cross_sector_table,
    reconcile_steel,
)

BASE_DIR = Path(__file__).resolve().parent.parent


def _build_table():
    item1_df = parse_turkiye_defaults(str(BASE_DIR / "data" / "item1.xlsx"))
    item2_df = load_trade(str(BASE_DIR / "data" / "item2.csv"), year=2024)
    return build_cross_sector_table(item1_df, item2_df)


def test_all_five_sectors_present():
    _, summary = _build_table()
    assert set(summary["sector"]) == set(SECTORS)
    assert len(summary) == 5


def test_shares_sum_to_one():
    _, summary = _build_table()
    assert abs(summary["share_of_total"].sum() - 1.0) < 1e-9


def test_steel_is_largest_sector():
    _, summary = _build_table()
    assert summary.loc[summary["sector"] == "Iron and steel", "share_of_total"].iloc[0] == summary["share_of_total"].max()


def test_cement_fallback_flagged_in_method():
    _, summary = _build_table()
    cement_method = summary.loc[summary["sector"] == "Cement", "method"].iloc[0]
    assert "fallback" in cement_method
    assert "25233000" in cement_method


def test_full_steel_reconciles_to_frozen_cleaned35():
    per_heading, _ = _build_table()
    recon = reconcile_steel(per_heading, BASE_DIR / "output" / "steel_clusters.csv")
    # the 7 dropped near-zero-exporter headings contribute ~0 exposure, so
    # full-book steel should reconcile to the frozen 35-heading book within
    # well under 1% -- this is a regression guard, not an exact-equality check
    assert abs(recon["diff_pct"]) < 0.1


def test_no_sector_silently_zeroed():
    _, summary = _build_table()
    assert (summary["exposure_tco2"] > 0).all()
    assert (summary["n_headings"] > 0).all()
