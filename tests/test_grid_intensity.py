from pathlib import Path

import pandas as pd
import pytest

from features.gridIntensity import turkey_grid_intensity

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "item3.csv"

pytestmark = pytest.mark.skipif(
    not DATA_PATH.exists(),
    reason="raw data files not committed (gitignored) — run locally with data/ populated, see data/README.md",
)


def test_turkey_grid_intensity_in_expected_range():
    grid_df = pd.read_csv(DATA_PATH)
    intensity = turkey_grid_intensity(grid_df)
    assert 0.4 < intensity < 0.5
