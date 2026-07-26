#!/usr/bin/env python3
"""Multi-model opcode sweep — registry of configs + crystal tree restack.

Models are CONFIGS, not forks (s256 canonical-harness lesson): one entry per
model records how to run it; the same trace pipeline runs them all. After
tracing, every model-VSM stacks into the tree:

    layer -> register -> model -> family -> root(universal)

and the root's Gram is compared against the bundled consensus reference — the
cross-model universality headline, with per-family agreement and per-model
health visible at every level (dissent is a first-class output, not an error).

Usage:
    # restack whatever model_vsm artifacts already exist:
    uv run python opcodes/sweep.py --restack-only

    # trace any missing registry models on cpu-class, then restack:
    uv run python opcodes/sweep.py --tier small
    uv run python opcodes/sweep.py --tier large --device mps
    uv run python opcodes/sweep.py --models Qwen/Qwen3-0.6B,Qwen/Qwen3-4B

License: MIT.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_HERE))

from classify import load_consensus_gram  # noqa: E402
from vsm import VSMNode, load_tree, offdiag_corr, save_tree, stack  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "opcode-trace"


# ── the registry (configs, not forks) ────────────────────────────────────────


@dataclass(frozen=True)
class ModelSpec:
    model: str
    family: str
    tier: str            # "small" (cpu-ok) | "large" (mps/cuda recommended)
    device: str = "cpu"
    notes: str = ""

    @property
    def slug(self) -> str:
        return self.model.split("/")[-1].lower().replace(".", "-")


REGISTRY: tuple[ModelSpec, ...] = (
    # Qwen3 ladder (scale-sharpening family, s217/s220/s264)
    ModelSpec("Qwen/Qwen3-0.6B", "qwen3", "small"),
    ModelSpec("Qwen/Qwen3-4B", "qwen3", "large", "mps"),
    ModelSpec("Qwen/Qwen3-14B", "qwen3", "large", "mps"),
    ModelSpec("Qwen/Qwen3-32B", "qwen3", "large", "mps"),
    # hybrid linear+full attention (per-layer attn resolution)
    ModelSpec("Qwen/Qwen3.6-27B", "qwen3", "large", "mps",
              "hybrid GatedDeltaNet+attention"),
    # other architectures
    ModelSpec("google/gemma-4-31B-it", "gemma", "large", "mps",
              "nested language_model container"),
    ModelSpec("allenai/OLMo-2-1124-13B", "olmo", "large", "mps"),
    # Pythia ladder (ungated up-proj proxy register)
    ModelSpec("EleutherAI/pythia-14m-deduped", "pythia", "small",
              notes="up-proj proxy"),
    ModelSpec("EleutherAI/pythia-160m-deduped", "pythia", "small",
              notes="up-proj proxy"),
    ModelSpec("EleutherAI/pythia-410m", "pythia", "small",
              notes="up-proj proxy"),
    ModelSpec("EleutherAI/pythia-2.8b-deduped", "pythia", "large", "mps",
              "up-proj proxy"),
)


def spec_for(model: str) -> ModelSpec:
    for s in REGISTRY:
        if s.model == model:
            return s
    # unknown model: still runnable — family from org prefix (configs > forks)
    fam = model.split("/")[0].lower()
    return ModelSpec(model, fam, "small")


# ── trace orchestration (subprocess per model: memory isolation) ─────────────


def has_artifact(spec: ModelSpec) -> bool:
    return (RESULTS_DIR / spec.slug / "model_vsm.json").exists()


def run_trace(
    spec: ModelSpec, device: str | None, smoke: bool, trace_args: str = ""
) -> bool:
    cmd = [
        sys.executable, str(_HERE / "trace.py"),
        "--model", spec.model,
        "--device", device or spec.device,
    ]
    if smoke:
        cmd.append("--smoke")
    if trace_args:
        cmd.extend(shlex.split(trace_args))  # open slot: any trace.py flag
    print(f"[sweep] tracing {spec.model} ({' '.join(cmd[2:])}) ...")
    r = subprocess.run(cmd, cwd=str(_ROOT), check=False)
    if r.returncode != 0:
        print(f"[sweep] FAILED ({r.returncode}): {spec.model} — continuing")
    return r.returncode == 0


# ── restack: model_vsm artifacts -> family -> root ───────────────────────────


def restack(reference=None) -> VSMNode | None:
    """Load every model_vsm artifact and stack family -> root(universal)."""
    reference = reference if reference is not None else load_consensus_gram()
    models: list[VSMNode] = []
    for p in sorted(RESULTS_DIR.glob("*/model_vsm.json")):
        node = load_tree(p.with_suffix(""))
        # re-anchor model-level gc against the reference (may predate it)
        models.append(node)
    if not models:
        return None
    by_family: dict[str, list[VSMNode]] = {}
    for m in models:
        fam = spec_for(m.name).family
        by_family.setdefault(fam, []).append(m)
    families = [
        stack(ms, level="family", name=fam, reference_gram=reference)
        for fam, ms in sorted(by_family.items())
    ]
    root = stack(
        families, level="root", name="universal", reference_gram=reference,
        meta={"n_models": len(models)},
    )
    return root


def regen_consensus() -> Path:
    """Rebuild opcodes/data/consensus_gram.json from gated REGISTRY trees.

    Reference = mean of model-level tree Grams (gate+attn rollup) across the
    registry models only — quantization rungs and ad-hoc traces are excluded
    so no backbone is double-counted. NOTE the self-consistency caveat: the
    restack root is built from (a superset of) these same trees, so root gc
    against this reference is a self-consistent read, not an independent one;
    per-model and per-family gc remain the informative numbers.
    """
    registry_models = {s.model for s in REGISTRY}
    names, grams, basis = [], [], None
    for p in sorted(RESULTS_DIR.glob("*/model_vsm.json")):
        node = load_tree(p.with_suffix(""))
        if node.name not in registry_models:
            print(f"[consensus] excluded (non-registry): {node.name}")
            continue
        if not node.gated or node.gram is None:
            print(f"[consensus] SKIP (ungated / no gram): {node.name}")
            continue
        if basis is None:
            basis = json.loads(p.read_text(encoding="utf-8")).get("basis")
        names.append(node.name)
        grams.append(np.asarray(node.gram, dtype=np.float64))
    if not grams:
        raise SystemExit("[consensus] no gated registry trees found")
    consensus = np.mean(np.stack(grams), axis=0)
    sha = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=str(_ROOT),
        capture_output=True, text=True, check=False,
    ).stdout.strip()
    out = _HERE / "data" / "consensus_gram.json"
    out.write_text(json.dumps({
        "description": (
            f"{len(names)}-model consensus crystal Gram — mean of gated "
            "model-level tree Grams from results/opcode-trace (clean "
            "539-probe bundle, contamination fix 48366f2). SELF-CONSISTENT "
            "reference for the restack root (built from the same trees)."
        ),
        "register": "topological/routing (model-level tree rollup: gate+attn)",
        "method": "mean of gated model-level Grams; registry models only",
        "source": "results/opcode-trace/*/model_vsm.json",
        "provenance_git_sha": sha,
        "generated": datetime.now(UTC).isoformat(timespec="seconds"),
        "n_models": len(names),
        "models": names,
        "crystal_order": basis,
        "consensus_gram": consensus.tolist(),
    }, indent=2), encoding="utf-8")
    print(f"[consensus] wrote {out} ({len(names)} models)")
    return out


def report(root: VSMNode, reference) -> None:
    print("=" * 72)
    print("OPCODE CRYSTAL TREE — cross-model consensus")
    print("=" * 72)
    print(root.summary())
    print("-" * 72)
    if root.gram is not None and reference is not None:
        gc = offdiag_corr(root.gram, reference)
        print(f"root Gram vs bundled consensus reference: gc = {gc:+.3f}")
    print(f"families: {root.meta['n_gated']}/{root.meta['n_children']} gated | "
          f"agreement mean={root.meta['agreement_mean']:.3f} "
          f"min={root.meta['agreement_min']:.3f} "
          f"dissent={root.meta['dissent']}")
    for fam in root.children:
        print(f"  {fam.name}: {fam.meta['n_gated']}/{fam.meta['n_children']} "
              f"models gated | agreement={fam.meta['agreement_mean']:.3f} | "
              f"gc={fam.health['gc_consensus']:.3f}")
    print("=" * 72)


def main() -> None:
    ap = argparse.ArgumentParser(description="Multi-model opcode sweep + restack")
    ap.add_argument("--tier", choices=["small", "large", "all"], default=None,
                    help="trace registry models of this tier if missing")
    ap.add_argument("--models", default=None,
                    help="comma list of model ids (overrides --tier)")
    ap.add_argument("--device", default=None,
                    help="override device for traced models")
    ap.add_argument("--force", action="store_true",
                    help="re-trace even if an artifact exists")
    ap.add_argument("--smoke", action="store_true",
                    help="pass --smoke to trace runs")
    ap.add_argument("--trace-args", default="",
                    help="extra args passed verbatim to every trace.py run "
                         "(e.g. \"--jspace-projector --n-perm 500\")")
    ap.add_argument("--restack-only", action="store_true",
                    help="skip tracing; restack existing artifacts")
    ap.add_argument("--regen-consensus", action="store_true",
                    help="rebuild opcodes/data/consensus_gram.json from gated "
                         "registry trees before restacking (implies no trace)")
    args = ap.parse_args()

    if args.regen_consensus:
        regen_consensus()
        args.restack_only = True

    if not args.restack_only:
        if args.models:
            specs = [spec_for(m.strip()) for m in args.models.split(",")]
        elif args.tier:
            specs = [
                s for s in REGISTRY
                if args.tier == "all" or s.tier == args.tier
            ]
        else:
            specs = []
        for spec in specs:
            if has_artifact(spec) and not args.force:
                print(f"[sweep] cached: {spec.model} "
                      f"({RESULTS_DIR / spec.slug / 'model_vsm.json'})")
                continue
            run_trace(spec, args.device, args.smoke, args.trace_args)

    reference = load_consensus_gram()
    root = restack(reference)
    if root is None:
        print("[sweep] no model_vsm artifacts found; trace something first.")
        sys.exit(1)
    report(root, reference)
    out = RESULTS_DIR / "universal_vsm"
    save_tree(root, out)
    summary = {
        "n_models": root.meta["n_models"],
        "families": {
            f.name: {
                "models": [m.name for m in f.children],
                "n_gated": f.meta["n_gated"],
                "agreement_mean": f.meta["agreement_mean"],
                "gc_consensus": f.health["gc_consensus"],
            }
            for f in root.children
        },
        "root_health": root.health,
        "root_agreement": {
            k: root.meta[k]
            for k in ("agreement_mean", "agreement_min", "dissent", "n_gated")
        },
    }
    (RESULTS_DIR / "sweep_summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=True), encoding="utf-8"
    )
    print(f"[sweep] wrote {out}.json + sweep_summary.json")


if __name__ == "__main__":
    main()
