#!/usr/bin/env python3
# register: functional (capability/usage — held-out generalization)
"""Exposure/format sweep — "training as a photograph" (session 229).

THE IDEA (Michael): a training step is an EXPOSURE to one "photograph". Many
exposures to the same β-reduction should converge faster than one. BUT the
metaphor has a fork that must be controlled or it measures the wrong thing:

  kx SAME EXACT instance      -> burns in THAT instance   -> MEMORIZATION
                                 (train loss falls, held-out flat)
  kx VARIED instances of the  -> burns in the INVARIANT   -> GENERALIZATION
  SAME RULE (same skeleton,      = the RULE itself          (each instance = the
  different atoms)                                           same object from a new
                                                             ANGLE; the hologram
                                                             forms only if angles
                                                             differ)

CROSSED DESIGN (resolves full-trace vs redex->NF AT THE SAME TIME):
  Axis 1  FORMAT (content per photograph)
    full_trace : every intermediate β-step  = long-exposure photo (move visible)
    redex_nf   : input -> normal form only   = single sharp snapshot (no motion)
  Axis 2  MULTIPLICITY
    one        : 1 instance / rule, seen 1x
    k_same     : 1 instance / rule, seen k x      (MEMORIZATION control)
    k_varied   : k DISTINCT instances / rule, 1x  (true burn-in: many angles)

METRIC: held-out generalization. The eval is FORMAT-INDEPENDENT — for an unseen
instance built from HELD-OUT atoms, greedily derive from "input -> " and check the
FINAL segment equals the true normal form (exact match). A full_trace model walks
the steps then emits the NF; a redex_nf model must leap to it. Either way we ask:
does the model produce the correct normal form for an instance it never saw, built
from atoms it was never trained on? Memorization (k_same) cannot pass this.

FALSIFIABLE PREDICTIONS:
  burn-in real : k_varied reaches held-out generalization faster than one;
                 k_same saturates early and stays LOW on held-out (rote).
  format trade : full_trace = info-rich long exposure (fewer distinct instances
                 needed); redex_nf = cheap snapshot (more angles needed). Honest
                 comparison is PER-TOKEN — full_trace photos cost more bytes each
                 (corpus_bytes reported). The crossover (full_trace wins low-budget,
                 redex_nf wins high) would itself be the finding.

Data is kernel-minted (lambda_ast.reduce) — exact, Church-Rosser, free.

Usage:
  uv run python scripts/experiments/exposure_format_sweep.py --smoke
  uv run python scripts/experiments/exposure_format_sweep.py --steps 4000 --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))
sys.path.insert(0, str(_SCRIPT_DIR))

# reuse the tiny byte-level student + vocab (one model definition, no fork)
from relational_loss_distillation import VOCAB, TinyLM  # noqa: E402

from verbum.lambda_ast import Status, parse, pretty, reduce  # noqa: E402

RESULTS_DIR = _PROJECT_ROOT / "results" / "exposure-format-sweep"

# Hand-curated multi-step skeletons (holes _0.._n filled with atoms). Each is
# VALIDATED at load: must reduce to NORMAL_FORM in >=2 steps. Mis-reasoned ones
# are dropped with a warning rather than crashing.
SKELETONS: list[str] = [
    "C K _0 _1",          # -> _1            (2 steps)
    "W K _0",             # -> _0            (2)
    "S K _0 _1",          # -> _1            (2)
    "S K K _0",           # -> _0            (2)
    "B I I _0",           # -> _0            (3)
    "B K I _0 _1",        # -> _0            (3)
    "W (K _0) _1",        # -> _0 _1         (2)
    "C B _0 _1 _2",       # -> _1 (_0 _2)    (2)
    "D I I I _0",         # -> _0            (4)
    "B (B _0) _1 _2 _3",  # -> _0 (_1 _2 _3) (2)
    "S (K _0) I _1",      # -> _0 _1         (3)
    "S B K _0 _1",        # -> _0 _0         (3)
    "C I _0 _1",          # -> _1 _0         (2)
]

TRAIN_ATOMS = list("abcdefghijklm")   # 13 — angles the model trains on
TEST_ATOMS = list("nopqrstuvwxyz")    # 13 — disjoint held-out angles
ARROW = " -> "
NEWLINE_BYTE = 10
MAX_NEW = 110


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# --------------------------------------------------------------------------- #
# Data minting (kernel oracle)                                                 #
# --------------------------------------------------------------------------- #
def n_holes(template: str) -> int:
    idx = [int(m) for m in re.findall(r"_(\d+)", template)]
    return (max(idx) + 1) if idx else 0


def fill(template: str, combo: tuple[str, ...]) -> str:
    return re.sub(r"_(\d+)", lambda m: combo[int(m.group(1))], template)


def reduce_strs(input_str: str) -> tuple[list[str], str, int, str]:
    """Return (trace_strs, normal_form_str, n_steps, status)."""
    red = reduce(parse(input_str))
    return [pretty(x) for x in red.trace], pretty(red.normal_form), red.steps, \
        red.status.value


def validate_skeletons(skeletons: list[str]) -> list[tuple[str, int]]:
    """Keep skeletons that reduce to a normal form in >=2 steps (full_trace and
    redex_nf must DIFFER). Returns (template, n_holes) for the survivors."""
    out: list[tuple[str, int]] = []
    for tmpl in skeletons:
        h = n_holes(tmpl)
        probe = fill(tmpl, tuple(TRAIN_ATOMS[:h]))
        try:
            trace, _nf, steps, status = reduce_strs(probe)
        except Exception as e:
            log(f"  DROP {tmpl!r}: parse/reduce error {e}")
            continue
        if status != Status.NORMAL_FORM.value:
            log(f"  DROP {tmpl!r}: status={status} (not normal form)")
            continue
        if steps < 2 or len(trace) < 3:
            log(f"  DROP {tmpl!r}: only {steps} step(s) (full_trace==redex_nf)")
            continue
        out.append((tmpl, h))
    return out


def make_fillings(rng: np.random.Generator, h: int, atoms: list[str],
                  k: int) -> list[tuple[str, ...]]:
    """k DISTINCT fillings; atoms within a term are distinct (sampled w/o repl)."""
    seen: set[tuple[str, ...]] = set()
    out: list[tuple[str, ...]] = []
    guard = 0
    while len(out) < k and guard < 10000:
        guard += 1
        combo = tuple(rng.choice(atoms, size=h, replace=False).tolist()) if h \
            else ()
        if combo not in seen:
            seen.add(combo)
            out.append(combo)
    return out


def render(template: str, combo: tuple[str, ...], fmt: str) -> str:
    trace, nf, _steps, _status = reduce_strs(fill(template, combo))
    if fmt == "redex_nf":
        return f"{trace[0]}{ARROW}{nf}"
    return ARROW.join(trace)


def build_corpus(rules: list[tuple[str, int]], train_fillings: dict[str, list],
                 fmt: str, mult: str, k: int, rng: np.random.Generator) -> str:
    """Assemble the training corpus for one (format, multiplicity) arm.

    one/k_same share fillings[0] so k_same is literally 'one repeated k times'."""
    sentences: list[str] = []
    for tmpl, _h in rules:
        fillings = train_fillings[tmpl]
        if mult == "one":
            chosen = [fillings[0]]
        elif mult == "k_same":
            chosen = [fillings[0]] * k
        else:  # k_varied
            chosen = fillings[:k]
        for combo in chosen:
            sentences.append(render(tmpl, combo, fmt))
    order = rng.permutation(len(sentences))
    return "\n".join(sentences[i] for i in order) + "\n"


def build_eval_items(rules: list[tuple[str, int]], m: int,
                     rng: np.random.Generator, atoms: list[str],
                     exclude: dict[str, list] | None = None
                     ) -> list[tuple[str, str]]:
    """Held-out (input, normal_form) pairs.

    heldout='combos' (default): atoms = TRAIN_ATOMS, but combos EXCLUDED from the
      training fillings -> isolates RULE generalization (the burn-in question) from
      symbol-copying. This is the right barrier (s229 diagnostic: tiny byte model
      reaches 0.365 here, 0.000 on disjoint atoms = a variable-binding failure, not
      a rule failure).
    heldout='atoms': atoms = TEST_ATOMS (disjoint) -> the SEPARATE, harder
      systematic/variable-binding generalization question.
    """
    exclude = exclude or {}
    items: list[tuple[str, str]] = []
    for tmpl, h in rules:
        ex = {tuple(c) for c in exclude.get(tmpl, [])}
        chosen: list[tuple[str, ...]] = []
        guard = 0
        while len(chosen) < m and guard < 10000:
            guard += 1
            combo = tuple(rng.choice(atoms, size=h, replace=False).tolist()) if h \
                else ()
            if combo not in ex and combo not in chosen:
                chosen.append(combo)
        for combo in chosen:
            trace, nf, _s, _st = reduce_strs(fill(tmpl, combo))
            items.append((trace[0], nf))
    return items


def to_byte_ids(text: str) -> np.ndarray:
    b = text.encode("utf-8", errors="ignore")
    return np.frombuffer(b, dtype=np.uint8).astype(np.int64)


# --------------------------------------------------------------------------- #
# Eval (format-independent exact-match derivation)                             #
# --------------------------------------------------------------------------- #
@torch.no_grad()
def generate(model: TinyLM, prompt_ids: list[int], block_size: int,
             device: str) -> str:
    model.eval()
    idx = torch.tensor(prompt_ids, dtype=torch.long, device=device)[None]
    out: list[int] = []
    for _ in range(MAX_NEW):
        cond = idx[:, -block_size:]
        logits, _, _ = model(cond)
        nxt = int(logits[0, -1].argmax().item())
        if nxt == NEWLINE_BYTE:
            break
        out.append(nxt)
        idx = torch.cat([idx, torch.tensor([[nxt]], device=device)], dim=1)
    return bytes(out).decode("utf-8", errors="ignore")


@torch.no_grad()
def eval_acc(model: TinyLM, eval_items: list[tuple[str, str]], block_size: int,
             device: str) -> float:
    correct = 0
    for inp, nf in eval_items:
        prompt = (inp + ARROW).encode("utf-8")
        gen = generate(model, list(prompt), block_size, device)
        pred = (inp + ARROW + gen).split(ARROW)[-1].strip()
        if pred == nf.strip():
            correct += 1
    return correct / max(1, len(eval_items))


# --------------------------------------------------------------------------- #
# Train one arm                                                                #
# --------------------------------------------------------------------------- #
def train_arm(name: str, corpus: str, eval_items: list[tuple[str, str]],
              args, device: str) -> dict:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    ids = to_byte_ids(corpus)
    T, bs = args.block_size, args.batch_size
    # tile a short corpus so random windows are always valid
    while ids.shape[0] <= 4 * (T + 1):
        ids = np.concatenate([ids, ids])
    n = ids.shape[0]
    model = TinyLM(args.d_model, args.n_head, args.n_layer, args.d_ff, T).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    curve: list[dict] = []
    t0 = time.time()
    for step in range(1, args.steps + 1):
        model.train()
        ix = torch.randint(0, n - T - 1, (bs,))
        xb = torch.stack([torch.from_numpy(ids[i:i + T]) for i in ix]).to(device)
        yb = torch.stack(
            [torch.from_numpy(ids[i + 1:i + 1 + T]) for i in ix]).to(device)
        logits, _, _ = model(xb)
        ce = F.cross_entropy(logits.reshape(-1, VOCAB), yb.reshape(-1))
        opt.zero_grad()
        ce.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % args.eval_every == 0 or step == args.steps:
            acc = eval_acc(model, eval_items, T, device)
            curve.append({"step": step, "tokens": step * bs * T,
                          "ce": round(float(ce.item()), 4), "heldout_acc": acc})
            log(f"  [{name}] step {step:5d} | CE {ce.item():.3f} "
                f"| held-out acc {acc:.3f} | {time.time()-t0:.0f}s")
    accs = [c["heldout_acc"] for c in curve]
    half = next((c["step"] for c in curve if c["heldout_acc"] >= 0.5), None)
    return {
        "arm": name,
        "corpus_bytes": int(to_byte_ids(corpus).shape[0]),  # the per-photo cost
        "final_acc": accs[-1] if accs else 0.0,
        "best_acc": max(accs) if accs else 0.0,
        "steps_to_half": half,
        "curve": curve,
    }


FORMATS = ["redex_nf", "full_trace"]
MULTS = ["one", "k_same", "k_varied"]


def run_seed(args, device: str, rules: list[tuple[str, int]],
             seed: int) -> list[dict]:
    """Train all 6 arms (FORMAT x MULTIPLICITY) at one seed; reseed data + init."""
    args.seed = seed
    fill_rng = np.random.default_rng(seed)
    train_fillings = {tmpl: make_fillings(fill_rng, h, TRAIN_ATOMS, args.k)
                      for tmpl, h in rules}
    eval_rng = np.random.default_rng(seed + 777)
    if args.heldout == "combos":
        eval_atoms, eval_exclude = TRAIN_ATOMS, train_fillings
    else:
        eval_atoms, eval_exclude = TEST_ATOMS, None
    eval_items = build_eval_items(rules, args.m_eval, eval_rng, eval_atoms,
                                  eval_exclude)
    log(f"  [seed {seed}] held-out eval instances={len(eval_items)} "
        f"(heldout={args.heldout})")
    arms: list[dict] = []
    for fmt in FORMATS:
        for mult in MULTS:
            corpus_rng = np.random.default_rng(seed + 13)
            corpus = build_corpus(rules, train_fillings, fmt, mult, args.k,
                                  corpus_rng)
            name = f"{fmt}/{mult}"
            log(f"\n=== seed {seed} {name}  (corpus {len(corpus.encode())} B) ===")
            v = train_arm(name, corpus, eval_items, args, device)
            v["format"], v["multiplicity"], v["seed"] = fmt, mult, seed
            arms.append(v)
    return arms


def _ms(vals: list[float]) -> list[float]:
    a = np.array(vals, dtype=float)
    return [round(float(a.mean()), 4), round(float(a.std()), 4)]


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps")
    ap.add_argument("--steps", type=int, default=4000)
    ap.add_argument("--eval-every", type=int, default=500)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--block-size", type=int, default=128)
    ap.add_argument("--d-model", type=int, default=128)
    ap.add_argument("--n-head", type=int, default=4)
    ap.add_argument("--n-layer", type=int, default=4)
    ap.add_argument("--d-ff", type=int, default=256)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--k", type=int, default=8, help="multiplicity (exposures/rule)")
    ap.add_argument("--m-eval", type=int, default=6, help="held-out instances/rule")
    ap.add_argument("--heldout", choices=["combos", "atoms"], default="combos",
                    help="combos=unseen fillings of SEEN atoms (rule generalization);"
                         " atoms=disjoint TEST atoms (variable-binding generalization)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", default="",
                    help="csv seeds for multi-seed harden, e.g. 0,1,2 "
                         "(overrides --seed; aggregates mean±std per arm)")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        args.steps, args.eval_every = 80, 40
        args.k, args.m_eval = 4, 3
        args.d_model, args.d_ff, args.n_layer = 64, 128, 3

    device = args.device
    if device == "mps" and not torch.backends.mps.is_available():
        device = "cpu"
        log("  mps unavailable -> cpu")
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    log("  validating skeletons (must be multi-step normal-forming)...")
    rules = validate_skeletons(SKELETONS)
    if args.smoke:
        rules = rules[:4]
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or [args.seed]
    log(f"  rules={len(rules)} train_atoms={len(TRAIN_ATOMS)} "
        f"test_atoms={len(TEST_ATOMS)} k={args.k} m_eval={args.m_eval} seeds={seeds}")

    all_arms: list[dict] = []
    for sd in seeds:
        all_arms.extend(run_seed(args, device, rules, sd))

    meta = {
        "experiment": "exposure-format-sweep",
        "register": "functional (held-out generalization)",
        "idea": "training as a photograph (s229); fork = memorization vs rule burn-in",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": git_sha(),
        "device": device,
        "smoke": args.smoke,
        "config": vars(args),
        "n_rules": len(rules),
        "heldout": args.heldout,
        "seeds": seeds,
        "elapsed_s": round(time.time() - t0, 1),
    }

    # ---- single-seed path (unchanged output contract) ----
    if len(seeds) == 1:
        by = {a["arm"]: a for a in all_arms}
        out = {**meta, "arms": all_arms}
        tag = "smoke" if args.smoke else "run"
        (RESULTS_DIR / f"verdict_{tag}.json").write_text(json.dumps(out, indent=2))
        log("\n  ==== EXPOSURE/FORMAT SWEEP ====")
        log(f"  {'arm':<22} {'corpus_B':>9} {'final_acc':>10} {'best_acc':>9} "
            f"{'steps@0.5':>10}")
        for fmt in FORMATS:
            for mult in MULTS:
                a = by[f"{fmt}/{mult}"]
                log(f"  {a['arm']:<22} {a['corpus_bytes']:>9} "
                    f"{a['final_acc']:>10.3f} {a['best_acc']:>9.3f} "
                    f"{a['steps_to_half']!s:>10}")
        log("\n  PREDICTIONS (held-out generalization):")
        for fmt in FORMATS:
            o = by[f"{fmt}/one"]["best_acc"]
            ks = by[f"{fmt}/k_same"]["best_acc"]
            kv = by[f"{fmt}/k_varied"]["best_acc"]
            log(f"   [{fmt}] burn-in (k_varied>one): {kv:.3f}>{o:.3f} = {kv > o}  | "
                f"rule>rote (k_varied>k_same): {kv:.3f}>{ks:.3f} = {kv > ks}")
        log(f"\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({meta['elapsed_s']}s)")
        return

    # ---- multi-seed aggregate (the harden) ----
    agg: dict[str, dict] = {}
    for fmt in FORMATS:
        for mult in MULTS:
            name = f"{fmt}/{mult}"
            rs = [a for a in all_arms if a["arm"] == name]
            agg[name] = {
                "n": len(rs),
                "best_acc": _ms([r["best_acc"] for r in rs]),
                "final_acc": _ms([r["final_acc"] for r in rs]),
                "corpus_bytes": rs[0]["corpus_bytes"],
                "per_seed_best": [r["best_acc"] for r in rs],
            }
    out = {**meta, "aggregate": agg, "runs": all_arms}
    (RESULTS_DIR / "verdict_multiseed.json").write_text(json.dumps(out, indent=2))

    log("\n  ==== MULTI-SEED AGGREGATE (mean±std over seeds) ====")
    log(f"  {'arm':<22} {'corpus_B':>9} {'best_acc(mean±std)':>22} {'per-seed':>20}")
    for fmt in FORMATS:
        for mult in MULTS:
            a = agg[f"{fmt}/{mult}"]
            ps = ",".join(f"{x:.2f}" for x in a["per_seed_best"])
            log(f"  {fmt + '/' + mult:<22} {a['corpus_bytes']:>9} "
                f"{a['best_acc'][0]:>+10.3f}±{a['best_acc'][1]:<5.3f}        {ps:>20}")
    log("\n  ROBUSTNESS (best_acc, mean±std; decisive if k_varied(mean-std) clears):")
    for fmt in FORMATS:
        kv = agg[f"{fmt}/k_varied"]["best_acc"]
        ks = agg[f"{fmt}/k_same"]["best_acc"]
        o = agg[f"{fmt}/one"]["best_acc"]
        rule_robust = (kv[0] - kv[1]) > (ks[0] + ks[1])
        burn_robust = (kv[0] - kv[1]) > (o[0] + o[1])
        log(f"   [{fmt}] rule>rote: k_varied {kv[0]:.3f}±{kv[1]:.3f} vs k_same "
            f"{ks[0]:.3f}±{ks[1]:.3f} -> DECISIVE={rule_robust} | "
            f"burn-in vs one {o[0]:.3f}±{o[1]:.3f} -> DECISIVE={burn_robust}")
    log(f"\n  wrote {RESULTS_DIR / 'verdict_multiseed.json'}  ({meta['elapsed_s']}s)")


if __name__ == "__main__":
    main()
