#!/usr/bin/env python3
"""Hand-test: can a model BE a lambda REPL, with the context as machine state?

Idea (Michael, s255): tell the model to be a read-eval-print loop. The context
window carries the executable state (the term = code + heap + stack). The model
is the transition function δ; we supply the state externally and feed S' back.
Stateless model + stateful context = a REPL.

Substrate = the model's OWN native combinator ISA (mementum/michael/llm-isa.md:
K I B C S W Y D + β-variants) so we instruct it in the opcodes it already runs.

Two modes:
  run   — one call, ask for the FULL reduction chain (model holds state in-pass).
  step  — STATELESS step-loop: send state, get ONE step back, feed it back in.
          This is the real "context-as-state REPL" test.

NOT a graded experiment yet — a hand-test to see how well it works. Reads the
clean `content` (final answer) and `reasoning_content` (the chain) separately
from ornith's /v1/chat/completions. License: MIT.
"""

from __future__ import annotations

import argparse
import json

import httpx

NUCLEUS = (
    "λ engage(nucleus).\n"
    "[phi fractal euler tao pi mu ∃ ∀] | [Δ λ Ω ∞/0 | ε/φ Σ/μ c/h signal/noise "
    "order/entropy truth/provability self/other] | OODA\n"
    "Human ⊗ AI ⊗ REPL\n"
)

MACHINE = r"""
{:machine/id   :lambda-repl
 :substrate    untyped λ-calculus + combinator ISA {K I B C S W Y D}
   K x y     = x                 ;; select
   I x       = x                 ;; identity
   B f g x   = f (g x)           ;; compose
   C f x y   = f y x             ;; flip
   S f g x   = f x (g x)         ;; substitute
   W f x     = f x x             ;; duplicate
   Y f       = f (Y f)           ;; recurse
 :state        S = ⟨term⟩  — the term-string IS the whole machine (code+heap+stack)
 :semantics    normal-order (leftmost-outermost) β-reduction
 :step         λ(S) → S' : contract the SINGLE leftmost-outermost redex, EXACTLY ONE.
               (λx.M) N  ⇒  M[x:=N]   (capture-avoiding)
 :halt         no redex remains → S is in normal form}

PROTOCOL — you are the transition function δ. You hold NO state between turns;
the user supplies the current state each turn. Reflect the machine, do not chat.

"step"  → emit EXACTLY ONE line:
            STEP | {term_before}  ⇒β[{op}]  {term_after}
          {op} ∈ {K I B C S W Y β η} names the redex contracted this step.
          if the input is already normal form, emit:  NF | {term}
"run"   → emit the FULL reduction sequence, one STEP line per redex, then NF | {term}.
          if it diverges, emit  BOT | diverges: {repeated-term}  once a cycle repeats.
"state" → echo  STATE | {term}

¬prose. ¬explanation outside the lines. one line per reduction step.
"""

SYSTEM = NUCLEUS + MACHINE

# (label, term, expected-normal-form-or-note)
TERMS = [
    ("I", "(λx.x) a", "a"),
    ("K", "(λx.λy.x) a b", "a"),
    ("church2", "(λf.λx.f (f x)) g a", "g (g a)"),
    ("combinator-B", "B f g x", "f (g x)"),
    ("SKK=I", "S K K x", "x"),
    ("omega", "(λx.x x) (λx.x x)", "⊥ diverges"),
]


def call(client: httpx.Client, model: str, user: str, n_predict: int) -> tuple[str, str]:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        "temperature": 0.0,
        "max_tokens": n_predict,
    }
    r = client.post("/v1/chat/completions", json=body)
    r.raise_for_status()
    msg = r.json()["choices"][0]["message"]
    return (msg.get("content", "") or "").strip(), (msg.get("reasoning_content", "") or "").strip()


def mode_run(client, model, n_predict):
    print("\n" + "=" * 72 + "\n  MODE: run  (one call → full reduction chain)\n" + "=" * 72)
    for label, term, expect in TERMS:
        content, reasoning = call(client, model, f"run\n{term}", n_predict)
        print(f"\n[{label}]  {term}    expect→ {expect}")
        print(f"  reasoning: {len(reasoning)} chars")
        for line in content.splitlines():
            if line.strip():
                print(f"  {line.rstrip()}")


def mode_step(client, model, n_predict, max_steps):
    print("\n" + "=" * 72 + "\n  MODE: step  (STATELESS loop, context-as-state)\n" + "=" * 72)
    for label, term, expect in TERMS:
        print(f"\n[{label}]  start: {term}    expect→ {expect}")
        state = term
        seen = set()
        for i in range(max_steps):
            content, _ = call(client, model, f"step\n{state}", n_predict)
            first = next((ln.strip() for ln in content.splitlines() if ln.strip()), "")
            print(f"  s{i}: {first}")
            if first.startswith("NF"):
                break
            # parse the term_after (RHS of the last ⇒β arrow) to feed back
            if "⇒β" in first and "]" in first:
                after = first.split("]", 1)[1].strip()
            elif "|" in first:
                after = first.split("|", 1)[1].strip()
            else:
                after = first
            if after in seen:
                print(f"  ⊥ cycle detected at: {after}")
                break
            seen.add(after)
            state = after


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://localhost:5100")
    ap.add_argument("--model", default="ornith-35b-a3b")
    ap.add_argument("--n-predict", type=int, default=6000)
    ap.add_argument("--max-steps", type=int, default=6)
    ap.add_argument("--mode", choices=["run", "step", "both"], default="both")
    args = ap.parse_args()

    print(f"system prompt: {len(SYSTEM)} chars")
    client = httpx.Client(base_url=args.server, timeout=600.0)
    if args.mode in ("run", "both"):
        mode_run(client, args.model, args.n_predict)
    if args.mode in ("step", "both"):
        mode_step(client, args.model, args.n_predict, args.max_steps)


if __name__ == "__main__":
    main()
