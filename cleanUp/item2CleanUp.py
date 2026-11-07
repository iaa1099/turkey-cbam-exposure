
"""Item 2 clean-up: Eurostat Comext DS-045409 -> Turkey->EU trade by HS4 heading."""
from pathlib import Path

import pandas as pd


def load_trade(path: str, year: int = 2024) -> pd.DataFrame:
    """Turkey->EU imports by HS4 heading, one recent full year.

    Returns one row per 4-digit heading: hs4, tonnes, value_eur.
    """
    df = pd.read_csv(path)

    # 1-4: keep only Turkey partner, target year, EU-27 aggregate reporter, HS4 rows
    df = df[
        (df["PARTNER"] == "Türkiye")
        & (df["TIME_PERIOD"] == year)
        & (df["REPORTER"].str.contains("European Union", na=False))
    ].copy()
    df["product"] = df["product"].astype(str)
    df = df[df["product"].str.len() == 4]  # drops lumped 72/73/76 chapter totals

    # 5: indicators (value + quantity) become columns
    df = df.pivot_table(
        index="product", columns="INDICATORS", values="OBS_VALUE", aggfunc="sum"
    ).reset_index()

    # 6: Comext quantity is in units of 100 kg -> tonnes
    df["tonnes"] = df["QUANTITY_IN_100KG"] / 10.0

    # 7: tidy
    df = df.rename(columns={"product": "hs4", "VALUE_IN_EUROS": "value_eur"})
    df = df[["hs4", "tonnes", "value_eur"]].sort_values("hs4").reset_index(drop=True)

    assert df["hs4"].str.len().eq(4).all(), "non-HS4 code leaked through"
    assert not df.empty, "no Turkey/EU-27 rows for that year — check filters"
    return df


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    input_path = base_dir / "data" / "item2.csv"
    output_path = base_dir / "data" / "item2_cleaned.csv"

    trade = load_trade(str(input_path), year=2024)
    trade.to_csv(output_path, index=False)
    print(f"Cleaned data saved to: {output_path}")


if __name__ == "__main__":
    main()