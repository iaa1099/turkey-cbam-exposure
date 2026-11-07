from pathlib import Path

import numpy as np
import pytest

from cleanUp.item1CleanUp import parse_turkiye_defaults
from cleanUp.item2CleanUp import load_trade
from features.clustering import (
    best_kmeans,
    diagnostic_filtered_clustering,
    prepare_cluster_features,
    run_dbscan,
)
from features.steelFeatures import build_steel_features

BASE_DIR = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.skipif(
    not (BASE_DIR / "data" / "item1.xlsx").exists() or not (BASE_DIR / "data" / "item2.csv").exists(),
    reason="raw data files not committed (gitignored) — run locally with data/ populated, see data/README.md",
)


def _features():
    item1_df = parse_turkiye_defaults(str(BASE_DIR / "data" / "item1.xlsx"))
    item2_df = load_trade(str(BASE_DIR / "data" / "item2.csv"), year=2024)
    return build_steel_features(item1_df, item2_df)


def test_kmeans_clustering_is_non_trivial():
    features = _features()
    X = prepare_cluster_features(features)
    _, labels, _ = best_kmeans(X)

    largest_cluster = np.bincount(labels).max()
    assert largest_cluster <= 0.85 * len(features)


def test_silhouette_score_reported_and_positive():
    features = _features()
    X = prepare_cluster_features(features)
    k, labels, silhouette = best_kmeans(X)

    assert k in range(2, 7)
    assert silhouette > 0
    assert len(labels) == len(features)


def test_every_heading_labeled_and_dbscan_runs():
    features = _features()
    X = prepare_cluster_features(features)
    _, kmeans_labels, _ = best_kmeans(X)
    dbscan_labels = run_dbscan(X)

    assert not np.any(np.isnan(kmeans_labels.astype(float)))
    assert len(kmeans_labels) == len(features)
    assert len(dbscan_labels) == len(features)


def test_diagnostic_filtered_clustering_drops_near_zero_exporters_and_finds_structure():
    features = _features()
    diag = diagnostic_filtered_clustering(features)

    assert diag["n_dropped"] == 7
    assert diag["n_remaining"] == len(features) - 7
    assert diag["silhouette"] > 0.3
    assert diag["has_real_structure"]
    assert len(diag["labels"]) == diag["n_remaining"]
