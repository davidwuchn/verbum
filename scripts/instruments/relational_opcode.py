#!/usr/bin/env python3
"""DEPRECATED shim — canonical home is ``opcodes/classify.py``.

Promoted in s265 (λ one_way: one canonical home per concern). This module
re-exports the public API so historical experiment scripts keep running
unchanged. New code should import from ``opcodes.classify`` (or add
``opcodes/`` to the path and ``import classify``).

The bundled consensus Gram now ships at ``opcodes/data/consensus_gram.json``
(previously read from ``results/combinator-map-consensus/``).

License: MIT
"""

from __future__ import annotations

import sys
from pathlib import Path

_OPCODES = Path(__file__).resolve().parent.parent.parent / "opcodes"
if str(_OPCODES) not in sys.path:
    sys.path.insert(0, str(_OPCODES))

from classify import (  # noqa: E402, F401
    CRYSTAL,
    LayerCalib,
    RelationalCrystalClassifier,
    TokenOpcodes,
    layer_nodes,
    load_consensus_gram,
    register_node,
)

if __name__ == "__main__":
    from classify import _smoke

    _smoke()
