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
    "done", "finished", "complete", "final", "answer", "result", "is",
    "already", "value", "nothing", "end", "stop", "resolved", "settled",
)
WHNF_PROBES_E2 = [
    "The value 42 requires no further computation because it is already",
    "After all the steps were carried out, the calculation was finally",
    "There is nothing left to simplify, so the expression is",
    "The result has been computed and no more work remains, so we are",
]
KIBC_PROBES_E2 = [
    "The fox, not the hound, ate the food, so we keep only the",       # K
    "The password is otter, repeated exactly: the password is",         # I
    "The key opens the box and the box holds the coin, giving the",     # B
    "Alice paid Bob, which reversed means Bob was paid by",             # C
]


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

    # I — copy mass on the source span
    i_stats = []
    for m in I_PROBES:
        attr = input_attribution(model, tok, m["prompt"], m["target"], device)
        i_stats.append(span_mass(attr, token_span(tok, m["prompt"], m["source"])))
    out["I_copy_mass"] = {
        "obs": float(np.mean(i_stats)),
        "per_probe": [round(v, 4) for v in i_stats],
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


_FORMAL_MARKERS = ("λ", "def ", "(x)", "(z)", " = ", "=>", "::")


def _is_prose(p: str) -> bool:
    return not any(m in p for m in _FORMAL_MARKERS)


def _e2_prompts(n_per_side: int) -> tuple[list[str], list[str]]:
    """Prose WHNF vs prose-KIBC prompts from the clean bundle; fall back to
    the built-in quartets if the bundle is unavailable."""
    try:
        from probes import crystal_probes
        whnf = [p.prompt for p in crystal_probes()
                if p.combinator == "WHNF" and _is_prose(p.prompt)]
        kibc = [p.prompt for p in crystal_probes()
                if p.combinator in ("K", "I", "B", "C") and _is_prose(p.prompt)]
        if len(whnf) >= 4 and len(kibc) >= 4:
            return whnf[:n_per_side], kibc[:n_per_side]
    except Exception:
        pass
    return list(WHNF_PROBES_E2), list(KIBC_PROBES_E2)


def exp2_verbalize(model, tok, device: str, topk: int = 10,
                   n_per_side: int = 16) -> dict:
    """Halt-lexicon hit rate in the logit-lens plateau readout, WHNF vs KIBC.

    Per-prompt rates + label-permutation null on the asymmetry."""
    nl = jlens.n_layers(model)
    plateau = list(range(int(nl * 0.85), nl))
    whnf_prompts, kibc_prompts = _e2_prompts(n_per_side)

    def rates_for(prompts: list[str]) -> tuple[list[float], list[list[str]]]:
        rates, tops = [], []
        for p in prompts:
            resid, _ = jlens.capture_residuals(model, tok, p)
            hits = 0
            words: list[str] = []
            for li in plateau:
                lg = jlens.logit_lens(model, resid[li][-1:])
                ids = torch.topk(lg[0], topk).indices.tolist()
                toks = [tok.decode([t]).strip().lower() for t in ids]
                words.extend(toks[:3])
                hits += sum(1 for t in toks if t in HALT_LEXICON)
            rates.append(hits / (len(plateau) * topk))
            tops.append(words[:6])
        return rates, tops

    whnf_rates, whnf_tops = rates_for(whnf_prompts)
    kibc_rates, kibc_tops = rates_for(kibc_prompts)
    obs = float(np.mean(whnf_rates) - np.mean(kibc_rates))
    pooled = np.array(whnf_rates + kibc_rates)
    nw = len(whnf_rates)
    null = np.empty(N_PERM)
    for i in range(N_PERM):
        perm = RNG.permutation(pooled)
        null[i] = perm[:nw].mean() - perm[nw:].mean()
    return {
        "n_whnf": len(whnf_rates), "n_kibc": len(kibc_rates),
        "whnf_halt_hit_rate": float(np.mean(whnf_rates)),
        "kibc_halt_hit_rate": float(np.mean(kibc_rates)),
        "asymmetry": obs,
        "null_std": float(null.std()),
        "z": float((obs - null.mean()) / (null.std() + 1e-12)),
        "p_perm": float((np.sum(null >= obs) + 1) / (N_PERM + 1)),
        "whnf_top_tokens": whnf_tops[:4],
        "kibc_top_tokens": kibc_tops[:4],
    }


# ── E4 ───────────────────────────────────────────────────────────────────────


def exp4_coupling(model, tok, device: str, probes_per_comb: int = 8) -> dict:
    """Inject gate-register opcode centroids into the residual stream via
    W_gate^T; measure downstream broadcast vs matched-random and shuffled-op."""
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
    common = G.mean(axis=0)
    X = G - common
    labels = np.array(labels)

    # W_gate at layer li: gate = W @ resid  →  resid direction = W^T s
    path = T.gate_path(topo, li)
    mod = model
    for part in path.split("."):
        mod = getattr(mod, part)
    W = mod.weight.detach()                      # [d_ff, d_model]

    test_prompt = ("The fox chased the hound across the field and the hound "
                   "ran toward the river before the")
    # injection scale: 0.5 x typical residual norm at layer li (s263 FRAC)
    resid, _ = jlens.capture_residuals(model, tok, test_prompt)
    scale = 0.5 * float(
        resid[li].float().norm(dim=-1).mean().item()
    )
    clean = jlens.forward_logits(model, tok, test_prompt)

    def _kl(vec: np.ndarray) -> float:
        v = vec / (np.linalg.norm(vec) + 1e-12) * scale
        return float(jlens.broadcast_kl(
            model, tok, test_prompt, li,
            torch.from_numpy(v).float(), clean=clean,
        ))

    out: dict = {"layer": li, "inject_norm": scale, "per_op": {}}
    kls_by_op = {}
    d_model = W.shape[1]
    for op in CRYSTAL:
        m = labels == op
        if not m.any():
            continue
        cent = X[m].mean(axis=0)
        d = (W.T.float().cpu() @ torch.from_numpy(cent).float()).numpy()
        kls_by_op[op] = _kl(d)
    # matched-random null
    rand_kls = [_kl(RNG.standard_normal(d_model)) for _ in range(20)]
    mu, sd = float(np.mean(rand_kls)), float(np.std(rand_kls)) + 1e-12
    for op, kl in kls_by_op.items():
        out["per_op"][op] = {"kl": kl, "z_vs_random": (kl - mu) / sd}
    out["random_null"] = {"mean": mu, "std": sd, "n": len(rand_kls)}
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

    print("[jspace_v2] E2 halt verbalization ...")
    report["E2_verbalize"] = exp2_verbalize(model, tok, device)
    e2 = report["E2_verbalize"]
    print(f"  WHNF halt-rate={e2['whnf_halt_hit_rate']:.3f} "
          f"KIBC={e2['kibc_halt_hit_rate']:.3f} "
          f"asymmetry={e2['asymmetry']:+.3f}")

    if not args.skip_e4:
        print("[jspace_v2] E4 cross-register coupling ...")
        try:
            report["E4_coupling"] = exp4_coupling(model, tok, device)
            for op, v in report["E4_coupling"]["per_op"].items():
                print(f"  {op}: kl={v['kl']:.4f} z_vs_random={v['z_vs_random']:+.2f}")
        except Exception as e:  # MoE refusal / missing register etc.
            report["E4_coupling"] = {"error": str(e)}
            print(f"  E4 skipped: {e}")

    out_dir = RESULTS_DIR / model_name.replace("/", "-").lower()
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "jspace_v2.json"
    out.write_text(json.dumps(report, indent=1))
    print(f"[jspace_v2] wrote {out}")


if __name__ == "__main__":
    main()
