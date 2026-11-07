from pathlib import Path

import pandas as pd
import pytest

from features.electricityGood import (
    BENCHMARK_TOLERANCE,
    EMBER_IEA_BENCHMARK,
    EXPORTED_MWH,
    EXPORTED_MWH_REFERENCE_YEAR,
    EXPORTED_MWH_SOURCE,
    EXPORTED_MWH_TR_BG,
    EXPORTED_MWH_TR_GR,
    TURKEY_EMISSION_FACTORS,
    electricity_exposure,
    geothermal_ncg_delta,
    grid_intensity_ncg_adjusted,
    load_generation_mix,
    renewable_share,
    renewable_share_sweep,
    validate_against_benchmark,
)

BASE_DIR = Path(__file__).resolve().parent.parent


def _mix():
    item3_df = pd.read_csv(BASE_DIR / "data" / "item3.csv")
    return load_generation_mix(item3_df)


def test_validation_run_reproduces_benchmark_with_geothermal_zeroed():
    validation = validate_against_benchmark(_mix())
    assert validation["within_tolerance"]
    assert abs(validation["relative_gap"]) <= BENCHMARK_TOLERANCE


def test_two_bases_and_named_delta():
    ncg_adjusted = grid_intensity_ncg_adjusted(_mix())
    delta = geothermal_ncg_delta(ncg_adjusted)

    assert delta["ember_iea_benchmark"] == EMBER_IEA_BENCHMARK
    assert delta["grid_intensity_ncg_adjusted"] == pytest.approx(ncg_adjusted)
    # the gap is a real, positive finding (NCG-adjusted > benchmark), not noise
    assert delta["delta_tco2_per_mwh"] > 0
    assert 0.03 < delta["delta_relative"] < 0.10
    assert "geothermal" in delta["provenance"].lower()


def test_geothermal_factor_is_not_zero():
    assert TURKEY_EMISSION_FACTORS["Jeotermal"].tco2_per_mwh > 0.5


def test_every_factor_has_a_source():
    for fuel, factor in TURKEY_EMISSION_FACTORS.items():
        assert factor.source and len(factor.source) > 10, f"{fuel} missing a real source string"


def test_module_never_touches_steel():
    import_lines = [
        line for line in Path("features/electricityGood.py").read_text().splitlines()
        if line.strip().startswith(("import ", "from "))
    ]
    for forbidden in ["steelFeatures", "steelClusterFrozen", "clustering", "item1CleanUp", "item2CleanUp"]:
        assert not any(forbidden in line for line in import_lines), f"found forbidden import: {forbidden}"


def test_electricity_exposure_stays_none_without_exported_mwh():
    result = electricity_exposure(0.4681, None)
    assert result.exposure is None

    result_with_volume = electricity_exposure(0.4681, 1000.0)
    assert result_with_volume.exposure == pytest.approx(468.1)


def test_renewable_share_sweep_bounds_and_shape():
    mix = _mix()
    sweep = renewable_share_sweep(mix, share_range=[0.0, 1.0])

    assert list(sweep.columns) == ["renewable_share", "intensity", "exposure"]
    assert sweep["exposure"].isna().all()

    zero_share_intensity = sweep.loc[sweep["renewable_share"] == 0.0, "intensity"].iloc[0]
    full_share_intensity = sweep.loc[sweep["renewable_share"] == 1.0, "intensity"].iloc[0]
    assert zero_share_intensity > full_share_intensity  # more renewables -> lower intensity, even with geothermal
    assert full_share_intensity > 0  # NOT zero -- geothermal keeps a real factor even at 100% "renewable"


def test_current_renewable_share_is_a_fraction():
    share = renewable_share(_mix())
    assert 0 < share < 1


def test_exported_mwh_is_gross_sum_of_the_two_borders():
    assert EXPORTED_MWH == EXPORTED_MWH_TR_GR + EXPORTED_MWH_TR_BG
    assert EXPORTED_MWH_TR_GR > 0
    assert EXPORTED_MWH_TR_BG > 0
    assert EXPORTED_MWH_REFERENCE_YEAR == 2024
    assert "entsoe" in EXPORTED_MWH_SOURCE.lower()


def test_exported_mwh_is_flagged_provisional_in_source():
    source = Path("features/electricityGood.py").read_text()
    assert "PROVISIONAL" in source
    assert "gross" in source.lower() and "net" in source.lower()


def test_full_exposure_computes_with_sourced_exported_mwh():
    ncg_adjusted = grid_intensity_ncg_adjusted(_mix())
    result = electricity_exposure(ncg_adjusted, EXPORTED_MWH)
    assert result.exposure == pytest.approx(ncg_adjusted * EXPORTED_MWH)
    assert result.exposure > 0
