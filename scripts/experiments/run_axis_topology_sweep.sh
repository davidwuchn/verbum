#!/usr/bin/env bash
# register: spectral/semantic — common axis + topology decomposition sweep
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 1
LOG="results/manifold-axis-topology/run.log"
mkdir -p results/manifold-axis-topology
PAIRS=(
  "EleutherAI/pythia-160m:float32"
  "EleutherAI/pythia-410m:float32"
  "Qwen/Qwen3-0.6B:bfloat16"
  "HuggingFaceTB/SmolLM3-3B:bfloat16"
  "Qwen/Qwen3-4B:bfloat16"
  "mistralai/Mistral-7B-v0.3:bfloat16"
  "allenai/OLMo-2-1124-13B:bfloat16"
  "Qwen/Qwen3-14B:bfloat16"
)
echo "=== axis+topology sweep start $(date -u +%FT%TZ) ===" | tee -a "$LOG"
for pair in "${PAIRS[@]}"; do
  model="${pair%%:*}"; dtype="${pair##*:}"
  echo "=== $model ($dtype) $(date -u +%FT%TZ) ===" | tee -a "$LOG"
  uv run python scripts/experiments/manifold_axis_topology.py \
      --model "$model" --device mps --dtype "$dtype" --n-perm 2000 2>&1 | tee -a "$LOG"
done
echo "=== axis+topology sweep done $(date -u +%FT%TZ) ===" | tee -a "$LOG"
