#!/usr/bin/env python3
# register: behavioral/output
"""Cross-model OUTPUT consensus — do independent-lineage models AGREE on the
compile output, and does agreement predict correctness?

THE IDEA (this session, Michael):
  Build teaching data only from where independent model ARCHITECTURES agree.
  Consensus = fitness function. Lambda/FOL probes have GROUND TRUTH, so we can
  CALIBRATE consensus-as-truth here (agreement -> P(correct)) before trusting it
  on prose where ground truth is absent.

  Output consensus needs NO frame alignment (cf combinator_map_consensus.py): the
  generated strings already share a space (the answer). This is the cheap register.

THE INSTRUMENT (this script):
  inputs : a gated probe set (default probes/binding.json) resolved via the
           loader -> full_prompt = gate_content + prompt (few-shot completion).
  models : cross-lineage pair (default Qwen/Qwen3-14B + allenai/OLMo-2-1124-13B).
           13B+ so the lambda function is "fully formed" (small models = immature
           circuits). Loaded one at a time via transformers (MPS, bf16), greedy.
  gen    : do_sample=False (deterministic), first completion line, leading arrow
           stripped. Written per-model to results/consensus-output/<safe>.jsonl.
  flags  : a probe whose prompt appears verbatim in the gate is a LEAK
           (in_gate=true) and is excluded from headline stats by the analyzer.

  Phase 2 (the analyzer, --analyze runs it after gen, or alone) computes:
    - cross-model agreement rate (normalized exact + token Jaccard),
    - the CALIBRATION: P(correct|agree) vs P(correct|disagree) vs ground_truth,
    - per-model overall correctness.

Usage:
  uv run python scripts/experiments/consensus_output_agreement.py
  uv run python scripts/experiments/consensus_output_agreement.py --analyze-only
  uv run python scripts/experiments/consensus_output_agreement.py \
      --models Qwen/Qwen3-14B allenai/OLMo-2-1124-13B --probe-set probes/binding.json

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import re
import subprocess
import sys
import time
import unicodedata
from itertools import combinations
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from verbum.probes import load_probe_set, resolve_probes  # noqa: E402

OUT_DIR = _PROJECT_ROOT / "results" / "consensus-output"
DEFAULT_MODELS = ["Qwen/Qwen3-14B", "allenai/OLMo-2-1124-13B"]


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=_PROJECT_ROOT,
            text=True).strip()
    except Exception:
        return "unknown"


def safe_name(model: str) -> str:
    return model.replace("/", "_")


def _r(x, nd: int = 3):
    """Round, passing through None."""
    return round(x, nd) if isinstance(x, (int, float)) else x


# ─────────────────────────── normalization / scoring ──────────────────────────

_ARROW = re.compile(r"^\s*(?:→|->|=>|\\Rightarrow)\s*")


def first_line(text: str) -> str:
    """First non-empty line of a completion, leading arrow stripped."""
    for ln in text.splitlines():
        ln = ln.strip()
        if ln:
            return _ARROW.sub("", ln).strip()
    return ""


_MARKER = re.compile(r"^(?:output|input|answer|result)\s*:\s*", re.I)


def parse_answer(raw: str) -> str:
    """Robustly extract the FOL/lambda answer across model output formats.

    OLMo emits ' → <fol>' on line 1; Qwen3 emits 'Output:\\n<fol>'. Skip empty,
    marker-only ('Output:'), and arrow-only lines; strip leading markers/arrows;
    return the first line with real content.
    """
    for ln in raw.splitlines():
        s = ln.strip()
        if not s:
            continue
        s = _MARKER.sub("", s)
        s = _ARROW.sub("", s).strip()
        if s:
            return s
    return ""


# ── canonicalization: predicate stemming + lowercasing kills the dominant
#    FOL scoring noise (fly/can_fly, love/loves, pass/passed, John/john) that
#    otherwise suppresses correctness AND fakes agreed-errors (s245 finding).
_MODAL = re.compile(r"^(?:can|could|will|would|shall|should|may|might|must)_")
_VOWEL = re.compile(r"[aeiouy]")
_TOK = re.compile(r"[A-Za-z_][A-Za-z_0-9]*|[0-9]+|[∀∃→∧∨¬ιλ∘.()=,!]")


def _stem(w: str) -> str:
    """Light Porter-style step-1 stem (consistency, not linguistics): strips
    modal_ prefix, plural -s/-ies/-sses, and (*v*)ed/ing. love/loves→love,
    pass/passed→pass, can_fly→fly."""
    w = _MODAL.sub("", w.lower())
    if w.endswith("sses"):
        w = w[:-2]
    elif w.endswith("ies") and len(w) > 4:
        w = w[:-3] + "y"
    elif w.endswith("ss"):
        pass
    elif w.endswith("s") and len(w) > 2:
        w = w[:-1]
    if w.endswith("eed"):
        pass
    elif w.endswith("ed") and _VOWEL.search(w[:-2]):
        w = w[:-2]
    elif w.endswith("ing") and _VOWEL.search(w[:-3]):
        w = w[:-3]
    return w


def _canon_toks(s: str) -> list[str]:
    """Tokenize and canonicalize: identifiers stemmed+lowercased, operators kept."""
    s = unicodedata.normalize("NFC", _ARROW.sub("", s.strip()))
    out = []
    for t in _TOK.findall(s):
        out.append(_stem(t) if t[0].isalpha() or t[0] == "_" else t)
    return out


def norm(s: str) -> str:
    """Canonical string: stemmed/lowercased identifiers, no whitespace."""
    return "".join(_canon_toks(s)).rstrip(".")


def tokens(s: str) -> set[str]:
    return set(_canon_toks(s))


def jaccard(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


# ─────────────────────────── generation ───────────────────────────────────────

def build_input(tok, rp, chat: bool) -> str:
    """Completion (raw few-shot, good for base models) or chat-templated
    (required by instruct models like Gemma that echo a raw completion)."""
    if not chat:
        return rp.full_prompt
    exemplars = rp.gate_content.replace("Input:", "").rstrip()
    body = f"{exemplars}\n{rp.prompt.strip()} →"
    user = ("Convert each English sentence into a first-order logic formula, "
            "following the examples. Reply with ONLY the formula.\n\n" + body)
    msgs = [{"role": "user", "content": user}]
    try:  # Qwen3 supports enable_thinking; others reject the kwarg
        return tok.apply_chat_template(msgs, add_generation_prompt=True,
                                       tokenize=False, enable_thinking=False)
    except TypeError:
        return tok.apply_chat_template(msgs, add_generation_prompt=True,
                                       tokenize=False)


def generate_for_model(model_name: str, resolved, device: str, dtype_str: str,
                       max_new_tokens: int, out_path: Path, chat: bool = False) -> None:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[dtype_str]
    log(f"[{model_name}] loading tokenizer + model ({dtype_str}, chat={chat}) ...")
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=dtype)
    model.to(device).eval()

    t0 = time.time()
    n = len(resolved)
    with out_path.open("w", encoding="utf-8") as fh:
        for i, rp in enumerate(resolved):
            enc = tok(build_input(tok, rp, chat), return_tensors="pt")
            enc = {k: v.to(device) for k, v in enc.items()}
            plen = enc["input_ids"].shape[1]
            with torch.no_grad():
                out = model.generate(
                    **enc, max_new_tokens=max_new_tokens, do_sample=False,
                    num_beams=1, pad_token_id=tok.eos_token_id,
                )
            new = out[0, plen:]
            text = tok.decode(new, skip_special_tokens=True)
            gen = first_line(text)
            rec = {
                "probe_id": rp.probe_id,
                "category": rp.category,
                "prompt": rp.prompt,
                "ground_truth": rp.ground_truth,
                "generation": gen,
                "raw_completion": text[:300],
                "in_gate": rp.prompt.strip() in rp.gate_content,
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
            log(f"    {i+1}/{n} {rp.probe_id}: {gen[:70]}")
    log(f"[{model_name}] done {n} probes in {time.time()-t0:.1f}s -> {out_path}")

    del model
    gc.collect()
    try:
        import torch as _t
        if device == "mps":
            _t.mps.empty_cache()
        elif device == "cuda":
            _t.cuda.empty_cache()
    except Exception:
        pass


# ─────────────────────────── analysis ─────────────────────────────────────────

def analyze(models: list[str], agree_jac: float = 0.85,
            correct_jac: float = 0.85) -> dict:
    per_model = {}
    for m in models:
        p = OUT_DIR / f"{safe_name(m)}.jsonl"
        if not p.exists():
            raise SystemExit(f"missing generations for {m}: {p} (run generation first)")
        recs = [json.loads(ln) for ln in p.read_text("utf-8").splitlines() if ln.strip()]
        per_model[m] = {r["probe_id"]: r for r in recs}

    probe_ids = sorted(set.intersection(*[set(d) for d in per_model.values()]))
    rows = []
    for pid in probe_ids:
        recs = {m: per_model[m][pid] for m in models}
        any_rec = next(iter(recs.values()))
        gt = any_rec["ground_truth"]
        in_gate = any_rec["in_gate"]
        # RE-PARSE from raw_completion to fix model-specific output formats
        # (Qwen 'Output:\n<fol>' vs OLMo ' → <fol>'); fall back to stored gen.
        gens = {m: (parse_answer(recs[m].get("raw_completion", ""))
                    or recs[m]["generation"]) for m in models}
        norms = {m: norm(gens[m]) for m in models}
        gt_n = norm(gt)
        empty = {m: norms[m] == "" for m in models}
        # pairwise agreement — normalized exact AND jaccard-threshold (FOL has
        # predicate-name / spacing variation that exact match punishes)
        pair_exact, pair_jac = [], []
        for a, b in combinations(models, 2):
            pair_exact.append(norms[a] == norms[b] and norms[a] != "")
            pair_jac.append(jaccard(gens[a], gens[b]))
        agree_exact = all(pair_exact) if pair_exact else False
        agree_jac_b = (all(j >= agree_jac for j in pair_jac)
                       and not any(empty.values())) if pair_jac else False
        jac_gt = {m: jaccard(gens[m], gt) for m in models}
        correct_exact = {m: (norms[m] == gt_n and gt_n != "") for m in models}
        correct_jac_b = {m: (jac_gt[m] >= correct_jac and not empty[m]) for m in models}
        rows.append({
            "probe_id": pid, "category": any_rec["category"], "in_gate": in_gate,
            "prompt": any_rec["prompt"], "ground_truth": gt,
            "generations": gens,
            "agree_exact": agree_exact,
            "agree_jac": agree_jac_b,
            "mean_pair_jaccard": round(sum(pair_jac) / len(pair_jac), 3) if pair_jac else None,
            "correct_exact": correct_exact,
            "correct_jac": correct_jac_b,
            "jaccard_vs_gt": {m: round(v, 3) for m, v in jac_gt.items()},
            "all_empty": all(empty.values()),
        })

    # headline stats exclude leaked-in-gate probes
    scored = [r for r in rows if not r["in_gate"]]
    n = len(scored)

    def calib(agree_key, correct_key):
        ag = [r for r in scored if r[agree_key]]
        dg = [r for r in scored if not r[agree_key]]
        pca = (sum(1 for r in ag if all(r[correct_key].values())) / len(ag)) if ag else None
        pcd = (sum(1 for r in dg if all(r[correct_key].values())) / len(dg)) if dg else None
        return {"n_agree": len(ag), "P_correct_given_agree": _r(pca),
                "n_disagree": len(dg), "P_correct_given_disagree": _r(pcd)}

    # ── FAILURE-MODE partition (jaccard register) ──
    def both_correct(r):
        return all(r["correct_jac"].values())
    def any_correct(r):
        return any(r["correct_jac"].values())

    fm = {
        "agreed_correct": [r["probe_id"] for r in scored
                           if r["agree_jac"] and both_correct(r)],
        "agreed_error": [r["probe_id"] for r in scored          # the BLIND SPOT
                         if r["agree_jac"] and not any_correct(r) and not r["all_empty"]],
        "agreed_abstain": [r["probe_id"] for r in scored if r["all_empty"]],
        "disagree": [r["probe_id"] for r in scored if not r["agree_jac"]
                     and not r["all_empty"]],
    }

    per_model_correct = {
        m: {"exact": _r(sum(1 for r in scored if r["correct_exact"][m]) / n if n else None),
            "jac": _r(sum(1 for r in scored if r["correct_jac"][m]) / n if n else None)}
        for m in models
    }
    mean_jac_cross = _r((sum(r["mean_pair_jaccard"] for r in scored) / n) if n else None)
    mean_jac_gt = {m: _r(sum(r["jaccard_vs_gt"][m] for r in scored) / n if n else None)
                   for m in models}

    out = {
        "register": "behavioral/output",
        "git_sha": git_sha(),
        "models": models,
        "thresholds": {"agree_jac": agree_jac, "correct_jac": correct_jac},
        "n_probes_total": len(rows),
        "n_probes_scored": n,
        "n_leaked_in_gate_excluded": len(rows) - n,
        "agreement_rate_exact": _r(sum(1 for r in scored if r["agree_exact"]) / n if n else None),
        "agreement_rate_jac": _r(sum(1 for r in scored if r["agree_jac"]) / n if n else None),
        "mean_cross_model_jaccard": mean_jac_cross,
        "calibration_exact": calib("agree_exact", "correct_exact"),
        "calibration_jac": calib("agree_jac", "correct_jac"),
        "failure_modes": {k: {"n": len(v), "probe_ids": v} for k, v in fm.items()},
        "per_model_correctness": per_model_correct,
        "mean_jaccard_vs_gt": mean_jac_gt,
        "rows": rows,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "consensus.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))

    # ── readable summary ──
    log("")
    log("  ════════ CROSS-MODEL OUTPUT CONSENSUS — calibration on FOL ════════")
    log(f"  models: {', '.join(models)}")
    log(f"  probes scored: {n}  (excluded {len(rows)-n} leaked-in-gate)")
    log(f"  thresholds: agree_jac>={agree_jac}  correct_jac>={correct_jac}")
    log(f"  agreement rate:  exact={out['agreement_rate_exact']}  "
        f"jaccard={out['agreement_rate_jac']}  (mean cross-jac={mean_jac_cross})")
    log("  ── CALIBRATION (does agreement predict correctness?) — jaccard register ──")
    c = out["calibration_jac"]
    log(f"    P(correct | AGREE)    = {c['P_correct_given_agree']}   (n={c['n_agree']})")
    log(f"    P(correct | DISAGREE) = {c['P_correct_given_disagree']}   (n={c['n_disagree']})")
    log("  ── FAILURE MODES ──")
    for k, v in out["failure_modes"].items():
        log(f"    {k:16s} n={v['n']:2d}  {v['probe_ids']}")
    log("  per-model correctness vs ground truth:")
    for m in models:
        pm = per_model_correct[m]
        log(f"    {m:32s} exact={pm['exact']}  jac={pm['jac']}  mean_jac_gt={mean_jac_gt[m]}")
    log(f"  wrote {OUT_DIR/'consensus.json'}")
    return out


# ─────────────────────────── main ─────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--probe-set", default="probes/binding.json")
    ap.add_argument("--gates-dir", default="gates")
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    ap.add_argument("--device", default="mps", choices=["mps", "cuda", "cpu"])
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--max-new-tokens", type=int, default=80)
    ap.add_argument("--chat", action="store_true",
                    help="use the tokenizer chat template (instruct models)")
    ap.add_argument("--agree-jac", type=float, default=0.85,
                    help="cross-model jaccard >= this counts as agreement")
    ap.add_argument("--correct-jac", type=float, default=0.85,
                    help="jaccard vs ground_truth >= this counts as correct")
    ap.add_argument("--force", action="store_true",
                    help="regenerate even if a model's JSONL already exists")
    ap.add_argument("--analyze-only", action="store_true",
                    help="skip generation; just (re)analyze existing JSONL")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not args.analyze_only:
        ps = load_probe_set(_PROJECT_ROOT / args.probe_set)
        resolved = resolve_probes(ps, _PROJECT_ROOT / args.gates_dir)
        log(f"probe set '{ps.id}' v{ps.version}: {len(resolved)} probes "
            f"(gate default '{ps.default_gate}')")
        for m in args.models:
            out_path = OUT_DIR / f"{safe_name(m)}.jsonl"
            if out_path.exists() and not args.force:
                log(f"[{m}] cached ({out_path}); skip (use --force to redo)")
                continue
            generate_for_model(m, resolved, args.device, args.dtype,
                               args.max_new_tokens, out_path, args.chat)

    analyze(args.models, args.agree_jac, args.correct_jac)


if __name__ == "__main__":
    main()
