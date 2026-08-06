#!/usr/bin/env python3
"""§P-TYPE-GRAM-1 runner — un-flatten the crystal gram by argument kind.

Pre-reg FROZEN s313 (mementum/knowledge/explore/gram-registers-and-the-
route-map.md §P-TYPE-GRAM-1, Michael-approved): when the SAME opcode fires
on arguments of different KINDS (atom / fn / app), does the routing
geometry organize by kind — a register that cross-cuts opcode identity?

Basis (30 states):
  9  crystal anchors: K I B C S D W Y WHNF   (library probes — TG4 gate)
  21 type-split:      X:t, X ∈ {K,I,B,C,S,D,W}, t ∈ {atom,fn,app}
                      (opcodes/data/type_probes.json, kernel-certified)

Pipeline: canonical sign-CMR (capture_gate -> calibrate(basis=BASIS30) ->
gram_from_centroids), consensus = mean gram over crystal-bearing layers
(sil_z >= 2; consensus_gram=None at calibrate per expanded_gram.py
precedent — the 9-subblock coherence vs the committed root.gram is
reported separately as TG4).

Gates (frozen; all label-nulls are FULL-PIPELINE — permute probe->node
assignments, recompute centroids/grams; the sign-CMR common mode is
label-independent, so kernels K = X X^T per layer are precomputed once
and permutations only rebuild membership matrices):

  TG1 TYPE-BLOCK  half-split reliability vs same-opcode-cross-kind
                  similarity; null = kind shuffle WITHIN opcode.
                  Passing = kind distinctions are real (beyond noise).
  TG2 CROSS-CUT   opcode-centered centroid gram: same-kind-different-
                  opcode vs different-kind-different-opcode contrast;
                  null = kind shuffle within opcode. Passing = kind is a
                  REGISTER (shared direction), not opcode flavor.
  TG3 POLES       advisory. PR of the opcode-centered type gram vs
                  matched-range null passed through the SAME centering
                  projector (rank-fair implementation of the frozen
                  matched-range null; the raw-random variant is
                  rank-inflated -> false +POLED). A shuffled-label PR
                  null is also reported for transparency.
  TG4 COHERENCE   9-subblock offdiag r vs committed root.gram >= 0.5
                  and >= 1 crystal-bearing layer; else verdict VOID
                  (committed runs: 0.71-0.80).
  TG5 SURFACE     TG2 statistic vs kind shuffle within
                  (opcode x length-tercile x paren-tercile) strata —
                  surface-complexity-preserving null. BUILD AMENDMENT
                  (pre-run, --validate-forced): significance alone cannot
                  detect "surface explains it" — a stratified null that
                  RETAINS most of the contrast can still sit tightly
                  below the observation (validate surface world: retained
                  ~0.9, p=0.015 -> false TYPE-REGISTER). Gate therefore
                  requires p < alpha AND retained_frac < 0.5, where
                  retained_frac = stratified-null mean / observed
                  contrast (the fraction of the effect surface explains).

Verdict tree (frozen): INCOHERENT (!TG4) -> NO-TYPE-SIGNAL (!TG1) ->
OPCODE-FLAVOR-ONLY (!TG2) -> SURFACE-STYLE (!TG5) -> TYPE-REGISTER
(+POLED iff TG3).

Output: results/type-gram/{slug}/{results.json, centroids.npz}

Usage:
    uv run python opcodes/type_gram.py --validate     # synthetic worlds
    uv run python opcodes/type_gram.py --smoke        # pythia-14m, quick
    uv run python opcodes/type_gram.py --models qwen3-4b
    uv run python opcodes/type_gram.py                # full registry sweep

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_HERE))

import capture as C  # noqa: E402
from classify import RelationalCrystalClassifier  # noqa: E402
from probes import crystal_probes  # noqa: E402
from sweep import REGISTRY  # noqa: E402
from topology import detect_topology  # noqa: E402
from type_probes import KINDS, TYPE_OPS  # noqa: E402
from vsm import gram_from_centroids, offdiag_corr  # noqa: E402

CRYSTAL9 = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
TYPE_NODES = [f"{o}:{t}" for o in TYPE_OPS for t in KINDS]
BASIS30 = [*CRYSTAL9, *TYPE_NODES]
PROBE_JSON = _HERE / "data" / "type_probes.json"

ALPHA = 0.05
TG4_R_MIN = 0.5
N_NULL = 1000
SEED = 20260806


# ── probe loading ────────────────────────────────────────────────────────────
def load_probe_sets(n_per_state: int):
    """(prompts, labels) over BASIS30 + per-probe surface stats for the
    type probes (lengths, parens; crystal anchors carry None)."""
    prompts, labels = [], []
    rng = np.random.default_rng(0)
    by: dict[str, list[str]] = {c: [] for c in CRYSTAL9}
    for p in crystal_probes():
        if p.combinator in by:
            by[p.combinator].append(p.prompt)
    for c in CRYSTAL9:
        sel = by[c]
        if len(sel) > n_per_state:
            idx = rng.choice(len(sel), size=n_per_state, replace=False)
            sel = [sel[i] for i in sorted(idx)]
        prompts += sel
        labels += [c] * len(sel)
    d = json.loads(PROBE_JSON.read_text())["states"]
    for state in TYPE_NODES:
        sel = d[state][:n_per_state]
        prompts += sel
        labels += [state] * len(sel)
    return prompts, labels


def surface_strata(labels_op: np.ndarray, lengths: np.ndarray,
                   parens: np.ndarray) -> np.ndarray:
    """Stratum id per type probe: opcode x length-tercile x paren-tercile
    (terciles computed within each opcode pool)."""
    strata = np.zeros(len(labels_op), dtype=np.int64)
    for o in np.unique(labels_op):
        m = labels_op == o
        lt = np.searchsorted(np.quantile(lengths[m], [1 / 3, 2 / 3]),
                             lengths[m], side="right")
        pt = np.searchsorted(np.quantile(parens[m], [1 / 3, 2 / 3]),
                             parens[m], side="right")
        strata[m] = o * 9 + lt * 3 + pt
    return strata


# ── gram-space statistics (label-null machinery) ─────────────────────────────
def _membership(node_ids: np.ndarray, n_nodes: int) -> np.ndarray:
    """[n_nodes, N] row-normalized indicator (mean-pooling matrix)."""
    M = np.zeros((n_nodes, len(node_ids)), dtype=np.float64)
    for nd in range(n_nodes):
        m = node_ids == nd
        c = m.sum()
        if c:
            M[nd, m] = 1.0 / c
    return M


def _normalize_gram(G: np.ndarray) -> np.ndarray:
    d = np.sqrt(np.clip(np.diag(G), 1e-30, None))
    return G / np.outer(d, d)


def _center_projector(n_ops: int, n_kinds: int) -> np.ndarray:
    """[n_nodes, n_nodes] projector removing the per-opcode mean over kinds
    (node order = op-major: op*n_kinds + kind)."""
    n = n_ops * n_kinds
    P = np.eye(n)
    for o in range(n_ops):
        s = slice(o * n_kinds, (o + 1) * n_kinds)
        P[s, s] -= 1.0 / n_kinds
    return P


class TypeGramStats:
    """TG1/TG2/TG3 statistics for one labeling, from precomputed per-layer
    probe kernels K = X X^T (type probes only). Permutation nulls rebuild
    only the membership matrices — full-pipeline, d-independent cost."""

    def __init__(self, kernels: list[np.ndarray], n_ops: int, n_kinds: int,
                 half_rank: np.ndarray):
        self.kernels = kernels
        self.n_ops, self.n_kinds = n_ops, n_kinds
        self.n_nodes = n_ops * n_kinds
        self.half_rank = half_rank          # fixed random probe order
        self.P = _center_projector(n_ops, n_kinds)
        node_op = np.repeat(np.arange(n_ops), n_kinds)
        node_kind = np.tile(np.arange(n_kinds), n_ops)
        same_op = node_op[:, None] == node_op[None, :]
        same_kind = node_kind[:, None] == node_kind[None, :]
        eye = np.eye(self.n_nodes, dtype=bool)
        self.pair_sameop_diffkind = same_op & ~same_kind & ~eye
        self.pair_samekind_diffop = same_kind & ~same_op
        self.pair_diffkind_diffop = ~same_kind & ~same_op

    def node_ids(self, labels_op: np.ndarray,
                 labels_kind: np.ndarray) -> np.ndarray:
        return labels_op * self.n_kinds + labels_kind

    def half_ids(self, node_ids: np.ndarray) -> np.ndarray:
        """Split each node's probes into two halves by the fixed order."""
        half = np.zeros(len(node_ids), dtype=np.int64)
        for nd in range(self.n_nodes):
            idx = np.where(node_ids == nd)[0]
            idx = idx[np.argsort(self.half_rank[idx])]
            half[idx[: len(idx) // 2]] = 0
            half[idx[len(idx) // 2:]] = 1
        return node_ids * 2 + half

    def stats(self, labels_op: np.ndarray, labels_kind: np.ndarray
              ) -> tuple[float, float, float]:
        """(tg1_stat, tg2_stat, pr_centered) aggregated over layers."""
        nid = self.node_ids(labels_op, labels_kind)
        hid = self.half_ids(nid)
        M = _membership(nid, self.n_nodes)
        Mh = _membership(hid, self.n_nodes * 2)
        t1, t2, prs = [], [], []
        for K in self.kernels:
            H = _normalize_gram(Mh @ K @ Mh.T)
            rel = np.mean([H[2 * i, 2 * i + 1]
                           for i in range(self.n_nodes)])
            # same-op diff-kind similarity read on half rows (all 4 combos)
            big = np.kron(self.pair_sameop_diffkind,
                          np.ones((2, 2), dtype=bool))
            t1.append(rel - H[big].mean())

            Cg = M @ K @ M.T
            Gc = _normalize_gram(self.P @ Cg @ self.P.T)
            t2.append(Gc[self.pair_samekind_diffop].mean()
                      - Gc[self.pair_diffkind_diffop].mean())
            ev = np.clip(np.linalg.eigvalsh(Gc), 0, None)
            prs.append(float((ev.sum() ** 2) / (np.sum(ev ** 2) + 1e-30)))
        return float(np.mean(t1)), float(np.mean(t2)), float(np.mean(prs))

    def matched_range_pr_null(self, labels_op: np.ndarray,
                              labels_kind: np.ndarray, n_iter: int,
                              rng: np.random.Generator) -> np.ndarray:
        """Frozen TG3 null, rank-fair: symmetric matrices with off-diag
        resampled from the observed CENTERED gram's off-diagonals, passed
        through the SAME centering projector before PR."""
        nid = self.node_ids(labels_op, labels_kind)
        M = _membership(nid, self.n_nodes)
        offs = []
        for K in self.kernels:
            Gc = _normalize_gram(self.P @ (M @ K @ M.T) @ self.P.T)
            offs.append(Gc[~np.eye(self.n_nodes, dtype=bool)])
        pool = np.concatenate(offs)
        n = self.n_nodes
        iu = np.triu_indices(n, k=1)
        out = np.empty(n_iter)
        for it in range(n_iter):
            R = np.eye(n)
            vals = rng.choice(pool, size=len(iu[0]))
            R[iu] = vals
            R[(iu[1], iu[0])] = vals
            Gn = _normalize_gram(self.P @ R @ self.P.T)
            ev = np.clip(np.linalg.eigvalsh(Gn), 0, None)
            out[it] = (ev.sum() ** 2) / (np.sum(ev ** 2) + 1e-30)
        return out


def _perm_within(groups: np.ndarray, values: np.ndarray,
                 rng: np.random.Generator) -> np.ndarray:
    out = values.copy()
    for g in np.unique(groups):
        idx = np.where(groups == g)[0]
        out[idx] = values[idx[rng.permutation(len(idx))]]
    return out


def score_type_gates(kernels: list[np.ndarray], labels_op: np.ndarray,
                     labels_kind: np.ndarray, lengths: np.ndarray,
                     parens: np.ndarray, n_iter: int = N_NULL,
                     alpha: float = ALPHA, seed: int = SEED) -> dict:
    """TG1/TG2/TG3/TG5 from per-layer type-probe kernels. TG4 is scored
    by the caller (needs the crystal anchors + committed root gram)."""
    rng = np.random.default_rng(seed)
    st = TypeGramStats(kernels, len(TYPE_OPS), len(KINDS),
                       half_rank=rng.permutation(len(labels_op)))
    obs1, obs2, obs_pr = st.stats(labels_op, labels_kind)

    strata = surface_strata(labels_op, lengths, parens)
    null1 = np.empty(n_iter)
    null2 = np.empty(n_iter)
    null_pr = np.empty(n_iter)
    null5 = np.empty(n_iter)
    for it in range(n_iter):
        k_op = _perm_within(labels_op, labels_kind, rng)
        n1, n2, npr = st.stats(labels_op, k_op)
        null1[it], null2[it], null_pr[it] = n1, n2, npr
        k_strat = _perm_within(strata, labels_kind, rng)
        _, n5, _ = st.stats(labels_op, k_strat)
        null5[it] = n5

    def p_greater(obs, null):
        return float((1 + np.sum(null >= obs)) / (1 + len(null)))

    p1 = p_greater(obs1, null1)
    p2 = p_greater(obs2, null2)
    p5 = p_greater(obs2, null5)
    retained5 = float(null5.mean() / obs2) if obs2 > 1e-12 else 1.0
    mr = st.matched_range_pr_null(labels_op, labels_kind, n_iter, rng)
    p3_matched = float((1 + np.sum(mr <= obs_pr)) / (1 + len(mr)))
    p3_shuffled = float((1 + np.sum(null_pr <= obs_pr)) / (1 + len(null_pr)))

    return {
        "tg1": {"stat": round(obs1, 4), "p": p1, "pass": bool(p1 < alpha),
                "null_mean": round(float(null1.mean()), 4)},
        "tg2": {"stat": round(obs2, 4), "p": p2, "pass": bool(p2 < alpha),
                "null_mean": round(float(null2.mean()), 4)},
        "tg3": {"pr_centered": round(obs_pr, 3),
                "p_matched_range": p3_matched,
                "p_shuffled_label": p3_shuffled,
                "pass": bool(p3_matched < alpha),
                "null_pr_matched_mean": round(float(mr.mean()), 3),
                "null_pr_shuffled_mean": round(float(null_pr.mean()), 3)},
        "tg5": {"stat": round(obs2, 4), "p": p5,
                "retained_frac": round(retained5, 3),
                "pass": bool(p5 < alpha and retained5 < 0.5),
                "null_mean": round(float(null5.mean()), 4),
                "n_strata": len(np.unique(strata))},
        "n_iter": n_iter, "alpha": alpha,
    }


def verdict_from_gates(gates: dict, tg4_pass: bool) -> str:
    if not tg4_pass:
        return "INCOHERENT"
    if not gates["tg1"]["pass"]:
        return "NO-TYPE-SIGNAL"
    if not gates["tg2"]["pass"]:
        return "OPCODE-FLAVOR-ONLY"
    if not gates["tg5"]["pass"]:
        return "SURFACE-STYLE"
    return "TYPE-REGISTER" + ("+POLED" if gates["tg3"]["pass"] else "")


# ── model run ────────────────────────────────────────────────────────────────
def run_model(spec, n_per_state: int, n_iter: int, out_root: Path
              ) -> dict | None:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    slug = spec.slug
    print(f"[tgram] ===== {spec.model} ({spec.device}) =====", file=sys.stderr)
    tok = AutoTokenizer.from_pretrained(spec.model)
    dtype = torch.bfloat16 if spec.tier == "large" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        spec.model, torch_dtype=dtype, trust_remote_code=True)
    model = model.to(spec.device).eval()
    topo = detect_topology(model, model.config)

    prompts, labels = load_probe_sets(n_per_state)
    labels_arr = np.array(labels)
    is_type = np.array([lb in TYPE_NODES for lb in labels])
    n = len(prompts)
    print(f"[tgram] {slug}: {n} probes x {topo.n_layers} layers",
          file=sys.stderr)

    feats: dict[int, list[np.ndarray]] = {}
    for i, text in enumerate(prompts):
        cap = C.capture_gate(model, tok, text, topo=topo)
        for li, arr in cap.gate.items():
            feats.setdefault(li, []).append(
                np.sign(arr[-1]).astype(np.int8))       # last-token sign row
        if (i + 1) % 200 == 0:
            print(f"[tgram] {slug}: probe {i + 1}/{n}", file=sys.stderr)
    del model
    gc.collect()
    if spec.device == "mps":
        torch.mps.empty_cache()

    layers = sorted(feats)
    gate_by_layer = {li: np.stack(feats[li]).astype(np.float32)
                     for li in layers}
    del feats
    clf = RelationalCrystalClassifier(layers, consensus_gram=None,
                                      basis=BASIS30)
    calib = clf.calibrate(gate_by_layer, labels_arr)

    per_layer, gated_grams, gated_cents, kernels, gated_layers = {}, [], [], [], []
    for li in layers:
        cal = calib[li]
        g = gram_from_centroids(cal.centroids, BASIS30)
        per_layer[str(li)] = {"sil_z": round(float(cal.silhouette_z), 3),
                              "bearing": bool(cal.crystal_bearing)}
        if cal.crystal_bearing:
            gated_grams.append(g)
            gated_cents.append(cal.centroids)
            # full-pipeline null substrate: CMR'd type-probe features
            S = np.sign(gate_by_layer[li].astype(np.float64))
            X = (S - S.mean(axis=0))[is_type]
            kernels.append((X @ X.T).astype(np.float64))
            gated_layers.append(li)
    del gate_by_layer
    gc.collect()

    consensus = (np.mean(np.stack(gated_grams), axis=0)
                 if gated_grams else None)

    # TG4 — 9-subblock coherence vs the committed root gram
    coherence = None
    vsm_path = _ROOT / "results" / "opcode-trace" / slug / "model_vsm.json"
    if consensus is not None and vsm_path.exists():
        ref = json.loads(vsm_path.read_text())
        rb, rg = ref["basis"], np.array(ref["root"]["gram"], float)
        if set(CRYSTAL9) <= set(rb):
            ia = [BASIS30.index(o) for o in CRYSTAL9]
            ib = [rb.index(o) for o in CRYSTAL9]
            coherence = round(offdiag_corr(consensus[np.ix_(ia, ia)],
                                           rg[np.ix_(ib, ib)]), 4)
    tg4_pass = bool(gated_grams) and coherence is not None \
        and coherence >= TG4_R_MIN
    print(f"[tgram] {slug}: gated={len(gated_grams)}/{len(layers)} "
          f"coherence_r={coherence} tg4={'PASS' if tg4_pass else 'FAIL'}",
          file=sys.stderr)

    gates, verdict = None, "INCOHERENT"
    if gated_grams:
        tl = labels_arr[is_type]
        labels_op = np.array([TYPE_OPS.index(x.split(":")[0]) for x in tl])
        labels_kind = np.array([KINDS.index(x.split(":")[1]) for x in tl])
        tp = [prompts[i] for i in np.where(is_type)[0]]
        lengths = np.array([len(p) for p in tp], dtype=float)
        parens = np.array([p.count("(") for p in tp], dtype=float)
        print(f"[tgram] {slug}: scoring {len(kernels)} layer kernels x "
              f"{n_iter} nulls", file=sys.stderr)
        gates = score_type_gates(kernels, labels_op, labels_kind, lengths,
                                 parens, n_iter=n_iter)
        verdict = verdict_from_gates(gates, tg4_pass)
    print(f"[tgram] {slug}: VERDICT: {verdict}", file=sys.stderr)

    out = out_root / slug
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": spec.model, "slug": slug,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": _git_sha(),
        "prereg": "§P-TYPE-GRAM-1 (frozen s313)",
        "basis": BASIS30, "n_per_state": n_per_state, "n_probes": n,
        "probe_source": str(PROBE_JSON.relative_to(_ROOT)),
        "probe_sha256": hashlib.sha256(
            PROBE_JSON.read_bytes()).hexdigest()[:16],
        "register": "gate (sign-CMR, off-target null)",
        "aggregation": "mean gram over crystal-bearing layers (sil_z>=2)",
        "n_layers": len(layers), "n_gated": len(gated_grams),
        "gated_layers": gated_layers,
        "per_layer": per_layer,
        "coherence_r_9subblock_vs_root_gram": coherence,
        "tg4": {"r": coherence, "r_min": TG4_R_MIN, "pass": tg4_pass},
        "gates": gates,
        "verdict": verdict,
        "consensus_gram_30": ([[round(float(v), 4) for v in row]
                               for row in consensus]
                              if consensus is not None else None),
    }
    (out / "results.json").write_text(json.dumps(payload, indent=1))
    if gated_cents:
        np.savez_compressed(
            out / "centroids.npz",
            basis=np.array(BASIS30),
            layers=np.array(gated_layers),
            centroids=np.stack(gated_cents).astype(np.float16))
    print(f"[tgram] {slug}: wrote {out}/results.json", file=sys.stderr)
    del kernels
    gc.collect()
    return payload


def _git_sha():
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                           text=True, cwd=_ROOT, timeout=10)
        return r.stdout.strip() or None
    except Exception:
        return None


# ── validate: synthetic planted worlds ───────────────────────────────────────
def _synth_world(kind_mode: str, rng: np.random.Generator,
                 m_per_node: int = 24, d: int = 192, noise: float = 1.2):
    """Synthetic CMR'd features for one world. Returns
    (kernels, labels_op, labels_kind, lengths, parens)."""
    n_ops, n_kinds = len(TYPE_OPS), len(KINDS)
    labels_op = np.repeat(np.arange(n_ops), n_kinds * m_per_node)
    labels_kind = np.tile(np.repeat(np.arange(n_kinds), m_per_node), n_ops)
    n = len(labels_op)
    v_op = rng.normal(size=(n_ops, d)) * 2.0
    v_kind = rng.normal(size=(n_kinds, d)) * 1.2
    v_opkind = rng.normal(size=(n_ops, n_kinds, d)) * 1.2
    v_stratum = rng.normal(size=(3, d)) * 1.2

    # surface stats: independent of kind by default
    lengths = rng.uniform(50, 100, size=n)
    parens = rng.integers(5, 12, size=n).astype(float)
    stratum = np.zeros(n, dtype=int)

    if kind_mode == "surface":
        # kind correlated with a surface stratum that drives geometry
        stratum = labels_kind.copy()
        flip = rng.random(n) < 0.1
        stratum[flip] = rng.integers(0, 3, size=int(flip.sum()))
        lengths = 50.0 + 25.0 * stratum + rng.uniform(-4, 4, size=n)
        parens = 5.0 + 3.0 * stratum + rng.integers(0, 2, size=n)

    X = v_op[labels_op] + noise * rng.normal(size=(n, d))
    if kind_mode == "register":
        X += v_kind[labels_kind]
    elif kind_mode == "flavor":
        X += v_opkind[labels_op, labels_kind]
    elif kind_mode == "surface":
        X += v_stratum[stratum]
    elif kind_mode == "none":
        pass
    else:
        raise ValueError(kind_mode)
    X -= X.mean(axis=0)
    K = X @ X.T
    return [K, K.copy()], labels_op, labels_kind, lengths, parens


def validate() -> int:
    n_fail = 0

    def check(name: str, ok: bool, detail: str = "") -> None:
        nonlocal n_fail
        mark = "PASS" if ok else "FAIL"
        if not ok:
            n_fail += 1
        print(f"[validate] {mark} {name} {detail}", file=sys.stderr)

    rng = np.random.default_rng(7)
    worlds = {
        "register": "TYPE-REGISTER",
        "flavor": "OPCODE-FLAVOR-ONLY",
        "surface": "SURFACE-STYLE",
        "none": "NO-TYPE-SIGNAL",
    }
    for mode, want in worlds.items():
        kern, lo, lk, ln, pa = _synth_world(mode, rng)
        gates = score_type_gates(kern, lo, lk, ln, pa, n_iter=200,
                                 seed=11)
        got = verdict_from_gates(gates, tg4_pass=True)
        ok = got == want or (want == "TYPE-REGISTER"
                             and got.startswith("TYPE-REGISTER"))
        check(f"world {mode} -> {want}", ok,
              f"got {got} (tg1 p={gates['tg1']['p']:.3f} "
              f"tg2 p={gates['tg2']['p']:.3f} tg5 p={gates['tg5']['p']:.3f})")

    # TG4 / INCOHERENT world: coherence machinery on planted grams
    ref = np.clip(rng.normal(scale=0.3, size=(9, 9)), -1, 1)
    ref = (ref + ref.T) / 2
    np.fill_diagonal(ref, 1.0)
    near = np.clip(ref + rng.normal(scale=0.05, size=(9, 9)), -1, 1)
    near = (near + near.T) / 2
    np.fill_diagonal(near, 1.0)
    scram = ref[np.ix_(rng.permutation(9), rng.permutation(9))]
    r_near = offdiag_corr(near, ref)
    r_scram = offdiag_corr(scram, ref)
    check("tg4 coherent gram passes", r_near >= TG4_R_MIN,
          f"r={r_near:.3f}")
    check("tg4 scrambled gram voids", r_scram < TG4_R_MIN,
          f"r={r_scram:.3f}")
    check("verdict INCOHERENT on tg4 fail",
          verdict_from_gates({"tg1": {"pass": True}, "tg2": {"pass": True},
                              "tg3": {"pass": True}, "tg5": {"pass": True}},
                             tg4_pass=False) == "INCOHERENT")

    # probe-set sanity: 21 nodes at full count + basis alignment
    d = json.loads(PROBE_JSON.read_text())["states"]
    check("probe json has all 21 nodes",
          sorted(d.keys()) == sorted(TYPE_NODES))
    check("probe nodes balanced >= 50",
          all(len(v) >= 50 for v in d.values()))
    _prompts, labels = load_probe_sets(12)
    check("basis30 load: 30 states populated",
          len(set(labels)) == 30, f"{len(set(labels))} states")

    print(f"[validate] {'ALL PASS' if n_fail == 0 else f'{n_fail} FAILURES'}",
          file=sys.stderr)
    return n_fail


def main() -> None:
    ap = argparse.ArgumentParser(description="§P-TYPE-GRAM-1 type-gram "
                                             "runner")
    ap.add_argument("--models", nargs="*", default=None,
                    help="HF names or slugs; default = full registry")
    ap.add_argument("--n-per-state", type=int, default=60)
    ap.add_argument("--n-null", type=int, default=N_NULL)
    ap.add_argument("--smoke", action="store_true",
                    help="pythia-14m only, n_per_state=12, n_null=100")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--output-root",
                    default=str(_ROOT / "results" / "type-gram"))
    args = ap.parse_args()

    if args.validate:
        sys.exit(1 if validate() else 0)

    specs = list(REGISTRY)
    if args.smoke:
        specs = [s for s in specs if "14m" in s.model]
        args.n_per_state = min(args.n_per_state, 12)
        args.n_null = min(args.n_null, 100)
    elif args.models:
        want = {m.lower() for m in args.models}
        specs = [s for s in specs
                 if s.model.lower() in want or s.slug in want]
    out_root = Path(args.output_root)
    out_root.mkdir(parents=True, exist_ok=True)

    summary = {}
    for spec in specs:
        try:
            r = run_model(spec, args.n_per_state, args.n_null, out_root)
            summary[spec.slug] = {
                "ok": r is not None,
                "verdict": (r or {}).get("verdict"),
                "coherence": (r or {}).get(
                    "coherence_r_9subblock_vs_root_gram"),
                "n_gated": (r or {}).get("n_gated")}
        except Exception as e:
            print(f"[tgram] {spec.slug}: FAILED {type(e).__name__}: {e}",
                  file=sys.stderr)
            summary[spec.slug] = {"ok": False, "error": str(e)[:200]}
    (out_root / "sweep_summary.json").write_text(json.dumps(
        {"timestamp_utc": datetime.now(UTC).isoformat(),
         "summary": summary}, indent=1))
    print(f"[tgram] SWEEP DONE: {summary}", file=sys.stderr)


if __name__ == "__main__":
    main()
