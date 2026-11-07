from pathlib import Path

import pytest

from cleanUp.item1CleanUp import parse_turkiye_defaults
from cleanUp.item2CleanUp import load_trade
from features.steelClusterFrozen import (
    K,
    SILHOUETTE_EXPECTED,
    SILHOUETTE_TOLERANCE,
    build_frozen_steel_clusters,
)

BASE_DIR = Path(__file__).resolve().parent.parent
EXPECTED_DROPPED_HS4 = {"7201", "7203", "7206", "7218", "7221", "7223", "7301"}

pytestmark = pytest.mark.skipif(
    not (BASE_DIR / "data" / "item1.xlsx").exists() or not (BASE_DIR / "data" / "item2.csv").exists(),
    reason="raw data files not committed (gitignored) — run locally with data/ populated, see data/README.md",
)


def _result():
    item1_df = parse_turkiye_defaults(str(BASE_DIR / "data" / "item1.xlsx"))
    item2_df = load_trade(str(BASE_DIR / "data" / "item2.csv"), year=2024)
    return build_frozen_steel_clusters(item1_df, item2_df)


def test_drop_list_matches_canonical_rule():
    item1_df = parse_turkiye_defaults(str(BASE_DIR / "data" / "item1.xlsx"))
    item2_df = load_trade(str(BASE_DIR / "data" / "item2.csv"), year=2024)
    from features.steelFeatures import build_steel_features

    full = build_steel_features(item1_df, item2_df)
    result = build_frozen_steel_clusters(item1_df, item2_df)

    assert result.n_dropped == 7
    kept_hs4 = set(result.assignments["hs4"])
    dropped_hs4 = set(full["hs4"]) - kept_hs4
    assert dropped_hs4 == EXPECTED_DROPPED_HS4


def test_k_is_fixed_at_three():
    result = _result()
    assert result.k == K == 3
    assert result.assignments["cluster_label"].nunique() == 3


def test_silhouette_regression_guard():
    result = _result()
    assert abs(result.silhouette - SILHOUETTE_EXPECTED) <= SILHOUETTE_TOLERANCE


def test_semantic_labels_match_centroid_ranking():
    result = _result()
    summary = result.summary.set_index("cluster_label")

    assert summary["mean_tonnes"].idxmax() == "commodity-volume"
    assert summary["mean_direct"].idxmax() == "specialty-intensity"
    assert set(summary.index) == {"commodity-volume", "specialty-intensity", "moderate-middle"}


def test_labels_reproducible_across_runs():
    item1_df = parse_turkiye_defaults(str(BASE_DIR / "data" / "item1.xlsx"))
    item2_df = load_trade(str(BASE_DIR / "data" / "item2.csv"), year=2024)

    run_a = build_frozen_steel_clusters(item1_df, item2_df)
    run_b = build_frozen_steel_clusters(item1_df, item2_df)

    a = run_a.assignments.sort_values("hs4").reset_index(drop=True)
    b = run_b.assignments.sort_values("hs4").reset_index(drop=True)
    assert (a["cluster_label"] == b["cluster_label"]).all()


def test_module_never_touches_grid_intensity():
    source = Path("features/steelClusterFrozen.py").read_text()
    assert "gridIntensity" not in source
    assert "grid_intensity" not in source


def test_assignment_columns_and_exposure_shares_sum_to_one():
    result = _result()
    assert list(result.assignments.columns) == [
        "hs4", "description", "direct_intensity", "tonnes", "exposure", "cluster_label",
    ]
    assert result.assignments["description"].notna().all()
    # shares are of TOTAL steel exposure (all 42 headings), so the 7 dropped
    # near-zero-volume headings' tiny combined share is the only gap to 1.0
    assert 0.99 < result.summary["exposure_share"].sum() < 1.0
