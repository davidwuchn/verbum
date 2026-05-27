# Session 162 — VSM ↔ Statechart ↔ Tensor + mmap Training

Explored two ideas that turned out to be the same: (1) Can VSMs be statecharts? (2) Can we use mmap'd files as delta plates? Built dual-runtime proof (Fulcro Clojure + Python tensor engine) and MmapPlateStore for checkpoint-free training. Proved safetensors export is zero-cost (prepend 1KB header).

Key insight: files ARE states, composition IS transition, mmap IS the runtime.

See `knowledge/explore/vsm-statechart-tensor.md` and `knowledge/explore/mmap-continuous-training.md`.
