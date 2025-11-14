"""Helpers for investigating missing metric definitions."""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence

from .aliases import load_alias_map, resolve_alias


def find_unknown_metrics(
    names: Iterable[str],
    known_metrics: Mapping[str, object],
) -> list[str]:
    """Return metrics whose canonical name is missing from ``known_metrics``."""

    alias_map = load_alias_map()
    missing: list[str] = []
    for name in names:
        canonical = resolve_alias(name, alias_map=alias_map)
        if canonical not in known_metrics:
            missing.append(canonical)
    return missing


def debug_missing_metrics(
    names: Sequence[str],
    known_metrics: Mapping[str, object],
) -> list[str]:
    """Convenience wrapper for notebooks and scripts."""

    missing = find_unknown_metrics(names, known_metrics)
    if missing:
        print("Missing metrics:")
        for metric in missing:
            print(f"  - {metric}")
    else:
        print("All metrics available.")
    return missing
