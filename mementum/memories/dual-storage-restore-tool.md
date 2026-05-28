🔄 Dual storage (npz + safetensors) needs a restore path

npz checkpoints = frozen windows. Immutable once written. Complete: model +
optimizer + delta plates + state.json (data position, TD state, loop counters).

Safetensors = live working copy. Moving target. Synced every 20 steps, APFS
snapshots every 200 steps. Same format used for training AND release.

**Problem:** When a failure poisons the safetensors (e.g. NaN rollback storm
writes bad Adam state back to training.safetensors), there was no way to
rebuild them from a clean npz checkpoint. Manual surgery required.

**Solution:** `scripts/v14/restore_safetensors.py` — standalone tool that:
1. Creates model (same pipeline as train_td.py)
2. Loads model + optimizer from npz checkpoint
3. Syncs everything to safetensors via SafetensorsStore.sync()
4. Copies state.json (data position, TD state, etc.)

Usage: `uv run python scripts/v14/restore_safetensors.py --checkpoint
checkpoints/v14-mmap/step_004000 --safetensors-dir checkpoints/v14-mmap`

Then resume normally with `--safetensors-dir`. No manual file copying, no
state.json hand-editing, no "which files are from which step" detective work.
The npz checkpoint is the source of truth. Safetensors are derived.
