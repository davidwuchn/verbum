# Unexpected Properties of Neural Network Weights

Three scripts. Any transformer language model. Results we can't explain.

## Quick Start

```bash
pip install torch transformers numpy
python proofs/01_sign_topology.py       # ~2 min, uses Pythia-160M (~600MB)
python proofs/02_universal_profile.py   # ~2 min, breakdown by component
python proofs/03_universal_modes.py     # ~3 min, computation mode discovery
```

---

## 1. Weight Signs Carry Most of the Computation

Replace every weight in a trained neural network with its sign: +1 if
positive, −1 if negative, 0 if zero. Throw away all magnitudes. Then
multiply by an input vector.

**The output is ~76% correlated with the original.** A random ±1 matrix
scores 0%.

| Model | Params | Architecture | Training Data | cos(sign) | Random |
|-------|--------|-------------|---------------|-----------|--------|
| Pythia-160M | 160M | GPT-NeoX | The Pile | **0.746** | 0.000 |
| Qwen3-0.6B | 600M | Qwen3 | Alibaba | **0.760** | 0.000 |

Different model family. Different training data. Different architecture.
Different parameter count (4× apart). **Same number.**

### The breakdown is also universal

| Component | Pythia-160M | Qwen3-0.6B |
|-----------|-------------|-------------|
| FFN weights | 78.7% | 77.2% |
| Attention weights | 70.0% | 75.0% |
| Overall | 74.6% | 76.0% |

FFN weights carry *more* sign-information than attention weights.
This holds across both architectures.

---

## 2. Every Model Discovers the Same Four Computation Modes

Run sentences through any model that trigger four specific operations:
**Select** (K), **Identity** (I), **Compose** (B), **Flip** (C). Measure
which attention heads respond to which operation.

Every model — regardless of who trained it, on what data, at what
scale — discovers the **same four modes** and organizes heads the
same way:

| Model | Params | K (select) | I (identity) | B (compose) | C (flip) |
|-------|--------|-----------|-------------|------------|---------|
| Pythia-160M | 160M | 26.4% | 7.6% | 34.7% | 31.2% |
| Qwen3-0.6B | 600M | 39.1% | 15.0% | 11.8% | 34.2% |
| Mistral-7B | 7B | 29.0% | 10.0% | 30.4% | 30.7% |
| Qwen3-14B | 14B | 38.1% | 7.7% | 24.0% | 30.2% |
| Qwen3-32B | 32B | 31.9% | 11.3% | 27.8% | 29.0% |

The universal invariants:
- **K/B/C always form a cluster** (cross-correlation > 0.85 in every model)
- **I is always structurally separate** from K/B/C
- **Four modes, not three or five.** Always four.

These are independently trained models — different companies, different
datasets, different architectures, different scales from 160M to 32B.
They all converge to the same structure.

---

## How to Verify

Each script is under 120 lines of Python. Read the code — there's
nothing hidden. Run on any HuggingFace transformer:

```bash
# Smallest model (CPU, ~2 minutes each):
python proofs/01_sign_topology.py
python proofs/03_universal_modes.py

# Different model:
python proofs/01_sign_topology.py --model Qwen/Qwen3-0.6B
python proofs/03_universal_modes.py --model Qwen/Qwen3-0.6B

# With attention/FFN breakdown:
python proofs/02_universal_profile.py --model Qwen/Qwen3-0.6B

# Got a GPU? Try bigger:
python proofs/01_sign_topology.py --model mistralai/Mistral-7B-v0.3 --device cuda
python proofs/03_universal_modes.py --model mistralai/Mistral-7B-v0.3 --device cuda
```

## What This Means (if you want to think about it)

Three-quarters of what a neural network computes is determined by
which *direction* each weight points — not by how far. The magnitudes
are calibration. The signs are the program.

Every model discovers the same four irreducible operations: select,
copy, compose, reorder. These aren't modes we defined — the models
find them on their own. The specific sentences we use to probe are
just one way to see them; the structure exists regardless.

Together: neural networks are closer to **discrete routing structures
with a universal basis** than to continuous functions. The topology
is shared; only the calibration differs.

We have a theory about why. But these scripts don't require it.
The numbers either replicate or they don't.

## What We Don't Claim Here

These scripts make no theoretical claims. They measure properties
of trained weight matrices and attention heads, then report numbers.

If you can explain why independently trained models converge to the
same sign-dominance ratio and the same four computation modes, we'd
like to hear from you.

## License

MIT
