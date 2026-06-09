#!/usr/bin/env python3
"""Audit #3 — The 9 FFN modes: real or k-means-imposed?

The claim (`mode-semantics.md`, s194; `tiny-classifier-ternary.md`, s192):
  "There are 9 ternary FFN modes per layer; a tiny linear classifier
   predicts them at 98-100% accuracy."

Suspected confound (audit-registry.md, failure modes #2 trivial-statistic
and #6 surface-confound):
  - k-means at k=9 ALWAYS returns 9 clusters. The count is chosen, not found.
  - Classifier accuracy is circular: the classifier is trained to predict
    the very k-means labels it is then scored against. Since mode is a
    near-linear function of the FFN input (gate = SiLU(W_g x)), ANY k-means
    partition pulls back to near-linearly-separable regions in input space,
    so accuracy is high for ANY k — it cannot single out 9.

The named discriminating control (registry #3):
  cluster-validity null — silhouette / gap-statistic at k=9 vs random data
  and vs k=8,10,...; does "9" survive a held-out elbow test, or is it
  imposed? Cross-reference the L0-characterization negative-silhouette finding.

Instruments
-----------
  1. Gap statistic (Tibshirani 2001) — log within-cluster dispersion of REAL
     gate patterns vs B matched-null reference datasets, across k. Optimal-k
     rule: smallest k with Gap(k) >= Gap(k+1) - s_{k+1}. Does it pick ~9?
  2. Silhouette excess — sil_real(k) - mean(sil_null(k)). Is k=9 distinguished
     above the matched null, or at/below it (as L0/L15 already hinted: ~0.05)?
  3. Inertia elbow (kneedle: max distance to the (k0,kN) chord). Does the
     elbow land near 9?
  4. Classifier-circularity curve — linear softmax classifier (FFN input ->
     k-means label), held-out test accuracy across k. High-AND-FLAT ==> the
     "98-100%" is generic linear separability of any convex partition, NOT
     evidence for 9. A label-permutation run gives the chance floor.

Two matched nulls (bracket the "no clusters but same cloud shape" hypothesis):
  - pca_gauss : Gaussian matched to the data's PCA covariance (top comps).
                Preserves the blob's dominant correlation structure; destroys
                any genuine multi-modality. (Strong null.)
  - shuffle   : per-feature independent permutation across tokens. Preserves
                every marginal exactly; destroys joint/cluster structure.

Verdict logic
-------------
  REAL (k=9 distinguished)  : gap optimal-k ~= 9 AND sil_excess(9) >> 0
                             AND classifier accuracy peaks/cliffs near 9.
  IMPOSED (k-means artifact): no distinguished 9 (gap monotone or picks ~2),
                             sil_excess(9) ~ 0, classifier high-and-flat.

This separates three distinct claims that mode-semantics.md conflates:
  (geometric)  "9 natural clusters exist"        <- tested here
  (circular)   "98-100% accuracy proves 9"       <- tested here
  (functional) "9 ternary programs ~= 1x PPL"    <- NOT tested here (s196);
               independent and may stand regardless of this verdict.

Usage:
  uv run python scripts/experiments/mode_cluster_validity.py \
    --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from verbum.probes.library import crystal_probes  # noqa: E402

# ══════════════════════════════════════════════════════════════════════
# Diverse calibration texts (broad syntactic + domain coverage)
# ══════════════════════════════════════════════════════════════════════

TEXTS = [
    "The theory of general relativity describes gravity as the curvature of spacetime.",
    "Photosynthesis converts carbon dioxide and water into glucose and oxygen.",
    "DNA carries genetic information in a double helix structure discovered by Watson and Crick.",
    "Quantum mechanics describes the behavior of particles at the atomic and subatomic scale.",
    "The human brain contains approximately 86 billion neurons connected by trillions of synapses.",
    "Black holes form when massive stars collapse under their own gravitational force.",
    "The periodic table organizes elements by atomic number and electron configuration.",
    "Enzymes are biological catalysts that speed up chemical reactions in living organisms.",
    "She walked through the ancient forest, her footsteps muffled by fallen leaves.",
    "The old man sat quietly by the river, watching the fish jump at dawn.",
    "Three children ran laughing through the sunlit meadow while their dog chased butterflies.",
    "He opened the letter carefully, his hands trembling with anticipation.",
    "The ship sailed slowly into the harbor as the storm clouds gathered on the horizon.",
    "A woman stood at the window, silently watching the rain fall on the empty street.",
    "The detective examined the crime scene, noting every detail with practiced precision.",
    "Birds sang in the treetops as morning light filtered through the canopy above.",
    "In a large mixing bowl, combine the flour, sugar, and baking powder.",
    "To solve this equation, first isolate the variable on one side.",
    "Install the software by running the setup wizard and following the prompts.",
    "Remove the old filter carefully and replace it with the new one.",
    "The patient should take two tablets every four hours with food.",
    "Preheat the oven to 350 degrees Fahrenheit before placing the dish inside.",
    "Always wash your hands thoroughly before handling raw ingredients.",
    "Connect the cable to the port on the left side of the device.",
    "The committee voted unanimously to approve the new environmental regulations.",
    "Democracy originated in ancient Greece, specifically in the city-state of Athens.",
    "The president addressed the nation regarding the economic recovery plan.",
    "International trade agreements require careful negotiation between multiple parties.",
    "The Supreme Court ruled that the legislation was constitutional.",
    "Parliament debated the proposed amendment for six consecutive hours.",
    "The treaty established a framework for peaceful cooperation between nations.",
    "Voters expressed strong opposition to the proposed tax increase.",
    "The function takes two arguments and returns their composition as a new callable.",
    "Machine learning algorithms can be categorized as supervised or unsupervised.",
    "The API endpoint accepts POST requests with JSON payload and returns status codes.",
    "Arrays are contiguous blocks of memory that allow constant-time access by index.",
    "The compiler transforms source code into machine-executable binary through multiple passes.",
    "Hash tables provide average constant-time lookup by mapping keys to bucket indices.",
    "The neural network learns feature representations through gradient descent optimization.",
    "Recursive functions call themselves with progressively smaller subproblems until reaching a base case.",
    "What time does the store close today?",
    "I think we should probably leave now before it gets too dark outside.",
    "Yes, that makes sense. Let me check the schedule and get back to you.",
    "The weather has been absolutely terrible this week, hasn't it?",
    "Can you believe they actually won the championship after being down three games?",
    "Would you mind passing me the salt, please?",
    "That restaurant on Main Street serves the best pasta I have ever tasted.",
    "How long have you been working at this company?",
    "The book that the professor recommended, which had been out of print for decades, was finally reissued.",
    "Although the experiment failed initially, the researchers persisted and eventually found the solution.",
    "Not only did the company exceed its quarterly targets, but it also expanded into three new markets.",
    "Having carefully considered all the evidence, the jury returned a verdict of not guilty.",
    "The discovery, which some called the most significant breakthrough of the century, changed everything.",
    "Neither the students nor the teachers were satisfied with the proposed curriculum changes.",
    "Whoever finishes the assignment first will receive extra credit from the professor.",
    "The more carefully you analyze the data, the more patterns you will discover.",
    "The primary colors are red, blue, and yellow.",
    "Countries in the European Union include France, Germany, Italy, Spain, and Poland.",
    "The Fibonacci sequence begins with 1, 1, 2, 3, 5, 8, 13, 21.",
    "There are four seasons: spring, summer, autumn, and winter.",
    "The planets in order from the Sun are Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune.",
    "The population of Tokyo is approximately 14 million people in the city proper.",
    "Pi is approximately equal to 3.14159265 and is an irrational number.",
    "The distance from Earth to the Moon is about 384,400 kilometers.",
    "Einstein's famous equation E equals mc squared relates mass and energy.",
    "The temperature dropped to negative 20 degrees Celsius during the winter storm.",
]

# Layers spanning the compilation phases + L0 as a known-no-cluster reference
# (L0 silhouette was negative at all k in l0-characterization — the worst case
#  our null should clearly flag).
DEFAULT_LAYERS = [0, 3, 15, 20, 35]


def log(msg=""):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


def get_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    if hasattr(model, "gpt_neox") and hasattr(model.gpt_neox, "layers"):
        return model.gpt_neox.layers
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


# ══════════════════════════════════════════════════════════════════════
# Collection — gate patterns + FFN inputs per layer
# ══════════════════════════════════════════════════════════════════════

def collect_layer(model, tokenizer, layer_idx, device, prompts):
    """Return (gate_patterns [N,intermediate], inputs [N,d_model])."""
    layers = get_layers(model)
    mlp = layers[layer_idx].mlp
    captured = {}

    def pre_hook(module, inp):
        x = inp[0] if isinstance(inp, tuple) else inp
        captured["input"] = x.detach().float()

    def gate_hook(module, inp, out):
        captured["gate_raw"] = out.detach().float()

    h_pre = mlp.register_forward_pre_hook(pre_hook)
    h_gate = mlp.gate_proj.register_forward_hook(gate_hook)

    all_gate, all_inp = [], []
    for prompt in prompts:
        captured.clear()
        enc = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128)
        enc_dev = {k: v.to(device) for k, v in enc.items()}
        with torch.no_grad():
            model(**enc_dev)
        if "input" not in captured or "gate_raw" not in captured:
            continue
        gate_raw = captured["gate_raw"][0]
        gate = (gate_raw * torch.sigmoid(gate_raw)).cpu().numpy()
        all_gate.append(gate)
        all_inp.append(captured["input"][0].cpu().numpy())

    h_pre.remove()
    h_gate.remove()
    return np.concatenate(all_gate, axis=0), np.concatenate(all_inp, axis=0)


# ══════════════════════════════════════════════════════════════════════
# Matched nulls
# ══════════════════════════════════════════════════════════════════════

def make_pca_gauss_null(X, rng, n_comp=100):
    """Gaussian matched to X's PCA covariance (top n_comp comps) + per-dim
    residual variance. Preserves the cloud's dominant correlation structure;
    contains NO cluster structure by construction."""
    n, d = X.shape
    mu = X.mean(axis=0)
    Xc = X - mu
    n_comp = min(n_comp, n - 1, d)
    # economy SVD for principal axes
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    comp = Vt[:n_comp]                      # (n_comp, d)
    var = (S[:n_comp] ** 2) / max(1, n - 1)  # per-component variance
    # residual isotropic variance from the tail (keeps total spread honest)
    total_var = (Xc ** 2).sum() / max(1, n - 1)
    resid = max(0.0, total_var - var.sum()) / max(1, d)
    z = rng.standard_normal((n, n_comp)) * np.sqrt(var)[None, :]
    Y = z @ comp + mu
    if resid > 0:
        Y = Y + rng.standard_normal((n, d)) * np.sqrt(resid)
    return Y.astype(np.float32)


def make_shuffle_null(X, rng):
    """Per-feature independent permutation across tokens. Preserves every
    marginal exactly; destroys all joint/cluster structure."""
    Y = X.copy()
    for j in range(Y.shape[1]):
        rng.shuffle(Y[:, j])
    return Y


# ══════════════════════════════════════════════════════════════════════
# Cluster validity over k
# ══════════════════════════════════════════════════════════════════════

def kmeans_fit(X, k, seed):
    km = KMeans(n_clusters=k, random_state=seed, n_init=5)
    labels = km.fit_predict(X)
    return labels, float(km.inertia_)


def sil(X, labels, sil_n, seed):
    n = len(X)
    if len(set(labels)) < 2:
        return 0.0
    if n > sil_n:
        idx = np.random.RandomState(seed).choice(n, sil_n, replace=False)
        return float(silhouette_score(X[idx], labels[idx]))
    return float(silhouette_score(X, labels))


def validity_sweep(X, ks, n_ref, sil_n, rng, log_prefix=""):
    """Gap statistic + silhouette excess across k for two matched nulls."""
    # Real
    real = {}
    log(f"{log_prefix}  real:")
    for k in ks:
        labels, inertia = kmeans_fit(X, k, seed=42)
        s = sil(X, labels, sil_n, seed=99)
        real[k] = {"logW": float(np.log(inertia + 1e-12)), "inertia": inertia, "sil": s}
        log(f"{log_prefix}    k={k:>3d}  logW={real[k]['logW']:.4f}  sil={s:+.4f}")

    nulls = {}
    for null_name, maker in (("pca_gauss", make_pca_gauss_null), ("shuffle", make_shuffle_null)):
        log(f"{log_prefix}  null={null_name} (B={n_ref}):")
        logW = np.zeros((n_ref, len(ks)))
        sils = np.zeros((n_ref, len(ks)))
        for b in range(n_ref):
            Y = maker(X, rng) if null_name == "shuffle" else maker(X, rng)
            for ki, k in enumerate(ks):
                labels, inertia = kmeans_fit(Y, k, seed=1000 + b)
                logW[b, ki] = np.log(inertia + 1e-12)
                sils[b, ki] = sil(Y, labels, sil_n, seed=1000 + b)
        nulls[null_name] = {
            "logW_mean": logW.mean(axis=0),
            "logW_std": logW.std(axis=0),
            "sil_mean": sils.mean(axis=0),
            "sil_std": sils.std(axis=0),
        }
        for ki, k in enumerate(ks):
            log(f"{log_prefix}    k={k:>3d}  logW={logW.mean(0)[ki]:.4f}±{logW.std(0)[ki]:.3f}  "
                f"sil={sils.mean(0)[ki]:+.4f}")

    # Gap statistic + Tibshirani optimal-k (per null)
    out = {"ks": list(ks), "real": real, "nulls": {}, "gap": {}}
    real_logW = np.array([real[k]["logW"] for k in ks])
    real_sil = np.array([real[k]["sil"] for k in ks])
    for null_name, nd in nulls.items():
        gap = nd["logW_mean"] - real_logW
        sk = nd["logW_std"] * np.sqrt(1.0 + 1.0 / n_ref)
        sil_excess = real_sil - nd["sil_mean"]
        # Tibshirani: smallest k with gap[k] >= gap[k+1] - sk[k+1]
        opt_k = None
        for i in range(len(ks) - 1):
            if gap[i] >= gap[i + 1] - sk[i + 1]:
                opt_k = ks[i]
                break
        if opt_k is None:
            opt_k = ks[int(np.argmax(gap))]
        out["nulls"][null_name] = {
            "logW_mean": nd["logW_mean"].tolist(),
            "logW_std": nd["logW_std"].tolist(),
            "sil_mean": nd["sil_mean"].tolist(),
            "sil_std": nd["sil_std"].tolist(),
        }
        out["gap"][null_name] = {
            "gap": gap.tolist(),
            "s_k": sk.tolist(),
            "sil_excess": sil_excess.tolist(),
            "tibshirani_optimal_k": int(opt_k),
            "argmax_gap_k": int(ks[int(np.argmax(gap))]),
        }
        log(f"{log_prefix}  [{null_name}] Tibshirani optimal-k = {opt_k}  "
            f"(argmax gap k={ks[int(np.argmax(gap))]})")

    # Inertia elbow (kneedle: max perpendicular distance to chord on log-inertia)
    out["elbow_k"] = _kneedle(np.array(ks, dtype=float), real_logW)
    log(f"{log_prefix}  inertia elbow (kneedle) k = {out['elbow_k']}")
    return out


def _kneedle(ks, logW):
    """Elbow = point of max distance from the line joining first & last."""
    x = (ks - ks[0]) / (ks[-1] - ks[0] + 1e-12)
    y = (logW - logW[0]) / (logW[-1] - logW[0] + 1e-12)
    # distance from straight chord y=x (both normalized, decreasing curve)
    dist = np.abs(y - x)
    return int(ks[int(np.argmax(dist))])


# ══════════════════════════════════════════════════════════════════════
# Classifier-circularity control
# ══════════════════════════════════════════════════════════════════════

def train_linear_classifier(X, y, n_classes, epochs=150, lr=0.05, seed=0):
    """Linear softmax classifier; returns held-out test accuracy."""
    g = torch.Generator().manual_seed(seed)
    n = len(X)
    perm = torch.randperm(n, generator=g)
    n_tr = int(0.8 * n)
    tr, te = perm[:n_tr], perm[n_tr:]
    Xt = torch.tensor(X, dtype=torch.float32)
    yt = torch.tensor(y, dtype=torch.long)
    W = (torch.randn(n_classes, X.shape[1], generator=g) * 0.01).requires_grad_(True)
    opt = torch.optim.Adam([W], lr=lr)
    for _ in range(epochs):
        logits = Xt[tr] @ W.T
        loss = F.cross_entropy(logits, yt[tr])
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        acc_tr = float((Xt[tr] @ W.T).argmax(-1).eq(yt[tr]).float().mean())
        acc_te = float((Xt[te] @ W.T).argmax(-1).eq(yt[te]).float().mean())
    return acc_tr, acc_te


def circularity_curve(inputs, gate, ks, rng, log_prefix=""):
    """Train input->kmeans-label classifier across k. High-AND-FLAT ==>
    accuracy is generic linear separability of any convex partition, not
    evidence for 9. Permuted-label run gives the chance floor at k=9."""
    out = {"ks": list(ks), "test_acc": {}, "train_acc": {}}
    log(f"{log_prefix}  classifier accuracy vs k (FFN input -> kmeans label):")
    for k in ks:
        labels, _ = kmeans_fit(gate, k, seed=42)
        acc_tr, acc_te = train_linear_classifier(inputs, labels, k, seed=0)
        out["test_acc"][int(k)] = acc_te
        out["train_acc"][int(k)] = acc_tr
        log(f"{log_prefix}    k={k:>3d}  test_acc={acc_te:.1%}  (train {acc_tr:.1%})")
    # chance floor: permute labels at k=9 (or nearest available)
    k9 = 9 if 9 in ks else ks[len(ks) // 2]
    labels, _ = kmeans_fit(gate, k9, seed=42)
    perm_labels = labels.copy()
    rng.shuffle(perm_labels)
    _, acc_perm = train_linear_classifier(inputs, perm_labels, k9, seed=0)
    out["permuted_label_acc_k9"] = acc_perm
    out["uniform_chance_k9"] = 1.0 / k9
    log(f"{log_prefix}  permuted-label test_acc @k={k9}: {acc_perm:.1%} "
        f"(uniform chance {1.0/k9:.1%})")
    return out


# ══════════════════════════════════════════════════════════════════════
# Per-layer driver
# ══════════════════════════════════════════════════════════════════════

def run_layer(model, tokenizer, layer_idx, device, prompts, ks,
              n_ref, sil_n, max_tokens, seed):
    log(f"\n{'═'*70}")
    log(f"  LAYER {layer_idx}")
    log(f"{'═'*70}")
    t0 = time.time()
    gate, inputs = collect_layer(model, tokenizer, layer_idx, device, prompts)
    n = len(gate)
    log(f"  collected {n} tokens  (gate {gate.shape[1]}-dim, input {inputs.shape[1]}-dim)")

    rng = np.random.default_rng(seed)
    if n > max_tokens:
        idx = rng.choice(n, max_tokens, replace=False)
        gate, inputs = gate[idx], inputs[idx]
        log(f"  subsampled to {max_tokens} tokens")

    validity = validity_sweep(gate, ks, n_ref, sil_n, rng, log_prefix="  ")
    circ = circularity_curve(inputs, gate, ks, rng, log_prefix="  ")

    log(f"  layer {layer_idx} done in {time.time()-t0:.1f}s")
    return {
        "layer_idx": layer_idx,
        "n_tokens": int(n),
        "n_used": len(gate),
        "validity": validity,
        "circularity": circ,
        "elapsed_s": round(time.time() - t0, 1),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="mps")
    p.add_argument("--layers", type=int, nargs="+", default=None)
    p.add_argument("--n-ref", type=int, default=10, help="null reference datasets (B)")
    p.add_argument("--max-tokens", type=int, default=2500)
    p.add_argument("--sil-n", type=int, default=1500, help="silhouette subsample")
    p.add_argument("--n-crystal", type=int, default=150)
    p.add_argument("--seed", type=int, default=12)
    args = p.parse_args()

    ks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 24, 32]
    layers = args.layers or DEFAULT_LAYERS

    log(f"\n{'='*70}")
    log("  AUDIT #3 — Are the 9 FFN modes real or k-means-imposed?")
    log(f"{'='*70}")
    log(f"  Model: {args.model}   Device: {args.device}")
    log(f"  Layers: {layers}   k-range: {ks}")
    log(f"  Nulls: pca_gauss + shuffle (B={args.n_ref})")
    log(f"  max_tokens={args.max_tokens}  sil_n={args.sil_n}  seed={args.seed}")

    dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
    log(f"\n  Loading {args.model} ({dtype})...")
    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    n_layers = model.config.num_hidden_layers
    log(f"  layers={n_layers} d_model={model.config.hidden_size} "
        f"intermediate={model.config.intermediate_size}")
    layers = [_l for _l in layers if _l < n_layers]

    prompts = list(TEXTS)
    prompts += [pr.prompt for pr in crystal_probes()[:args.n_crystal]]

    results = {
        "audit": "3-mode-cluster-validity",
        "model": args.model,
        "k_range": ks,
        "n_ref": args.n_ref,
        "max_tokens": args.max_tokens,
        "sil_n": args.sil_n,
        "seed": args.seed,
        "n_prompts": len(prompts),
        "layers": {},
    }
    for li in layers:
        results["layers"][str(li)] = run_layer(
            model, tokenizer, li, args.device, prompts, ks,
            args.n_ref, args.sil_n, args.max_tokens, args.seed)

    # ── Verdict summary ────────────────────────────────────────────────
    log(f"\n{'='*70}")
    log("  VERDICT SUMMARY")
    log(f"{'='*70}")
    log(f"  {'layer':>5} | {'gap_optk(pca/shuf)':>20} | {'elbow':>5} | "
        f"{'sil@9(real/pca/shuf)':>24} | {'acc@9':>6} {'acc@2':>6} {'acc@32':>6}")
    for li in layers:
        lr = results["layers"][str(li)]
        v = lr["validity"]
        ks_list = v["ks"]
        i9 = ks_list.index(9) if 9 in ks_list else len(ks_list) // 2
        sil_r = v["real"][9]["sil"] if 9 in v["real"] else v["real"][ks_list[i9]]["sil"]
        sil_pg = v["nulls"]["pca_gauss"]["sil_mean"][i9]
        sil_sh = v["nulls"]["shuffle"]["sil_mean"][i9]
        optk_pg = v["gap"]["pca_gauss"]["tibshirani_optimal_k"]
        optk_sh = v["gap"]["shuffle"]["tibshirani_optimal_k"]
        c = lr["circularity"]["test_acc"]
        log(f"  {li:>5} | {optk_pg:>9d}/{optk_sh:<9d} | {v['elbow_k']:>5} | "
            f"{sil_r:+.3f}/{sil_pg:+.3f}/{sil_sh:+.3f} | "
            f"{c.get(9, float('nan')):.1%} {c.get(2, float('nan')):.1%} {c.get(32, float('nan')):.1%}")

    log("\n  Reading: if gap optimal-k is far from 9 and sil@9(real) ~= sil@9(null)")
    log("  and classifier accuracy is high-and-flat across k, then '9' is IMPOSED")
    log("  by k-means, not a natural count. (Functional '9 ternary programs ~= 1x")
    log("  PPL' is a separate claim, untouched here.)")

    out_dir = _PROJECT_ROOT / "results" / "mode-cluster-validity"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.model.replace('/', '_')}.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    log(f"\n  saved -> {out_path}")
    log(f"\n{'='*70}\n  DONE\n{'='*70}\n")


if __name__ == "__main__":
    main()
