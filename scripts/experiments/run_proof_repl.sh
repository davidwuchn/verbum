#!/usr/bin/env bash
# session 228 — continuation-driven prover. Does STEPWISE proving (one inference rule
# per turn, the goal stack = the reified continuation) rescue the composition failures
# the single-shot prover hit? Soundness is structural (non-theorems have no closing
# derivation). See knowledge/explore/proofs-as-continuations.md + proof_search.py.
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

echo "=== CONTINUATION-DRIVEN PROVER : ${#MODELS[@]} models @ $(date -u +%FT%TZ) ==="

echo ""; echo ">>> PHASE 1 — ENGINE FLOOR (auto solver + reconstruction)"
uv run python scripts/experiments/proof_repl.py --mode engine \
  || { echo "!!! ENGINE FLOOR FAILED — aborting"; exit 1; }

for m in "${MODELS[@]}"; do
  echo ""; echo ">>> PROVE (REPL) $m"
  uv run python scripts/experiments/proof_repl.py \
    --mode model --model "$m" --device "$DEVICE" --dtype "$DTYPE" \
    || echo "!!! FAILED $m"
done

echo ""; echo ">>> AGGREGATE (vs single-shot baseline)"
uv run python scripts/experiments/proof_repl.py --mode aggregate

echo ""
echo "=== DONE @ $(date -u +%FT%TZ) ==="
echo "ALLDONE"
