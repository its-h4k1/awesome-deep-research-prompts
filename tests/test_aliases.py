from __future__ import annotations

import json
from pathlib import Path

import pytest

from desert_storm.aliases import (
    MAX_ALIAS_DEPTH,
    AliasResolutionError,
    load_alias_map,
    resolve_alias,
)


def write_alias_file(tmp_path: Path, mapping: dict[str, str]) -> Path:
    alias_path = tmp_path / "aliases.json"
    alias_path.write_text(json.dumps(mapping), encoding="utf-8")
    return alias_path


def test_load_alias_map_reads_valid_json(tmp_path: Path) -> None:
    alias_path = write_alias_file(tmp_path, {"MJ": "Michael"})

    loaded = load_alias_map(alias_path)

    assert loaded == {"MJ": "Michael"}


def test_resolve_alias_returns_original_when_missing() -> None:
    assert resolve_alias("Unknown", alias_map={}) == "Unknown"


def test_resolve_alias_handles_simple_chain() -> None:
    alias_map = {"MJ": "Michael"}

    assert resolve_alias("MJ", alias_map=alias_map) == "Michael"


def test_resolve_alias_handles_transitive_chain() -> None:
    alias_map = {"MJ": "Michael", "Michael": "M"}

    assert resolve_alias("MJ", alias_map=alias_map) == "M"


def test_resolve_alias_detects_cycles() -> None:
    alias_map = {"A": "B", "B": "A"}

    with pytest.raises(AliasResolutionError):
        resolve_alias("A", alias_map=alias_map)


def test_resolve_alias_enforces_max_depth() -> None:
    alias_map = {}
    current = "A0"
    for index in range(MAX_ALIAS_DEPTH + 1):
        next_value = f"A{index + 1}"
        alias_map[current] = next_value
        current = next_value

    with pytest.raises(AliasResolutionError):
        resolve_alias("A0", alias_map=alias_map)
