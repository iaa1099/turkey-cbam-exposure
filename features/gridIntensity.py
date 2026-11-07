"""Turkey grid carbon intensity, generation-weighted across fuels.

This computes the NCG-adjusted basis (geothermal costed at its real 0.887
tCO2/MWh, not the standard-accounting ~0 convention) — see
features/electricityGood.py for the full two-basis structure: this figure
alongside the named EMBER_IEA_BENCHMARK (0.4425, geothermal-zero), and the
geothermal_ncg_delta() between them, which is the citable finding, not an
error to resolve. Factors here are kept in sync with that module's
TURKEY_EMISSION_FACTORS (Sözen et al. for lignite; Herrera Martinez et al.
(2016) for geothermal); if you change one, change both.
"""
from pathlib import Path

import pandas as pd

# tCO2/MWh by fuel column in item3.csv. Uluslararası (imports) and Atık Isı
# (waste heat) are deliberately excluded, not zeroed.
EMISSION_FACTORS = {
    "Doğal Gaz": 0.37,       # natural gas
    "LNG": 0.37,
    "Nafta": 0.37,           # naphtha
    "Linyit": 1.08,          # lignite, Turkey-specific (Sözen et al.), not generic 1.10
    "Taş Kömür": 0.90,       # hard coal
    "İthal Kömür": 0.90,     # imported coal
    "Asfaltit Kömür": 0.90,  # asphaltite coal
    "Fuel Oil": 0.65,
    "Barajlı": 0.0,          # hydro, dam
    "Akarsu": 0.0,           # hydro, run-of-river
    "Rüzgar": 0.0,           # wind
    "Güneş": 0.0,            # solar
    "Jeotermal": 0.887,      # geothermal, NOT zero — Turkey degasses reservoir CO2 (Herrera Martinez et al., 2016)
    "Biyokütle": 0.0,        # biomass
}


def turkey_grid_intensity(grid_df: pd.DataFrame) -> float:
    """Generation-weighted grid carbon intensity, in tCO2/MWh."""
    fuel_totals = grid_df[list(EMISSION_FACTORS)].sum()
    emissions = sum(fuel_totals[fuel] * factor for fuel, factor in EMISSION_FACTORS.items())
    total_generation = fuel_totals.sum()
    return emissions / total_generation


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    grid_df = pd.read_csv(base_dir / "data" / "item3.csv")
    intensity = turkey_grid_intensity(grid_df)
    print(f"Turkey 2024 grid carbon intensity: {intensity:.4f} tCO2/MWh")


if __name__ == "__main__":
    main()
