"""Steel HS4 feature matrix: direct-emissions CBAM exposure + trade."""
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cleanUp.item1CleanUp import parse_turkiye_defaults
from cleanUp.item2CleanUp import load_trade


def build_steel_features(item1_df: pd.DataFrame, item2_df: pd.DataFrame) -> pd.DataFrame:
    """One row per steel HS4 heading: direct, tonnes, value_eur, exposure.

    exposure = direct x tonnes. EU CBAM defaults report indirect emissions as
    N/A for steel at HS4 granularity, so this is a direct-emissions-only
    exposure model — no indirect, no grid factor, no gap.
    """
    steel = item1_df[item1_df["sector"] == "Iron and steel"].copy()
    steel["hs4"] = steel["cn_code"].str[:4]

    # mean(), not fillna: a heading with no non-N/A direct value in any of its
    # CN8/CN6 rows must surface as NaN, not silently become 0.
    agg = steel.groupby("hs4").agg(direct=("direct", "mean")).reset_index()

    features = agg.merge(item2_df, on="hs4", how="left")
    features[["tonnes", "value_eur"]] = features[["tonnes", "value_eur"]].fillna(0.0)
    features["exposure"] = features["direct"] * features["tonnes"]

    return features[["hs4", "direct", "tonnes", "value_eur", "exposure"]]


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    item1_df = parse_turkiye_defaults(str(base_dir / "data" / "item1.xlsx"))
    item2_df = load_trade(str(base_dir / "data" / "item2.csv"), year=2024)

    features = build_steel_features(item1_df, item2_df)

    print(features.to_string(index=False))
    print()
    print(features.describe())
    print(f"\nrow count: {len(features)}")


if __name__ == "__main__":
    main()
