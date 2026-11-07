from pathlib import Path

from cleanUp.item1CleanUp import parse_turkiye_defaults
from cleanUp.item2CleanUp import load_trade
from features.steelFeatures import build_steel_features

BASE_DIR = Path(__file__).resolve().parent.parent


def _build_features():
    item1_df = parse_turkiye_defaults(str(BASE_DIR / "data" / "item1.xlsx"))
    item2_df = load_trade(str(BASE_DIR / "data" / "item2.csv"), year=2024)
    return build_steel_features(item1_df, item2_df)


def test_row_count_matches_steel_hs4_count():
    item1_df = parse_turkiye_defaults(str(BASE_DIR / "data" / "item1.xlsx"))
    steel = item1_df[item1_df["sector"] == "Iron and steel"].copy()
    steel_hs4_count = steel["cn_code"].str[:4].nunique()

    features = _build_features()
    assert len(features) == steel_hs4_count
    assert 35 <= len(features) <= 50


def test_direct_has_no_silent_zero_coercion():
    features = _build_features()
    # a literal 0.0 direct emission intensity for steel isn't physically real;
    # seeing one here means an N/A got coerced to 0 instead of staying NaN
    assert not (features["direct"] == 0).any()


def test_direct_shows_real_spread():
    features = _build_features()
    direct = features["direct"].dropna()
    assert direct.min() > 0
    assert direct.max() - direct.min() > 3  # observed ~0.18 to ~6.77 tCO2/t


def test_exposure_and_trade_join():
    features = _build_features()
    no_trade = features["tonnes"] == 0
    assert features["tonnes"].notna().all()  # no EU trade -> 0, never null
    assert features.loc[~no_trade, "exposure"].notna().all()
