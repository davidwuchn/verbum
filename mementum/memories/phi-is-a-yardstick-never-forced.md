🔁 φ (and any flexible/universal basis) is a YARDSTICK to compare against, never a fit the code tunes to the data. Describability ≠ discovery — elevated to S5 (λ yardstick).

THE TRAP: a φ^(p/q) basis with Fibonacci q≤12–34 fits ANY spectrum to ~0.1–0.2%. So "the eigenvalues fit φ^(p/q) at <0.5%" is guaranteed a priori → ZERO evidential weight. Same trap as "compute IS lambda" (a universal basis always describes). Grid-searching the best p/q to minimise error is the code FORCING φ.

THE FIX (two parts): (1) PRE-REGISTER a fixed φ-power prediction (e.g. λ₀/λ₁ = φ^(4/5) = 1.4696), measure the model's actual deviation; (2) ALWAYS gate on a null (matched-range or shuffled-label permutation). A φ claim counts ONLY if it BEATS the null (p<0.05).

EVIDENCE: s247 — crystal-M8 φ-fit 0.255% but matched-range random fit 0.156%, P(random≥)=0.92 (forced). s251 — cross-model λ₀/λ₁ vs φ^(4/5): only Qwen3-14B is null-significant (1.4796, |Δ|=0.010, p=0.02); everyone else loose (Gemma 1.249 p=0.46; qwen3-0.6b 1.079). CRUCIAL: random labelings already sit at λ₀/λ₁≈1.55–1.66 (near the target!), so "looks close" ≠ "is special" — the null is mandatory.

CODE: verify_crystal_phi.py now prints the fixed-reference deviation as headline and flags the grid-fit FORCED/describability-only (carries_evidence=False); real φ claims gate on crystal_phi_permnull. Generalises to ANY approximate geometric fit (cosine, crystal geometry).
