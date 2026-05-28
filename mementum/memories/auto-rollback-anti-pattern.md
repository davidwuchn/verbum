❌ Auto-rollback is an anti-pattern: stop-and-report instead

Auto-rollback on NaN failed because training state is not just model weights.
A consistent checkpoint requires ALL of: model weights, Adam moments, data
loader position, TD direction/magnitude EMAs, FlipMap state, crystal EMA,
and safetensors files.

The old rollback loaded model.npz and called it done. Adam moments from 360
steps later pointed into a different parameter space → first step after
rollback diverges → NaN → rollback → same NaN. Sisyphus.

**Correct pattern:** On 3 consecutive NaN, STOP training with a diagnostic
report (which loss component is NaN, gnorm value, available checkpoints,
suggested recovery commands). Let the human decide: resume from earlier
checkpoint, lower learning rate, inspect the model, etc.

**Dual storage lesson:** npz checkpoints are frozen windows into the full
state. Safetensors are the live working copy. When they diverge during a
failure, `restore_safetensors.py` rebuilds safetensors from any npz
checkpoint. The tool exists so surgery is never needed again.

Recovery = human decision + mechanical restoration tool. Not automation.
