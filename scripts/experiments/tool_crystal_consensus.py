#!/usr/bin/env python3
# register: topological/routing
"""Tool-calling normal form — is it a consensus routing structure, or common mode?

THE PRIOR CLAIM (lattice/tool_crystal_run.log, scripts/v12/probe_tool_crystal.py):
  "STRONG SUPPORT: Tool x Lambda overlap peaks at 1.000 at layer 20.
   Tool calling IS lambda calculus applied to JSON schema."
  — measured as RAW cosine similarity of the residual hidden state, single
    model (Qwen). But that run's own Selectivity column reads ~-0.01..+0.03 and
    every layer is marked "SHARED": the 0.9999 is the generic high-dim prose
    COMMON MODE (Schema/Lambda/Tool x Lambda all 0.9999 at L20), not tool
    structure. Classic wrong-register/common-mode artifact (cf. audit s202/s211).

THE CORRECT INSTRUMENT (this script):
  Measure the ROUTING register, not the raw residual:
    routing(x) = sign( FFN gate pre-activation )          (s203: gate_proj sign
                                                            carries routing topology)
  with COMMON-MODE REMOVAL (center features across probes before the RDM), and
  against a SHUFFLED-LABEL null. Then the part the prior run never did:
  CROSS-MODEL CONSENSUS — does the tool-calling routing RDM AGREE across
  independent model families above a shuffled-probe null?  Agreement == the
  empirical signature of a shared normal form (Church-Rosser confluence across
  independent trainings; crystal-universality.md).

Per-model invocation (like manifold_axis_topology.py). Saves per-layer RDMs
(probe-aligned, so cross-model agreement needs no re-run) + within-model
selectivity. tool_crystal_consensus_summary.py does the cross-model verdict.

Registers compared (the scientific contrast):
  hidden_full   raw residual cosine        -> reproduces the prior "SHARED" common mode
  hidden_cmr    residual cosine, centered  -> residual after common-mode removal
  route_sign    sign(gate) cosine          -> the routing register (the claim's register)
  route_cmr     sign(gate) cosine, centered-> routing after common-mode removal  <-- KEY

Usage:
  uv run python scripts/experiments/tool_crystal_consensus.py \
      --model Qwen/Qwen3-8B --device mps --dtype bfloat16

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "tool-crystal-consensus"
PROBES_PATH = _PROJECT_ROOT / "lattice" / "tool_crystal" / "probes.json"

# layer fractions to capture (depth-normalized so models of different depth align)
LAYER_FRACS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# ---- probes -----------------------------------------------------------------
def render(prompt: str) -> str:
    """Strip model-specific chat special tokens -> plain text, so every family
    sees the SAME token surface (isolates internal routing from chat scaffolding)."""
    return (prompt.replace("<|im_start|>", "")
                  .replace("<|im_end|>", "")
                  .strip())


def load_probes(limit: int = 0, seed: int = 0):
    data = json.loads(PROBES_PATH.read_text())
    if limit and limit < len(data):
        rng = np.random.default_rng(seed)
        data = [data[i] for i in sorted(rng.permutation(len(data))[:limit])]
    prompts = [render(p["prompt"]) for p in data]
    domain = [p.get("domain", "?") for p in data]
    subdomain = [p.get("subdomain", "?") for p in data]
    return prompts, domain, subdomain


# ---- model introspection ----------------------------------------------------
def find_gate_modules(model):
    """Return ordered [(layer_idx, module, kind)] for the FFN gate/intermediate.
    SwiGLU (Qwen/Mistral/SmolLM/OLMo): mlp.gate_proj.  GPTNeoX (Pythia): mlp.dense_h_to_4h."""
    hits = []
    pat = re.compile(r"\.(\d+)\.mlp\.(gate_proj|dense_h_to_4h)$")
    for name, mod in model.named_modules():
        m = pat.search(name)
        if m:
            hits.append((int(m.group(1)), name, mod, m.group(2)))
    hits.sort(key=lambda x: x[0])
    kind = "gate_proj" if any(h[3] == "gate_proj" for h in hits) else "dense_h_to_4h"
    return [(li, name, mod) for (li, name, mod, k) in hits], kind


def pick_layers(n_layers: int):
    idxs = sorted({min(n_layers - 1, max(0, round(f * (n_layers - 1)))) for f in LAYER_FRACS})
    return idxs


# ---- capture ----------------------------------------------------------------
@torch.no_grad()
def collect(model, tokenizer, device, prompts, max_length, want_layers):
    """Return:
      hidden  [N x d]          final residual at last token (raw register)
      gate    {layer_idx: [N x d_ff]} gate pre-activation at last token (routing register)
    """
    gate_mods, kind = find_gate_modules(model)
    n_layers = len(gate_mods)
    want = set(want_layers)
    buf = {}

    def mk_hook(li):
        def hook(_m, _inp, out):
            # out: [B, T, d_ff]; take last token of batch item 0
            buf[li] = out[0, -1].detach().float().cpu().numpy().astype(np.float32)
        return hook

    handles = [mod.register_forward_hook(mk_hook(li))
               for (li, _nm, mod) in gate_mods if li in want]

    n = len(prompts)
    hidden = None
    gate = {li: None for li in want}
    plen = np.empty(n, np.int32)
    try:
        for i, text in enumerate(prompts):
            buf.clear()
            enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length)
            enc = {k: v.to(device) for k, v in enc.items()}
            out = model(**enc, output_hidden_states=True)
            h = out.hidden_states[-1][0, -1].float().cpu().numpy().astype(np.float32)
            if hidden is None:
                hidden = np.empty((n, h.shape[0]), np.float32)
            hidden[i] = h
            plen[i] = int(enc["input_ids"].shape[1])
            for li in want:
                g = buf[li]
                if gate[li] is None:
                    gate[li] = np.empty((n, g.shape[0]), np.float32)
                gate[li][i] = g
            del out
            if (i + 1) % 50 == 0:
                log(f"    {i + 1}/{n}")
    finally:
        for hd in handles:
            hd.remove()
    return hidden, gate, plen, kind, n_layers


# ---- RDMs -------------------------------------------------------------------
def cosine_rdm(X):
    X = X.astype(np.float64)
    nrm = np.linalg.norm(X, axis=1, keepdims=True) + 1e-30
    cos = np.clip((X / nrm) @ (X / nrm).T, -1, 1)
    d = 1.0 - cos
    np.fill_diagonal(d, 0.0)
    return d


def cmr(X):
    """Common-mode removal: subtract the per-feature mean across probes
    (kills the shared common mode that makes high-dim prose cosine ~1)."""
    return X - X.mean(axis=0, keepdims=True)


def upper(D):
    iu = np.triu_indices_from(D, k=1)
    return D[iu]


def separation(D, labels, mask=None, n_perm=2000, seed=0):
    """Permutation test: between-label mean dist minus within-label mean dist.
    mask: optional bool over probes to restrict to a sub-contrast."""
    lab = np.array(labels)
    if mask is not None:
        idx = np.where(mask)[0]
        D = D[np.ix_(idx, idx)]
        lab = lab[idx]
    iu = np.triu_indices_from(D, k=1)
    dv = D[iu]

    def gap(L):
        same = L[iu[0]] == L[iu[1]]
        if same.all() or (~same).all():
            return 0.0
        return dv[~same].mean() - dv[same].mean()

    obs = gap(lab)
    rng = np.random.default_rng(seed)
    null = np.array([gap(rng.permutation(lab)) for _ in range(n_perm)])
    sd = null.std() + 1e-30
    return {"gap": float(obs), "null_mean": float(null.mean()),
            "null_std": float(null.std()),
            "z": float((obs - null.mean()) / sd),
            "p_value": float((np.sum(null >= obs) + 1) / (n_perm + 1)),
            "n": len(lab)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--max-length", type=int, default=512)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    safe = args.model.replace("/", "_")
    t0 = time.time()

    prompts, domain, subdomain = load_probes(args.limit, args.seed)
    log(f"[{args.model}] {len(prompts)} tool-crystal probes")

    # contrast masks
    domain_arr = np.array(domain)
    sub_arr = np.array(subdomain)
    is_control = domain_arr == "control"
    recog_mask = np.isin(sub_arr, ["recognition/tool", "recognition/no_tool"])
    # tool vs control (broad) uses is_control as the label over all probes

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()

    # probe layer count first
    gate_mods, kind = find_gate_modules(model)
    n_layers = len(gate_mods)
    want_layers = pick_layers(n_layers)
    log(f"  arch: {n_layers} layers, FFN gate = {kind}; capturing layers {want_layers}")

    log("  forward passes ...")
    hidden, gate, plen, kind, n_layers = collect(model, tok, args.device, prompts,
                                                 args.max_length, want_layers)
    width = int(hidden.shape[1])
    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    # ---- build registers & RDMs ----
    log("  building RDMs (hidden raw/cmr; route_sign raw/cmr) per layer ...")
    out = {"model": args.model, "dtype": args.dtype, "n_probes": len(prompts),
           "hidden_width": width, "n_layers": n_layers, "gate_kind": kind,
           "want_layers": want_layers, "n_perm": args.n_perm,
           "git_sha": git_sha(), "domains": sorted(set(domain)),
           "per_layer": {}}

    rdm_store = {}  # for npz

    # hidden registers are layer-independent (final residual); compute once
    hid_full = cosine_rdm(hidden)
    hid_cmr = cosine_rdm(cmr(hidden))
    rdm_store["hidden_full"] = hid_full.astype(np.float32)
    rdm_store["hidden_cmr"] = hid_cmr.astype(np.float32)

    def both_selectivity(D):
        return {
            "recog_tool_vs_notool": separation(
                D, sub_arr, mask=recog_mask, n_perm=args.n_perm, seed=args.seed),
            "tool_vs_control": separation(
                D, is_control.astype(int), n_perm=args.n_perm, seed=args.seed),
            "domain_separation": separation(
                D, domain_arr, n_perm=args.n_perm, seed=args.seed),
        }

    out["hidden"] = {"full": both_selectivity(hid_full),
                     "cmr": both_selectivity(hid_cmr)}

    # routing register, per captured layer
    for li in want_layers:
        g = gate[li]
        sign = np.sign(g)
        r_full = cosine_rdm(sign)
        r_cmr = cosine_rdm(cmr(sign))
        rdm_store[f"route_sign_full_L{li:02d}"] = r_full.astype(np.float32)
        rdm_store[f"route_sign_cmr_L{li:02d}"] = r_cmr.astype(np.float32)
        out["per_layer"][str(li)] = {
            "frac": round(li / max(n_layers - 1, 1), 3),
            "d_ff": int(g.shape[1]),
            "route_sign_full": both_selectivity(r_full),
            "route_sign_cmr": both_selectivity(r_cmr),
        }
        st = out["per_layer"][str(li)]["route_sign_cmr"]["recog_tool_vs_notool"]
        log(f"    L{li:02d} (f={li/max(n_layers-1,1):.2f}) "
            f"route_cmr recog tool/no_tool: gap={st['gap']:+.4f} z={st['z']:+.2f} p={st['p_value']:.4f}")

    # best routing layer by recog selectivity (cmr)
    best_li = max(want_layers, key=lambda li:
                  out["per_layer"][str(li)]["route_sign_cmr"]["recog_tool_vs_notool"]["z"])
    out["best_routing_layer"] = int(best_li)
    out["elapsed_s"] = round(time.time() - t0, 1)

    # save probe-aligned RDMs (cross-model agreement done in summary; no re-run)
    np.savez_compressed(
        RESULTS_DIR / f"{safe}.npz",
        domain=domain_arr, subdomain=sub_arr, prompt_len=plen,
        **rdm_store)
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))

    hb = out["hidden"]["full"]["recog_tool_vs_notool"]
    hc = out["hidden"]["cmr"]["recog_tool_vs_notool"]
    rb = out["per_layer"][str(best_li)]["route_sign_full"]["recog_tool_vs_notool"]
    rc = out["per_layer"][str(best_li)]["route_sign_cmr"]["recog_tool_vs_notool"]
    log("")
    log(f"  === {args.model}  (recog tool vs no_tool selectivity) ===")
    log(f"  hidden_full  gap={hb['gap']:+.4f} z={hb['z']:+.2f} p={hb['p_value']:.4f}   (prior 'SHARED' register)")
    log(f"  hidden_cmr   gap={hc['gap']:+.4f} z={hc['z']:+.2f} p={hc['p_value']:.4f}")
    log(f"  route_full   gap={rb['gap']:+.4f} z={rb['z']:+.2f} p={rb['p_value']:.4f}   (L{best_li})")
    log(f"  route_cmr    gap={rc['gap']:+.4f} z={rc['z']:+.2f} p={rc['p_value']:.4f}   (L{best_li})  <-- KEY")
    log(f"  wrote {safe}.json + .npz  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
