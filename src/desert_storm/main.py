"""Command line entry point for normalising roster aliases."""

from __future__ import annotations

import argparse
from typing import Iterable, List

from .aliases import load_alias_map, resolve_alias


def normalise_names(names: Iterable[str]) -> List[str]:
    """Return the canonical representation for every entry in ``names``."""

    alias_map = load_alias_map()
    return [resolve_alias(name, alias_map=alias_map) for name in names]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "names",
        metavar="NAME",
        nargs="+",
        help="Roster names that should be normalised.",
    )
    return parser


def main(argv: list[str] | None = None) -> List[str]:
    parser = build_parser()
    args = parser.parse_args(argv)
    normalised = normalise_names(args.names)
    for value in normalised:
        print(value)
    return normalised


if __name__ == "__main__":  # pragma: no cover - CLI passthrough
    main()
