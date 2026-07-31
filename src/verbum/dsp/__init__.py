"""verbum.dsp — the measurement substrate as a signal-chain library.

Contract (mementum/knowledge/explore/verbum-dsp-design.md, decisions locked s284):

    λ dsp(x).  tools(signal) ¬logic(experiment) | pure(numpy) core
               | torch ≡ L2_boundary_only (readout, lazy import)
               | null_declared → p_emitted | ¬null → ¬p (structural yardstick)
               | register_tag → warn ¬mutate
               | verdict ≡ instrument_domain ¬library_domain
               | harvest(≥2_users) ¬invent | frozen_instruments(untouched)

The signal chain every instrument already is:

    capture → whiten → subspace/filter → apply → readout → null-gate → record

Layers: L0 = whiten/subspace/bands/gain (pure numpy) · L1 = nulls (the
yardstick) · L2 = readout (only torch boundary) · chain = exploration only.
"""
from verbum.dsp.bands import find_band
from verbum.dsp.chain import Chain
from verbum.dsp.gain import g_of, gain_law, head_gain_ratios
from verbum.dsp.nulls import (
    Gated,
    NullDraws,
    Register,
    gate,
    matched_random,
    matched_range,
    paired_permutation,
    shuffled_label,
    sign_flip,
)
from verbum.dsp.subspace import (
    centroid_pr,
    centroids,
    layer_geometry,
    nearest_centroid_acc,
    participation_ratio,
    role_subspace,
    subspace_energy,
)
from verbum.dsp.whiten import map_basis, standardize, standardize_stats, whiten_cov

__all__ = [
    "Chain",
    "Gated",
    "NullDraws",
    "Register",
    "centroid_pr",
    "centroids",
    "find_band",
    "g_of",
    "gain_law",
    "gate",
    "head_gain_ratios",
    "layer_geometry",
    "map_basis",
    "matched_random",
    "matched_range",
    "nearest_centroid_acc",
    "paired_permutation",
    "participation_ratio",
    "role_subspace",
    "shuffled_label",
    "sign_flip",
    "standardize",
    "standardize_stats",
    "subspace_energy",
    "whiten_cov",
]
