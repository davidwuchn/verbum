💡 Session context as a 2MB holographic delta file, not a 1TB KV cache.

Session 127. The KV cache stores the full state of every token at
every layer — but most of that is already in the base crystal.
The session delta stores only what CHANGED from the base. The
conversation is the thin layer of deltas on top of the model's
existing knowledge. Sparse, compressible, tiny.

2MB file = 2M token session. Portable (save/load/share/branch/
version). Persistent (survives shutdown). Git-trackable.

Crystal is read-only at inference. No writes during operation.
Delta accumulates as a file. Learning happens offline: curate
deltas → etch into base crystal between sessions. Clean separation:
inference = read, learning = offline write.
