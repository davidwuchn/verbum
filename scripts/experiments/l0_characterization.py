#!/usr/bin/env python3
"""L0 Characterization — Why Can't the Lexer Be Ternarized?

L0 is catastrophic (115× PPL) when replaced with 9 ternary modes.
Every other layer survives (≤1.15×). This experiment asks WHY.

Five instruments:
  1. Natural cluster count: silhouette score from k=2..512 on gate patterns
  2. Mode sweep PPL: replace L0 FFN with k-mode ternary at k=9..512
  3. Effective rank: SVD of gate_proj and up_proj — how much is low-rank?
  4. Token property correlation: do modes map to unicode/frequency/script?
  5. L0 vs L15 comparison: same instruments on the sweet-spot layer (control)

Reuses patterns from mode_semantics.py and tiny_classifier_ternary.py.

Usage:
  uv run python scripts/experiments/l0_characterization.py --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from verbum.probes.library import crystal_probes


# ══════════════════════════════════════════════════════════════════════
# Diverse calibration texts
# ══════════════════════════════════════════════════════════════════════

CALIBRATION_TEXTS = [
    # Science
    "The theory of general relativity describes gravity as the curvature of spacetime.",
    "Photosynthesis converts carbon dioxide and water into glucose and oxygen.",
    "DNA carries genetic information in a double helix structure discovered by Watson and Crick.",
    "Quantum mechanics describes the behavior of particles at the atomic and subatomic scale.",
    "The human brain contains approximately 86 billion neurons connected by trillions of synapses.",
    "Black holes form when massive stars collapse under their own gravitational force.",
    "The periodic table organizes elements by atomic number and electron configuration.",
    "Enzymes are biological catalysts that speed up chemical reactions in living organisms.",
    # Narrative
    "She walked through the ancient forest, her footsteps muffled by fallen leaves.",
    "The old man sat quietly by the river, watching the fish jump at dawn.",
    "Three children ran laughing through the sunlit meadow while their dog chased butterflies.",
    "He opened the letter carefully, his hands trembling with anticipation.",
    "The ship sailed slowly into the harbor as the storm clouds gathered on the horizon.",
    "A woman stood at the window, silently watching the rain fall on the empty street.",
    "The detective examined the crime scene, noting every detail with practiced precision.",
    "Birds sang in the treetops as morning light filtered through the canopy above.",
    # Instructional
    "In a large mixing bowl, combine the flour, sugar, and baking powder.",
    "To solve this equation, first isolate the variable on one side.",
    "Install the software by running the setup wizard and following the prompts.",
    "Remove the old filter carefully and replace it with the new one.",
    "The patient should take two tablets every four hours with food.",
    "Preheat the oven to 350 degrees Fahrenheit before placing the dish inside.",
    "Always wash your hands thoroughly before handling raw ingredients.",
    "Connect the cable to the port on the left side of the device.",
    # Formal/political
    "The committee voted unanimously to approve the new environmental regulations.",
    "Democracy originated in ancient Greece, specifically in the city-state of Athens.",
    "The president addressed the nation regarding the economic recovery plan.",
    "International trade agreements require careful negotiation between multiple parties.",
    "The Supreme Court ruled that the legislation was constitutional.",
    "Parliament debated the proposed amendment for six consecutive hours.",
    # Technical
    "The function takes two arguments and returns their composition as a new callable.",
    "Machine learning algorithms can be categorized as supervised or unsupervised.",
    "The API endpoint accepts POST requests with JSON payload and returns status codes.",
    "Arrays are contiguous blocks of memory that allow constant-time access by index.",
    "The compiler transforms source code into machine-executable binary through multiple passes.",
    "Hash tables provide average constant-time lookup by mapping keys to bucket indices.",
    # Conversational
    "What time does the store close today?",
    "I think we should probably leave now before it gets too dark outside.",
    "Yes, that makes sense. Let me check the schedule and get back to you.",
    "The weather has been absolutely terrible this week, hasn't it?",
    "Can you believe they actually won the championship after being down three games?",
    # Complex syntax
    "The book that the professor recommended, which had been out of print for decades, was finally reissued.",
    "Although the experiment failed initially, the researchers persisted and eventually found the solution.",
    "Not only did the company exceed its quarterly targets, but it also expanded into three new markets.",
    # Lists / numbers
    "The primary colors are red, blue, and yellow.",
    "Countries in the European Union include France, Germany, Italy, Spain, and Poland.",
    "The Fibonacci sequence begins with 1, 1, 2, 3, 5, 8, 13, 21.",
    "Pi is approximately equal to 3.14159265 and is an irrational number.",
    "The distance from Earth to the Moon is about 384,400 kilometers.",
]

EVAL_TEXTS = [
    "The theory of general relativity describes gravity as the curvature of spacetime caused by mass and energy.",
    "In a large mixing bowl, combine the flour, sugar, and baking powder. Make a well in the center.",
    "The committee voted unanimously to approve the new environmental regulations for manufacturing plants.",
    "She walked through the ancient forest, her footsteps muffled by centuries of fallen leaves.",
    "The function takes two arguments and returns their composition as a new callable object.",
    "During the Cambrian explosion, roughly 541 million years ago, most major animal phyla appeared.",
    "The patient was admitted with acute respiratory distress. Initial blood work showed elevated levels.",
    "To solve this equation, first isolate the variable on one side by subtracting three from both sides.",
]

FACT_PROMPTS = [
    {"prompt": "The capital of France is", "expected": "Paris"},
    {"prompt": "The capital of Japan is", "expected": "Tokyo"},
    {"prompt": "Water boils at", "expected": "100"},
    {"prompt": "The speed of light is approximately", "expected": "300"},
    {"prompt": "The first president of the United States was", "expected": "George Washington"},
    {"prompt": "The year World War II ended was", "expected": "1945"},
    {"prompt": "The chemical symbol for gold is", "expected": "Au"},
    {"prompt": "The largest planet in our solar system is", "expected": "Jupiter"},
    {"prompt": "The author of Romeo and Juliet is", "expected": "Shakespeare"},
    {"prompt": "Pi is approximately equal to", "expected": "3.14"},
    {"prompt": "The Great Wall of China is located in", "expected": "China"},
    {"prompt": "The human body has", "expected": "206"},
    {"prompt": "Einstein's famous equation is E equals", "expected": "mc"},
    {"prompt": "The freezing point of water in Celsius is", "expected": "0"},
    {"prompt": "The currency of the United Kingdom is the", "expected": "pound"},
]


def log(msg=""):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


def get_layers(model):
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        return model.gpt_neox.layers
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


def measure_ppl(model, tokenizer, texts, device):
    total_loss = 0.0
    total_tokens = 0
    for text in texts:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        labels = inputs["input_ids"].clone()
        with torch.no_grad():
            outputs = model(**inputs, labels=labels)
            total_loss += outputs.loss.item() * labels.numel()
            total_tokens += labels.numel()
    return float(np.exp(total_loss / total_tokens))


def generate_text(model, tokenizer, prompt, max_new_tokens=30, device="cpu"):
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=max_new_tokens,
            do_sample=False, temperature=1.0,
            pad_token_id=tokenizer.pad_token_id)
    generated = outputs[0][inputs['input_ids'].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True)


def check_fact(generated, expected):
    return expected.lower() in generated.lower()


# ══════════════════════════════════════════════════════════════════════
# Instrument 1: Collect gate patterns + token info for a layer
# ══════════════════════════════════════════════════════════════════════

def collect_layer_data(model, tokenizer, layer_idx, device, texts, n_crystal=100):
    """Collect (gate_pattern, mlp_input, mlp_output, token_info) per token.

    Returns:
      gate_patterns: (N, intermediate_size) — SiLU(gate_proj(x))
      mlp_inputs: (N, d_model)
      mlp_outputs: (N, d_model)
      token_infos: list[dict] with token_id, text, position, etc.
    """
    layers = get_layers(model)
    mlp = layers[layer_idx].mlp
    captured = {}

    def pre_hook(module, inp):
        x = inp[0] if isinstance(inp, tuple) else inp
        captured["input"] = x.detach().float()

    def post_hook(module, inp, out):
        captured["output"] = out.detach().float()

    def gate_hook(module, inp, out):
        captured["gate_raw"] = out.detach().float()

    h_pre = mlp.register_forward_pre_hook(pre_hook)
    h_post = mlp.register_forward_hook(post_hook)
    h_gate = mlp.gate_proj.register_forward_hook(gate_hook)

    all_gate = []
    all_inputs = []
    all_outputs = []
    all_token_infos = []

    all_prompts = list(texts)
    probes = crystal_probes()
    all_prompts.extend([p.prompt for p in probes[:n_crystal]])
    all_prompts.extend([f["prompt"] for f in FACT_PROMPTS])

    for prompt in all_prompts:
        captured.clear()
        enc = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128)
        input_ids = enc["input_ids"][0].tolist()
        enc_dev = {k: v.to(device) for k, v in enc.items()}

        with torch.no_grad():
            model(**enc_dev)

        if "input" not in captured or "gate_raw" not in captured:
            continue

        inp = captured["input"][0].cpu().numpy()
        out = captured["output"][0].cpu().numpy()
        gate_raw = captured["gate_raw"][0]
        gate_pattern = (gate_raw * torch.sigmoid(gate_raw)).cpu().numpy()

        seq_len = len(input_ids)
        for i, tid in enumerate(input_ids):
            tok_text = tokenizer.decode([tid])
            all_token_infos.append({
                "token_id": tid,
                "text": tok_text,
                "position": i,
                "seq_len": seq_len,
                "rel_pos": i / max(1, seq_len - 1),
            })

        all_gate.append(gate_pattern)
        all_inputs.append(inp)
        all_outputs.append(out)

    h_pre.remove()
    h_post.remove()
    h_gate.remove()

    return (
        np.concatenate(all_gate, axis=0),
        np.concatenate(all_inputs, axis=0),
        np.concatenate(all_outputs, axis=0),
        all_token_infos,
    )


# ══════════════════════════════════════════════════════════════════════
# Instrument 2: Natural cluster count (silhouette sweep)
# ══════════════════════════════════════════════════════════════════════

def cluster_sweep(gate_patterns, ks, max_samples=3000):
    """Run k-means for each k and compute silhouette score.

    Returns list of {k, silhouette, inertia, time_s}.
    """
    # Subsample for silhouette (expensive)
    n = len(gate_patterns)
    if n > max_samples:
        idx = np.random.RandomState(42).choice(n, max_samples, replace=False)
        gp_sub = gate_patterns[idx]
    else:
        gp_sub = gate_patterns

    results = []
    for k in ks:
        if k >= len(gp_sub):
            break
        t0 = time.time()
        km = MiniBatchKMeans(n_clusters=k, random_state=42,
                             batch_size=min(256, len(gp_sub)), n_init=5)
        labels = km.fit_predict(gp_sub)
        elapsed = time.time() - t0

        # Silhouette on a smaller subset for speed
        sil_n = min(2000, len(gp_sub))
        if len(gp_sub) > sil_n:
            sil_idx = np.random.RandomState(99).choice(len(gp_sub), sil_n, replace=False)
            sil_score = silhouette_score(gp_sub[sil_idx], labels[sil_idx], sample_size=None)
        else:
            sil_score = silhouette_score(gp_sub, labels, sample_size=None)

        results.append({
            "k": k,
            "silhouette": float(sil_score),
            "inertia": float(km.inertia_),
            "time_s": round(elapsed, 2),
        })
        log(f"      k={k:>4d}  sil={sil_score:>7.4f}  inertia={km.inertia_:.2e}  ({elapsed:.1f}s)")

    return results


# ══════════════════════════════════════════════════════════════════════
# Instrument 3: Mode sweep PPL
# ══════════════════════════════════════════════════════════════════════

class TinyClassifierFFN(torch.nn.Module):
    """Entire FFN replaced by: tiny linear classifier → ternary lookup."""

    def __init__(self, classifier_weight, ternary_patterns, gamma_patterns):
        super().__init__()
        self.register_buffer('classifier', torch.tensor(classifier_weight, dtype=torch.float32))
        self.register_buffer('ternary', torch.tensor(ternary_patterns, dtype=torch.float32))
        self.register_buffer('gamma', torch.tensor(gamma_patterns, dtype=torch.float32))

    def forward(self, x):
        orig_shape = x.shape
        x_flat = x.reshape(-1, x.shape[-1]).float()
        logits = x_flat @ self.classifier.T
        mode = logits.argmax(dim=-1)
        output = self.ternary[mode] * self.gamma[mode]
        return output.to(x.dtype).reshape(orig_shape)


def train_classifier(inputs, labels, n_modes, n_epochs=100, lr=0.01):
    """Train a linear classifier: input → mode_id."""
    d_model = inputs.shape[1]
    X = torch.tensor(inputs, dtype=torch.float32)
    Y = torch.tensor(labels, dtype=torch.long)
    W = torch.randn(n_modes, d_model) * 0.01
    W.requires_grad_(True)
    optimizer = torch.optim.Adam([W], lr=lr)

    best_acc = 0.0
    best_W = None
    for _epoch in range(n_epochs):
        logits = X @ W.T
        loss = F.cross_entropy(logits, Y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        with torch.no_grad():
            acc = float((logits.argmax(dim=-1) == Y).float().mean())
            if acc > best_acc:
                best_acc = acc
                best_W = W.detach().clone()
    return best_W.numpy(), best_acc


def mode_sweep_ppl(model, tokenizer, layer_idx, device,
                   mlp_inputs, mlp_outputs, baseline_ppl, mode_counts):
    """Replace layer's FFN with k-mode ternary for each k, measure PPL."""
    d_model = mlp_inputs.shape[1]
    layers = get_layers(model)
    mlp = layers[layer_idx].mlp
    results = []

    for n_modes in mode_counts:
        if n_modes >= len(mlp_outputs):
            continue

        log(f"      k={n_modes}: clustering...")
        km = MiniBatchKMeans(n_clusters=n_modes, random_state=42,
                             batch_size=min(256, len(mlp_outputs)), n_init=5)
        labels = km.fit_predict(mlp_outputs)

        # Ternary patterns + gamma
        ternary = np.zeros((n_modes, d_model))
        gamma = np.zeros((n_modes, d_model))
        for i in range(n_modes):
            mask = labels == i
            if mask.sum() == 0:
                continue
            centroid = mlp_outputs[mask].mean(axis=0)
            ternary[i] = np.sign(centroid)
            gamma[i] = np.abs(centroid)

        # Train classifier
        cls_W, cls_acc = train_classifier(mlp_inputs, labels, n_modes)
        log(f"      k={n_modes}: classifier acc={cls_acc:.1%}")

        # Install and measure
        replacement = TinyClassifierFFN(cls_W, ternary, gamma).to(device)

        def make_hook(repl):
            def hook_fn(module, input, output):
                x = input[0] if isinstance(input, tuple) else input
                return repl(x)
            return hook_fn

        handle = mlp.register_forward_hook(make_hook(replacement))
        ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, device)
        handle.remove()

        ppl_ratio = ppl / baseline_ppl

        # Fact recall
        correct = 0
        handle = mlp.register_forward_hook(make_hook(replacement))
        for fp in FACT_PROMPTS:
            gen = generate_text(model, tokenizer, fp["prompt"], device=device)
            correct += int(check_fact(gen, fp["expected"]))
        handle.remove()
        fact_rate = correct / len(FACT_PROMPTS)

        log(f"      k={n_modes}: PPL={ppl:.2f} ({ppl_ratio:.2f}×), facts={fact_rate:.0%}, cls_acc={cls_acc:.1%}")

        results.append({
            "n_modes": n_modes,
            "ppl": ppl,
            "ppl_ratio": ppl_ratio,
            "fact_rate": fact_rate,
            "classifier_acc": cls_acc,
            "classifier_params": d_model * n_modes,
        })

    return results


# ══════════════════════════════════════════════════════════════════════
# Instrument 4: Effective rank (SVD)
# ══════════════════════════════════════════════════════════════════════

def effective_rank_analysis(model, layer_idx):
    """SVD of gate_proj and up_proj weight matrices."""
    layers = get_layers(model)
    mlp = layers[layer_idx].mlp

    results = {}
    for name, proj_name in [("gate_proj", "gate_proj"), ("up_proj", "up_proj"), ("down_proj", "down_proj")]:
        W = getattr(mlp, proj_name).weight.detach().float().cpu().numpy()
        # W shape: (out_features, in_features)
        _U, S, _Vt = np.linalg.svd(W, full_matrices=False)

        total_energy = float((S ** 2).sum())
        cumulative = np.cumsum(S ** 2) / total_energy

        rank_90 = int(np.searchsorted(cumulative, 0.90) + 1)
        rank_95 = int(np.searchsorted(cumulative, 0.95) + 1)
        rank_99 = int(np.searchsorted(cumulative, 0.99) + 1)
        full_rank = len(S)

        # Effective rank (exponential of entropy of normalized singular values)
        S_norm = S / S.sum()
        eff_rank = float(np.exp(-np.sum(S_norm * np.log(S_norm + 1e-10))))

        # Top singular value ratios
        sv_ratios = (S[:10] / S[0]).tolist()

        # Spectral decay rate
        log_S = np.log(S + 1e-10)
        if len(log_S) > 10:
            slope = float(np.polyfit(np.arange(min(100, len(log_S))),
                                     log_S[:min(100, len(log_S))], 1)[0])
        else:
            slope = 0.0

        results[name] = {
            "shape": list(W.shape),
            "full_rank": full_rank,
            "rank_90": rank_90,
            "rank_95": rank_95,
            "rank_99": rank_99,
            "effective_rank": round(eff_rank, 1),
            "rank_90_fraction": round(rank_90 / full_rank, 4),
            "rank_95_fraction": round(rank_95 / full_rank, 4),
            "rank_99_fraction": round(rank_99 / full_rank, 4),
            "top_10_sv_ratios": [round(r, 4) for r in sv_ratios],
            "spectral_decay_slope": round(slope, 6),
            "condition_number": float(S[0] / S[-1]) if S[-1] > 0 else float('inf'),
            "singular_values_top20": [round(float(s), 4) for s in S[:20]],
        }
        log(f"      {name}: shape={W.shape}, eff_rank={eff_rank:.1f}, "
            f"90%={rank_90}/{full_rank} ({rank_90/full_rank:.1%}), "
            f"99%={rank_99}/{full_rank} ({rank_99/full_rank:.1%})")

    return results


# ══════════════════════════════════════════════════════════════════════
# Instrument 5: Token property correlation
# ══════════════════════════════════════════════════════════════════════

def classify_token(text, token_id, tokenizer):
    """Classify a token by unicode category, byte length, script, etc."""
    # Strip the byte-fallback / special prefix
    clean = text.strip()
    if not clean:
        clean = text

    # Unicode category of first real character
    cats = set()
    scripts = set()
    for ch in clean:
        try:
            cats.add(unicodedata.category(ch))
            scripts.add(unicodedata.name(ch).split()[0] if unicodedata.name(ch, None) else "UNKNOWN")
        except (ValueError, TypeError):
            cats.add("Cc")
            scripts.add("CONTROL")

    # Primary unicode category
    primary_cat = "OTHER"
    if any(c.startswith("L") for c in cats):
        primary_cat = "LETTER"
    elif any(c.startswith("N") for c in cats):
        primary_cat = "NUMBER"
    elif any(c.startswith("P") for c in cats):
        primary_cat = "PUNCT"
    elif any(c.startswith("Z") for c in cats):
        primary_cat = "SPACE"
    elif any(c.startswith("S") for c in cats):
        primary_cat = "SYMBOL"

    # Script detection
    if "LATIN" in scripts:
        script = "LATIN"
    elif "CJK" in scripts or any("CJK" in s for s in scripts):
        script = "CJK"
    elif "CYRILLIC" in scripts:
        script = "CYRILLIC"
    elif "ARABIC" in scripts:
        script = "ARABIC"
    elif "DIGIT" in scripts or any("DIGIT" in s for s in scripts):
        script = "DIGIT"
    elif any(s in ("COMMA", "FULL", "SEMICOLON", "COLON", "EXCLAMATION",
                    "QUESTION", "APOSTROPHE", "QUOTATION", "HYPHEN",
                    "LEFT", "RIGHT") for s in scripts):
        script = "PUNCT"
    else:
        script = scripts.pop() if scripts else "UNKNOWN"

    # Byte length (proxy for complexity)
    byte_len = len(text.encode("utf-8"))

    # Is it a subword continuation?
    is_continuation = not text.startswith(" ") and not text.startswith("▁") and len(text) > 0

    return {
        "unicode_cat": primary_cat,
        "script": script,
        "byte_len": byte_len,
        "is_continuation": is_continuation,
        "is_special": token_id < 10 or "special" in tokenizer.convert_ids_to_tokens(token_id).lower(),
    }


def token_property_analysis(token_infos, labels, tokenizer, n_modes):
    """Cross-tabulate cluster assignments with token properties."""
    prop_dist = defaultdict(lambda: defaultdict(Counter))  # {property: {mode: Counter}}

    for info, label in zip(token_infos, labels, strict=False):
        mode = int(label)
        props = classify_token(info["text"], info["token_id"], tokenizer)
        for prop_name, prop_val in props.items():
            prop_dist[prop_name][mode][str(prop_val)] += 1

    # Compute mutual information between mode and each property
    mi_scores = {}
    for prop_name in prop_dist:
        # Joint distribution
        total = 0
        joint = defaultdict(int)
        mode_marginal = Counter()
        prop_marginal = Counter()
        for mode in range(n_modes):
            for val, count in prop_dist[prop_name][mode].items():
                joint[(mode, val)] += count
                mode_marginal[mode] += count
                prop_marginal[val] += count
                total += count

        if total == 0:
            mi_scores[prop_name] = 0.0
            continue

        # MI = Σ p(m,v) log(p(m,v) / (p(m)p(v)))
        mi = 0.0
        for (m, v), c in joint.items():
            p_mv = c / total
            p_m = mode_marginal[m] / total
            p_v = prop_marginal[v] / total
            if p_mv > 0 and p_m > 0 and p_v > 0:
                mi += p_mv * np.log2(p_mv / (p_m * p_v))

        # Normalized MI (divide by min entropy)
        h_mode = -sum((c/total) * np.log2(c/total + 1e-10) for c in mode_marginal.values())
        h_prop = -sum((c/total) * np.log2(c/total + 1e-10) for c in prop_marginal.values())
        nmi = mi / min(h_mode, h_prop) if min(h_mode, h_prop) > 0 else 0.0

        mi_scores[prop_name] = round(float(nmi), 4)

    # Per-mode dominant property values
    mode_dominant = {}
    for mode in range(n_modes):
        mode_dominant[mode] = {}
        for prop_name in prop_dist:
            counts = prop_dist[prop_name][mode]
            if counts:
                total = sum(counts.values())
                top = counts.most_common(3)
                mode_dominant[mode][prop_name] = [
                    {"value": v, "count": c, "fraction": round(c/total, 3)}
                    for v, c in top
                ]

    return {
        "nmi_scores": mi_scores,
        "distributions": {
            prop_name: {
                int(mode): dict(counts)
                for mode, counts in modes.items()
            }
            for prop_name, modes in prop_dist.items()
        },
        "mode_dominant": {int(k): v for k, v in mode_dominant.items()},
    }


# ══════════════════════════════════════════════════════════════════════
# Instrument 6: Transform physics (cos, norm, gate stats per mode)
# ══════════════════════════════════════════════════════════════════════

def transform_physics(gate_patterns, inputs, outputs, labels, n_modes):
    """Per-mode: cos(in,out), norm ratio, gate sparsity, gate consistency."""
    stats = {}
    for mode in range(n_modes):
        mask = labels == mode
        count = int(mask.sum())
        if count == 0:
            stats[mode] = {"count": 0}
            continue

        mi = inputs[mask]
        mo = outputs[mask]
        mg = gate_patterns[mask]

        in_norms = np.linalg.norm(mi, axis=1, keepdims=True) + 1e-8
        out_norms = np.linalg.norm(mo, axis=1, keepdims=True) + 1e-8
        cos_vals = np.sum((mi / in_norms) * (mo / out_norms), axis=1)
        norm_ratios = (out_norms / in_norms).squeeze()

        gate_active = (np.abs(mg) > 0.1).mean(axis=1)

        if count > 1:
            gc = mg.mean(axis=0)
            gc_n = np.linalg.norm(gc) + 1e-8
            mg_n = np.linalg.norm(mg, axis=1, keepdims=True) + 1e-8
            gate_cos = np.sum((mg / mg_n) * (gc / gc_n), axis=1)
            gate_consistency = float(np.mean(gate_cos))
        else:
            gate_consistency = 1.0

        stats[mode] = {
            "count": count,
            "cos_in_out": {"mean": float(np.mean(cos_vals)), "std": float(np.std(cos_vals))},
            "norm_ratio": {"mean": float(np.mean(norm_ratios)), "std": float(np.std(norm_ratios))},
            "gate_sparsity": {"mean": float(np.mean(gate_active)), "std": float(np.std(gate_active))},
            "gate_consistency": gate_consistency,
        }

    return stats


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def run_layer(model, tokenizer, layer_idx, device, baseline_ppl, layer_name):
    """Run all instruments on one layer. Returns results dict."""
    log(f"\n{'═'*70}")
    log(f"  LAYER {layer_idx} ({layer_name})")
    log(f"{'═'*70}")

    t_layer = time.time()

    # ── Collect data ──────────────────────────────────────────────
    log("    Collecting gate patterns + FFN I/O...")
    t0 = time.time()
    gate_patterns, mlp_inputs, mlp_outputs, token_infos = collect_layer_data(
        model, tokenizer, layer_idx, device, CALIBRATION_TEXTS)
    n_tokens = len(mlp_inputs)
    d_model = mlp_inputs.shape[1]
    intermediate = gate_patterns.shape[1]
    log(f"    Collected {n_tokens} tokens ({d_model}-dim, {intermediate} intermediate) in {time.time()-t0:.1f}s")

    # ── 1. Cluster sweep (natural cluster count) ─────────────────
    log("\n    ── INSTRUMENT 1: Cluster Sweep ──")
    ks = [2, 4, 6, 8, 9, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384, 512]
    cluster_results = cluster_sweep(gate_patterns, ks)

    best_sil = max(cluster_results, key=lambda x: x["silhouette"])
    log(f"    Best silhouette: k={best_sil['k']} (sil={best_sil['silhouette']:.4f})")

    # ── 2. Mode sweep PPL ────────────────────────────────────────
    log("\n    ── INSTRUMENT 2: Mode Sweep PPL ──")
    mode_counts = [9, 16, 32, 64, 128, 256, 512]
    ppl_results = mode_sweep_ppl(
        model, tokenizer, layer_idx, device,
        mlp_inputs, mlp_outputs, baseline_ppl, mode_counts)

    # ── 3. Effective rank (SVD) ──────────────────────────────────
    log("\n    ── INSTRUMENT 3: Effective Rank (SVD) ──")
    rank_results = effective_rank_analysis(model, layer_idx)

    # ── 4. Token property analysis (at best-silhouette k) ────────
    log(f"\n    ── INSTRUMENT 4: Token Property Analysis (k={best_sil['k']}) ──")
    km_best = MiniBatchKMeans(n_clusters=best_sil["k"], random_state=42,
                               batch_size=min(256, n_tokens), n_init=5)
    labels_best = km_best.fit_predict(gate_patterns)
    prop_results = token_property_analysis(token_infos, labels_best, tokenizer, best_sil["k"])
    log(f"    NMI scores: {prop_results['nmi_scores']}")

    # Also run at k=9 for comparison
    log("    Token property analysis at k=9...")
    km_9 = MiniBatchKMeans(n_clusters=9, random_state=42,
                            batch_size=min(256, n_tokens), n_init=5)
    labels_9 = km_9.fit_predict(gate_patterns)
    prop_results_9 = token_property_analysis(token_infos, labels_9, tokenizer, 9)

    # ── 5. Transform physics at k=9 and k=best ──────────────────
    log("\n    ── INSTRUMENT 5: Transform Physics ──")
    physics_9 = transform_physics(gate_patterns, mlp_inputs, mlp_outputs, labels_9, 9)
    physics_best = transform_physics(gate_patterns, mlp_inputs, mlp_outputs, labels_best, best_sil["k"])

    # Print summary table
    log("\n    Transform physics at k=9:")
    log(f"    {'Mode':>4} {'N':>5} | {'cos':>7} {'‖o/i‖':>7} {'gate%':>7} {'g_con':>7}")
    for m in sorted(physics_9.keys()):
        s = physics_9[m]
        if s.get("count", 0) == 0:
            continue
        log(f"    {m:>4} {s['count']:>5} | "
            f"{s['cos_in_out']['mean']:>7.3f} "
            f"{s['norm_ratio']['mean']:>7.3f} "
            f"{s['gate_sparsity']['mean']:>6.1%} "
            f"{s['gate_consistency']:>7.3f}")

    # ── 6. Gate pattern variance decomposition ───────────────────
    log("\n    ── INSTRUMENT 6: Gate Variance Decomposition ──")
    # PCA of gate patterns — how many components explain 90%?
    from sklearn.decomposition import PCA
    n_comp = min(100, min(gate_patterns.shape))
    pca = PCA(n_components=n_comp, random_state=42)
    pca.fit(gate_patterns)
    cum_var = np.cumsum(pca.explained_variance_ratio_)
    pca_90 = int(np.searchsorted(cum_var, 0.90) + 1)
    pca_95 = int(np.searchsorted(cum_var, 0.95) + 1)
    pca_99 = int(np.searchsorted(cum_var, 0.99) + 1) if cum_var[-1] >= 0.99 else n_comp
    log(f"    Gate PCA: 90%={pca_90}, 95%={pca_95}, 99%={pca_99} components (of {n_comp} tested)")

    gate_pca = {
        "components_90": pca_90,
        "components_95": pca_95,
        "components_99": pca_99,
        "max_components_tested": n_comp,
        "explained_variance_top20": [round(float(v), 6) for v in pca.explained_variance_ratio_[:20]],
        "cumulative_variance_top20": [round(float(v), 4) for v in cum_var[:20]],
    }

    layer_time = time.time() - t_layer
    log(f"\n    Layer {layer_idx} done in {layer_time:.1f}s")

    return {
        "layer_idx": layer_idx,
        "layer_name": layer_name,
        "n_tokens": n_tokens,
        "d_model": d_model,
        "intermediate_size": intermediate,
        "cluster_sweep": cluster_results,
        "best_silhouette_k": best_sil["k"],
        "mode_sweep_ppl": ppl_results,
        "effective_rank": rank_results,
        "token_properties_best_k": prop_results,
        "token_properties_k9": prop_results_9,
        "transform_physics_k9": {int(k): v for k, v in physics_9.items()},
        "transform_physics_best_k": {int(k): v for k, v in physics_best.items()},
        "gate_pca": gate_pca,
        "elapsed_s": round(layer_time, 1),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    args = p.parse_args()

    log(f"\n{'='*70}")
    log("  L0 CHARACTERIZATION — Why Can't the Lexer Be Ternarized?")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log("  Target layers: L0 (lexer) vs L15 (sweet spot, control)")
    log()

    # ── Load model ────────────────────────────────────────────────
    dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
    log(f"  Loading {args.model} ({dtype})...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size
    intermediate = model.config.intermediate_size
    log(f"  Layers: {n_layers}, d_model: {d_model}, intermediate: {intermediate}")

    # ── Baseline PPL ──────────────────────────────────────────────
    log("\n  Measuring baseline PPL...")
    baseline_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    log(f"  Baseline PPL: {baseline_ppl:.2f}")

    baseline_correct = 0
    for fp in FACT_PROMPTS:
        gen = generate_text(model, tokenizer, fp["prompt"], device=args.device)
        baseline_correct += int(check_fact(gen, fp["expected"]))
    baseline_fact_rate = baseline_correct / len(FACT_PROMPTS)
    log(f"  Baseline facts: {baseline_correct}/{len(FACT_PROMPTS)} = {baseline_fact_rate:.0%}")

    # ── Run both layers ───────────────────────────────────────────
    layers_to_test = [
        (0, "LEXER (embedding→features)"),
        (15, "OPTIMIZER (sweet spot, control)"),
    ]

    all_results = {
        "model": args.model,
        "baseline_ppl": baseline_ppl,
        "baseline_fact_rate": baseline_fact_rate,
        "d_model": d_model,
        "intermediate_size": intermediate,
        "n_layers": n_layers,
        "layers": {},
    }

    for layer_idx, layer_name in layers_to_test:
        layer_result = run_layer(model, tokenizer, layer_idx, args.device,
                                 baseline_ppl, layer_name)
        all_results["layers"][str(layer_idx)] = layer_result

    # ══════════════════════════════════════════════════════════════
    # COMPARATIVE SUMMARY
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  COMPARATIVE SUMMARY: L0 vs L15")
    log(f"{'='*70}")

    for key, layer_idx in [("L0 (LEXER)", "0"), ("L15 (OPTIMIZER)", "15")]:
        lr = all_results["layers"][layer_idx]
        log(f"\n  {key}:")
        log(f"    Best natural cluster count: k={lr['best_silhouette_k']}")

        # Cluster sweep
        sil_at_9 = next((c for c in lr["cluster_sweep"] if c["k"] == 9), None)
        sil_best = next((c for c in lr["cluster_sweep"]
                         if c["k"] == lr["best_silhouette_k"]), None)
        if sil_at_9:
            log(f"    Silhouette at k=9: {sil_at_9['silhouette']:.4f}")
        if sil_best:
            log(f"    Silhouette at k={lr['best_silhouette_k']}: {sil_best['silhouette']:.4f}")

        # Mode sweep PPL
        log("    Mode sweep PPL:")
        for r in lr["mode_sweep_ppl"]:
            marker = " ✓" if r["ppl_ratio"] < 1.5 else " ✗" if r["ppl_ratio"] > 10 else " ⚠"
            log(f"      k={r['n_modes']:>4d}: PPL={r['ppl']:>8.2f} ({r['ppl_ratio']:>6.2f}×), "
                f"facts={r['fact_rate']:>4.0%}, cls_acc={r['classifier_acc']:>5.1%}{marker}")

        # Effective rank
        for proj in ["gate_proj", "up_proj", "down_proj"]:
            rk = lr["effective_rank"][proj]
            log(f"    {proj}: eff_rank={rk['effective_rank']:.1f}, "
                f"90%={rk['rank_90']}/{rk['full_rank']} ({rk['rank_90_fraction']:.1%}), "
                f"99%={rk['rank_99']}/{rk['full_rank']} ({rk['rank_99_fraction']:.1%})")

        # Gate PCA
        gp = lr["gate_pca"]
        log(f"    Gate PCA: 90%={gp['components_90']}, 95%={gp['components_95']}, "
            f"99%={gp['components_99']} components")

        # Token property NMI
        nmi = lr["token_properties_best_k"]["nmi_scores"]
        log(f"    Token property NMI: {nmi}")

    # ── Save results ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "l0-characterization"
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}.json"

    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    log(f"\n  Results saved to {out_path}")

    log(f"\n{'='*70}")
    log("  DONE")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
