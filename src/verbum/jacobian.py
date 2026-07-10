"""Input-attribution Jacobian — reading combinator OPCODES as routing structure.

Thesis (AGENTS.md S5 + the J-space discussion): an opcode is *how arguments
route to the output*, and that is exactly what a Jacobian measures. The
tractable, position-space read of that routing Jacobian is **input
attribution** — the gradient of a target prediction w.r.t. the input embedding
at each source position:

    infl[p] = || ∂ logit(target) / ∂ embed[p] ||

Each combinator makes a DIFFERENT structural prediction about the shape of
``infl`` over source positions (this is the "opcode = Jacobian pattern" claim
made empirical):

    K  select/discard      → CONCENTRATION  (mass on few positions; discard the rest)
    I  identity/copy        → COPY-MASS      (mass on repeated / copied-from tokens)
    B  compose/nest         → RANGE          (long-range, mediated dependence)
    C  flip/permute         → FRONT-BIAS     (argument-role order shifted vs canonical)
    S  share/duplicate      → (none clean; a LINEAR read under-reads argument sharing —
                               the second-order/duplication term is invisible to a
                               first-order Jacobian. Predicted flat/braided.)

This is the OPERATOR projection of the same object Anthropic's J-lens reads as
the OPERAND projection (J-space = the verbalizable live subspace). We read the
routing STRUCTURE; they read the token image.

Model-agnostic (uses ``get_input_embeddings`` + ``inputs_embeds``). Requires
grad (no ``torch.no_grad``). License: MIT.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np
import torch
from torch import nn

__all__ = [
    "attr_range",
    "concentration",
    "copy_mass",
    "front_bias",
    "input_attribution",
    "self_test",
]


# ── the routing Jacobian (position-space input attribution) ──────────────────


def input_attribution(
    model: nn.Module,
    tokenizer: Any,
    text: str,
    *,
    target_pos: int = -1,
    target_token: int | None = None,
) -> tuple[np.ndarray, np.ndarray, list[str], int]:
    """Per-source-position influence on the prediction at ``target_pos``.

    Returns ``(influence[seq], input_ids[seq], token_strs, target_token)`` where
    ``influence[p] = ||∂ logit(target_token @ target_pos) / ∂ embed[p]||``.
    ``target_token`` defaults to the model's own argmax at ``target_pos`` (attribute
    the behavior the model actually produces).
    """
    dev = next(model.parameters()).device
    enc = tokenizer(text, return_tensors="pt").to(dev)
    ids = enc["input_ids"]
    seq = ids.shape[1]
    tp = target_pos % seq
    emb = model.get_input_embeddings()(ids).detach().clone().requires_grad_(True)
    kw = {k: v for k, v in enc.items() if k != "input_ids"}
    logits = model(inputs_embeds=emb, **kw).logits  # (1, seq, vocab)
    if target_token is None:
        target_token = int(logits[0, tp].argmax())
    score = logits[0, tp, target_token]
    (grad,) = torch.autograd.grad(score, emb)
    infl = grad[0].float().norm(dim=-1).detach().cpu().numpy()  # (seq,)
    toks = [tokenizer.decode([int(i)]) for i in ids[0].tolist()]
    return infl, ids[0].detach().cpu().numpy(), toks, target_token


# ── structural read metrics (each keyed to one combinator signature) ─────────


def _prob(attr: np.ndarray) -> np.ndarray:
    a = np.clip(attr.astype(np.float64), 0, None)
    s = a.sum()
    return a / s if s > 1e-12 else np.full_like(a, 1.0 / max(1, len(a)))


def concentration(attr: np.ndarray) -> float:
    """K-signature: 1 - normalized entropy (1 = single position, 0 = uniform)."""
    p = _prob(attr)
    n = len(p)
    if n <= 1:
        return 1.0
    ent = -(p * np.log(p + 1e-12)).sum()
    return float(1.0 - ent / np.log(n))


def copy_mass(attr: np.ndarray, ids: np.ndarray) -> float:
    """I-signature: fraction of attribution mass on REPEATED tokens (copy sources)."""
    c = Counter(int(t) for t in ids)
    rep = np.array([1.0 if c[int(t)] > 1 else 0.0 for t in ids])
    return float((_prob(attr) * rep).sum())


def attr_range(attr: np.ndarray, target_pos: int) -> float:
    """B-signature: attribution-weighted mean |distance| to the target position."""
    p = _prob(attr)
    n = len(p)
    tp = target_pos % n
    idx = np.arange(n)
    return float((p * np.abs(idx - tp)).sum() / max(1, n - 1))  # normalized 0..1


def front_bias(attr: np.ndarray) -> float:
    """C-signature: attribution center-of-mass position (0 = front, 1 = back)."""
    p = _prob(attr)
    n = len(p)
    if n <= 1:
        return 0.5
    idx = np.arange(n)
    return float((p * idx).sum() / (n - 1))


METRICS = {
    "concentration": lambda attr, ids, tp: concentration(attr),
    "copy_mass": lambda attr, ids, tp: copy_mass(attr, ids),
    "range": lambda attr, ids, tp: attr_range(attr, tp),
    "front_bias": lambda attr, ids, tp: front_bias(attr),
}
# which metric each combinator predicts (the diagonal of the opcode x metric matrix)
PREDICTED = {"K": "concentration", "I": "copy_mass", "B": "range", "C": "front_bias"}


# ── self-test: validate metrics on ideal synthetic attributions ──────────────


def self_test() -> dict[str, Any]:
    """Unit-check the structural metrics recover their ideal signatures."""
    n = 10
    one_hot = np.zeros(n)
    one_hot[3] = 1.0
    uniform = np.ones(n)

    # concentration: one-hot ~ 1, uniform ~ 0
    c_one = concentration(one_hot)
    c_uni = concentration(uniform)

    # copy_mass: attribution on a repeated token vs a unique token
    ids = np.array([5, 6, 7, 5, 8, 9, 5, 10, 11, 12])  # token 5 repeats at 0,3,6
    on_rep = np.zeros(n)
    on_rep[[0, 3, 6]] = 1.0
    on_uni = np.zeros(n)
    on_uni[[1, 4, 8]] = 1.0
    cm_rep = copy_mass(on_rep, ids)
    cm_uni = copy_mass(on_uni, ids)

    # range: far-from-target vs near-target (target = last)
    far = np.zeros(n)
    far[0] = 1.0
    near = np.zeros(n)
    near[n - 1] = 1.0
    r_far = attr_range(far, -1)
    r_near = attr_range(near, -1)

    # front_bias: mass at front vs back
    fb_front = front_bias(one_hot)  # pos 3 -> < 0.5
    back = np.zeros(n)
    back[n - 1] = 1.0
    fb_back = front_bias(back)  # = 1.0

    checks = {
        "concentration_onehot>0.99": c_one > 0.99,
        "concentration_uniform<0.01": c_uni < 0.01,
        "copy_mass_rep>uni": cm_rep > cm_uni and cm_rep > 0.99,
        "range_far>near": r_far > r_near and r_near < 1e-9,
        "front_bias_front<back": fb_front < fb_back,
    }
    return {
        "values": {
            "conc_onehot": round(c_one, 4), "conc_uniform": round(c_uni, 4),
            "copy_rep": round(cm_rep, 4), "copy_uni": round(cm_uni, 4),
            "range_far": round(r_far, 4), "range_near": round(r_near, 4),
            "front": round(fb_front, 4), "back": round(fb_back, 4),
        },
        "checks": checks,
        "all_pass": all(checks.values()),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(self_test(), indent=2))
