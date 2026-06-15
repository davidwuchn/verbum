#!/usr/bin/env python3
# register: functional (capability/usage — held-out COMPOSITIONAL generalization)
"""Compiler-cascade v1 — does compiler-minted COMPOSITION-variety converge capability
that COMPOSES? (session 230; the fractal-collapse thesis, IOU #1).

THE THESIS (Michael, s230; fractal-collapse-compiler-cascade.md): capability =
inventory (x) continuation, and s230b proved they are causally separable with the
continuation the trained bottleneck. So converging capability is a DATA problem: mint
high-variety inputs (s229: variety = the rule), reduce each with the EXACT compiler
(lambda_ast, canonical Church-Rosser outputs), train the student continuation on
(input -> normal form). The decisive open question (IOU #1): does HIGH-VARIETY minted
data converge capability that GENERALIZES TO NOVEL COMPOSITIONS, or stay "too narrow
to compose" (the s225 worry)?

THE TEST: lift the s229 variety lesson one level — from fillings->rule to
compositions->ALGEBRA. Auto-generate a pool of combinator-composition templates over
{K,I,B,C} (non-duplicating => always terminating), each validated to normal-form via
lambda_ast. Hold out a DISJOINT set of compositions (never trained). Vary the number
of distinct TRAIN compositions (the COMPOSITION-variety axis) at a MATCHED total-
example budget:

  low   : few distinct compositions, MANY fillings each   (memorize compositions)
  mid   : ...
  high  : many distinct compositions, FEW fillings each   (the collapse)

Nested (low subset of mid subset of high) so the ONLY difference is MORE distinct
compositions. Atoms are SEEN (combos-style, TRAIN_ATOMS) for both train and eval ->
isolates COMPOSITION generalization from the s229 disjoint-atom variable-binding floor
(that is a separate copy mechanism). Two eval sets:

  heldout_comp : NOVEL compositions (held-out templates), seen atoms  <- the question
  in_dist      : TRAIN compositions, held-out FILLINGS                <- control
METRIC: teacher-forced per-token NF accuracy (value register). Exact-match of a full
NF is a crisp probe that FLOORS for a micro byte model even as CE drops (a λ measure
false-negative, observed s230); TF NF-token accuracy reads the graded reduction
competence and separates the arms. Relative (high vs low variety) is the signal.

FALSIFIABLE PREDICTION (the collapse's IOU #1): high composition-variety GENERALIZES
to novel compositions (learns the combinator algebra); low MEMORIZES its few
compositions and fails held-out. Monotone rise of heldout_comp with composition-
variety = the collapse is real. If high also fails heldout_comp => minted variety is
not enough (need diverse paraphrase). Relative is the signal (tiny model; s229 caveat).

Data is kernel-minted (lambda_ast) — exact, canonical, free, MIT level-4.

Usage:
  uv run python scripts/experiments/compiler_cascade.py --smoke
  uv run python scripts/experiments/compiler_cascade.py --seeds 0,1,2

License: MIT
"""

from __future__ import annotations

import argparse
import json
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

from exposure_format_sweep import (  # noqa: E402
    ARROW,
    TRAIN_ATOMS,
    fill,
    make_fillings,
    n_holes,
    reduce_strs,
    render,
    to_byte_ids,
)
from relational_loss_distillation import VOCAB, TinyLM  # noqa: E402

from verbum.lambda_ast import Status  # noqa: E402

RESULTS_DIR = _PROJECT_ROOT / "results" / "compiler-cascade"

COMBS = ["K", "I", "B", "C"]      # non-duplicating => terminating composition space
ARITY = {"K": 2, "I": 1, "B": 3, "C": 3}


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# --------------------------------------------------------------------------- #
# Composition-template generator (the COMPOSITION axis)                         #
# --------------------------------------------------------------------------- #
def _build_node(rng: np.random.Generator, depth: int, holes: list[int],
                p_recurse: float):
    """Node = ('hole', idx) or ('app', head, [children])."""
    if depth <= 0 or rng.random() >= p_recurse:
        idx = holes[0]
        holes[0] += 1
        return ("hole", idx)
    head = COMBS[int(rng.integers(len(COMBS)))]
    children = [_build_node(rng, depth - 1, holes, p_recurse)
                for _ in range(ARITY[head])]
    return ("app", head, children)


def _node_str(node, as_arg: bool) -> str:
    if node[0] == "hole":
        return f"_{node[1]}"
    _, head, children = node
    s = head + " " + " ".join(_node_str(c, True) for c in children)
    return f"({s})" if as_arg else s


def gen_templates(rng: np.random.Generator, n_target: int, max_depth: int,
                  p_recurse: float, min_steps: int, max_steps: int,
                  min_holes: int, max_holes: int, max_nf_len: int) -> list[str]:
    """Distinct combinator-composition templates (holes _0.._n) that normal-form."""
    seen: set[str] = set()
    out: list[str] = []
    guard = 0
    while len(out) < n_target and guard < n_target * 400:
        guard += 1
        holes = [0]
        head = COMBS[int(rng.integers(len(COMBS)))]
        top = ("app", head, [_build_node(rng, max_depth - 1, holes, p_recurse)
                             for _ in range(ARITY[head])])
        h = holes[0]
        if not (min_holes <= h <= max_holes):
            continue
        tmpl = _node_str(top, False)
        if tmpl in seen:
            continue
        probe = fill(tmpl, tuple(TRAIN_ATOMS[:h]))
        try:
            trace, nf, steps, status = reduce_strs(probe)
        except Exception:
            continue
        if status != Status.NORMAL_FORM.value or not (min_steps <= steps <= max_steps):
            continue
        if len(nf) > max_nf_len or len(trace) < 2:
            continue
        seen.add(tmpl)
        out.append(tmpl)
    return out


def template_holes(tmpl: str) -> int:
    return n_holes(tmpl)


# --------------------------------------------------------------------------- #
# Corpus + eval items                                                           #
# --------------------------------------------------------------------------- #
def build_corpus(templates: list[str], fillings: dict[str, list],
                 rng: np.random.Generator) -> str:
    lines: list[str] = []
    for t in templates:
        for combo in fillings[t]:
            lines.append(render(t, combo, "redex_nf"))
    order = rng.permutation(len(lines))
    return "\n".join(lines[i] for i in order) + "\n"


def eval_items_for(templates: list[str], m: int, rng: np.random.Generator,
                   exclude: dict[str, list] | None = None) -> list[tuple[str, str]]:
    exclude = exclude or {}
    items: list[tuple[str, str]] = []
    for t in templates:
        h = template_holes(t)
        ex = {tuple(c) for c in exclude.get(t, [])}
        chosen: list[tuple[str, ...]] = []
        guard = 0
        while len(chosen) < m and guard < 5000:
            guard += 1
            combo = tuple(rng.choice(TRAIN_ATOMS, size=h, replace=False).tolist())
            if combo not in ex and combo not in chosen:
                chosen.append(combo)
        for combo in chosen:
            trace, nf, _s, _st = reduce_strs(fill(t, combo))
            items.append((trace[0], nf))
    return items


# --------------------------------------------------------------------------- #
# Graded eval — TEACHER-FORCED per-token NF accuracy (value register).          #
# Exact-match of a full NF is a CRISP probe on a GRADED substrate -> it floors  #
# for a micro byte model even as CE drops (a λ measure false-negative). TF NF   #
# accuracy reads the partial reduction competence: given the TRUE prefix, what  #
# fraction of NF bytes does the model predict? Not gameable by copying the      #
# input (scored on the NF region given true context). One forward pass / item.  #
# --------------------------------------------------------------------------- #
@torch.no_grad()
def tf_nf_acc(model, items: list[tuple[str, str]], block_size: int,
              device: str) -> float:
    model.eval()
    total, correct = 0, 0
    for inp, nf in items:
        prefix_len = len((inp + ARROW).encode("utf-8"))
        full = (inp + ARROW + nf).encode("utf-8")[:block_size]
        if len(full) < 2:
            continue
        x = torch.tensor(list(full), dtype=torch.long, device=device)[None]
        logits, _, _ = model(x)
        preds = logits[0, :-1].argmax(-1)
        tgt = x[0, 1:]
        for t in range(tgt.shape[0]):
            if (t + 1) >= prefix_len:  # target byte lies in the NF region
                total += 1
                correct += int(preds[t].item() == tgt[t].item())
    return correct / max(1, total)


# --------------------------------------------------------------------------- #
# Train one arm                                                                 #
# --------------------------------------------------------------------------- #
def train_arm(name: str, corpus: str, heldout_comp: list[tuple[str, str]],
              in_dist: list[tuple[str, str]], args, device: str) -> dict:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    ids = to_byte_ids(corpus)
    T, bs = args.block_size, args.batch_size
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
            hc = tf_nf_acc(model, heldout_comp, T, device)
            idd = tf_nf_acc(model, in_dist, T, device)
            curve.append({"step": step, "heldout_comp": round(hc, 4),
                          "in_dist": round(idd, 4), "ce": round(float(ce.item()), 4)})
            log(f"  [{name}] step {step:5d} | CE {ce.item():.3f} "
                f"| heldout_comp_tf {hc:.3f} | in_dist_tf {idd:.3f} "
                f"| {time.time()-t0:.0f}s")
    hcs = [c["heldout_comp"] for c in curve]
    idds = [c["in_dist"] for c in curve]
    return {
        "arm": name,
        "corpus_bytes": int(to_byte_ids(corpus).shape[0]),
        "heldout_comp_best": max(hcs) if hcs else 0.0,
        "heldout_comp_final": hcs[-1] if hcs else 0.0,
        "in_dist_best": max(idds) if idds else 0.0,
        "in_dist_final": idds[-1] if idds else 0.0,
        "curve": curve,
    }


def _ms(vals: list[float]) -> list[float]:
    a = np.array(vals, dtype=float)
    return [round(float(a.mean()), 4), round(float(a.std()), 4)]


def run_seed(args, device: str, train_pool: list[str], heldout_templates: list[str],
             seed: int, arm_levels: list[int]) -> list[dict]:
    args.seed = seed
    rng = np.random.default_rng(seed)
    # nested arms: high = first max(levels) of a shuffled pool; lower = prefixes
    pool = list(train_pool)
    rng.shuffle(pool)
    n_max = max(arm_levels)
    chosen_pool = pool[:n_max]
    # held-out-composition eval (NOVEL compositions, seen atoms)
    eval_rng = np.random.default_rng(seed + 999)
    heldout_comp = eval_items_for(heldout_templates, args.m_eval, eval_rng)
    log(f"  [seed {seed}] train_pool={len(train_pool)} heldout_templates="
        f"{len(heldout_templates)} heldout_comp_items={len(heldout_comp)}")
    arms: list[dict] = []
    for lvl in arm_levels:
        templates = chosen_pool[:lvl]
        n_fill = max(1, args.budget // lvl)  # matched total-example budget
        fill_rng = np.random.default_rng(seed + lvl)
        fillings = {t: make_fillings(fill_rng, template_holes(t), TRAIN_ATOMS, n_fill)
                    for t in templates}
        corpus = build_corpus(templates, fillings, np.random.default_rng(seed + 7))
        # in-dist control: TRAIN compositions, held-out FILLINGS
        ind_rng = np.random.default_rng(seed + 31 + lvl)
        ind_templates = templates[:args.in_dist_templates]
        in_dist = eval_items_for(ind_templates, args.m_eval, ind_rng,
                                 exclude={t: fillings[t] for t in ind_templates})
        name = f"comp{lvl}"
        ex_ct = sum(len(v) for v in fillings.values())
        log(f"\n=== seed {seed} {name}  ({lvl} compositions x {n_fill} fillings "
            f"= {ex_ct} ex, corpus {len(corpus.encode())} B) ===")
        v = train_arm(name, corpus, heldout_comp, in_dist, args, device)
        v["n_compositions"], v["n_fillings"], v["examples"] = lvl, n_fill, ex_ct
        v["seed"] = seed
        arms.append(v)
    return arms


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps")
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--eval-every", type=int, default=1000)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--block-size", type=int, default=128)
    ap.add_argument("--d-model", type=int, default=128)
    ap.add_argument("--n-head", type=int, default=4)
    ap.add_argument("--n-layer", type=int, default=4)
    ap.add_argument("--d-ff", type=int, default=256)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--budget", type=int, default=2304,
                    help="matched total examples per arm")
    ap.add_argument("--arm-levels", default="16,48,144",
                    help="csv distinct-composition counts (nested; the variety axis)")
    ap.add_argument("--pool-size", type=int, default=320,
                    help="distinct train-composition templates to generate")
    ap.add_argument("--heldout-templates", type=int, default=40,
                    help="distinct NOVEL compositions held out for the eval")
    ap.add_argument("--in-dist-templates", type=int, default=20)
    ap.add_argument("--m-eval", type=int, default=3, help="fillings per eval template")
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--p-recurse", type=float, default=0.55)
    ap.add_argument("--min-steps", type=int, default=2)
    ap.add_argument("--max-steps", type=int, default=6)
    ap.add_argument("--min-holes", type=int, default=3)
    ap.add_argument("--max-holes", type=int, default=6)
    ap.add_argument("--max-nf-len", type=int, default=26)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", default="")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        args.steps, args.eval_every = 150, 75
        args.budget, args.arm_levels = 256, "8,32"
        args.pool_size, args.heldout_templates = 60, 12
        args.in_dist_templates, args.m_eval = 6, 2
        args.d_model, args.d_ff, args.n_layer = 64, 128, 3

    device = args.device
    if device == "mps" and not torch.backends.mps.is_available():
        device = "cpu"
        log("  mps unavailable -> cpu")
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    arm_levels = [int(x) for x in args.arm_levels.split(",") if x.strip()]
    # generate the composition pool ONCE (shared across seeds; seeds reshuffle/sample)
    gen_rng = np.random.default_rng(12345)
    n_need = args.pool_size + args.heldout_templates
    pool = gen_templates(gen_rng, n_need, args.max_depth, args.p_recurse,
                         args.min_steps, args.max_steps, args.min_holes,
                         args.max_holes, args.max_nf_len)
    if len(pool) < n_need:
        log(f"  WARN: generated {len(pool)} < requested {n_need} templates")
    heldout_templates = pool[:args.heldout_templates]
    train_pool = pool[args.heldout_templates:]
    if max(arm_levels) > len(train_pool):
        arm_levels = [lvl for lvl in arm_levels if lvl <= len(train_pool)]
    log(f"  composition pool={len(pool)} (train {len(train_pool)}, heldout "
        f"{len(heldout_templates)}) arm_levels={arm_levels} budget={args.budget}")
    log(f"  sample templates: {train_pool[:3]} | heldout: {heldout_templates[:2]}")

    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or [args.seed]
    all_arms: list[dict] = []
    for sd in seeds:
        all_arms.extend(run_seed(args, device, train_pool, heldout_templates, sd,
                                 arm_levels))

    meta = {
        "experiment": "compiler-cascade",
        "register": "functional (held-out compositional generalization)",
        "idea": "fractal-collapse IOU#1: does compiler-minted COMPOSITION-variety "
                "converge capability that COMPOSES (held-out novel compositions)?",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": git_sha(),
        "device": device,
        "smoke": args.smoke,
        "config": vars(args),
        "arm_levels": arm_levels,
        "seeds": seeds,
        "n_train_pool": len(train_pool),
        "n_heldout_templates": len(heldout_templates),
        "elapsed_s": round(time.time() - t0, 1),
    }

    agg: dict[str, dict] = {}
    for lvl in arm_levels:
        rs = [a for a in all_arms if a["n_compositions"] == lvl]
        agg[f"comp{lvl}"] = {
            "n_compositions": lvl,
            "n_fillings": rs[0]["n_fillings"],
            "examples": rs[0]["examples"],
            "heldout_comp_best": _ms([r["heldout_comp_best"] for r in rs]),
            "heldout_comp_final": _ms([r["heldout_comp_final"] for r in rs]),
            "in_dist_best": _ms([r["in_dist_best"] for r in rs]),
            "per_seed_heldout": [r["heldout_comp_best"] for r in rs],
        }

    tag = "smoke" if args.smoke else ("multiseed" if len(seeds) > 1 else "run")
    out = {**meta, "aggregate": agg, "runs": all_arms}
    (RESULTS_DIR / f"verdict_{tag}.json").write_text(json.dumps(out, indent=2))

    log("\n  ==== COMPILER-CASCADE v1 — COMPOSITION-VARIETY -> GENERALIZATION ====")
    log(f"  {'arm':<10} {'comps':>6} {'fills':>6} {'heldout_comp(mean±std)':>24} "
        f"{'in_dist':>16}")
    for lvl in arm_levels:
        a = agg[f"comp{lvl}"]
        hc, idd = a["heldout_comp_best"], a["in_dist_best"]
        ps = ",".join(f"{x:.2f}" for x in a["per_seed_heldout"])
        log(f"  comp{lvl:<6} {a['n_compositions']:>6} {a['n_fillings']:>6} "
            f"{hc[0]:>+10.3f}±{hc[1]:<5.3f} [{ps}]   {idd[0]:.3f}±{idd[1]:.3f}")
    if len(arm_levels) >= 2:
        lo, hi = agg[f"comp{arm_levels[0]}"], agg[f"comp{arm_levels[-1]}"]
        h_lo, h_hi = lo["heldout_comp_best"], hi["heldout_comp_best"]
        decisive = (h_hi[0] - h_hi[1]) > (h_lo[0] + h_lo[1])
        log(f"\n  COLLAPSE IOU#1: heldout-composition rises with composition-variety? "
            f"comp{arm_levels[0]}={h_lo[0]:.3f} -> comp{arm_levels[-1]}={h_hi[0]:.3f}  "
            f"DECISIVE={decisive}")
        log("  (atoms SEEN both sides => COMPOSITION generalization, not copy)")
    log(f"\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({meta['elapsed_s']}s)")


if __name__ == "__main__":
    main()
