"""Neighborhood Library application package."""

from __future__ import annotations

import sys
from pathlib import Path

# Generated protobuf/gRPC stubs live under ``generated/`` as ``library.v1``.
_gen = Path(__file__).resolve().parent / "generated"
if _gen.is_dir() and str(_gen) not in sys.path:
    sys.path.insert(0, str(_gen))
