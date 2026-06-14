#!/usr/bin/env bash
# session 228 — proof-as-inhabitation (Curry-Howard). Can a model PROVE an
# implicational-logic proposition by emitting a closed combinator term whose type the
# constructed kernel certifies? proof-check = type-check; the continuation (beta-
# reduction -> WHNF) = cut-elimination. The sound basis excludes Y (recursion =
# inconsistency = the Y-trap). See knowledge/explore (Curry-Howard page) + proof_kernel.py.
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

echo "=== PROOF-AS-INHABITATION : ${#MODELS[@]} models @ $(date -u +%FT%TZ) ==="

echo ""; echo ">>> PHASE 1 — KERNEL FLOOR (proof checker + consistency firewall)"
uv run python scripts/experiments/proof_inhabitation.py --mode kernel \
  || { echo "!!! KERNEL FLOOR FAILED — aborting"; exit 1; }

for m in "${MODELS[@]}"; do
  echo ""; echo ">>> PROVE $m"
  uv run python scripts/experiments/proof_inhabitation.py \
    --mode model --model "$m" --device "$DEVICE" --dtype "$DTYPE" \
    || echo "!!! FAILED $m"
done

echo ""; echo ">>> AGGREGATE"
uv run python scripts/experiments/proof_inhabitation.py --mode aggregate

echo ""
echo "=== DONE @ $(date -u +%FT%TZ) ==="
echo "ALLDONE"
