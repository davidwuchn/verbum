"""Combinator Addressing — Do relation directions use combinator beam angles?

Session 172. Tests whether the moiré addressing mechanism for factual
retrieval uses the same combinator basis (KIBC) that computation uses.

Hypothesis: if "The capital of France is" is really (λx. capital(x)) France,
then the retrieval beam angle should have combinator components. The "near
zero" KIBC in retrieval mode might mean the combinators are being USED
as beam angles (selecting which grating resolves) rather than being
COMPUTED as programs (running beta reductions).

Three phases:

  Phase 1: CROSS-FORM
    Present the same fact as natural language AND as lambda expression.
    Compare combinator activations and moiré patterns.
    Q: Does lambda form activate the compute path for the same fact?

  Phase 2: RELATION-COMBINATOR PROJECTION
    Project moiré centroids onto the combinator fingerprint basis.
    Q: Do relation types map to specific combinator combinations?

  Phase 3: RESIDUAL DECOMPOSITION
    Decompose the residual stream direction (the query beam) at each
    ENRICH layer into combinator components.
    Q: What is the query beam made of?

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/combinator_addressing.py
    uv run python scripts/experiments/combinator_addressing.py --model Qwen/Qwen3-0.6B

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

RESULTS_BASE = Path(__file__).parent.parent.parent / "results" / "combinator-addressing"
PROBES_DIR = Path(__file__).parent.parent.parent / "probes"
HOLOGRAM_READER_DIR = Path(__file__).parent.parent.parent / "results" / "hologram-reader"

COMPILE_GATE = (
    "You are a lambda calculus compiler. Convert natural language to "
    "typed lambda calculus.\nInput a combinator expression. Output its "
    "beta-normal form.\nBe terse. Output ONLY the reduced expression."
)

COMBINATOR_NAMES = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]
BETA_NAMES = ["beta_K", "beta_I", "beta_apply", "beta_compose"]
ALL_OP_NAMES = COMBINATOR_NAMES + BETA_NAMES
N_OPS = len(ALL_OP_NAMES)


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Cross-Form Probes — same fact in NL and lambda
# ══════════════════════════════════════════════════════════════════════

def build_cross_form_probes() -> list[dict]:
    """Build paired probes: natural language + lambda form for the same fact."""

    probes = []

    # Capital relations: capital_of(x) — K-like (select attribute)
    capitals = [
        ("France", "Paris"), ("Japan", "Tokyo"), ("Germany", "Berlin"),
        ("Italy", "Rome"), ("Brazil", "Brasilia"), ("Egypt", "Cairo"),
        ("Spain", "Madrid"), ("Australia", "Canberra"),
    ]
    for entity, target in capitals:
        probes.append({
            "id": f"capital_{entity.lower()}",
            "category": "capital",
            "relation": "capital_of",
            "entity": entity,
            "target": target,
            "nl_prompt": f"The capital of {entity} is",
            "lambda_prompt": f"(λx. capital_of(x)) {entity} =",
            "apply_prompt": f"capital_of({entity}) =",
            "combinator_prompt": f"K capital {entity} =",
            # K a b = a: K (capital entity) noise = capital(entity)
            # This is a reach — K selects the first arg, here we're
            # testing if the model treats relation lookup as K-selection
        })

    # Language relations: language_of(x)
    languages = [
        ("Brazil", "Portuguese"), ("Japan", "Japanese"),
        ("Germany", "German"), ("France", "French"),
        ("China", "Mandarin"), ("Russia", "Russian"),
        ("Mexico", "Spanish"), ("Italy", "Italian"),
    ]
    for entity, target in languages:
        probes.append({
            "id": f"language_{entity.lower()}",
            "category": "language",
            "relation": "language_of",
            "entity": entity,
            "target": target,
            "nl_prompt": f"The official language of {entity} is",
            "lambda_prompt": f"(λx. language_of(x)) {entity} =",
            "apply_prompt": f"language_of({entity}) =",
            "combinator_prompt": f"K language {entity} =",
        })

    # Continent relations: continent_of(x)
    continents = [
        ("France", "Europe"), ("Japan", "Asia"),
        ("Brazil", "South America"), ("Egypt", "Africa"),
        ("Australia", "Oceania"), ("Canada", "North America"),
    ]
    for entity, target in continents:
        probes.append({
            "id": f"continent_{entity.lower()}",
            "category": "continent",
            "relation": "continent_of",
            "entity": entity,
            "target": target,
            "nl_prompt": f"{entity} is located on the continent of",
            "lambda_prompt": f"(λx. continent_of(x)) {entity} =",
            "apply_prompt": f"continent_of({entity}) =",
            "combinator_prompt": f"K continent {entity} =",
        })

    # Currency relations: currency_of(x)
    currencies = [
        ("Japan", "yen"), ("UK", "pound"),
        ("USA", "dollar"), ("India", "rupee"),
        ("China", "yuan"), ("Brazil", "real"),
    ]
    for entity, target in currencies:
        probes.append({
            "id": f"currency_{entity.lower()}",
            "category": "currency",
            "relation": "currency_of",
            "entity": entity,
            "target": target,
            "nl_prompt": f"The currency of {entity} is the",
            "lambda_prompt": f"(λx. currency_of(x)) {entity} =",
            "apply_prompt": f"currency_of({entity}) =",
            "combinator_prompt": f"K currency {entity} =",
        })

    return probes


# ══════════════════════════════════════════════════════════════════════
# Engine
# ══════════════════════════════════════════════════════════════════════

class CombinatorAddressingProbe:
    """Measure whether factual retrieval uses combinator beam angles."""

    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B", device: str = "auto"):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        self.layers = None
        self.n_layers = 0
        self.d_model = 0
        self.d_ff = 0
        self.fingerprints: dict[str, np.ndarray] = {}
        self.results_dir = RESULTS_BASE / model_name.replace("/", "_")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def _load_model(self):
        log(f"  Loading {self.model_name}...")
        t0 = time.time()

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        if self.device == "auto":
            if torch.cuda.is_available():
                dev = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                dev = "mps"
            else:
                dev = "cpu"
        else:
            dev = self.device

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, torch_dtype=torch.bfloat16,
            device_map=dev if dev != "mps" else "auto",
            low_cpu_mem_usage=True, trust_remote_code=True,
        )
        self.model.eval()

        config = self.model.config
        self.n_layers = config.num_hidden_layers
        self.d_model = config.hidden_size
        self.d_ff = getattr(config, "intermediate_size", self.d_model * 4)

        # Get layers
        for attr_path in ["model.layers", "transformer.h", "gpt_neox.layers"]:
            obj = self.model
            try:
                for part in attr_path.split("."):
                    obj = getattr(obj, part)
                self.layers = list(obj)
                break
            except AttributeError:
                continue

        log(f"  Loaded in {time.time()-t0:.1f}s ({self.n_layers} layers, d={self.d_model}, d_ff={self.d_ff})")

    def _load_fingerprints(self):
        """Load cached fingerprints from hologram reader."""
        slug = self.model_name.replace("/", "_")
        fp_path = HOLOGRAM_READER_DIR / slug / f"fingerprints_{slug}.npz"
        if not fp_path.exists():
            log(f"  ⚠ No cached fingerprints at {fp_path}")
            log(f"    Run hologram_reader.py first: --model {self.model_name}")
            sys.exit(1)

        data = np.load(fp_path)
        self.fingerprints = {op: data[op] for op in ALL_OP_NAMES if op in data}
        log(f"  Loaded {len(self.fingerprints)} fingerprints from {fp_path}")

    def _capture_activations(
        self, text: str, layer_indices: list[int]
    ) -> dict[str, dict[int, np.ndarray]]:
        """Capture FFN output, gate output, up output, and residual at specified layers."""
        ids = self.tokenizer.encode(text, return_tensors="pt")
        device = next(self.model.parameters()).device
        ids = ids.to(device)

        ffn_caps = {}
        gate_caps = {}
        up_caps = {}
        res_caps = {}
        hooks = []

        for li in layer_indices:
            layer = self.layers[li]
            mlp = layer.mlp if hasattr(layer, "mlp") else layer

            # FFN down_proj output
            if hasattr(mlp, "down_proj"):
                def make_ffn_hook(idx):
                    def hook(m, inp, out):
                        ffn_caps[idx] = out[0, -1, :].detach().cpu().float().numpy()
                    return hook
                hooks.append(mlp.down_proj.register_forward_hook(make_ffn_hook(li)))

                # Gate output
                def make_gate_hook(idx):
                    def hook(m, inp, out):
                        gate_caps[idx] = out[0, -1, :].detach().cpu().float().numpy()
                    return hook
                hooks.append(mlp.gate_proj.register_forward_hook(make_gate_hook(li)))

                # Up output
                def make_up_hook(idx):
                    def hook(m, inp, out):
                        up_caps[idx] = out[0, -1, :].detach().cpu().float().numpy()
                    return hook
                hooks.append(mlp.up_proj.register_forward_hook(make_up_hook(li)))

            # Residual pre-hook
            def make_res_hook(idx):
                def hook(m, inp, out=None):
                    x = inp[0] if isinstance(inp, tuple) else inp
                    res_caps[idx] = x[0, -1, :].detach().cpu().float().numpy()
                return hook
            hooks.append(layer.register_forward_pre_hook(make_res_hook(li)))

        with torch.no_grad():
            _ = self.model(input_ids=ids)

        for h in hooks:
            h.remove()

        return {"ffn": ffn_caps, "gate": gate_caps, "up": up_caps, "residual": res_caps}

    def _project_onto_combinators(self, vec: np.ndarray, layer: int) -> dict[str, float]:
        """Project a vector onto the combinator fingerprint basis at a given layer."""
        norm = np.linalg.norm(vec)
        if norm < 1e-10:
            return {op: 0.0 for op in ALL_OP_NAMES}

        unit = vec / norm
        projections = {}
        for op in ALL_OP_NAMES:
            fp = self.fingerprints[op][layer]
            fp_norm = np.linalg.norm(fp)
            if fp_norm > 1e-10:
                projections[op] = float(np.dot(unit, fp / fp_norm))
            else:
                projections[op] = 0.0
        return projections

    # ── Phase 1: Cross-Form ──

    def phase1_cross_form(self, probes: list[dict]):
        """Compare combinator activation and moiré for NL vs lambda form."""
        log(f"\n{'═' * 70}")
        log(f"  Phase 1: CROSS-FORM COMPARISON")
        log(f"  Same fact, different surface form. Does lambda form activate KIBC?")
        log(f"{'═' * 70}")

        # ENRICH layers (50-85% depth)
        enrich_start = int(self.n_layers * 0.50)
        enrich_end = int(self.n_layers * 0.85)
        enrich_layers = list(range(enrich_start, enrich_end + 1))

        results = []
        forms = ["nl_prompt", "lambda_prompt", "apply_prompt"]
        form_labels = ["Natural Language", "Lambda (λx.f(x))", "Apply f(x)"]

        for pi, probe in enumerate(probes):
            probe_result = {
                "id": probe["id"],
                "category": probe["category"],
                "relation": probe["relation"],
                "entity": probe["entity"],
                "forms": {},
            }

            for form_key, form_label in zip(forms, form_labels):
                text = probe[form_key]
                caps = self._capture_activations(text, enrich_layers)

                # Combinator projection of FFN output at each ENRICH layer
                form_data = {
                    "prompt": text,
                    "per_layer": {},
                    "avg_combinator_strength": {},
                }

                all_projections = {op: [] for op in ALL_OP_NAMES}

                for li in enrich_layers:
                    if li in caps["ffn"]:
                        proj = self._project_onto_combinators(caps["ffn"][li], li)
                        form_data["per_layer"][li] = proj
                        for op, val in proj.items():
                            all_projections[op].append(abs(val))

                # Average combinator strength across ENRICH layers
                for op in ALL_OP_NAMES:
                    vals = all_projections[op]
                    form_data["avg_combinator_strength"][op] = float(np.mean(vals)) if vals else 0.0

                # Total combinator energy
                form_data["total_combinator_energy"] = sum(form_data["avg_combinator_strength"].values())

                # Dominant combinator
                sorted_ops = sorted(form_data["avg_combinator_strength"].items(), key=lambda x: x[1], reverse=True)
                form_data["dominant"] = sorted_ops[0][0] if sorted_ops else ""
                form_data["dominant_strength"] = sorted_ops[0][1] if sorted_ops else 0.0

                probe_result["forms"][form_key] = form_data

            results.append(probe_result)

            if (pi + 1) % 4 == 0:
                log(f"    {pi + 1}/{len(probes)} probes")

        # Summarize
        log(f"\n  Cross-form comparison ({len(results)} probes):")
        log(f"  {'':>20s}  {'NL':>10s}  {'Lambda':>10s}  {'Apply':>10s}")

        # Average total energy by form
        for form_key, label in zip(forms, ["NL", "Lambda", "Apply"]):
            energies = [r["forms"][form_key]["total_combinator_energy"] for r in results]
            log(f"  {'Avg total energy':>20s}  " if form_key == forms[0] else f"  {'':>20s}  ", )

        nl_energies = [r["forms"]["nl_prompt"]["total_combinator_energy"] for r in results]
        lam_energies = [r["forms"]["lambda_prompt"]["total_combinator_energy"] for r in results]
        app_energies = [r["forms"]["apply_prompt"]["total_combinator_energy"] for r in results]

        log(f"  Avg total combinator energy:")
        log(f"    Natural language:  {np.mean(nl_energies):.4f}")
        log(f"    Lambda form:       {np.mean(lam_energies):.4f}")
        log(f"    Apply form:        {np.mean(app_energies):.4f}")
        log(f"    Ratio (λ/NL):      {np.mean(lam_energies)/max(np.mean(nl_energies), 1e-10):.2f}x")
        log(f"    Ratio (apply/NL):  {np.mean(app_energies)/max(np.mean(nl_energies), 1e-10):.2f}x")

        # Per-combinator comparison
        log(f"\n  Per-combinator avg |strength| in ENRICH zone:")
        log(f"  {'Op':>12s}  {'NL':>8s}  {'Lambda':>8s}  {'Apply':>8s}  {'λ/NL':>6s}")
        for op in ALL_OP_NAMES:
            nl_avg = np.mean([r["forms"]["nl_prompt"]["avg_combinator_strength"][op] for r in results])
            lam_avg = np.mean([r["forms"]["lambda_prompt"]["avg_combinator_strength"][op] for r in results])
            app_avg = np.mean([r["forms"]["apply_prompt"]["avg_combinator_strength"][op] for r in results])
            ratio = lam_avg / max(nl_avg, 1e-10)
            log(f"  {op:>12s}  {nl_avg:>8.4f}  {lam_avg:>8.4f}  {app_avg:>8.4f}  {ratio:>6.2f}x")

        # Dominant combinator per relation type
        log(f"\n  Dominant combinator per relation (lambda form):")
        for cat in sorted(set(r["category"] for r in results)):
            cat_results = [r for r in results if r["category"] == cat]
            dominants = [r["forms"]["lambda_prompt"]["dominant"] for r in cat_results]
            from collections import Counter
            counts = Counter(dominants)
            top = counts.most_common(3)
            top_str = ", ".join(f"{op}({n})" for op, n in top)
            log(f"    {cat:>12s}: {top_str}")

        return results

    # ── Phase 2: Relation-Combinator Projection ──

    def phase2_relation_projection(self, probes: list[dict]):
        """Project moiré centroids onto combinator basis."""
        log(f"\n{'═' * 70}")
        log(f"  Phase 2: RELATION-COMBINATOR PROJECTION")
        log(f"  Do relation centroids have combinator components?")
        log(f"{'═' * 70}")

        enrich_start = int(self.n_layers * 0.50)
        enrich_end = int(self.n_layers * 0.85)
        enrich_layers = list(range(enrich_start, enrich_end + 1))

        # Collect moiré patterns per relation
        relation_moires: dict[str, list[np.ndarray]] = {}
        # Also collect residual patterns per relation
        relation_residuals: dict[str, list[dict[int, np.ndarray]]] = {}

        for pi, probe in enumerate(probes):
            text = probe["nl_prompt"]
            cat = probe["category"]
            caps = self._capture_activations(text, enrich_layers)

            # Moiré at each ENRICH layer
            for li in enrich_layers:
                if li in caps["gate"] and li in caps["up"]:
                    gate = caps["gate"][li]
                    up = caps["up"][li]
                    sig = 1.0 / (1.0 + np.exp(-np.clip(gate, -20, 20)))
                    silu = gate * sig
                    moire = silu * up

                    key = f"{cat}_L{li}"
                    relation_moires.setdefault(key, []).append(moire)

                if li in caps["residual"]:
                    relation_residuals.setdefault(cat, [])
                    if len(relation_residuals[cat]) <= pi:
                        relation_residuals[cat].append({})
                    relation_residuals[cat][-1][li] = caps["residual"][li]

            if (pi + 1) % 8 == 0:
                log(f"    {pi + 1}/{len(probes)} probes")

        # Compute centroids per (relation, layer) and project onto combinator basis
        log(f"\n  Centroid → combinator projection per relation × layer:")

        # Aggregate across layers for each relation
        categories = sorted(set(p["category"] for p in probes))
        relation_combinator_profile = {}

        for cat in categories:
            cat_profile = {op: [] for op in ALL_OP_NAMES}

            for li in enrich_layers:
                key = f"{cat}_L{li}"
                if key not in relation_moires or len(relation_moires[key]) < 2:
                    continue

                patterns = np.array(relation_moires[key])
                centroid = np.mean(patterns, axis=0)

                # Project centroid (d_ff-dimensional) into d_model space via down_proj
                layer = self.layers[li]
                mlp = layer.mlp if hasattr(layer, "mlp") else layer
                if hasattr(mlp, "down_proj"):
                    down_w = mlp.down_proj.weight.detach().cpu().float().numpy()
                    # centroid is in d_ff space, project to d_model
                    projected = centroid @ down_w.T  # (d_model,)

                    # Now project onto combinator basis
                    proj = self._project_onto_combinators(projected, li)
                    for op, val in proj.items():
                        cat_profile[op].append(val)

            # Average across ENRICH layers
            relation_combinator_profile[cat] = {
                op: float(np.mean(vals)) if vals else 0.0
                for op, vals in cat_profile.items()
            }

        # Print the relation × combinator matrix
        log(f"\n  Relation × Combinator Matrix (centroid projection, signed avg):")
        header = f"  {'Relation':>12s}"
        for op in COMBINATOR_NAMES:
            header += f"  {op:>6s}"
        for op in BETA_NAMES:
            header += f"  {op:>10s}"
        log(header)

        for cat in categories:
            prof = relation_combinator_profile.get(cat, {})
            line = f"  {cat:>12s}"
            for op in COMBINATOR_NAMES:
                v = prof.get(op, 0)
                line += f"  {v:>+6.3f}"
            for op in BETA_NAMES:
                v = prof.get(op, 0)
                line += f"  {v:>+10.3f}"
            log(line)

        # Compute combinator energy fraction
        log(f"\n  Total |combinator projection| per relation:")
        for cat in categories:
            prof = relation_combinator_profile.get(cat, {})
            total = sum(abs(v) for v in prof.values())
            top3 = sorted(prof.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
            top3_str = ", ".join(f"{op}({v:+.3f})" for op, v in top3)
            log(f"    {cat:>12s}: total={total:.3f}  top3=[{top3_str}]")

        return relation_combinator_profile

    # ── Phase 3: Residual Decomposition ──

    def phase3_residual_decomposition(self, probes: list[dict]):
        """Decompose the query beam (residual direction) into combinator components."""
        log(f"\n{'═' * 70}")
        log(f"  Phase 3: RESIDUAL DECOMPOSITION")
        log(f"  What is the query beam made of?")
        log(f"{'═' * 70}")

        # Use a subset of layers spanning full depth
        sample_layers = list(range(0, self.n_layers, max(1, self.n_layers // 12)))

        # Collect residual combinator projections for NL vs lambda form
        nl_residual_profiles = {op: {li: [] for li in sample_layers} for op in ALL_OP_NAMES}
        lam_residual_profiles = {op: {li: [] for li in sample_layers} for op in ALL_OP_NAMES}

        for pi, probe in enumerate(probes[:16]):  # Subset for speed
            # Natural language
            caps_nl = self._capture_activations(probe["nl_prompt"], sample_layers)
            caps_lam = self._capture_activations(probe["lambda_prompt"], sample_layers)

            for li in sample_layers:
                if li in caps_nl["residual"]:
                    proj = self._project_onto_combinators(caps_nl["residual"][li], li)
                    for op, val in proj.items():
                        nl_residual_profiles[op][li].append(val)

                if li in caps_lam["residual"]:
                    proj = self._project_onto_combinators(caps_lam["residual"][li], li)
                    for op, val in proj.items():
                        lam_residual_profiles[op][li].append(val)

        # Print depth profile
        log(f"\n  Residual combinator energy by depth (avg |projection|):")
        log(f"  {'Layer':>6s}  {'depth':>5s}  {'NL total':>8s}  {'λ total':>8s}  {'NL top':>20s}  {'λ top':>20s}")

        for li in sample_layers:
            depth = li / max(1, self.n_layers - 1)
            nl_total = 0
            lam_total = 0
            nl_per_op = {}
            lam_per_op = {}

            for op in ALL_OP_NAMES:
                nl_vals = nl_residual_profiles[op][li]
                lam_vals = lam_residual_profiles[op][li]
                nl_avg = float(np.mean([abs(v) for v in nl_vals])) if nl_vals else 0
                lam_avg = float(np.mean([abs(v) for v in lam_vals])) if lam_vals else 0
                nl_total += nl_avg
                lam_total += lam_avg
                nl_per_op[op] = nl_avg
                lam_per_op[op] = lam_avg

            nl_top = sorted(nl_per_op.items(), key=lambda x: x[1], reverse=True)[:2]
            lam_top = sorted(lam_per_op.items(), key=lambda x: x[1], reverse=True)[:2]
            nl_top_str = " ".join(f"{op}:{v:.3f}" for op, v in nl_top)
            lam_top_str = " ".join(f"{op}:{v:.3f}" for op, v in lam_top)

            log(f"  L{li:02d}     {depth:.2f}   {nl_total:>8.3f}  {lam_total:>8.3f}  {nl_top_str:>20s}  {lam_top_str:>20s}")

        return nl_residual_profiles, lam_residual_profiles

    # ── Main ──

    def run(self):
        t0 = time.time()
        log(f"\n{'═' * 70}")
        log(f"  Combinator Addressing Probe — {self.model_name}")
        log(f"{'═' * 70}")

        self._load_model()
        self._load_fingerprints()

        probes = build_cross_form_probes()
        log(f"  Built {len(probes)} cross-form probes across {len(set(p['category'] for p in probes))} relations")

        # Phase 1: Cross-form comparison
        cross_results = self.phase1_cross_form(probes)

        # Phase 2: Relation-combinator projection
        relation_profiles = self.phase2_relation_projection(probes)

        # Phase 3: Residual decomposition
        nl_res, lam_res = self.phase3_residual_decomposition(probes)

        # Save results
        output = {
            "model": self.model_name,
            "n_layers": self.n_layers,
            "d_model": self.d_model,
            "d_ff": self.d_ff,
            "n_probes": len(probes),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "phase1_cross_form": [
                {
                    "id": r["id"],
                    "category": r["category"],
                    "relation": r["relation"],
                    "nl_energy": r["forms"]["nl_prompt"]["total_combinator_energy"],
                    "lambda_energy": r["forms"]["lambda_prompt"]["total_combinator_energy"],
                    "apply_energy": r["forms"]["apply_prompt"]["total_combinator_energy"],
                    "nl_dominant": r["forms"]["nl_prompt"]["dominant"],
                    "lambda_dominant": r["forms"]["lambda_prompt"]["dominant"],
                    "apply_dominant": r["forms"]["apply_prompt"]["dominant"],
                }
                for r in cross_results
            ],
            "phase2_relation_profiles": {
                cat: {op: round(v, 4) for op, v in prof.items()}
                for cat, prof in relation_profiles.items()
            },
        }

        out_path = self.results_dir / "results.json"
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2)
        log(f"\n  Saved results to {out_path}")

        elapsed = time.time() - t0
        log(f"\n  ✅ Complete in {elapsed:.1f}s")

        # Cleanup
        del self.model
        self.model = None
        gc.collect()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Combinator Addressing Probes")
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B", help="Model name")
    parser.add_argument("--device", default="auto", help="Device")
    args = parser.parse_args()

    probe = CombinatorAddressingProbe(model_name=args.model, device=args.device)
    probe.run()


if __name__ == "__main__":
    main()
