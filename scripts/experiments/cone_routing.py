#!/usr/bin/env python3
"""P-CONE-ROUTING - within-prompt read-mass routing probe (frozen s335, pre-data).

Successor to P-PREFILL-CONE (VOID: magnitude/transport read aimed at a
value/routing claim). This probe is register-matched: ROUTING. At the cell that
emits the answer, does the machine READ FROM the argument the naive algorithm
selects (`e`) or the one capture-avoiding substitution selects (the captured
variable, `y` in the exemplar)?

Within-prompt: both candidate answers sit in the SAME prompt, same forward
pass - the s335 surface-repetition confound never forms. One forward per
variant, no perturbation loop (54 forwards).

Substrate: the s335 matched triples (`build_variants` via `build_battery`,
18 triples / 54 variants, 9 kernel-certified clean flips), identical layout
one character apart, so `e` sits at the same token in A/B/P by construction.

  A  capture live    - correct NF discards `e`, naive NF is built from it
  B  binders renamed - capture-free, NF head = cap var  => ground truth: not-e
  P  head var swapped- capture-free, NF head = `e`      => ground truth: e

Readout: value-weighted attention (s206 scar: never bare QK) from the answer
column (primary cell) and the term-final interior cell (secondary, advisory)
onto candidate source positions. GQA-aware per-kv-head v-norm expansion,
head-mean, per-layer normalized. Primary scalar = LAYER-MEAN mass (pre-data
instantiation; per-layer stored for the RC4 depth advisory).

Frozen statistics (knowledge page section P-CONE-ROUTING):

  primary   rho_e   = (mass_A(e) - mass_B(e)) / (mass_P(e) - mass_B(e))
  secondary rho_Sel = same shape on Sel = mass(cap) - mass(e), within-prompt.
            Named bound: A carries the cap token TWICE (binder + argument);
            mass is read at the ARGUMENT position, binder mass is diagnostic.

Gate tree (frozen): RC0 sanity -> RC1 CALIBRATION make-or-break read FIRST
(mass_P(e) > mass_B(e) paired p<0.05 AND Cliff's delta >= 0.2, corroborated by
Sel_B > Sel_P) -> RC2 primary (bootstrap CI on median rho_e must exclude 0.5)
-> RC3 secondary sign agreement -> RC4 depth advisory. Nulls: placebo `f`
(must not discriminate), shuffled-variant-label (== the sign-flip permutation),
distance control (B/P are geometry-identical with opposite answers - the pole
contrast IS the distance control).

Verdicts: VOID / NO-CALIBRATION / NAIVE-ROUTING / CORRECT-ROUTING /
UNDIFFERENTIATED. The 3 advisory read-mass records from
results/p_prefill_cone_s335/run_14b (cap_000) are DISCLOSED and excluded -
this is a fresh run directory; nothing is read from that run.

Standing bound: attention mass is correlational (s206) - a positive licenses
"reads from", not "uses".

`--validate` drives planted NAIVE / CORRECT / NO-CALIBRATION / PLACEBO worlds
through the REAL scoring and gate path (s331: planted plumbing must be probe
plumbing). No model is loaded.

License: MIT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from prefill_cone import (
    TermSpec,
    _shadow_binders,
    battery_hash,
    build_battery,
    build_prompt,
    git_sha,
)

from verbum.cone import span_token_range
from verbum.lambda_ast import parse

# frozen constants
N_PERM = 10_000
N_BOOT = 10_000
ALPHA = 0.05
RC1_MIN_CLIFF = 0.2
# pre-data instantiations (declared in meta.json):
PLACEBO_ABS_FLOOR = 0.005  # abs mass floor so a dead calibration can't fake VOID
PLACEBO_REL = 0.5  # placebo fires only if it carries >= 50% of the pole contrast
DET_TOL = 1e-4  # deterministic-repeat max abs mass difference
MIN_ALIGNED_CLEAN = 6  # RC0: minimum aligned clean triples
ROWSUM_TOL = 2e-2  # attention row must sum to ~1 (bf16 tolerance)
CELLS = ("answer", "term_final")


# -- position extraction (shared by real and planted paths) ------------------
@dataclass(frozen=True, slots=True)
class TripleCtx:
    """Per-triple constants derived from the kernel-certified battery."""

    pair_id: str
    cap_var: str
    diff_chars: tuple[int, ...]  # char idxs where A and B render differently


def triple_ctx(a_spec: TermSpec, b_spec: TermSpec) -> TripleCtx:
    shadows = _shadow_binders(parse(a_spec.term))
    diffs = tuple(
        i for i, (ca, cb) in enumerate(zip(a_spec.term, b_spec.term, strict=True))
        if ca != cb and ca == shadows[0]
    )
    return TripleCtx(a_spec.pair_id, shadows[0], diffs)


def free_atom_spans(spec: TermSpec, name: str) -> list[tuple[int, int]]:
    return [
        (s.start, s.end)
        for s in spec.spans
        if s.kind == "atom" and s.free_leaf and spec.term[s.start : s.end] == name
    ]


def source_toks(
    spec: TermSpec, ctx: TripleCtx, offsets: list[tuple[int, int]], base: int
) -> dict[str, Any] | None:
    """Token indices of every read target; None on any extraction failure."""

    def one(spans: list[tuple[int, int]]) -> int | None:
        if len(spans) != 1:
            return None
        rng = span_token_range(spans[0][0], spans[0][1], offsets, base)
        return None if rng is None else rng[1]

    e_tok = one(free_atom_spans(spec, "e"))
    f_tok = one(free_atom_spans(spec, "f"))
    if e_tok is None or f_tok is None:
        return None
    cap_spans = free_atom_spans(spec, ctx.cap_var)
    cap_tok = one(cap_spans)  # None when 0 or >1 free occurrences (Sel skipped)
    binder_toks: list[int] = []
    for c in ctx.diff_chars:
        rng = span_token_range(c, c + 1, offsets, base)
        if rng is not None and rng[1] not in binder_toks:
            binder_toks.append(rng[1])
    root = spec.spans[spec.root]
    term_rng = span_token_range(root.start, root.end, offsets, base)
    if term_rng is None:
        return None
    return {
        "e": e_tok,
        "cap": cap_tok,
        "f": f_tok,
        "binder": binder_toks,
        "term_final": term_rng[1],
        "cap_free_count": len(cap_spans),
    }


# -- backends ----------------------------------------------------------------
class HFBackend:
    """HF host: one forward per variant; value-weighted GQA-aware read-mass."""

    def __init__(self, model_id: str, device: str, dtype: str):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(model_id)
        self.model = (
            AutoModelForCausalLM.from_pretrained(
                model_id, dtype=getattr(torch, dtype), attn_implementation="eager"
            )
            .to(device)
            .eval()
        )
        self.device = device
        cfg = self.model.config
        self.n_heads = int(cfg.num_attention_heads)
        self.n_kv = int(getattr(cfg, "num_key_value_heads", self.n_heads))
        self.gqa_ok = self.n_heads % self.n_kv == 0
        self.L = len(self.model.model.layers)

    def tokenize(self, text: str) -> list[tuple[int, int]]:
        enc = self.tok(text, return_offsets_mapping=True, add_special_tokens=True)
        return [tuple(o) for o in enc["offset_mapping"]]

    def mass(
        self, text: str, cells: list[int]
    ) -> tuple[np.ndarray, float]:
        """Read-mass (n_cells, L, T) + max |rowsum - 1| before value weighting."""
        torch = self.torch
        inputs = self.tok(text, return_tensors="pt").to(self.device)
        vns: dict[int, np.ndarray] = {}
        handles = []

        def mk(i: int):
            def hook(_m, _inp, out):
                v = out[0] if isinstance(out, tuple) else out
                hd = v.shape[-1] // self.n_kv
                vns[i] = (
                    v[0].float().view(-1, self.n_kv, hd).norm(dim=-1).cpu().numpy()
                )  # (T, n_kv)

            return hook

        try:
            for i, layer in enumerate(self.model.model.layers):
                handles.append(layer.self_attn.v_proj.register_forward_hook(mk(i)))
            with torch.no_grad():
                out = self.model(**inputs, output_attentions=True)
        finally:
            for h in handles:
                h.remove()
        T = int(inputs["input_ids"].shape[1])
        group = self.n_heads // self.n_kv
        m = np.zeros((len(cells), self.L, T), dtype=np.float64)
        dev = 0.0
        for i, att in enumerate(out.attentions):
            w_all = att[0].float().cpu().numpy()  # (H, T, T)
            w = w_all[:, cells, :]  # (H, C, T)
            dev = max(dev, float(np.abs(w.sum(axis=-1) - 1.0).max()))
            vn = vns[i]  # (T, n_kv)
            vn_exp = np.repeat(vn.T, group, axis=0)  # (H, T), kv-head blocks
            weighted = (w * vn_exp[:, None, :]).mean(axis=0)  # (C, T)
            s = weighted.sum(axis=-1, keepdims=True)
            m[:, i, :] = np.where(s > 0, weighted / s, weighted)
        return m, dev


class PlantedBackend:
    """Char-tokenized world with planted read-mass (validate only).

    Bumps are keyed by prompt TEXT -> {token: weight}; the scoring path
    extracts positions and reads mass through the identical code (s331).
    Deterministic per text (sha256 seed) so the repeat check is exercised.
    """

    L = 8
    gqa_ok = True
    n_heads = 4
    n_kv = 2

    def __init__(self) -> None:
        self.bump_by_text: dict[str, dict[int, float]] = {}

    def tokenize(self, text: str) -> list[tuple[int, int]]:
        return [(i, i + 1) for i in range(len(text))]

    def mass(self, text: str, cells: list[int]) -> tuple[np.ndarray, float]:
        T = len(text)
        seed = int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        base = 1.0 + 0.05 * rng.standard_normal((self.L, T))
        base = np.clip(base, 0.01, None)
        for tok, wgt in self.bump_by_text.get(text, {}).items():
            base[2:, tok] += wgt  # layers >= 2 only (exercises RC4 storage)
        m = np.zeros((len(cells), self.L, T), dtype=np.float64)
        for c, cell in enumerate(cells):
            w = base.copy()
            w[:, cell + 1 :] = 0.0  # causal
            m[c] = w / w.sum(axis=-1, keepdims=True)
        return m, 0.0


# -- scoring (identical path for real and planted) ---------------------------
def score_variant(backend, spec: TermSpec, ctx: TripleCtx) -> tuple[dict, dict]:
    """One forward -> one results.jsonl record (+ full mass grids for npz)."""
    prompt, base = build_prompt(spec.term)
    offsets = backend.tokenize(prompt)
    rec: dict[str, Any] = {
        "term_id": spec.id,
        "pair_id": spec.pair_id,
        "variant": spec.variant,
        "clean_flip": bool(spec.clean_flip),
        "term": spec.term,
        "correct_nf": spec.correct_nf,
        "naive_nf": spec.naive_nf,
        "cap_var": ctx.cap_var,
        "offsets_sig": hashlib.sha256(json.dumps(offsets).encode()).hexdigest()[:12],
        "n_tokens": len(offsets),
        "error": None,
    }
    toks = source_toks(spec, ctx, offsets, base)
    if toks is None:
        rec["error"] = "position_extraction_failed"
        return rec, {}
    ans = len(offsets) - 1
    cells = {"answer": ans, "term_final": toks["term_final"]}
    rec["toks"] = {**toks, "answer": ans}
    m, dev = backend.mass(prompt, [cells[c] for c in CELLS])
    rec["rowsum_dev"] = float(dev)
    rec["n_layers"] = int(m.shape[1])
    grids = {}
    for ci, cname in enumerate(CELLS):
        grid = m[ci]  # (L, T)
        grids[f"{spec.id}:{cname}"] = grid.astype(np.float32)
        cell_rec: dict[str, Any] = {
            "mass_e": float(grid[:, toks["e"]].mean()),
            "mass_f": float(grid[:, toks["f"]].mean()),
            "mass_binder": float(
                sum(grid[:, t].mean() for t in toks["binder"])
            ),
            "layers_e": [float(x) for x in grid[:, toks["e"]]],
            "layers_f": [float(x) for x in grid[:, toks["f"]]],
        }
        if toks["cap"] is not None:
            cell_rec["mass_cap"] = float(grid[:, toks["cap"]].mean())
            cell_rec["sel"] = cell_rec["mass_cap"] - cell_rec["mass_e"]
            cell_rec["layers_cap"] = [float(x) for x in grid[:, toks["cap"]]]
        else:
            cell_rec["mass_cap"] = None
            cell_rec["sel"] = None
        rec[cname] = cell_rec
    return rec, grids


# -- statistics --------------------------------------------------------------
def perm_p(diffs: np.ndarray, rng, one_sided: bool) -> float:
    """Sign-flip permutation p == the shuffled-variant-label null (paired)."""
    if diffs.size == 0:
        return 1.0
    obs = float(diffs.mean())
    signs = rng.choice([-1.0, 1.0], size=(N_PERM, diffs.size))
    null = (signs * diffs[None, :]).mean(axis=1)
    if one_sided:
        return float((np.sum(null >= obs) + 1) / (N_PERM + 1))
    return float((np.sum(np.abs(null) >= abs(obs)) + 1) / (N_PERM + 1))


def cliffs_delta(a: np.ndarray) -> float:
    """Cliff's delta of paired diffs vs zero."""
    if a.size == 0:
        return 0.0
    return float(((a > 0).sum() - (a < 0).sum()) / a.size)


def boot_ci_median(vals: np.ndarray, rng) -> tuple[float, float]:
    if vals.size == 0:
        return (float("nan"), float("nan"))
    idx = rng.integers(0, vals.size, size=(N_BOOT, vals.size))
    meds = np.median(vals[idx], axis=1)
    return (float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5)))


def group_triples(recs: list[dict]) -> tuple[list[dict[str, dict]], int]:
    by: dict[str, dict[str, dict]] = {}
    for r in recs:
        if r.get("error") is None:
            by.setdefault(r["pair_id"], {})[r["variant"]] = r
    out, mis = [], 0
    for pid in sorted(by):
        vs = by[pid]
        if set(vs) != {"A", "B", "P"}:
            mis += 1
            continue
        if len({vs[t]["offsets_sig"] for t in "ABP"}) != 1:
            mis += 1
            continue
        if len({vs[t]["toks"]["e"] for t in "ABP"}) != 1:
            mis += 1
            continue
        out.append(vs)
    return out, mis


def cell_stats(
    triples: list[dict[str, dict]], cell: str, rng
) -> dict[str, Any]:
    """RC1/RC2/RC3(/RC4 for answer) on one readout cell."""
    clean = [t for t in triples if t["A"]["clean_flip"]]

    def arr(tag: str, key: str, pool: list) -> np.ndarray:
        return np.array([t[tag][cell][key] for t in pool], dtype=np.float64)

    # RC1 calibration (make-or-break, read FIRST)
    d_pole = arr("P", "mass_e", clean) - arr("B", "mass_e", clean)
    p1 = perm_p(d_pole, rng, one_sided=True)
    cd = cliffs_delta(d_pole)
    sel_pairs = [
        (t["B"][cell]["sel"], t["P"][cell]["sel"])
        for t in clean
        if t["B"][cell]["sel"] is not None and t["P"][cell]["sel"] is not None
    ]
    sel_corr = (
        float(np.mean([b - p for b, p in sel_pairs])) if sel_pairs else None
    )
    corr_ok = sel_corr is None or sel_corr > 0
    rc1 = {
        "n_triples": int(d_pole.size),
        "mean_pole_sep": float(d_pole.mean()) if d_pole.size else 0.0,
        "median_pole_sep": float(np.median(d_pole)) if d_pole.size else 0.0,
        "cliffs_delta": cd,
        "p_one_sided": p1,
        "sel_corroboration_mean_B_minus_P": sel_corr,
        "sel_corroboration_ok": bool(corr_ok),
        "pass": bool(
            d_pole.size
            and d_pole.mean() > 0
            and cd >= RC1_MIN_CLIFF
            and p1 < ALPHA
            and corr_ok
        ),
    }

    # placebo `f` (all aligned triples; must NOT discriminate)
    fA = arr("A", "mass_f", triples) - arr("B", "mass_f", triples)
    fP = arr("P", "mass_f", triples) - arr("B", "mass_f", triples)
    thresh = max(PLACEBO_REL * abs(rc1["mean_pole_sep"]), PLACEBO_ABS_FLOOR)
    placebo = {}
    fired = False
    for name, d in (("A_minus_B", fA), ("P_minus_B", fP)):
        p = perm_p(d, rng, one_sided=False)
        mean = float(d.mean()) if d.size else 0.0
        hit = bool(d.size and p < ALPHA and abs(mean) >= thresh)
        placebo[name] = {"mean": mean, "p": p, "fired": hit}
        fired = fired or hit
    placebo["threshold"] = float(thresh)
    placebo["fired"] = bool(fired)

    # RC2 primary rho_e (clean triples; per-triple pole denominator must be > 0)
    rhos, excluded = [], 0
    for t in clean:
        b, p_, a = (t[tag][cell]["mass_e"] for tag in ("B", "P", "A"))
        den = p_ - b
        if den <= 0:
            excluded += 1
            continue
        rhos.append((a - b) / den)
    rho_e = np.array(rhos, dtype=np.float64)
    lo, hi = boot_ci_median(rho_e, rng)
    med_e = float(np.median(rho_e)) if rho_e.size else float("nan")
    rc2 = {
        "n_used": int(rho_e.size),
        "n_excluded_bad_denominator": int(excluded),
        "rho_e_values": [float(x) for x in rho_e],
        "median_rho_e": med_e,
        "ci95_low": lo,
        "ci95_high": hi,
        "ci_excludes_half": bool(rho_e.size and (lo > 0.5 or hi < 0.5)),
    }

    # RC3 secondary rho_Sel (denominator Sel_P - Sel_B must be < 0: mass moves
    # from cap toward e between the poles)
    rhos_s, excluded_s = [], 0
    for t in clean:
        sb, sp, sa = (t[tag][cell]["sel"] for tag in ("B", "P", "A"))
        if sb is None or sp is None or sa is None:
            excluded_s += 1
            continue
        den = sp - sb
        if den >= 0:
            excluded_s += 1
            continue
        rhos_s.append((sa - sb) / den)
    rho_s = np.array(rhos_s, dtype=np.float64)
    med_s = float(np.median(rho_s)) if rho_s.size else float("nan")
    agrees = bool(
        rho_e.size and rho_s.size and (med_e - 0.5) * (med_s - 0.5) > 0
    )
    rc3 = {
        "n_used": int(rho_s.size),
        "n_excluded": int(excluded_s),
        "median_rho_sel": med_s,
        "agrees_with_rho_e": agrees,
    }

    # RC4 depth advisory (per-layer median rho_e)
    rc4: dict[str, Any] = {}
    if clean:
        n_layers = len(clean[0]["A"][cell]["layers_e"])
        per_layer = []
        for layer in range(n_layers):
            vals = []
            for t in clean:
                b, p_, a = (
                    t[tag][cell]["layers_e"][layer] for tag in ("B", "P", "A")
                )
                if p_ - b > 0:
                    vals.append((a - b) / (p_ - b))
            per_layer.append(
                float(np.median(vals)) if vals else float("nan")
            )
        seps = [
            float(
                np.median(
                    [
                        t["P"][cell]["layers_e"][layer]
                        - t["B"][cell]["layers_e"][layer]
                        for t in clean
                    ]
                )
            )
            for layer in range(n_layers)
        ]
        rc4 = {
            "per_layer_median_rho_e": per_layer,
            "per_layer_median_pole_sep": seps,
            "best_sep_layer": int(np.argmax(seps)),
        }

    # diagnostics: binder mass (the named A-two-tokens bound) + raw masses
    diag = {
        "median_mass_binder_A": (
            float(np.median(arr("A", "mass_binder", triples)))
            if triples
            else None
        ),
        "median_mass_e": {
            tag: float(np.median(arr(tag, "mass_e", clean))) if clean else None
            for tag in ("A", "B", "P")
        },
        "median_mass_cap": {
            tag: (
                float(
                    np.median(
                        [
                            t[tag][cell]["mass_cap"]
                            for t in clean
                            if t[tag][cell]["mass_cap"] is not None
                        ]
                    )
                )
                if clean
                else None
            )
            for tag in ("A", "B", "P")
        },
    }
    return {
        "RC1": rc1,
        "placebo": placebo,
        "RC2": rc2,
        "RC3": rc3,
        "RC4": rc4,
        "diagnostics": diag,
    }


def decide(rc0: dict, cell: dict) -> str:
    """The frozen verdict tree."""
    if not rc0["pass"]:
        return "VOID"
    if not cell["RC1"]["pass"]:
        return "NO-CALIBRATION"
    if not cell["RC2"]["ci_excludes_half"]:
        return "UNDIFFERENTIATED"
    if not cell["RC3"]["agrees_with_rho_e"]:
        return "UNDIFFERENTIATED"
    return (
        "NAIVE-ROUTING"
        if cell["RC2"]["median_rho_e"] > 0.5
        else "CORRECT-ROUTING"
    )


def compute_gates(
    recs: list[dict], rng, *, det_dev: float | None, gqa_ok: bool
) -> dict:
    triples, mis = group_triples(recs)
    clean_n = sum(1 for t in triples if t["A"]["clean_flip"])
    n_err = sum(1 for r in recs if r.get("error"))
    rowsum = max((r.get("rowsum_dev", 0.0) for r in recs), default=0.0)
    answer = cell_stats(triples, "answer", rng)
    term_final = cell_stats(triples, "term_final", rng)
    rc0 = {
        "n_records": len(recs),
        "n_errors": int(n_err),
        "n_triples_aligned": len(triples),
        "n_triples_misaligned": int(mis),
        "n_clean_aligned": int(clean_n),
        "max_rowsum_dev": float(rowsum),
        "rowsum_ok": bool(rowsum < ROWSUM_TOL),
        "det_repeat_dev": det_dev,
        "det_ok": bool(det_dev is None or det_dev < DET_TOL),
        "gqa_ok": bool(gqa_ok),
        "placebo_fired": bool(answer["placebo"]["fired"]),
        "s335_advisory_records": "excluded (fresh run; nothing read)",
    }
    rc0["pass"] = bool(
        n_err == 0
        and clean_n >= MIN_ALIGNED_CLEAN
        and rc0["rowsum_ok"]
        and rc0["det_ok"]
        and rc0["gqa_ok"]
        and not rc0["placebo_fired"]
    )
    verdict = decide(rc0, answer)
    return {
        "RC0": rc0,
        "answer": answer,
        "term_final_advisory": term_final,
        "verdict": verdict,
        "verdict_cell": "answer",
    }


# -- battery helpers ---------------------------------------------------------
def battery_triples(
    smoke: bool = False,
) -> list[tuple[TripleCtx, dict[str, TermSpec]]]:
    battery = build_battery()
    by: dict[str, dict[str, TermSpec]] = {}
    order: list[str] = []
    for s in battery:
        if s.pair_id not in by:
            order.append(s.pair_id)
        by.setdefault(s.pair_id, {})[s.variant] = s
    if smoke:
        order = order[:2]
    return [(triple_ctx(by[p]["A"], by[p]["B"]), by[p]) for p in order]


# -- planted-world validation ------------------------------------------------
def _plant(be: PlantedBackend, specs: dict[str, TermSpec], world: str) -> None:
    bump = 6.0
    for tag, spec in specs.items():
        prompt, base = build_prompt(spec.term)
        e_spans = free_atom_spans(spec, "e")
        f_spans = free_atom_spans(spec, "f")
        shadows = _shadow_binders(parse(specs["A"].term))
        cap_spans = free_atom_spans(spec, shadows[0])
        if len(e_spans) != 1 or len(f_spans) != 1 or len(cap_spans) != 1:
            continue
        e_tok = base + e_spans[0][1] - 1
        f_tok = base + f_spans[0][1] - 1
        cap_tok = base + cap_spans[0][1] - 1
        bumps: dict[int, float] = {}
        if world == "nocal":
            pass
        elif world == "naive":
            bumps[e_tok if tag in ("A", "P") else cap_tok] = bump
        elif world == "correct":
            bumps[e_tok if tag == "P" else cap_tok] = bump
        elif world == "placebo":
            bumps[e_tok if tag in ("A", "P") else cap_tok] = bump
            if tag in ("A", "P"):
                bumps[f_tok] = bump  # differential placebo -> must go VOID
        be.bump_by_text[prompt] = bumps


def validate() -> bool:
    ok = True
    triples = battery_triples()
    n_clean = sum(1 for _c, vs in triples if vs["A"].clean_flip)
    print(
        f"[cr] battery: {len(triples)} triples / {3 * len(triples)} variants, "
        f"{n_clean} clean flips"
    )
    ok &= len(triples) == 18 and n_clean == 9
    for ctx, vs in triples:
        for spec in vs.values():
            assert len(free_atom_spans(spec, "e")) == 1, spec.id
            assert len(free_atom_spans(spec, "f")) == 1, spec.id
        assert ctx.diff_chars, ctx.pair_id
    print("[cr] e/f single free occurrence in all 54 variants ✓")

    worlds = (
        ("naive", "NAIVE-ROUTING"),
        ("correct", "CORRECT-ROUTING"),
        ("nocal", "NO-CALIBRATION"),
        ("placebo", "VOID"),
    )
    for world, want in worlds:
        be = PlantedBackend()
        for _ctx, vs in triples:
            _plant(be, vs, world)
        recs = []
        for ctx, vs in triples:
            for tag in ("A", "B", "P"):
                rec, _grids = score_variant(be, vs[tag], ctx)
                recs.append(rec)
        # deterministic repeat through the real path
        r1, _ = score_variant(be, triples[0][1]["A"], triples[0][0])
        det = max(
            abs(a - b)
            for a, b in zip(
                r1["answer"]["layers_e"],
                recs[0]["answer"]["layers_e"],
                strict=True,
            )
        )
        g = compute_gates(
            recs, np.random.default_rng(0), det_dev=float(det), gqa_ok=True
        )
        a = g["answer"]
        print(
            f"[cr] world={world!r}: verdict={g['verdict']} | "
            f"RC1 sep={a['RC1']['median_pole_sep']:.4f} "
            f"d={a['RC1']['cliffs_delta']:.2f} p={a['RC1']['p_one_sided']:.4f} "
            f"pass={a['RC1']['pass']} | "
            f"RC2 rho_e={a['RC2']['median_rho_e']:.3f} "
            f"CI=({a['RC2']['ci95_low']:.3f},{a['RC2']['ci95_high']:.3f}) | "
            f"RC3 rho_sel={a['RC3']['median_rho_sel']:.3f} "
            f"agree={a['RC3']['agrees_with_rho_e']} | "
            f"placebo_fired={a['placebo']['fired']}"
        )
        ok &= g["verdict"] == want
    print(f"[cr] {'ALL PASS' if ok else 'FAIL'}")
    return bool(ok)


# -- provenance --------------------------------------------------------------
def write_meta(out: Path, args, n_variants: int, bhash: str, gates: dict) -> None:
    import platform

    meta = {
        "run_id": out.name,
        "probe": "P-CONE-ROUTING",
        "frozen": (
            "s335 pre-data (queue row + knowledge page "
            "latent-reasoning-and-the-prefill-triangle.md freeze section); "
            "3 advisory s335 read-mass records disclosed and excluded"
        ),
        "pre_data_instantiations": {
            "primary_scalar": "layer-mean of per-layer-normalized read-mass",
            "rc1_population": "kernel-certified clean-flip triples (n=9)",
            "rc1_corroboration": "mean(Sel_B - Sel_P) > 0 required (direction)",
            "placebo_rule": (
                f"fires iff p<{ALPHA} and |mean| >= "
                f"max({PLACEBO_REL}*|pole_sep|, {PLACEBO_ABS_FLOOR})"
            ),
            "det_tol": DET_TOL,
            "min_aligned_clean": MIN_ALIGNED_CLEAN,
            "rho_denominator_rule": (
                "per-triple exclusion: rho_e needs P-B>0, rho_sel needs "
                "SelP-SelB<0; counts reported"
            ),
        },
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "model_id": args.model_id,
        "device": args.device,
        "dtype": args.dtype,
        "seed": args.seed,
        "smoke": bool(args.smoke),
        "n_variants": n_variants,
        "battery_hash": bhash,
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
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return 0 if validate() else 1

    triples = battery_triples(smoke=args.smoke)
    bhash = battery_hash(
        [vs[t] for _c, vs in triples for t in ("A", "B", "P")]
    )
    n_variants = 3 * len(triples)
    print(
        f"[cr] {len(triples)} triples / {n_variants} variants hash={bhash} "
        f"model={args.model_id} dtype={args.dtype}",
        flush=True,
    )
    backend = HFBackend(args.model_id, args.device, args.dtype)
    print(
        f"[cr] layers={backend.L} heads={backend.n_heads} kv={backend.n_kv} "
        f"gqa_ok={backend.gqa_ok}",
        flush=True,
    )

    recs: list[dict] = []
    all_grids: dict[str, np.ndarray] = {}
    det_dev: float | None = None
    i = 0
    for ctx, vs in triples:
        for tag in ("A", "B", "P"):
            spec = vs[tag]
            rec, grids = score_variant(backend, spec, ctx)
            if i == 0:  # deterministic repeat on the very first variant
                rec2, _ = score_variant(backend, spec, ctx)
                if rec.get("error") is None and rec2.get("error") is None:
                    det_dev = max(
                        abs(a - b)
                        for a, b in zip(
                            rec["answer"]["layers_e"],
                            rec2["answer"]["layers_e"],
                            strict=True,
                        )
                    )
            recs.append(rec)
            all_grids.update(grids)
            i += 1
            print(
                f"[cr] {i}/{n_variants} {spec.id} err={rec['error']}",
                flush=True,
            )

    gates = compute_gates(
        recs,
        np.random.default_rng(args.seed + 7),
        det_dev=det_dev,
        gqa_ok=backend.gqa_ok,
    )
    print(json.dumps(gates, indent=2, default=str))
    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        with (out / "results.jsonl").open("w") as fh:
            for r in recs:
                fh.write(json.dumps(r, default=str) + "\n")
        (out / "gates.json").write_text(json.dumps(gates, indent=2, default=str))
        np.savez_compressed(out / "mass.npz", **all_grids)
        write_meta(out, args, n_variants, bhash, gates)
        print(f"[cr] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
