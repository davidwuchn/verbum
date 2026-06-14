#!/usr/bin/env python3
# register: functional (continuation-driven prover, kernel-verified)
"""Continuation-driven prover — does STEPWISE proving rescue composition? (s228).

THE HYPOTHESIS. The single-shot prover (proof_inhabitation.py) proved AXIOMS but
failed to COMPOSE multi-combinator proof terms. lambda-halt-continuation.md predicts
the fix: prove one inference rule per turn and let the CONTINUATION (the open goal
stack) carry the proof state between steps. proof_search.py is the goal-directed
natural-deduction engine; here the MODEL chooses one move per turn, the kernel applies
it and reconstructs+verifies the term at QED. Soundness is structural: a non-theorem
has NO closing derivation, so the model cannot falsely prove one regardless of moves.

  PHASE 1 (--mode engine, no GPU) — the automatic solver floor: every positive solved
    + reconstructed term kernel-verified; every negative unsolvable.
  PHASE 2 (--mode model) — the model navigates the proof tree turn by turn, picking
    from the legal-move menu; compare sensitivity to the s228 single-shot baseline.

Usage:
  uv run python scripts/experiments/proof_repl.py --mode engine
  uv run python scripts/experiments/proof_repl.py --mode model -m Qwen/Qwen3-8B
  uv run python scripts/experiments/proof_repl.py --mode aggregate

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
from verbum.lambda_ast import pretty
from verbum.probes.proof_tasks import proof_tasks
from verbum.proof_kernel import pretty_prop
from verbum.proof_search import (
    init_state,
    legal_moves,
    make_move,
    solve,
    verify_state,
)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "proof-repl"

MAX_TURNS = 20

INSTRUCTION = (
    "You are an interactive proof assistant for intuitionistic implicational logic.\n"
    "You prove a goal by choosing ONE move at a time. Moves:\n"
    "  intro     — if the goal is an implication P -> Q: assume P, goal becomes Q\n"
    "  exact hN   — close the goal using hypothesis hN whose type IS the goal\n"
    "  apply hN   — if hN : ... -> Goal, reduce to proving its premise(s)\n"
    "At each step you are shown the goal, the hypotheses, and the available moves.\n"
    "Reply with EXACTLY ONE move from the available list, nothing else.\n"
    "\n"
    "Example — proving A -> B -> A:\n"
    "  Goal: A -> B -> A | Context: empty | Moves: intro\n"
    "  Move: intro\n"
    "  Goal: B -> A | Context: h1:A | Moves: intro\n"
    "  Move: intro\n"
    "  Goal: A | Context: h1:A, h2:B | Moves: exact h1\n"
    "  Move: exact h1\n"
    "  (proved)\n"
    "\n"
    "Example — proving (A -> B) -> (B -> C) -> A -> C:\n"
    "  Goal: ... | Context: empty | Moves: intro\n"
    "  Move: intro     (assume h1:A->B)\n"
    "  Move: intro     (assume h2:B->C)\n"
    "  Move: intro     (assume h3:A)\n"
    "  Goal: C | Context: h1:A->B, h2:B->C, h3:A | Moves: apply h2\n"
    "  Move: apply h2  (now prove B)\n"
    "  Move: apply h1  (now prove A)\n"
    "  Move: exact h3\n"
    "  (proved)\n"
)


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


def render_ctx(ctx) -> str:
    if not ctx:
        return "empty"
    return ", ".join(f"{n}:{pretty_prop(t)}" for n, t in ctx)


def render_turn(st) -> str:
    g = st.goals[0]
    moves = legal_moves(st)
    return (f"Goal: {pretty_prop(g.target)} | Context: {render_ctx(g.ctx)} | "
            f"Moves: {' , '.join(moves)}\nMove:")


def parse_move(text: str, moves: list[str]) -> str | None:
    """Match the model's reply to a legal move (case/space tolerant)."""
    t = text.strip()
    for marker in ("Move:", "move:"):
        if marker in t:
            t = t.split(marker)[-1]
    line = next((ln.strip() for ln in t.splitlines() if ln.strip()), "")
    low = " ".join(line.lower().replace("`", "").split())
    legal_low = {m.lower(): m for m in moves}
    if low in legal_low:
        return legal_low[low]
    for ml, m in legal_low.items():       # tolerate trailing commentary
        if low.startswith(ml):
            return m
    return None


# --------------------------------------------------------------------------- #
# PHASE 1 — engine floor (no GPU)                                              #
# --------------------------------------------------------------------------- #
def run_engine(args) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    recs = []
    floor_ok = True
    for t in proof_tasks():
        st = solve(t.prop)
        if t.provable:
            ok = st is not None and verify_state(st).valid
            floor_ok &= ok
            term = pretty(__import__(
                "verbum.proof_search", fromlist=["reconstruct"]
            ).reconstruct(st)) if st is not None else None
            recs.append({"id": t.id, "prop": t.prop, "provable": True,
                         "solved": st is not None, "verified": ok, "term": term})
        else:
            ok = st is None              # negatives must be unsolvable
            floor_ok &= ok
            recs.append({"id": t.id, "prop": t.prop, "provable": False,
                         "solved": st is not None, "verified": None})
    out = {"phase": "engine (auto solver floor)",
           "timestamp": datetime.now(UTC).isoformat(),
           "floor_ok": floor_ok, "records": recs, "git_sha": git_sha()}
    (RESULTS_DIR / "engine.json").write_text(json.dumps(out, indent=2))
    log("")
    log("  === PHASE 1 — ENGINE FLOOR (auto solver) ===")
    for r in recs:
        if r["provable"]:
            log(f"    {'OK ' if r['verified'] else 'XX '}{r['id']:16} "
                f"{r['prop']:34} -> {r['term']}")
        else:
            log(f"    {'OK ' if not r['solved'] else 'BAD'}{r['id']:16} "
                f"{r['prop']:34} (unprovable)")
    log(f"  floor_ok (positives solved+verified, negatives unsolvable): {floor_ok}")
    log("  wrote engine.json")
    if not floor_ok:
        sys.exit(1)


# --------------------------------------------------------------------------- #
# the per-task interactive loop                                                #
# --------------------------------------------------------------------------- #
def prove_interactive(task, gen_fn) -> dict:
    """Run the multi-turn proof loop for one task. gen_fn(prompt)->str."""
    st = init_state(task.prop)
    transcript = (f"{INSTRUCTION}\n=== Prove: {task.prop} ===\n")
    moves_made: list[str] = []
    status = "open"
    for _turn in range(MAX_TURNS):
        if st.done:
            status = "qed"
            break
        moves = legal_moves(st)
        if not moves:
            status = "stuck"            # no legal move (dead end / non-theorem)
            break
        prompt = transcript + render_turn(st)
        reply = gen_fn(prompt)
        mv = parse_move(reply, moves)
        if mv is None:
            status = "illegal"
            moves_made.append(f"?{reply.strip()[:20]!r}")
            break
        try:
            st = make_move(st, mv)
        except ValueError:
            status = "illegal"
            break
        moves_made.append(mv)
        transcript += f"{render_turn_done(mv)}\n"
    chk = verify_state(st) if st.done else None
    proved = chk is not None and chk.valid
    return {
        "id": task.id, "prop": task.prop, "provable": task.provable,
        "complexity": task.complexity, "status": status, "proved": proved,
        "turns": len(moves_made), "moves": moves_made,
        "term": pretty(__import__("verbum.proof_search", fromlist=["reconstruct"])
                       .reconstruct(st)) if st.done else None,
        "verdict": chk.verdict if chk is not None else None,
        # correct: positive -> proved; negative -> NOT proved
        "correct": proved if task.provable else (not proved),
    }


def render_turn_done(mv: str) -> str:
    return f"Move: {mv}"


# --------------------------------------------------------------------------- #
# PHASE 2 — model as prover (GPU)                                             #
# --------------------------------------------------------------------------- #
def run_model(args) -> None:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    safe = args.model.replace("/", "_")
    t0 = time.time()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    tasks = proof_tasks()

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()
    used_chat = getattr(tok, "chat_template", None) is not None
    log(f"[{args.model}] {len(tasks)} tasks ({'chat' if used_chat else 'base/raw'})")

    @torch.no_grad()
    def gen_fn(prompt: str, _model=model, _tok=tok) -> str:
        text = prompt
        if used_chat:
            try:
                text = _tok.apply_chat_template(
                    [{"role": "user", "content": prompt}], tokenize=False,
                    add_generation_prompt=True, enable_thinking=False)
            except (TypeError, ValueError):
                try:
                    text = _tok.apply_chat_template(
                        [{"role": "user", "content": prompt}], tokenize=False,
                        add_generation_prompt=True)
                except (TypeError, ValueError):
                    text = prompt
        enc = _tok(text, return_tensors="pt").to(args.device)
        out = _model.generate(**enc, max_new_tokens=12, do_sample=False,
                              pad_token_id=_tok.pad_token_id or _tok.eos_token_id)
        return _tok.decode(out[0][enc["input_ids"].shape[1]:],
                           skip_special_tokens=True)

    records = [prove_interactive(t, gen_fn) for t in tasks]

    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()
    elif args.device == "cuda":
        torch.cuda.empty_cache()

    pos = [r for r in records if r["provable"]]
    neg = [r for r in records if not r["provable"]]
    n_sens = sum(r["proved"] for r in pos)
    n_spec = sum(not r["proved"] for r in neg)
    false_proofs = [r for r in neg if r["proved"]]
    by_cx: dict[int, dict] = {}
    for r in pos:
        d = by_cx.setdefault(r["complexity"], {"n": 0, "proved": 0})
        d["n"] += 1
        d["proved"] += int(r["proved"])
    avg_turns = round(sum(r["turns"] for r in pos) / max(len(pos), 1), 2)

    out = {
        "model": args.model, "dtype": args.dtype,
        "prompt_mode": "chat" if used_chat else "base/raw",
        "register": "functional (continuation-driven prover, kernel-verified)",
        "timestamp": datetime.now(UTC).isoformat(),
        "max_turns": MAX_TURNS,
        "n": len(records), "n_positive": len(pos), "n_negative": len(neg),
        "sensitivity": round(n_sens / max(len(pos), 1), 4),
        "specificity": round(n_spec / max(len(neg), 1), 4),
        "avg_turns_positive": avg_turns,
        "false_proofs": false_proofs,
        "by_complexity": {str(k): {**v, "rate": round(v["proved"] / v["n"], 3)}
                          for k, v in sorted(by_cx.items())},
        "records": records,
        "git_sha": git_sha(), "elapsed_s": round(time.time() - t0, 1),
    }
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))

    log("")
    log(f"  === {args.model} continuation-driven prover ===")
    log(f"  sensitivity {out['sensitivity']:.3f} ({n_sens}/{len(pos)}); "
        f"specificity {out['specificity']:.3f} ({n_spec}/{len(neg)}); "
        f"avg turns {avg_turns}")
    if false_proofs:
        log(f"  !! {len(false_proofs)} FALSE PROOF(S): "
            + ", ".join(r["id"] for r in false_proofs))
    log("  by complexity (pos): "
        + "  ".join(f"d{k}:{v['proved']}/{v['n']}"
                    for k, v in out["by_complexity"].items()))
    log("  positives not proved:")
    for r in pos:
        if not r["proved"]:
            log(f"    {r['id']:16} {r['prop']:30} status={r['status']} "
                f"turns={r['turns']} moves={r['moves']}")
    log(f"  wrote {safe}.json  ({out['elapsed_s']}s)")


def run_aggregate(args) -> None:
    files = sorted(f for f in RESULTS_DIR.glob("*.json")
                   if f.stem not in ("aggregate", "engine"))
    if not files:
        log(f"no model jsons in {RESULTS_DIR}")
        sys.exit(1)
    models = [json.loads(f.read_text()) for f in files]
    # single-shot baseline for the delta
    base_path = (_PROJECT_ROOT / "results" / "proof-inhabitation" / "aggregate.json")
    base = {}
    if base_path.exists():
        for r in json.loads(base_path.read_text())["rows"]:
            base[r["model"]] = r["sensitivity"]
    rows = [{"model": m["model"], "sensitivity": m["sensitivity"],
             "specificity": m["specificity"], "avg_turns": m["avg_turns_positive"],
             "false_proofs": len(m["false_proofs"]),
             "single_shot_sensitivity": base.get(m["model"]),
             "delta": (None if base.get(m["model"]) is None
                       else round(m["sensitivity"] - base[m["model"]], 3))}
            for m in models]
    out = {"models": [m["model"] for m in models], "rows": rows,
           "git_sha": git_sha(), "timestamp": datetime.now(UTC).isoformat()}
    (RESULTS_DIR / "aggregate.json").write_text(json.dumps(out, indent=2))
    log("")
    log("  === CONTINUATION-DRIVEN PROVER (kernel-verified) ===")
    log(f"  {'model':>24} {'sens':>5} {'spec':>5} {'turns':>5} "
        f"{'1shot':>6} {'Δ':>6} {'falseP':>6}")
    for r in rows:
        ss = "  n/a" if r["single_shot_sensitivity"] is None \
            else f"{r['single_shot_sensitivity']:>6.2f}"
        dd = "   n/a" if r["delta"] is None else f"{r['delta']:>+6.2f}"
        log(f"  {r['model']:>24} {r['sensitivity']:>5.2f} {r['specificity']:>5.2f} "
            f"{r['avg_turns']:>5.1f} {ss} {dd} {r['false_proofs']:>6}")
    log("  wrote aggregate.json")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["engine", "model", "aggregate"],
                    default="engine")
    ap.add_argument("-m", "--model", default="Qwen/Qwen3-32B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    args = ap.parse_args()
    if args.mode == "engine":
        run_engine(args)
    elif args.mode == "model":
        run_model(args)
    else:
        run_aggregate(args)


if __name__ == "__main__":
    main()
