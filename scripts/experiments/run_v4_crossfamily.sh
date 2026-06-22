#!/usr/bin/env bash
# Cross-family CAUSAL ablation (v4) sweep — type-directed composition.
# Runs type_directed_v4_ablation across independent (non-Qwen) lineages.
# Architecture-agnostic layer access (decoder_layers) → GPTNeoX/Pythia + Llama-likes.
set -u
cd "$(dirname "$0")/../.."
MODELS=(
  EleutherAI/pythia-1.4b-deduped
  HuggingFaceTB/SmolLM3-3B
  mistralai/Mistral-7B-v0.3
  allenai/OLMo-2-1124-13B
)
for m in "${MODELS[@]}"; do
  echo "===MODEL $m ==="
  uv run python scripts/experiments/type_directed_v4_ablation.py \
    --model "$m" --n-each 4 --n-teach 2 2>&1
done | tee results/type-directed/crossfamily_v4_ablation.log
echo "=== v4 cross-family sweep DONE ==="
