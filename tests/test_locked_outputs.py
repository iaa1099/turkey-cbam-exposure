"""Regression pins for every number in the "Locked outputs" list (repo task
spec / CLAUDE.md). Reads only the already-committed output/*.csv files — not
the gitignored raw data/ files — so this suite runs unconditionally in CI,
unlike the data-dependent tests elsewhere in tests/ (see data/README.md).

Steel's silhouette/k are recomputed here directly from the persisted
per-heading columns in output/steel_clusters.csv (direct_intensity, tonnes,
cluster_label) — the same feature space and labels
features/steelClusterFrozen.py produced them with — rather than re-running
KMeans against raw data. If these ever drift, re-run
`python -m cbam_exposure run` and compare against CLAUDE.md before updating
the numbers below.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"


@pytest.fixture(scope="module")
def steel_clusters():
    return pd.read_csv(OUTPUT_DIR / "steel_clusters.csv")


@pytest.fixture(scope="module")
def cross_sector():
    return pd.read_csv(OUTPUT_DIR / "cbam_cross_sector_exposure.csv")


@pytest.fixture(scope="module")
def grid_intensity_bases():
    return pd.read_csv(OUTPUT_DIR / "electricity_grid_intensity_bases.csv").set_index("basis")


@pytest.fixture(scope="module")
def electricity_exposure_current():
    return pd.read_csv(OUTPUT_DIR / "electricity_exposure_current.csv").iloc[0]


def test_steel_cluster_count_and_heading_count(steel_clusters):
    assert len(steel_clusters) == 35
    assert steel_clusters["cluster_label"].nunique() == 3


def test_steel_silhouette_approx_0_51(steel_clusters):
    X = steel_clusters[["direct_intensity", "tonnes"]].copy()
    X["tonnes"] = np.log1p(X["tonnes"])
    Xs = StandardScaler().fit_transform(X)
    silhouette = silhouette_score(Xs, steel_clusters["cluster_label"])
    assert abs(silhouette - 0.51) <= 0.05


def test_steel_cluster_shares_and_means(steel_clusters):
    shares = steel_clusters.groupby("cluster_label")["exposure"].sum() / steel_clusters["exposure"].sum()
    means = steel_clusters.groupby("cluster_label")["direct_intensity"].mean()

    assert shares["commodity-volume"] == pytest.approx(0.82, abs=0.02)
    assert means["commodity-volume"] == pytest.approx(2.63, abs=0.1)

    assert shares["specialty-intensity"] == pytest.approx(0.15, abs=0.02)
    assert means["specialty-intensity"] == pytest.approx(5.99, abs=0.1)

    assert shares["moderate-middle"] == pytest.approx(0.03, abs=0.01)


def test_steel_plus_cement_approx_90_6_pct(cross_sector):
    steel_and_cement = cross_sector.loc[
        cross_sector["sector"].isin(["Iron and steel", "Cement"]), "share_of_total"
    ].sum()
    assert steel_and_cement == pytest.approx(0.906, abs=0.01)


def test_grid_intensity_two_bases_and_delta(grid_intensity_bases):
    benchmark = grid_intensity_bases.loc["ember_iea_benchmark", "intensity_tco2_per_mwh"]
    ncg_adjusted = grid_intensity_bases.loc["grid_intensity_ncg_adjusted", "intensity_tco2_per_mwh"]
    delta = grid_intensity_bases.loc["geothermal_ncg_delta", "intensity_tco2_per_mwh"]

    assert benchmark == pytest.approx(0.4425, abs=0.0001)
    assert ncg_adjusted == pytest.approx(0.4681, abs=0.0001)
    assert delta / benchmark == pytest.approx(0.058, abs=0.005)


def test_exported_electricity_approx_2_54m_mwh_gross_provisional(electricity_exposure_current):
    assert electricity_exposure_current["exported_mwh"] == pytest.approx(2_543_000, rel=0.001)
    assert electricity_exposure_current["exported_mwh_tr_gr"] + electricity_exposure_current["exported_mwh_tr_bg"] \
        == electricity_exposure_current["exported_mwh"]
    assert "PROVISIONAL" in electricity_exposure_current["exported_mwh_status"]


def test_electricity_exposure_lower_bound_approx_1_2_mtco2_provisional(electricity_exposure_current):
    exposure_tco2 = electricity_exposure_current["exposure_tco2"]
    assert exposure_tco2 == pytest.approx(1_200_000, rel=0.03)
    assert "PROVISIONAL" in electricity_exposure_current["exported_mwh_status"]
