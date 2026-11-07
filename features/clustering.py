"""Cluster steel HS4 headings on direct intensity + trade volume/value.

k-means is primary (k chosen by silhouette score, k=2..6); DBSCAN is a
density-based robustness cross-check on the same scaled features.
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cleanUp.item1CleanUp import parse_turkiye_defaults
from cleanUp.item2CleanUp import load_trade
from features.steelFeatures import build_steel_features

CLUSTER_INPUT_COLUMNS = ["direct", "tonnes", "value_eur"]
LOG_COLUMNS = ["tonnes", "value_eur"]  # heavily right-skewed; direct is not


def prepare_cluster_features(features_df: pd.DataFrame) -> np.ndarray:
    """Log1p the skewed volume/value columns, then z-score all three. Never
    include exposure — it's direct x tonnes, so clustering on it plus its own
    components would be circular."""
    X = features_df[CLUSTER_INPUT_COLUMNS].copy()
    for col in LOG_COLUMNS:
        X[col] = np.log1p(X[col])
    return StandardScaler().fit_transform(X)


def select_kmeans_k(X: np.ndarray, k_range=range(2, 7), random_state: int = 42) -> pd.DataFrame:
    """Silhouette score for each k in k_range. One row per k."""
    rows = []
    for k in k_range:
        labels = KMeans(n_clusters=k, random_state=random_state, n_init=10).fit_predict(X)
        rows.append({"k": k, "silhouette": silhouette_score(X, labels), "labels": labels})
    return pd.DataFrame(rows)


def best_kmeans(X: np.ndarray, k_range=range(2, 7), random_state: int = 42):
    """Returns (k, labels, silhouette) for the k with the highest silhouette score."""
    scores = select_kmeans_k(X, k_range, random_state)
    best = scores.loc[scores["silhouette"].idxmax()]
    return int(best["k"]), best["labels"], float(best["silhouette"])


def run_dbscan(X: np.ndarray, eps: float = 0.8, min_samples: int = 3) -> np.ndarray:
    return DBSCAN(eps=eps, min_samples=min_samples).fit_predict(X)


def cluster_table(features_df: pd.DataFrame, kmeans_labels: np.ndarray, dbscan_labels: np.ndarray) -> pd.DataFrame:
    """Per-heading table: kmeans/dbscan labels alongside direct/tonnes/exposure, sorted by kmeans cluster."""
    table = features_df[["hs4", "direct", "tonnes", "exposure"]].copy()
    table["kmeans_cluster"] = kmeans_labels
    table["dbscan_cluster"] = dbscan_labels
    return table.sort_values(["kmeans_cluster", "direct"]).reset_index(drop=True)


def cluster_summary(features_df: pd.DataFrame, kmeans_labels: np.ndarray) -> pd.DataFrame:
    """One row per k-means cluster: heading count, mean direct, mean tonnes, total exposure."""
    df = features_df.copy()
    df["cluster"] = kmeans_labels
    summary = df.groupby("cluster").agg(
        n_headings=("hs4", "count"),
        mean_direct=("direct", "mean"),
        mean_tonnes=("tonnes", "mean"),
        total_exposure=("exposure", "sum"),
    ).reset_index()
    return summary.sort_values("total_exposure", ascending=False).reset_index(drop=True)


def acute_set_agreement(features_df: pd.DataFrame, kmeans_labels: np.ndarray, dbscan_labels: np.ndarray) -> dict:
    """Compares k-means' minority (non-majority) cluster against DBSCAN's noise points."""
    hs4 = features_df["hs4"].to_numpy()
    kmeans_counts = pd.Series(kmeans_labels).value_counts()
    majority_label = kmeans_counts.idxmax()
    kmeans_acute = set(hs4[kmeans_labels != majority_label])
    dbscan_noise = set(hs4[dbscan_labels == -1])

    overlap = kmeans_acute & dbscan_noise
    union = kmeans_acute | dbscan_noise
    return {
        "kmeans_acute": sorted(kmeans_acute),
        "dbscan_noise": sorted(dbscan_noise),
        "overlap": sorted(overlap),
        "jaccard": len(overlap) / len(union) if union else 0.0,
        "kmeans_acute_covered_by_dbscan_noise": len(overlap) / len(kmeans_acute) if kmeans_acute else 0.0,
    }


VOLUME_TRANSFORMS = {
    "none": lambda x: x,
    "sqrt": np.sqrt,
    "log1p": np.log1p,
}

# Canonical steel-clustering universe: HS4 headings with negligible EU trade
# volume are excluded from cluster-structure analysis (noted as zero/negligible
# exposure, not dropped from the sector total). This is the single source of
# truth for the drop rule — the frozen clustering pipeline reuses it rather
# than re-deriving its own filter.
STEEL_DROP_TONNES_FLOOR = 1000


def drop_near_zero_exporters(features_df: pd.DataFrame, tonnes_floor: float = STEEL_DROP_TONNES_FLOOR) -> pd.DataFrame:
    return features_df[features_df["tonnes"] > tonnes_floor].reset_index(drop=True)


def prepare_diagnostic_features(filtered_df: pd.DataFrame, volume_transform: str = "sqrt") -> np.ndarray:
    """direct + tonnes only (no value_eur) for the filtered-exporters robustness check."""
    transform = VOLUME_TRANSFORMS[volume_transform]
    X = filtered_df[["direct", "tonnes"]].copy()
    X["tonnes"] = transform(X["tonnes"])
    return StandardScaler().fit_transform(X)


def diagnostic_filtered_clustering(
    features_df: pd.DataFrame,
    tonnes_floor: float = STEEL_DROP_TONNES_FLOOR,
    volume_transform: str = "sqrt",
    k_range=range(2, 6),
) -> dict:
    """Robustness check: drop near-zero-volume headings (the trivial split that
    dominates the primary 3-feature clustering), cluster the remainder on
    direct + tonnes only, and report whether an intensity-vs-volume structure
    survives or whether silhouette says there's nothing real left."""
    filtered = drop_near_zero_exporters(features_df, tonnes_floor)
    X = prepare_diagnostic_features(filtered, volume_transform)
    k, labels, silhouette = best_kmeans(X, k_range)
    summary = cluster_summary(filtered, labels)
    return {
        "n_dropped": len(features_df) - len(filtered),
        "n_remaining": len(filtered),
        "k": k,
        "silhouette": silhouette,
        "labels": labels,
        "filtered": filtered,
        "summary": summary,
        "has_real_structure": silhouette >= 0.3,
    }


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    item1_df = parse_turkiye_defaults(str(base_dir / "data" / "item1.xlsx"))
    item2_df = load_trade(str(base_dir / "data" / "item2.csv"), year=2024)
    features = build_steel_features(item1_df, item2_df)

    X = prepare_cluster_features(features)

    scores = select_kmeans_k(X)
    print("k-means silhouette by k:")
    print(scores[["k", "silhouette"]].to_string(index=False))

    k, kmeans_labels, silhouette = best_kmeans(X)
    print(f"\nchosen k = {k}, silhouette = {silhouette:.4f}")

    dbscan_labels = run_dbscan(X)
    dbscan_counts = pd.Series(dbscan_labels).value_counts().sort_index()
    print(f"\nDBSCAN cluster sizes (label -1 = noise):\n{dbscan_counts.to_string()}")

    table = cluster_table(features, kmeans_labels, dbscan_labels)
    print("\nper-heading table (sorted by k-means cluster):")
    print(table.to_string(index=False))

    summary = cluster_summary(features, kmeans_labels)
    print("\nk-means cluster summary:")
    print(summary.to_string(index=False))

    agreement = acute_set_agreement(features, kmeans_labels, dbscan_labels)
    print(f"\nk-means acute (minority) cluster headings: {agreement['kmeans_acute']}")
    print(f"DBSCAN noise headings: {agreement['dbscan_noise']}")
    print(f"overlap: {agreement['overlap']}")
    print(
        f"{agreement['kmeans_acute_covered_by_dbscan_noise']:.0%} of k-means' acute set "
        f"is also flagged as DBSCAN noise (Jaccard = {agreement['jaccard']:.2f})"
    )

    print("\n--- diagnostic: filtered-exporters robustness check ---")
    diag = diagnostic_filtered_clustering(features)
    print(
        f"dropped {diag['n_dropped']} near-zero-volume headings "
        f"(tonnes <= 1000), {diag['n_remaining']} remaining"
    )
    print(f"chosen k = {diag['k']}, silhouette = {diag['silhouette']:.4f}")
    print(diag["summary"].to_string(index=False))
    if diag["has_real_structure"]:
        print("silhouette >= 0.3: real structure survives after removing the trivial low-volume split")
    else:
        print("silhouette < 0.3: no real structure once the trivial low-volume split is removed")


if __name__ == "__main__":
    main()
