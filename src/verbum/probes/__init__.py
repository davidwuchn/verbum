"""Unified probe library for Verbum crystal measurement experiments.

This package provides two layers:

1. **Probe-set loader** (`verbum.probes._loader`) — the original probe-set
   infrastructure for loading JSON probe files with gates. Exports:
   Gate, Probe (the JSON model), ProbeSet, ResolvedProbe, etc.

2. **Unified probe library** (`verbum.probes.library`) — consolidated
   collection of ~800+ probes from all sources, normalized to a single
   `CrystalProbe` dataclass with combinator labels. Exports:
   CrystalProbe, all_probes, by_combinator, crystal_probes, etc.

Quick start for crystal measurement:

    from verbum.probes.library import all_probes, by_combinator, crystal_probes

    probes = all_probes()          # all ~780 deduplicated probes
    k = by_combinator("K")        # all K-combinator probes
    crystal = crystal_probes()     # KIBC+DWYS+WHNF subset

Quick start for probe-set loading (JSON files):

    from verbum.probes import load_probe_set, resolve_probes
"""

# ── Re-export the original probe-set loader (backward compat) ────────────────
from verbum.probes._loader import (
    Gate,
    Probe,
    ProbeSet,
    ResolvedProbe,
    gate_hash,
    load_gate,
    load_probe_set,
    probe_set_hash,
    resolve_probes,
)

# ── Re-export the unified library ────────────────────────────────────────────
from verbum.probes.library import (
    Probe as CrystalProbe,  # renamed to avoid conflict with _loader.Probe
    all_probes,
    by_category,
    by_combinator,
    by_source,
    combinator_counts,
    crystal_probes,
    print_stats,
)

__all__ = [
    # Probe-set loader (original)
    "Gate",
    "Probe",
    "ProbeSet",
    "ResolvedProbe",
    "gate_hash",
    "load_gate",
    "load_probe_set",
    "probe_set_hash",
    "resolve_probes",
    # Unified library
    "CrystalProbe",
    "all_probes",
    "by_category",
    "by_combinator",
    "by_source",
    "combinator_counts",
    "crystal_probes",
    "print_stats",
]
