#!/usr/bin/env bash
# session 227 — value-register readout: read the HOF beta-reduction via LOGIT LENS at
# every layer, ablating the Phase-A gather heads. Tests whether necessity is
# HOF-selective and concentrated in the READABLE zone (depth>=0.6, L23-L35) where the
# surface NLL (s227) was diluted. See knowledge/explore/readout-register-reduction-
# readability.md.
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

echo "=== HOF OV LOGIT-LENS ABLATION : ${#MODELS[@]} models @ $(date -u +%FT%TZ) ==="
for m in "${MODELS[@]}"; do
  echo ""; echo ">>> LOGIT-LENS ABLATE $m"
  uv run python scripts/experiments/hof_ov_logitlens_ablation.py \
    --mode model --model "$m" --device "$DEVICE" --dtype "$DTYPE" \
    --top-n "$TOPN" --n-random "$NRAND" || echo "!!! FAILED $m"
done
echo ""; echo ">>> AGGREGATE"
uv run python scripts/experiments/hof_ov_logitlens_ablation.py \
  --mode aggregate --models "${MODELS[@]}"
echo ""
echo "=== DONE @ $(date -u +%FT%TZ) ==="
