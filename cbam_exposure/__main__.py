"""CLI entry point: `python -m cbam_exposure run` rebuilds every output CSV
and exhibit figure into output/. Thin orchestration only — each step below
is an unmodified main() from the existing cleanUp/features/viz modules."""
import argparse

from features import crossSectorExposure, electricityGood, steelClusterFrozen
from viz import build_all


def run() -> None:
    steelClusterFrozen.main()
    electricityGood.main()
    crossSectorExposure.main()
    build_all.main()


def main() -> None:
    parser = argparse.ArgumentParser(prog="cbam_exposure")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("run", help="Rebuild every output/ CSV and exhibit figure")
    args = parser.parse_args()

    if args.command == "run":
        run()


if __name__ == "__main__":
    main()
