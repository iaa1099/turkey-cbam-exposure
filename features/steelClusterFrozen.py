"""Frozen steel HS4 clustering: fixed k, fixed features, deterministic labels.

This is NOT the exploratory pipeline (see clustering.py, which silhouette-
sweeps k and is the right place to re-explore hyperparameters). This module
locks them: k=3, direct + log1p(tonnes) only, random_state fixed. Do not
re-run a k-sweep here — see CLAUDE.md "Clustering (steel) — FROZEN".

Guardrail: steel exposure is direct-emissions and grid-independent. This
module must never import or compute grid carbon intensity.
"""
from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cleanUp.item1CleanUp import parse_turkiye_defaults
from cleanUp.item2CleanUp import load_trade
from features.clustering import STEEL_DROP_TONNES_FLOOR, drop_near_zero_exporters
from features.steelFeatures import build_steel_features

K = 3
RANDOM_STATE = 42
SILHOUETTE_EXPECTED = 0.51
SILHOUETTE_TOLERANCE = 0.05

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "output" / "steel_clusters.csv"


@dataclass(frozen=True)
class FrozenClusterResult:
    assignments: pd.DataFrame  # hs4, description, direct_intensity, tonnes, exposure, cluster_label
    summary: pd.DataFrame      # cluster_label, n_headings, exposure_share, mean_direct, mean_tonnes
    k: int
    silhouette: float
    n_dropped: int


def hs4_descriptions(item1_df: pd.DataFrame) -> pd.Series:
    """One representative description per HS4 heading: the heading-level row
    if the source has one, else the first child CN code's description."""
    df = item1_df.copy()
    df["hs4"] = df["cn_code"].str[:4]
    df["is_heading_level"] = df["cn_code"] == df["hs4"]
    df = df.sort_values(["hs4", "is_heading_level", "cn_code"], ascending=[True, False, True])
    return df.groupby("hs4")["description"].first()


def prepare_frozen_features(filtered_df: pd.DataFrame) -> np.ndarray:
    """direct (as-is) + log1p(tonnes), both standardised. No value_eur, no
    exposure, no grid intensity — direct + trade volume only."""
    X = filtered_df[["direct", "tonnes"]].copy()
    X["tonnes"] = np.log1p(X["tonnes"])
    return StandardScaler().fit_transform(X)


def assign_semantic_labels(raw_labels: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Maps KMeans' arbitrary integer labels to fixed semantic names by each
    cluster's centroid position in the standardised feature space — so the
    label assigned to a given heading is independent of KMeans' internal label
    numbering and of input row order.

    highest-tonnes centroid   -> commodity-volume
    highest-direct centroid (of what's left) -> specialty-intensity
    remaining                 -> moderate-middle
    """
    centroids = pd.DataFrame(X, columns=["direct_z", "tonnes_z"])
    centroids["_raw_label"] = raw_labels
    centroid_means = centroids.groupby("_raw_label")[["direct_z", "tonnes_z"]].mean()

    commodity_label = centroid_means["tonnes_z"].idxmax()
    remaining = centroid_means.drop(index=commodity_label)
    specialty_label = remaining["direct_z"].idxmax()
    moderate_label = remaining.drop(index=specialty_label).index[0]

    mapping = {
        commodity_label: "commodity-volume",
        specialty_label: "specialty-intensity",
        moderate_label: "moderate-middle",
    }
    return np.array([mapping[label] for label in raw_labels])


def build_frozen_steel_clusters(item1_df: pd.DataFrame, item2_df: pd.DataFrame) -> FrozenClusterResult:
    features = build_steel_features(item1_df, item2_df)
    filtered = drop_near_zero_exporters(features, STEEL_DROP_TONNES_FLOOR)

    X = prepare_frozen_features(filtered)
    raw_labels = KMeans(n_clusters=K, random_state=RANDOM_STATE, n_init=10).fit_predict(X)
    silhouette = silhouette_score(X, raw_labels)
    cluster_label = assign_semantic_labels(raw_labels, X)

    descriptions = hs4_descriptions(item1_df)
    assignments = filtered[["hs4", "direct", "tonnes", "exposure"]].copy()
    assignments["description"] = assignments["hs4"].map(descriptions)
    assignments["cluster_label"] = cluster_label
    assignments = assignments.rename(columns={"direct": "direct_intensity"})
    assignments = assignments[
        ["hs4", "description", "direct_intensity", "tonnes", "exposure", "cluster_label"]
    ].sort_values("cluster_label").reset_index(drop=True)

    total_steel_exposure = features["exposure"].sum()
    summary = assignments.groupby("cluster_label").agg(
        n_headings=("hs4", "count"),
        mean_direct=("direct_intensity", "mean"),
        mean_tonnes=("tonnes", "mean"),
        cluster_exposure=("exposure", "sum"),
    ).reset_index()
    summary["exposure_share"] = summary["cluster_exposure"] / total_steel_exposure
    summary = summary.drop(columns="cluster_exposure")
    summary = summary[["cluster_label", "n_headings", "exposure_share", "mean_direct", "mean_tonnes"]]

    return FrozenClusterResult(
        assignments=assignments,
        summary=summary,
        k=K,
        silhouette=float(silhouette),
        n_dropped=len(features) - len(filtered),
    )


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    item1_df = parse_turkiye_defaults(str(base_dir / "data" / "item1.xlsx"))
    item2_df = load_trade(str(base_dir / "data" / "item2.csv"), year=2024)

    result = build_frozen_steel_clusters(item1_df, item2_df)

    print(f"k = {result.k} (fixed), silhouette = {result.silhouette:.4f}")
    print(f"dropped {result.n_dropped} near-zero-volume headings (tonnes <= {STEEL_DROP_TONNES_FLOOR})")

    print("\nper-heading assignments:")
    print(result.assignments.to_string(index=False))

    print("\ncluster summary:")
    print(result.summary.to_string(index=False))

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    result.assignments.to_csv(OUTPUT_PATH, index=False)
    print(f"\nassignments written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
