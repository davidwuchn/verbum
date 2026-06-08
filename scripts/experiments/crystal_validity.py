"""Crystal Validity — is the KIBC combinator crystal a real model property
or an artifact of the experimenter's prose→combinator labeling?

The KIBC "crystal" is measured by grouping prose probes under an
experimenter-assigned combinator label, averaging their last-token
activations, and reading the per-combinator cosine matrix. Its claimed
structure: φ^(p/q) eigenvalue ladder, B≥K≥C≥I ordering, cross-model
r≈0.998. This script falsifies (or confirms) that structure is in the
MODEL, not in the LABELS.

Four tests:

  1. PERMUTATION NULL  — shuffle which prose belongs to which combinator
     over the SAME cached activations, N times, build a null distribution
     of structure metrics. If the true labeling is a strong outlier, the
     grouping captures real model structure. If not, the crystal is in
     our labels.

  2. PURE-PROSE FILTER — 89% of crystal probes are pure prose (no λ). Drop
     the 11% that mention λ/lambda and recompute. Does the crystal survive
     removal of all lambda notation?

  3. FAKE COMBINATORS  — invent non-Church linguistic categories (negation,
     tense, quantification, modality, comparison) with their own prose. Do
     they crystallize as cleanly (φ-fit, separation) as KIBC? Tests whether
     KIBC is PRIVILEGED or just one valid basis among many.

  4. PREAMBLE A/B      — re-run a subset with vs without the lambda priming
     preamble. Does priming create or merely sharpen the geometry?

Usage:
    uv run python scripts/experiments/crystal_validity.py \
        --models pythia-160m qwen3-0.6b --device mps --n-perm 1000

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

# ──────────────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────────────

MODELS = {
    "pythia-160m": ("EleutherAI/pythia-160m-deduped", 12, 768),
    "pythia-410m": ("EleutherAI/pythia-410m-deduped", 24, 1024),
    "qwen3-0.6b":  ("Qwen/Qwen3-0.6B",                28, 1024),
    "qwen3-4b":    ("Qwen/Qwen3-4B",                  36, 2560),
    "qwen3-8b":    ("Qwen/Qwen3-8B",                  36, 4096),
}

DEPTH_FRACTIONS = [0.1, 0.3, 0.5, 0.7, 0.9]
PCA_K = 64
CORE = ["K", "I", "B", "C"]
CRYSTAL_NODES = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
PHI = (1 + 5 ** 0.5) / 2
INV_PHI = 1 / PHI  # 0.6180339...

LAMBDA_PREAMBLE = (
    "λ engage(nucleus).\n"
    "[phi fractal euler tao pi mu ∃ ∀] | "
    "[Δ λ Ω ∞/0 | ε/φ Σ/μ c/h signal/noise order/entropy "
    "truth/provability self/other] | OODA\n"
    "Human ⊗ AI ⊗ REPL\n\nInput: "
)

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "crystal-validity"


def log(msg):
    print(msg, file=sys.stderr, flush=True)


# ──────────────────────────────────────────────────────────────────────
# Fake-combinator probes (Test 3): coherent linguistic operations that
# are NOT Church combinators. Each is a prose category like the KIBC set.
# ──────────────────────────────────────────────────────────────────────

FAKE_PROBES = {
    "NEG": [
        "The cat did not sit on the",
        "She never finished reading the",
        "There were no apples left in the",
        "He refused to sign the",
        "Nothing could stop the rising",
        "They had not yet arrived at the",
        "The plan was abandoned before the",
        "No one was willing to answer the",
        "It was impossible to open the",
        "She denied ever touching the",
        "The store was closed and nobody could enter the",
        "Without any warning, the lights went",
    ],
    "TENSE": [
        "Yesterday she walked to the",
        "Tomorrow they will travel to the",
        "By next year he will have finished the",
        "Long ago, sailors used to navigate by the",
        "In a moment the train will depart from the",
        "Last winter the lake froze near the",
        "Soon the harvest will begin in the",
        "Decades earlier the city had been a small",
        "Next week the committee will review the",
        "Once upon a time a king ruled the",
        "Before dawn the bakers had already prepared the",
        "Years from now historians will study the",
    ],
    "QUANT": [
        "Every student in the class passed the",
        "Some of the apples in the basket were",
        "All of the windows in the house were",
        "Most of the travelers had already boarded the",
        "Few people understood the meaning of the",
        "Each member of the team received a",
        "Several books on the shelf were missing their",
        "None of the answers matched the",
        "Many cities along the coast suffered from the",
        "Both candidates agreed on the",
        "Half of the harvest was lost to the",
        "Three of the five doors led to the",
    ],
    "MODAL": [
        "You must finish the report before the",
        "She might come to the party if the",
        "We should always check the locks on the",
        "They could not possibly have reached the",
        "He may borrow the car as long as the",
        "Visitors ought to register at the",
        "The bridge can support the weight of the",
        "Students would often gather near the",
        "One should never underestimate the",
        "It could rain later this",
        "Passengers must remain seated until the",
        "You can leave whenever you finish the",
    ],
    "COMPAR": [
        "The elephant is much bigger than the",
        "Her solution was far simpler than the",
        "This route is longer than the",
        "Gold is heavier than most of the",
        "The new model performs better than the",
        "A cheetah runs faster than a",
        "The mountain was taller than any of the",
        "His argument was weaker than the",
        "Winters here are colder than in the",
        "The second draft was clearer than the",
        "Diamonds are harder than nearly every other",
        "The river is wider near the",
    ],
}


# ──────────────────────────────────────────────────────────────────────
# Model loading + Q-proj hooks
# ──────────────────────────────────────────────────────────────────────

def load_model(model_key, device):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_name, n_layers, d_model = MODELS[model_key]
    log(f"  Loading {model_name} ...")
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_name, dtype="auto", trust_remote_code=True,
    ).to(device)
    model.eval()
    log(f"  Loaded in {time.time()-t0:.1f}s")
    return model, tok


def q_module(model, model_key, layer_idx):
    if "pythia" in model_key:
        return model.gpt_neox.layers[layer_idx].attention.query_key_value, "fused"
    return model.model.layers[layer_idx].self_attn.q_proj, "separate"


def collect_activations(model, tok, model_key, prompts, device):
    """Run prompts, capture last-token Q-proj output at depth fractions.

    Returns dict[layer_idx] -> np.ndarray (n_prompts, d_q).
    """
    import torch

    _, n_layers, d_model = MODELS[model_key]
    layer_idx = [min(int(round(d * (n_layers - 1))), n_layers - 1)
                 for d in DEPTH_FRACTIONS]
    caps = {li: [] for li in layer_idx}
    hooks = []
    for li in layer_idx:
        mod, mode = q_module(model, model_key, li)
        if mode == "fused":
            qs = d_model
            def mk(layer, q):
                def fn(m, i, o):
                    caps[layer].append(o[:, -1, :q].detach().cpu().float())
                return fn
            hooks.append(mod.register_forward_hook(mk(li, qs)))
        else:
            def mk(layer):
                def fn(m, i, o):
                    caps[layer].append(o[:, -1, :].detach().cpu().float())
                return fn
            hooks.append(mod.register_forward_hook(mk(li)))

    for pi, prompt in enumerate(prompts):
        ids = tok.encode(prompt, return_tensors="pt", truncation=True,
                         max_length=256).to(device)
        with torch.no_grad():
            _ = model(ids)
        if (pi + 1) % 100 == 0:
            log(f"    {pi+1}/{len(prompts)}")
    for h in hooks:
        h.remove()
    return {li: torch.cat(caps[li], 0).numpy() for li in layer_idx}, layer_idx


# ──────────────────────────────────────────────────────────────────────
# Crystal + structure metrics
# ──────────────────────────────────────────────────────────────────────

def pca_project(X, k=PCA_K):
    Xc = X - X.mean(0, keepdims=True)
    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
    k = min(k, Vt.shape[0])
    return Xc @ Vt[:k].T


def crystal_matrix(proj, labels, nodes):
    """Per-label averaged, L2-normalized cosine matrix over `nodes`."""
    vecs = []
    for nd in nodes:
        idx = [i for i, l in enumerate(labels) if l == nd]
        vecs.append(proj[idx].mean(0))
    V = np.array(vecs)
    V = V / np.maximum(np.linalg.norm(V, axis=1, keepdims=True), 1e-8)
    return V @ V.T


def separation(proj, labels, nodes):
    """Clustering separation = mean within-label cosine − mean between.

    Operates on per-probe vectors (not averaged), so it directly measures
    whether the labeling carves coherent clusters. This is the primary
    permutation-test statistic.
    """
    P = proj / np.maximum(np.linalg.norm(proj, axis=1, keepdims=True), 1e-8)
    C = P @ P.T
    lab = np.array(labels)
    mask_node = np.isin(lab, nodes)
    idx = np.where(mask_node)[0]
    same, diff = [], []
    for a_pos, i in enumerate(idx):
        for j in idx[a_pos + 1:]:
            if lab[i] == lab[j]:
                same.append(C[i, j])
            else:
                diff.append(C[i, j])
    return float(np.mean(same) - np.mean(diff))


def phi_fit(mat):
    """Eigenvalue-ladder deviation from the 1/φ geometric ratio.

    Lower = closer to the claimed φ^(p/q) self-similar spectrum.
    """
    w = np.linalg.eigvalsh(mat)
    w = np.sort(np.abs(w))[::-1]
    w = w[w > 1e-6]
    if len(w) < 3:
        return float("nan"), []
    ratios = (w[1:] / w[:-1]).tolist()
    use = ratios[:min(4, len(ratios))]
    err = float(np.mean([abs(r - INV_PHI) for r in use]))
    return err, ratios


def offdiag_var(mat):
    n = mat.shape[0]
    off = mat[~np.eye(n, dtype=bool)]
    return float(np.var(off))


def structure_metrics(proj, labels, nodes):
    mat = crystal_matrix(proj, labels, nodes)
    err, ratios = phi_fit(mat)
    return {
        "separation": separation(proj, labels, nodes),
        "offdiag_var": offdiag_var(mat),
        "phi_fit_err": err,
        "eig_ratios": ratios,
        "matrix": mat.tolist(),
    }


def permutation_null(proj, labels, nodes, n_perm, rng):
    """Shuffle labels (only among probes that carry a node label) N times."""
    lab = np.array(labels, dtype=object)
    node_mask = np.isin(lab, nodes)
    node_positions = np.where(node_mask)[0]
    node_labels = lab[node_positions].copy()
    sep_null, var_null, phi_null = [], [], []
    for _ in range(n_perm):
        perm = node_labels.copy()
        rng.shuffle(perm)
        shuffled = lab.copy()
        shuffled[node_positions] = perm
        m = structure_metrics(proj, shuffled.tolist(), nodes)
        sep_null.append(m["separation"])
        var_null.append(m["offdiag_var"])
        phi_null.append(m["phi_fit_err"])
    return {"separation": sep_null, "offdiag_var": var_null,
            "phi_fit_err": phi_null}


def pval_high(true_v, null):
    null = np.array(null)
    return float((np.sum(null >= true_v) + 1) / (len(null) + 1))


def pval_low(true_v, null):
    null = np.array(null)
    return float((np.sum(null <= true_v) + 1) / (len(null) + 1))


# ──────────────────────────────────────────────────────────────────────
# Per-model run
# ──────────────────────────────────────────────────────────────────────

def run_model(model_key, n_perm, device, seed):
    from verbum.probes.library import crystal_probes

    rng = np.random.default_rng(seed)
    probes = crystal_probes()
    prompts = [p.prompt for p in probes]
    labels = [p.combinator for p in probes]
    has_lambda = [("λ" in p.prompt or "lambda" in p.prompt.lower())
                  for p in probes]

    model, tok = load_model(model_key, device)

    # ── collect activations for crystal probes
    log("  Collecting crystal-probe activations ...")
    acts, layer_idx = collect_activations(model, tok, model_key, prompts, device)

    # ── Test 4 setup: subset with/without preamble
    sub_n = min(120, len(prompts))
    sub_idx = list(np.random.default_rng(seed + 1).permutation(len(prompts))[:sub_n])
    sub_prompts = [prompts[i] for i in sub_idx]
    sub_labels = [labels[i] for i in sub_idx]
    log("  Collecting preamble-OFF subset ...")
    acts_off, _ = collect_activations(model, tok, model_key, sub_prompts, device)
    log("  Collecting preamble-ON subset ...")
    acts_on, _ = collect_activations(
        model, tok, model_key,
        [LAMBDA_PREAMBLE + p for p in sub_prompts], device)

    # ── Test 3 setup: fake combinators
    fake_prompts, fake_labels = [], []
    for cat, ps in FAKE_PROBES.items():
        fake_prompts.extend(ps)
        fake_labels.extend([cat] * len(ps))
    log("  Collecting fake-combinator activations ...")
    acts_fake, _ = collect_activations(model, tok, model_key, fake_prompts, device)

    del model, tok
    gc.collect()
    import torch
    if device == "mps" and torch.backends.mps.is_available():
        torch.mps.empty_cache()

    # ── depth-averaged PCA projection helper
    def proj_of(act_dict, idxs):
        parts = [pca_project(act_dict[li]) for li in idxs]
        # concatenate depth projections (each PCA'd independently)
        return np.concatenate(parts, axis=1)

    proj_full = proj_of(acts, layer_idx)

    out = {"model": MODELS[model_key][0], "model_key": model_key,
           "n_perm": n_perm, "seed": seed}

    # ════ TEST 1 — permutation null (KIBC core + full crystal nodes) ════
    for node_set, tag in [(CORE, "core_KIBC"), (CRYSTAL_NODES, "all9")]:
        true_m = structure_metrics(proj_full, labels, node_set)
        null = permutation_null(proj_full, labels, node_set, n_perm, rng)
        out[f"test1_{tag}"] = {
            "nodes": node_set,
            "true": {k: true_m[k] for k in
                     ["separation", "offdiag_var", "phi_fit_err", "eig_ratios"]},
            "p_separation": pval_high(true_m["separation"], null["separation"]),
            "p_offdiag_var": pval_high(true_m["offdiag_var"], null["offdiag_var"]),
            "p_phi_fit": pval_low(true_m["phi_fit_err"], null["phi_fit_err"]),
            "null_sep_mean": float(np.mean(null["separation"])),
            "null_sep_std": float(np.std(null["separation"])),
        }
        v = out[f"test1_{tag}"]
        log(f"\n  [TEST 1 {tag}] separation true={true_m['separation']:+.4f} "
            f"null={v['null_sep_mean']:+.4f}±{v['null_sep_std']:.4f} "
            f"p={v['p_separation']:.4f} | phi_fit p={v['p_phi_fit']:.4f}")

    # ════ TEST 2 — pure-prose filter (drop λ probes) ════
    keep = [i for i, h in enumerate(has_lambda) if not h]
    proj_nolam = proj_full[keep]
    labels_nolam = [labels[i] for i in keep]
    m_full = structure_metrics(proj_full, labels, CORE)
    m_nolam = structure_metrics(proj_nolam, labels_nolam, CORE)
    null_nolam = permutation_null(proj_nolam, labels_nolam, CORE, n_perm, rng)
    out["test2_pure_prose"] = {
        "n_dropped": int(sum(has_lambda)),
        "full_separation": m_full["separation"],
        "nolambda_separation": m_nolam["separation"],
        "full_phi_fit": m_full["phi_fit_err"],
        "nolambda_phi_fit": m_nolam["phi_fit_err"],
        "p_separation_nolambda": pval_high(m_nolam["separation"], null_nolam["separation"]),
        "matrix_cos": float(
            np.dot(np.array(m_full["matrix"]).ravel(),
                   np.array(m_nolam["matrix"]).ravel())
            / (np.linalg.norm(m_full["matrix"]) * np.linalg.norm(m_nolam["matrix"]))),
    }
    log(f"\n  [TEST 2] sep full={m_full['separation']:+.4f} "
        f"no-λ={m_nolam['separation']:+.4f} "
        f"(dropped {out['test2_pure_prose']['n_dropped']}) "
        f"p_no-λ={out['test2_pure_prose']['p_separation_nolambda']:.4f}")

    # ════ TEST 3 — fake combinators ════
    proj_fake = proj_of(acts_fake, layer_idx)
    fake_nodes = list(FAKE_PROBES.keys())
    m_fake = structure_metrics(proj_fake, fake_labels, fake_nodes)
    null_fake = permutation_null(proj_fake, fake_labels, fake_nodes, n_perm, rng)
    out["test3_fake"] = {
        "nodes": fake_nodes,
        "separation": m_fake["separation"],
        "phi_fit_err": m_fake["phi_fit_err"],
        "eig_ratios": m_fake["eig_ratios"],
        "p_separation": pval_high(m_fake["separation"], null_fake["separation"]),
        "p_phi_fit": pval_low(m_fake["phi_fit_err"], null_fake["phi_fit_err"]),
        "kibc_separation": m_full["separation"],
        "kibc_phi_fit": structure_metrics(proj_full, labels, CORE)["phi_fit_err"],
    }
    log(f"\n  [TEST 3] FAKE sep={m_fake['separation']:+.4f} "
        f"(p={out['test3_fake']['p_separation']:.4f}) vs "
        f"KIBC sep={m_full['separation']:+.4f} | "
        f"FAKE phi_fit={m_fake['phi_fit_err']:.4f}")

    # ════ TEST 4 — preamble A/B ════
    proj_off = proj_of(acts_off, layer_idx)
    proj_on = proj_of(acts_on, layer_idx)
    m_off = structure_metrics(proj_off, sub_labels, CORE)
    m_on = structure_metrics(proj_on, sub_labels, CORE)
    mo, mn = np.array(m_off["matrix"]), np.array(m_on["matrix"])
    out["test4_preamble"] = {
        "n_subset": sub_n,
        "sep_off": m_off["separation"],
        "sep_on": m_on["separation"],
        "phi_off": m_off["phi_fit_err"],
        "phi_on": m_on["phi_fit_err"],
        "matrix_cos_on_off": float(
            np.dot(mo.ravel(), mn.ravel())
            / (np.linalg.norm(mo) * np.linalg.norm(mn))),
    }
    log(f"\n  [TEST 4] sep preamble OFF={m_off['separation']:+.4f} "
        f"ON={m_on['separation']:+.4f} "
        f"matrix_cos={out['test4_preamble']['matrix_cos_on_off']:.4f}")

    # save the full KIBC matrix for cross-model comparison
    out["kibc_matrix_core"] = m_full["matrix"]
    out["kibc_matrix_all9"] = structure_metrics(proj_full, labels, CRYSTAL_NODES)["matrix"]
    return out


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["qwen3-0.6b"],
                    choices=list(MODELS.keys()))
    ap.add_argument("--device", default="mps")
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    all_out = {}
    for mk in args.models:
        log("═" * 60)
        log(f"  CRYSTAL VALIDITY — {mk}")
        log("═" * 60)
        res = run_model(mk, args.n_perm, args.device, args.seed)
        all_out[mk] = res
        with open(RESULTS_DIR / f"{mk}.json", "w") as f:
            json.dump(res, f, indent=2)
        log(f"  saved → {RESULTS_DIR / f'{mk}.json'}")

    # ── cross-model KIBC correlation (the r≈0.998 re-test) ──
    if len(all_out) >= 2:
        log("\n═══ Cross-model KIBC matrix correlation (upper triangle) ═══")
        keys = list(all_out.keys())
        cross = {}
        for a in range(len(keys)):
            for b in range(a + 1, len(keys)):
                ma = np.array(all_out[keys[a]]["kibc_matrix_all9"])
                mb = np.array(all_out[keys[b]]["kibc_matrix_all9"])
                iu = np.triu_indices_from(ma, k=1)
                r = float(np.corrcoef(ma[iu], mb[iu])[0, 1])
                cross[f"{keys[a]}__{keys[b]}"] = r
                log(f"  {keys[a]} ↔ {keys[b]}: r = {r:+.4f}")
        with open(RESULTS_DIR / "cross_model.json", "w") as f:
            json.dump(cross, f, indent=2)

    log("\nDONE.")


if __name__ == "__main__":
    main()
