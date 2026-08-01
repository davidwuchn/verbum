"""P-HOLO-XTERM — the interference terms: which interaction, which register?

Pre-reg: mementum/knowledge/explore/geometry-holography-signals-convergence.md
§P-HOLO-XTERM (FROZEN s292, Michael GO). CAP's COHERENT-GAIN promoted this:
at 32B, coherent co-installed exposures raise the queried retrieval 2.4x
while energy-matched random does nothing. Three readings, three kill-shots:

  H-INT   constructive interference in the MEDIUM  -> A1 >> A2, A1 >> A3
  H-PRIME domain-priming by context MEANING        -> A2 ~= A1
  H-NORM  contrast from ANY structured background  -> A3 ~= A1

Arms (k_gain distractors, paired draws, one query per draw):
  A1 content-install   (CAP replication, reference)
  A2 text-mention      (real landmark NAMES in preamble, no installs)
  A3 offdomain-install (coherent animal operands at distractor slots)
  A4 random-install    (matched-norm floor)   A5 bare (floor)

Gates (frozen): gate-0 = A1-A5 gain expressed (paired perm p<.05) at the
verdict host (4B = pre-registered NO-GAIN host, mechanics smoke only).
G1 primary = Delta_install (A1-A2) and Delta_domain (A1-A3), paired perm.
G2 secondary (value register, single-slot superposition): cross-term
X = r(A(+)B) - r(A) - r(B) + r(0); magnitude + structure (sum axis, diff
axis, continent axis) vs shuffled-pair null. G3 advisory dose trend.

Verdicts: INTERFERENCE-COHERENT / PRIMING / CONTRAST-GENERIC / MIXED /
negative-inconclusive. `λ measure`: behavioral claim gated behaviorally
(G1); geometry read (G2) corroborates, never gates.

License: MIT (`λ provenance`).
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
from holo_cap import NONCE_CANDS, build_preamble
from holo_frag import _json_safe

from verbum.dsp import gate, paired_permutation

_WRAP = Path(__file__).resolve().parents[2] / "wrapper"
if str(_WRAP) not in sys.path:
    sys.path.insert(0, str(_WRAP))

K_TREND_DEFAULT = (1, 6, 12)
K_GAIN_DEFAULT = 12

OFFDOM = [
    "giraffe", "salmon", "eagle", "tiger", "whale", "falcon", "cobra",
    "otter", "bison", "lemur", "heron", "gecko", "moose", "shark",
    "raven", "panda", "lynx", "toad",
]

ARMS = ("content", "text", "offdom", "random", "bare")


# ══════════════════════════════════════════════════════════════════════════
# Frozen verdict logic (pure; --validate exercises it)
# ══════════════════════════════════════════════════════════════════════════
def g1_verdict(gate0_ok: bool, d_install, d_domain, a2_gain, a3_gain) -> str:
    """Frozen verdict table. d_* / *_gain are Gated objects (or None)."""
    if not gate0_ok:
        return "negative/inconclusive (gate-0)"
    inst = d_install is not None and d_install.verdict
    dom = d_domain is not None and d_domain.verdict
    a2g = a2_gain is not None and a2_gain.verdict
    a3g = a3_gain is not None and a3_gain.verdict
    if inst and dom:
        return "INTERFERENCE-COHERENT"
    if (not inst) and a2g:
        return "PRIMING"
    if inst and (not dom) and a3g:
        return "CONTRAST-GENERIC"
    return "MIXED"


def xterm_stats(r_ab: np.ndarray, r_a: np.ndarray, r_b: np.ndarray,
                r_0: np.ndarray, axes: dict[str, np.ndarray],
                rng: np.random.Generator, n_shuf: int = 200) -> dict:
    """G2 at one layer over P pairs. r_*: (P, D). axes: name -> (P, D) unit.

    X = r_ab - r_a - r_b + r_0. Magnitude vs shuffled-pair null (mismatched
    A'/B' subtraction); structure = |cos(X, axis)| per declared axis vs the
    same shuffled null.
    """
    x = r_ab - r_a - r_b + r_0
    xn = np.linalg.norm(x, axis=1)

    def proj(mat):
        out = {}
        for name, ax in axes.items():
            c = np.abs(np.sum(mat * ax, axis=1)
                       / (np.linalg.norm(mat, axis=1)
                          * np.linalg.norm(ax, axis=1) + 1e-12))
            out[name] = float(np.mean(c))
        return out

    obs_proj = proj(x)
    p = r_ab.shape[0]
    null_norm, null_proj = [], {k: [] for k in axes}
    for _ in range(n_shuf):
        perm = rng.permutation(p)
        # derangement-ish: avoid fixed points dominating small P
        xs = r_ab - r_a[perm] - r_b[perm[::-1]] + r_0
        null_norm.append(float(np.mean(np.linalg.norm(xs, axis=1))))
        pr = proj(xs)
        for k in axes:
            null_proj[k].append(pr[k])
    mean_xn = float(np.mean(xn))
    nn = np.array(null_norm)
    p_norm = float((1 + np.sum(nn >= mean_xn)) / (1 + nn.size))
    struct = {}
    for k in axes:
        npk = np.array(null_proj[k])
        struct[k] = {"obs": obs_proj[k], "null_mean": float(npk.mean()),
                     "p": float((1 + np.sum(npk >= obs_proj[k]))
                                / (1 + npk.size))}
    return {"mean_xnorm": mean_xn, "null_xnorm_mean": float(nn.mean()),
            "p_norm_vs_shuffled": p_norm, "structure": struct,
            "n_pairs": int(p)}


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds exercise verdict table + cross-term detector
# ══════════════════════════════════════════════════════════════════════════
def run_validate(alpha: float) -> int:
    rng = np.random.default_rng(0)
    print("── P-HOLO-XTERM --validate (planted worlds, no model) ──")
    ok = True
    r, base, gain, noise = 60, 1.0, 1.3, 0.5

    def world(a1, a2, a3):
        m = {"content": base + a1 * gain + rng.normal(0, noise, r),
             "text": base + a2 * gain + rng.normal(0, noise, r),
             "offdom": base + a3 * gain + rng.normal(0, noise, r),
             "bare": base + rng.normal(0, noise, r)}

        def paired(x, y, name):
            null = paired_permutation(m[x], m[y], rng)
            return gate(float(np.mean(m[x] - m[y])), null, "greater",
                        alpha, name=name)

        g0 = paired("content", "bare", "gate0")
        return g1_verdict(g0.verdict, paired("content", "text", "d_install"),
                          paired("content", "offdom", "d_domain"),
                          paired("text", "bare", "a2_gain"),
                          paired("offdom", "bare", "a3_gain"))

    calls = {"interference": world(1, 0, 0), "priming": world(1, 1, 0),
             "contrast": world(1, 0, 1)}
    want = {"interference": "INTERFERENCE-COHERENT", "priming": "PRIMING",
            "contrast": "CONTRAST-GENERIC"}
    for w, call in calls.items():
        good = call == want[w]
        print(f"[G1] {w}-world -> {call} (want {want[w]}) {'OK' if good else 'FAIL'}")
        ok &= good

    # G2 detector: linear medium -> null; planted bilinear -> norm + structure
    p_pairs, d = 40, 128
    r_a = rng.standard_normal((p_pairs, d))
    r_b = rng.standard_normal((p_pairs, d))
    r_0 = rng.standard_normal((1, d)).repeat(p_pairs, axis=0)
    axis = rng.standard_normal(d)
    axis /= np.linalg.norm(axis)
    axes = {"planted": np.tile(axis, (p_pairs, 1))}
    lin = xterm_stats(r_a + r_b - r_0 + rng.normal(0, .05, (p_pairs, d)),
                      r_a, r_b, r_0, axes, rng)
    bil = xterm_stats(r_a + r_b - r_0 + 6.0 * axes["planted"]
                      + rng.normal(0, .05, (p_pairs, d)),
                      r_a, r_b, r_0, axes, rng)
    lin_ok = bool(lin["p_norm_vs_shuffled"] > alpha)
    bil_ok = bool(bil["structure"]["planted"]["p"] < alpha
                  and bil["structure"]["planted"]["obs"]
                  > 3 * bil["structure"]["planted"]["null_mean"])
    print(f"[G2] linear plant: p_norm={lin['p_norm_vs_shuffled']:.3f} "
          f"(want >{alpha}) {'OK' if lin_ok else 'FAIL'}")
    print(f"[G2] bilinear plant: proj={bil['structure']['planted']['obs']:.3f} "
          f"vs null {bil['structure']['planted']['null_mean']:.3f} "
          f"p={bil['structure']['planted']['p']:.3f} {'OK' if bil_ok else 'FAIL'}")
    ok &= lin_ok and bil_ok
    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# Model path
# ══════════════════════════════════════════════════════════════════════════
def run_model(args) -> int:
    import operand_multihop3 as mh3
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    rng = np.random.default_rng(args.seed)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    dec, _n, _u = mh3.resolve_parts(model)
    L, S = args.ref_layer, args.scale
    print(f"[xterm] {args.model_id} L_ref={L} scale={S} dev={dev} "
          f"n_layers={len(dec)}")

    cont_ids = {c: mh3.first_tid(tok, c) for c in mh3.CONTINENTS}
    nonce_tid, nonces = {}, []
    for n in NONCE_CANDS:
        t = tok(" " + n, add_special_tokens=False).input_ids[-1]
        if t not in nonce_tid.values():
            nonce_tid[n] = t
            nonces.append(n)

    # ceiling (holo_cap pattern)
    def real_pred(prefix, query, word, label_ids):
        ids = tok(prefix + query.format(x=word), return_tensors="pt").to(dev)
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        return max(label_ids, key=lambda k: lo[label_ids[k]])

    city_ids = {c: mh3.first_tid(tok, c) for c in mh3.CITIES}
    country_ids = {c: mh3.first_tid(tok, c) for c in mh3.COUNTRIES}
    valid = []
    for lm in mh3.LM_LIST:
        ok = (real_pred(mh3.CITY_PREFIX, mh3.CITY_QUERY, lm, city_ids)
              == mh3.CITY_OF[lm]
              and real_pred(mh3.CITY2COUNTRY_PREFIX, mh3.CITY2COUNTRY_QUERY,
                            mh3.CITY_OF[lm], country_ids)
              == mh3.CITY_COUNTRY[mh3.CITY_OF[lm]]
              and real_pred(mh3.COUNTRY2CONT_PREFIX, mh3.COUNTRY2CONT_QUERY,
                            mh3.COUNTRY_OF[lm], cont_ids)
              == mh3.COUNTRY_CONT[mh3.COUNTRY_OF[lm]])
        if ok:
            valid.append(lm)
    print(f"[xterm] valid landmarks: {len(valid)}/{len(mh3.LM_LIST)}")

    def build_dirs(items):
        per = {e: [] for e in items}
        for fr in mh3.FRAMES:
            for e in items:
                store: dict[int, np.ndarray] = {}
                h = dec[L].register_forward_hook(mh3.cap_hook(store, L))
                ids = tok(fr.format(x=e), return_tensors="pt").to(dev)
                with torch.no_grad():
                    model(**ids)
                h.remove()
                per[e].append(store[L][0, -2, :])
        em = {e: np.mean(per[e], axis=0) for e in items}
        gm = np.mean([em[e] for e in items], axis=0)
        return {e: em[e] - gm for e in items}

    d_lm = build_dirs(mh3.LM_LIST)
    d_off = build_dirs(OFFDOM)
    dim = d_lm[valid[0]].shape[0]
    lm_norm = float(np.mean([np.linalg.norm(d_lm[x]) for x in valid]))
    off_norm = float(np.mean([np.linalg.norm(d_off[x]) for x in OFFDOM]))
    # norm-match offdomain operands to the landmark operand scale (recorded)
    off_scale = lm_norm / (off_norm + 1e-9)
    print(f"[xterm] operand norms: lm={lm_norm:.2f} offdom={off_norm:.2f} "
          f"(offdom matched x{off_scale:.2f})")

    def rand_vec(norm):
        v = rng.standard_normal(dim)
        return v / (np.linalg.norm(v) + 1e-9) * norm

    def forward_margin(prompt, adds):
        ids = tok(prompt, return_tensors="pt").to(dev)
        toks = ids.input_ids[0].tolist()
        handles = []
        for vec, tid, which in adds:
            occ = [i for i, t in enumerate(toks) if t == tid]
            if not occ:
                continue
            pos = occ[-1] if which == "last" else occ[0]
            vt = torch.tensor(vec, dtype=torch.float32, device=dev)
            handles.append(dec[L].register_forward_hook(
                mh3.add_hook_at(vt, pos)))
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        for hd in handles:
            hd.remove()
        return lo

    def margin_of(lo, lm):
        truth = mh3.CONT_OF[lm]
        others = [c for c in mh3.CONTINENTS if c != truth]
        return float(lo[cont_ids[truth]]
                     - max(lo[cont_ids[c]] for c in others))

    def arm_margin(arm, k, tgt, d_lms, d_offs):
        """One draw, one arm, query the target. k-1 distractors."""
        tgt_nonce = nonces[0]
        d_nonces = nonces[1:k]
        if arm == "text":
            names = [f"the {x}" for x in d_lms] + [f"the {tgt_nonce}"]
            order = rng.permutation(len(names))
            items = [names[i][4:] for i in order]  # strip "the " for builder
            pre = build_preamble(items)
            adds = [(d_lm[tgt] * S, nonce_tid[tgt_nonce], "last")]
        else:
            pre = build_preamble([tgt_nonce, *d_nonces])
            adds = [(d_lm[tgt] * S, nonce_tid[tgt_nonce], "last")]
            for i, dn in enumerate(d_nonces):
                if arm == "content":
                    vec = d_lm[d_lms[i]] * S
                elif arm == "offdom":
                    vec = d_off[d_offs[i]] * off_scale * S
                elif arm == "random":
                    vec = rand_vec(np.linalg.norm(d_lm[d_lms[i]] * S))
                else:  # bare
                    continue
                adds.append((vec, nonce_tid[dn], "first"))
        prompt = mh3.CONT_PREFIX + pre + mh3.CONT_QUERY.format(x=tgt_nonce)
        return margin_of(forward_margin(prompt, adds), tgt)

    # ── G1/G3: arms x k-trend, paired draws ────────────────────────────────
    k_trend = [k for k in args.k_trend if k <= min(len(valid), len(nonces))]
    k_gain = min(args.k_gain, max(k_trend))
    arms_data = {a: {str(k): [] for k in k_trend} for a in ARMS}
    for k in k_trend:
        for _ in range(args.draws):
            tgt = str(rng.choice(valid))
            pool = [x for x in valid if x != tgt]
            d_lms = [str(x) for x in rng.choice(pool, k - 1, replace=False)] \
                if k > 1 else []
            d_offs = [str(x) for x in rng.choice(OFFDOM, k - 1, replace=False)] \
                if k > 1 else []
            for a in ARMS:
                if k == 1 and a != "content":
                    continue  # k=1: all arms identical; content stands in
                arms_data[a][str(k)].append(arm_margin(a, k, tgt, d_lms, d_offs))
        row = {a: (round(float(np.mean(arms_data[a][str(k)])), 3)
                   if arms_data[a][str(k)] else None) for a in ARMS}
        print(f"[xterm] k={k}: {row}")

    def arr(a, k):
        return np.asarray(arms_data[a][str(k)], dtype=float)

    def paired(x, y, name):
        a, b = arr(x, k_gain), arr(y, k_gain)
        null = paired_permutation(a, b, rng)
        return gate(float(np.mean(a - b)), null, "greater", args.alpha,
                    name=name)

    g0 = paired("content", "bare", "gate0_gain")
    d_install = paired("content", "text", "delta_install")
    d_domain = paired("content", "offdom", "delta_domain")
    a2_gain = paired("text", "bare", "a2_gain")
    a3_gain = paired("offdom", "bare", "a3_gain")
    verdict = g1_verdict(g0.verdict, d_install, d_domain, a2_gain, a3_gain)
    print(f"[xterm] gate-0 gain={g0.value:.3f} p={g0.p:.4f} "
          f"expressed={g0.verdict}")
    print(f"[xterm] G1: d_install={d_install.value:.3f} (p={d_install.p:.4f}) "
          f"d_domain={d_domain.value:.3f} (p={d_domain.p:.4f}) | "
          f"a2_gain p={a2_gain.p:.4f} a3_gain p={a3_gain.p:.4f}")
    print(f"[xterm] G1 VERDICT -> {verdict}")

    # ── G2: single-slot cross-terms over pairs ─────────────────────────────
    def capture_resid(adds_vec):
        """Last-token residuals at all layers; single query-slot installs."""
        prompt = mh3.CONT_PREFIX + build_preamble([nonces[0]]) \
            + mh3.CONT_QUERY.format(x=nonces[0])
        ids = tok(prompt, return_tensors="pt").to(dev)
        toks = ids.input_ids[0].tolist()
        occ = [i for i, t in enumerate(toks) if t == nonce_tid[nonces[0]]]
        pos = occ[-1]
        handles = []
        if adds_vec is not None:
            vt = torch.tensor(adds_vec, dtype=torch.float32, device=dev)
            handles.append(dec[L].register_forward_hook(
                mh3.add_hook_at(vt, pos)))
        with torch.no_grad():
            out = model(**ids, output_hidden_states=True)
        for hd in handles:
            hd.remove()
        return np.stack([h[0, -1, :].float().cpu().numpy()
                         for h in out.hidden_states])  # (n_layers+1, D)

    pairs = []
    pool = list(valid)
    for _ in range(args.n_pairs):
        a, b = (str(x) for x in rng.choice(pool, 2, replace=False))
        pairs.append((a, b))
    r0 = capture_resid(None)
    singles = {}
    for lm in {x for p in pairs for x in p}:
        singles[lm] = capture_resid(d_lm[lm] * S)
    n_lay = r0.shape[0]
    lay_sel = list(range(2, n_lay - 1))
    g2_layers = {}
    r_ab_all, r_a_all, r_b_all, ax_sum, ax_diff, ax_cont = [], [], [], [], [], []
    cont_axis = {c: np.mean([d_lm[x] for x in valid
                             if mh3.CONT_OF[x] == c], axis=0)
                 for c in mh3.CONTINENTS}
    for (a, b) in pairs:
        r_ab_all.append(capture_resid((d_lm[a] + d_lm[b]) * S))
        r_a_all.append(singles[a])
        r_b_all.append(singles[b])
        s_ax = d_lm[a] + d_lm[b]
        d_ax = d_lm[a] - d_lm[b]
        c_ax = cont_axis[mh3.CONT_OF[a]] + cont_axis[mh3.CONT_OF[b]]
        ax_sum.append(s_ax / (np.linalg.norm(s_ax) + 1e-12))
        ax_diff.append(d_ax / (np.linalg.norm(d_ax) + 1e-12))
        ax_cont.append(c_ax / (np.linalg.norm(c_ax) + 1e-12))
    ax_sum, ax_diff, ax_cont = map(np.stack, (ax_sum, ax_diff, ax_cont))
    for li in lay_sel:
        g2_layers[str(li)] = xterm_stats(
            np.stack([r[li] for r in r_ab_all]),
            np.stack([r[li] for r in r_a_all]),
            np.stack([r[li] for r in r_b_all]),
            np.tile(r0[li], (len(pairs), 1)),
            {"sum": ax_sum, "diff": ax_diff, "continent": ax_cont}, rng)
    # aggregate: median across layers
    agg = {"p_norm_median": float(np.median(
        [g2_layers[k]["p_norm_vs_shuffled"] for k in g2_layers]))}
    for axn in ("sum", "diff", "continent"):
        agg[f"{axn}_p_median"] = float(np.median(
            [g2_layers[k]["structure"][axn]["p"] for k in g2_layers]))
        agg[f"{axn}_obs_median"] = float(np.median(
            [g2_layers[k]["structure"][axn]["obs"] for k in g2_layers]))
    print(f"[xterm] G2 aggregate: {agg}")

    result = {
        "model_id": args.model_id, "seed": args.seed, "scale": S,
        "ref_layer": L, "k_trend": k_trend, "k_gain": k_gain,
        "draws": args.draws, "alpha": args.alpha, "n_pairs": len(pairs),
        "valid_landmarks": valid, "offdom": OFFDOM,
        "operand_norms": {"lm": lm_norm, "offdom_raw": off_norm,
                          "offdom_scale": off_scale},
        "arms_data": {a: arms_data[a] for a in ARMS},
        "g1": {"gate0": asdict(g0), "delta_install": asdict(d_install),
               "delta_domain": asdict(d_domain), "a2_gain": asdict(a2_gain),
               "a3_gain": asdict(a3_gain), "verdict": verdict},
        "g2": {"per_layer": g2_layers, "aggregate": agg},
    }
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "holo_xterm.json").write_text(
        json.dumps(_json_safe(result), indent=2, allow_nan=False))
    print(f"[xterm] wrote {out}/holo_xterm.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="P-HOLO-XTERM interference terms")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--ref-layer", type=int, default=9)
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--draws", type=int, default=12)
    ap.add_argument("--k-trend", type=int, nargs="+",
                    default=list(K_TREND_DEFAULT))
    ap.add_argument("--k-gain", type=int, default=K_GAIN_DEFAULT)
    ap.add_argument("--n-pairs", type=int, default=40)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/holo-xterm/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
