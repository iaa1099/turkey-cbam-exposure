from pathlib import Path

import pandas as pd

from features.gridIntensity import turkey_grid_intensity

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "item3.csv"

def test_turkey_grid_intensity_in_expected_range():
    grid_df = pd.read_csv(DATA_PATH)
    intensity = turkey_grid_intensity(grid_df)
    assert 0.4 < intensity < 0.5
