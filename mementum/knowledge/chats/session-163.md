# Session 163 — Safetensors-Backed Continuous Training

Wired safetensors mmap into the real training loop. Extracted step 2500 checkpoint to 3 safetensors files (base/delta/training, 987 tensors verified). Built SafetensorsStore (load/sync/fold). Benchmarked sync: 4.5s total, 1.3% overhead at 20-step interval. Added APFS snapshot crash protection (12ms clone) and kept legacy npz checkpoints every 500 steps. Training launched in tmux, safetensors-backed, headed to step 20000.

Key insight: safetensors IS mmap. Same file for training AND release.

See `knowledge/explore/safetensors-training.md` and `knowledge/explore/mmap-continuous-training.md`.
