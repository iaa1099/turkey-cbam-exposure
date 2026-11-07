"""Build all four Implications exhibits. Read-only on model outputs — plot
only, no recompute. Run: python3 -m viz.build_all"""

from viz import (
    exhibit1_cross_sector_cliff,
    exhibit2_steel_inversion,
    exhibit3_renewable_floor,
    exhibit4_two_basis,
)
from viz.style import save_exhibit

EXHIBITS = [
    (exhibit1_cross_sector_cliff, "exhibit1_cross_sector_cliff"),
    (exhibit2_steel_inversion, "exhibit2_steel_inversion"),
    (exhibit3_renewable_floor, "exhibit3_renewable_floor"),
    (exhibit4_two_basis, "exhibit4_two_basis"),
]

if __name__ == "__main__":
    for module, name in EXHIBITS:
        fig = module.build()
        png, svg = save_exhibit(fig, name)
        print(png)
        print(svg)
