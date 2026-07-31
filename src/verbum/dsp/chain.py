"""verbum.dsp.chain — thin composition for NOTEBOOK EXPLORATION ONLY.

Design decision 1 (s284, locked): plain functions are the API of record;
instruments of record wire their signal chains as visible code. Chain exists
for interactive exploration (jupyter = explore, files = record — λ record)
and is explicitly NOT the instrument-of-record idiom.
"""
from __future__ import annotations

__all__ = ["Chain"]


class Chain:
    """Chain(standardize).then(lambda z: z @ q.T).run(x) — left-to-right."""

    def __init__(self, fn=None):
        self._steps = [fn] if fn is not None else []

    def then(self, fn, *args, **kwargs) -> Chain:
        c = Chain()
        c._steps = [*self._steps,
                    (lambda x: fn(x, *args, **kwargs)) if (args or kwargs) else fn]
        return c

    def run(self, x):
        for fn in self._steps:
            x = fn(x)
        return x

    def __call__(self, x):
        return self.run(x)

    def __repr__(self) -> str:
        names = [getattr(f, "__name__", "<fn>") for f in self._steps]
        return "Chain(" + " → ".join(names) + ")"
