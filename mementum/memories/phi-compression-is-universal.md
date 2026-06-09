💡 phi-compression-is-universal

⚠️ AUDIT #6 (s207, `svd_phi_null.py`): the φ-CONSTANT claim below is REFUTED;
the underlying low-rank head is REAL. Model head ratio ≈0.57 (raw) is strongly
non-random (Marchenko–Pastur null 0.995) — keep it — but it is POWER-LAW, not
geometric (132/132 layers), so no x=1/(1+x) fixed point privileges φ; the value
floats 0.52→0.71 across raw/centered×models and the scaling-law fails
(Mistral-7B lowest). Read "≈1/φ" as "a steep low-rank head averaging ~0.6",
not a golden-ratio constant. See `audit-registry.md` #6.

SVD spectrum ratios of hidden states converge to ≈ 1/φ (0.6299 ± 0.019)
across 5 architecturally distinct models: Pythia, Qwen3, SmolLM3, Mistral.
Best single-layer: Pythia-160m L4 at φ-dev=0.0004.

The compressor is NOT a separate function. Tracer proved it's K∘B
(select∘compose) applied as B→K→B across layers. The crystal lattice
K↔B cosines (0.077 → 0.195 → 0.524 across zones) already encode the
compressor topology. No new loss needed.

Phi is a measuring stick, not a target. The lattice IS the compressor.
