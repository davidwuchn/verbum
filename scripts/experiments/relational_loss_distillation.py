#!/usr/bin/env python3
# register: functional + topological/routing
"""Relational-loss distillation — does the teacher's GEOMETRY transfer to a
student, and ONLY in the routing register?  (session 223)

THE IDEA (Michael):
  "Because we have the lambda compiler, extract from the teacher a set of
   training for the student.  With relational loss we could guide GD into any
   geometry that falls out."

  The teacher contributes NOT its weights and NOT its tokens, but its
  RELATIONAL GEOMETRY: the routing-register combinator Gram (the 9x9 cosine
  matrix between K I B C S D W Y WHNF centroids, after common-mode removal).
  A relational loss pulls the student's geometry toward the teacher's RELATIONS
  while leaving its absolute frame free ("any geometry that falls out").

THE FRAME ARGUMENT (why relational, not output/weight matching):
  absolute weights/signs : cross-init corr 0.000   (incommensurable)
  relational Gram        : cross-model +0.78        (universal)
  -> a relational loss targets EXACTLY the invariant and nothing else.

THE EXPERIMENT (3 conditions, tiny from-scratch byte-level student):
  (a) CE only
  (b) CE + relational loss on the RAW hidden-CMR Gram      <- control / decoy
  (c) CE + relational loss on the routing-CMR gate Gram    <- the hypothesis

THE FALSIFIABLE CLAIM (two-registers discipline, lambda measure):
  the combinator shape is INVISIBLE in raw geometry (silhouette ~ -0.035) and
  only appears in the ROUTING register after CMR (silhouette +0.101, z=7.97).
  So a relational loss on the RAW Gram (b) should match the common-mode crystal
  and transfer NOTHING combinator-specific, while (c) transfers the function.
  Prediction: silhouette-z and GramCorr-to-teacher:  (c) >> (b) ~ (a).
  If (b) ~ (c) -> the register claim is WRONG (we want to know immediately).

Verdict instrument (mirrors combinator_relationship_map.py): student sign(gate)
CMR combinator silhouette vs label-permutation null (z) + GramCorr(student,
teacher) on the off-diagonal.

Usage:
  uv run python scripts/experiments/relational_loss_distillation.py --smoke
  uv run python scripts/experiments/relational_loss_distillation.py \
      --steps 1500 --rel-lambda 1.0 --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))
from verbum.probes.library import all_probes, crystal_probes  # noqa: E402

RESULTS_DIR = _PROJECT_ROOT / "results" / "relational-loss-distillation"
TEACHER_DIR = _PROJECT_ROOT / "results" / "combinator-relationship-map"

CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
VOCAB = 256  # byte-level


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# ---- data -------------------------------------------------------------------
def build_corpus() -> str:
    """Self-contained CE corpus: all probe prompts joined (no external download)."""
    parts = [p.prompt for p in all_probes() if p.prompt]
    return "\n".join(parts)


def to_bytes(text: str, max_len: int) -> np.ndarray:
    b = text.encode("utf-8", errors="ignore")[:max_len]
    return np.frombuffer(b, dtype=np.uint8).astype(np.int64)


def load_crystal_probe_batch(max_len: int):
    """Return (padded_ids [N,L] int64, lengths [N] int64, labels [N] str)."""
    probes = crystal_probes()
    by: dict[str, list[str]] = {c: [] for c in CRYSTAL}
    for p in probes:
        if p.combinator in by:
            by[p.combinator].append(p.prompt)
    prompts, labels = [], []
    for c in CRYSTAL:
        for s in by[c]:
            prompts.append(s)
            labels.append(c)
    seqs = [to_bytes(s, max_len) for s in prompts]
    seqs = [s if len(s) > 0 else np.array([10], dtype=np.int64) for s in seqs]
    lengths = np.array([len(s) for s in seqs], dtype=np.int64)
    L = int(lengths.max())
    ids = np.zeros((len(seqs), L), dtype=np.int64)
    for i, s in enumerate(seqs):
        ids[i, : len(s)] = s
    return ids, lengths, np.array(labels)


# ---- model ------------------------------------------------------------------
class CausalSelfAttention(nn.Module):
    def __init__(self, d_model: int, n_head: int):
        super().__init__()
        assert d_model % n_head == 0
        self.n_head = n_head
        self.d_head = d_model // n_head
        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.proj = nn.Linear(d_model, d_model)

    def forward(self, x):
        B, T, C = x.shape
        qkv = self.qkv(x)
        q, k, v = qkv.split(C, dim=2)
        q = q.view(B, T, self.n_head, self.d_head).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.d_head).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.d_head).transpose(1, 2)
        att = (q @ k.transpose(-2, -1)) / math.sqrt(self.d_head)
        mask = torch.triu(torch.ones(T, T, device=x.device, dtype=torch.bool), 1)
        att = att.masked_fill(mask, float("-inf"))
        att = F.softmax(att, dim=-1)
        out = att @ v
        out = out.transpose(1, 2).contiguous().view(B, T, C)
        return self.proj(out)


class Block(nn.Module):
    """Pre-norm transformer block with a SwiGLU MLP. The gate pre-activation
    (w_gate output) IS the routing register (mirrors gate_proj in real models)."""

    def __init__(self, d_model: int, n_head: int, d_ff: int):
        super().__init__()
        self.ln1 = nn.LayerNorm(d_model)
        self.attn = CausalSelfAttention(d_model, n_head)
        self.ln2 = nn.LayerNorm(d_model)
        self.w_gate = nn.Linear(d_model, d_ff)
        self.w_up = nn.Linear(d_model, d_ff)
        self.w_down = nn.Linear(d_ff, d_model)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        h = self.ln2(x)
        gate = self.w_gate(h)               # <-- routing register (pre-activation)
        h = F.silu(gate) * self.w_up(h)
        x = x + self.w_down(h)
        return x, gate


class TinyLM(nn.Module):
    def __init__(self, d_model=128, n_head=4, n_layer=4, d_ff=256, block_size=64):
        super().__init__()
        self.block_size = block_size
        self.tok = nn.Embedding(VOCAB, d_model)
        self.pos = nn.Embedding(block_size, d_model)
        self.blocks = nn.ModuleList(
            [Block(d_model, n_head, d_ff) for _ in range(n_layer)])
        self.ln_f = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, VOCAB, bias=False)
        self.n_layer = n_layer

    def forward(self, idx, capture_layer: int | None = None):
        _B, T = idx.shape
        pos = torch.arange(T, device=idx.device)
        x = self.tok(idx) + self.pos(pos)[None]
        cap_hidden = cap_gate = None
        for li, blk in enumerate(self.blocks):
            x, gate = blk(x)
            if capture_layer is not None and li == capture_layer:
                cap_hidden = x          # residual after this block, all positions
                cap_gate = gate         # gate pre-activation, all positions
        logits = self.head(self.ln_f(x))
        return logits, cap_hidden, cap_gate


# ---- relational geometry (differentiable) -----------------------------------
def gather_last(feats, lengths):
    """feats [N,T,d], lengths [N] -> [N,d] at the last real token."""
    idx = (lengths - 1).clamp_min(0)
    return feats[torch.arange(feats.shape[0], device=feats.device), idx]


def soft_gram(feats, label_idx):
    """Differentiable routing/raw Gram. feats [N,d], label_idx [N] in 0..8.
    CMR (subtract per-feature mean over probes) -> per-combinator centroid ->
    cosine Gram [9,9]."""
    feats = feats - feats.mean(dim=0, keepdim=True)        # common-mode removal
    d = feats.shape[1]
    cents = torch.zeros(len(CRYSTAL), d, device=feats.device, dtype=feats.dtype)
    for j in range(len(CRYSTAL)):
        m = label_idx == j
        cents[j] = feats[m].mean(dim=0)
    u = cents / cents.norm(dim=1, keepdim=True).clamp_min(1e-8)
    return u @ u.t()


def offdiag_mse(g_pred, g_target):
    off = ~torch.eye(len(CRYSTAL), dtype=torch.bool, device=g_pred.device)
    return ((g_pred - g_target)[off] ** 2).mean()


# ---- verdict instrument (numpy, mirrors combinator_relationship_map) ---------
def np_cmr(X):
    return X - X.mean(axis=0, keepdims=True)


def np_unit(v):
    return v / (np.linalg.norm(v) + 1e-30)


def np_centroids(X, labels):
    C = np.zeros((len(CRYSTAL), X.shape[1]), np.float64)
    for j, c in enumerate(CRYSTAL):
        C[j] = X[labels == c].mean(axis=0)
    return C


def np_gram(C):
    U = np.array([np_unit(c) for c in C])
    return np.clip(U @ U.T, -1, 1)


def np_silhouette(X, labels):
    C = np_centroids(X, labels)
    U = np.array([np_unit(c) for c in C])
    Xu = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)
    sims = Xu @ U.T
    lab_idx = np.array([CRYSTAL.index(c) for c in labels])
    own = sims[np.arange(len(labels)), lab_idx]
    other = sims.copy()
    other[np.arange(len(labels)), lab_idx] = -np.inf
    return float(np.mean(own - other.max(axis=1)))


def np_silhouette_null(X, labels, n_perm=1000, seed=0):
    obs = np_silhouette(X, labels)
    rng = np.random.default_rng(seed)
    null = np.array([np_silhouette(X, rng.permutation(labels)) for _ in range(n_perm)])
    sd = null.std() + 1e-30
    return {"silhouette": obs, "null_mean": float(null.mean()),
            "null_std": float(null.std()), "z": float((obs - null.mean()) / sd),
            "p_value": float((np.sum(null >= obs) + 1) / (n_perm + 1))}


def offdiag_corr(g_a, g_b):
    off = ~np.eye(len(CRYSTAL), dtype=bool)
    a, b = g_a[off], g_b[off]
    if a.std() < 1e-9 or b.std() < 1e-9:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


# ---- training ---------------------------------------------------------------
def train_condition(name, rel_target, rel_kind, args, device, corpus_ids,
                    probe_ids, probe_len, probe_labels, teacher_route, teacher_hidden):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    model = TinyLM(args.d_model, args.n_head, args.n_layer, args.d_ff,
                   args.block_size).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    cap = args.capture_layer if args.capture_layer >= 0 else args.n_layer // 2
    label_idx = torch.tensor([CRYSTAL.index(c) for c in probe_labels], device=device)
    p_ids = torch.tensor(probe_ids, device=device)
    p_len = torch.tensor(probe_len, device=device)
    n_corpus = corpus_ids.shape[0]
    bs, T = args.batch_size, args.block_size
    g_target = (torch.tensor(rel_target, device=device, dtype=torch.float32)
                if rel_target is not None else None)
    t0 = time.time()
    last = {}
    for step in range(1, args.steps + 1):
        model.train()
        # CE batch: random windows
        ix = torch.randint(0, n_corpus - T - 1, (bs,))
        xb = torch.stack(
            [torch.from_numpy(corpus_ids[i:i + T]) for i in ix]).to(device)
        yb = torch.stack(
            [torch.from_numpy(corpus_ids[i + 1:i + 1 + T]) for i in ix]).to(device)
        logits, _, _ = model(xb)
        ce = F.cross_entropy(logits.reshape(-1, VOCAB), yb.reshape(-1))
        loss = ce
        rel_val = 0.0
        if g_target is not None and (step % args.rel_every == 0):
            feats = []
            for s in range(0, p_ids.shape[0], args.probe_batch):
                pb = p_ids[s:s + args.probe_batch]
                _, hid, gate = model(pb, capture_layer=cap)
                src = hid if rel_kind == "hidden" else gate
                feats.append(gather_last(src, p_len[s:s + args.probe_batch]))
            feats = torch.cat(feats, dim=0)
            g_pred = soft_gram(feats, label_idx)
            rel = offdiag_mse(g_pred, g_target)
            loss = ce + args.rel_lambda * rel
            rel_val = float(rel.item())
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % args.log_every == 0 or step == 1:
            log(f"  [{name}] step {step:5d} | CE {ce.item():.4f} | rel {rel_val:.5f} "
                f"| {(time.time()-t0):.0f}s")
            last = {"step": step, "ce": float(ce.item()), "rel": rel_val}

    # ---- verdict: measure in the SIGN routing register (teacher instrument) --
    model.eval()
    with torch.no_grad():
        gate_feats, hid_feats = [], []
        for s in range(0, p_ids.shape[0], args.probe_batch):
            pb = p_ids[s:s + args.probe_batch]
            _, hid, gate = model(pb, capture_layer=cap)
            pl = p_len[s:s + args.probe_batch]
            gate_feats.append(gather_last(gate, pl).cpu().numpy())
            hid_feats.append(gather_last(hid, pl).cpu().numpy())
    gate_np = np.concatenate(gate_feats, axis=0).astype(np.float64)
    hid_np = np.concatenate(hid_feats, axis=0).astype(np.float64)

    sign_cmr = np_cmr(np.sign(gate_np))
    route_sil = np_silhouette_null(sign_cmr, probe_labels, args.n_perm, args.seed)
    route_gram = np_gram(np_centroids(sign_cmr, probe_labels))
    hid_cmr = np_cmr(hid_np)
    hid_sil = np_silhouette_null(hid_cmr, probe_labels, args.n_perm, args.seed)
    hid_gram = np_gram(np_centroids(hid_cmr, probe_labels))

    verdict = {
        "condition": name,
        "rel_kind": rel_kind,
        "capture_layer": cap,
        "final": last,
        "route_cmr_silhouette": route_sil,
        "hidden_cmr_silhouette": hid_sil,
        "gramcorr_route_vs_teacher": offdiag_corr(route_gram, teacher_route),
        "gramcorr_hidden_vs_teacher": offdiag_corr(hid_gram, teacher_hidden),
    }
    log(f"  [{name}] VERDICT route_cmr silhouette z={route_sil['z']:+.2f} "
        f"p={route_sil['p_value']:.4f} | GramCorr(route,teacher)="
        f"{verdict['gramcorr_route_vs_teacher']:+.3f}")
    return verdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--teacher", default="Qwen_Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--steps", type=int, default=1500)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--block-size", type=int, default=64)
    ap.add_argument("--d-model", type=int, default=128)
    ap.add_argument("--n-head", type=int, default=4)
    ap.add_argument("--n-layer", type=int, default=4)
    ap.add_argument("--d-ff", type=int, default=256)
    ap.add_argument("--capture-layer", type=int, default=-1, help="-1 = middle")
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--rel-lambda", type=float, default=1.0)
    ap.add_argument("--rel-every", type=int, default=1)
    ap.add_argument("--probe-batch", type=int, default=64)
    ap.add_argument("--probe-max-len", type=int, default=96)
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--log-every", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--sweep", action="store_true",
                    help="multi-seed x lambda grid confirm")
    ap.add_argument("--seeds", default="0,1,2", help="csv seeds for --sweep")
    ap.add_argument("--lambdas", default="0.3,1.0,3.0", help="csv rel-lambdas")
    args = ap.parse_args()

    if args.smoke:
        args.steps, args.n_perm, args.log_every = 30, 200, 10
        args.d_model, args.d_ff, args.n_layer = 64, 128, 3

    device = args.device
    if device == "mps" and not torch.backends.mps.is_available():
        device = "cpu"
        log("  mps unavailable -> cpu")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    # ---- teacher targets ----
    tnpz = TEACHER_DIR / f"{args.teacher}.npz"
    tjson = TEACHER_DIR / f"{args.teacher}.json"
    d = np.load(tnpz, allow_pickle=True)
    best = json.loads(tjson.read_text())["best_routing_layer"]
    teacher_route = d[f"gram_route_cmr_L{best:02d}"].astype(np.float64)
    teacher_hidden = d["gram_hidden_cmr"].astype(np.float64)
    log(f"  teacher={args.teacher} best_layer=L{best:02d} "
        f"route_gram offdiag_mean={teacher_route[~np.eye(9,dtype=bool)].mean():+.3f}")

    # ---- data ----
    corpus_ids = to_bytes(build_corpus(), max_len=4_000_000)
    log(f"  corpus bytes={corpus_ids.shape[0]}")
    probe_ids, probe_len, probe_labels = load_crystal_probe_batch(args.probe_max_len)
    log(f"  crystal probes={probe_ids.shape[0]} maxlen={probe_ids.shape[1]}")

    def run_triple(seed, lam):
        """Run conditions a/b/c at one (seed, lambda); return list of verdicts."""
        args.seed, args.rel_lambda = seed, lam
        out_v = []
        for name, target, kind in [("a_ce_only", None, None),
                                   ("b_ce_raw_gram", teacher_hidden, "hidden"),
                                   ("c_ce_route_gram", teacher_route, "gate")]:
            log(f"\n=== {name} seed={seed} lambda={lam} ===")
            v = train_condition(name, target, kind, args, device, corpus_ids,
                                probe_ids, probe_len, probe_labels,
                                teacher_route, teacher_hidden)
            v["seed"], v["lam"] = seed, lam
            out_v.append(v)
        return out_v

    if not args.sweep:
        verdicts = run_triple(args.seed, args.rel_lambda)
        out = {
            "experiment": "relational-loss-distillation",
            "register": "functional + topological/routing",
            "teacher": args.teacher, "teacher_best_layer": int(best),
            "git_sha": git_sha(), "smoke": args.smoke,
            "config": vars(args), "elapsed_s": round(time.time() - t0, 1),
            "conditions": verdicts,
        }
        tag = "smoke" if args.smoke else "run"
        (RESULTS_DIR / f"verdict_{tag}.json").write_text(json.dumps(out, indent=2))
        log("\n  ==== RELATIONAL-LOSS DISTILLATION VERDICT ====")
        log(f"  {'condition':<18} {'route_z':>8} {'route_p':>8} {'GC(route)':>10} "
            f"{'hidden_z':>9} {'GC(hidden)':>11}")
        for v in verdicts:
            log(f"  {v['condition']:<18} {v['route_cmr_silhouette']['z']:>+8.2f} "
                f"{v['route_cmr_silhouette']['p_value']:>8.4f} "
                f"{v['gramcorr_route_vs_teacher']:>+10.3f} "
                f"{v['hidden_cmr_silhouette']['z']:>+9.2f} "
                f"{v['gramcorr_hidden_vs_teacher']:>+11.3f}")
        log("\n  PREDICTION: c(route) >> b(raw) ~ a  on route_z & GC(route).")
        log(f"  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({out['elapsed_s']}s)")
        return

    # ---- SWEEP: multi-seed x lambda grid ----
    seeds = [int(s) for s in args.seeds.split(",")]
    lambdas = [float(x) for x in args.lambdas.split(",")]
    log(f"\n  SWEEP seeds={seeds} lambdas={lambdas}")
    runs = []
    for lam in lambdas:
        for sd in seeds:
            runs.extend(run_triple(sd, lam))

    def summarize(rs):
        def ms(fn):
            a = np.array([fn(r) for r in rs], float)
            return [round(float(a.mean()), 4), round(float(a.std()), 4)]
        return {
            "n": len(rs),
            "route_z": ms(lambda r: r["route_cmr_silhouette"]["z"]),
            "route_p": ms(lambda r: r["route_cmr_silhouette"]["p_value"]),
            "gc_route": ms(lambda r: r["gramcorr_route_vs_teacher"]),
            "hidden_z": ms(lambda r: r["hidden_cmr_silhouette"]["z"]),
            "gc_hidden": ms(lambda r: r["gramcorr_hidden_vs_teacher"]),
            "ce": ms(lambda r: r["final"]["ce"]),
        }

    agg = {}
    for lam in lambdas:
        for cond in ("a_ce_only", "b_ce_raw_gram", "c_ce_route_gram"):
            rs = [r for r in runs if r["condition"] == cond and r["lam"] == lam]
            agg[f"{cond}@lam{lam}"] = summarize(rs)

    out = {
        "experiment": "relational-loss-distillation-sweep",
        "register": "functional + topological/routing",
        "teacher": args.teacher, "teacher_best_layer": int(best),
        "git_sha": git_sha(), "seeds": seeds, "lambdas": lambdas,
        "config": vars(args), "elapsed_s": round(time.time() - t0, 1),
        "aggregate": agg, "runs": runs,
    }
    (RESULTS_DIR / "verdict_sweep.json").write_text(json.dumps(out, indent=2))

    log("\n  ==== SWEEP AGGREGATE (mean +/- std over seeds) ====")
    hdr = (f"  {'cond@lambda':<22} {'route_z':>14} {'GC(route)':>14} "
           f"{'hidden_z':>14} {'GC(hidden)':>14}")
    log(hdr)
    for lam in lambdas:
        for cond in ("a_ce_only", "b_ce_raw_gram", "c_ce_route_gram"):
            s = agg[f"{cond}@lam{lam}"]
            log(f"  {cond + '@' + str(lam):<22} "
                f"{s['route_z'][0]:>+7.2f}+-{s['route_z'][1]:<5.2f} "
                f"{s['gc_route'][0]:>+7.3f}+-{s['gc_route'][1]:<5.3f} "
                f"{s['hidden_z'][0]:>+7.2f}+-{s['hidden_z'][1]:<5.2f} "
                f"{s['gc_hidden'][0]:>+7.3f}+-{s['gc_hidden'][1]:<5.3f}")
    log("\n  DECISIVE if c.route_z(mean-std) > a.route_z(mean+std) at every lambda")
    log("  and c.gc_route > b.gc_route consistently (routing register carries it).")
    for lam in lambdas:
        a = agg[f"a_ce_only@lam{lam}"]["route_z"]
        c = agg[f"c_ce_route_gram@lam{lam}"]["route_z"]
        bg = agg[f"b_ce_raw_gram@lam{lam}"]["gc_route"][0]
        cg = agg[f"c_ce_route_gram@lam{lam}"]["gc_route"][0]
        sep = (c[0] - c[1]) > (a[0] + a[1])
        log(f"    lambda={lam}: c-a separated={sep}  c.gc>b.gc={cg > bg} "
            f"(c.route_z={c[0]:+.2f}+-{c[1]:.2f} vs a={a[0]:+.2f}+-{a[1]:.2f})")
    log(f"\n  wrote {RESULTS_DIR / 'verdict_sweep.json'}  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
