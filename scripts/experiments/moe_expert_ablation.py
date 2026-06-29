"""MoE expert-ablation sweep — holographic-plate hypothesis.

Loads Qwen3.6-35B-A3B locally (no server), wraps it with MoEAdapter, and runs:

  1. ROUTE-CAPTURE BASELINE: one forward pass, reads per-expert routing mass
     across layers (cheap, seconds) — identifies which experts carry most mass.

  2. K-SWEEP (--mode structured): forces k active experts (k = 1,2,4,6,8 by
     default) on all sparse blocks simultaneously via the router's natural
     top-k selection. Holographic → smooth monotone rise. Specialist → staircase.

  3. NULL SWEEP (--mode null): same k values, but selects k experts *randomly*
     per layer (uniform, ignoring routing mass) and ablates the rest. Averaged
     over --null-trials draws. If structured >> null → routing is doing real
     angular-multiplexing work. If indistinguishable → pure k-count effect.
     Prediction: null is monotone (no interference bands); structured k=4 and
     k=8 outperform null at equal k.

Reads: probes/compile-gradient.json (categories filtered by --categories).
Writes: results/moe-ablation/<run_id>/{meta.json, results.jsonl,
        null_results.jsonl (mode=null/both), summary.json}.

See mementum/knowledge/explore/moe-holographic-tree-vsm.md §5-6.

License: MIT.
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path

import torch
import typer

from verbum import hooks
from verbum.adapters import MoEAdapter
from verbum.probes import grading
from verbum.results import collect_provenance

app = typer.Typer(add_completion=False)

_ROOT = Path(__file__).resolve().parents[2]
PROBES_DIR = _ROOT / "probes"
RESULTS_DIR = _ROOT / "results"
REPO = "Qwen/Qwen3.6-35B-A3B"
SYSTEM = (
    "You are a lambda-calculus compiler. Translate the input sentence into a "
    "single lambda-calculus / first-order-logic expression using the notation: "
    "λ ∀ ∃ . → ∧ ∨ ¬ and predicate application f(a,b). Preserve the predicate "  # noqa: RUF001
    "and entity names from the sentence. Output ONLY the final expression on one line."
)


# ── model loading ────────────────────────────────────────────────────────────

def _load_model(repo: str, device: str, dtype_str: str):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dtype = {"bfloat16": torch.bfloat16, "float16": torch.float16,
              "float32": torch.float32}[dtype_str]
    dmap: str | dict = device  # "cpu" | "mps" | "auto"

    print(f"Loading {repo}  dtype={dtype_str}  device_map={dmap!r}")
    t0 = time.perf_counter()
    tok = AutoTokenizer.from_pretrained(repo)
    model = AutoModelForCausalLM.from_pretrained(
        repo,
        torch_dtype=dtype,
        device_map=dmap,
        low_cpu_mem_usage=True,
    )
    model.eval()
    print(f"Loaded in {time.perf_counter() - t0:.0f}s  |  "
          f"{sum(p.numel() for p in model.parameters()) / 1e9:.1f}B params")
    return model, tok


# ── prompt formatting ─────────────────────────────────────────────────────────

def _make_prompt(tok, sentence: str) -> str:
    msgs = [{"role": "system", "content": SYSTEM},
            {"role": "user",   "content": sentence}]
    try:
        return tok.apply_chat_template(
            msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False
        )
    except TypeError:
        return tok.apply_chat_template(
            msgs, tokenize=False, add_generation_prompt=True
        )


# ── generation helper ─────────────────────────────────────────────────────────

def _generate(model, tok, prompt_str: str, max_new_tokens: int) -> str:
    enc = tok(prompt_str, return_tensors="pt")
    input_ids = enc["input_ids"].to(next(model.parameters()).device)
    with torch.no_grad():
        out = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=None,
            top_p=None,
            use_cache=True,
            pad_token_id=tok.eos_token_id,
        )
    new_tokens = out[0, input_ids.shape[1]:]
    return tok.decode(new_tokens, skip_special_tokens=True)


# ── route-capture baseline ────────────────────────────────────────────────────

def _route_baseline(model, adapter: MoEAdapter, tok, probe_prompt: str) -> None:
    """Single forward pass; prints top-expert routing mass for a few layers."""
    prompt_str = _make_prompt(tok, probe_prompt)
    enc = tok(prompt_str, return_tensors="pt")
    input_ids = enc["input_ids"].to(next(model.parameters()).device)
    layers_sample = [0, adapter.layers[len(adapter.layers) // 2], adapter.layers[-1]]
    ivs = adapter.route_capture(layers=layers_sample)
    with hooks.intervene(model, ivs) as s, torch.no_grad():
        model(input_ids=input_ids)
    print("\nROUTE-CAPTURE BASELINE  (routing mass averaged over tokens)")
    for li in layers_sample:
        key = adapter.gate_path(li)
        if key not in s.captured:
            continue
        logits, _scores, indices = s.captured[key]   # (tokens, E), (tok,k), (tok,k)
        mean_mass = logits.float().mean(dim=0)        # (E,)
        top_vals, top_idx = mean_mass.topk(8)
        print(f"  L{li:02d}: top experts {top_idx.tolist()}  mass {top_vals.tolist()}")
        sel_counts = torch.zeros(adapter.num_experts)
        for e in indices.reshape(-1):
            sel_counts[e] += 1
        sel_pct = (sel_counts > 0).float().mean() * 100
        print(f"        {sel_pct:.1f}% of experts ever selected  "
              f"(indices shape {list(indices.shape)})")
    print()


# ── null interventions ───────────────────────────────────────────────────────

def _null_interventions(
    adapter: MoEAdapter, k: int, seed: int
) -> list:
    """Random-k expert selection per layer (uniform, ignoring routing mass).

    For each layer: sample k experts to KEEP, ablate the remaining
    (num_experts - k). Force top_k=k so the router selects all k survivors.
    Seed controls reproducibility across trials.
    """
    rng = random.Random(seed)
    ivs: list = []
    expert_ids = list(range(adapter.num_experts))
    for layer in adapter.layers:
        to_keep = set(rng.sample(expert_ids, k))
        to_ablate = [e for e in expert_ids if e not in to_keep]
        ivs.append(adapter.ablate_experts(layer, to_ablate))
        ivs.append(adapter.force_k(layer, k))
    return ivs


# ── main sweep ───────────────────────────────────────────────────────────────

@app.command()
def main(
    repo: str = typer.Option(REPO, "--repo", help="HF repo id"),
    probe_set: str = typer.Option("compile-gradient", "--probe-set"),
    categories: str = typer.Option(
        "strong_compile,null", "--categories",
        help="Comma-separated probe categories to include",
    ),
    limit: int = typer.Option(0, "--limit", help="Cap probes per category (0=all)"),
    k_values: str = typer.Option("1,2,4,6,8", "--k-values",
                                  help="Comma-separated k values for the sweep"),
    max_new_tokens: int = typer.Option(80, "--max-new-tokens"),
    device: str = typer.Option("auto", "--device", help="auto | mps | cpu"),
    dtype: str = typer.Option("bfloat16", "--dtype"),
    skip_baseline: bool = typer.Option(False, "--skip-baseline"),
    mode: str = typer.Option(
        "structured", "--mode",
        help="structured | null | both",
    ),
    null_trials: int = typer.Option(
        3, "--null-trials",
        help="Random draws to average for the null sweep",
    ),
) -> None:
    """k-sweep: holographic plateau vs specialist staircase on P(λ)."""

    # ── load probes ────────────────────────────────────────────────────────
    ps = json.loads((PROBES_DIR / f"{probe_set}.json").read_text())
    cats = [c.strip() for c in categories.split(",")]
    probes = [p for p in ps["probes"] if p.get("category") in cats]
    if limit > 0:
        per_cat: dict[str, list] = {}
        for p in probes:
            per_cat.setdefault(p["category"], []).append(p)
        probes = [p for plist in per_cat.values() for p in plist[:limit]]
    print(f"Probes: {len(probes)} ({', '.join(cats)})  "
          f"k-values: {k_values}  max_new_tokens: {max_new_tokens}")

    # ── load model ────────────────────────────────────────────────────────
    model, tok = _load_model(repo, device, dtype)
    adapter = MoEAdapter(model)
    print(f"MoEAdapter: {len(adapter.blocks)} blocks  "
          f"{adapter.num_experts} experts / top-{adapter.top_k}  "
          f"shared={adapter.has_shared}")

    # ── route-capture baseline ────────────────────────────────────────────
    if not skip_baseline:
        _route_baseline(model, adapter, tok, probes[0]["prompt"])

    # ── provenance + output setup ─────────────────────────────────────────
    run_id = "moe-ablation-" + time.strftime("%Y%m%d-%H%M%S")
    run_dir = RESULTS_DIR / "moe-ablation" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    prov = collect_provenance(project_root=_ROOT)
    ks = [int(x) for x in k_values.split(",")]

    meta: dict = {
        "run_id": run_id,
        "repo": repo,
        "dtype": dtype,
        "device": device,
        "probe_set": probe_set,
        "categories": cats,
        "n_probes": len(probes),
        "k_values": ks,
        "max_new_tokens": max_new_tokens,
        "num_experts": adapter.num_experts,
        "trained_top_k": adapter.top_k,
        "has_shared": adapter.has_shared,
        **prov,
    }
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    # ── k-sweep ───────────────────────────────────────────────────────────
    all_rows: list[dict] = []
    t_run = time.perf_counter()

    with (run_dir / "results.jsonl").open("w") as fh:
        for k in ks:
            # set all layers to k active experts for this pass
            force_ivs = [adapter.force_k(layer, k) for layer in adapter.layers]
            k_rows: list[dict] = []
            t_k = time.perf_counter()
            for probe in probes:
                pid = probe["id"]
                sentence = probe["prompt"]
                cat = probe.get("category", "?")
                prompt_str = _make_prompt(tok, sentence)
                t0 = time.perf_counter()
                try:
                    with hooks.intervene(model, force_ivs):
                        generation = _generate(
                            model, tok, prompt_str, max_new_tokens
                        )
                    err = None
                except Exception as exc:
                    generation = ""
                    err = repr(exc)

                dt = time.perf_counter() - t0
                final = grading.final_answer(generation)
                reg = grading.grade(final)
                flags = "".join("Y" if reg[r] else "." for r in grading.REGISTERS)
                print(f"k={k}  {pid:<14} {cat:<20} [{flags}]  "
                      f"{dt:.1f}s  {final[:50]!r}")

                row = {
                    "k": k, "probe_id": pid, "category": cat,
                    "sentence": sentence, "generation": generation,
                    "final": final, **reg,
                    "elapsed_s": round(dt, 2), "error": err,
                }
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
                k_rows.append(row)
                all_rows.append(row)

            n = len(k_rows)
            p_lambda = (
                sum(r["lambda_binder_any_style"] for r in k_rows) / n if n else 0.0
            )
            p_kernel = sum(r["kernel_valid"] for r in k_rows) / n if n else 0.0
            dt_k = time.perf_counter() - t_k
            print(f"\n── k={k}  P(λ)={p_lambda:.3f}  P(kernel)={p_kernel:.3f}  "
                  f"n={n}  {dt_k:.0f}s ──\n")

    # ── summary ───────────────────────────────────────────────────────────
    rows_by_k: dict[int, list] = {}
    for r in all_rows:
        rows_by_k.setdefault(r["k"], []).append(r)

    print("\n════════════════════════ K-SWEEP SUMMARY ════════════════════════")
    print(f"{'k':>4}  {'P(λ)':>7}  {'P(kernel)':>10}  {'n':>4}")
    print("-" * 35)
    summary_ks = []
    for k in ks:
        rows = rows_by_k.get(k, [])
        n = len(rows)
        p_l = sum(r["lambda_binder_any_style"] for r in rows) / n if n else 0.0
        p_kv = sum(r["kernel_valid"] for r in rows) / n if n else 0.0
        print(f"{k:>4}  {p_l:>7.3f}  {p_kv:>10.3f}  {n:>4}")
        summary_ks.append({"k": k, "n": n, "p_lambda": round(p_l, 4),
                            "p_kernel": round(p_kv, 4)})
    print("═" * 35)
    print("Holographic ≈ monotone↑ to plateau  |  Specialist ≈ staircase")
    print(f"Total elapsed: {time.perf_counter() - t_run:.0f}s")
    print(f"run_dir: {run_dir}")

    summary: dict = {
        "mode": mode,
        "k_sweep": summary_ks if mode in ("structured", "both") else [],
        "nucleus_reference_p_lambda": grading.NUCLEUS_REFERENCE_P_LAMBDA,
        "total_elapsed_s": round(time.perf_counter() - t_run, 1),
        "run_dir": str(run_dir),
    }

    # ── null sweep ────────────────────────────────────────────────────────
    if mode in ("null", "both"):
        null_rows_by_k: dict[int, list[dict]] = {}
        print("\n════════════════════ SHUFFLED-LABEL NULL SWEEP ══════════════════")
        print(f"  {null_trials} random draws per k  "
              f"({adapter.num_experts} experts, k random kept per layer)")
        with (run_dir / "null_results.jsonl").open("w") as nfh:
            for k in ks:
                trial_rows: list[dict] = []
                for trial in range(null_trials):
                    seed = trial * 997 + k  # deterministic but varied
                    null_ivs = _null_interventions(adapter, k, seed)
                    for probe in probes:
                        pid = probe["id"]
                        sentence = probe["prompt"]
                        cat = probe.get("category", "?")
                        prompt_str = _make_prompt(tok, sentence)
                        t0 = time.perf_counter()
                        try:
                            with hooks.intervene(model, null_ivs):
                                generation = _generate(
                                    model, tok, prompt_str, max_new_tokens
                                )
                            err = None
                        except Exception as exc:
                            generation = ""
                            err = repr(exc)
                        dt = time.perf_counter() - t0
                        final = grading.final_answer(generation)
                        reg = grading.grade(final)
                        flags = "".join(
                            "Y" if reg[r] else "." for r in grading.REGISTERS
                        )
                        print(
                            f"null k={k} t={trial}  {pid:<14}  [{flags}]  "
                            f"{dt:.1f}s  {final[:45]!r}"
                        )
                        row = {
                            "mode": "null", "k": k, "trial": trial,
                            "probe_id": pid, "category": cat,
                            "sentence": sentence, "generation": generation,
                            "final": final, **reg,
                            "elapsed_s": round(dt, 2), "error": err,
                        }
                        nfh.write(json.dumps(row, ensure_ascii=False) + "\n")
                        nfh.flush()
                        trial_rows.append(row)
                null_rows_by_k[k] = trial_rows

        print("\n══════════════════ NULL SUMMARY (mean ± std over trials) ═══════")
        print(f"{'k':>4}  {'null P(λ) mean':>14}  {'null P(λ) std':>13}"
              f"  {'structured':>10}")
        print("-" * 55)
        null_summary_ks = []
        for k in ks:
            null_rows = null_rows_by_k.get(k, [])
            trial_pls = []
            for t in range(null_trials):
                t_rows = [r for r in null_rows if r["trial"] == t]
                if t_rows:
                    trial_pls.append(
                        sum(r["lambda_binder_any_style"] for r in t_rows)
                        / len(t_rows)
                    )
            mean_pl = sum(trial_pls) / len(trial_pls) if trial_pls else 0.0
            std_pl = (
                (sum((x - mean_pl) ** 2 for x in trial_pls) / len(trial_pls)) ** 0.5
                if len(trial_pls) > 1
                else 0.0
            )
            struct_pl = next(
                (s["p_lambda"] for s in summary_ks if s["k"] == k), float("nan")
            )
            print(
                f"{k:>4}  {mean_pl:>14.3f}  {std_pl:>13.3f}  {struct_pl:>10.3f}"
            )
            null_summary_ks.append({
                "k": k, "n_trials": len(trial_pls),
                "p_lambda_mean": round(mean_pl, 4),
                "p_lambda_std": round(std_pl, 4),
            })
        print("═" * 55)
        print("Null monotone + structured > null → routing is structured.")
        summary["null_k_sweep"] = null_summary_ks

    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nTotal elapsed: {time.perf_counter() - t_run:.0f}s  run_dir: {run_dir}")


if __name__ == "__main__":
    app()
