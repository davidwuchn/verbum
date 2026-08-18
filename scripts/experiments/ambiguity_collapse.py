#!/usr/bin/env python3
"""§P-AMBIGUITY-COLLAPSE — s337 pre-registered probe (frozen, Michael GO).

Probe question: when one ambiguous string generates a continuation, does its
internal trajectory sit between the two readings' basins and COLLAPSE onto the
sampled reading at a readable commitment point, or was it committed before
decode began?

Battery: scope / anaphora / attachment classes, 12 items each.
Registers: value (hidden state), routing (gate_proj sign), attention mass (ana).
Gate tree: C0-C3 calibration, then per-class VOID / PRE-COMMITTED /
SUPERPOSED-COLLAPSE / NO-DECODE-GEOMETRY, global: same -> that / disagree ->
MIXED-BY-CLASS / all VOID -> VOID.

Frozen constants and masses in FROZEN_CONSTANTS block below.

License: MIT.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ambiguity_gate import (
    ANA_ITEMS,
    ATT_ITEMS,
    SCOPE_ITEMS,
    _ana_prompt,
    _att_prompt,
    _json_native,
    _scope_prompt,
    build_battery,
)
from combinator_relationship_map import find_gate_modules, git_sha, log

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS  (§P-AMBIGUITY-COLLAPSE, s337)
# ---------------------------------------------------------------------------
PROBE = "P-AMBIGUITY-COLLAPSE"
FROZEN_NOTE = (
    "s337 pre-data freeze (Michael GO): all three classes, three registers, "
    "C0-C3 calibration before A reads, ordering discipline (commit before "
    "first cue token), masses P30/S25/N25/M15/V5"
)
TEMP = 0.8
TOP_P = 1.0
K_SAMPLES = 16
K_SAMPLES_SMOKE = 4
MAX_NEW_TOKENS = 24
LAYER_FRACS_READ = [0.3, 0.4, 0.5, 0.6, 0.7]
ALPHA = 0.05
C0_ACC = 0.9
C1_MINORITY = 0.2
ALIGN_T = 0.65
SCHMITT_WINDOW = 3
ECHO_FRACTION = 0.5
LABELABLE_MIN = 0.5
CALIB_K = 2  # continuations per pole per item for calibration
APRIORI_MASSES = {
    "PRE-COMMITTED": 30,
    "SUPERPOSED-COLLAPSE": 25,
    "NO-DECODE-GEOMETRY": 25,
    "MIXED-BY-CLASS": 15,
    "VOID": 5,
}

# ANA gender table: M/F per item index (12 items, alternating M,F,M,F,...)
# John/Mark=M, Sarah/Emma=F, Peter/James=M, Alice/Karen=F, ...
ANA_GENDER = tuple(
    "m" if i % 2 == 0 else "f" for i in range(len(ANA_ITEMS))
)


# ---------------------------------------------------------------------------
# Ambiguous A-string templates
# ---------------------------------------------------------------------------

def _scope_a(item) -> str:
    s, _spl, o, _opl, vp, _vpp = item
    return f"Every {s} {vp} a {o}."


def _ana_a(item, gender: str) -> str:
    n1, n2, _pred = item
    pron = "he" if gender == "m" else "she"
    return f"{n1} told {n2} that {pron} had {{pred}}.".format(pred=_pred)


def _att_a(item) -> str:
    ag, pe, ins, _vb, vp, _vpp = item
    return f"The {ag} {vp} the {pe} with the {ins}."


def elicit(a_str: str) -> str:
    """Elicitation prompt: A + ' That is,'"""
    return a_str + " That is,"


# ---------------------------------------------------------------------------
# Cue lexicons for behavioral labeling
# ---------------------------------------------------------------------------

SCOPE_D1_CUES = [
    "the same ", "single ", "one particular", "one and the same",
    "just one", "only one", "the very same",
]
SCOPE_D2_CUES = [
    "each ", "their own", "different ", "or other",
    "separate ", "respective", "one apiece",
    "not necessarily",
]

ATT_D1_CUES = [
    "used the", "using the", "by means of", "with the help of",
    "in hand", "it was with",
]  # Note: "to {verb_base} the" is dynamic — added per item below
ATT_D2_CUES = [
    "had the", "carrying", "holding", "who had",
    "was holding", "in possession", "the one with",
]


def _att_d1_cues(item) -> list[str]:
    """ATT D1 lexicon including the dynamic verb cue."""
    _ag, _pe, _ins, vb, _vp, _vpp = item
    return [*ATT_D1_CUES, f"to {vb} the"]


def _att_d2_cues(item) -> list[str]:
    """ATT D2 lexicon including the dynamic passive-voice cue."""
    _ag, _pe, _ins, _vb, _vp, vpp = item
    return [*ATT_D2_CUES, f"was {vpp} by"]


def _count_cues(text: str, cues: list[str]) -> int:
    t = text.lower()
    return sum(1 for c in cues if c.lower() in t)


def grade_scope(continuation: str) -> str | None:
    """Returns 'D1', 'D2', or None (tie/zero)."""
    c1 = _count_cues(continuation, SCOPE_D1_CUES)
    c2 = _count_cues(continuation, SCOPE_D2_CUES)
    if c1 > c2:
        return "D1"
    if c2 > c1:
        return "D2"
    return None


def grade_att(continuation: str, item) -> str | None:
    d1_cues = _att_d1_cues(item)
    d2_cues = _att_d2_cues(item)
    c1 = _count_cues(continuation, d1_cues)
    c2 = _count_cues(continuation, d2_cues)
    if c1 > c2:
        return "D1"
    if c2 > c1:
        return "D2"
    return None


def grade_ana(continuation: str, item) -> str | None:
    """Returns 'D1' (n1), 'D2' (n2), or None.

    D1 = n1 is the referent, D2 = n2. Graded by finding which name appears
    in a 'had'-clause pattern first; fallback to first occurrence.
    """
    n1, n2, _pred = item
    cont = continuation.lower()
    n1l, n2l = n1.lower(), n2.lower()

    # Look for "{name} had" pattern
    pat1 = f"{n1l} had"
    pat2 = f"{n2l} had"
    i1 = cont.find(pat1)
    i2 = cont.find(pat2)
    if i1 >= 0 and (i2 < 0 or i1 < i2):
        return "D1"
    if i2 >= 0 and (i1 < 0 or i2 < i1):
        return "D2"

    # Fallback: first occurrence of either name
    j1 = cont.find(n1l)
    j2 = cont.find(n2l)
    if j1 >= 0 and (j2 < 0 or j1 < j2):
        return "D1"
    if j2 >= 0 and (j1 < 0 or j2 < j1):
        return "D2"
    return None


def grade_continuation(cls: str, continuation: str, item, pole: int | None = None
                        ) -> str | None:
    """Grade a continuation string. pole is ignored (used by static check path)."""
    if cls == "scope":
        return grade_scope(continuation)
    if cls == "ana":
        return grade_ana(continuation, item)
    if cls == "att":
        return grade_att(continuation, item)
    raise ValueError(cls)


# ---------------------------------------------------------------------------
# Static grader accuracy check (--validate, no model needed)
# ---------------------------------------------------------------------------

def _pole_sentence_as_continuation(cls: str, item, pole: int, f: int) -> str:
    """Return the D1/D2 gate sentence as a pseudo-continuation for grader check."""
    if cls == "scope":
        return _scope_prompt(item, pole, f)
    if cls == "ana":
        return _ana_prompt(item, pole, f)
    if cls == "att":
        return _att_prompt(item, pole, f)
    raise ValueError(cls)


def static_grader_check(items_by_class: dict, n_items: int = 12) -> dict[str, float]:
    """Check grader recovers correct pole on pole sentences.

    Return per-class accuracy.
    """
    classes_items = {
        "scope": SCOPE_ITEMS,
        "ana": ANA_ITEMS,
        "att": ATT_ITEMS,
    }
    from ambiguity_gate import N_FRAMES
    acc = {}
    for cls, items_list in classes_items.items():
        total, correct = 0, 0
        for i in range(min(n_items, len(items_list))):
            item = items_list[i]
            for pole in (0, 1):
                expected = "D1" if pole == 0 else "D2"
                for f in range(N_FRAMES):
                    sent = _pole_sentence_as_continuation(cls, item, pole, f)
                    pred = grade_continuation(cls, sent, item)
                    if pred == expected:
                        correct += 1
                    total += 1
        acc[cls] = correct / max(total, 1)
    return acc


# ---------------------------------------------------------------------------
# Layer index helpers
# ---------------------------------------------------------------------------

def _read_layer_indices(n_layers: int) -> list[int]:
    """Map LAYER_FRACS_READ to actual layer indices (no model dependency)."""
    return sorted({
        min(n_layers - 1, max(0, round(f * (n_layers - 1))))
        for f in LAYER_FRACS_READ
    })


# ---------------------------------------------------------------------------
# Analysis functions (shared by real and planted paths — s331 law)
# ---------------------------------------------------------------------------

def _schmitt_commit(delta: np.ndarray, window: int) -> int:
    """First t >= 1 s.t. sign(delta[t:t+window]) all == sign(delta[-1]).
    Returns 1-based step index (1 = committed from start).
    Falls back to T if never triggered.
    """
    T = len(delta)
    if T == 0:
        return 1
    final_sign = np.sign(np.mean(delta[-3:])) if T >= 3 else np.sign(delta[-1])
    if final_sign == 0:
        final_sign = 1
    for t in range(0, T):
        end = min(t + window, T)
        chunk = delta[t:end]
        if len(chunk) == 0:
            continue
        if np.all(np.sign(chunk) == final_sign):
            return t + 1  # 1-based
    return T


def _first_cue_step_from_text(
    tokens_text: list[str],
    label: str | None,
    cls: str,
    item,
) -> int | None:
    """Find first generated step index (0-based) where cue for label appears.

    For ana: first occurrence of labeled name in incremental text.
    Returns None if label is None.
    """
    if label is None:
        return None
    cues: list[str]
    if cls == "scope":
        cues = SCOPE_D1_CUES if label == "D1" else SCOPE_D2_CUES
    elif cls == "att":
        cues = _att_d1_cues(item) if label == "D1" else _att_d2_cues(item)
    elif cls == "ana":
        n1, n2, _ = item
        cues = [n1.lower()] if label == "D1" else [n2.lower()]
    else:
        return None

    cumulative = ""
    for step, tok in enumerate(tokens_text):
        cumulative += tok
        cl = cumulative.lower()
        if any(c in cl for c in cues):
            return step
    return None  # cue never appears


def _final_sign_from_delta(delta_steps: list[float]) -> float:
    """Sign of mean of last 3 steps of delta trajectory (same rule used everywhere)."""
    arr = np.array(delta_steps)
    if len(arr) >= 3:
        return float(np.sign(np.mean(arr[-3:])))
    if len(arr) > 0:
        return float(np.sign(arr[-1]))
    return 0.0


def analyze_samples(
    samples: list[dict],
    cls: str,
    item,
    pole_axis: np.ndarray,
    pole_mean_d1: float,
    pole_std_d1: float,
    pole_mean_d2: float,
    pole_std_d2: float,
    best_layer: int,
) -> dict[str, Any]:
    """Analyze a list of labeled A-generation samples for one item.

    Each sample: {label, delta_steps, first_cue_step, commit_step, ...}
    Returns alignment_rate, pre_committed_frac, echo check, licensed flag.
    The alignment permutation null shuffles label assignments, then recomputes
    final_aligned from the unchanged trajectories — this properly tests
    whether trajectory sign is correlated with the actual label.
    """
    labeled = [s for s in samples if s["label"] is not None]
    if not labeled:
        return {
            "n_labeled": 0, "labelable_frac": 0.0,
            "alignment_rate": None, "alignment_p": None,
            "pre_committed_frac": None, "echo_frac": None,
            "licensed_precedes_surface": None,
            "median_commit_step": None,
        }

    n = len(samples)
    n_lab = len(labeled)
    labelable_frac = n_lab / max(n, 1)

    # Trajectory signs and true labels (for permutation test)
    traj_signs = np.array([
        _final_sign_from_delta(s["delta_steps"]) for s in labeled
    ])
    true_labels_d1 = np.array([1.0 if s["label"] == "D1" else -1.0 for s in labeled])

    # final alignment: sign(delta_end) == expected_sign_for_label
    aligned_mask = traj_signs == true_labels_d1
    alignment_rate = float(aligned_mask.mean())

    # label-shuffle permutation: shuffle label assignments, recompute alignment
    # Null: sign(delta_end) alignment with SHUFFLED labels
    n_perm = 5000
    rng = np.random.default_rng(42)
    obs_rate = alignment_rate
    null_rates = np.zeros(n_perm)
    for p in range(n_perm):
        perm_labels = rng.permutation(true_labels_d1)
        null_rates[p] = float(np.mean(traj_signs == perm_labels))
    alignment_p = float(np.mean(null_rates >= obs_rate))

    # commit_step stats
    commit_steps = [s["commit_step"] for s in labeled if s["commit_step"] is not None]
    pre_committed = [cs for cs in commit_steps if cs == 1]
    pre_committed_frac = len(pre_committed) / max(len(commit_steps), 1)
    median_commit_step = float(np.median(commit_steps)) if commit_steps else None

    # echo check: committed before first cue
    echo_eligible = [
        s for s in labeled
        if s["commit_step"] is not None and s["first_cue_step"] is not None
    ]
    echo_before = [
        s for s in echo_eligible
        # commit_step is 1-based (lock begins at generated index commit_step-1);
        # first_cue_step is 0-based (cue completes at that index). "Commit
        # precedes surface" == lock index strictly < cue index.
        if (s["commit_step"] - 1) < s["first_cue_step"]
    ]
    echo_frac = (
        len(echo_before) / max(len(echo_eligible), 1)
        if echo_eligible else None
    )
    licensed = echo_frac is not None and echo_frac >= ECHO_FRACTION

    return {
        "n_labeled": n_lab,
        "labelable_frac": float(labelable_frac),
        "alignment_rate": float(alignment_rate),
        "alignment_p": float(alignment_p),
        "pre_committed_frac": float(pre_committed_frac),
        "median_commit_step": median_commit_step,
        "echo_frac": float(echo_frac) if echo_frac is not None else None,
        "licensed_precedes_surface": bool(licensed),
    }


def per_class_verdict(
    cls_items_stats: list[dict],
    c0_acc: float,
    c2_pass: bool,
    c1_minority_fail_majority: bool,
    cls_align_rate: float | None = None,
    cls_align_p: float | None = None,
) -> str:
    """Frozen per-class verdict logic.

    cls_align_rate and cls_align_p are the pooled class-level alignment
    stats (from compute_class_alignment). If not provided, they are
    estimated from the per-item stats (fallback only).
    """
    # VOID-C: C0 fail or labelable fraction < LABELABLE_MIN
    lab_fracs = [s["labelable_frac"] for s in cls_items_stats
                 if s["labelable_frac"] is not None]
    mean_labelable = float(np.mean(lab_fracs)) if lab_fracs else 0.0
    if c0_acc < C0_ACC or mean_labelable < LABELABLE_MIN:
        return "VOID-C"
    # If C2 failed: VOID-C (instrument, not substrate)
    if not c2_pass:
        return "VOID-C"

    # Alignment gate (class-level pooled stats preferred)
    if cls_align_rate is not None and cls_align_p is not None:
        mean_align = cls_align_rate
        mean_p = cls_align_p
    else:
        align_rates = [s["alignment_rate"] for s in cls_items_stats
                       if s["alignment_rate"] is not None]
        align_ps = [s["alignment_p"] for s in cls_items_stats
                    if s["alignment_p"] is not None]
        mean_align = float(np.mean(align_rates)) if align_rates else 0.0
        mean_p = float(np.mean(align_ps)) if align_ps else 1.0

    alignment_gate_passes = mean_align >= ALIGN_T and mean_p < ALPHA

    precommit_fracs = [s["pre_committed_frac"] for s in cls_items_stats
                       if s["pre_committed_frac"] is not None]
    mean_precommit = float(np.mean(precommit_fracs)) if precommit_fracs else 0.0

    # PRE-COMMITTED-C
    if c1_minority_fail_majority or (alignment_gate_passes and mean_precommit > 0.5):
        return "PRE-COMMITTED-C"

    # SUPERPOSED-COLLAPSE-C
    med_steps = [s["median_commit_step"] for s in cls_items_stats
                 if s["median_commit_step"] is not None]
    med_commit = float(np.median(med_steps)) if med_steps else None
    if alignment_gate_passes and med_commit is not None and med_commit >= 2:
        return "SUPERPOSED-COLLAPSE-C"

    # NO-DECODE-GEOMETRY-C
    return "NO-DECODE-GEOMETRY-C"


def compute_class_alignment(
    samples_per_item: list[list[dict]],
    n_perm: int = 5000,
) -> tuple[float, float]:
    """Pooled class-level alignment rate and permutation p-value.

    Pools all labeled samples across items. Per-item label shuffles are
    done independently to preserve within-item balance (spec: within item).
    """
    all_traj_signs: list[float] = []
    all_lab_signs: list[float] = []
    item_slices: list[tuple[int, int]] = []

    for samples in samples_per_item:
        labeled = [s for s in samples if s.get("label") is not None]
        start = len(all_traj_signs)
        for s in labeled:
            all_traj_signs.append(_final_sign_from_delta(s["delta_steps"]))
            all_lab_signs.append(1.0 if s["label"] == "D1" else -1.0)
        item_slices.append((start, len(all_traj_signs)))

    traj = np.array(all_traj_signs)
    lab = np.array(all_lab_signs)
    if len(traj) == 0:
        return 0.0, 1.0

    obs_rate = float(np.mean(traj == lab))

    rng = np.random.default_rng(77)
    null_rates = np.zeros(n_perm)
    for p in range(n_perm):
        plab = lab.copy()
        for start, end in item_slices:
            # Shuffle within each item independently
            plab[start:end] = rng.permutation(plab[start:end])
        null_rates[p] = float(np.mean(traj == plab))

    p_val = float(np.mean(null_rates >= obs_rate))
    return obs_rate, p_val


def global_verdict(class_verdicts: dict[str, str]) -> str:
    live = {k: v for k, v in class_verdicts.items() if v != "VOID-C"}
    if not live:
        return "VOID"
    unique = set(live.values())
    if len(unique) == 1:
        # map class verdict to global (strip trailing "-C" suffix only)
        cv = next(iter(unique))
        return cv[:-2] if cv.endswith("-C") else cv
    return "MIXED-BY-CLASS"


# ---------------------------------------------------------------------------
# Name-position extraction for attention (ana items)
# ---------------------------------------------------------------------------

def _find_name_token_positions(
    prompt: str, n1: str, n2: str, tokenizer
) -> tuple[list[int], list[int]]:
    """Find token indices for n1 and n2 in the prompt using offset mapping."""
    enc = tokenizer(prompt, return_offsets_mapping=True, add_special_tokens=True)
    offsets = enc["offset_mapping"]

    def name_positions(name: str) -> list[int]:
        # Find first occurrence of name in prompt text
        start = prompt.find(name)
        if start < 0:
            return []
        end = start + len(name)
        toks = []
        for ti, (ts, te) in enumerate(offsets):
            if ts < end and te > start:
                toks.append(ti)
        return toks

    return name_positions(n1), name_positions(n2)


# ---------------------------------------------------------------------------
# Real model backend
# ---------------------------------------------------------------------------

class RealBackend:
    def __init__(self, model_id: str, device: str, dtype_str: str):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.device = device
        dtype = getattr(torch, dtype_str)
        log(f"[ac] loading {model_id} ({dtype_str}, {device})")
        self.tok = AutoTokenizer.from_pretrained(model_id)
        self.model = (
            AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=dtype,
                attn_implementation="eager",
            )
            .to(device)
            .eval()
        )
        cfg = self.model.config
        self.n_heads = int(cfg.num_attention_heads)
        self.n_kv = int(getattr(cfg, "num_key_value_heads", self.n_heads))
        gate_mods = find_gate_modules(self.model)
        self.n_layers = len(gate_mods)
        self.gate_mods = gate_mods
        self.read_layers = _read_layer_indices(self.n_layers)
        log(
            f"[ac] n_layers={self.n_layers} heads={self.n_heads} "
            f"kv={self.n_kv} read_layers={self.read_layers}"
        )

    # -- prefill capture (pole sentences) ------------------------------------
    def prefill_hidden(
        self, prompt: str, read_layers: list[int]
    ) -> dict[int, np.ndarray]:
        """Capture last-token hidden states at read_layers for a single prompt."""
        torch = self.torch
        enc = self.tok(prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            out = self.model(**enc, output_hidden_states=True)
        result = {}
        for li in read_layers:
            h = out.hidden_states[li + 1][0, -1].float().cpu().numpy()
            result[li] = h
        return result

    def prefill_gate_sign(
        self, prompt: str, read_layers: list[int]
    ) -> dict[int, np.ndarray]:
        """Capture last-token gate_proj pre-activation signs at read_layers."""
        torch = self.torch
        buf: dict[int, np.ndarray] = {}
        handles = []
        want = set(read_layers)

        def mk(li):
            def hook(_m, _inp, out):
                buf[li] = np.sign(out[0, -1].detach().float().cpu().numpy())
            return hook

        for li, _nm, mod in self.gate_mods:
            if li in want:
                handles.append(mod.register_forward_hook(mk(li)))
        try:
            enc = self.tok(prompt, return_tensors="pt").to(self.device)
            with torch.no_grad():
                self.model(**enc)
        finally:
            for h in handles:
                h.remove()
        return dict(buf)

    # -- value-weighted attention mass (for ana) ------------------------------
    def prefill_v_norms(
        self, prompt: str, read_layers: list[int]
    ) -> dict[int, np.ndarray]:
        """Per-position per-kv-head value norms at read_layers.

        Uses the cone_routing value-weighted attention mass pattern.
        """
        torch = self.torch
        buf: dict[int, np.ndarray] = {}
        handles = []
        want = set(read_layers)

        def mk(li):
            def hook(_m, _inp, out):
                v = out[0] if isinstance(out, tuple) else out
                head_dim = v.shape[-1] // self.n_kv
                # v: (1, T, n_kv * head_dim) -> norms: (T, n_kv)
                buf[li] = (
                    v[0].float().view(-1, self.n_kv, head_dim)
                    .norm(dim=-1).cpu().numpy()
                )
            return hook

        for li, layer in enumerate(self.model.model.layers):
            if li in want:
                handles.append(layer.self_attn.v_proj.register_forward_hook(mk(li)))
        try:
            enc = self.tok(prompt, return_tensors="pt").to(self.device)
            with torch.no_grad():
                self.model(**enc, output_attentions=True)
        finally:
            for h in handles:
                h.remove()
        return buf

    # -- generation with per-step capture ------------------------------------
    def generate_with_capture(
        self,
        prompt: str,
        k: int,
        seed: int,
        read_layers: list[int],
        capture_attn_for_names: tuple[list[int], list[int]] | None,
        v_norms_by_layer: dict[int, np.ndarray] | None,
    ) -> list[dict]:
        """Generate k continuations, each with per-step value/gate/attn capture.

        Returns list of sample dicts each with:
          token_ids, token_texts, hidden_steps[li], gate_steps[li],
          attn_mass_steps[li] (if ana).
        """
        torch = self.torch
        enc = self.tok(prompt, return_tensors="pt").to(self.device)
        group = self.n_heads // self.n_kv

        samples = []
        for ki in range(k):
            rng_seed = seed * 1000 + ki
            torch.manual_seed(rng_seed)
            if self.device == "mps":
                torch.mps.manual_seed(rng_seed)

            token_ids: list[int] = []
            hidden_steps: dict[int, list[np.ndarray]] = {li: [] for li in read_layers}
            gate_steps: dict[int, list[np.ndarray]] = {li: [] for li in read_layers}
            attn_mass_steps: dict[int, list[tuple[float, float]]] = (
                {li: [] for li in read_layers}
                if capture_attn_for_names is not None
                else {}
            )

            # Autoregressive decode loop
            input_ids = enc["input_ids"].clone()
            attention_mask = enc["attention_mask"].clone()
            past_key_values = None

            for _step in range(MAX_NEW_TOKENS):
                gate_buf: dict[int, np.ndarray] = {}
                handles = []
                want = set(read_layers)

                _captured_buf = gate_buf

                def mk_gate(layer_idx: int, _buf: dict = _captured_buf):
                    def hook(_m, _inp, hook_out):
                        _buf[layer_idx] = np.sign(
                            hook_out[0, -1].detach().float().cpu().numpy()
                        )
                    return hook

                for li, _nm, mod in self.gate_mods:
                    if li in want:
                        handles.append(mod.register_forward_hook(mk_gate(li)))
                try:
                    with torch.no_grad():
                        out = self.model(
                            input_ids=input_ids,
                            attention_mask=attention_mask,
                            past_key_values=past_key_values,
                            use_cache=True,
                            output_hidden_states=True,
                            output_attentions=(capture_attn_for_names is not None),
                        )
                finally:
                    for hd in handles:
                        hd.remove()

                past_key_values = out.past_key_values
                logits = out.logits[0, -1]

                # Sample with temperature and top_p
                logits_f = logits.float()
                logits_f = logits_f / max(TEMP, 1e-9)
                probs = torch.softmax(logits_f, dim=-1)

                # Top-p filtering
                sorted_probs, sorted_idx = torch.sort(probs, descending=True)
                cumprob = torch.cumsum(sorted_probs, dim=0)
                mask = cumprob - sorted_probs > TOP_P
                sorted_probs[mask] = 0.0
                sorted_probs = sorted_probs / sorted_probs.sum()
                chosen_local = torch.multinomial(sorted_probs, 1)
                next_token = sorted_idx[chosen_local]
                tid = int(next_token.item())
                token_ids.append(tid)

                # Capture hidden states
                for li in read_layers:
                    h = out.hidden_states[li + 1][0, -1].float().cpu().numpy()
                    hidden_steps[li].append(h)

                # Capture gate signs
                for li in read_layers:
                    if li in gate_buf:
                        gate_steps[li].append(gate_buf[li])

                # Capture attention mass (ana only)
                if capture_attn_for_names is not None and out.attentions is not None:
                    n1_toks, n2_toks = capture_attn_for_names
                    for li in read_layers:
                        if li < len(out.attentions):
                            attn = out.attentions[li]  # (1, H, T_q, T_k)
                            # last generated position attending to prompt
                            w = attn[0, :, -1, :].float().cpu().numpy()  # (H, T_k)
                            # value-weighted using prefill v_norms
                            if v_norms_by_layer is not None and li in v_norms_by_layer:
                                vn = v_norms_by_layer[li]  # (T_prompt, n_kv)
                                # expand to (H, T_prompt)
                                vn_exp = np.repeat(vn.T, group, axis=0)
                                # w shape may differ from vn if T_k includes past
                                # only use prompt positions
                                T_prompt = vn.shape[0]
                                w_prompt = w[:, :T_prompt]
                                weighted = w_prompt * vn_exp  # (H, T_prompt)
                            else:
                                T_prompt = w.shape[1]
                                weighted = w

                            # mass toward n1 and n2
                            m1 = float(
                                sum(
                                    weighted[:, p].mean()
                                    for p in n1_toks
                                    if p < T_prompt
                                )
                            )
                            m2 = float(
                                sum(
                                    weighted[:, p].mean()
                                    for p in n2_toks
                                    if p < T_prompt
                                )
                            )
                            attn_mass_steps[li].append((m1, m2))

                # Update input for next step
                next_tok_tensor = next_token.view(1, 1)
                input_ids = next_tok_tensor
                attention_mask = torch.ones(
                    (1, 1), dtype=torch.long, device=self.device
                )

                if self.tok.eos_token_id is not None and tid == self.tok.eos_token_id:
                    break

            # Decode token texts
            token_texts = [
                self.tok.decode([tid], skip_special_tokens=False)
                for tid in token_ids
            ]
            samples.append({
                "seed": rng_seed,
                "token_ids": token_ids,
                "token_texts": token_texts,
                "hidden_steps": {
                    li: list(hs) for li, hs in hidden_steps.items()
                },
                "gate_steps": {
                    li: list(gs) for li, gs in gate_steps.items()
                },
                "attn_mass_steps": attn_mass_steps,
            })

        return samples


# ---------------------------------------------------------------------------
# Planted world backend (--validate, no model)
# ---------------------------------------------------------------------------

class PlantedBackend:
    """Synthetic analysis inputs for planted-world validation."""

    def __init__(self, n_layers: int = 16, d: int = 64):
        self.n_layers = n_layers
        self.n_heads = 8
        self.n_kv = 4
        self.d = d
        self.read_layers = _read_layer_indices(n_layers)

    def make_pole_states(
        self,
        cls_items: list[tuple],
        n_items: int,
        cls: str,
    ) -> tuple[dict, dict, dict]:
        """Synthetic: (d1_states, d2_states) per item per layer,
        plus pole axes and calibration stats.
        """
        rng = np.random.default_rng(7)
        d = self.d
        # Class-level pole axis per layer
        axes = {}
        for li in self.read_layers:
            ax = rng.normal(size=d)
            ax = ax / (np.linalg.norm(ax) + 1e-12)
            axes[li] = ax

        calib = {}
        for li in self.read_layers:
            calib[li] = {
                "mean_d1": 1.0,
                "std_d1": 0.3,
                "mean_d2": -1.0,
                "std_d2": 0.3,
            }

        return axes, calib

    def synthetic_delta_trajectory(
        self,
        world: str,
        k: int,
        T: int,
        label: str,
        rng,
    ) -> tuple[np.ndarray, int, int]:
        """Returns (delta_steps[T], commit_step[1-based], first_cue_step).

        label: 'D1' -> positive pole, 'D2' -> negative.
        """
        sign = 1.0 if label == "D1" else -1.0

        if world == "collapse":
            # Starts near 0, ramps up to labeled pole around step 5, locks
            noise = rng.normal(0, 0.1, T)
            ramp = np.zeros(T)
            for t in range(T):
                ramp[t] = sign * min(1.0, max(0.0, (t - 2) / 4.0))
            delta = ramp + noise
            first_cue = min(10, T - 1)

        elif world == "precommit":
            # At labeled pole from step 0
            noise = rng.normal(0, 0.05, T)
            delta = sign * (1.0 + noise)
            first_cue = min(5, T - 1)

        elif world == "nogeom":
            # Pure noise, no alignment
            delta = rng.normal(0, 0.5, T)
            first_cue = min(5, T - 1)

        elif world == "echo":
            # Locks AFTER cue step — commit_step > first_cue_step
            noise = rng.normal(0, 0.05, T)
            ramp = np.zeros(T)
            cue_t = min(4, T - 1)
            for t in range(T):
                ramp[t] = sign * min(1.0, max(0.0, (t - cue_t - 1) / 3.0))
            delta = ramp + noise
            first_cue = cue_t

        else:
            raise ValueError(f"Unknown world: {world}")

        # Compute commit_step using Schmitt trigger
        commit = _schmitt_commit(delta, SCHMITT_WINDOW)
        return delta, commit, first_cue


def _planted_sample(
    world: str, cls: str, item_idx: int, ki: int, label: str, T: int = 15
) -> dict:
    """Build a synthetic sample for a planted world."""
    rng = np.random.default_rng(world.__hash__() % (2**31) + item_idx * 100 + ki)
    be = PlantedBackend()
    delta, commit_step, first_cue_step = be.synthetic_delta_trajectory(
        world, 1, T, label, rng
    )
    # final alignment: sign(mean(last 3)) == label
    final_sign = np.sign(np.mean(delta[-3:])) if T >= 3 else np.sign(delta[-1])
    expected_sign = 1.0 if label == "D1" else -1.0
    final_aligned = bool(final_sign == expected_sign)

    return {
        "cls": cls,
        "item": item_idx,
        "kind": "A",
        "label": label,
        "seed": ki,
        "delta_steps": delta.tolist(),
        "commit_step": commit_step,
        "first_cue_step": first_cue_step,
        "final_aligned": final_aligned,
    }


# ---------------------------------------------------------------------------
# Calibration gate helpers
# ---------------------------------------------------------------------------

def compute_c1_minority(labels_per_item: list[list[str | None]]) -> dict:
    """C1: for each item, fraction of minority label among labeled samples."""
    results = []
    for labs in labels_per_item:
        labeled = [lb for lb in labs if lb is not None]
        if not labeled:
            results.append({"minority_frac": 0.0, "n": 0})
            continue
        d1 = sum(1 for lb in labeled if lb == "D1")
        d2 = len(labeled) - d1
        minority = min(d1, d2)
        results.append({
            "minority_frac": minority / max(len(labeled), 1),
            "n": len(labeled),
        })
    minority_fracs = [r["minority_frac"] for r in results if r["n"] > 0]
    fail_majority = (
        sum(1 for f in minority_fracs if f < C1_MINORITY)
        > len(minority_fracs) / 2
    )
    return {
        "per_item": results,
        "mean_minority": float(np.mean(minority_fracs)) if minority_fracs else 0.0,
        "fail_majority": bool(fail_majority),
    }


def compute_c2_axis_sep(
    d1_projs: list[float], d2_projs: list[float], n_perm: int = 5000
) -> dict:
    """C2: AUC > chance with label-permutation p < 0.05."""
    if not d1_projs or not d2_projs:
        return {"pass": False, "mean_d1": None, "mean_d2": None, "p": 1.0}
    d1 = np.array(d1_projs)
    d2 = np.array(d2_projs)
    obs_sep = float(d1.mean() - d2.mean())
    rng = np.random.default_rng(99)
    all_vals = np.concatenate([d1, d2])
    null = np.array([
        rng.permutation(all_vals)[: len(d1)].mean()
        - rng.permutation(all_vals)[len(d1) :].mean()
        for _ in range(n_perm)
    ])
    p = float(np.mean(np.abs(null) >= abs(obs_sep)))
    return {
        "pass": bool(p < ALPHA and obs_sep != 0),
        "mean_d1": float(d1.mean()),
        "mean_d2": float(d2.mean()),
        "sep": float(obs_sep),
        "p": p,
    }


def compute_c3_ana_mass(diffs: list[float], n_perm: int = 5000) -> dict:
    """C3 (ana only): mean differenced mass toward known referent > 0."""
    if not diffs:
        return {"pass": False, "mean_diff": None, "p": 1.0}
    arr = np.array(diffs)
    obs = float(arr.mean())
    rng = np.random.default_rng(13)
    null = np.array([
        (rng.choice([-1.0, 1.0], size=arr.size) * arr).mean()
        for _ in range(n_perm)
    ])
    p = float(np.mean(null >= obs))
    return {
        "pass": bool(p < ALPHA and obs > 0),
        "mean_diff": obs,
        "p": p,
    }


# ---------------------------------------------------------------------------
# Main: --validate (planted worlds, no model)
# ---------------------------------------------------------------------------

def run_validate(args) -> int:
    ok = True

    # Static grader check
    acc = static_grader_check({}, n_items=12)
    log("[ac] --- static grader check ---")
    grader_ok = True
    for cls, a in acc.items():
        hit = a >= C0_ACC
        grader_ok &= hit
        log(f"[ac]   {cls}: acc={a:.3f} (need >= {C0_ACC}) {'OK' if hit else 'FAIL'}")
    ok &= grader_ok
    log(f"[ac] static grader: {'OK' if grader_ok else 'FAIL'}")

    # Planted worlds
    log("\n[ac] --- planted world verdicts ---")
    n_items = 2  # minimal for validate

    worlds_spec: list[tuple[str, str, str | None]] = [
        ("collapse", "SUPERPOSED-COLLAPSE", None),
        ("precommit", "PRE-COMMITTED", None),
        ("nogeom", "NO-DECODE-GEOMETRY", None),
        ("echo", "SUPERPOSED-COLLAPSE", "licensed_precedes_surface==False"),
    ]

    for world, want_verdict, extra_check in worlds_spec:
        # Build synthetic samples for 3 classes x n_items items
        k = 16  # enough permutation power for p < 0.05 (C(16,8)>>100)
        T = 15
        class_verdicts: dict[str, str] = {}
        all_licensed: list[bool] = []

        for cls in ("scope", "ana", "att"):
            items_stats = []
            samples_per_item: list[list[dict]] = []

            for item_idx in range(n_items):
                # Alternate label assignment to ensure minority > 0
                item_samples = []
                for ki in range(k):
                    label = "D1" if ki % 2 == 0 else "D2"
                    if world == "nogeom":
                        # nogeom: mixed labels (equal split)
                        label = "D1" if ki < k // 2 else "D2"
                    s = _planted_sample(world, cls, item_idx, ki, label, T)
                    item_samples.append(s)
                samples_per_item.append(item_samples)

                labeled = [s for s in item_samples if s["label"] is not None]
                n_lab = len(labeled)
                labelable_frac = n_lab / max(k, 1)

                if not labeled:
                    items_stats.append({
                        "n_labeled": 0,
                        "labelable_frac": 0.0,
                        "alignment_rate": None,
                        "alignment_p": None,
                        "pre_committed_frac": None,
                        "median_commit_step": None,
                        "echo_frac": None,
                        "licensed_precedes_surface": None,
                    })
                    continue

                commit_steps = [s["commit_step"] for s in labeled]
                n_pre = sum(1 for c in commit_steps if c == 1)
                pre_committed_frac = n_pre / max(len(commit_steps), 1)
                med_commit = float(np.median(commit_steps))

                echo_eligible = [
                    s for s in labeled
                    if s["commit_step"] is not None
                    and s["first_cue_step"] is not None
                ]
                echo_before = [
                    s for s in echo_eligible
                    if s["commit_step"] < s["first_cue_step"]
                ]
                echo_frac = (
                    len(echo_before) / max(len(echo_eligible), 1)
                    if echo_eligible else None
                )
                licensed = echo_frac is not None and echo_frac >= ECHO_FRACTION

                if world == "echo":
                    all_licensed.append(licensed)

                items_stats.append({
                    "n_labeled": n_lab,
                    "labelable_frac": float(labelable_frac),
                    "alignment_rate": None,  # filled by pooled test
                    "alignment_p": None,
                    "pre_committed_frac": float(pre_committed_frac),
                    "median_commit_step": float(med_commit),
                    "echo_frac": float(echo_frac) if echo_frac is not None else None,
                    "licensed_precedes_surface": bool(licensed),
                })

            # Pooled class-level alignment test (per-item shuffle within)
            cls_align_rate, cls_align_p = compute_class_alignment(
                samples_per_item, n_perm=2000
            )

            # C2 pass: for nogeom, the axis EXISTS but A-trajectories
            # show no signal (alignment gate fails) -> NO-DECODE-GEOMETRY-C.
            # C2=True for all non-VOID planted worlds.
            c2_pass = True
            # Compute C1
            labels_per_item = [
                [s["label"] for s in sp if s["label"] is not None]
                for sp in samples_per_item
            ]
            c1 = compute_c1_minority(labels_per_item)
            c0_acc_val = 1.0  # static grader passes

            cv = per_class_verdict(
                items_stats,
                c0_acc_val,
                c2_pass,
                c1["fail_majority"],
                cls_align_rate=cls_align_rate,
                cls_align_p=cls_align_p,
            )
            class_verdicts[cls] = cv

        gv = global_verdict(class_verdicts)

        if extra_check == "licensed_precedes_surface==False":
            # For echo world: check that licensed_precedes_surface is False
            # (commit_step > first_cue_step for most samples)
            echo_licensed_false = not any(all_licensed) if all_licensed else True
            hit_verdict = gv == want_verdict
            hit_echo = echo_licensed_false
            hit = hit_verdict and hit_echo
            ok &= hit
            log(
                f"[ac] world={world!r}: verdict={gv} (want {want_verdict}) "
                f"licensed_precedes_surface=False: {echo_licensed_false} "
                f"{'OK' if hit else 'FAIL'}"
            )
        else:
            hit = gv == want_verdict
            ok &= hit
            log(
                f"[ac] world={world!r}: verdict={gv} (want {want_verdict}) "
                f"{'OK' if hit else 'FAIL'} | class_verdicts={class_verdicts}"
            )

    log(f"\n[ac] {'ALL PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# Battery hash
# ---------------------------------------------------------------------------

def _battery_hash(recs: list[dict]) -> str:
    blob = json.dumps([r["prompt"] for r in recs], sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Results writing
# ---------------------------------------------------------------------------

def write_meta(
    out: Path,
    args,
    n_variants: int,
    bhash: str,
    gates: dict,
    lib_versions: dict,
) -> None:
    meta = {
        "run_id": out.name,
        "probe": PROBE,
        "frozen": FROZEN_NOTE,
        "pre_data_instantiations": {
            "TEMP": TEMP,
            "TOP_P": TOP_P,
            "K_SAMPLES": K_SAMPLES,
            "MAX_NEW_TOKENS": MAX_NEW_TOKENS,
            "LAYER_FRACS_READ": LAYER_FRACS_READ,
            "ALPHA": ALPHA,
            "C0_ACC": C0_ACC,
            "C1_MINORITY": C1_MINORITY,
            "ALIGN_T": ALIGN_T,
            "SCHMITT_WINDOW": SCHMITT_WINDOW,
            "ECHO_FRACTION": ECHO_FRACTION,
            "LABELABLE_MIN": LABELABLE_MIN,
            "apriori_masses": APRIORI_MASSES,
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
        "lib_versions": lib_versions,
        "gates": gates,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=_json_native))


# ---------------------------------------------------------------------------
# Main: real run
# ---------------------------------------------------------------------------

def run_real(args) -> int:
    import torch

    n_items_per_class = 2 if args.smoke else 12
    k_samples = K_SAMPLES_SMOKE if args.smoke else K_SAMPLES

    # Build battery (for gate-sentence capture)
    gate_recs = build_battery(smoke=args.smoke)
    bhash = _battery_hash(gate_recs)
    log(f"[ac] gate battery: {len(gate_recs)} records hash={bhash}")

    out_dir = (
        args.out
        or (
            "results/p_ambiguity_collapse_s337/"
            + ("smoke_4b" if args.smoke else "run_14b")
        )
    )
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Load backend
    be = RealBackend(args.model_id, args.device, args.dtype)

    # --- STEP 2: STATIC POLE CAPTURE ---
    log("[ac] === STEP 2: pole capture ===")
    # For each class x layer: collect D1 and D2 last-token hidden states
    # Use all gate battery sentences as the pole pool
    pole_hiddens: dict[str, dict[int, dict[int, list[np.ndarray]]]] = {
        cls: {pole: {li: [] for li in be.read_layers} for pole in (0, 1)}
        for cls in ("scope", "ana", "att")
    }
    for i, rec in enumerate(gate_recs):
        cls = rec["cls"]
        pole = rec["pole"]
        hs = be.prefill_hidden(rec["prompt"], be.read_layers)
        for li in be.read_layers:
            pole_hiddens[cls][pole][li].append(hs[li])
        if (i + 1) % 50 == 0:
            log(f"[ac] pole prefill {i + 1}/{len(gate_recs)}")

    # Class-level pole axis per (class, layer) and calibration stats
    pole_axes: dict[str, dict[int, np.ndarray]] = {}
    pole_calib: dict[str, dict[int, dict]] = {}
    for cls in ("scope", "ana", "att"):
        pole_axes[cls] = {}
        pole_calib[cls] = {}
        for li in be.read_layers:
            d1 = np.stack(pole_hiddens[cls][0][li]).astype(np.float64)
            d2 = np.stack(pole_hiddens[cls][1][li]).astype(np.float64)
            axis = d1.mean(axis=0) - d2.mean(axis=0)
            norm = np.linalg.norm(axis)
            axis = axis / max(norm, 1e-12)
            pole_axes[cls][li] = axis
            # Calibration: mean/std of D1 and D2 projections
            p1 = d1 @ axis
            p2 = d2 @ axis
            pole_calib[cls][li] = {
                "mean_d1": float(p1.mean()),
                "std_d1": float(p1.std()) + 1e-12,
                "mean_d2": float(p2.mean()),
                "std_d2": float(p2.std()) + 1e-12,
            }
    log("[ac] pole axes computed")

    # --- STEP 3: CALIBRATION GENERATIONS ---
    log("[ac] === STEP 3: calibration generations ===")
    # For each class, item, pole: k=2 continuations from pole frame 0
    items_by_class = {
        "scope": SCOPE_ITEMS[:n_items_per_class],
        "ana": ANA_ITEMS[:n_items_per_class],
        "att": ATT_ITEMS[:n_items_per_class],
    }
    prompt_fns = {
        "scope": lambda item, pole: _scope_prompt(item, pole, 0),
        "ana": lambda item, pole: _ana_prompt(item, pole, 0),
        "att": lambda item, pole: _att_prompt(item, pole, 0),
    }

    c0_results: dict[str, list[bool]] = {c: [] for c in ("scope", "ana", "att")}
    c2_d1_projs: dict[str, dict[int, list[float]]] = {
        c: {li: [] for li in be.read_layers} for c in ("scope", "ana", "att")
    }
    c2_d2_projs: dict[str, dict[int, list[float]]] = {
        c: {li: [] for li in be.read_layers} for c in ("scope", "ana", "att")
    }
    # ana only: accumulated mass diffs (best layer selected later)
    c3_diffs: list[float] = []

    calib_records: list[dict] = []

    for cls in ("scope", "ana", "att"):
        items = items_by_class[cls]
        for item_idx, item in enumerate(items):
            for pole in (0, 1):
                prompt = prompt_fns[cls](item, pole) + " That is,"
                samples = be.generate_with_capture(
                    prompt=prompt,
                    k=CALIB_K,
                    seed=args.seed + item_idx * 100 + pole * 10,
                    read_layers=be.read_layers,
                    capture_attn_for_names=None,
                    v_norms_by_layer=None,
                )
                expected = "D1" if pole == 0 else "D2"
                for s in samples:
                    text = "".join(s["token_texts"])
                    label = grade_continuation(cls, text, item)
                    correct = label == expected
                    c0_results[cls].append(correct)
                    # C2: project per-step hidden onto axis, collect per-layer
                    for li in be.read_layers:
                        axis = pole_axes[cls][li]
                        cal = pole_calib[cls][li]
                        for h in s["hidden_steps"].get(li, []):
                            proj = float(np.dot(h.astype(np.float64), axis))
                            if pole == 0:
                                c2_d1_projs[cls][li].append(proj)
                            else:
                                c2_d2_projs[cls][li].append(proj)

                    calib_records.append({
                        "cls": cls,
                        "item": item_idx,
                        "kind": "calib",
                        "pole": expected,
                        "label": label,
                        "seed": args.seed + item_idx * 100 + pole * 10,
                        "text": text,
                        "commit_step": None,
                        "first_cue_step": None,
                        "per_step_delta": [],
                    })

    # C0 accuracy per class
    c0_acc_per_cls: dict[str, float] = {
        cls: float(np.mean(hits)) if hits else 0.0
        for cls, hits in c0_results.items()
    }
    c0_pooled = float(np.mean([v for v in c0_acc_per_cls.values()]))
    log(f"[ac] C0 acc: {c0_acc_per_cls} pooled={c0_pooled:.3f} (need >= {C0_ACC})")

    # C2: per class, select best layer (max |mean_D1 - mean_D2|)
    c2_best_layer: dict[str, int] = {}
    c2_gates: dict[str, dict] = {}
    for cls in ("scope", "ana", "att"):
        best_li = be.read_layers[0]
        best_sep = -1.0
        for li in be.read_layers:
            d1p = c2_d1_projs[cls][li]
            d2p = c2_d2_projs[cls][li]
            if d1p and d2p:
                sep = abs(np.mean(d1p) - np.mean(d2p))
                if sep > best_sep:
                    best_sep = sep
                    best_li = li
        c2_best_layer[cls] = best_li
        gate = compute_c2_axis_sep(
            c2_d1_projs[cls][best_li], c2_d2_projs[cls][best_li]
        )
        c2_gates[cls] = {**gate, "best_layer": best_li}
        log(
            f"[ac] C2 {cls}: layer={best_li} "
            f"sep={gate.get('sep', 'N/A'):.4f} "
            f"p={gate.get('p', 1):.4f} "
            f"pass={gate['pass']}"
        )

    # --- STEP 4: A GENERATIONS ---
    log("[ac] === STEP 4: A generations ===")

    a_records: list[dict] = []
    traj_arrays: dict[str, np.ndarray] = {}  # key: f"{cls}-{item_idx}-{ki}"
    ana_mass_arrays: dict[str, np.ndarray] = {}

    # For C3 (ana) and tracking item-level labels
    labels_per_item_per_cls: dict[str, list[list[str | None]]] = {
        cls: [] for cls in ("scope", "ana", "att")
    }

    items_stats_per_cls: dict[str, list[dict]] = {
        cls: [] for cls in ("scope", "ana", "att")
    }
    # Tracks per-item sample lists for pooled class-level alignment test
    samples_per_item_per_cls: dict[str, list[list[dict]]] = {
        cls: [] for cls in ("scope", "ana", "att")
    }

    # det-repeat tracking
    det_item0_samples_run1: list[dict] | None = None
    det_dev: float | None = None

    for cls in ("scope", "ana", "att"):
        items = items_by_class[cls]
        cls_item_labels: list[list[str | None]] = []

        for item_idx, item in enumerate(items):
            # Build ambiguous A prompt
            if cls == "scope":
                a_str = _scope_a(item)
            elif cls == "ana":
                gender = ANA_GENDER[item_idx]
                a_str = _ana_a(item, gender)
            else:
                a_str = _att_a(item)

            prompt = elicit(a_str)

            # Prefill v_norms for ana attention mass
            v_norms = None
            name_positions: tuple[list[int], list[int]] | None = None
            if cls == "ana":
                n1, n2, _ = item
                v_norms = be.prefill_v_norms(prompt, be.read_layers)
                n1_toks, n2_toks = _find_name_token_positions(prompt, n1, n2, be.tok)
                name_positions = (n1_toks, n2_toks)

            # Generate K samples
            samples = be.generate_with_capture(
                prompt=prompt,
                k=k_samples,
                seed=(
                    args.seed
                    + item_idx * 1000
                    + {"scope": 0, "ana": 10000, "att": 20000}[cls]
                ),
                read_layers=be.read_layers,
                capture_attn_for_names=name_positions,
                v_norms_by_layer=v_norms,
            )

            # Det-repeat: item 0, sample 0
            if item_idx == 0 and cls == "scope":
                if det_item0_samples_run1 is None:
                    det_item0_samples_run1 = samples
                    # Re-run sample 0 to check determinism
                    det_samples2 = be.generate_with_capture(
                        prompt=prompt,
                        k=1,
                        seed=args.seed + 0,
                        read_layers=be.read_layers,
                        capture_attn_for_names=None,
                        v_norms_by_layer=None,
                    )
                    s1 = samples[0]
                    s2 = det_samples2[0]
                    ids_match = s1["token_ids"] == s2["token_ids"]
                    rl0 = be.read_layers[0]
                    if (
                        s1["hidden_steps"].get(rl0)
                        and s2["hidden_steps"].get(rl0)
                    ):
                        h1 = np.array(s1["hidden_steps"][rl0])
                        h2 = np.array(s2["hidden_steps"][rl0])
                        det_dev = (
                            float(np.max(np.abs(h1 - h2)))
                            if h1.shape == h2.shape
                            else None
                        )
                    else:
                        det_dev = None
                    log(f"[ac] det-repeat: ids_match={ids_match} value_dev={det_dev}")

            # Grade each sample
            best_li = c2_best_layer[cls]
            item_labels: list[str | None] = []

            item_sample_stats: list[dict] = []
            for ki, s in enumerate(samples):
                text = "".join(s["token_texts"])
                label = grade_continuation(cls, text, item)
                item_labels.append(label)

                # Per-step delta at best layer
                axis = pole_axes[cls][best_li]
                cal = pole_calib[cls][best_li]
                std_pool = (cal["std_d1"] + cal["std_d2"]) / 2
                delta_steps: list[float] = []
                mid = (cal["mean_d1"] + cal["mean_d2"]) / 2
                for h in s["hidden_steps"].get(best_li, []):
                    proj = float(np.dot(h.astype(np.float64), axis))
                    z = (proj - mid) / max(std_pool, 1e-12)
                    delta_steps.append(z)

                delta_arr = np.array(delta_steps)
                T = len(delta_arr)

                # Final alignment
                if T >= 3:
                    final_sign = np.sign(np.mean(delta_arr[-3:]))
                elif T > 0:
                    final_sign = np.sign(delta_arr[-1])
                else:
                    final_sign = 0.0
                expected_sign = 1.0 if label == "D1" else -1.0 if label == "D2" else 0.0
                final_aligned = bool(final_sign == expected_sign and label is not None)

                # Commit step
                if T > 0:
                    commit_step = _schmitt_commit(delta_arr, SCHMITT_WINDOW)
                else:
                    commit_step = None

                # First cue step
                first_cue_step = _first_cue_step_from_text(
                    s["token_texts"], label, cls, item
                )

                item_sample_stats.append({
                    "label": label,
                    "final_aligned": final_aligned,
                    "commit_step": commit_step,
                    "first_cue_step": first_cue_step,
                    "delta_steps": delta_steps,
                })

                # Store trajectories
                key = f"{cls}-{item_idx:02d}-{ki:02d}"
                traj_arrays[key] = delta_arr.astype(np.float32)

                # Ana mass arrays
                if cls == "ana":
                    mass_steps = s.get("attn_mass_steps", {}).get(best_li, [])
                    if mass_steps:
                        diffs = [m1 - m2 for m1, m2 in mass_steps]
                        ana_mass_arrays[f"ana-{item_idx:02d}-{ki:02d}"] = np.array(
                            diffs, dtype=np.float32
                        )
                        # C3 accumulation
                        if label is not None:
                            sign = 1.0 if label == "D1" else -1.0
                            c3_diffs.extend([sign * d for d in diffs])

                a_records.append({
                    "cls": cls,
                    "item": item_idx,
                    "kind": "A",
                    "label": label,
                    "seed": s["seed"],
                    "text": text,
                    "commit_step": commit_step,
                    "first_cue_step": first_cue_step,
                    "per_step_delta": [round(x, 4) for x in delta_steps],
                })

            cls_item_labels.append(item_labels)
            samples_per_item_per_cls[cls].append(item_sample_stats)

            # Compute per-item analysis stats
            istat = analyze_samples(
                item_sample_stats,
                cls, item,
                pole_axes[cls][best_li],
                pole_calib[cls][best_li]["mean_d1"],
                pole_calib[cls][best_li]["std_d1"],
                pole_calib[cls][best_li]["mean_d2"],
                pole_calib[cls][best_li]["std_d2"],
                best_li,
            )
            items_stats_per_cls[cls].append(istat)

        labels_per_item_per_cls[cls] = cls_item_labels

    # Free model memory
    log("[ac] freeing model memory")
    del be.model
    gc.collect()
    try:
        import torch
        torch.mps.empty_cache()
    except Exception:
        pass

    # --- ANALYSIS ---
    log("[ac] === ANALYSIS ===")
    c3_gate = compute_c3_ana_mass(c3_diffs)
    _c3_md = c3_gate.get("mean_diff")
    log(f"[ac] C3 ana mass: pass={c3_gate['pass']} mean_diff={_c3_md}")

    class_verdicts: dict[str, str] = {}
    class_gate_details: dict[str, dict] = {}
    for cls in ("scope", "ana", "att"):
        c1 = compute_c1_minority(labels_per_item_per_cls[cls])
        cls_align_rate, cls_align_p = compute_class_alignment(
            samples_per_item_per_cls[cls]
        )
        class_verdicts[cls] = per_class_verdict(
            items_stats_per_cls[cls],
            c0_acc_per_cls[cls],
            c2_gates[cls]["pass"],
            c1["fail_majority"],
            cls_align_rate=cls_align_rate,
            cls_align_p=cls_align_p,
        )
        class_gate_details[cls] = {
            "c0_acc": c0_acc_per_cls[cls],
            "c1": c1,
            "c2": c2_gates[cls],
            "cls_align_rate": cls_align_rate,
            "cls_align_p": cls_align_p,
            "verdict_class": class_verdicts[cls],
        }
        log(f"[ac] {cls}: verdict={class_verdicts[cls]}")

    gv = global_verdict(class_verdicts)
    log(f"[ac] GLOBAL VERDICT: {gv}")

    gates = {
        "c0_pooled": c0_pooled,
        "c0_per_class": c0_acc_per_cls,
        "c3_ana": c3_gate,
        "class_details": class_gate_details,
        "class_verdicts": class_verdicts,
        "global_verdict": gv,
        "det_dev": det_dev,
    }

    # Write outputs
    (out / "gates.json").write_text(json.dumps(gates, indent=2, default=_json_native))
    with (out / "results.jsonl").open("w") as fh:
        for r in calib_records + a_records:
            fh.write(json.dumps(r, default=_json_native) + "\n")
    npz_data: dict[str, np.ndarray] = {}
    npz_data.update(traj_arrays)
    npz_data.update(ana_mass_arrays)
    np.savez_compressed(out / "trajectories.npz", **npz_data)

    try:
        import torch
        import transformers
        lib_versions = {
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "numpy": np.__version__,
        }
    except ImportError:
        lib_versions = {"numpy": np.__version__}

    write_meta(out, args, len(gate_recs), bhash, gates, lib_versions)
    log(f"[ac] wrote {out}/")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model-id", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return run_validate(args)
    return run_real(args)


if __name__ == "__main__":
    raise SystemExit(main())
