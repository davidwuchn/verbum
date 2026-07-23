#!/usr/bin/env python3
"""J-space v2 — corrected probe construction (s269 audit of s263 EXP1/EXP3).

    λ jspace_v2(model). operator ≠ direction | operator ≡ Jacobian_structure
      E1 operator:  position-resolved attribution AT THE RESULT POSITION on
                    token-matched minimal pairs (same token multiset, roles
                    swapped) → span-level structural signatures + pair nulls
      E2 verbalize: halt-state (WHNF) vs KIBC operator verbalizability at the
                    logit-lens plateau → halt-lexicon hit rate vs shuffled
      E4 coupling:  gate sign-CMR opcode centroid → residual via W_gate^T →
                    broadcast KL vs matched-random ∧ shuffled-op null

PRE-REGISTERED s269, before data:
  P-E1: K annihilation ratio > 1 and flips with pair swap; C attribution
        anti-correlates across swap; I copy-mass high; B intermediate-mass
        (2-hop) > matched 1-hop. All vs shuffled-pair nulls.
  P-E2: WHNF probes verbalize halt lexicon above shuffled null; KIBC operator
        probes do NOT (visibility asymmetry — operators are not bus content).
  P-E4: opcode-centroid injections broadcast above matched-random IFF the
        routing lattice is coupled to the value bus; shuffled-op null decides
        whether coupling is op-specific.

Corrections over s263 (all three were EXP3's own unactioned diagnosis):
  1. result-position readout (not last-token aggregate)
  2. token-matched pairs (kills the copy_mass surface confound)
  3. matrix/span structure (not scalar aggregates)
  4. operator read via Jacobian structure; verbalization tested ONLY where
     the theory predicts bus content (halt state), not for operators

Usage:
    uv run python scripts/experiments/jspace_v2.py --self-test
    uv run python scripts/experiments/jspace_v2.py --model Qwen/Qwen3.6-27B \
        --device mps
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "opcodes"))

from verbum import jlens  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "jspace-v2"
N_PERM = 1000
RNG = np.random.default_rng(269)

# ── E1: token-matched minimal pairs with span annotations ────────────────────
# Each entry: (prompt, spans, target_word). Spans name the argument substrings.
# Within a pair the token multiset is identical; only the ROLES swap. The
# signature must therefore come from routing, not surface statistics.

K_PAIRS = [  # selection: attribution should concentrate on selected, ~0 on discarded
    ({"prompt": "The fox, not the hound, ate the stolen food, so the eater was the",
      "selected": "fox", "discarded": "hound", "target": " fox"},
     {"prompt": "The hound, not the fox, ate the stolen food, so the eater was the",
      "selected": "hound", "discarded": "fox", "target": " hound"}),
    ({"prompt": "Mary, rather than John, signed the letter, so the signer was",
      "selected": "Mary", "discarded": "John", "target": " Mary"},
     {"prompt": "John, rather than Mary, signed the letter, so the signer was",
      "selected": "John", "discarded": "Mary", "target": " John"}),
    ({"prompt": "The oak, not the pine, fell in the storm, so the fallen tree was the",
      "selected": "oak", "discarded": "pine", "target": " oak"},
     {"prompt": "The pine, not the oak, fell in the storm, so the fallen tree was the",
      "selected": "pine", "discarded": "oak", "target": " pine"}),
    ({"prompt": "Rome, rather than Paris, hosted the summit, so the host city was",
      "selected": "Rome", "discarded": "Paris", "target": " Rome"},
     {"prompt": "Paris, rather than Rome, hosted the summit, so the host city was",
      "selected": "Paris", "discarded": "Rome", "target": " Paris"}),
    ({"prompt": "The silver coin, not the gold coin, was stolen, "
                "so the missing one was the",
      "selected": "silver", "discarded": "gold", "target": " silver"},
     {"prompt": "The gold coin, not the silver coin, was stolen, "
                "so the missing one was the",
      "selected": "gold", "discarded": "silver", "target": " gold"}),
    ({"prompt": "The red cup, not the blue cup, broke on the floor, "
                "so the broken one was the",
      "selected": "red", "discarded": "blue", "target": " red"},
     {"prompt": "The blue cup, not the red cup, broke on the floor, "
                "so the broken one was the",
      "selected": "blue", "discarded": "red", "target": " blue"}),
]

C_PAIRS = [  # swap: attribution over the two argument spans should invert
    ({"prompt": "The fox chased the hound, so the one being chased was the",
      "arg1": "fox", "arg2": "hound", "target": " hound"},
     {"prompt": "The hound chased the fox, so the one being chased was the",
      "arg1": "hound", "arg2": "fox", "target": " fox"}),
    ({"prompt": "Alice paid Bob, so the one receiving money was",
      "arg1": "Alice", "arg2": "Bob", "target": " Bob"},
     {"prompt": "Bob paid Alice, so the one receiving money was",
      "arg1": "Bob", "arg2": "Alice", "target": " Alice"}),
    ({"prompt": "The cat feared the dog, so the frightening one was the",
      "arg1": "cat", "arg2": "dog", "target": " dog"},
     {"prompt": "The dog feared the cat, so the frightening one was the",
      "arg1": "dog", "arg2": "cat", "target": " cat"}),
    ({"prompt": "The teacher praised the student, so the one being praised was the",
      "arg1": "teacher", "arg2": "student", "target": " student"},
     {"prompt": "The student praised the teacher, so the one being praised was the",
      "arg1": "student", "arg2": "teacher", "target": " teacher"}),
    ({"prompt": "The hawk hunted the mouse, so the hunted one was the",
      "arg1": "hawk", "arg2": "mouse", "target": " mouse"},
     {"prompt": "The mouse hunted the hawk, so the hunted one was the",
      "arg1": "mouse", "arg2": "hawk", "target": " hawk"}),
    ({"prompt": "Emma followed Liam, so the one being followed was",
      "arg1": "Emma", "arg2": "Liam", "target": " Liam"},
     {"prompt": "Liam followed Emma, so the one being followed was",
      "arg1": "Liam", "arg2": "Emma", "target": " Emma"}),
]

I_PROBES = [  # copy: attribution should concentrate on the copy source
    {"prompt": "The password is otter. Remember it well: the password is",
     "source": "otter", "target": " otter"},
    {"prompt": "The code word is maple. Repeat it back: the code word is",
     "source": "maple", "target": " maple"},
    {"prompt": "Her name is Vera. Say it again: her name is",
     "source": "Vera", "target": " Vera"},
]

B_PAIRS = [  # composition: 2-hop routes through the intermediate span
    ({"prompt": "The key opens the box and the box holds the coin, "
                "so the key leads to the",
      "intermediate": "box", "target": " coin", "hops": 2},
     {"prompt": "The key holds the coin and the box opens the box, "
                "so the key leads to the",
      "intermediate": "box", "target": " coin", "hops": 1}),
    ({"prompt": "The wire powers the lamp and the lamp lights the room, "
                "so the wire ultimately lights the",
      "intermediate": "lamp", "target": " room", "hops": 2},
     {"prompt": "The wire lights the room and the lamp powers the lamp, "
                "so the wire ultimately lights the",
      "intermediate": "lamp", "target": " room", "hops": 1}),
]

# ── E2: halt-state vs operator verbalization ─────────────────────────────────

HALT_LEXICON = (
    "done", "finished", "complete", "completed", "final", "answer",
    "result", "already", "value", "nothing", "end", "stop", "resolved",
    "settled", "given", "fixed", "constant",
)


# ── attribution machinery (result-position, per-position magnitudes) ─────────


def token_span(tok, prompt: str, word: str) -> list[int]:
    """Token indices covering the first occurrence of `word` in `prompt`."""
    enc = tok(prompt, return_offsets_mapping=True, add_special_tokens=True)
    start = prompt.index(word)
    end = start + len(word)
    return [
        i for i, (a, b) in enumerate(enc["offset_mapping"])
        if a < end and b > start and b > a
    ]


def input_attribution(model, tok, prompt: str, target: str, device: str
                      ) -> np.ndarray:
    """|d logit(target_first_token) / d input_embedding| per position, L2 over
    embed dim — read at the RESULT position (the final prompt token)."""
    enc = tok(prompt, return_tensors="pt").to(device)
    ids = enc["input_ids"]
    tid = tok(target, add_special_tokens=False)["input_ids"][0]
    emb_layer = model.get_input_embeddings()
    emb = emb_layer(ids).detach().clone().requires_grad_(True)
    out = model(inputs_embeds=emb, attention_mask=enc.get("attention_mask"))
    logit = out.logits[0, -1, tid]
    logit.backward()
    g = emb.grad[0]                          # [T, d]
    return g.norm(dim=-1).float().cpu().numpy()


def span_mass(attr: np.ndarray, span: list[int]) -> float:
    total = float(attr[1:].sum()) + 1e-12    # skip BOS
    return float(attr[span].sum()) / total


def pair_null(obs: float, samples: list[float], n_perm: int = N_PERM) -> dict:
    """Sign-flip null over per-pair statistics."""
    s = np.asarray(samples)
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = (s * RNG.choice([-1, 1], size=len(s))).mean()
    return {
        "obs": obs,
        "null_std": float(null.std()),
        "z": float((obs - null.mean()) / (null.std() + 1e-12)),
        "p_perm": float((np.sum(null >= obs) + 1) / (n_perm + 1)),
    }


# ── E1 ───────────────────────────────────────────────────────────────────────


def exp1_operators(model, tok, device: str) -> dict:
    out: dict = {}

    # K — annihilation: mass(selected) minus mass(discarded), both members
    k_stats = []
    for a, b in K_PAIRS:
        for m in (a, b):
            attr = input_attribution(model, tok, m["prompt"], m["target"], device)
            sel = span_mass(attr, token_span(tok, m["prompt"], m["selected"]))
            dis = span_mass(attr, token_span(tok, m["prompt"], m["discarded"]))
            k_stats.append(sel - dis)
    out["K_annihilation"] = pair_null(float(np.mean(k_stats)), k_stats)

    # C — swap: within a pair the arg1/arg2 attribution difference must invert
    c_stats = []
    for a, b in C_PAIRS:
        da = db = None
        for m, sign in ((a, 1.0), (b, -1.0)):
            attr = input_attribution(model, tok, m["prompt"], m["target"], device)
            d = (span_mass(attr, token_span(tok, m["prompt"], m["arg2"]))
                 - span_mass(attr, token_span(tok, m["prompt"], m["arg1"])))
            if sign > 0:
                da = d
            else:
                db = d
        # arg2 is always the target's antecedent → d should be positive in
        # BOTH members despite the swap of which word fills the role
        c_stats.extend([da, db])
    out["C_role_tracking"] = pair_null(float(np.mean(c_stats)), c_stats)

    # I — copy mass on the source span, vs equal-length span-position null
    i_stats, i_zs = [], []
    for m in I_PROBES:
        attr = input_attribution(model, tok, m["prompt"], m["target"], device)
        span = token_span(tok, m["prompt"], m["source"])
        obs = span_mass(attr, span)
        w = len(span)
        others = [
            span_mass(attr, list(range(s, s + w)))
            for s in range(1, len(attr) - w)
            if not set(range(s, s + w)) & set(span)
        ]
        i_stats.append(obs)
        i_zs.append((obs - np.mean(others)) / (np.std(others) + 1e-12))
    out["I_copy_mass"] = {
        "obs": float(np.mean(i_stats)),
        "mean_z_vs_span_null": float(np.mean(i_zs)),
        "per_probe_z": [round(float(z), 2) for z in i_zs],
    }

    # B — intermediate mass: 2-hop vs token-matched 1-hop
    b_stats = []
    for two, one in B_PAIRS:
        m2 = input_attribution(model, tok, two["prompt"], two["target"], device)
        m1 = input_attribution(model, tok, one["prompt"], one["target"], device)
        s2 = span_mass(m2, token_span(tok, two["prompt"], two["intermediate"]))
        s1 = span_mass(m1, token_span(tok, one["prompt"], one["intermediate"]))
        b_stats.append(s2 - s1)
    out["B_intermediate"] = pair_null(float(np.mean(b_stats)), b_stats)
    return out


# ── E2 ───────────────────────────────────────────────────────────────────────


def gate_calibration(model, tok, probes_per_comb: int = 8) -> dict:
    """Shared gate-register calibration at the mid layer: sign-CMR features,
    labels, and W_gate (the residual→gate map whose transpose carries opcode
    centroids back into residual space)."""
    import capture as C
    import topology as T
    from classify import CRYSTAL
    from probes import crystal_probes

    topo = T.detect_topology(model, getattr(model, "config", None))
    li = topo.n_layers // 2
    sel: list = []
    counts: dict[str, int] = {}
    for p in crystal_probes():
        if p.combinator in CRYSTAL and counts.get(p.combinator, 0) < probes_per_comb:
            sel.append(p)
            counts[p.combinator] = counts.get(p.combinator, 0) + 1
    feats, labels = [], []
    for p in sel:
        cap = C.capture_gate(model, tok, p.prompt, topo=topo, layers=[li],
                             register="gate")
        feats.append(cap.gate[li][-1])
        labels.append(p.combinator)
    G = np.sign(np.stack(feats))
    X = G - G.mean(axis=0)
    path = T.gate_path(topo, li)
    mod = model
    for part in path.split("."):
        mod = getattr(mod, part)
    return {"topo": topo, "layer": li, "X": X,
            "labels": np.array(labels), "W": mod.weight.detach()}


def _op_direction(calib: dict, mask: np.ndarray) -> np.ndarray:
    cent = calib["X"][mask].mean(axis=0)
    d = (calib["W"].T.float().cpu() @ torch.from_numpy(cent).float()).numpy()
    return d / (np.linalg.norm(d) + 1e-12)


def exp2_direction_verbalize(model, tok, calib: dict, topk: int = 10,
                             n_perm: int = 300) -> dict:
    """v3 readout: verbalize each opcode centroid DIRECTION (unembed matmul,
    no prompt → no demanded-completion confound). Halt-lexicon hit rate per
    op; null = directions from label-shuffled centroids."""
    from classify import CRYSTAL

    labels = calib["labels"]

    def halt_rate(d: np.ndarray) -> tuple[float, list[str]]:
        toks = jlens.verbalize(model, tok, torch.from_numpy(d).float(),
                               top_k=topk)
        clean = [t.strip().lower() for t in toks]
        return sum(1 for t in clean if t in HALT_LEXICON) / topk, toks

    true_rates, tops = {}, {}
    for op in CRYSTAL:
        m = labels == op
        if m.any():
            r, t = halt_rate(_op_direction(calib, m))
            true_rates[op], tops[op] = r, t

    # null: label-shuffled centroids of WHNF-sized groups
    n_whnf = int((labels == "WHNF").sum())
    null = np.empty(n_perm)
    for i in range(n_perm):
        idx = RNG.choice(len(labels), size=n_whnf, replace=False)
        mask = np.zeros(len(labels), dtype=bool)
        mask[idx] = True
        null[i], _ = halt_rate(_op_direction(calib, mask))
    mu, sd = float(null.mean()), float(null.std()) + 1e-12
    return {
        "halt_rate_per_op": {k: round(v, 3) for k, v in true_rates.items()},
        "z_per_op": {k: round((v - mu) / sd, 2) for k, v in true_rates.items()},
        "whnf_z": (true_rates.get("WHNF", 0.0) - mu) / sd,
        "kibc_max_z": max(
            (true_rates[o] - mu) / sd for o in ("K", "I", "B", "C")
            if o in true_rates
        ),
        "null_mean": mu, "null_std": sd, "n_perm": n_perm,
        "top_tokens": {k: v[:6] for k, v in tops.items()},
    }


# ── E4 ───────────────────────────────────────────────────────────────────────


def exp4_coupling(model, tok, calib: dict, n_shuffle: int = 20) -> dict:
    """Inject gate-register opcode centroids into the residual stream via
    W_gate^T; broadcast KL vs BOTH nulls: matched-random (any direction) and
    shuffled-op (label-identity — the s263 EXP1 trap-killer)."""
    from classify import CRYSTAL

    li, labels = calib["layer"], calib["labels"]
    d_model = calib["W"].shape[1]

    test_prompt = ("The fox chased the hound across the field and the hound "
                   "ran toward the river before the")
    # injection scale: 0.5 x typical residual norm at layer li (s263 FRAC)
    resid, _ = jlens.capture_residuals(model, tok, test_prompt)
    scale = 0.5 * float(resid[li].float().norm(dim=-1).mean().item())
    clean = jlens.forward_logits(model, tok, test_prompt)

    def _kl(vec: np.ndarray) -> float:
        v = vec / (np.linalg.norm(vec) + 1e-12) * scale
        return float(jlens.broadcast_kl(
            model, tok, test_prompt, li,
            torch.from_numpy(v).float(), clean=clean,
        ))

    kls_by_op = {
        op: _kl(_op_direction(calib, labels == op))
        for op in CRYSTAL if (labels == op).any()
    }
    # null 1: matched-random directions
    rand_kls = [_kl(RNG.standard_normal(d_model)) for _ in range(20)]
    mu_r, sd_r = float(np.mean(rand_kls)), float(np.std(rand_kls)) + 1e-12
    # null 2: shuffled-op — permute labels, rebuild all centroids, inject
    shuf: dict[str, list[float]] = {op: [] for op in kls_by_op}
    for _ in range(n_shuffle):
        perm = RNG.permutation(labels)
        for op in kls_by_op:
            shuf[op].append(_kl(_op_direction(calib, perm == op)))
    out: dict = {"layer": li, "inject_norm": scale, "per_op": {}}
    for op, kl in kls_by_op.items():
        mu_s = float(np.mean(shuf[op]))
        sd_s = float(np.std(shuf[op])) + 1e-12
        out["per_op"][op] = {
            "kl": kl,
            "z_vs_random": (kl - mu_r) / sd_r,
            "z_vs_shuffled_op": (kl - mu_s) / sd_s,
            "shuffled_mean": mu_s,
        }
    out["random_null"] = {"mean": mu_r, "std": sd_r, "n": len(rand_kls)}
    out["n_shuffle"] = n_shuffle
    return out


# ── main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    ap = argparse.ArgumentParser(description="J-space v2 (corrected probes)")
    ap.add_argument("--model", default="EleutherAI/pythia-14m-deduped")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--self-test", action="store_true",
                    help="mechanics check on pythia-14m")
    ap.add_argument("--skip-e4", action="store_true")
    ap.add_argument("--dtype", default="float32",
                    choices=["float32", "bfloat16"],
                    help="bfloat16 for large models (27B backward passes)")
    args = ap.parse_args()
    model_name = "EleutherAI/pythia-14m-deduped" if args.self_test else args.model
    device = args.device if torch.backends.mps.is_available() else "cpu"

    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, dtype=getattr(torch, args.dtype), device_map=device
    ).eval()

    report: dict = {"model": model_name, "self_test": args.self_test,
                    "n_perm": N_PERM}
    print("[jspace_v2] E1 operator structure ...")
    report["E1_operators"] = exp1_operators(model, tok, device)
    for k, v in report["E1_operators"].items():
        z = v.get("z")
        print(f"  {k}: obs={v['obs']:+.4f}"
              + (f" z={z:.2f} p={v['p_perm']:.4f}" if z is not None else ""))

    calib = None
    try:
        print("[jspace_v2] gate calibration (shared E2/E4) ...")
        calib = gate_calibration(model, tok)
    except Exception as e:  # MoE refusal / missing register etc.
        report["calibration"] = {"error": str(e)}
        print(f"  calibration failed, skipping E2/E4: {e}")

    if calib is not None:
        print("[jspace_v2] E2 direction verbalization (v3 readout) ...")
        report["E2_verbalize"] = exp2_direction_verbalize(model, tok, calib)
        e2 = report["E2_verbalize"]
        print(f"  WHNF z={e2['whnf_z']:+.2f} | KIBC max z={e2['kibc_max_z']:+.2f}"
              f" | per-op halt-rate {e2['halt_rate_per_op']}")

    if calib is not None and not args.skip_e4:
        print("[jspace_v2] E4 cross-register coupling ...")
        report["E4_coupling"] = exp4_coupling(model, tok, calib)
        for op, v in report["E4_coupling"]["per_op"].items():
            print(f"  {op}: kl={v['kl']:.4f} "
                  f"z_rand={v['z_vs_random']:+.2f} "
                  f"z_shufop={v['z_vs_shuffled_op']:+.2f}")

    out_dir = RESULTS_DIR / model_name.replace("/", "-").lower()
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "jspace_v2.json"
    out.write_text(json.dumps(report, indent=1))
    print(f"[jspace_v2] wrote {out}")


if __name__ == "__main__":
    main()
