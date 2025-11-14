from __future__ import annotations

import sys
from pathlib import Path

# Ensure ``src`` is on ``sys.path`` for the test suite.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
