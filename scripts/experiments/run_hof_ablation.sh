#!/usr/bin/env bash
# session 226 — CAUSAL leg: ablate the Phase-A gather heads, measure necessity.
# Knock out the gather heads (full head knockout via o_proj input zeroing) and ask
# if HOF computation degrades > control > random-head baseline, on list stims (KL)
# and held-out prose (dNLL). Completes the observational Phase A/B with a causal test.
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 1

DEVICE="${DEVICE:-mps}"
DTYPE="${DTYPE:-bfloat16}"
TOPN="${TOPN:-8}"
NRAND="${NRAND:-3}"

MODELS=(
  "Qwen/Qwen3-8B"
  "Qwen/Qwen3-14B"
  "Qwen/Qwen3-32B"
  "mistralai/Mistral-7B-v0.3"
  "allenai/OLMo-2-1124-13B"
)

echo "=== HOF ABLATION : ${#MODELS[@]} models @ $(date -u +%FT%TZ) ==="
for m in "${MODELS[@]}"; do
  echo ""; echo ">>> ABLATE $m"
  uv run python scripts/experiments/hof_attention_ablation.py \
    --mode model --model "$m" --device "$DEVICE" --dtype "$DTYPE" \
    --top-n "$TOPN" --n-random "$NRAND" || echo "!!! FAILED $m"
done
echo ""; echo ">>> AGGREGATE"
uv run python scripts/experiments/hof_attention_ablation.py \
  --mode aggregate --models "${MODELS[@]}"
echo ""
echo "=== DONE @ $(date -u +%FT%TZ) ==="
