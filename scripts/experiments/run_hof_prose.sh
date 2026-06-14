#!/usr/bin/env bash
# session 225 — HOF prose engagement: does the model USE higher-order functions
# on natural prose? Transfer test (train direction on curated probes, test on
# held-out minimal-pair prose) across the same ≥8B / 3-architecture set.
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 1

DEVICE="${DEVICE:-mps}"
DTYPE="${DTYPE:-bfloat16}"

MODELS=(
  "Qwen/Qwen3-8B"
  "Qwen/Qwen3-14B"
  "Qwen/Qwen3-32B"
  "mistralai/Mistral-7B-v0.3"
  "allenai/OLMo-2-1124-13B"
)

echo "=== HOF prose engagement : ${#MODELS[@]} models @ $(date -u +%FT%TZ) ==="
for m in "${MODELS[@]}"; do
  echo ""
  echo ">>> MODEL $m"
  uv run python scripts/experiments/hof_prose_engagement.py \
    --mode model --model "$m" --device "$DEVICE" --dtype "$DTYPE" \
    || echo "!!! FAILED $m (continuing)"
done

echo ""
echo ">>> AGGREGATE"
uv run python scripts/experiments/hof_prose_engagement.py \
  --mode aggregate --models "${MODELS[@]}"

echo ""
echo "=== DONE @ $(date -u +%FT%TZ) ==="
