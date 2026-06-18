"""Verifiable reward — the kernel as an RLVR reward function (spliced-reward, §2/§4/§5).

THE ROLE (session 241). `spliced-reward-vsm-kernel.md` says: the constructed kernel is
a *perfect verifier*, and a verifier is a *verifiable reward* (RLVR). Because the
kernel is DISCRETE, policy-gradient (GRPO-style) scores rollouts without backprop
through the reward — the v12-v15 gradient-death is sidestepped, the discreteness is a
FEATURE. This module is the canonical reward spec: it generalises the s226
reduction-equality grader (buried in `scripts/experiments/compile_frontend.py`) into
the package, CPU-only, no torch.

TWO REGISTERS (the reward is parser-agnostic):

    applicative : `lambda_ast.parse`        — the compile_frontend register (juxtaposed
                                              combinator/expression terms `f (g x)`)
    surface     : `lambda_surface.to_kernel` — the canonical-corpus register (surface
                                              FOL/λ: `∀x. artist(x) → knows(x, baker)`)

Both end at a kernel `Term` → reduce → normal form → compare to the gold NF. Reduction-
equality is REPRESENTATION-INVARIANT (`f (g x)` and `B f g x` both accepted) — reward
the WHAT (the normal form), free the HOW (every combinator path).

THE CHANNELS (§2) ARE VSM LAYER STATES — the forward pass observed at the right
registers, not bolted on:

    parsed            — (input gate)  did parse/lower succeed
    well_typed   S2   — did the CCG typecheck pass (IllTyped → False)
    halts_in_budget  S4/S3  — reduce reached NORMAL_FORM within the step/size budget
    size_ok      S3   — the normal form is no larger than the (canonical) target
    reduces_correct  S5  — NF == target  (the ANCHOR — exact-by-construction)
    trace_prefix_frac  S1  — fraction of the certified `fired_sequence` matched

ANCHOR vs POTENTIAL (§5). `reduces_correct` is the exact, constructed ANCHOR — it
defines correctness and owns the optimum. The other channels are dense partial-credit
signals; when read off a *learned* policy they over-read (s202/s204/s240) and must be
confined to the potential (shaping) channel — see `potential` / `shaped_reward`
(spliced-reward §4). The scalar OUTCOME reward `R_parent` is `reduces_correct` alone.

License: MIT. AGENTS.md S5 λ provenance (kernel = constructed verifier, MIT).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from verbum.lambda_ast import (
    MAX_SIZE,
    MAX_STEPS,
    Status,
    Term,
    _alpha_eq,  # structural equality of normal forms — the kernel's verifier core
    fired_sequence,
    normal_form,
    parse,
    pretty,
    reduce,
    size,
    typecheck,
)
from verbum.lambda_surface import SurfaceError, to_kernel

__all__ = [
    "DEFAULT_WEIGHTS",
    "POTENTIAL_WEIGHTS",
    "ParseStrategy",
    "ProcessStep",
    "RewardChannels",
    "RewardConfig",
    "RewardResult",
    "ShapedReturn",
    "TreeReward",
    "channels",
    "dense_reward",
    "potential",
    "reward",
    "shaped_return",
    "shaping",
    "to_term",
    "tree_process_reward",
    "verifiable_reward",
]

# A parse strategy is either a named register or a custom callable str -> Term
# (AGENTS.md λ extend: open slot > closed dispatch — pass your own lowerer).
ParseStrategy = str | Callable[[str], Term]

_NAMED_PARSERS: dict[str, Callable[[str], Term]] = {
    "applicative": parse,   # juxtaposed combinator/expression terms
    "surface": to_kernel,   # surface FOL/λ → kernel Term (bracket abstraction)
}

# Default dense-aggregate weights. Anchor-heavy (reduces_correct dominates); the rest
# are partial credit. Sum to 1.0 so a fully-correct output scores dense == 1.0.
DEFAULT_WEIGHTS: dict[str, float] = {
    "parsed": 0.10,
    "well_typed": 0.15,
    "halts_in_budget": 0.15,
    "size_ok": 0.10,
    "reduces_correct": 0.40,
    "trace_prefix_frac": 0.10,
}


def to_term(s: str, strategy: ParseStrategy) -> Term:
    """Parse a candidate string into a kernel Term under the chosen register.

    Raises (ValueError/SurfaceError/...) on a bad parse — the caller treats any
    exception as `parsed=False` (a compile failure, reward 0 on the anchor).
    """
    if callable(strategy):
        return strategy(s)
    try:
        fn = _NAMED_PARSERS[strategy]
    except KeyError:
        raise ValueError(
            f"unknown parse strategy {strategy!r}; "
            f"expected one of {sorted(_NAMED_PARSERS)} or a callable"
        ) from None
    return fn(s)


@dataclass(frozen=True, slots=True)
class RewardChannels:
    """The per-channel verdicts (§2). Booleans are exact; trace_prefix_frac ∈ [0,1]."""

    parsed: bool
    well_typed: bool
    halts_in_budget: bool
    size_ok: bool
    reduces_correct: bool
    trace_prefix_frac: float
    # diagnostics (not reward channels) — for logging / failure taxonomy
    nf: str | None = None
    steps: int | None = None
    status: str | None = None
    error: str | None = None

    def as_scores(self) -> dict[str, float]:
        """The six channels as floats in [0,1] (booleans → 0.0/1.0)."""
        return {
            "parsed": float(self.parsed),
            "well_typed": float(self.well_typed),
            "halts_in_budget": float(self.halts_in_budget),
            "size_ok": float(self.size_ok),
            "reduces_correct": float(self.reduces_correct),
            "trace_prefix_frac": float(self.trace_prefix_frac),
        }


@dataclass(frozen=True, slots=True)
class RewardConfig:
    """Reward spec: parse register, budgets, type env, dense-aggregate weights."""

    parse: ParseStrategy = "surface"
    max_steps: int = MAX_STEPS
    size_budget: int = MAX_SIZE
    type_env: dict[str, object] | None = None
    weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))


@dataclass(frozen=True, slots=True)
class RewardResult:
    """The full reward read: the outcome anchor + dense aggregate + channels."""

    reward: float            # R_parent — the OUTCOME anchor (reduces_correct ∈ {0,1})
    dense: float             # weighted multi-channel partial credit ∈ [0,1]
    channels: RewardChannels


def _trace_prefix_frac(cand_seq: list[str], gold_seq: list[str]) -> float:
    """Fraction of a REFERENCE opcode trace the candidate matches as a prefix.

    The S1 process channel: how far along a reference `fired_sequence` the candidate's
    own reduction agrees. 1.0 when the candidate walks the whole reference as a prefix;
    0.0 when the first step diverges. NEUTRAL (1.0) when there is NO reference trace —
    e.g. the gold is already a normal form (no redexes to fire), so there is nothing to
    constrain and a correct candidate must not be penalised. The channel only bites when
    an explicit non-trivial reference trace is supplied (the combinator/reduction
    register; on the surface corpus, gold is near-NF so this channel is mostly neutral,
    exactly the faint S1 trace-align of spliced-reward §5).

    Diagnostic / shaping only — order, not outcome; the outcome is reduction-equality,
    which is representation-invariant.
    """
    if not gold_seq:
        return 1.0  # no reference trace → no constraint (neutral)
    matched = 0
    for a, b in zip(cand_seq, gold_seq, strict=False):
        if a != b:
            break
        matched += 1
    return matched / len(gold_seq)


def _resolve_term(state: str | Term, config: RewardConfig) -> Term:
    """A rollout state is either a surface/applicative string or an already-parsed Term.

    Strings are parsed under `config.parse`; Terms pass through (e.g. the intermediate
    terms of a reduction trace, used by the potential / tree process reward).
    """
    if isinstance(state, str):
        return to_term(state, config.parse)
    return state


def channels(
    candidate: str | Term, gold_nf: str, config: RewardConfig
) -> RewardChannels:
    """Read all §2 reward channels for one candidate against the gold normal form.

    `gold_nf` is a kernel-term string already in (or reducible to) normal form — e.g.
    the corpus row's precomputed `normal_form`. The candidate is a surface/applicative
    string parsed under `config.parse`, or an already-parsed Term (a reduction-trace
    state). Any parse/lower failure → parsed=False and every downstream channel False
    (a compile failure, anchor reward 0).
    """
    # gold is kernel-language; parse + normalise it (idempotent if already NF).
    gold_term = parse(gold_nf)
    gold_nf_term = normal_form(gold_term, max_steps=config.max_steps)
    gold_seq = fired_sequence(gold_term, max_steps=config.max_steps)
    gold_size = size(gold_nf_term)

    # candidate
    try:
        cand = _resolve_term(candidate, config)
    except (ValueError, SurfaceError, KeyError, RecursionError, IndexError) as ex:
        return RewardChannels(
            parsed=False, well_typed=False, halts_in_budget=False, size_ok=False,
            reduces_correct=False, trace_prefix_frac=0.0,
            nf=None, steps=None, status=None, error=f"{type(ex).__name__}: {ex}",
        )

    tc = typecheck(cand, config.type_env)  # type: ignore[arg-type]
    red = reduce(cand, max_steps=config.max_steps, max_size=config.size_budget)
    halts = red.status is Status.NORMAL_FORM
    cand_nf = red.normal_form
    cand_size = size(cand_nf)
    size_ok = halts and cand_size <= gold_size
    # reduction-equality (the anchor): candidate's NF structurally equals gold's NF.
    reduces_correct = halts and _alpha_eq(cand_nf, gold_nf_term)
    cand_seq = fired_sequence(cand, max_steps=config.max_steps)
    trace_frac = _trace_prefix_frac(cand_seq, gold_seq)

    return RewardChannels(
        parsed=True,
        well_typed=tc.ok,
        halts_in_budget=halts,
        size_ok=size_ok,
        reduces_correct=reduces_correct,
        trace_prefix_frac=trace_frac,
        nf=pretty(cand_nf),
        steps=red.steps,
        status=red.status.value,
        error=None,
    )


def dense_reward(ch: RewardChannels, weights: dict[str, float] | None = None) -> float:
    """Weighted multi-channel partial credit ∈ [0,1] (normalised by Σweights).

    Dense / diagnostic / shaping signal — NOT the outcome. The outcome is the anchor
    `reduces_correct` (see `verifiable_reward`). With DEFAULT_WEIGHTS a fully-correct
    output scores 1.0 and a parse failure scores 0.0.
    """
    w = weights if weights is not None else DEFAULT_WEIGHTS
    scores = ch.as_scores()
    total = sum(w.get(k, 0.0) for k in scores)
    if total == 0.0:
        return 0.0
    return sum(w.get(k, 0.0) * v for k, v in scores.items()) / total


def verifiable_reward(
    candidate: str | Term, gold_nf: str, config: RewardConfig | None = None
) -> float:
    """R_parent — the OUTCOME reward: 1.0 iff the candidate reduces to the gold NF.

    Exact, terminal, representation-invariant — the s226 verifier as a scalar reward.
    This is the channel that owns the optimum (spliced-reward §4); everything else is
    shaping.
    """
    cfg = config or RewardConfig()
    return float(channels(candidate, gold_nf, cfg).reduces_correct)


def reward(
    candidate: str | Term, gold_nf: str, config: RewardConfig | None = None
) -> RewardResult:
    """Full reward read: outcome anchor (R_parent) + dense aggregate + channels."""
    cfg = config or RewardConfig()
    ch = channels(candidate, gold_nf, cfg)
    return RewardResult(
        reward=float(ch.reduces_correct),
        dense=dense_reward(ch, cfg.weights),
        channels=ch,
    )


# --------------------------------------------------------------------------- #
# §4 — THE SPLICE: parent outcome ⊗ inline process                            #
#                                                                             #
# R_parent (above) is the exact terminal anchor. The inline process reward is #
# cast as a POTENTIAL and spliced via the potential-DIFFERENCE form so it can #
# only guide the path, never move the optimum (Ng-Harada-Russell 1999). The   #
# safety is ENTIRELY in the difference form — a raw additive bonus Goodharts. #
# --------------------------------------------------------------------------- #

# Φ_inline weights (§4a). The S1 trace channel is neutral on the surface corpus
# (gold near-NF), so the monotone signal during reduction is carried by typed +
# nf_proximity. All in [0,1]; weights sum to 1 → Φ ∈ [0,1].
POTENTIAL_WEIGHTS: dict[str, float] = {
    "trace": 0.40,
    "typed": 0.20,
    "nf_proximity": 0.40,
}


def potential(
    state: str | Term,
    gold_nf: str,
    config: RewardConfig | None = None,
    *,
    weights: dict[str, float] | None = None,
    gold_trace: list[str] | None = None,
) -> float:
    """Φ_inline(state) ∈ [0,1] — the inline process potential (spliced-reward §4a).

    A deterministic, bounded function of a rollout state (a surface/applicative string
    or a partial/intermediate Term). Combines: distance along an optional reference
    `gold_trace` (S1), well-typed-so-far (S2), and normal-form proximity in size to the
    gold NF (S3/S5). Climbs to 1.0 at the correct normal form. An unparseable state → 0.

    This is the OVER-READABLE estimate; it is only ever consumed through the
    potential-DIFFERENCE form (`shaping` / `shaped_return`), where the invariance
    guarantees it cannot corrupt 'correct'.
    """
    cfg = config or RewardConfig()
    w = weights if weights is not None else POTENTIAL_WEIGHTS
    gold_term = parse(gold_nf)
    gold_nf_term = normal_form(gold_term, max_steps=cfg.max_steps)
    gold_size = max(size(gold_nf_term), 1)
    ref_trace = gold_trace if gold_trace is not None else fired_sequence(
        gold_term, max_steps=cfg.max_steps
    )
    try:
        t = _resolve_term(state, cfg)
    except (ValueError, SurfaceError, KeyError, RecursionError, IndexError):
        return 0.0
    tc = typecheck(t, cfg.type_env)  # type: ignore[arg-type]
    red = reduce(t, max_steps=cfg.max_steps, max_size=cfg.size_budget)
    halts = red.status is Status.NORMAL_FORM
    cand_seq = fired_sequence(t, max_steps=cfg.max_steps)
    trace_frac = _trace_prefix_frac(cand_seq, ref_trace)
    nf_prox = (
        max(0.0, 1.0 - abs(size(red.normal_form) - gold_size) / gold_size)
        if halts
        else 0.0
    )
    phi = (
        w["trace"] * trace_frac
        + w["typed"] * float(tc.ok)
        + w["nf_proximity"] * nf_prox
    )
    return max(0.0, min(1.0, phi))


def shaping(
    prev: str | Term,
    nxt: str | Term,
    gold_nf: str,
    config: RewardConfig | None = None,
    *,
    gamma: float = 1.0,
    weights: dict[str, float] | None = None,
    gold_trace: list[str] | None = None,
) -> float:
    """The single-transition shaping reward F = γ·Φ(nxt) − Φ(prev) (§4a).

    THE potential-difference form — the ONLY form with the optimal-policy invariance.
    A raw additive Φ(nxt) bonus does NOT have it (the §4a TRAP).
    """
    cfg = config or RewardConfig()
    phi_next = potential(nxt, gold_nf, cfg, weights=weights, gold_trace=gold_trace)
    phi_prev = potential(prev, gold_nf, cfg, weights=weights, gold_trace=gold_trace)
    return gamma * phi_next - phi_prev


@dataclass(frozen=True, slots=True)
class ShapedReturn:
    """A spliced rollout return: terminal outcome + telescoping shaping (§4a)."""

    outcome: float       # R_parent at the terminal state (anchor ∈ {0,1})
    shaping_sum: float   # Σ_t γ^t (γΦ(s_{t+1}) − Φ(s_t))  — the discounted shaping
    total: float         # outcome + shaping_sum  — the spliced return
    telescoped: float    # γ^T·Φ(s_T) − Φ(s_0)  — what shaping_sum MUST equal (§4a)


def shaped_return(
    states: list[str | Term],
    gold_nf: str,
    config: RewardConfig | None = None,
    *,
    gamma: float = 1.0,
    weights: dict[str, float] | None = None,
    gold_trace: list[str] | None = None,
) -> ShapedReturn:
    """Splice R_parent (terminal outcome) with the telescoping inline shaping (§4a).

    `states` is the rollout trajectory s_0 … s_T (generation states, or — for the CPU
    scaffold — a reduction trace). The shaping channel is the discounted sum of
    potential differences, which telescopes to γ^T·Φ(s_T) − Φ(s_0): it depends ONLY on
    the endpoints, so any over-read in Φ along the path cancels. The optimum is owned by
    `outcome` alone. The `telescoped` field is the invariance witness — it must equal
    `shaping_sum` (asserted in tests).
    """
    if not states:
        raise ValueError("shaped_return: need at least one state")
    cfg = config or RewardConfig()
    phis = [
        potential(s, gold_nf, cfg, weights=weights, gold_trace=gold_trace)
        for s in states
    ]
    shaping_sum = sum(
        gamma**t * (gamma * phis[t + 1] - phis[t]) for t in range(len(phis) - 1)
    )
    big_t = len(phis) - 1
    telescoped = gamma**big_t * phis[-1] - phis[0]
    outcome = float(channels(states[-1], gold_nf, cfg).reduces_correct)
    return ShapedReturn(
        outcome=outcome,
        shaping_sum=shaping_sum,
        total=outcome + shaping_sum,
        telescoped=telescoped,
    )


# --------------------------------------------------------------------------- #
# §4c — the verbum-native splice: reward along the certified reduction tree    #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class ProcessStep:
    """One node of the certified reduction tree — a ground-truth process reward."""

    index: int               # step position in the certified fired_sequence
    opcode: str              # which combinator the kernel fired (B,K,C,…)
    delta_potential: float   # Φ(s_{i+1}) − Φ(s_i) — this rewrite's progress to the NF
    reward: float            # max(0, delta_potential) — the dense per-step credit


@dataclass(frozen=True, slots=True)
class TreeReward:
    """Reduction-tree-structured credit (§4c): root outcome + per-node process reward.

    The kernel emits the WHOLE certified reduction trace (`fired_sequence`) — each fired
    step is a kernel-certified rewrite. This is the ground-truth PRM a learned PRM only
    approximates: root = R_parent outcome, each node = an exact process reward. On the
    surface corpus the gold is near-NF so most candidates have an empty trace (the
    tree is just the root); per-step structure shows in the reduction register.
    """

    outcome: float                 # R_parent at the root (reduces_correct ∈ {0,1})
    steps: list[ProcessStep]       # one per fired step, aligned to fired_sequence
    potentials: list[float]        # Φ at each reduction-trace term (len = steps + 1)


def tree_process_reward(
    candidate: str | Term,
    gold_nf: str,
    config: RewardConfig | None = None,
    *,
    weights: dict[str, float] | None = None,
    gold_trace: list[str] | None = None,
) -> TreeReward:
    """Walk the candidate's certified reduction tree, scoring each fired step (§4c).

    Each step's process reward is the potential increment toward the gold NF as the
    kernel fires that combinator — a dense, ground-truth credit signal aligned 1:1 to
    `lambda_ast.fired_sequence`. The root is the exact outcome anchor.
    """
    cfg = config or RewardConfig()
    try:
        t = _resolve_term(candidate, cfg)
    except (ValueError, SurfaceError, KeyError, RecursionError, IndexError):
        return TreeReward(outcome=0.0, steps=[], potentials=[0.0])
    red = reduce(t, max_steps=cfg.max_steps, max_size=cfg.size_budget)
    cand_seq = fired_sequence(t, max_steps=cfg.max_steps)
    phis = [
        potential(term, gold_nf, cfg, weights=weights, gold_trace=gold_trace)
        for term in red.trace
    ]
    steps: list[ProcessStep] = []
    for i, op in enumerate(cand_seq):
        dphi = phis[i + 1] - phis[i] if i + 1 < len(phis) else 0.0
        steps.append(
            ProcessStep(
                index=i, opcode=op, delta_potential=dphi, reward=max(0.0, dphi)
            )
        )
    outcome = float(channels(t, gold_nf, cfg).reduces_correct)
    return TreeReward(outcome=outcome, steps=steps, potentials=phis)
