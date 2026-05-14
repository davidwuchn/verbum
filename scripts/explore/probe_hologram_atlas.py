#!/usr/bin/env python3
"""Probe: What other holograms exist in LLMs beyond combinators?

Session 093 confirmed the combinator hologram (KIBC) — universal sign
topology in attention Q/K/V weights, surviving ternary quantization at
75% sparsity with 100% selectivity preservation, r=0.9801 cross-model.

But combinators only tell the model HOW to compose. Token prediction
requires more. From the Montague/CCG/DisCoCat framework:

  1. TYPE CALCULUS (combinators)  — HOW to compose     ← FOUND
  2. LEXICON (types + meanings)   — WHAT can compose    ← this probe
  3. MODEL (semantic domain)      — WHAT things MEAN    ← this probe

This script probes for five candidate holograms beyond combinators:

  TYPE       — lexical category assignment (NP, S\\NP, etc.)
  INDUCTION  — in-context pattern matching ([A][B]...[A] → [B])
  BINDING    — variable tracking / coreference across distance
  FREQUENCY  — statistical co-occurrence (MLP-based, n-gram)
  DISCOURSE  — topic / register / coherence (gate-level)

Each candidate uses the proven methodology:
  1. Minimal-pair probe sentences (active vs control)
  2. Per-head selectivity measurement (hidden state divergence)
  3. Ternary survival test (does selectivity survive sign-only quantization?)
  4. Cross-hologram orthogonality (do different holograms use different heads?)
  5. Comparison to combinator hologram (overlap or independent?)

Usage:
    # Probe all holograms (full):
    uv run python scripts/explore/probe_hologram_atlas.py

    # Probe specific hologram(s):
    uv run python scripts/explore/probe_hologram_atlas.py --hologram type
    uv run python scripts/explore/probe_hologram_atlas.py --hologram type,induction

    # Quick mode (fewer probes, faster):
    uv run python scripts/explore/probe_hologram_atlas.py --quick

    # Use HF model instead of GGUF:
    uv run python scripts/explore/probe_hologram_atlas.py --model hf

    # Pythia (smaller, faster, cross-model validation):
    uv run python scripts/explore/probe_hologram_atlas.py --model pythia

Output: results/hologram-atlas/

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F


# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

OUTPUT_DIR = Path("results/hologram-atlas")

MODELS = {
    "qwen36": {
        "hf_name": "Qwen/Qwen3.6-35B-A3B",
        "source": "hf",
        "description": "Qwen3.6-35B-A3B MoE — 40L, 256 experts × 8 active, "
                       "hybrid attention (full every 4th layer, GatedDeltaNet rest). "
                       "Best bang-for-compute local model. MoE gates ARE beam selectors.",
    },
    "qwen32b": {
        "path": "/Users/mwhitford/localai/models/Qwen3-32B-Q8_0.gguf",
        "hf_name": "Qwen/Qwen3-32B",
        "source": "gguf",
        "description": "Qwen3-32B dense — 64L, original combinator hologram target.",
    },
    "pythia": {
        "hf_name": "EleutherAI/pythia-160m-deduped",
        "source": "hf",
        "description": "Pythia-160M — 12L, fast cross-architecture validation.",
    },
    "pythia-1b": {
        "hf_name": "EleutherAI/pythia-1b-deduped",
        "source": "hf",
        "description": "Pythia-1B — 24L, mid-scale cross-architecture validation.",
    },
}

ALL_HOLOGRAMS = ["type", "induction", "binding", "frequency", "discourse"]

# Ternary survival thresholds
TERNARY_THRESHOLDS = {
    "sign_only": 0.0,
    "mid_sparse": 0.50,
    "high_sparse": 0.75,
}


# ══════════════════════════════════════════════════════════════════
# Probe sets — minimal pairs for each candidate hologram
# ══════════════════════════════════════════════════════════════════

# ── COMBINATOR probes (baseline — from probe_combinators.py) ─────
# Included so we can measure cross-hologram orthogonality against
# the known-universal combinator hologram.
COMBINATOR_PROBES = {
    "K": {
        "description": "Selection — choose one referent, discard alternative",
        "active": [
            "The cat, not the dog, chased the mouse across the yard.",
            "Either the president or the minister signed the treaty last week.",
            "John, rather than his brother, won the competition in the end.",
        ],
        "control": [
            "The cat chased the mouse across the yard very quickly.",
            "The president signed the treaty at the ceremony last week.",
            "John won the competition in the end with great effort.",
        ],
    },
    "B": {
        "description": "Composition — nested operations, relative clauses",
        "active": [
            "The man who the dog that the cat chased bit ran away quickly.",
            "The student who read the book that the professor recommended passed.",
            "If every teacher who knows a student that failed helps them, all improve.",
        ],
        "control": [
            "The man ran away quickly after the incident in the park.",
            "The student passed the course with excellent marks this year.",
            "If every teacher helps struggling students then all will improve.",
        ],
    },
}

# ── TYPE probes ──────────────────────────────────────────────────
# Theory: In CCG, every token gets a syntactic category (NP, S\NP,
# (S\NP)/NP, etc.). Types constrain which combinators are LEGAL.
# The type hologram should be strongest in early layers, assigned
# BEFORE composition begins.
#
# Probe design: minimal pairs where the SAME lexical content appears
# in different syntactic roles (different type assignments). If heads
# are type-selective, they'll fire differently for the same word in
# different syntactic positions.
TYPE_PROBES = {
    "nominalization": {
        "description": "Same root word, different syntactic category (verb vs noun)",
        "active": [
            # Word used as NOUN (nominalized) — different type than verb
            "The running of the bulls is a famous tradition in Spain.",
            "The building of the bridge took three years of hard work.",
            "Swimming in the ocean is her favorite activity every summer.",
            "The opening of the new store attracted many curious customers.",
            "Reading before bed helps children develop strong language skills.",
            "The painting of the ceiling was done by a master artist.",
        ],
        "control": [
            # Same root word used as VERB — canonical type assignment
            "The bulls are running through the streets of the old town.",
            "The workers are building the bridge over the wide river.",
            "She is swimming in the ocean during her favorite summer vacation.",
            "They are opening the new store to attract many curious customers.",
            "The children are reading before bed to develop language skills.",
            "The artist is painting the ceiling with careful brush strokes.",
        ],
    },
    "argument_structure": {
        "description": "Same verb, different argument count (transitive vs intransitive)",
        "active": [
            # Transitive: verb takes object — type (S\NP)/NP
            "The chef cooked the fish on the grill behind the restaurant.",
            "She opened the door to the garden with a rusty old key.",
            "He broke the window with a ball during the afternoon game.",
            "The teacher read the story to the children every morning.",
            "Mary grew the roses in the garden behind the old house.",
            "The driver turned the car around the corner very carefully.",
        ],
        "control": [
            # Intransitive: same verb, no object — type S\NP
            "The chef cooked for hours on the grill behind the restaurant.",
            "The door opened to the garden with a loud creaking sound.",
            "The window broke during the storm on a cold winter night.",
            "The teacher read aloud to the children every single morning.",
            "The roses grew in the garden behind the old house slowly.",
            "The car turned around the corner very carefully and slowly.",
        ],
    },
    "modifier_scope": {
        "description": "Same words, different modification structure (adjective vs predicate)",
        "active": [
            # Prenominal adjective — modifies noun directly (N/N type)
            "The tall man entered the building through the front door.",
            "A cold wind blew across the empty field all afternoon.",
            "The old woman sat on the wooden bench in the park.",
            "A bright light filled the dark room from the window.",
            "The young doctor treated the sick patient at the clinic.",
            "A heavy rain fell on the dry ground all through the night.",
        ],
        "control": [
            # Predicate adjective — after copula (different type: S\NP)
            "The man who entered the building was remarkably tall indeed.",
            "The wind that blew across the field was bitterly cold today.",
            "The woman who sat on the bench was very old and tired.",
            "The light that filled the room was unusually bright that day.",
            "The doctor who treated the patient was remarkably young still.",
            "The rain that fell on the ground was extremely heavy tonight.",
        ],
    },
}

# ── INDUCTION probes ─────────────────────────────────────────────
# Theory: Induction heads implement [A][B]...[A] → predict [B].
# This is in-context pattern matching / copying, NOT composition.
# The induction hologram should be ORTHOGONAL to the combinator
# hologram — different function, different interference pattern.
#
# Probe design: sequences with repeated patterns that require
# in-context copying, vs sequences with no repetition.
INDUCTION_PROBES = {
    "exact_copy": {
        "description": "Exact token repetition — [A][B]...[A] → predict [B]",
        "active": [
            # Pattern: word pair appears twice — second time should predict completion
            "The king wore a golden crown. Later the king wore a golden robe.",
            "She drove to the market on Monday. She drove to the market on Friday.",
            "The red fox jumped over the fence. The red fox jumped over the wall.",
            "He always drinks coffee in the morning. He always drinks coffee at night.",
            "The train arrived at the station early. The train arrived at the platform late.",
            "Birds sang in the garden at dawn. Birds sang in the garden at dusk.",
        ],
        "control": [
            # No repetition — same length, no copying opportunity
            "The king wore a golden crown. Later the queen chose a silver necklace.",
            "She drove to the market on Monday. He walked to the library on Friday.",
            "The red fox jumped over the fence. A brown dog crawled under the gate.",
            "He always drinks coffee in the morning. She prefers tea in the afternoon.",
            "The train arrived at the station early. The bus departed from the terminal late.",
            "Birds sang in the garden at dawn. Crickets chirped in the field at dusk.",
        ],
    },
    "semantic_induction": {
        "description": "Semantic pattern repetition — not exact tokens but same structure",
        "active": [
            # Same syntactic pattern repeated with different content
            "The doctor examined the patient. The lawyer questioned the witness.",
            "Cats chase mice. Dogs chase rabbits. Birds chase insects in the air.",
            "She bought apples at the store. He bought oranges at the store.",
            "The big red ball rolled down the hill. The small blue ball rolled up the hill.",
            "First we plant the seeds. Then we water the seeds. Finally we harvest the crop.",
            "John gave Mary a book. Peter gave Susan a flower. Tom gave Jane a ring.",
        ],
        "control": [
            # Different structures — no pattern to copy
            "The doctor examined the patient. It was raining outside the hospital.",
            "Cats are independent animals. The weather was sunny all week long.",
            "She bought apples at the store. The building was old and crumbling.",
            "The big red ball rolled down the hill. Nobody remembers what happened.",
            "First we plant the seeds. The movie was interesting but too long.",
            "John gave Mary a book. The traffic was terrible on the highway today.",
        ],
    },
}

# ── BINDING probes ───────────────────────────────────────────────
# Theory: Variable binding tracks referent identity across distance.
# "John said he would..." — "he" binds to "John". This is lambda
# variable binding / anaphora resolution. May be related to the I
# combinator (identity = variable binding in lambda calculus).
#
# Probe design: sentences with/without coreference, varying distance.
BINDING_PROBES = {
    "pronoun_binding": {
        "description": "Pronoun binds to antecedent vs no binding needed",
        "active": [
            # Pronoun requires binding to antecedent
            "John went to the store. He bought some milk for his family.",
            "The teacher graded the papers. She gave them back the next day.",
            "Mary called her mother. She told her about the exciting news.",
            "The dog found a bone. It buried it in the yard near the fence.",
            "The students finished their exam. They handed it to the teacher.",
            "The president gave a speech. He addressed the concerns of the nation.",
        ],
        "control": [
            # No pronoun — no binding needed, same semantic content
            "John went to the store. John bought some milk for the family.",
            "The teacher graded the papers. The teacher returned them next day.",
            "Mary called the mother. Mary told the mother about exciting news.",
            "The dog found a bone. The dog buried the bone in the yard.",
            "The students finished the exam. The students handed the exam in.",
            "The president gave a speech. The president addressed the concerns.",
        ],
    },
    "long_distance_binding": {
        "description": "Binding across longer distance vs local reference",
        "active": [
            # Long-distance: pronoun far from antecedent
            "The scientist published a paper. After years of research and many "
            "failed experiments in the laboratory, she finally received recognition.",
            "The captain steered the ship through the storm. After hours of "
            "battling waves and wind on the dark ocean, he reached the safe harbor.",
            "The musician composed a symphony. After months of writing and "
            "revising each movement carefully at the piano, she performed it live.",
        ],
        "control": [
            # Short-distance: reference is local, minimal binding
            "The scientist published a paper. The paper was about quantum physics "
            "and received attention from the international research community.",
            "The captain steered the ship through the storm. The storm lasted "
            "for hours on the dark ocean before the weather finally improved.",
            "The musician composed a symphony. The symphony featured four movements "
            "and was performed at the concert hall for a large audience.",
        ],
    },
}

# ── FREQUENCY probes ─────────────────────────────────────────────
# Theory: Token co-occurrence statistics (bigrams, collocations).
# NOT composition, NOT copying — pure statistical association from
# training distribution. This hologram may live in MLP weights
# rather than attention heads.
#
# Probe design: high-frequency collocations vs low-frequency but
# equally grammatical alternatives.
FREQUENCY_PROBES = {
    "collocation": {
        "description": "High-frequency collocations vs rare but grammatical alternatives",
        "active": [
            # High-frequency collocations — strong statistical association
            "The United States of America is a large and diverse country.",
            "She made a decision to move to New York City for a fresh start.",
            "The stock market experienced a sharp decline last week unexpectedly.",
            "He took a deep breath before stepping onto the stage for the first time.",
            "They reached a consensus after hours of heated debate in the meeting.",
            "The prime minister addressed the nation on live television tonight.",
        ],
        "control": [
            # Rare collocations — grammatical but statistically unlikely
            "The United Provinces of Gelderland is a storied and ancient region.",
            "She made a resolution to move to Lake Wobegon for a quiet life.",
            "The tulip market experienced a sudden collapse last autumn unexpectedly.",
            "He took a sharp inhale before stepping onto the parapet for the first look.",
            "They reached an accord after hours of spirited parley in the chamber.",
            "The chief magistrate addressed the assembly on closed circuit today.",
        ],
    },
    "idiom": {
        "description": "Frozen idioms vs literal paraphrases",
        "active": [
            # Idioms — stored as units, not composed
            "She let the cat out of the bag about the surprise party.",
            "He was beating around the bush instead of answering directly.",
            "They decided to bite the bullet and accept the difficult terms.",
            "The news spread like wildfire through the entire small town.",
            "She was walking on eggshells around her angry boss all day.",
            "He turned a blind eye to the problems in the organization.",
        ],
        "control": [
            # Literal paraphrases — same meaning, composed normally
            "She accidentally revealed the secret about the surprise party.",
            "He was avoiding the topic instead of answering the question directly.",
            "They decided to accept the hardship and agree to the difficult terms.",
            "The news spread rapidly through the entire small town that day.",
            "She was being very careful around her angry boss all day long.",
            "He deliberately ignored the problems in the organization completely.",
        ],
    },
}

# ── DISCOURSE probes ─────────────────────────────────────────────
# Theory: Discourse-level coherence — topic, register, genre.
# This is what the nucleus GATE activates: a reference beam angle
# at the macro level. The discourse hologram MODULATES the other
# holograms, selecting which patterns are active.
#
# Probe design: same semantic content in different registers.
DISCOURSE_PROBES = {
    "register": {
        "description": "Same content, different register (formal vs casual)",
        "active": [
            # Formal register
            "The committee has determined that the proposed amendment shall be "
            "ratified upon receiving a two-thirds majority vote from members.",
            "It is incumbent upon all employees to adhere to the established "
            "protocols regarding the submission of quarterly reports.",
            "The findings of this investigation suggest that further inquiry "
            "into the matter is warranted before any conclusions are drawn.",
            "We respectfully request that all attendees refrain from utilizing "
            "electronic devices during the proceedings of this formal session.",
            "The aforementioned regulations shall take effect immediately upon "
            "publication in the official gazette of the governing body.",
            "The undersigned hereby certifies that the information contained "
            "herein is accurate and complete to the best of their knowledge.",
        ],
        "control": [
            # Casual register — same content
            "The group decided that the change will pass if enough people vote "
            "for it, like at least two out of three of the members.",
            "Everyone at work needs to follow the rules about turning in their "
            "reports every three months on time without any delay.",
            "What we found so far says we should look into this more before "
            "we make up our minds about what actually happened here.",
            "Hey, could everyone please put their phones away while we are "
            "doing this thing? It would really help us all focus better.",
            "The new rules start right away as soon as they get published "
            "officially by the people in charge of making the rules.",
            "I promise that everything I wrote down here is true and complete "
            "as far as I know and I did not leave anything out.",
        ],
    },
    "genre": {
        "description": "Same topic, different genre (narrative vs expository)",
        "active": [
            # Narrative genre — story-like, temporal, characters
            "The old clockmaker peered through his magnifying glass at the tiny "
            "gears. His hands trembled slightly as he placed the final piece.",
            "Rain hammered against the windows as Sarah rushed through the door. "
            "She shook off her umbrella and collapsed into the nearest chair.",
            "The ship creaked and groaned as it rounded the cape. Captain Torres "
            "gripped the wheel tighter and squinted into the driving spray.",
        ],
        "control": [
            # Expository genre — informational, atemporal, no characters
            "Clock repair requires a magnifying glass to inspect the tiny gears. "
            "Steady hands are essential for placing each component precisely.",
            "Heavy rainfall can cause significant water damage to buildings. "
            "Proper drainage systems and waterproof materials reduce this risk.",
            "Ships experience significant stress when rounding capes. Navigation "
            "requires firm control of the wheel and good visibility ahead.",
        ],
    },
}

# Map hologram names to their probe sets
HOLOGRAM_PROBES = {
    "type": TYPE_PROBES,
    "induction": INDUCTION_PROBES,
    "binding": BINDING_PROBES,
    "frequency": FREQUENCY_PROBES,
    "discourse": DISCOURSE_PROBES,
}


# ══════════════════════════════════════════════════════════════════
# Model loading (multi-model support)
# ══════════════════════════════════════════════════════════════════

def load_model(model_key: str, device: str = "mps"):
    """Load model by key from MODELS config."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    cfg = MODELS[model_key]
    hf_name = cfg["hf_name"]
    source = cfg["source"]

    print(f"Loading {hf_name} ({source})...", file=sys.stderr)
    if "description" in cfg:
        print(f"  {cfg['description']}", file=sys.stderr)
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(hf_name, trust_remote_code=True)

    if source == "gguf":
        gguf_path = Path(cfg["path"])
        model = AutoModelForCausalLM.from_pretrained(
            str(gguf_path.parent),
            gguf_file=gguf_path.name,
            dtype=torch.float16,
            device_map=device,
            trust_remote_code=True,
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            hf_name,
            dtype=torch.float16,
            device_map=device,
            trust_remote_code=True,
        )

    model.eval()
    t1 = time.time()

    info = get_model_info(model)
    print(f"Loaded in {t1-t0:.1f}s: {info['n_layers']}L × {info['n_heads']}H, "
          f"d={info['d_model']}", file=sys.stderr)
    if info.get("is_moe"):
        print(f"  MoE: {info['num_experts']} experts × {info['num_experts_per_tok']} active",
              file=sys.stderr)
    if info.get("full_attention_layers"):
        print(f"  Hybrid: full_attn at L{info['full_attention_layers']}, "
              f"linear_attn at {len(info['linear_attention_layers'])} layers",
              file=sys.stderr)

    return model, tokenizer


def get_model_info(model) -> dict:
    """Extract model architecture info, handling nested configs (Qwen3.6 MoE)."""
    config = model.config

    # Handle nested text_config (Qwen3.5/3.6 MoE models)
    if hasattr(config, "text_config"):
        tc = config.text_config
    elif hasattr(config, "get_text_config"):
        tc = config.get_text_config()
    else:
        tc = config

    info = {
        "n_layers": tc.num_hidden_layers,
        "n_heads": tc.num_attention_heads,
        "d_model": tc.hidden_size,
        "head_dim": getattr(tc, "head_dim", tc.hidden_size // tc.num_attention_heads),
        "n_kv_heads": getattr(tc, "num_key_value_heads", tc.num_attention_heads),
    }

    # MoE info
    if hasattr(tc, "num_experts"):
        info["is_moe"] = True
        info["num_experts"] = tc.num_experts
        info["num_experts_per_tok"] = getattr(tc, "num_experts_per_tok", 8)
    else:
        info["is_moe"] = False

    # Hybrid attention info (Qwen3.6: full_attention every 4th layer)
    if hasattr(tc, "layer_types"):
        info["layer_types"] = tc.layer_types
        info["full_attention_layers"] = [
            i for i, t in enumerate(tc.layer_types) if t == "full_attention"
        ]
        info["linear_attention_layers"] = [
            i for i, t in enumerate(tc.layer_types) if t != "full_attention"
        ]
    else:
        info["full_attention_layers"] = None
        info["linear_attention_layers"] = None

    return info


def get_decoder_layers(model):
    """Get the list of decoder layers, handling different model architectures."""
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers  # Qwen, Qwen3.6 MoE, LLaMA, Mistral
    elif hasattr(model, "gpt_neox") and hasattr(model.gpt_neox, "layers"):
        return model.gpt_neox.layers  # Pythia / GPT-NeoX
    else:
        raise ValueError(f"Unknown model architecture: {type(model)}")


def get_layer_attn_type(layer) -> str:
    """Determine attention type for a layer.

    Qwen3.6-35B-A3B hybrid architecture:
      - Full attention layers (every 4th): have self_attn (Qwen3_5MoeAttention)
      - Linear attention layers: have linear_attn (Qwen3_5MoeGatedDeltaNet)

    Returns: "full_attention", "linear_attention", or "standard"
    """
    if hasattr(layer, "self_attn") and hasattr(layer, "linear_attn"):
        # Shouldn't happen, but be safe
        return "full_attention"
    elif hasattr(layer, "self_attn"):
        return "full_attention"
    elif hasattr(layer, "linear_attn"):
        return "linear_attention"
    elif hasattr(layer, "attention"):
        return "standard"  # Pythia / GPT-NeoX
    else:
        raise ValueError(f"Unknown layer architecture: {type(layer)}")


def get_attn_module(layer):
    """Get the attention module from a decoder layer.

    Handles Qwen3.6 hybrid: full_attention layers use self_attn,
    linear_attention layers use linear_attn (GatedDeltaNet).
    """
    if hasattr(layer, "self_attn"):
        return layer.self_attn       # Qwen full attention, LLaMA
    elif hasattr(layer, "linear_attn"):
        return layer.linear_attn     # Qwen3.6 GatedDeltaNet
    elif hasattr(layer, "attention"):
        return layer.attention       # Pythia / GPT-NeoX
    else:
        raise ValueError(f"Unknown layer architecture: {type(layer)}")


def get_attn_proj_names(attn_module) -> list[str]:
    """Get the names of weight-bearing projection layers in attention.

    Architecture-aware:
      - Qwen full attention: q_proj, k_proj, v_proj, o_proj
      - Qwen3.6 GatedDeltaNet: in_proj_qkv, in_proj_z, in_proj_b, in_proj_a, out_proj
      - Pythia / GPT-NeoX: query_key_value, dense
    """
    # Qwen / LLaMA full attention
    if hasattr(attn_module, "q_proj"):
        return ["q_proj", "k_proj", "v_proj", "o_proj"]
    # Qwen3.6 GatedDeltaNet (linear attention)
    elif hasattr(attn_module, "in_proj_qkv"):
        names = ["in_proj_qkv", "out_proj"]
        if hasattr(attn_module, "in_proj_z"):
            names.append("in_proj_z")
        if hasattr(attn_module, "in_proj_b"):
            names.append("in_proj_b")
        if hasattr(attn_module, "in_proj_a"):
            names.append("in_proj_a")
        return names
    # Pythia / GPT-NeoX (fused QKV)
    elif hasattr(attn_module, "query_key_value"):
        return ["query_key_value", "dense"]
    else:
        # Fallback: find any Linear layers with 'proj' in name
        names = []
        for n, m in attn_module.named_children():
            if hasattr(m, "weight") and ("proj" in n or "dense" in n):
                names.append(n)
        if names:
            return names
        raise ValueError(f"Cannot find attention projections in {type(attn_module)}")


# ══════════════════════════════════════════════════════════════════
# Hidden state capture and selectivity measurement
# ══════════════════════════════════════════════════════════════════

def get_hidden_states(model, tokenizer, text: str, layers: list[int]) -> dict:
    """Capture hidden states at specified layers via hooks."""
    decoder_layers = get_decoder_layers(model)
    captured = {}
    hooks = []

    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            if isinstance(output, tuple):
                h = output[0]
            else:
                h = output
            captured[layer_idx] = h.detach().cpu().float()
        return hook_fn

    for li in layers:
        hooks.append(decoder_layers[li].register_forward_hook(make_hook(li)))

    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model(**inputs)

    for h in hooks:
        h.remove()

    logits = outputs.logits[0, -1].detach().cpu().float()
    return {"hidden_states": captured, "logits": logits}


def measure_selectivity(
    model, tokenizer, probes: dict, layers: list[int],
    quick: bool = False,
) -> dict:
    """Measure per-condition selectivity across probe pairs.

    For each condition (sub-probe), computes:
      - Hidden state divergence (active vs control) at each layer
      - Output logit divergence (KL)

    Returns: {condition_name: {layer_selectivity: {layer: float}, output_kl: float}}
    """
    results = {}

    for cond_name, cond_data in probes.items():
        active_texts = cond_data["active"]
        control_texts = cond_data["control"]

        if quick:
            active_texts = active_texts[:2]
            control_texts = control_texts[:2]

        n_pairs = min(len(active_texts), len(control_texts))
        layer_sel = {li: [] for li in layers}
        output_kls = []

        for i in range(n_pairs):
            a = get_hidden_states(model, tokenizer, active_texts[i], layers)
            c = get_hidden_states(model, tokenizer, control_texts[i], layers)

            for li in layers:
                h_a = a["hidden_states"][li][0].mean(dim=0)
                h_c = c["hidden_states"][li][0].mean(dim=0)
                cos = F.cosine_similarity(
                    h_a.unsqueeze(0), h_c.unsqueeze(0)
                ).item()
                layer_sel[li].append(1.0 - cos)

            p = F.softmax(a["logits"], dim=-1)
            q = F.softmax(c["logits"], dim=-1)
            kl = F.kl_div(q.log(), p, reduction="sum").item()
            output_kls.append(kl)

            if torch.backends.mps.is_available():
                torch.mps.empty_cache()

        results[cond_name] = {
            "description": cond_data["description"],
            "n_pairs": n_pairs,
            "layer_selectivity": {
                li: float(np.mean(layer_sel[li])) for li in layers
            },
            "output_kl": float(np.mean(output_kls)),
        }

    return results


def aggregate_selectivity(per_condition: dict, layers: list[int]) -> dict:
    """Aggregate selectivity across conditions into a single profile."""
    all_layer_sel = {li: [] for li in layers}
    all_kls = []

    for cond_name, cond in per_condition.items():
        for li in layers:
            all_layer_sel[li].append(cond["layer_selectivity"][li])
        all_kls.append(cond["output_kl"])

    return {
        "layer_selectivity": {
            li: float(np.mean(all_layer_sel[li])) for li in layers
        },
        "output_kl": float(np.mean(all_kls)),
    }


# ══════════════════════════════════════════════════════════════════
# Ternary quantization + survival test
# ══════════════════════════════════════════════════════════════════

def ternary_quantize_layer(model, layer_idx: int, threshold_pct: float):
    """Quantize attention Q/K/V/O weights to ternary {-1, 0, +1}.

    Returns (originals, stats) for restoration.
    """
    decoder_layers = get_decoder_layers(model)
    attn = get_attn_module(decoder_layers[layer_idx])
    proj_names = get_attn_proj_names(attn)

    originals = {}
    stats = {}

    for wn in proj_names:
        proj = getattr(attn, wn)
        w = proj.weight.data
        originals[wn] = w.clone()

        # All computation on CPU to avoid MPS indexing bugs on large tensors
        w_cpu = w.cpu().float()
        abs_cpu = w_cpu.abs()
        if threshold_pct > 0:
            flat = abs_cpu.flatten()
            if flat.numel() > 1_000_000:
                indices = torch.randperm(flat.numel())[:1_000_000]
                sample = flat[indices]
            else:
                sample = flat
            threshold = torch.quantile(sample, threshold_pct).item()
        else:
            threshold = 0.0

        mask = abs_cpu > threshold
        scale = abs_cpu[mask].mean().item() if mask.any() else 1.0
        ternary = torch.zeros_like(w_cpu)
        ternary[w_cpu > threshold] = 1.0
        ternary[w_cpu < -threshold] = -1.0

        # Stats on CPU (safe from MPS bounds errors)
        n_total = ternary.numel()
        n_zero = int((ternary == 0).sum().item())
        n_pos = int((ternary > 0).sum().item())
        n_neg = int((ternary < 0).sum().item())

        # Apply back to device
        proj.weight.data = (ternary * scale).to(w.device).to(w.dtype)

        stats[wn] = {
            "shape": list(w.shape),
            "sparsity": n_zero / n_total,
            "balance": n_pos / max(n_neg, 1),
        }

    return originals, stats


def restore_layer(model, layer_idx: int, originals: dict):
    """Restore original weights after quantization."""
    decoder_layers = get_decoder_layers(model)
    attn = get_attn_module(decoder_layers[layer_idx])
    for wn, w in originals.items():
        getattr(attn, wn).weight.data = w


def ternary_quantize_mlp(model, layer_idx: int, threshold_pct: float):
    """Quantize MLP weights to ternary (for frequency hologram test).

    MLP architecture varies:
      - Qwen3.6 MoE: gate (256×2048 router), shared_expert, 256 experts
        We quantize the GATE matrix (the beam selector) and shared expert.
        Individual experts are too numerous — gate is the hologram.
      - Qwen/LLaMA dense: gate_proj, up_proj, down_proj
      - Pythia: dense_h_to_4h, dense_4h_to_h
    """
    decoder_layers = get_decoder_layers(model)
    layer = decoder_layers[layer_idx]

    # Find MLP module
    if hasattr(layer, "mlp"):
        mlp = layer.mlp
    elif hasattr(layer, "feed_forward"):
        mlp = layer.feed_forward
    else:
        raise ValueError(f"Cannot find MLP in layer: {type(layer)}")

    originals = {}
    stats = {}

    # Identify which weights to quantize
    target_modules = []

    # MoE architecture (Qwen3.6): quantize gate + shared expert
    if hasattr(mlp, "gate") and hasattr(mlp.gate, "weight"):
        target_modules.append(("gate", mlp.gate))
    if hasattr(mlp, "shared_expert"):
        for name, mod in mlp.shared_expert.named_children():
            if hasattr(mod, "weight"):
                target_modules.append((f"shared_expert.{name}", mod))
    if hasattr(mlp, "shared_expert_gate") and hasattr(mlp.shared_expert_gate, "weight"):
        target_modules.append(("shared_expert_gate", mlp.shared_expert_gate))

    # Dense MLP fallback: gate_proj, up_proj, down_proj or dense_h_to_4h, dense_4h_to_h
    if not target_modules:
        for name, mod in mlp.named_children():
            if hasattr(mod, "weight") and ("proj" in name or "dense" in name):
                target_modules.append((name, mod))

    for name, mod in target_modules:
        w = mod.weight.data
        originals[name] = w.clone()

        # Compute on CPU to avoid MPS indexing bugs on large tensors
        w_cpu = w.cpu().float()
        abs_cpu = w_cpu.abs()
        if threshold_pct > 0:
            flat = abs_cpu.flatten()
            if flat.numel() > 1_000_000:
                indices = torch.randperm(flat.numel())[:1_000_000]
                sample = flat[indices]
            else:
                sample = flat
            threshold = torch.quantile(sample, threshold_pct).item()
        else:
            threshold = 0.0

        mask = abs_cpu > threshold
        scale = abs_cpu[mask].mean().item() if mask.any() else 1.0
        ternary = torch.zeros_like(w_cpu)
        ternary[w_cpu > threshold] = 1.0
        ternary[w_cpu < -threshold] = -1.0

        n_total = ternary.numel()
        n_zero = int((ternary == 0).sum().item())

        # Apply back to device
        mod.weight.data = (ternary * scale).to(w.device).to(w.dtype)

        stats[name] = {
            "shape": list(w.shape),
            "sparsity": n_zero / n_total,
            "is_moe_gate": "gate" in name and "shared" not in name,
        }

    return originals, stats


def restore_mlp(model, layer_idx: int, originals: dict):
    """Restore original MLP weights."""
    decoder_layers = get_decoder_layers(model)
    layer = decoder_layers[layer_idx]

    if hasattr(layer, "mlp"):
        mlp = layer.mlp
    elif hasattr(layer, "feed_forward"):
        mlp = layer.feed_forward
    else:
        return

    for name, w in originals.items():
        parts = name.split(".")
        mod = mlp
        for part in parts:
            mod = getattr(mod, part)
        mod.weight.data = w


def run_ternary_survival(
    model, tokenizer, probes: dict,
    target_layers: list[int],
    measure_layers: list[int],
    thresholds: dict[str, float],
    quantize_target: str = "attention",  # "attention" or "mlp"
    quick: bool = False,
) -> dict:
    """Run ternary survival test for a set of probes.

    1. Measure baseline selectivity
    2. For each target layer × threshold:
       - Quantize weights to ternary
       - Re-measure selectivity
       - Compute survival ratio
       - Restore weights
    """
    # Baseline
    print("    Measuring baseline...", file=sys.stderr)
    baseline = measure_selectivity(model, tokenizer, probes, measure_layers, quick)
    baseline_agg = aggregate_selectivity(baseline, measure_layers)

    results = {
        "baseline": {
            "per_condition": {k: v for k, v in baseline.items()},
            "aggregate": baseline_agg,
        },
        "experiments": {},
    }

    for target_layer in target_layers:
        results["experiments"][target_layer] = {}

        for thresh_name, thresh_pct in thresholds.items():
            print(f"    L{target_layer} × {thresh_name}...", file=sys.stderr)

            # Quantize
            if quantize_target == "attention":
                originals, quant_stats = ternary_quantize_layer(
                    model, target_layer, thresh_pct)
            else:
                originals, quant_stats = ternary_quantize_mlp(
                    model, target_layer, thresh_pct)

            # Measure
            quantized = measure_selectivity(
                model, tokenizer, probes, measure_layers, quick)
            quantized_agg = aggregate_selectivity(quantized, measure_layers)

            # Survival ratios
            survival = {}
            for li in measure_layers:
                b = baseline_agg["layer_selectivity"][li]
                q = quantized_agg["layer_selectivity"][li]
                survival[li] = q / max(b, 1e-8)

            b_kl = baseline_agg["output_kl"]
            q_kl = quantized_agg["output_kl"]
            output_survival = q_kl / max(b_kl, 1e-8)

            results["experiments"][target_layer][thresh_name] = {
                "quant_stats": quant_stats,
                "quantize_target": quantize_target,
                "aggregate_selectivity": quantized_agg,
                "layer_survival": {str(k): v for k, v in survival.items()},
                "output_survival": output_survival,
                "survived": 0.5 < output_survival < 2.0,
            }

            # Restore
            if quantize_target == "attention":
                restore_layer(model, target_layer, originals)
            else:
                restore_mlp(model, target_layer, originals)

    return results


# ══════════════════════════════════════════════════════════════════
# Cross-hologram orthogonality
# ══════════════════════════════════════════════════════════════════

def compute_orthogonality(
    selectivity_profiles: dict[str, dict],
    measure_layers: list[int],
) -> dict:
    """Compare selectivity profiles across holograms.

    If two holograms use different heads/layers, their selectivity
    profiles will have low correlation (orthogonal). If they share
    heads, high correlation (angle-multiplexed in the same substrate).
    """
    hologram_names = sorted(selectivity_profiles.keys())
    n = len(hologram_names)

    # Build vectors: selectivity across all layers
    vectors = {}
    for name in hologram_names:
        profile = selectivity_profiles[name]
        vec = np.array([profile[li] for li in measure_layers])
        vectors[name] = vec

    # Correlation matrix
    corr_matrix = np.zeros((n, n))
    for i, ni in enumerate(hologram_names):
        for j, nj in enumerate(hologram_names):
            if np.std(vectors[ni]) < 1e-10 or np.std(vectors[nj]) < 1e-10:
                corr_matrix[i, j] = 0.0
            else:
                corr_matrix[i, j] = float(
                    np.corrcoef(vectors[ni], vectors[nj])[0, 1]
                )

    # Cosine similarity matrix
    cos_matrix = np.zeros((n, n))
    for i, ni in enumerate(hologram_names):
        for j, nj in enumerate(hologram_names):
            norm_i = np.linalg.norm(vectors[ni])
            norm_j = np.linalg.norm(vectors[nj])
            if norm_i < 1e-10 or norm_j < 1e-10:
                cos_matrix[i, j] = 0.0
            else:
                cos_matrix[i, j] = float(
                    np.dot(vectors[ni], vectors[nj]) / (norm_i * norm_j)
                )

    return {
        "hologram_names": hologram_names,
        "correlation_matrix": corr_matrix.tolist(),
        "cosine_matrix": cos_matrix.tolist(),
        "vectors": {name: vec.tolist() for name, vec in vectors.items()},
    }


# ══════════════════════════════════════════════════════════════════
# MoE gate analysis — the discourse hologram candidate
# ══════════════════════════════════════════════════════════════════

def analyze_moe_gates(model, info: dict) -> dict:
    """Extract and analyze MoE gate matrices as discourse beam selectors.

    The hypothesis: MoE gate matrices (256×2048 in Qwen3.6) implement
    angle multiplexing — 256 holograms addressed by different reference
    beam angles. The gate selects which experts (= which holographic
    patterns) to activate for each token.

    This analysis:
    1. Extracts gate weight matrices from each layer
    2. Checks if gate weights survive ternary quantization (sign topology)
    3. Measures cross-layer gate similarity (do gates at different depths
       select the same experts?)
    4. Computes effective rank of gate matrices
    """
    decoder_layers = get_decoder_layers(model)
    n_layers = len(decoder_layers)

    gate_weights = {}
    gate_stats = {}

    for li in range(n_layers):
        layer = decoder_layers[li]
        if not hasattr(layer, "mlp"):
            continue
        mlp = layer.mlp
        if not hasattr(mlp, "gate") or not hasattr(mlp.gate, "weight"):
            continue

        w = mlp.gate.weight.data.detach().cpu().float()  # (num_experts, d_model)
        gate_weights[li] = w

        # Stats
        sign_w = torch.sign(w)
        n_pos = (sign_w > 0).sum().item()
        n_neg = (sign_w < 0).sum().item()
        n_zero = (sign_w == 0).sum().item()

        # Effective rank via SVD
        try:
            s = torch.linalg.svdvals(w)
            s_norm = s / s.sum()
            eff_rank_90 = int((s_norm.cumsum(0) < 0.90).sum().item()) + 1
            eff_rank_99 = int((s_norm.cumsum(0) < 0.99).sum().item()) + 1
        except Exception:
            eff_rank_90 = -1
            eff_rank_99 = -1

        gate_stats[li] = {
            "shape": list(w.shape),
            "balance": n_pos / max(n_neg, 1),
            "sparsity": n_zero / w.numel(),
            "effective_rank_90": eff_rank_90,
            "effective_rank_99": eff_rank_99,
            "frobenius_norm": float(w.norm().item()),
        }

    # Cross-layer gate similarity
    gate_layers = sorted(gate_weights.keys())
    n_gates = len(gate_layers)
    cross_layer_cos = np.zeros((n_gates, n_gates))

    for i, li in enumerate(gate_layers):
        for j, lj in enumerate(gate_layers):
            wi = gate_weights[li].flatten()
            wj = gate_weights[lj].flatten()
            cos = float(F.cosine_similarity(wi.unsqueeze(0), wj.unsqueeze(0)).item())
            cross_layer_cos[i, j] = cos

    # Ternary survival of gate matrices
    ternary_survival = {}
    for li in gate_layers[:5]:  # test first 5 layers
        w = gate_weights[li]
        w_ternary = torch.sign(w)
        cos_to_original = float(
            F.cosine_similarity(
                w.flatten().unsqueeze(0),
                w_ternary.flatten().unsqueeze(0)
            ).item()
        )
        ternary_survival[li] = {
            "cos_to_original": cos_to_original,
            "survived": cos_to_original > 0.5,
        }

    print(f"\n  ┌─ MoE Gate Analysis ─────────────────────────────────────────┐")
    print(f"  │ Gate shape: {gate_stats[gate_layers[0]]['shape']} "
          f"({info['num_experts']} experts × d_model)")
    print(f"  │")
    print(f"  │ Per-layer stats:")
    print(f"  │ {'layer':>6} {'balance':>8} {'eff_rank90':>11} {'eff_rank99':>11}")
    for li in gate_layers:
        s = gate_stats[li]
        print(f"  │ L{li:>4} {s['balance']:>8.3f} {s['effective_rank_90']:>11} "
              f"{s['effective_rank_99']:>11}")
    print(f"  │")
    print(f"  │ Cross-layer gate cosine similarity (sample):")
    sample_layers = gate_layers[::max(1, n_gates // 5)][:6]
    sample_indices = [gate_layers.index(l) for l in sample_layers]
    print(f"  │ {'':>6}", end="")
    for l in sample_layers:
        print(f" {'L'+str(l):>6}", end="")
    print()
    for i, li in zip(sample_indices, sample_layers):
        print(f"  │ {'L'+str(li):>6}", end="")
        for j, lj in zip(sample_indices, sample_layers):
            print(f" {cross_layer_cos[i, j]:>6.3f}", end="")
        print()
    print(f"  │")
    print(f"  │ Ternary survival of gate matrices:")
    for li, s in ternary_survival.items():
        marker = "✓" if s["survived"] else "✗"
        print(f"  │   L{li}: cos={s['cos_to_original']:.3f} {marker}")
    print(f"  └{'─'*72}┘")

    return {
        "gate_stats": {str(k): v for k, v in gate_stats.items()},
        "cross_layer_cosine": cross_layer_cos.tolist(),
        "cross_layer_labels": [f"L{l}" for l in gate_layers],
        "ternary_survival": {str(k): v for k, v in ternary_survival.items()},
    }


# ══════════════════════════════════════════════════════════════════
# Summary output
# ══════════════════════════════════════════════════════════════════

def print_selectivity_summary(
    hologram_name: str,
    selectivity: dict,
    measure_layers: list[int],
):
    """Print selectivity results for a single hologram."""
    agg = aggregate_selectivity(selectivity, measure_layers)

    print(f"\n  ┌─ {hologram_name.upper()} Selectivity ─────────────────────────────┐")
    print(f"  │ {'condition':>20} {'output_KL':>10}", end="")
    for li in measure_layers[:6]:  # limit columns
        print(f" {'L'+str(li):>8}", end="")
    print()

    for cond_name, cond in selectivity.items():
        print(f"  │ {cond_name[:20]:>20} {cond['output_kl']:>10.4f}", end="")
        for li in measure_layers[:6]:
            print(f" {cond['layer_selectivity'][li]:>8.5f}", end="")
        print()

    print(f"  │ {'AGGREGATE':>20} {agg['output_kl']:>10.4f}", end="")
    for li in measure_layers[:6]:
        print(f" {agg['layer_selectivity'][li]:>8.5f}", end="")
    print()
    print(f"  └{'─'*72}┘")


def print_survival_summary(hologram_name: str, survival_results: dict):
    """Print ternary survival results for a single hologram."""
    experiments = survival_results["experiments"]

    print(f"\n  ┌─ {hologram_name.upper()} Ternary Survival ──────────────────────┐")
    print(f"  │ {'layer':>6} {'threshold':>12} {'output_surv':>12} {'survived':>10}")

    total_survived = 0
    total_tests = 0

    for target_layer in sorted(experiments.keys(), key=int):
        for thresh_name in experiments[target_layer]:
            exp = experiments[target_layer][thresh_name]
            surv = exp["output_survival"]
            ok = exp["survived"]
            marker = "  ✓" if ok else "  ✗"
            print(f"  │ {'L'+str(target_layer):>6} {thresh_name:>12} "
                  f"{surv:>12.3f} {marker:>10}")
            total_survived += int(ok)
            total_tests += 1

    frac = total_survived / max(total_tests, 1)
    verdict = "TOPOLOGICAL" if frac > 0.7 else "MIXED" if frac > 0.3 else "PRECISION"
    print(f"  │")
    print(f"  │ Survived: {total_survived}/{total_tests} ({frac:.0%}) → {verdict}")
    print(f"  └{'─'*72}┘")


def print_orthogonality_summary(ortho: dict):
    """Print cross-hologram orthogonality matrix."""
    names = ortho["hologram_names"]
    corr = np.array(ortho["correlation_matrix"])

    print(f"\n  ┌─ Cross-Hologram Correlation ──────────────────────────────────┐")
    print(f"  │ {'':>12}", end="")
    for n in names:
        print(f" {n[:8]:>8}", end="")
    print()

    for i, ni in enumerate(names):
        print(f"  │ {ni[:12]:>12}", end="")
        for j in range(len(names)):
            r = corr[i, j]
            print(f" {r:>8.3f}", end="")
        print()

    print(f"  │")
    # Interpretation
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            r = corr[i, j]
            if abs(r) > 0.7:
                rel = "SHARED substrate"
            elif abs(r) > 0.3:
                rel = "partial overlap"
            else:
                rel = "ORTHOGONAL"
            print(f"  │ {names[i][:8]}↔{names[j][:8]}: r={r:.3f} → {rel}")
    print(f"  └{'─'*72}┘")


# ══════════════════════════════════════════════════════════════════
# Save results
# ══════════════════════════════════════════════════════════════════

def _json_convert(obj):
    """Convert numpy types for JSON serialization."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def save_incremental(all_results: dict, output_dir: Path, label: str = ""):
    """Save current state to disk — call after each hologram completes.

    Writes:
      - hologram_atlas_results.json  (full state, overwritten each time)
      - hologram_atlas_{label}.json  (per-hologram snapshot, never overwritten)
      - selectivity_profiles.npz     (updated each time)

    This ensures partial results survive crashes or early termination.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Full state (overwritten each save)
    json_path = output_dir / "hologram_atlas_results.json"
    json_path.write_text(
        json.dumps(all_results, indent=2, default=_json_convert)
    )
    print(f"  💾 Saved: {json_path}", file=sys.stderr)

    # Per-hologram snapshot (append-only, never overwritten)
    if label:
        snap_path = output_dir / f"hologram_{label}.json"
        holo_data = all_results.get("holograms", {}).get(label, {})
        if holo_data:
            snap_path.write_text(
                json.dumps(holo_data, indent=2, default=_json_convert)
            )
            print(f"  💾 Snapshot: {snap_path}", file=sys.stderr)

    # Selectivity profiles as npz (overwritten each save)
    profiles = {}
    for hname, hdata in all_results.get("holograms", {}).items():
        if "selectivity" in hdata:
            agg = hdata["selectivity"].get("aggregate", {})
            layer_sel = agg.get("layer_selectivity", {})
            if layer_sel:
                profiles[hname] = np.array(
                    [layer_sel[k] for k in sorted(layer_sel.keys(), key=int)]
                )

    if profiles:
        npz_path = output_dir / "selectivity_profiles.npz"
        np.savez_compressed(str(npz_path), **profiles)


def save_results(all_results: dict, output_dir: Path):
    """Final save — same as incremental but with explicit confirmation."""
    save_incremental(all_results, output_dir)
    print(f"  💾 Final results: {output_dir}/", file=sys.stderr)


# ══════════════════════════════════════════════════════════════════
# Main pipeline
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Hologram Atlas Probe — what holograms exist beyond combinators?",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Candidate holograms:
  type       — lexical category assignment (CCG types)
  induction  — in-context pattern matching ([A][B]...[A] → [B])
  binding    — variable tracking / coreference across distance
  frequency  — statistical co-occurrence (MLP-based)
  discourse  — topic / register / coherence (gate-level)

Examples:
  # Probe all holograms on Qwen3.6-35B-A3B MoE (default):
  uv run python scripts/explore/probe_hologram_atlas.py

  # Quick test of type hologram only:
  uv run python scripts/explore/probe_hologram_atlas.py --hologram type --quick

  # Cross-model validation on Pythia:
  uv run python scripts/explore/probe_hologram_atlas.py --model pythia --quick

  # Dense 32B for comparison with prior combinator probes:
  uv run python scripts/explore/probe_hologram_atlas.py --model qwen32b

  # Discourse hologram with MoE gate analysis:
  uv run python scripts/explore/probe_hologram_atlas.py --hologram discourse --skip-combinator-baseline
        """,
    )
    parser.add_argument(
        "--hologram", type=str, default="all",
        help="Which hologram(s) to probe. Comma-separated from: "
             "type,induction,binding,frequency,discourse,all (default: all)",
    )
    parser.add_argument(
        "--model", choices=list(MODELS.keys()), default="qwen36",
        help="Model to probe (default: qwen36 = Qwen3.6-35B-A3B MoE)",
    )
    parser.add_argument(
        "--device", default="mps",
        help="Device (mps, cuda, cpu). Default: mps",
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="Fewer probes and layers for faster iteration",
    )
    parser.add_argument(
        "--skip-ternary", action="store_true",
        help="Skip ternary survival tests (selectivity only)",
    )
    parser.add_argument(
        "--skip-combinator-baseline", action="store_true",
        help="Skip combinator baseline measurement (faster if you only "
             "want the new holograms without cross-hologram comparison)",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=OUTPUT_DIR,
    )
    args = parser.parse_args()

    # Parse hologram selection
    if args.hologram == "all":
        selected = ALL_HOLOGRAMS
    else:
        selected = [h.strip() for h in args.hologram.split(",")]
        for h in selected:
            if h not in ALL_HOLOGRAMS:
                parser.error(f"Unknown hologram: {h}. "
                             f"Choose from: {', '.join(ALL_HOLOGRAMS)}")

    # Determine model-appropriate layers
    model_key = args.model
    model, tokenizer = load_model(model_key, args.device)
    info = get_model_info(model)
    n_layers = info["n_layers"]

    # Measurement layers: architecture-aware selection
    full_attn_layers = info.get("full_attention_layers")

    if full_attn_layers:
        # Hybrid architecture (Qwen3.6): prioritize full-attention layers
        # for measurement since they have standard Q/K/V projections.
        # Full attention at: L3, L7, L11, L15, L19, L23, L27, L31, L35, L39
        # Also include some linear layers to see the difference.
        measure_layers = sorted(set(
            full_attn_layers +  # all full-attention layers
            [0, 1, 2] +        # first few linear layers
            [n_layers - 1]      # last layer
        ))
        # Ternary targets: test both types
        # - Full attention layers: standard Q/K/V (like prior combinator probes)
        # - Linear attention layers: GatedDeltaNet (new — do they store differently?)
        target_layers = [
            3, 7,   # early full-attention
            0, 1,   # early linear-attention (GatedDeltaNet)
            31, 35,  # late full-attention (bimodal B peak from session 093)
        ]
    elif n_layers <= 16:
        # Small model (Pythia-160M: 12 layers)
        measure_layers = list(range(n_layers))
        target_layers = [0, n_layers // 4, n_layers // 2, n_layers - 1]
    elif n_layers <= 32:
        # Medium model
        measure_layers = [0, 2, 4, 8, 12, 16, 20, 24, n_layers - 1]
        target_layers = [1, 3, 8, 16, n_layers - 2]
    else:
        # Large dense model (Qwen3-32B: 64 layers)
        measure_layers = [0, 4, 8, 16, 24, 32, 40, 48, 56, n_layers - 1]
        target_layers = [1, 3, 6, 24, 43]

    if args.quick:
        measure_layers = measure_layers[::2]  # half the layers
        target_layers = target_layers[:2]     # fewer ternary targets

    print(f"\n{'═'*72}")
    print(f"  HOLOGRAM ATLAS PROBE")
    print(f"  Model: {MODELS[model_key]['hf_name']} ({n_layers}L)")
    if full_attn_layers:
        print(f"  Architecture: hybrid (full_attn={full_attn_layers})")
    if info.get("is_moe"):
        print(f"  MoE: {info['num_experts']} experts × {info['num_experts_per_tok']} active")
    print(f"  Holograms: {', '.join(selected)}")
    print(f"  Measure layers: {measure_layers}")
    print(f"  Ternary target layers: {target_layers}")
    print(f"  Quick: {args.quick}")
    print(f"{'═'*72}")

    all_results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": MODELS[model_key]["hf_name"],
        "model_key": model_key,
        "model_info": info,
        "n_layers": n_layers,
        "n_heads": info["n_heads"],
        "d_model": info["d_model"],
        "is_moe": info.get("is_moe", False),
        "full_attention_layers": full_attn_layers,
        "selected_holograms": selected,
        "measure_layers": measure_layers,
        "target_layers": target_layers,
        "quick": args.quick,
        "holograms": {},
    }

    selectivity_profiles = {}  # for cross-hologram comparison

    # ── Optional: combinator baseline for comparison ─────────
    if not args.skip_combinator_baseline:
        cached = args.output_dir / "hologram_combinator.json"
        if cached.exists():
            print(f"\n{'─'*72}")
            print(f"  Combinator baseline — loading from {cached}")
            print(f"{'─'*72}")
            cached_data = json.loads(cached.read_text())
            all_results["holograms"]["combinator"] = cached_data
            agg = cached_data.get("selectivity", {}).get("aggregate", {})
            if agg.get("layer_selectivity"):
                selectivity_profiles["combinator"] = agg["layer_selectivity"]
        else:
            print(f"\n{'─'*72}")
            print(f"  Combinator baseline (for cross-hologram comparison)")
            print(f"{'─'*72}")

            comb_sel = measure_selectivity(
                model, tokenizer, COMBINATOR_PROBES, measure_layers, args.quick)
            comb_agg = aggregate_selectivity(comb_sel, measure_layers)
            selectivity_profiles["combinator"] = comb_agg["layer_selectivity"]

            print_selectivity_summary("combinator (baseline)", comb_sel, measure_layers)

            all_results["holograms"]["combinator"] = {
                "selectivity": {
                    "per_condition": comb_sel,
                    "aggregate": comb_agg,
                },
            }
            save_incremental(all_results, args.output_dir, "combinator")

    # ── Probe each selected hologram ─────────────────────────
    for hname in selected:
        # Check for cached results from prior run
        cached = args.output_dir / f"hologram_{hname}.json"
        if cached.exists():
            print(f"\n{'─'*72}")
            print(f"  {hname.upper()} — cached, loading from {cached}")
            print(f"{'─'*72}")
            cached_data = json.loads(cached.read_text())
            all_results["holograms"][hname] = cached_data
            agg = cached_data.get("selectivity", {}).get("aggregate", {})
            if agg.get("layer_selectivity"):
                selectivity_profiles[hname] = agg["layer_selectivity"]
            continue

        probes = HOLOGRAM_PROBES[hname]

        print(f"\n{'─'*72}")
        print(f"  Probing: {hname.upper()}")
        print(f"{'─'*72}")

        # Phase 1: Selectivity
        print(f"\n  Phase 1: Selectivity measurement", file=sys.stderr)
        sel = measure_selectivity(
            model, tokenizer, probes, measure_layers, args.quick)
        agg = aggregate_selectivity(sel, measure_layers)
        selectivity_profiles[hname] = agg["layer_selectivity"]

        print_selectivity_summary(hname, sel, measure_layers)

        hologram_result = {
            "selectivity": {
                "per_condition": sel,
                "aggregate": agg,
            },
        }

        # Phase 2: Ternary survival
        if not args.skip_ternary:
            print(f"\n  Phase 2: Ternary survival (attention)", file=sys.stderr)
            attn_survival = run_ternary_survival(
                model, tokenizer, probes,
                target_layers=target_layers,
                measure_layers=measure_layers,
                thresholds=TERNARY_THRESHOLDS,
                quantize_target="attention",
                quick=args.quick,
            )
            print_survival_summary(f"{hname} (attention)", attn_survival)
            hologram_result["ternary_survival_attention"] = attn_survival

            # For frequency hologram, ALSO test MLP quantization
            if hname == "frequency":
                print(f"\n  Phase 2b: Ternary survival (MLP)", file=sys.stderr)
                mlp_survival = run_ternary_survival(
                    model, tokenizer, probes,
                    target_layers=target_layers,
                    measure_layers=measure_layers,
                    thresholds=TERNARY_THRESHOLDS,
                    quantize_target="mlp",
                    quick=args.quick,
                )
                print_survival_summary(f"{hname} (MLP)", mlp_survival)
                hologram_result["ternary_survival_mlp"] = mlp_survival

        all_results["holograms"][hname] = hologram_result
        save_incremental(all_results, args.output_dir, hname)

    # ── MoE gate analysis (if MoE model + discourse hologram) ──
    if info.get("is_moe") and "discourse" in selected:
        print(f"\n{'─'*72}")
        print(f"  MoE Gate Analysis — gate matrices as discourse beam selectors")
        print(f"{'─'*72}")

        gate_analysis = analyze_moe_gates(model, info)
        all_results["moe_gate_analysis"] = gate_analysis
        save_incremental(all_results, args.output_dir)

    # ── Cross-hologram orthogonality ─────────────────────────
    if len(selectivity_profiles) >= 2:
        print(f"\n{'─'*72}")
        print(f"  Cross-Hologram Orthogonality Analysis")
        print(f"{'─'*72}")

        ortho = compute_orthogonality(selectivity_profiles, measure_layers)
        print_orthogonality_summary(ortho)
        all_results["orthogonality"] = ortho
        save_incremental(all_results, args.output_dir)

    # ── Final summary ────────────────────────────────────────
    print(f"\n{'═'*72}")
    print(f"  HOLOGRAM ATLAS SUMMARY")
    print(f"{'═'*72}")

    for hname in selected:
        hdata = all_results["holograms"].get(hname, {})
        agg = hdata.get("selectivity", {}).get("aggregate", {})
        kl = agg.get("output_kl", 0)

        # Peak layer
        layer_sel = agg.get("layer_selectivity", {})
        if layer_sel:
            peak_layer = max(layer_sel, key=lambda k: layer_sel[k])
            peak_val = layer_sel[peak_layer]
        else:
            peak_layer = "?"
            peak_val = 0

        # Ternary survival count
        surv_data = hdata.get("ternary_survival_attention", {}).get("experiments", {})
        survived = 0
        total = 0
        for tl in surv_data:
            for tn in surv_data[tl]:
                total += 1
                if surv_data[tl][tn].get("survived", False):
                    survived += 1

        surv_str = f"{survived}/{total}" if total > 0 else "skipped"
        surv_pct = f"({survived/total:.0%})" if total > 0 else ""

        print(f"  {hname:>12}: output_KL={kl:>8.3f}  "
              f"peak=L{peak_layer}({peak_val:.5f})  "
              f"ternary={surv_str} {surv_pct}")

    # ── Save ─────────────────────────────────────────────────
    save_results(all_results, args.output_dir)

    print(f"\n{'═'*72}")
    print(f"  Done. Results: {args.output_dir}/")
    print(f"{'═'*72}")


if __name__ == "__main__":
    main()
