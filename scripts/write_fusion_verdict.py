from __future__ import annotations

import argparse

from bioir.fusion_intervention import write_verdict_artifact


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recompute and persist the frozen BioIR temporal-fusion verdict."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="artifacts/fusion_verdict_v1.json",
        help="output JSON path",
    )
    args = parser.parse_args()
    print(write_verdict_artifact(args.path))


if __name__ == "__main__":
    main()
