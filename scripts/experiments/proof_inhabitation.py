#!/usr/bin/env python3
# register: functional (the learned prover, kernel-verified)
"""Proof-as-inhabitation — can a model RUN proofs via Curry-Howard? (session 228).

THE QUESTION (Michael: "would continuations allow us to run proofs?"). Under
Curry-Howard a proof of proposition P is a closed term inhabiting the type P;
proof-check = type-check; normalization (the continuation, β-reduction → WHNF) =
cut-elimination. The combinator basis IS a Hilbert proof calculus (K, S are the axiom
schemes). This experiment measures BOTH layers:

  PHASE 1 (--mode kernel, no GPU) — the CONSTRUCTED kernel as proof checker:
    certify every positive's reference proof (the 100% floor by construction),
    confirm negatives have no sound proof, and demonstrate the CONSISTENCY FIREWALL
    (Y types (a->a)->a so a recursion-admitting kernel would "prove" (A->A)->A; the
    sound-basis gate rejects it).

  PHASE 2 (--mode model) — the LLM as PROVER, kernel as verifier:
    few-shot a model `proposition -> proof term` over the sound basis {S,K,I,B,C,W,D}
    (Y forbidden), allow `none` for non-theorems, GRADE BY THE KERNEL. Model proposes,
    kernel disposes — the compiler-as-loss / co-processor pattern.

  Metrics: sensitivity (positives proved), specificity (negatives NOT falsely proved),
  failure breakdown (parse / open / ill-typed / type-mismatch / unsound-recursion),
  by-complexity curve.

Usage:
  uv run python scripts/experiments/proof_inhabitation.py --mode kernel
  uv run python scripts/experiments/proof_inhabitation.py --mode model -m Qwen/Qwen3-8B
  uv run python scripts/experiments/proof_inhabitation.py --mode aggregate

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
from verbum.probes.proof_tasks import (
    negatives,
    positives,
    proof_tasks,
)
from verbum.proof_kernel import Verdict, check_proof

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "proof-inhabitation"

INSTRUCTION = (
    "You are a proof assistant for the implicational fragment of intuitionistic "
    "propositional logic.\n"
    "By the Curry-Howard correspondence, a PROOF of a proposition is a closed "
    "combinator term whose type is that proposition.\n"
    "Prove the proposition by giving a closed term over the basis combinators "
    "S, K, I, B, C, W (application is juxtaposition, left-associative; use "
    "parentheses to group). Their types are the logical axioms:\n"
    "  I : A -> A\n"
    "  K : A -> B -> A\n"
    "  B : (B -> C) -> (A -> B) -> A -> C\n"
    "  C : (A -> B -> C) -> B -> A -> C\n"
    "  S : (A -> B -> C) -> (A -> B) -> A -> C\n"
    "  W : (A -> A -> B) -> A -> B\n"
    "Do NOT use Y or self-application (they are logically unsound). If the "
    "proposition is NOT provable, answer exactly: none\n"
    "Output ONLY the proof term (or none) on a single line, nothing else."
)

# Few-shot — the four axioms + one non-theorem. Atom names are illustrative; the
# combinators are atom-agnostic so this primes FORMAT, not specific answers.
FEWSHOT: list[tuple[str, str]] = [
    ("A -> A", "I"),
    ("A -> B -> A", "K"),
    ("(A -> B -> C) -> (A -> B) -> A -> C", "S"),
    ("(B -> C) -> (A -> B) -> A -> C", "B"),
    ("(A -> B) -> A", "none"),
]


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


def build_prompt(prop: str) -> str:
    lines = [INSTRUCTION, ""]
    for p, e in FEWSHOT:
        lines += [f"Proposition: {p}", f"Proof: {e}", ""]
    lines += [f"Proposition: {prop}", "Proof:"]
    return "\n".join(lines)


def clean_output(text: str) -> str:
    """Extract the candidate proof term from the model's generation."""
    t = text.strip()
    if "Proof:" in t:
        t = t.split("Proof:")[-1]
    t = t.replace("`", "")
    for line in t.splitlines():
        line = line.strip()
        if line:
            return line.rstrip(".").strip()
    return ""


# --------------------------------------------------------------------------- #
# PHASE 1 — kernel as proof checker (no GPU)                                    #
# --------------------------------------------------------------------------- #
def run_kernel(args) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    floor_ok = True
    for t in positives():
        r = check_proof(t.ref_proof, t.prop)
        floor_ok &= r.valid
        records.append({
            "id": t.id, "prop": t.prop, "provable": True,
            "ref_proof": t.ref_proof, "verdict": r.verdict, "valid": r.valid,
            "principal": r.principal, "normal_form": r.normal_form,
        })

    # The consistency firewall, made concrete: Y types the Y-trap, sound gate rejects.
    from verbum.lambda_ast import parse, typecheck  # local: phase-1 only
    from verbum.proof_kernel import pretty_prop
    y_cat = typecheck(parse("Y")).cat
    y_trap = next(t for t in negatives() if t.y_trap)
    y_sound = check_proof("Y", y_trap.prop)            # sound gate
    firewall = {
        "prop": y_trap.prop,
        "Y_principal_type": pretty_prop(y_cat) if y_cat else None,
        "sound_gate_verdict": y_sound.verdict,
        "firewall_holds": y_sound.verdict == Verdict.UNSOUND_RECURSION,
    }

    # Negatives: confirm a sweep of tempting sound terms never validates one.
    tempting = ["I", "K", "S", "B", "C", "W", "K I", "C I", "S K K", "B B"]
    neg_records = []
    soundness_ok = True
    for t in negatives():
        falsely = [tm for tm in tempting if check_proof(tm, t.prop).valid]
        soundness_ok &= (len(falsely) == 0)
        neg_records.append({
            "id": t.id, "prop": t.prop, "y_trap": t.y_trap,
            "falsely_proved_by": falsely,
        })

    out = {
        "phase": "kernel (proof checker)",
        "timestamp": datetime.now(UTC).isoformat(),
        "floor_all_positives_valid": floor_ok,
        "soundness_no_negative_falsely_proved": soundness_ok,
        "consistency_firewall": firewall,
        "positives": records,
        "negatives": neg_records,
        "git_sha": git_sha(),
    }
    (RESULTS_DIR / "kernel.json").write_text(json.dumps(out, indent=2))
    log("")
    log("  === PHASE 1 — KERNEL AS PROOF CHECKER ===")
    log(f"  floor (all {len(records)} positive ref-proofs VALID): {floor_ok}")
    for r in records:
        log(f"    {'OK ' if r['valid'] else 'XX '}{r['id']:16} {r['prop']:34} "
            f"{r['ref_proof']:6} -> {r['verdict']}")
    log(f"  soundness (no negative falsely proved by {len(tempting)} sound terms): "
        f"{soundness_ok}")
    log(f"  consistency firewall: Y : {firewall['Y_principal_type']}  "
        f"=> check_proof(Y, {y_trap.prop}) = {firewall['sound_gate_verdict']}  "
        f"(holds={firewall['firewall_holds']})")
    log("  wrote kernel.json")
    if not (floor_ok and soundness_ok and firewall["firewall_holds"]):
        sys.exit(1)


# --------------------------------------------------------------------------- #
# PHASE 2 — the LLM as prover (GPU)                                            #
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
    log(f"[{args.model}] {len(tasks)} proof tasks "
        f"({'chat' if used_chat else 'base/raw'} prompt)")

    records = []
    with torch.no_grad():
        for i, task in enumerate(tasks):
            prompt = build_prompt(task.prop)
            text = None
            if getattr(tok, "chat_template", None):
                msg = [{"role": "user", "content": prompt}]
                try:
                    text = tok.apply_chat_template(
                        msg, tokenize=False, add_generation_prompt=True,
                        enable_thinking=False)
                except (TypeError, ValueError):
                    try:
                        text = tok.apply_chat_template(
                            msg, tokenize=False, add_generation_prompt=True)
                    except (TypeError, ValueError):
                        text = None
            if text is None:
                text = prompt  # base model (no chat template): raw few-shot cue
            enc = tok(text, return_tensors="pt").to(args.device)
            out = model.generate(**enc, max_new_tokens=24, do_sample=False,
                                 pad_token_id=tok.pad_token_id or tok.eos_token_id)
            gen = tok.decode(out[0][enc["input_ids"].shape[1]:],
                             skip_special_tokens=True)
            cand = clean_output(gen)
            chk = check_proof(cand, task.prop)
            # correct: positives -> a VALID proof; negatives -> NOT a valid proof
            correct = chk.valid if task.provable else (not chk.valid)
            records.append({
                "id": task.id, "prop": task.prop, "provable": task.provable,
                "complexity": task.complexity, "y_trap": task.y_trap,
                "model_output": cand, "verdict": chk.verdict, "valid": chk.valid,
                "principal": chk.principal, "normal_form": chk.normal_form,
                "correct": correct, "ref_proof": task.ref_proof,
            })
            if (i + 1) % 5 == 0:
                log(f"    {i + 1}/{len(tasks)}")

    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()
    elif args.device == "cuda":
        torch.cuda.empty_cache()

    pos = [r for r in records if r["provable"]]
    neg = [r for r in records if not r["provable"]]
    n_sens = sum(r["valid"] for r in pos)
    n_spec = sum(not r["valid"] for r in neg)
    # any negative falsely "proved" is alarming (checker bug or a Y-style trick)
    false_proofs = [r for r in neg if r["valid"]]
    by_cx: dict[int, dict] = {}
    for r in pos:
        c = r["complexity"]
        d = by_cx.setdefault(c, {"n": 0, "proved": 0})
        d["n"] += 1
        d["proved"] += int(r["valid"])
    verdict_hist: dict[str, int] = {}
    for r in records:
        verdict_hist[r["verdict"]] = verdict_hist.get(r["verdict"], 0) + 1

    out = {
        "model": args.model, "dtype": args.dtype,
        "prompt_mode": "chat" if used_chat else "base/raw",
        "register": "functional (learned prover, kernel-verified)",
        "timestamp": datetime.now(UTC).isoformat(),
        "n": len(records), "n_positive": len(pos), "n_negative": len(neg),
        "sensitivity": round(n_sens / max(len(pos), 1), 4),
        "specificity": round(n_spec / max(len(neg), 1), 4),
        "false_proofs": false_proofs,
        "by_complexity": {str(k): {**v, "rate": round(v["proved"] / v["n"], 3)}
                          for k, v in sorted(by_cx.items())},
        "verdict_hist": verdict_hist,
        "records": records,
        "git_sha": git_sha(), "elapsed_s": round(time.time() - t0, 1),
    }
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))

    log("")
    log(f"  === {args.model} proof-as-inhabitation ===")
    log(f"  sensitivity (positives proved) {out['sensitivity']:.3f} "
        f"({n_sens}/{len(pos)});  specificity (negatives held) "
        f"{out['specificity']:.3f} ({n_spec}/{len(neg)})")
    if false_proofs:
        log(f"  !! {len(false_proofs)} NEGATIVE(S) FALSELY PROVED:")
        for r in false_proofs:
            log(f"     {r['id']} {r['prop']!r} <- {r['model_output']!r} "
                f"({r['verdict']})")
    log("  by complexity (positives): "
        + "  ".join(f"d{k}:{v['proved']}/{v['n']}"
                    for k, v in out["by_complexity"].items()))
    log("  verdicts: " + "  ".join(f"{k}={v}" for k, v in verdict_hist.items()))
    log("  failures (positives not proved):")
    for r in pos:
        if not r["valid"]:
            log(f"    {r['id']:16} {r['prop']:30} got={r['model_output']!r} "
                f"-> {r['verdict']} (ref={r['ref_proof']})")
    log(f"  wrote {safe}.json  ({out['elapsed_s']}s)")


# --------------------------------------------------------------------------- #
# aggregate                                                                    #
# --------------------------------------------------------------------------- #
def run_aggregate(args) -> None:
    files = sorted(f for f in RESULTS_DIR.glob("*.json")
                   if f.stem not in ("aggregate", "kernel"))
    if not files:
        log(f"no model jsons in {RESULTS_DIR}")
        sys.exit(1)
    models = [json.loads(f.read_text()) for f in files]
    rows = [{"model": m["model"], "sensitivity": m["sensitivity"],
             "specificity": m["specificity"],
             "false_proofs": len(m["false_proofs"]),
             "by_complexity": m["by_complexity"]} for m in models]
    out = {"models": [m["model"] for m in models], "rows": rows,
           "git_sha": git_sha(), "timestamp": datetime.now(UTC).isoformat()}
    (RESULTS_DIR / "aggregate.json").write_text(json.dumps(out, indent=2))
    log("")
    log("  === PROOF-AS-INHABITATION (kernel-verified) ===")
    log(f"  {'model':>24} {'sens':>5} {'spec':>5} {'falseP':>6}")
    for r in rows:
        log(f"  {r['model']:>24} {r['sensitivity']:>5.2f} "
            f"{r['specificity']:>5.2f} {r['false_proofs']:>6}")
    log("  wrote aggregate.json")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["kernel", "model", "aggregate"],
                    default="kernel")
    ap.add_argument("-m", "--model", default="Qwen/Qwen3-32B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    args = ap.parse_args()
    if args.mode == "kernel":
        run_kernel(args)
    elif args.mode == "model":
        run_model(args)
    else:
        run_aggregate(args)


if __name__ == "__main__":
    main()
