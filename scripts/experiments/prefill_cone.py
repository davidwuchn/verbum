#!/usr/bin/env python3
"""§P-PREFILL-CONE — the interior of the prefill triangle (frozen s335, Amendments 1–2).

Every tape-face law this project owns was read at the LAST column of the prefill
grid. This harness reads the INTERIOR: for kernel-certified lambda terms it
diffs the (position × layer) residual grid under a single-leaf perturbation and
asks whether the machine's dependency cone matches the calculus's — computed
under BOTH capture-avoiding (``R_NORMAL``) and naive (``R_NAIVE``) substitution
by :mod:`verbum.cone`.

Probe shape (Amendment 2). Each battery term is

    (λd.λr.r) c (BASE e f)

where BASE is a subst_pairs capture term. Three leaf ROLES fall out of the
kernel, and every role is certified per term, per leaf:

    none        — ``c``: discarded under BOTH calculi ⇒ the negative control,
                  and it sits UPSTREAM of the readout cell
    both        — dependency under BOTH calculi ⇒ the positive control
    naive_only  — ``e``: the correct NF DISCARDS it, the naive NF is BUILT from
                  it ⇒ the discriminator (9 of 18 terms)

Readout cell = the root span's closing token (downstream of every leaf).
Arrival fraction ``(Δ_naive_only − Δ_none) / (Δ_both − Δ_none)`` ≈ 1 means the
discarded-under-correct-semantics argument reaches the term's final cell
(naive); ≈ 0 means it is dropped like the control (capture-avoiding).

Measurables (registers named at freeze, AGENTS.md ``λ measure``):
  M1 value        — subterm-NF first-token rank at the subterm's closing cell
  M2 value        — per-cell normalized residual Δ (the cone substrate)
  M3 value        — D_naive at the readout cell (the headline discriminator)
  M4 value+routing— answer-column necessity lens + value-weighted read-mass
                    (routing half ADVISORY, s206 scar: never bare QK)

``--validate`` drives planted CONE-NAIVE / CONE-CORRECT worlds through the REAL
scoring and gate path (s331: planted plumbing must be probe plumbing). No model
is loaded.

License: MIT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from verbum.cone import (
    LeafPerturbation,
    Span,
    annotate,
    leaf_perturbations,
    span_token_range,
    term_names,
)
from verbum.lambda_ast import (
    R_NAIVE,
    R_NORMAL,
    Status,
    parse,
    pretty,
    reduce,
)
from verbum.probes.subst_pairs import capture_pairs
from verbum.probes.subst_pairs import validate as subst_validate

# ── frozen constants ────────────────────────────────────────────────────────
REPLS = ("n", "m", "t")  # M3 replication axis (fresh for every battery term)
N_PERM = 10_000
PC1_MIN_RANK_GAIN = 10.0
PC2_MIN_CLIFF = 0.2
ALPHA = 0.05

_FEWSHOT_DIRECT = (
    "Reduce each lambda-calculus term to its normal form, renaming bound "
    "variables as needed to avoid variable capture.\n\n"
    "Term: (λx.x) a\nNormal form: a\n\n"
    "Term: (λx.λy.x) p q\nNormal form: p\n\n"
    "Term: (λf.λx.f (f x)) g z\nNormal form: g (g z)\n\n"
)
_TERM_PREFIX = "Term: "
_TERM_SUFFIX = "\nNormal form:"


def wrap_term(base: str) -> str:
    """Amendment 2 probe shape: upstream discarded control + trailing args."""
    return f"(λd.λr.r) c ({base} e f)"


def build_prompt(term_text: str) -> tuple[str, int]:
    """Full prompt + the char offset at which ``term_text`` starts."""
    head = _FEWSHOT_DIRECT + _TERM_PREFIX
    return head + term_text + _TERM_SUFFIX, len(head)


# ── battery ─────────────────────────────────────────────────────────────────
@dataclass(frozen=True, slots=True)
class TermSpec:
    id: str
    base_term: str
    term: str
    correct_nf: str
    naive_nf: str
    spans: list[Span]
    span_nf: list[str | None]
    root: int  # span index of the whole term (the readout span)
    perts: dict[str, list[LeafPerturbation]] = field(default_factory=dict)
    roles: dict[str, str] = field(default_factory=dict)  # leaf name → role


def leaf_role(lp: LeafPerturbation, root: int) -> str:
    """Certified dependency role of a leaf w.r.t. the WHOLE term."""
    inn, inv = root in lp.cone_normal, root in lp.cone_naive
    if inv and not inn:
        return "naive_only"
    if inn and not inv:
        return "correct_only"
    return "both" if inn else "none"


def build_battery() -> list[TermSpec]:
    seen: set[str] = set()
    bases: list[tuple[str, str]] = []
    for p in capture_pairs():
        if p.mode != "direct":
            continue
        canon = pretty(parse(p.term))
        if canon not in seen:
            seen.add(canon)
            bases.append((p.id.replace("_direct", ""), canon))

    out: list[TermSpec] = []
    for pid, bt in bases:
        term = wrap_term(bt)
        t = parse(term)
        if pretty(t) != term:
            raise ValueError(f"{pid}: non-canonical wrapped term {term!r}")
        rn, rv = reduce(t, calc=R_NORMAL), reduce(t, calc=R_NAIVE)
        if rn.status is not Status.NORMAL_FORM or rv.status is not Status.NORMAL_FORM:
            raise ValueError(f"{pid}: wrapped term does not normalize under both")
        if pretty(rn.normal_form) == pretty(rv.normal_form):
            raise ValueError(f"{pid}: wrapped term no longer discriminates")
        text, spans, subterms = annotate(t)
        root = max(range(len(spans)), key=lambda i: spans[i].end - spans[i].start)
        span_nf = []
        for st in subterms:
            r = reduce(st, calc=R_NORMAL)
            span_nf.append(
                pretty(r.normal_form) if r.status is Status.NORMAL_FORM else None
            )
        names = term_names(t)
        perts = {
            rp: leaf_perturbations(text, repl=rp)
            for rp in REPLS
            if rp not in names
        }
        roles = {
            lp.orig: leaf_role(lp, root)
            for lps in perts.values()
            for lp in lps
        }
        out.append(
            TermSpec(
                id=pid,
                base_term=bt,
                term=term,
                correct_nf=pretty(rn.normal_form),
                naive_nf=pretty(rv.normal_form),
                spans=spans,
                span_nf=span_nf,
                root=root,
                perts=perts,
                roles=roles,
            )
        )
    return out


def battery_hash(battery: list[TermSpec]) -> str:
    blob = json.dumps(
        [[b.id, b.term, b.correct_nf, b.naive_nf] for b in battery], sort_keys=True
    )
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


# ── backends (real HF host / planted world; identical downstream path) ──────
@dataclass
class Prepared:
    offsets: list[tuple[int, int]]
    resid: np.ndarray  # (L, T, D)
    text: str = ""

    @property
    def n_tokens(self) -> int:
        return len(self.offsets)


class PlantedBackend:
    """Synthetic char-tokenized world planting a KNOWN cone (validate only).

    Planting is keyed by the perturbed prompt TEXT — per perturbation, never
    per term: a per-term union would make one leaf's out-of-cone cells another
    leaf's in-cone cells and wash out the very contrast under test (caught by
    this validation path, s335).
    """

    def __init__(self, n_layers: int = 8, d: int = 16):
        self.L, self.D = n_layers, d
        self.cone_by_text: dict[str, set[int]] = {}
        self.good_rank_pos: set[int] = set()

    def tokenize(self, text: str) -> list[tuple[int, int]]:
        return [(i, i + 1) for i in range(len(text))]

    def prepare(self, text: str, *, perturbed_char: int | None = None) -> Prepared:
        offs = self.tokenize(text)
        resid = (
            np.random.default_rng(1234)
            .standard_normal((self.L, len(offs), self.D))
            .astype(np.float32)
        )
        cone = self.cone_by_text.get(text)
        if perturbed_char is None or cone is None:
            return Prepared(offs, resid, text)
        jitter = 1.0 + 0.05 * (hash(text) % 7)  # replicate-level noise
        raw = np.random.default_rng(99).standard_normal((self.L, self.D))
        bump = raw * 3.0 * jitter
        resid = resid.copy()
        resid[:, perturbed_char, :] += bump.astype(np.float32)
        for c in cone:
            if c > perturbed_char:
                resid[:, c, :] += (bump * 0.6).astype(np.float32)
        return Prepared(offs, resid, text)

    def ranks(self, prep: Prepared, pos: int, token_strs: list[str]) -> np.ndarray:
        out = np.full((len(token_strs), self.L), 5000.0, dtype=np.float64)
        if pos in self.good_rank_pos:
            out[:, self.L // 2 :] = 3.0
        return out

    def read_mass(self, prep: Prepared, ans_pos: int) -> np.ndarray | None:
        return None


class HFBackend:
    """HF host (Qwen/LLaMA/Pythia): prefill grid + logit-lens + read-mass."""

    def __init__(self, model_id: str, device: str, dtype: str):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        from verbum import jlens

        self.torch, self.jlens = torch, jlens
        self.tok = AutoTokenizer.from_pretrained(model_id)
        self.model = (
            AutoModelForCausalLM.from_pretrained(
                model_id, dtype=getattr(torch, dtype), attn_implementation="eager"
            )
            .to(device)
            .eval()
        )
        self.device = device
        self.L = jlens.n_layers(self.model)

    def tokenize(self, text: str) -> list[tuple[int, int]]:
        enc = self.tok(text, return_offsets_mapping=True, add_special_tokens=True)
        return [tuple(o) for o in enc["offset_mapping"]]

    def prepare(self, text: str, *, perturbed_char: int | None = None) -> Prepared:
        offs = self.tokenize(text)
        resids, _ids = self.jlens.capture_residuals(self.model, self.tok, text)
        grid = np.stack([resids[i].numpy() for i in range(self.L)], axis=0)
        return Prepared(offs, grid.astype(np.float32), text)

    def ranks(self, prep: Prepared, pos: int, token_strs: list[str]) -> np.ndarray:
        torch = self.torch
        h = torch.from_numpy(prep.resid[:, pos, :])
        logits = self.jlens.logit_lens(self.model, h).float().cpu()  # (L, V)
        ids = [self.tok(s, add_special_tokens=False).input_ids[0] for s in token_strs]
        out = np.zeros((len(ids), logits.shape[0]), dtype=np.float64)
        for k, tid in enumerate(ids):
            out[k] = (logits > logits[:, tid : tid + 1]).sum(dim=-1).numpy() + 1.0
        return out

    def read_mass(self, prep: Prepared, ans_pos: int) -> np.ndarray | None:
        """Value-weighted attention from the answer column (s206: never bare QK)."""
        torch = self.torch
        inputs = self.tok(prep.text, return_tensors="pt").to(self.device)
        vnorms: dict[int, np.ndarray] = {}
        handles = []

        def mk(i: int):
            def hook(_m, _inp, out):
                v = out[0] if isinstance(out, tuple) else out
                vnorms[i] = v[0].float().norm(dim=-1).detach().cpu().numpy()

            return hook

        try:
            for i, layer in enumerate(self.model.model.layers):
                handles.append(layer.self_attn.v_proj.register_forward_hook(mk(i)))
            with torch.no_grad():
                out = self.model(**inputs, output_attentions=True)
            mass = np.zeros((self.L, prep.n_tokens), dtype=np.float64)
            for i, att in enumerate(out.attentions):
                w = att[0, :, ans_pos, :].float().cpu().numpy().mean(axis=0)
                vn = vnorms.get(i)
                if vn is not None and vn.shape[0] == w.shape[0]:
                    w = w * vn
                s = w.sum()
                mass[i] = w / s if s > 0 else w
            return mass
        except (AttributeError, RuntimeError) as exc:  # visible failure, never silent
            print(f"[pc] read_mass unavailable: {exc}", flush=True)
            return None
        finally:
            for h in handles:
                h.remove()


# ── analysis primitives ─────────────────────────────────────────────────────
def delta_grid(orig: Prepared, pert: Prepared) -> np.ndarray | None:
    """Normalized per-cell residual distance ``(L, T)``; ``None`` if the two
    tokenizations do not align (a hard skip, never a silent fudge)."""
    if orig.offsets != pert.offsets:
        return None
    num = np.linalg.norm(orig.resid - pert.resid, axis=-1)
    den = np.linalg.norm(orig.resid, axis=-1) + 1e-6
    return num / den


def cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    if a.size == 0 or b.size == 0:
        return 0.0
    gt = (a[:, None] > b[None, :]).sum()
    lt = (a[:, None] < b[None, :]).sum()
    return float((gt - lt) / (a.size * b.size))


def perm_p_paired(diffs: np.ndarray, rng, n_perm: int = N_PERM) -> float:
    """Two-sided sign-flip permutation p on paired differences."""
    if diffs.size == 0:
        return 1.0
    obs = abs(float(diffs.mean()))
    signs = rng.choice([-1.0, 1.0], size=(n_perm, diffs.size))
    null = np.abs((signs * diffs[None, :]).mean(axis=1))
    return float((np.sum(null >= obs) + 1) / (n_perm + 1))


def base_token(prep: Prepared, base: int) -> int:
    for i, (_s, e) in enumerate(prep.offsets):
        if e > base:
            return i
    return 0


def score_term(backend, spec: TermSpec, *, do_m1: bool, do_mass: bool) -> dict:
    """All measurables for one term → one results.jsonl record."""
    prompt, base = build_prompt(spec.term)
    orig = backend.prepare(prompt)
    cells = [span_token_range(s.start, s.end, orig.offsets, base) for s in spec.spans]
    ans_pos = orig.n_tokens - 1
    rec: dict[str, Any] = {
        "term_id": spec.id,
        "term": spec.term,
        "correct_nf": spec.correct_nf,
        "naive_nf": spec.naive_nf,
        "roles": spec.roles,
        "n_tokens": orig.n_tokens,
        "n_layers": int(orig.resid.shape[0]),
        "leaves": [],
        "m1": [],
        "pc0": {},
        "error": None,
    }
    if any(c is None for c in cells):
        rec["error"] = "span_token_mapping_failed"
        return rec
    readout = cells[spec.root][1]
    rec["readout_tok"] = readout

    causal_max, leaf_min = 0.0, float("inf")
    for repl, lps in spec.perts.items():
        for lp in lps:
            rng_ = span_token_range(lp.start, lp.end, orig.offsets, base)
            if rng_ is None:
                continue
            leaf_tok = rng_[1]
            pert_prompt, _ = build_prompt(lp.pert_text)
            pert = backend.prepare(pert_prompt, perturbed_char=base + lp.start)
            d = delta_grid(orig, pert)
            if d is None:
                rec["leaves"].append(
                    {"repl": repl, "leaf": lp.orig, "error": "token_misalignment"}
                )
                continue
            cell = d.mean(axis=0)  # mean over layers → (T,)
            causal_max = max(causal_max, float(cell[:leaf_tok].max(initial=0.0)))
            leaf_min = min(leaf_min, float(cell[leaf_tok]))
            rec["leaves"].append(
                {
                    "repl": repl,
                    "leaf": lp.orig,
                    "role": leaf_role(lp, spec.root),
                    "leaf_tok": leaf_tok,
                    "delta_readout": float(cell[readout]),
                    "delta_answer": float(cell[ans_pos]),
                    "delta_profile_layers": [
                        float(x) for x in d[:, readout]
                    ],  # depth advisory
                    "error": None,
                }
            )
    rec["pc0"] = {
        "causal_max_upstream_delta": causal_max,
        "leaf_min_delta": None if leaf_min == float("inf") else leaf_min,
    }

    if do_m1:
        rng = np.random.default_rng(abs(hash(spec.id)) % (2**32))
        by_pos: dict[int, list[tuple[int, str]]] = {}
        for i, s in enumerate(spec.spans):
            if spec.span_nf[i] is None or s.kind == "comb":
                continue
            by_pos.setdefault(cells[i][1], []).append((i, " " + spec.span_nf[i]))
        pool = [p for p in range(base_token(orig, base), ans_pos)]
        for pos, items in by_pos.items():
            toks = [t for _, t in items]
            actual = backend.ranks(orig, pos, toks)
            alt = [p for p in pool if p != pos] or [pos]
            npos = int(rng.choice(alt))
            null = backend.ranks(orig, npos, toks)
            for k, (i, _t) in enumerate(items):
                rec["m1"].append(
                    {
                        "span": i,
                        "tok": pos,
                        "nf": spec.span_nf[i],
                        "best_rank": float(actual[k].min()),
                        "best_layer": int(actual[k].argmin()),
                        "null_pos": npos,
                        "null_best_rank": float(null[k].min()),
                    }
                )

    c_tok, n_tok = " " + spec.correct_nf, " " + spec.naive_nf
    if c_tok != n_tok:
        r = backend.ranks(orig, ans_pos, [c_tok, n_tok])
        rec["m4_necessity"] = {
            "correct_final_rank": float(r[0][-1]),
            "naive_final_rank": float(r[1][-1]),
            "favors_correct_final": bool(r[0][-1] < r[1][-1]),
        }
    if do_mass:
        mass = backend.read_mass(orig, ans_pos)
        if mass is not None:
            interior = list(range(base_token(orig, base), ans_pos))
            rec["m4_read_mass"] = {
                "interior_mass_final_layer": float(mass[-1, interior].sum()),
                "profile": [float(x) for x in mass[:, interior].sum(axis=1)],
            }
    return rec


# ── gates ───────────────────────────────────────────────────────────────────
def _role_means(rec: dict, key: str = "delta_readout") -> dict[str, float]:
    acc: dict[str, list[float]] = {}
    for lv in rec.get("leaves", []):
        if lv.get("error"):
            continue
        acc.setdefault(lv["role"], []).append(lv[key])
    return {k: float(np.mean(v)) for k, v in acc.items()}


def compute_gates(recs: list[dict], rng) -> dict:
    good = [r for r in recs if r.get("error") is None]

    causal = max((r["pc0"].get("causal_max_upstream_delta", 1.0) for r in good),
                 default=1.0)
    leafd = [r["pc0"]["leaf_min_delta"] for r in good
             if r["pc0"].get("leaf_min_delta") is not None]
    pc0 = {
        "n_terms": len(good),
        "n_errors": len(recs) - len(good),
        "causal_max_upstream_delta": float(causal),
        "causal_ok": bool(causal < 1e-3),
        "leaf_delta_min": float(min(leafd)) if leafd else 0.0,
        "leaf_moves_ok": bool(leafd and min(leafd) > 1e-2),
    }
    pc0["pass"] = bool(pc0["causal_ok"] and pc0["leaf_moves_ok"] and good)

    gains = np.array(
        [m["null_best_rank"] - m["best_rank"] for r in good for m in r["m1"]]
    )
    p1 = perm_p_paired(gains, rng) if gains.size else 1.0
    pc1 = {
        "n_cells": int(gains.size),
        "median_rank_gain": float(np.median(gains)) if gains.size else 0.0,
        "p": p1,
        "pass": bool(
            gains.size and float(np.median(gains)) >= PC1_MIN_RANK_GAIN and p1 < ALPHA
        ),
    }
    pc1["qualifier"] = "INTERIOR-VISIBLE" if pc1["pass"] else "LAST-COLUMN-ONLY"

    # PC2 — selectivity: does a BOTH-dependent leaf move the readout cell more
    # than the discarded control? (positive control + localization in one)
    both_v, none_v, diffs = [], [], []
    for r in good:
        m = _role_means(r)
        if "both" in m and "none" in m:
            both_v.append(m["both"])
            none_v.append(m["none"])
            diffs.append(m["both"] - m["none"])
    a, b, dd = np.array(both_v), np.array(none_v), np.array(diffs)
    cd = cliffs_delta(a, b)
    p2 = perm_p_paired(dd, rng) if dd.size else 1.0
    pc2 = {
        "n_terms": int(dd.size),
        "mean_both": float(a.mean()) if a.size else 0.0,
        "mean_none": float(b.mean()) if b.size else 0.0,
        "mean_diff": float(dd.mean()) if dd.size else 0.0,
        "cliffs_delta": cd,
        "p": p2,
        "pass": bool(dd.size and cd >= PC2_MIN_CLIFF and p2 < ALPHA),
    }

    # PC3 — D_naive at the readout cell + arrival fraction
    dn, arr = [], []
    for r in good:
        m = _role_means(r)
        if "naive_only" in m and "none" in m:
            dn.append(m["naive_only"] - m["none"])
            if "both" in m and (m["both"] - m["none"]) > 1e-9:
                arr.append((m["naive_only"] - m["none"]) / (m["both"] - m["none"]))
    d3 = np.array(dn)
    p3 = perm_p_paired(d3, rng) if d3.size else 1.0
    pc3 = {
        "n_terms": int(d3.size),
        "D_naive": float(d3.mean()) if d3.size else 0.0,
        "median_D": float(np.median(d3)) if d3.size else 0.0,
        "n_positive": int((d3 > 0).sum()),
        "median_arrival_fraction": float(np.median(arr)) if arr else None,
        "p": p3,
        "sig": bool(d3.size and p3 < ALPHA),
        "sign": int(np.sign(d3.mean())) if d3.size else 0,
    }

    nec = [r["m4_necessity"] for r in good if "m4_necessity" in r]
    pc4 = {
        "n": len(nec),
        "frac_favors_correct_final": (
            float(np.mean([x["favors_correct_final"] for x in nec])) if nec else None
        ),
        "median_correct_final_rank": (
            float(np.median([x["correct_final_rank"] for x in nec])) if nec else None
        ),
        "median_naive_final_rank": (
            float(np.median([x["naive_final_rank"] for x in nec])) if nec else None
        ),
    }
    return {
        "PC0": pc0, "PC1": pc1, "PC2": pc2, "PC3": pc3, "PC4": pc4,
        "verdict": decide(pc0, pc2, pc3),
    }


def decide(pc0: dict, pc2: dict, pc3: dict) -> str:
    """The frozen verdict tree (s335, estimator per Amendment 2)."""
    if not pc0["pass"]:
        return "VOID"
    if not pc2["pass"]:
        return "DIFFUSE/NO-CONE"
    if pc3["sig"] and pc3["sign"] > 0:
        return "CONE-NAIVE"
    if pc3["sig"] and pc3["sign"] < 0:
        return "CONE-CORRECT"
    if pc3["n_terms"]:
        return "CONE-CORRECT"  # selectivity works; the discarded arg never arrives
    return "CONE-UNDIFFERENTIATED"


# ── planted-world validation ────────────────────────────────────────────────
def validate() -> bool:
    ok = True
    print("[validate] subst_pairs battery ...")
    ok &= bool(subst_validate())

    battery = build_battery()
    print(f"[validate] battery: {len(battery)} terms (hash {battery_hash(battery)})")
    n_disc = sum(1 for s in battery if "naive_only" in s.roles.values())
    n_ctrl = sum(1 for s in battery if "none" in s.roles.values())
    print(
        f"[validate] naive_only-leaf terms: {n_disc}; none-control terms: {n_ctrl}"
    )
    ok &= n_disc == 9 and n_ctrl == len(battery)

    for spec in battery:  # control must sit upstream of the readout cell
        for lps in spec.perts.values():
            for lp in lps:
                if leaf_role(lp, spec.root) == "none":
                    assert lp.end <= spec.spans[spec.root].end - 1, spec.id
    print("[validate] every none-control leaf is upstream of the readout cell ✓")

    for world, want in (("naive", "CONE-NAIVE"), ("correct", "CONE-CORRECT")):
        be = PlantedBackend()
        recs = []
        for spec in battery:
            _p, base = build_prompt(spec.term)
            be.good_rank_pos = {
                base + s.end - 1 for s in spec.spans if s.kind != "comb"
            }
            for lps in spec.perts.values():
                for lp in lps:
                    ids = lp.cone_naive if world == "naive" else lp.cone_normal
                    pp, _ = build_prompt(lp.pert_text)
                    be.cone_by_text[pp] = {base + spec.spans[i].end - 1 for i in ids}
            recs.append(score_term(be, spec, do_m1=True, do_mass=False))
        g = compute_gates(recs, np.random.default_rng(0))
        print(
            f"[validate] world={world!r}: verdict={g['verdict']} | "
            f"PC0 {g['PC0']['pass']} | PC1 {g['PC1']['qualifier']} | "
            f"PC2 δ={g['PC2']['cliffs_delta']:.2f} p={g['PC2']['p']:.4f} | "
            f"PC3 D={g['PC3']['D_naive']:.3f} p={g['PC3']['p']:.4f} "
            f"n={g['PC3']['n_terms']} arrival={g['PC3']['median_arrival_fraction']}"
        )
        ok &= g["verdict"] == want
    print(f"[validate] {'ALL PASS' if ok else 'FAIL'}")
    return bool(ok)


# ── provenance ──────────────────────────────────────────────────────────────
def git_sha() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[2]
            )
            .decode()
            .strip()
        )
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def write_meta(out: Path, args, battery: list[TermSpec], gates: dict) -> None:
    import platform

    meta = {
        "run_id": out.name,
        "probe": "P-PREFILL-CONE",
        "frozen": "s335 (freeze) + Amendment 1 + Amendment 2 (both pre-data)",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "model_id": args.model_id,
        "device": args.device,
        "dtype": args.dtype,
        "seed": args.seed,
        "smoke": bool(args.smoke),
        "n_terms": len(battery),
        "battery_hash": battery_hash(battery),
        "probe_shape": "(λd.λr.r) c (BASE e f)",
        "repls": list(REPLS),
        "git_sha": git_sha(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "gates": gates,
    }
    try:
        import torch
        import transformers

        meta["lib_versions"] = {
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "numpy": np.__version__,
        }
    except ImportError:
        meta["lib_versions"] = {"numpy": np.__version__}
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=str))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--no-m1", action="store_true")
    ap.add_argument("--mass-terms", type=int, default=3)
    args = ap.parse_args()

    if args.validate:
        return 0 if validate() else 1

    battery = build_battery()
    if args.smoke:
        battery = battery[:3]
    print(
        f"[pc] battery={len(battery)} hash={battery_hash(battery)} "
        f"model={args.model_id} dtype={args.dtype}",
        flush=True,
    )
    backend = HFBackend(args.model_id, args.device, args.dtype)
    recs = []
    for i, spec in enumerate(battery):
        rec = score_term(
            backend, spec, do_m1=not args.no_m1, do_mass=i < args.mass_terms
        )
        recs.append(rec)
        print(f"[pc] {i + 1}/{len(battery)} {spec.id} err={rec['error']}", flush=True)

    gates = compute_gates(recs, np.random.default_rng(args.seed + 99))
    print(json.dumps(gates, indent=2, default=str))
    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        with (out / "results.jsonl").open("w") as fh:
            for r in recs:
                fh.write(json.dumps(r, default=str) + "\n")
        (out / "gates.json").write_text(json.dumps(gates, indent=2, default=str))
        (out / "battery.json").write_text(
            json.dumps(
                [
                    {
                        "id": s.id, "term": s.term, "correct_nf": s.correct_nf,
                        "naive_nf": s.naive_nf, "roles": s.roles,
                    }
                    for s in battery
                ],
                indent=2,
            )
        )
        write_meta(out, args, battery, gates)
        print(f"[pc] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
