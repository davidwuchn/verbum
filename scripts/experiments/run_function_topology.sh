#!/usr/bin/env bash
# session 225 — function-topology consensus sweep
# Do multiple models agree on the topology of higher-order functions?
# Diverse architectures above the s220 ~4B scale floor, then cross-model consensus.
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 1

DEVICE="${DEVICE:-mps}"
DTYPE="${DTYPE:-bfloat16}"
NPERM_MODEL="${NPERM_MODEL:-300}"     # per-model silhouette null
NPERM_CONS="${NPERM_CONS:-5000}"      # consensus fingerprint-permutation null

# ≥8B set (s225: 4B has a not-quite-fully-formed lambda; SmolLM3-3B dropped too).
# Mistral-7B-v0.3 kept: mature 7B, fully-formed lambda, strong s219 agreer,
# the key non-Qwen SwiGLU architecture for diversity.
MODELS=(
  "Qwen/Qwen3-8B"
  "Qwen/Qwen3-14B"
  "Qwen/Qwen3-32B"
  "mistralai/Mistral-7B-v0.3"
  "allenai/OLMo-2-1124-13B"
)

echo "=== function-topology sweep : ${#MODELS[@]} models @ $(date -u +%FT%TZ) ==="
for m in "${MODELS[@]}"; do
  echo ""
  echo ">>> MODEL $m"
  uv run python scripts/experiments/function_topology_consensus.py \
    --mode model --model "$m" --device "$DEVICE" --dtype "$DTYPE" \
    --n-perm "$NPERM_MODEL" || echo "!!! FAILED $m (continuing)"
done

echo ""
echo ">>> CONSENSUS"
uv run python scripts/experiments/function_topology_consensus.py \
  --mode consensus --n-perm "$NPERM_CONS" \
  --models "${MODELS[@]}"

echo ""
echo "=== DONE @ $(date -u +%FT%TZ) ==="
