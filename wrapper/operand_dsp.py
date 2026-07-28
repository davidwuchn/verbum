"""P-DSP-1 — DSP-decompose the operand-INSERT injection (SuperBake=I reframe).

Pre-registration: mementum/knowledge/explore/operand-dsp-decomposition-prereg.md.
Question (Michael s278): SuperBake used a signal-processing lens to reverse-engineer
*fact* injection. Do the same for our operand injection. Core reframe: SuperBake
reverse-engineered the I combinator (fact = key->value unchanged = identity; a matched
filter IS I). Its whole pipeline is I-flavored -- no B/C transform. A3 register-split
grounds it: I/WHNF/Y register-INVARIANT (portable, bakeable), C=0.0 register-BOUND.

H1: operand pipeline = [WRITTEN: I-portable payload d_cat, value register]
                     + [RESIDENT: the B/C join that transports+transforms it].
    fact = all-I, all-written (no resident I-path). Predict: operand needs 1 written
    component, fact 3. C-TRANSPORT must separate an I-copy (deliver unchanged) from a
    genuine B/C-transform (categorize), and locate where the transform fires.

Three register-typed, null-gated component tests + the fact-vs-operand contrast.
`lambda measure`: name the register before the probe (s206). `lambda yardstick`: every
DSP signature predicted a-priori with a matched-random / shuffled-label null beside it
(phi-ladder scar). Planted ground truth: we built d_cat -> C-PAYLOAD is a known-answer
instrument check.

License: MIT (`lambda provenance`; SuperBake is method-reference only).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ── the operand-insert fixtures (reused verbatim from operand_insert.py) ──────────
CATS = {
    "animal": ["dog", "cat", "horse", "cow", "wolf", "sheep"],
    "vehicle": ["car", "truck", "train", "boat", "jet", "bus"],
    "plant": ["rose", "oak", "fern", "pine", "palm", "vine"],
}
ALL_OPS = [o for os in CATS.values() for o in os]
NONCE = [("zorp", "animal"), ("blint", "vehicle"), ("drell", "plant"),
         ("frob", "animal"), ("glark", "vehicle"), ("murv", "plant")]
FRAMES = [
    ("The farmer", "saw"), ("The child", "drew"), ("The hunter", "tracked"),
    ("A woman", "bought"), ("The boy", "chased"), ("A man", "found"),
    ("The girl", "wanted"), ("The old sailor", "watched"),
]
PREFIXES = [
    "dog: animal\ncar: vehicle\nrose: plant\n",
    "cat: animal\ntruck: vehicle\noak: plant\n",
    "horse: animal\nboat: vehicle\nfern: plant\n",
    "cow: animal\ntrain: vehicle\npine: plant\n",
]
# natural-text corpus for the residual-PCA basis (register: value; layer-L residuals)
CORPUS = [
    "The sun set slowly behind the distant hills as the day came to an end.",
    "She opened the old book and began to read the first page carefully.",
    "Rain fell on the quiet street while the city slept through the night.",
    "He walked along the river thinking about everything that had happened.",
    "The market was crowded with people buying fruit and fresh bread.",
    "A gentle wind moved the leaves and carried the smell of the sea.",
    "They talked for hours about the future and the choices ahead of them.",
    "The train arrived on time and the passengers stepped onto the platform.",
    "Music drifted from the open window into the warm summer evening.",
    "The scientist recorded the results and checked the numbers again.",
    "Children played in the park until the light began to fade away.",
    "The letter arrived a week late but the news inside was still good.",
    "Snow covered the fields and the road disappeared under the white.",
    "He fixed the engine and the car started on the very first try.",
    "The teacher explained the problem twice before the class understood.",
    "Waves crashed against the rocks as the storm moved along the coast.",
    "She planted flowers in the garden and watered them every morning.",
    "The old clock in the hall chimed softly at the top of the hour.",
    "A group of friends gathered around the fire to share their stories.",
    "The plane climbed above the clouds into a clear and open sky.",
    "He counted the coins on the table and put them back in the jar.",
    "The dog ran across the yard chasing a ball into the tall grass.",
    "Morning light filled the kitchen while the coffee slowly brewed.",
    "The bridge spanned the wide river connecting the two small towns.",
]


def decl(frame, obj):
    s, v = frame
    return f"{s} {v} a {obj}."


def tid(tok, w):
    return tok(" " + w, add_special_tokens=False).input_ids[0]


def cap_hook(store, li):
    def hook(_m, _i, out):
        h = out[0] if isinstance(out, tuple) else out
        store[li] = h.detach().float().cpu().numpy()
    return hook


def add_hook_at(vec_t, pos):
    def hook(_m, _i, out):
        tup = isinstance(out, tuple)
        h = out[0] if tup else out
        if 0 <= pos < h.shape[1]:
            h[0, pos, :] = h[0, pos, :] + vec_t.to(h.dtype)
        return out
    return hook


def ablate_head_prehook(h, head_dim):
    """zero head h's slice of the o_proj input (routing-register ablation)."""
    def hook(_mod, inp):
        x = inp[0].clone()
        x[..., h * head_dim:(h + 1) * head_dim] = 0.0
        return (x, *inp[1:])
    return hook


def participation_ratio(vecs):
    m = np.stack(vecs, 0).astype(np.float64)
    s = np.linalg.svd(m, compute_uv=False)
    lam = s ** 2
    return float((lam.sum() ** 2) / (np.square(lam).sum() + 1e-12))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--layer", type=int, default=7, help="d_cat build layer (payload)")
    ap.add_argument("--readout-lo", type=int, default=20)
    ap.add_argument("--readout-hi", type=int, default=27)
    ap.add_argument("--pca-k", type=int, default=64, help="low-var subspace size")
    ap.add_argument("--n-null", type=int, default=32)
    ap.add_argument("--skip-ablation", action="store_true")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--out", default="results/ffn-bake/operand-dsp-qwen3-0-6b")
    args = ap.parse_args()

    L = args.layer
    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    rng = np.random.default_rng(0)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=torch.float32,
        attn_implementation="eager").to(dev).eval()
    cfg = model.config
    dec = model.model.layers
    n_layers = len(dec)
    n_heads = cfg.num_attention_heads
    head_dim = getattr(cfg, "head_dim", cfg.hidden_size // n_heads)
    W_U = model.lm_head.weight.detach().float().cpu().numpy()          # (V, d)
    cat_ids = {c: tid(tok, c) for c in CATS}
    ro_layers = list(range(args.readout_lo, min(args.readout_hi + 1, n_layers)))
    print(f"[dsp] {args.model_id} layers={n_layers} heads={n_heads} hd={head_dim} "
          f"dev={dev}  payload L={L}  readout={ro_layers}")

    # ── d_cat payload (register: VALUE), built in declaratives ────────────────────
    per_op = {o: [] for o in ALL_OPS}
    for fr in FRAMES:
        for o in ALL_OPS:
            store: dict[int, np.ndarray] = {}
            h = dec[L].register_forward_hook(cap_hook(store, L))
            ids = tok(decl(fr, o), return_tensors="pt").to(dev)
            with torch.no_grad():
                model(**ids)
            h.remove()
            per_op[o].append(store[L][0, -2, :])
    op_mean = {o: np.mean(per_op[o], axis=0) for o in ALL_OPS}
    global_mean = np.mean([op_mean[o] for o in ALL_OPS], axis=0)
    d_cat = {c: np.mean([op_mean[o] for o in objs], axis=0) - global_mean
             for c, objs in CATS.items()}
    d = d_cat["animal"].shape[0]

    def rand_dir(norm):
        v = rng.standard_normal(d)
        return v / (np.linalg.norm(v) + 1e-9) * norm

    # ══ C-PAYLOAD (VALUE register) ════════════════════════════════════════════════
    # residual PCA basis from natural text at layer L
    feats = []
    for t in CORPUS:
        store = {}
        h = dec[L].register_forward_hook(cap_hook(store, L))
        ids = tok(t, return_tensors="pt").to(dev)
        with torch.no_grad():
            model(**ids)
        h.remove()
        feats.append(store[L][0])
    X = np.concatenate(feats, 0).astype(np.float64)
    Xc = X - X.mean(0)
    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)   # Vt desc by variance
    k = min(args.pca_k, Vt.shape[0])

    def lowvar_frac(vec):
        c = Vt @ vec
        e = c ** 2
        return float(e[-k:].sum() / (e.sum() + 1e-12))

    def logit_energy(vec):
        vh = vec / (np.linalg.norm(vec) + 1e-9)
        return float(np.linalg.norm(W_U @ vh))

    # subspace coherence: PR of the 12 operand means and the 3 d_cat dirs
    pr_ops = participation_ratio([op_mean[o] - global_mean for o in ALL_OPS])
    pr_dcat = participation_ratio(list(d_cat.values()))
    pr_ops_null = float(np.mean([participation_ratio(
        [rand_dir(1.0) for _ in ALL_OPS]) for _ in range(8)]))

    lv_dcat = float(np.mean([lowvar_frac(v) for v in d_cat.values()]))
    lv_null = float(np.mean([lowvar_frac(rand_dir(1.0)) for _ in range(args.n_null)]))
    ue_dcat = float(np.mean([logit_energy(v) for v in d_cat.values()]))
    ue_null = float(np.mean([logit_energy(rand_dir(1.0)) for _ in range(args.n_null)]))

    # shuffled-label null for d_cat: permute operand->category then rebuild dirs
    perm = rng.permutation(ALL_OPS)
    shuf_cats = {c: perm[i * 6:(i + 1) * 6] for i, c in enumerate(CATS)}
    d_shuf = {c: np.mean([op_mean[o] for o in objs], axis=0) - global_mean
              for c, objs in shuf_cats.items()}
    lv_shuf = float(np.mean([lowvar_frac(v) for v in d_shuf.values()]))
    ue_shuf = float(np.mean([logit_energy(v) for v in d_shuf.values()]))

    payload = {
        "pr_operand_means": round(pr_ops, 3), "pr_dcat": round(pr_dcat, 3),
        "pr_random_null": round(pr_ops_null, 3),
        "lowvar_frac_dcat": round(lv_dcat, 4),
        "lowvar_frac_random": round(lv_null, 4),
        "lowvar_frac_shuffled": round(lv_shuf, 4),
        "lowvar_baseline_uniform": round(k / Vt.shape[0], 4),
        "unembed_energy_dcat": round(ue_dcat, 3),
        "unembed_energy_random": round(ue_null, 3),
        "unembed_energy_shuffled": round(ue_shuf, 3),
    }
    print("\n── C-PAYLOAD (VALUE register) ──")
    print(f"  subspace coherence  PR: operand-means={pr_ops:.2f} d_cat={pr_dcat:.2f} "
          f"(random-null={pr_ops_null:.2f})")
    print(f"  low-var concentration (bottom-{k}/{Vt.shape[0]}): d_cat={lv_dcat:.3f} "
          f"random={lv_null:.3f} shuffled={lv_shuf:.3f} uniform={k/Vt.shape[0]:.3f}")
    print(f"  unembed silence (‖W_U d̂‖): d_cat={ue_dcat:.2f} random={ue_null:.2f} "
          f"shuffled={ue_shuf:.2f}  (lower = quieter)")

    # ══ readout / composition helpers (routing tests reuse these) ═════════════════
    def slot_and_colon(prefix, word):
        ids = tok(prefix + word + ":", return_tensors="pt").to(dev)
        toks = ids.input_ids[0].tolist()
        colon = max(i for i, t in enumerate(toks) if ":" in tok.decode([t]))
        return ids, colon, colon - 1   # slot = nonce last subtoken

    def category_pred(prefix, word, add_vec=None, pos=None, ablate=None):
        ids, _, slot = slot_and_colon(prefix, word)
        handles = []
        if add_vec is not None:
            p = slot if pos is None else pos
            vt = torch.tensor(add_vec, dtype=torch.float32, device=dev)
            handles.append(dec[L].register_forward_hook(add_hook_at(vt, p)))
        if ablate is not None:
            lyr, hd = ablate
            handles.append(dec[lyr].self_attn.o_proj.register_forward_pre_hook(
                ablate_head_prehook(hd, head_dim)))
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        for hh in handles:
            hh.remove()
        return max(cat_ids, key=lambda c: lo[cat_ids[c]])

    def acc(word, target, add_vec=None, pos=None, ablate=None, prefixes=PREFIXES):
        return np.mean([category_pred(p, word, add_vec, pos, ablate) == target
                        for p in prefixes])

    # ══ C-KEY (ROUTING register) ══════════════════════════════════════════════════
    # (1) clean-pass attention mass: readout query -> operand slot vs random token.
    #     Measured on the RESIDENT category task (real operand) — is the slot read?
    def clean_attn_to_slot(prefix, word):
        ids, colon, slot = slot_and_colon(prefix, word)
        n = ids.input_ids.shape[1]
        cand = [i for i in range(n) if i not in (slot, colon, n - 1)]
        rnd = int(rng.choice(cand)) if cand else 0
        with torch.no_grad():
            out = model(**ids, output_attentions=True)
        to_slot, to_rnd = [], []
        for lyr in ro_layers:
            a = out.attentions[lyr][0]           # (heads, q, k)
            q = a.shape[1] - 1                    # readout query = last position
            to_slot.append(a[:, q, slot].mean().item())
            to_rnd.append(a[:, q, rnd].mean().item())
        return float(np.mean(to_slot)), float(np.mean(to_rnd))

    real_pairs = [("dog", "animal"), ("car", "vehicle"), ("rose", "plant"),
                  ("horse", "animal"), ("truck", "vehicle"), ("oak", "plant")]
    ks, kr = [], []
    for w, _ in real_pairs:
        for pfx in PREFIXES[:2]:
            s_, r_ = clean_attn_to_slot(pfx, w)
            ks.append(s_)
            kr.append(r_)
    attn_slot, attn_rnd = float(np.mean(ks)), float(np.mean(kr))

    # (2) placement robustness: inject d_cat at slot-1/slot/slot+1 vs wrong-key
    def place_acc(offset, scale=2.0, wrong=False):
        vals = []
        for w, t in NONCE:
            dv = d_cat[t] * scale
            for pfx in PREFIXES:
                _, _, slot = slot_and_colon(pfx, w)
                pos = 0 if wrong else slot + offset
                vals.append(category_pred(pfx, w, add_vec=dv, pos=pos) == t)
        return float(np.mean(vals))

    place = {"slot-1": place_acc(-1), "slot": place_acc(0), "slot+1": place_acc(1),
             "wrong_key": place_acc(0, wrong=True)}
    key = {"clean_attn_to_slot": round(attn_slot, 4),
           "clean_attn_to_random": round(attn_rnd, 4),
           "attn_ratio": round(attn_slot / (attn_rnd + 1e-9), 2),
           "placement": {k2: round(v2, 3) for k2, v2 in place.items()}}
    print("\n── C-KEY (ROUTING register) ──")
    print(f"  clean-pass attn readout→slot={attn_slot:.4f} vs →random={attn_rnd:.4f}"
          f"  ratio={attn_slot/(attn_rnd+1e-9):.2f}")
    print(f"  placement robustness: {key['placement']}")

    # ══ C-TRANSPORT (ROUTING register) ════════════════════════════════════════════
    # I-copy vs B/C-transform: logit-lens sweep on the INSTALLED nonce. Where does the
    # CATEGORY (transform) overtake the others? Installed content is category-level, so
    # track the target-category margin per layer (onset = where the transform fires).
    def logit_lens_installed(word, target, scale=2.0):
        pfx = PREFIXES[0]
        ids, _, slot = slot_and_colon(pfx, word)
        dv = torch.tensor(
            d_cat[target] * scale, dtype=torch.float32, device=dev)
        hstore: dict[int, np.ndarray] = {}
        hs = [dec[i].register_forward_hook(cap_hook(hstore, i))
              for i in range(n_layers)]
        ha = dec[L].register_forward_hook(add_hook_at(dv, slot))
        with torch.no_grad():
            model(**ids)
        for hh in [*hs, ha]:
            hh.remove()
        norm = model.model.norm
        per_layer = []
        for i in range(n_layers):
            r = torch.tensor(hstore[i][0, -1, :], dtype=torch.float32, device=dev)
            with torch.no_grad():
                lg = model.lm_head(norm(r)).float().cpu().numpy()
            other = [cat_ids[c] for c in CATS if c != target]
            m = lg[cat_ids[target]] - np.max([lg[o] for o in other])
            per_layer.append(float(m))
        return per_layer

    lens = np.mean([logit_lens_installed(w, t) for w, t in NONCE], axis=0)
    # transform onset: first layer >= injection L where the target-category margin goes
    # AND STAYS positive. early-layer logit-lens is noise; an onset < L is impossible
    # (nothing is injected yet), so restrict the search to layers >= L.
    onset = next((i for i in range(L, n_layers)
                  if all(lens[j] > 0 for j in range(i, n_layers))), None)
    onset_raw = next((i for i, m in enumerate(lens) if m > 0), None)  # incl. noise
    transport = {"transform_onset_layer": onset, "onset_raw_incl_noise": onset_raw,
                 "target_margin_by_layer": [round(float(x), 3) for x in lens]}
    print("\n── C-TRANSPORT (ROUTING register) ──")
    print(f"  transform onset (stable margin>0, ≥L) at layer {onset}/{n_layers} "
          f"(raw incl. early-noise={onset_raw})")
    print(f"  margin@[L{L},mid,late]: "
          f"{lens[L]:.2f}, {lens[n_layers//2]:.2f}, {lens[-1]:.2f}")

    # head necessity at readout-locus layers (installed nonce; reduced eval set)
    if not args.skip_ablation:
        base = np.mean([acc(w, t, add_vec=d_cat[t] * 2.0, prefixes=PREFIXES[:2])
                        for w, t in NONCE[:3]])
        drops = []
        for lyr in ro_layers:
            for hd in range(n_heads):
                a = np.mean([acc(w, t, add_vec=d_cat[t] * 2.0, ablate=(lyr, hd),
                                 prefixes=PREFIXES[:2]) for w, t in NONCE[:3]])
                drops.append({"layer": lyr, "head": hd, "acc": round(float(a), 3),
                              "drop": round(float(base - a), 3)})
        drops.sort(key=lambda x: -x["drop"])
        n_necessary = sum(1 for x in drops if x["drop"] >= 0.34)
        transport["head_ablation"] = {
            "installed_base_acc": round(float(base), 3),
            "n_heads_tested": len(drops),
            "n_necessary_drop>=0.34": n_necessary,
            "top5": drops[:5]}
        print(f"  head necessity: base={base:.3f}  necessary heads "
              f"(drop≥0.34)={n_necessary}/{len(drops)}  top: "
              f"{[(x['layer'], x['head'], x['drop']) for x in drops[:3]]}")

    # ══ CONTRAST: operand (resident task) vs novel fact (no resident task) ═════════
    # tractable form: clean-pass attention residence. For the operand the readout
    # attends the slot (resident routing). For a NOVEL fact with no task, nothing
    # routes the key -> attention to the key should be at-random.  fact prompt: a bare
    # novel key with a colon (no few-shot task establishing a join).
    def fact_attn(word):
        ids = tok(word + ":", return_tensors="pt").to(dev)
        n = ids.input_ids.shape[1]
        toks = ids.input_ids[0].tolist()
        colon = max(i for i, t in enumerate(toks) if ":" in tok.decode([t]))
        slot = colon - 1
        cand = [i for i in range(n) if i not in (slot, colon, n - 1)]
        rnd = int(rng.choice(cand)) if cand else 0
        with torch.no_grad():
            out = model(**ids, output_attentions=True)
        s_, r_ = [], []
        for lyr in ro_layers:
            a = out.attentions[lyr][0]
            q = a.shape[1] - 1
            s_.append(a[:, q, slot].mean().item())
            r_.append(a[:, q, rnd].mean().item() if rnd != slot else 0.0)
        return float(np.mean(s_)), float(np.mean(r_))

    fs, fr = [], []
    for w, _ in NONCE:
        s_, r_ = fact_attn(w)
        fs.append(s_)
        fr.append(r_)
    fact_slot, fact_rnd = float(np.mean(fs)), float(np.mean(fr))
    contrast = {
        "operand_resident_attn_to_slot": round(attn_slot, 4),
        "operand_attn_ratio": round(attn_slot / (attn_rnd + 1e-9), 2),
        "novelfact_attn_to_slot": round(fact_slot, 4),
        "novelfact_attn_ratio": round(fact_slot / (fact_rnd + 1e-9), 2),
        "note": ("operand reuses a resident task's routing (few-shot join); a bare "
                 "novel fact has no resident join -> lower slot-attention ratio.")}
    print("\n── CONTRAST (operand resident-routing vs novel-fact no-routing) ──")
    print(f"  operand readout→slot ratio={contrast['operand_attn_ratio']}  "
          f"novel-fact ratio={contrast['novelfact_attn_ratio']}")

    # ── verdicts (pre-registered) ─────────────────────────────────────────────────
    v_payload = ("I-CODED" if (lv_dcat > lv_null and ue_dcat < ue_null)
                 else "NOT-CODED-LIKE-SUPERBAKE")
    v_key = ("RESIDENT-KEY" if (attn_slot > 2 * attn_rnd
                                and place["slot"] > place["wrong_key"] + 0.34
                                and min(place["slot-1"], place["slot+1"])
                                > place["wrong_key"] + 0.17)
             else "KEY-PLACEMENT-OURS")
    v_transport = ("RESIDENT-BC-TRANSFORM" if (onset is not None and onset > L + 2)
                   else "I-COPY-OR-EARLY")
    verdicts = {"C_PAYLOAD": v_payload, "C_KEY": v_key, "C_TRANSPORT": v_transport}
    print("\n[dsp] VERDICTS:", verdicts)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    res = {"model": args.model_id, "device": dev, "payload_layer": L,
           "readout_layers": ro_layers, "n_layers": n_layers, "n_heads": n_heads,
           "C_PAYLOAD": payload, "C_KEY": key, "C_TRANSPORT": transport,
           "CONTRAST": contrast, "verdicts": verdicts}
    (out / "operand_dsp.json").write_text(json.dumps(res, indent=2))
    print(f"[dsp] wrote {out}/operand_dsp.json")


if __name__ == "__main__":
    main()
