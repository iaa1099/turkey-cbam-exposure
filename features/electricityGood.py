"""Electricity good: CBAM exposure from Turkey's grid carbon intensity.

Fully separate from the steel book. The renewable-generation link lives here
ONLY — this module must never import, read, or modify anything in
features/steelFeatures.py, features/clustering.py, or features/steelClusterFrozen.py.

TWO ACCOUNTING BASES, not one number:
  - EMBER_IEA_BENCHMARK (0.4425 tCO2/MWh): standard grid-carbon accounting,
    which omits geothermal non-condensable-gas (NCG) reservoir degassing
    (geothermal treated as ~0). This is a real, citable external benchmark —
    not an error, not superseded. Kept and cited.
  - grid_intensity_ncg_adjusted (~0.4681 tCO2/MWh): our bottom-up build,
    same generation mix, but geothermal costed at its real Turkey-specific
    factor (0.887 — see TURKEY_EMISSION_FACTORS). This is the OPERATIVE
    figure for electricity_exposure() and the renewable-share sweep.

The ~5.8% gap between them is a FINDING, not a discrepancy to resolve:
standard accounting understates Turkey's grid carbon intensity by omitting
geothermal NCG. validate_against_benchmark() checks that forcing geothermal
to 0 in our own build reproduces the benchmark — confirming the gap is
attributable to the geothermal treatment and not a mix/methodology error
elsewhere. See geothermal_ncg_delta() for the named, citable result.
"""
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

# Named external benchmark (Ember/IEA convention): geothermal ~0, standard
# NCG-omitting accounting. NOT superseded, NOT an error — a different,
# citable accounting basis. Do not delete or treat as legacy.
EMBER_IEA_BENCHMARK = 0.4425
BENCHMARK_TOLERANCE = 0.02  # +/- 2%, for the geothermal-zero validation run


@dataclass(frozen=True)
class EmissionFactor:
    tco2_per_mwh: float
    source: str


# Turkey-specific per-fuel emission factors. Every entry is sourced; fuels
# where the standard "renewables = 0 direct" convention would be wrong for
# Turkey are called out explicitly rather than defaulted.
TURKEY_EMISSION_FACTORS = {
    "Doğal Gaz": EmissionFactor(
        0.37,
        "IPCC/IEA generic natural gas combustion factor; corroborated by "
        "Sözen et al., Energy Policy (~2011-2012), 'Carbon dioxide emission "
        "from the Turkish electricity sector and its mitigation options', "
        "which independently estimates 0.374 tCO2/MWh for Turkish gas-fired "
        "generation specifically.",
    ),
    "LNG": EmissionFactor(0.37, "As natural gas — same combustion chemistry."),
    "Nafta": EmissionFactor(0.37, "As natural gas — light distillate, comparable carbon content."),
    "Linyit": EmissionFactor(
        1.08,
        "Turkey-specific domestic low-calorific lignite, NOT the generic "
        "IPCC global default. Sözen et al., Energy Policy (~2011-2012) "
        "empirically estimate 1080 kg CO2/MWh (1.08 tCO2/MWh) for the "
        "Turkish lignite fleet, reflecting Turkey's low-grade domestic "
        "lignite (net calorific value ~1,000-2,200 kcal/kg average, per "
        "Turkish Coal Enterprise / 'Coal power in Turkey' figures).",
    ),
    "Taş Kömür": EmissionFactor(0.90, "IPCC/IEA generic hard coal combustion factor."),
    "İthal Kömür": EmissionFactor(0.90, "IPCC/IEA generic imported (hard) coal combustion factor."),
    "Asfaltit Kömür": EmissionFactor(
        0.90,
        "IPCC/IEA generic hard-coal-equivalent factor applied to asphaltite "
        "coal; no Turkey-specific asphaltite figure was located.",
    ),
    "Fuel Oil": EmissionFactor(0.65, "IPCC/IEA generic fuel oil combustion factor."),
    "Barajlı": EmissionFactor(0.0, "Hydro (dam). Operational direct-emissions convention: 0."),
    "Akarsu": EmissionFactor(0.0, "Hydro (run-of-river). Operational direct-emissions convention: 0."),
    "Rüzgar": EmissionFactor(0.0, "Wind. Operational direct-emissions convention: 0."),
    "Güneş": EmissionFactor(0.0, "Solar. Operational direct-emissions convention: 0."),
    "Jeotermal": EmissionFactor(
        0.887,
        "NOT zero — Turkish geothermal reservoirs (concentrated in Western "
        "Turkey: Kızıldere, Germencik, etc.) release substantial reservoir "
        "CO2 through non-condensable gas (NCG) venting during power "
        "generation. Herrera Martinez et al. (2016), weighted average of "
        "887 g CO2/kWh across 12 Turkish plants, 2015 data — this is ~7x "
        "the ~121 g/kWh global average cited in the same literature. "
        "VINTAGE FLAG (footnote-tier, not blocking): the Turkish geothermal "
        "fleet has grown materially since 2015, and the literature notes "
        "the factor evolves over a well's lifetime (NCG concentration "
        "typically declines as reservoir gas dilutes) — this figure should "
        "be treated as a sensitivity, not a fixed constant, if a more "
        "recent fleet-weighted estimate becomes available.",
    ),
    "Biyokütle": EmissionFactor(
        0.0,
        "Biomass — treated as biogenic/carbon-neutral by standard grid-"
        "accounting convention (combustion CO2 not counted against the "
        "generator). No Turkey-specific override located.",
    ),
}
# Uluslararası (imports) and Atık Isı (waste heat) excluded entirely — not
# domestic generation.


def load_generation_mix(item3_df: pd.DataFrame) -> pd.Series:
    """Annual generation total (MWh) per fuel column, for the fuels in
    TURKEY_EMISSION_FACTORS only."""
    fuel_cols = list(TURKEY_EMISSION_FACTORS)
    return item3_df[fuel_cols].sum()


def grid_intensity(mix: pd.Series, factors: dict = TURKEY_EMISSION_FACTORS) -> float:
    """Generation-weighted grid carbon intensity, in tCO2/MWh. Pure function
    of the generation mix and the factor mapping — no file I/O."""
    emissions = sum(mix[fuel] * factors[fuel].tco2_per_mwh for fuel in factors)
    return emissions / mix.sum()


def grid_intensity_ncg_adjusted(mix: pd.Series) -> float:
    """The operative figure: real generation mix, geothermal costed at its
    true Turkey-specific factor (0.887, NCG-inclusive). This is what feeds
    electricity_exposure() and the renewable-share sweep."""
    return grid_intensity(mix, TURKEY_EMISSION_FACTORS)


def validate_against_benchmark(mix: pd.Series) -> dict:
    """Forces geothermal to 0 (matching the Ember/IEA benchmark's NCG-omitting
    convention) and checks that OUR build reproduces EMBER_IEA_BENCHMARK
    within tolerance. This does not compare the two accounting bases against
    each other (they're expected to differ — that's the finding); it checks
    that our mix/other-factors are sound. Does not raise — the caller must
    check within_tolerance and stop if False, per the "do not proceed past a
    failed validation" rule."""
    geothermal_zero_factors = dict(TURKEY_EMISSION_FACTORS)
    geothermal_zero_factors["Jeotermal"] = EmissionFactor(0.0, "forced to 0 for benchmark validation only")

    computed = grid_intensity(mix, geothermal_zero_factors)
    gap = computed - EMBER_IEA_BENCHMARK
    relative_gap = gap / EMBER_IEA_BENCHMARK
    return {
        "computed": computed,
        "benchmark": EMBER_IEA_BENCHMARK,
        "gap": gap,
        "relative_gap": relative_gap,
        "within_tolerance": abs(relative_gap) <= BENCHMARK_TOLERANCE,
    }


def geothermal_ncg_delta(ncg_adjusted: float, benchmark: float = EMBER_IEA_BENCHMARK) -> dict:
    """Named, citable result: the gap between the two accounting bases,
    attributed to omitted geothermal NCG degassing."""
    delta = ncg_adjusted - benchmark
    relative = delta / benchmark
    return {
        "ember_iea_benchmark": benchmark,
        "grid_intensity_ncg_adjusted": ncg_adjusted,
        "delta_tco2_per_mwh": delta,
        "delta_relative": relative,
        "provenance": (
            f"standard grid accounting understates Turkey's grid carbon "
            f"intensity by {relative:.1%} ({delta:+.4f} tCO2/MWh) via "
            f"omitted geothermal NCG (non-condensable gas) degassing"
        ),
    }


# ============================================================================
# QUARANTINE: exported_mwh is PROVISIONAL. Do not mark locked. See CLAUDE.md
# "Known open items" -> "exported_mwh PROVISIONAL — pending Aras confirmation
# of gross figure + direction."
#
# Quantity: GROSS Turkey->EU electricity physical flow, direction INTO the EU
# only = (TR->GR) + (TR->BG). This is NOT Turkey's net cross-border balance
# and NOT any "net exporter" headline figure -- Turkiye became a net exporter
# in 2024 overall, but that is a different number from the one-directional
# gross flow CBAM charges.
#
# Source: ENTSO-E Statistical Factsheet 2024 (published from ENTSO-E Central
# Transparency Platform data), "Physical energy flows" map, Balkans inset --
# https://eepublicdownloads.blob.core.windows.net/public-cdn-container/clean-documents/Publications/Statistics/Factsheet/entsoe_sfs2024_web.pdf
# Reference year: 2024 (most recent COMPLETE calendar year available; a 2025
# factsheet does not yet exist as of this sourcing -- ENTSO-E's underlying
# 2025 statistical reports were published March 2026 but the polished
# factsheet/map has not followed). 2024 was Turkiye's first net-export year,
# so flows are volatile -- treat this reference year as just that, a
# reference year, not a multi-year average.
#
# Values read directly off the map's directional arrows (not the net
# balance): TR->GR = 687 GWh, TR->BG = 1856 GWh. Both borders show Turkey
# netting as an exporter, consistent with Turkiye's 2024 net-exporter status
# -- an internal consistency check, not proof, since this was read visually
# off a compressed map graphic rather than a raw structured data table.
EXPORTED_MWH_TR_GR = 687_000  # GWh -> MWh
EXPORTED_MWH_TR_BG = 1_856_000  # GWh -> MWh
EXPORTED_MWH_REFERENCE_YEAR = 2024
EXPORTED_MWH = EXPORTED_MWH_TR_GR + EXPORTED_MWH_TR_BG  # 2,543,000 MWh, GROSS TR->EU, NOT net
EXPORTED_MWH_SOURCE = (
    "ENTSO-E Statistical Factsheet 2024, 'Physical energy flows' map (Balkans inset), "
    "https://eepublicdownloads.blob.core.windows.net/public-cdn-container/clean-documents/"
    "Publications/Statistics/Factsheet/entsoe_sfs2024_web.pdf"
)
# ============================================================================


RENEWABLE_FUELS = ["Barajlı", "Akarsu", "Rüzgar", "Güneş", "Jeotermal", "Biyokütle"]
NON_RENEWABLE_FUELS = [
    "Doğal Gaz", "LNG", "Nafta", "Linyit", "Taş Kömür", "İthal Kömür", "Asfaltit Kömür", "Fuel Oil",
]


def renewable_share(mix: pd.Series) -> float:
    return mix[RENEWABLE_FUELS].sum() / mix.sum()


def intensity_under_renewable_share(
    mix: pd.Series, target_renewable_share: float, factors: dict = TURKEY_EMISSION_FACTORS
) -> float:
    """Recompute grid intensity under a hypothetical renewable-generation
    share, holding total generation fixed and each group's (renewable /
    non-renewable) internal fuel-mix proportions fixed. Geothermal keeps its
    real, non-zero emission factor here — a higher 'renewable share' is NOT
    automatically a proportionally cleaner grid if geothermal's share of the
    renewable mix grows along with it."""
    total = mix.sum()
    renewable_total = mix[RENEWABLE_FUELS].sum()
    nonrenewable_total = mix[NON_RENEWABLE_FUELS].sum()

    renewable_scaled = mix[RENEWABLE_FUELS] / renewable_total * (target_renewable_share * total)
    nonrenewable_scaled = mix[NON_RENEWABLE_FUELS] / nonrenewable_total * ((1 - target_renewable_share) * total)
    scaled_mix = pd.concat([renewable_scaled, nonrenewable_scaled])
    return grid_intensity(scaled_mix, factors)


@dataclass(frozen=True)
class ElectricityExposureResult:
    grid_intensity: float
    exported_mwh: float | None
    exposure: float | None


def electricity_exposure(grid_intensity_value: float, exported_mwh: float | None) -> ElectricityExposureResult:
    """Pure. exported_mwh is required to get a real exposure figure — pass
    None (not a fabricated placeholder) if it isn't sourced yet; exposure
    then stays None rather than silently becoming 0 or a made-up number."""
    exposure = grid_intensity_value * exported_mwh if exported_mwh is not None else None
    return ElectricityExposureResult(grid_intensity=grid_intensity_value, exported_mwh=exported_mwh, exposure=exposure)


def exposure_under_renewable_share(
    mix: pd.Series,
    target_renewable_share: float,
    factors: dict = TURKEY_EMISSION_FACTORS,
    exported_mwh: float | None = None,
) -> tuple[float, float | None]:
    intensity = intensity_under_renewable_share(mix, target_renewable_share, factors)
    exposure = intensity * exported_mwh if exported_mwh is not None else None
    return intensity, exposure


def renewable_share_sweep(
    mix: pd.Series,
    factors: dict = TURKEY_EMISSION_FACTORS,
    exported_mwh: float | None = None,
    share_range=None,
) -> pd.DataFrame:
    """One row per renewable-share scenario: share, intensity, exposure.
    exposure is None/NaN throughout if exported_mwh isn't supplied — this is
    the DataFrame persisted to CSV and cited by Implications."""
    if share_range is None:
        share_range = np.round(np.arange(0.0, 1.01, 0.05), 2)
    rows = []
    for share in share_range:
        intensity, exposure = exposure_under_renewable_share(mix, share, factors, exported_mwh)
        rows.append({"renewable_share": share, "intensity": intensity, "exposure": exposure})
    return pd.DataFrame(rows)


def main() -> None:
    item3_df = pd.read_csv(DATA_DIR / "item3.csv")
    mix = load_generation_mix(item3_df)

    print("generation mix (MWh, annual):")
    print(mix.sort_values(ascending=False).to_string())

    # STEP 1: validation gate. Must pass before anything downstream is trusted.
    validation = validate_against_benchmark(mix)
    print(f"\n--- validation run (geothermal forced to 0, vs Ember/IEA benchmark) ---")
    print(f"our build, geothermal=0:  {validation['computed']:.4f} tCO2/MWh")
    print(f"Ember/IEA benchmark:      {validation['benchmark']:.4f} tCO2/MWh")
    print(
        f"gap: {validation['gap']:+.4f} tCO2/MWh ({validation['relative_gap']:+.1%}), "
        f"within +/-{BENCHMARK_TOLERANCE:.0%} tolerance: {validation['within_tolerance']}"
    )
    if not validation["within_tolerance"]:
        print(
            "\nVALIDATION FAILED: forcing geothermal to 0 does not reproduce the "
            "Ember/IEA benchmark within tolerance. This means a NON-geothermal "
            "factor or the generation mix has also drifted — STOPPING. Do not "
            "trust the NCG-adjusted figure or downstream exposure numbers until "
            "this is investigated."
        )
        return
    print("validation passed — the two-basis gap below is attributable to geothermal, not a build error.")

    # STEP 2: the two accounting bases + the named delta.
    ncg_adjusted = grid_intensity_ncg_adjusted(mix)
    delta = geothermal_ncg_delta(ncg_adjusted)

    print(f"\n--- two accounting bases ---")
    print(f"ember_iea_benchmark (geothermal-zero):     {delta['ember_iea_benchmark']:.4f} tCO2/MWh")
    print(f"grid_intensity_ncg_adjusted (operative):   {delta['grid_intensity_ncg_adjusted']:.4f} tCO2/MWh")
    print(f"delta: {delta['delta_tco2_per_mwh']:+.4f} tCO2/MWh ({delta['delta_relative']:+.1%})")
    print(delta["provenance"])

    OUTPUT_DIR.mkdir(exist_ok=True)
    bases_path = OUTPUT_DIR / "electricity_grid_intensity_bases.csv"
    pd.DataFrame([
        {
            "basis": "ember_iea_benchmark",
            "intensity_tco2_per_mwh": delta["ember_iea_benchmark"],
            "description": "Standard grid-carbon accounting, geothermal treated as ~0 (NCG omitted)",
        },
        {
            "basis": "grid_intensity_ncg_adjusted",
            "intensity_tco2_per_mwh": delta["grid_intensity_ncg_adjusted"],
            "description": "Bottom-up build, geothermal costed at 0.887 tCO2/MWh (operative figure)",
        },
        {
            "basis": "geothermal_ncg_delta",
            "intensity_tco2_per_mwh": delta["delta_tco2_per_mwh"],
            "description": delta["provenance"],
        },
    ]).to_csv(bases_path, index=False)
    print(f"\ntwo-basis result written to: {bases_path}")

    # STEP 3: renewable-share lever + exposure, on the NCG-adjusted basis.
    current_renewable_share = renewable_share(mix)
    print(f"\ncurrent renewable generation share: {current_renewable_share:.1%}")

    exported_mwh = EXPORTED_MWH  # PROVISIONAL -- see quarantine block above
    print("\n" + "!" * 78)
    print("! exported_mwh is PROVISIONAL -- pending Aras confirmation of gross figure + direction")
    print("!" * 78)
    print(f"adopted value: {exported_mwh:,.0f} MWh (GROSS Turkey->EU, NOT net)")
    print(f"  = TR->GR {EXPORTED_MWH_TR_GR:,.0f} MWh + TR->BG {EXPORTED_MWH_TR_BG:,.0f} MWh")
    print(f"reference year: {EXPORTED_MWH_REFERENCE_YEAR} (Turkiye's first net-export year -- flows volatile)")
    print(f"source: {EXPORTED_MWH_SOURCE}")
    print("confirmed GROSS directional (TR-into-EU), NOT Turkey's net cross-border balance")
    print("!" * 78)

    exposure_result = electricity_exposure(ncg_adjusted, exported_mwh)
    print(f"\ncurrent-state exposure (PROVISIONAL): {exposure_result.exposure:,.0f} tCO2")

    sweep = renewable_share_sweep(mix, exported_mwh=exported_mwh)
    print("\nrenewable-share sweep, geothermal-real basis, exposure PROVISIONAL:")
    print(sweep.to_string(index=False))

    sweep_path = OUTPUT_DIR / "electricity_renewable_sweep.csv"
    sweep.to_csv(sweep_path, index=False)
    print(f"\nsweep written to: {sweep_path} (exposure column PROVISIONAL)")

    exposure_path = OUTPUT_DIR / "electricity_exposure_current.csv"
    pd.DataFrame([{
        "grid_intensity_ncg_adjusted": exposure_result.grid_intensity,
        "exported_mwh": exposure_result.exported_mwh,
        "exported_mwh_tr_gr": EXPORTED_MWH_TR_GR,
        "exported_mwh_tr_bg": EXPORTED_MWH_TR_BG,
        "exported_mwh_reference_year": EXPORTED_MWH_REFERENCE_YEAR,
        "exported_mwh_source": EXPORTED_MWH_SOURCE,
        "exported_mwh_status": "PROVISIONAL -- pending Aras confirmation of gross figure + direction",
        "exposure_tco2": exposure_result.exposure,
    }]).to_csv(exposure_path, index=False)
    print(f"current-state exposure written to: {exposure_path} (PROVISIONAL)")


if __name__ == "__main__":
    main()
