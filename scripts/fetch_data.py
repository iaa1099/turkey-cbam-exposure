"""Check for the raw data files this model needs and print retrieval
instructions for any that are missing.

None of the three raw sources (EU CBAM default values, Eurostat Comext trade,
EPİAŞ hourly generation) have a stable, unauthenticated, single-URL bulk
download suitable for an unattended `curl`/`requests` fetch — each requires a
manual step (a versioned regulation workbook, an Easy Comext query, or a
transparency-platform export/API pull). This script does not pretend
otherwise: it reports what is missing and points at data/README.md for the
exact retrieval steps and source URLs, rather than silently failing or
fabricating a fetch that wouldn't reproduce the committed files.
"""
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

REQUIRED_FILES = {
    "item1.xlsx": (
        "EU CBAM default emission values. Download the 'Default values "
        "definitive period' workbook from the European Commission's CBAM "
        "definitive-regime page and save as data/item1.xlsx. "
        "See data/README.md for the exact URL and regulatory citation."
    ),
    "item2.csv": (
        "Eurostat Comext DS-045409, Turkiye->EU imports, 2024, EU-27 "
        "aggregate reporter. Re-run the Easy Comext query described in "
        "data/README.md and save the raw extract as data/item2.csv."
    ),
    "item3.csv": (
        "Consolidated 2024 hourly Turkish grid generation by fuel type. "
        "This is already a processed/deduplicated file, not a raw EPIAS "
        "export -- see data/README.md for the source platform and what "
        "re-deriving it from scratch would require."
    ),
}


def main() -> None:
    missing = [name for name in REQUIRED_FILES if not (DATA_DIR / name).exists()]

    if not missing:
        print(f"All raw data files present in {DATA_DIR}.")
        return

    print(f"Missing {len(missing)} raw data file(s) in {DATA_DIR}:\n")
    for name in missing:
        print(f"  {name}")
        print(f"    {REQUIRED_FILES[name]}\n")
    print("Full source URLs, retrieval dates, and licence terms: data/README.md")


if __name__ == "__main__":
    main()
