#!/usr/bin/env python3
"""Crystal Seed Probe — Map the universal low-frequency hologram for relational loss.

Philosophy: A crystal doesn't need every atom specified. It needs the LATTICE SEED —
the low-frequency scaffold that all higher-frequency details organize around.
Provide enough of this scaffold and the model "snaps" into the correct configuration.

This probe maps the broadest, most universal patterns across models by:
1. Using DIVERSE probes that span many linguistic axes (not just factual recall)
2. Running the cross-model tomography (Qwen3-14B × OLMo-2-13B)
3. SVD of the universal RDM → every significant eigenvector = a verified dimension
4. Output: verified_dimensions.json containing the full constraint set
5. Each dimension becomes a weighted relational loss term automatically

The probes are designed for MAXIMUM DIVERSITY (span the space) not density.
Each probe axis reveals a different dimension of universal representation structure.
We want the minimum number of probes that maximally constrains the geometry.

Axes probed:
  - Factual recall (geography, science, culture, math, common)
  - Syntactic structure (active/passive, simple/complex, embedded)
  - Semantic relations (synonymy, antonymy, hypernymy, meronymy)
  - Relational structure (cause→effect, agent→action, possession)
  - Analogical structure (A:B::C:D proportional)
  - Temporal structure (past/present, before/after)
  - Logical structure (conditional, negation, quantification)
  - Register (formal/informal)
  - Sentence length / complexity gradient

Usage:
    # Full run (loads both models, captures hidden states, SVD)
    uv run python scripts/explore/probe_crystal_seed.py

    # Quick (use cached RDM from tomography, just compute new probes)
    uv run python scripts/explore/probe_crystal_seed.py --quick

    # With specific models
    uv run python scripts/explore/probe_crystal_seed.py --models qwen3-14b,olmo-2-13b

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path
from collections import defaultdict

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

OUTPUT_DIR = Path("results/holographic-extraction")

# ══════════════════════════════════════════════════════════════════
# Model registry
# ══════════════════════════════════════════════════════════════════

MODELS = {
    "qwen3-14b": "Qwen/Qwen3-14B",
    "olmo-2-13b": "allenai/OLMo-2-1124-13B",
}

# ══════════════════════════════════════════════════════════════════
# Diverse probe set — span the representation space
# ══════════════════════════════════════════════════════════════════

PROBES = {
    # ── Factual recall (carried forward from previous experiments) ──
    "fact_geography": [
        "The capital of France is",
        "The capital of Japan is",
        "The capital of Germany is",
        "The capital of Australia is",
        "The largest ocean is the",
        "The longest river in the world is the",
        "The highest mountain in the world is Mount",
    ],
    "fact_science": [
        "The chemical symbol for gold is",
        "The speed of light is approximately 300,000 kilometers per",
        "DNA stands for deoxyribonucleic",
        "The closest star to Earth is the",
        "Gravity was described by Isaac",
        "The theory of relativity was developed by Albert",
    ],
    "fact_culture": [
        "Shakespeare wrote Romeo and",
        "The Mona Lisa was painted by Leonardo da",
        "The Eiffel Tower is in",
        "The Colosseum is in",
        "The Odyssey was written by",
    ],
    "fact_math": [
        "Two plus two equals",
        "The square root of 144 is",
        "Pi is approximately 3.14",
        "A triangle has three",
        "A right angle measures exactly",
    ],

    # ── Syntactic structure ──
    "syntax_active": [
        "The cat chased the mouse across the",
        "The scientist discovered a new species of",
        "The teacher explained the concept to the",
        "The wind blew the leaves off the",
        "The artist painted a beautiful portrait of",
    ],
    "syntax_passive": [
        "The mouse was chased by the cat across the",
        "A new species was discovered by the scientist in",
        "The concept was explained by the teacher to the",
        "The leaves were blown off by the wind into the",
        "A beautiful portrait was painted by the artist of",
    ],
    "syntax_embedded": [
        "The man who saw the dog that chased the cat went",
        "The book that the student who failed the exam read was",
        "The house that Jack built collapsed after the storm that",
        "The theory which the professor who won the prize proposed was",
        "The song that the band who toured last summer performed became",
    ],
    "syntax_simple": [
        "Dogs bark at strangers in the",
        "Rain falls from the clouds during",
        "Children play in the park after",
        "Stars shine brightly in the clear",
        "Fish swim in the deep blue",
    ],

    # ── Semantic relations ──
    "semantic_synonym": [
        "Big and large mean the same",
        "Happy and joyful are both words for",
        "Fast and quick describe the same",
        "Start and begin have the same",
        "Cold and chilly both refer to",
    ],
    "semantic_antonym": [
        "The opposite of hot is",
        "The opposite of light is",
        "The opposite of fast is",
        "The opposite of big is",
        "The opposite of happy is",
    ],
    "semantic_hypernym": [
        "A dog is a type of",
        "A rose is a type of",
        "A hammer is a type of",
        "Gold is a type of",
        "French is a type of",
    ],
    "semantic_meronym": [
        "A wheel is part of a",
        "A page is part of a",
        "A branch is part of a",
        "A key is part of a",
        "A wing is part of a",
    ],

    # ── Relational structure ──
    "relation_cause_effect": [
        "Because it rained heavily, the river began to",
        "Since the temperature dropped below zero, the water started to",
        "Due to the earthquake, many buildings began to",
        "Because he studied hard, he was able to",
        "Since the sun set, it became very",
    ],
    "relation_agent_action": [
        "The doctor carefully examined the",
        "The chef skillfully prepared the",
        "The pilot safely landed the",
        "The judge carefully considered the",
        "The engineer designed the new",
    ],
    "relation_possession": [
        "The king's crown was made of",
        "The company's profits increased by",
        "The child's toy was broken during",
        "The country's borders extend to the",
        "The library's collection includes many",
    ],

    # ── Analogical structure (A:B as C:?) ──
    "analogy_proportional": [
        "Paris is to France as Tokyo is to",
        "Hot is to cold as light is to",
        "Doctor is to hospital as teacher is to",
        "Pen is to writing as brush is to",
        "Bird is to fly as fish is to",
    ],

    # ── Temporal structure ──
    "temporal_past": [
        "Yesterday the team won the championship by",
        "Last year the company launched its new",
        "In ancient times people believed that the earth was",
        "Before the invention of electricity people used",
        "The dinosaurs went extinct millions of years",
    ],
    "temporal_present": [
        "Right now the sun is shining on the",
        "Currently the world population is approximately",
        "Today most people use smartphones to",
        "At this moment the Earth is rotating around",
        "These days children learn to use computers at",
    ],
    "temporal_future": [
        "Tomorrow the weather will likely be",
        "In the next decade technology will probably",
        "Scientists predict that by 2050 the climate will",
        "Next year the company plans to expand into",
        "Eventually all stars will run out of",
    ],

    # ── Logical structure ──
    "logic_conditional": [
        "If it rains tomorrow then we will need to",
        "If the temperature rises above 100 degrees then the water will",
        "If all mammals are warm-blooded and whales are mammals then whales are",
        "If the store is closed then we will have to",
        "If you mix blue and yellow you will get",
    ],
    "logic_negation": [
        "Not all birds can actually",
        "There is no evidence that the earth is",
        "It is impossible to divide any number by",
        "No human has ever visited the planet",
        "Nothing can travel faster than the speed of",
    ],
    "logic_quantifier": [
        "Every person needs water to",
        "All metals conduct electricity and",
        "Some animals can survive without water for",
        "Most countries in Europe use the",
        "Few people have ever climbed Mount",
    ],

    # ── Register / formality ──
    "register_formal": [
        "The committee hereby resolves to implement the",
        "It is with great pleasure that we announce the",
        "The aforementioned party shall be responsible for",
        "Pursuant to the regulations outlined in section",
        "The empirical evidence strongly suggests that the",
    ],
    "register_informal": [
        "Hey so I was thinking we should probably",
        "Dude that movie was absolutely",
        "Gonna grab some food from the",
        "Yeah no worries I can totally help you with",
        "So basically what happened was the whole thing just",
    ],

    # ── Complexity gradient ──
    "complexity_minimal": [
        "The cat sat on the",
        "Water is",
        "He went to the",
        "She said",
        "It was",
    ],
    "complexity_medium": [
        "The large brown dog ran quickly across the open field toward the",
        "After finishing dinner the family decided to watch a movie about",
        "The new research paper published last week suggests that climate change might",
        "During the summer months many tourists visit the ancient ruins near the",
        "Although the experiment failed the scientists learned something valuable about the",
    ],
    "complexity_high": [
        "The unprecedented geopolitical ramifications of the recently negotiated multilateral trade agreement between the emerging economies of Southeast Asia and the established markets of Western Europe suggest that the fundamental assumptions underlying contemporary macroeconomic",
        "Notwithstanding the considerable methodological limitations inherent in cross-sectional observational studies of this nature, the statistically significant correlation between early childhood nutritional interventions and subsequent cognitive development outcomes provides compelling evidence for the",
        "The recursive self-referential nature of consciousness as conceptualized within the integrated information theory framework poses fundamental challenges to any purely computational account of subjective experience, particularly when one considers the hard problem of",
    ],

    # ══════════════════════════════════════════════════════════════
    # NON-LINGUISTIC AXES — code, reasoning, tools, structure
    # These should reveal ORTHOGONAL dimensions to linguistic probes
    # ══════════════════════════════════════════════════════════════

    # ── Code: Python ──
    "code_python_function": [
        "def fibonacci(n):\n    if n <=",
        "def binary_search(arr, target):\n    left, right = 0, len(arr) -",
        "def merge_sort(lst):\n    if len(lst) <=",
        "class LinkedList:\n    def __init__(self):\n        self.head =",
        "def read_file(path):\n    with open(path, 'r') as",
    ],
    "code_python_expression": [
        "result = [x**2 for x in range(10) if x %",
        "data = {k: v for k, v in zip(keys,",
        "filtered = list(filter(lambda x: x >",
        "total = sum(item.price for item in cart if item.quantity >",
        "output = '\\n'.join(sorted(set(words), key=lambda w: w.",
    ],
    "code_javascript": [
        "const fetchData = async (url) => {\n  const response = await",
        "document.querySelectorAll('.item').forEach(el => {\n    el.addEventListener('click',",
        "const reducer = (state, action) => {\n  switch (action.type) {\n    case",
        "export default function App({ children }) {\n  return (\n    <div className=",
        "const debounce = (fn, ms) => {\n  let timer;\n  return (...args) =>",
    ],
    "code_shell": [
        "find /var/log -name '*.log' -mtime +7 |",
        "cat data.csv | awk -F',' '{print $2}' | sort | uniq -c | sort -",
        "docker run -d --name app -p 8080:80 -v $(pwd):/",
        "git log --oneline --graph --all | head -",
        "curl -X POST -H 'Content-Type: application/json' -d '{\"key\":\"value\"}' http://",
    ],

    # ── Structured output / formatting ──
    "format_json": [
        '{\"name\": \"Alice\", \"age\": 30, \"address\": {\"city\":',
        '[{\"id\": 1, \"status\": \"active\"}, {\"id\": 2, \"status\":',
        '{\"model\": \"gpt-4\", \"messages\": [{\"role\": \"user\", \"content\":',
        '{\"type\": \"object\", \"properties\": {\"name\": {\"type\":',
        '{\"error\": {\"code\": 404, \"message\":',
    ],
    "format_markdown": [
        "# Introduction\n\n## Background\n\nThe field of machine learning has",
        "| Column A | Column B | Column C |\n|----------|----------|----------|\n|",
        "1. First, prepare the environment\n2. Next, install the dependencies\n3.",
        "```python\nimport numpy as np\n\ndef transform(data):\n    return",
        "> **Note:** This approach requires careful consideration of the",
    ],
    "format_yaml": [
        "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name:",
        "services:\n  web:\n    image: nginx:latest\n    ports:\n      -",
        "steps:\n  - name: Build\n    run: |\n      npm install\n      npm",
        "model:\n  name: transformer\n  layers: 12\n  hidden_size:",
        "database:\n  host: localhost\n  port: 5432\n  name:",
    ],

    # ── Reasoning / step-by-step ──
    "reasoning_math": [
        "To solve 3x + 7 = 22, first subtract 7 from both sides to get 3x =",
        "The area of a circle with radius 5 is pi * r^2 = pi *",
        "If a train travels at 60 mph for 2.5 hours, the distance is",
        "To find the derivative of f(x) = x^3 + 2x, we apply the power rule:",
        "The probability of rolling a 6 twice in a row is (1/6) * (1/6) =",
    ],
    "reasoning_logic": [
        "All mammals are warm-blooded. Whales are mammals. Therefore, whales are",
        "If it is raining, the ground is wet. The ground is wet. Can we conclude",
        "Premise: No reptiles have fur. Premise: All dogs have fur. Conclusion: No dogs are",
        "Given: A implies B. Given: not B. By modus tollens, we conclude:",
        "Either the butler or the maid committed the crime. The maid has an alibi. Therefore,",
    ],
    "reasoning_planning": [
        "To bake a cake, the steps are: 1) preheat oven to 350F, 2) mix dry ingredients, 3)",
        "To deploy this application, first we need to: build the Docker image, then push to registry, then",
        "The project timeline is: Week 1 - requirements, Week 2 - design, Week 3 -",
        "To debug this issue, I should: 1) reproduce the error, 2) check the logs, 3)",
        "My morning routine: wake up at 6am, exercise for 30 minutes, shower, then",
    ],

    # ── Tool use / API patterns ──
    "tool_function_call": [
        "I need to search for information. <tool_call>\n{\"name\": \"search\", \"arguments\": {\"query\":",
        "Let me calculate that. <tool_call>\n{\"name\": \"calculator\", \"arguments\": {\"expression\":",
        "I'll look up the weather. <tool_call>\n{\"name\": \"weather\", \"arguments\": {\"location\":",
        "Let me read that file. <tool_call>\n{\"name\": \"read_file\", \"arguments\": {\"path\":",
        "I'll create a new document. <tool_call>\n{\"name\": \"write\", \"arguments\": {\"content\":",
    ],
    "tool_api_response": [
        "<tool_response>\n{\"results\": [{\"title\": \"Machine Learning\", \"url\":",
        "<tool_response>\n{\"temperature\": 72, \"condition\": \"sunny\", \"humidity\":",
        "<tool_response>\n{\"status\": \"success\", \"data\": {\"id\": 12345, \"created\":",
        "<tool_response>\n{\"error\": null, \"output\": \"Hello, World!\\n\", \"exit_code\":",
        "<tool_response>\n{\"files\": [{\"name\": \"main.py\", \"size\": 1234, \"modified\":",
    ],

    # ── Instruction following / control ──
    "instruction_system": [
        "You are a helpful assistant. You should provide clear, accurate answers and",
        "You are an expert Python developer. When writing code, always include type hints and",
        "You are a medical professional. Never provide diagnoses. Always recommend consulting a",
        "You are a creative writing assistant. Use vivid imagery and avoid cliches. Your tone should be",
        "You are a data analyst. Present findings with statistical rigor and",
    ],
    "instruction_constraint": [
        "Answer in exactly three sentences. Do not use the word 'the'. The topic is",
        "Respond only in JSON format. Include fields: name, description, and",
        "List exactly five items, numbered. Each item must be under ten words.",
        "Explain this concept as if speaking to a five-year-old child who has never",
        "Write your response as a haiku (5-7-5 syllables). The subject is",
    ],

    # ── Pattern completion / sequence ──
    "pattern_numeric": [
        "1, 1, 2, 3, 5, 8, 13, 21,",
        "2, 4, 8, 16, 32, 64,",
        "1, 4, 9, 16, 25, 36,",
        "0, 1, 1, 2, 3, 5, 8,",
        "3, 6, 9, 12, 15, 18,",
    ],
    "pattern_alphabetic": [
        "A, C, E, G, I, K,",
        "Z, Y, X, W, V, U,",
        "AA, AB, AC, AD, AE,",
        "alpha, beta, gamma, delta,",
        "do, re, mi, fa, sol,",
    ],

    # ── Multilingual (shared structure across languages) ──
    "multilingual_romance": [
        "En francais: Le chat est sur la",
        "En espanol: El gato esta en la",
        "In italiano: Il gatto e sul",
        "Em portugues: O gato esta no",
        "In romaneste: Pisica este pe",
    ],
    "multilingual_greeting": [
        "Hello, how are you doing today? I hope you are",
        "Hola, como estas hoy? Espero que estes",
        "Bonjour, comment allez-vous aujourd'hui? J'espere que vous",
        "Hallo, wie geht es Ihnen heute? Ich hoffe Sie",
        "Konnichiwa, kyou wa ogenki desu ka? Odaiji ni",
    ],

    # ══════════════════════════════════════════════════════════════
    # OPERATION-LEVEL AXES — cognitive modes, directionality, epistemic
    # ══════════════════════════════════════════════════════════════

    # ── Compression / Summarization ──
    "compress_tldr": [
        "The following is a summary of the key points:",
        "In brief, the main argument is that",
        "TL;DR: The article discusses how",
        "To summarize the three main findings:",
        "The executive summary: Our quarterly results show",
    ],

    # ── Expansion / Elaboration ──
    "expand_elaborate": [
        "Let me explain this in more detail. The concept of entropy",
        "To elaborate on that point, there are several factors to consider:",
        "Breaking this down step by step: First, we need to understand that",
        "In other words, what this really means is that the underlying",
        "To put it more concretely, imagine a scenario where",
    ],

    # ── Classification / Labeling ──
    "classify_sentiment": [
        "The sentiment of this review is clearly",
        "This text expresses a primarily negative emotion of",
        "Based on the tone, this message is",
        "The overall sentiment: positive. The key indicators are",
        "Classification: This is a complaint about",
    ],
    "classify_category": [
        "This article belongs to the category of",
        "Topic: Science. Subtopic:",
        "This question is about mathematics, specifically",
        "Genre: Fantasy fiction. Key elements include",
        "This falls under the domain of computer science, particularly",
    ],

    # ── Evaluation / Judgment ──
    "evaluate_quality": [
        "Rating: 4/5. The strengths of this approach are",
        "This solution is suboptimal because it fails to",
        "Comparing the two options, the first is better due to",
        "The main weakness of this argument is that it",
        "This code has a critical bug: the variable",
    ],

    # ── Certainty / Epistemic state ──
    "epistemic_certain": [
        "I am absolutely certain that the answer is",
        "This is definitively correct because",
        "There is no doubt that the result is",
        "The evidence conclusively shows that",
        "It is a well-established fact that",
    ],
    "epistemic_uncertain": [
        "I'm not entirely sure, but it might be",
        "This is speculative, but one possibility is that",
        "There are competing theories, and the evidence suggests",
        "I would estimate approximately, though this could be",
        "It's difficult to say with certainty, but perhaps",
    ],

    # ── Correction / Error handling ──
    "correction_fix": [
        "Actually, that's incorrect. The right answer is",
        "There's an error in line 3: you should change",
        "That's a common misconception. In reality,",
        "Wait, let me reconsider. The correct approach is",
        "I need to correct my earlier statement:",
    ],

    # ── Refusal / Boundaries ──
    "refusal_boundary": [
        "I cannot provide instructions for creating",
        "I'm not able to help with that request because",
        "That falls outside my capabilities. Instead, I can",
        "I don't have access to real-time information about",
        "I should not speculate about specific individuals'",
    ],

    # ── Inverse / Reverse operations ──
    "inverse_debug": [
        "The output is 'IndexError'. This means the code tried to",
        "Given this error message, the likely cause is",
        "Working backwards from the result, the input must have been",
        "To produce this output, the function must have received",
        "Reverse engineering: if the hash is X, the original",
    ],

    # ── Meta / Self-reference ──
    "meta_self_reference": [
        "As a language model, I process text by",
        "The previous paragraph contained three logical fallacies:",
        "This sentence has exactly seven words in it",
        "Let me think about what I just said and whether",
        "The structure of this conversation so far has been",
    ],

    # ── Dialogue / Turn-taking ──
    "dialogue_question": [
        "What do you think about the current state of",
        "Could you help me understand why the",
        "How would you approach solving this problem if",
        "Can you explain the difference between",
        "What would happen if we changed the",
    ],
    "dialogue_acknowledgment": [
        "That's a great point. Building on your observation,",
        "I see what you mean. Let me add that",
        "Yes, exactly. And furthermore, this implies that",
        "I understand your concern. Here's how we can address",
        "Good question. The short answer is",
    ],

    # ── Specificity gradient ──
    "specificity_concrete": [
        "At 3:47 PM on March 15th, 2023, the red Toyota Camry with plate number",
        "The 47-year-old male patient presented with a 3cm laceration on the left",
        "In apartment 4B at 221 Baker Street, the temperature was exactly",
        "The function received exactly 3 arguments: 'hello', 42, and",
        "On row 157 of the spreadsheet, column F contains the value",
    ],
    "specificity_abstract": [
        "The fundamental nature of consciousness remains",
        "In general, systems tend toward equilibrium when",
        "The relationship between form and function in any",
        "All recursive processes share the property of",
        "The concept of emergence suggests that complex behavior arises from",
    ],

    # ── Narrative / Creative ──
    "narrative_story": [
        "Once upon a time, in a kingdom far away, there lived a",
        "The detective examined the crime scene carefully, noting that the",
        "She opened the letter with trembling hands, knowing that its contents would",
        "The spaceship emerged from hyperspace to find the planet completely",
        "Years later, he would remember this moment as the turning point when",
    ],
    "narrative_descriptive": [
        "The sunset painted the sky in brilliant shades of orange and",
        "The old library smelled of dust and leather, its shelves lined with",
        "The city at night was alive with neon lights reflecting off the wet",
        "The garden in spring was a riot of color, with tulips and",
        "The mountain loomed above them, its peak shrouded in thick gray",
    ],
}


def flatten_probes(probe_dict: dict | None = None) -> list[dict]:
    """Flatten all probes with axis labels."""
    if probe_dict is None:
        probe_dict = PROBES
    flat = []
    for axis, prompts in probe_dict.items():
        for prompt in prompts:
            flat.append({"prompt": prompt, "axis": axis})
    return flat


# ══════════════════════════════════════════════════════════════════
# Hidden state extraction (reused from tomography)
# ══════════════════════════════════════════════════════════════════


def extract_hidden_states(
    model_key: str,
    target_layers: list[int],
    probes: list[dict],
    device: str,
) -> dict[int, np.ndarray]:
    """Extract last-position hidden states at target layers for all probes."""
    model_info = MODELS[model_key]
    model_name = model_info

    print(f"  Loading {model_key} ({model_name})...", file=sys.stderr)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=device,
    )
    model.eval()

    layers = model.model.layers
    hidden_captures = {li: [] for li in target_layers}
    hooks = []

    for li in target_layers:
        def make_hook(layer_idx):
            def hook_fn(module, input, output):
                if isinstance(output, tuple):
                    h = output[0]
                else:
                    h = output
                hidden_captures[layer_idx].append(h.detach().cpu().float())
            return hook_fn
        h = layers[li].register_forward_hook(make_hook(li))
        hooks.append(h)

    # Batched: process probes in chunks to avoid OOM on large models
    print(f"  Running {len(probes)} probes (batched)...", file=sys.stderr)
    batch_size = 32  # probes per batch — tune for GPU memory
    encoded = [tokenizer.encode(p["prompt"]) for p in probes]
    lengths = [len(e) for e in encoded]
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id

    for batch_start in range(0, len(probes), batch_size):
        batch_end = min(batch_start + batch_size, len(probes))
        batch_encoded = encoded[batch_start:batch_end]
        batch_lengths = lengths[batch_start:batch_end]
        max_len = max(batch_lengths)

        # Right-pad to max length in this batch
        padded = [e + [pad_id] * (max_len - len(e)) for e in batch_encoded]
        input_ids = torch.tensor(padded, dtype=torch.long, device=device)

        with torch.no_grad():
            _ = model(input_ids)

    for h in hooks:
        h.remove()

    # Extract last REAL token for each probe from batched captures
    hidden_states = {}
    for li in target_layers:
        # hidden_captures[li] is a list of tensors, one per batch: (batch, max_len, d)
        all_last_token = []
        probe_idx = 0
        for batch_h in hidden_captures[li]:
            batch_len = batch_h.shape[0]
            for i in range(batch_len):
                if probe_idx < len(probes):
                    last_pos = lengths[probe_idx] - 1
                    all_last_token.append(batch_h[i, last_pos, :].unsqueeze(0))
                    probe_idx += 1
        hidden_states[li] = torch.cat(all_last_token, dim=0).numpy()

    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    return hidden_states


# ══════════════════════════════════════════════════════════════════
# Auto-discovery of verified dimensions
# ══════════════════════════════════════════════════════════════════


def discover_dimensions(
    universal_rdm: np.ndarray,
    probes: list[dict],
    min_eigenvalue_frac: float = 0.005,
) -> dict:
    """SVD the universal RDM → extract verified dimensions.

    Each eigenvector with eigenvalue > noise floor is a verified
    dimension of universal representation structure.

    Returns:
        {
            "n_dimensions": int,
            "eigenvalues": list[float],
            "explained_variance": list[float],
            "cumulative_variance": list[float],
            "dimensions": [
                {
                    "index": int,
                    "eigenvalue": float,
                    "variance_explained": float,
                    "axis_loadings": {axis: mean_loading},
                    "interpretation": str,
                }
            ]
        }
    """
    n = universal_rdm.shape[0]

    # SVD
    U, S, Vt = np.linalg.svd(universal_rdm)
    explained = S ** 2 / (S ** 2).sum()
    cumvar = np.cumsum(explained)

    # Find significant dimensions (above noise floor)
    significant = explained > min_eigenvalue_frac
    n_dims = int(significant.sum())

    # For each significant dimension: what axes load on it?
    axes = [p["axis"] for p in probes]
    unique_axes = sorted(set(axes))

    dimensions = []
    for dim_idx in range(n_dims):
        loadings = Vt[dim_idx]  # (n_probes,) — how each probe loads on this dimension

        # Mean loading per axis
        axis_loadings = {}
        for ax in unique_axes:
            ax_indices = [i for i, a in enumerate(axes) if a == ax]
            axis_loadings[ax] = float(np.mean(loadings[ax_indices]))

        # Find the axes with strongest positive and negative loadings
        sorted_axes = sorted(axis_loadings.items(), key=lambda x: x[1])
        neg_end = sorted_axes[:3]
        pos_end = sorted_axes[-3:]

        # Auto-interpretation: what does this dimension separate?
        neg_labels = [a[0].split("_", 1)[-1] for a in neg_end if abs(a[1]) > 0.01]
        pos_labels = [a[0].split("_", 1)[-1] for a in pos_end if abs(a[1]) > 0.01]

        interpretation = ""
        if neg_labels and pos_labels:
            interpretation = f"{'/'.join(neg_labels[:2])} ←→ {'/'.join(pos_labels[:2])}"

        dimensions.append({
            "index": dim_idx,
            "eigenvalue": float(S[dim_idx]),
            "variance_explained": float(explained[dim_idx]),
            "cumulative_variance": float(cumvar[dim_idx]),
            "axis_loadings": axis_loadings,
            "top_positive": [(a, float(v)) for a, v in pos_end],
            "top_negative": [(a, float(v)) for a, v in neg_end],
            "interpretation": interpretation,
        })

    return {
        "n_dimensions": n_dims,
        "n_probes": n,
        "eigenvalues": S[:n_dims].tolist(),
        "explained_variance": explained[:n_dims].tolist(),
        "cumulative_variance": cumvar[:n_dims].tolist(),
        "dimensions": dimensions,
        "noise_floor": float(min_eigenvalue_frac),
    }


def build_relational_target(
    universal_rdm: np.ndarray,
    dimensions: dict,
    residual: bool = True,
) -> dict:
    """Build the relational loss target from discovered dimensions.

    Returns a structure that relational_distill.py can load directly
    as its loss target.

    If residual=True: mean-subtracts (removes PC1 "all probes alike"),
    focuses on discriminative structure.
    """
    rdm = universal_rdm.copy()

    if residual:
        rdm = rdm - rdm.mean()
        np.fill_diagonal(rdm, 0.0)

    # Eigenvalue-weighted target: emphasize strong dimensions
    # (The RDM already does this implicitly via its structure,
    #  but we can provide explicit weights for the loss)
    dim_weights = {}
    for dim in dimensions["dimensions"]:
        dim_weights[dim["index"]] = dim["variance_explained"]

    return {
        "rdm": rdm.tolist(),
        "n_probes": int(rdm.shape[0]),
        "n_dimensions": dimensions["n_dimensions"],
        "residual": residual,
        "dim_weights": dim_weights,
    }


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="Crystal seed probe — map universal hologram")
    parser.add_argument("--models", default="qwen3-14b,olmo-2-13b")
    parser.add_argument("--layers", default="0,10,20,30",
                        help="Layers to probe (comma-separated)")
    parser.add_argument("--device", default="mps")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--min-eigenvalue", type=float, default=0.005,
                        help="Minimum variance fraction to count as significant dimension")
    parser.add_argument("--quick", action="store_true",
                        help="Use fewer layers (0,20)")
    parser.add_argument("--probe-set", default="crystal",
                        choices=["crystal", "lambda", "both"],
                        help="Which probe set to use: crystal (311 original), "
                             "lambda (380 combinator-focused), both (691 combined)")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model_keys = args.models.split(",")
    target_layers = [int(x) for x in args.layers.split(",")]
    if args.quick:
        target_layers = [0, 20]

    # Select probe set
    if args.probe_set == "lambda":
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
        from probes.lambda_kernel_probes import LAMBDA_PROBES
        probe_dict = LAMBDA_PROBES
        output_prefix = "lambda_kernel"
    elif args.probe_set == "both":
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
        from probes.lambda_kernel_probes import LAMBDA_PROBES
        probe_dict = {**PROBES, **LAMBDA_PROBES}
        output_prefix = "combined_crystal_lambda"
    else:
        probe_dict = PROBES
        output_prefix = "crystal_seed"

    probes = flatten_probes(probe_dict)

    print(f"\n{'═'*70}", file=sys.stderr)
    print(f"  CRYSTAL SEED PROBE — Map the Universal Hologram Scaffold", file=sys.stderr)
    print(f"{'═'*70}", file=sys.stderr)
    print(f"  Models:     {model_keys}", file=sys.stderr)
    print(f"  Layers:     {target_layers}", file=sys.stderr)
    print(f"  Probe set:  {args.probe_set} ({output_prefix})", file=sys.stderr)
    print(f"  Probes:     {len(probes)} across {len(probe_dict)} axes", file=sys.stderr)
    print(f"  Axes:       {list(probe_dict.keys())}", file=sys.stderr)
    print(f"  Min eigen:  {args.min_eigenvalue}", file=sys.stderr)
    print(f"{'═'*70}\n", file=sys.stderr)

    # ══ Phase 1: Extract hidden states from each model ═══════════
    print("Phase 1: Extracting hidden states...\n", file=sys.stderr)

    all_hidden = {li: [] for li in target_layers}

    for mk in model_keys:
        print(f"  ─── {mk} ───", file=sys.stderr)
        t0 = time.time()
        hs = extract_hidden_states(mk, target_layers, probes, args.device)
        for li in target_layers:
            all_hidden[li].append(hs[li])
        print(f"  Done in {time.time()-t0:.1f}s\n", file=sys.stderr)

    # ══ Phase 2: Build universal RDMs ════════════════════════════
    print("Phase 2: Building universal RDMs...\n", file=sys.stderr)

    universal_rdms = {}
    for li in target_layers:
        # Build per-model RDMs and average
        rdms = []
        for hs_model in all_hidden[li]:
            norms = np.linalg.norm(hs_model, axis=1, keepdims=True)
            norms = np.maximum(norms, 1e-8)
            hs_norm = hs_model / norms
            rdm = hs_norm @ hs_norm.T
            rdms.append(rdm)

        # Universal = average
        universal_rdms[li] = np.mean(rdms, axis=0)

        # RSA between models
        flat_a = rdms[0][np.triu_indices(len(probes), k=1)]
        flat_b = rdms[1][np.triu_indices(len(probes), k=1)]
        rsa = np.corrcoef(flat_a, flat_b)[0, 1]
        print(f"  L{li}: RSA between models = {rsa:.4f}", file=sys.stderr)

    # ══ Phase 3: Discover dimensions ═════════════════════════════
    print(f"\nPhase 3: Discovering universal dimensions...\n", file=sys.stderr)

    per_layer_dimensions = {}
    for li in target_layers:
        dims = discover_dimensions(universal_rdms[li], probes, args.min_eigenvalue)
        per_layer_dimensions[li] = dims

        print(f"  L{li}: {dims['n_dimensions']} significant dimensions "
              f"(cumulative var = {dims['cumulative_variance'][-1]:.4f})", file=sys.stderr)
        print(f"  Top dimensions:", file=sys.stderr)
        for d in dims["dimensions"][:8]:
            print(f"    PC{d['index']+1}: var={d['variance_explained']:.4f} "
                  f"| {d['interpretation']}", file=sys.stderr)
        print(file=sys.stderr)

    # ══ Phase 4: Build relational targets ════════════════════════
    print("Phase 4: Building relational loss targets...\n", file=sys.stderr)

    targets = {}
    for li in target_layers:
        target = build_relational_target(
            universal_rdms[li], per_layer_dimensions[li], residual=True
        )
        targets[li] = target
        print(f"  L{li}: {target['n_dimensions']} dims, residual=True", file=sys.stderr)

    # ══ Phase 5: Summary ═════════════════════════════════════════
    print(f"\n{'═'*70}", file=sys.stderr)
    print(f"  CRYSTAL SEED — Universal Hologram Scaffold", file=sys.stderr)
    print(f"{'���'*70}", file=sys.stderr)

    # Aggregate statistics
    total_dims = sum(d["n_dimensions"] for d in per_layer_dimensions.values())
    print(f"\n  Total verified dimensions: {total_dims} (across {len(target_layers)} layers)",
          file=sys.stderr)
    print(f"  Probes used: {len(probes)} across {len(probe_dict)} axes", file=sys.stderr)

    # Per-axis clustering (which axes produce signal?)
    print(f"\n  Axis clustering in universal RDM (L{target_layers[0]}):", file=sys.stderr)
    rdm0 = universal_rdms[target_layers[0]]
    axes_list = [p["axis"] for p in probes]
    unique_axes = sorted(set(axes_list))

    print(f"  {'Axis':<25} {'Within':>8} {'Between':>9} {'Ratio':>7}", file=sys.stderr)
    print(f"  {'─'*25} {'─'*8} {'─'*9} {'─'*7}", file=sys.stderr)

    axis_signals = []
    for ax in unique_axes:
        ax_idx = [i for i, a in enumerate(axes_list) if a == ax]
        other_idx = [i for i, a in enumerate(axes_list) if a != ax]
        if len(ax_idx) < 2:
            continue
        within = [rdm0[i, j] for i in ax_idx for j in ax_idx if i != j]
        between = [rdm0[i, j] for i in ax_idx for j in other_idx]
        mean_w = np.mean(within)
        mean_b = np.mean(between)
        ratio = mean_w / mean_b if mean_b > 0 else 0
        axis_signals.append((ax, ratio, mean_w, mean_b))

    axis_signals.sort(key=lambda x: -x[1])
    for ax, ratio, mean_w, mean_b in axis_signals:
        signal = '✅' if ratio > 1.3 else ('⚠️' if ratio > 1.1 else '  ')
        print(f"  {ax:<25} {mean_w:>8.4f} {mean_b:>9.4f} {ratio:>6.2f}× {signal}", file=sys.stderr)

    # ══ Save results ═════════════════════════════════════════════
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "config": {
            "models": model_keys,
            "target_layers": target_layers,
            "n_probes": len(probes),
            "probe_set": args.probe_set,
            "n_axes": len(probe_dict),
            "axes": list(probe_dict.keys()),
            "min_eigenvalue": args.min_eigenvalue,
        },
        "per_layer_dimensions": {
            str(li): dims for li, dims in per_layer_dimensions.items()
        },
        "relational_targets": {
            str(li): target for li, target in targets.items()
        },
        "axis_clustering": [
            {"axis": ax, "ratio": ratio, "within": w, "between": b}
            for ax, ratio, w, b in axis_signals
        ],
    }

    def numpy_serializer(obj):
        """Convert numpy types to Python native for JSON serialization."""
        if isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    json_path = args.output_dir / f"{output_prefix}_results.json"
    json_path.write_text(json.dumps(output, indent=2, default=numpy_serializer))
    print(f"\n  💾 Results: {json_path}", file=sys.stderr)

    # Also save just the targets for relational_distill.py to load
    target_path = args.output_dir / f"{output_prefix}_verified_dimensions.json"
    target_output = {
        "n_probes": len(probes),
        "probes": [{"prompt": p["prompt"], "axis": p["axis"]} for p in probes],
        "targets": {str(li): targets[li] for li in target_layers},
        "total_dimensions": total_dims,
    }
    target_path.write_text(json.dumps(target_output, indent=2, default=numpy_serializer))
    print(f"  💾 Verified dimensions: {target_path}", file=sys.stderr)
    print(f"     (Load this in relational_distill.py for full constraint set)", file=sys.stderr)
    print(f"{'═'*70}\n", file=sys.stderr)


if __name__ == "__main__":
    main()
