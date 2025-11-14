"""Centralised alias loading and resolution utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Mapping, MutableMapping, Optional

# The repository stores aliases in ``data/aliases.json``.  The helper keeps
# the default close to the code while still allowing tests to point to
# temporary files.
DEFAULT_ALIAS_FILE = Path(__file__).resolve().parents[1] / "data" / "aliases.json"

# Historically alias resolution stopped at 64 indirections but silently fell
# back to the original name.  Keeping the same upper bound protects against
# bad data while explicitly surfacing issues instead of masking them.
MAX_ALIAS_DEPTH = 64


class AliasResolutionError(ValueError):
    """Raised when alias resolution cannot succeed."""


def _normalise_alias_map(raw_map: Mapping[str, str]) -> Dict[str, str]:
    """Validate and normalise the alias mapping.

    The helper guarantees that both keys and values are strings.  The
    repository's data files should already follow that convention; enforcing it
    here prevents subtle bugs should the file content drift in the future.
    """

    normalised: Dict[str, str] = {}
    for alias, target in raw_map.items():
        if not isinstance(alias, str) or not isinstance(target, str):
            raise AliasResolutionError(
                "Alias files must map strings to strings."
            )
        normalised[alias] = target
    return normalised


def load_alias_map(path: Optional[Path] = None) -> Dict[str, str]:
    """Load the alias map from ``path``.

    Parameters
    ----------
    path:
        Optional custom path.  When omitted, ``data/aliases.json`` is used.

    Returns
    -------
    dict
        Mapping of alias -> canonical name.  An empty mapping is returned when
        the file is missing or empty.
    """

    resolved_path = Path(path) if path is not None else DEFAULT_ALIAS_FILE
    if not resolved_path.exists():
        return {}

    text = resolved_path.read_text(encoding="utf-8").strip()
    if not text:
        return {}

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
        raise AliasResolutionError(
            f"Alias file {resolved_path} is not valid JSON"
        ) from exc

    if not isinstance(data, MutableMapping):
        raise AliasResolutionError(
            f"Alias file {resolved_path} must contain a JSON object."
        )

    return _normalise_alias_map(data)


def resolve_alias(
    name: Optional[str],
    *,
    alias_map: Optional[Mapping[str, str]] = None,
    max_depth: int = MAX_ALIAS_DEPTH,
) -> Optional[str]:
    """Resolve ``name`` via the configured alias map.

    Aliases may form chains (``A -> B -> C``).  The resolver follows them until
    a canonical name is reached or the maximum depth is exceeded.  Cycles and
    chains longer than ``max_depth`` raise :class:`AliasResolutionError` to make
    data issues obvious to callers and tests alike.
    """

    if name is None:
        return None

    if max_depth <= 0:
        raise AliasResolutionError("max_depth must be a positive integer")

    if alias_map is None:
        alias_map = load_alias_map()

    current = str(name)
    visited = {current}

    for _ in range(max_depth):
        target = alias_map.get(current)
        if target is None:
            return current

        if target in visited:
            raise AliasResolutionError(
                f"Cycle detected while resolving alias {name!r}: {target!r}"
            )

        visited.add(target)
        current = target

    # Explicit failure keeps unexpected data from silently producing
    # inconsistent results.
    raise AliasResolutionError(
        f"Maximum alias resolution depth of {max_depth} exceeded for {name!r}"
    )
