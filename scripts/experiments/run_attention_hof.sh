#!/usr/bin/env bash
# session 225 — HOF topology + engagement in the ATTENTION register.
# s221: "attention-over-positions IS the fold"; s225: map under-read in the FFN gate.
# Prediction: map strengthens in attn_q + a shared fold/iteration substrate appears.
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 1

DEVICE="${DEVICE:-mps}"
DTYPE="${DTYPE:-bfloat16}"
TARGET="${TARGET:-attn_q}"

MODELS=(
  "Qwen/Qwen3-8B"
  "Qwen/Qwen3-14B"
  "Qwen/Qwen3-32B"
  "mistralai/Mistral-7B-v0.3"
  "allenai/OLMo-2-1124-13B"
)

echo "=== ATTENTION HOF ($TARGET) : ${#MODELS[@]} models @ $(date -u +%FT%TZ) ==="

echo ""
echo "### PART 1 — topology consensus ($TARGET) ###"
for m in "${MODELS[@]}"; do
  echo ""; echo ">>> TOPOLOGY $m"
  uv run python scripts/experiments/function_topology_consensus.py \
    --mode model --target "$TARGET" --model "$m" --device "$DEVICE" --dtype "$DTYPE" \
    --n-perm 300 || echo "!!! FAILED $m"
done
echo ""; echo ">>> CONSENSUS ($TARGET)"
uv run python scripts/experiments/function_topology_consensus.py \
  --mode consensus --target "$TARGET" --n-perm 5000 --models "${MODELS[@]}"
echo ""; echo ">>> FUNCTION-PAIR SIMILARITY ($TARGET)"
uv run python scripts/experiments/function_pair_similarity.py --target "$TARGET"

echo ""
echo "### PART 2 — prose engagement ($TARGET) ###"
for m in "${MODELS[@]}"; do
  echo ""; echo ">>> PROSE $m"
  uv run python scripts/experiments/hof_prose_engagement.py \
    --mode model --target "$TARGET" --model "$m" --device "$DEVICE" --dtype "$DTYPE" \
    || echo "!!! FAILED $m"
done
echo ""; echo ">>> AGGREGATE ($TARGET)"
uv run python scripts/experiments/hof_prose_engagement.py \
  --mode aggregate --target "$TARGET" --models "${MODELS[@]}"

echo ""
echo "=== DONE @ $(date -u +%FT%TZ) ==="
