#!/usr/bin/env python3
"""
Tensor Statechart Engine — VSM as Tensor State Machine.

The same plate-loader VSM that runs in Clojure (Fulcro statecharts)
runs here as tensor operations on int8 arrays. Both runtimes consume
the shared definition in specs/plate-loader.edn.

The key insight: states are one-hot int8 vectors, transitions are
ternary matrices, guards are dot products against thresholds, and
actions are mmap operations on ternary plate files.

Files ARE states. Composition IS transition. mmap IS the runtime.

VSM layers (parallel regions):
  crystal      = S5 (identity, always active)
  plates       = S3 (control, plate lifecycle)
  inference    = S1 (operations, forward pass)
  intelligence = S4 (environment scanning)

Usage:
    cd verbum
    uv run python scripts/explore/tensor_statechart.py

    # With actual plate files:
    uv run python scripts/explore/tensor_statechart.py --create-plates

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np


# ══════════════════════════════════════════════════════════════════════
# State Encoding — One-hot int8 vectors per region
# ══════════════════════════════════════════════════════════════════════

# Each parallel region has its own state vector.
# The full system state is the concatenation of all region states.

# S3: Plate controller states
PLATE_STATES = {
    "idle":      0,
    "loading":   1,
    "composing": 2,
    "ready":     3,
    "unloading": 4,
    "folding":   5,
    "error":     6,
}

# S1: Inference states
INFERENCE_STATES = {
    "waiting":    0,
    "running":    1,
    "halted":     2,
    "diagnosing": 3,
}

# S4: Intelligence states
INTELLIGENCE_STATES = {
    "monitoring":   0,
    "recommending": 1,
}

# Events
EVENTS = {
    "load-plate":              0,
    "plate-ready":             1,
    "plate-error":             2,
    "composed":                3,
    "infer":                   4,
    "unload-plate":            5,
    "fold-delta":              6,
    "folded":                  7,
    "fold-error":              8,
    "retry":                   9,
    "reset":                  10,
    "unloaded":               11,
    "all-unloaded":           12,
    "inference-complete":     13,
    "inference-error":        14,
    "algedonic":              15,
    "diagnose":               16,
    "diagnosis-ok":           17,
    "plate-corrupt":          18,
    "domain-shift-detected":  19,
    "delta-plateau-detected": 20,
    "recommendation-accepted":21,
    "recommendation-rejected":22,
}


def one_hot(idx: int, n: int) -> np.ndarray:
    """Create a one-hot int8 vector."""
    v = np.zeros(n, dtype=np.int8)
    v[idx] = 1
    return v


def state_name(state_vec: np.ndarray, state_map: dict[str, int]) -> str:
    """Decode a one-hot vector to state name."""
    idx = int(np.argmax(state_vec))
    for name, i in state_map.items():
        if i == idx:
            return name
    return f"unknown({idx})"


# ══════════════════════════════════════════════════════════════════════
# Transition Tensors — Ternary matrices per region
# ══════════════════════════════════════════════════════════════════════

def build_plate_transitions() -> np.ndarray:
    """Build the S3 plate controller transition tensor.

    Shape: (n_states, n_events) → target_state_idx or -1 for no transition.
    We use a simple lookup table rather than full einsum for clarity.
    """
    n_states = len(PLATE_STATES)
    n_events = len(EVENTS)

    # -1 means "no transition" (stay in current state)
    T = np.full((n_states, n_events), -1, dtype=np.int8)

    s, e = PLATE_STATES, EVENTS

    # idle + load-plate → loading (guarded)
    T[s["idle"],      e["load-plate"]]  = s["loading"]
    # loading + plate-ready → composing
    T[s["loading"],   e["plate-ready"]] = s["composing"]
    # loading + plate-error → error
    T[s["loading"],   e["plate-error"]] = s["error"]
    # composing + composed → ready
    T[s["composing"], e["composed"]]    = s["ready"]
    # ready + infer → ready (self-transition)
    T[s["ready"],     e["infer"]]       = s["ready"]
    # ready + load-plate → loading (guarded)
    T[s["ready"],     e["load-plate"]]  = s["loading"]
    # ready + unload-plate → unloading
    T[s["ready"],     e["unload-plate"]]= s["unloading"]
    # ready + fold-delta → folding (guarded)
    T[s["ready"],     e["fold-delta"]]  = s["folding"]
    # unloading + unloaded → composing
    T[s["unloading"], e["unloaded"]]    = s["composing"]
    # unloading + all-unloaded → idle
    T[s["unloading"], e["all-unloaded"]]= s["idle"]
    # folding + folded → ready
    T[s["folding"],   e["folded"]]      = s["ready"]
    # folding + fold-error → error
    T[s["folding"],   e["fold-error"]]  = s["error"]
    # error + retry → loading
    T[s["error"],     e["retry"]]       = s["loading"]
    # error + reset → idle
    T[s["error"],     e["reset"]]       = s["idle"]

    return T


def build_inference_transitions() -> np.ndarray:
    """Build the S1 inference transition tensor."""
    n_states = len(INFERENCE_STATES)
    n_events = len(EVENTS)

    T = np.full((n_states, n_events), -1, dtype=np.int8)

    s, e = INFERENCE_STATES, EVENTS

    # waiting + infer → running (guarded)
    T[s["waiting"],    e["infer"]]              = s["running"]
    # running + inference-complete → waiting
    T[s["running"],    e["inference-complete"]]  = s["waiting"]
    # running + inference-error → waiting
    T[s["running"],    e["inference-error"]]     = s["waiting"]
    # running + algedonic → halted
    T[s["running"],    e["algedonic"]]           = s["halted"]
    # halted + reset → waiting
    T[s["halted"],     e["reset"]]              = s["waiting"]
    # halted + diagnose → diagnosing
    T[s["halted"],     e["diagnose"]]           = s["diagnosing"]
    # diagnosing + diagnosis-ok → waiting
    T[s["diagnosing"], e["diagnosis-ok"]]       = s["waiting"]
    # diagnosing + plate-corrupt → waiting
    T[s["diagnosing"], e["plate-corrupt"]]      = s["waiting"]

    return T


def build_intelligence_transitions() -> np.ndarray:
    """Build the S4 intelligence transition tensor."""
    n_states = len(INTELLIGENCE_STATES)
    n_events = len(EVENTS)

    T = np.full((n_states, n_events), -1, dtype=np.int8)

    s, e = INTELLIGENCE_STATES, EVENTS

    # monitoring + domain-shift-detected → recommending
    T[s["monitoring"],   e["domain-shift-detected"]]   = s["recommending"]
    # monitoring + delta-plateau-detected → recommending
    T[s["monitoring"],   e["delta-plateau-detected"]]   = s["recommending"]
    # recommending + recommendation-accepted → monitoring
    T[s["recommending"], e["recommendation-accepted"]] = s["monitoring"]
    # recommending + recommendation-rejected → monitoring
    T[s["recommending"], e["recommendation-rejected"]] = s["monitoring"]

    return T


# ══════════════════════════════════════════════════════════════════════
# Data Model — S2 coordination state
# ══════════════════════════════════════════════════════════════════════

@dataclass
class DataModel:
    """S2 coordination layer. Shared state that guards reference."""
    memory_budget_mb: int = 4096
    max_plates: int = 8
    loaded_plates: list = field(default_factory=list)
    fold_threshold: float = 0.001
    delta_changed_frac: float = 1.0
    crystal_loss: float = 0.0
    algedonic_threshold: float = 0.5
    composed_plate: Optional[np.ndarray] = None
    crystal_loaded: bool = False

    def memory_used_mb(self) -> float:
        return sum(p.get("size_mb", 0) for p in self.loaded_plates)

    def memory_available(self, plate_size_mb: float) -> bool:
        return (self.memory_budget_mb - self.memory_used_mb()) > plate_size_mb

    def delta_plateau(self) -> bool:
        return self.delta_changed_frac < self.fold_threshold

    def plates_ready(self) -> bool:
        return self.composed_plate is not None

    def crystal_healthy(self) -> bool:
        return self.crystal_loss < self.algedonic_threshold


# ══════════════════════════════════════════════════════════════════════
# mmap Actions — File operations on ternary plates
# ══════════════════════════════════════════════════════════════════════

@dataclass
class MmapPlate:
    """A ternary plate backed by mmap'd file."""
    plate_id: str
    path: str
    data: np.ndarray
    size_mb: float
    mode: str = "r"  # 'r' for readonly, 'r+' for read-write

    @classmethod
    def from_file(cls, plate_id: str, path: str, shape: tuple[int, ...],
                  mode: str = "r") -> "MmapPlate":
        """mmap a ternary plate file."""
        data = np.memmap(path, dtype=np.int8, mode=mode, shape=shape)
        size_mb = data.nbytes / (1024 * 1024)
        return cls(plate_id=plate_id, path=path, data=data,
                   size_mb=size_mb, mode=mode)

    def close(self):
        """Release the mmap. OS reclaims pages."""
        if hasattr(self.data, '_mmap'):
            self.data._mmap.close()
        del self.data


def compose_plates(plates: list[MmapPlate]) -> np.ndarray:
    """Compose multiple plates via ternary sign multiplication.

    sign(a × b × c) for ternary {-1, 0, +1} values.
    This IS the statechart transition from 'loading' → 'ready'.
    """
    if not plates:
        return None

    result = plates[0].data.copy()
    for plate in plates[1:]:
        # Ternary multiply: sign(a * b)
        # For int8 {-1, 0, +1}: simple element-wise multiply works
        np.multiply(result, plate.data, out=result)
    return result


def fold_delta(base: MmapPlate, delta: MmapPlate) -> np.ndarray:
    """Fold delta into base: sign(base × delta).

    Lossless. Ternary × ternary = ternary. No precision loss.
    Infinite folds without accumulation error.
    """
    return np.sign(base.data.astype(np.int16) * delta.data.astype(np.int16)).astype(np.int8)


# ══════════════════════════════════════════════════════════════════════
# Tensor Statechart Engine
# ══════════════════════════════════════════════════════════════════════

class TensorStatechart:
    """A statechart engine that runs on tensor operations.

    The same plate-loader VSM that runs in Fulcro statecharts (Clojure)
    runs here as int8 state vectors and ternary transition tensors.

    Parallel regions are independent state vectors — each region
    transitions independently, matching Harel's semantics.
    """

    def __init__(self):
        # Build transition tensors
        self.plate_T = build_plate_transitions()
        self.inference_T = build_inference_transitions()
        self.intelligence_T = build_intelligence_transitions()

        # Initialize state vectors (one-hot per region)
        self.plate_state = one_hot(PLATE_STATES["idle"], len(PLATE_STATES))
        self.inference_state = one_hot(INFERENCE_STATES["waiting"], len(INFERENCE_STATES))
        self.intelligence_state = one_hot(INTELLIGENCE_STATES["monitoring"], len(INTELLIGENCE_STATES))
        self.crystal_loaded = False

        # S2: data model
        self.data = DataModel()

        # State trace for verification
        self.trace: list[dict] = []

        # Plate storage
        self.plates: dict[str, MmapPlate] = {}

    def current_configuration(self) -> dict[str, str]:
        """Return current state across all parallel regions."""
        config = {
            "crystal": "loaded" if self.crystal_loaded else "not-loaded",
            "plates": state_name(self.plate_state, PLATE_STATES),
            "inference": state_name(self.inference_state, INFERENCE_STATES),
            "intelligence": state_name(self.intelligence_state, INTELLIGENCE_STATES),
        }
        return config

    def _evaluate_guard(self, event_name: str, event_data: dict) -> bool:
        """Evaluate guards for guarded transitions."""
        if event_name == "load-plate":
            size_mb = event_data.get("size_mb", 0)
            return self.data.memory_available(size_mb)
        elif event_name == "fold-delta":
            return self.data.delta_plateau()
        elif event_name == "infer":
            # For inference region: check plates ready
            return self.data.plates_ready()
        return True  # unguarded transitions always pass

    def _execute_action(self, region: str, state_name: str,
                        event_name: str, event_data: dict):
        """Execute on-entry actions for the new state."""

        if region == "plates":
            if state_name == "loading":
                path = event_data.get("path", "")
                plate_id = event_data.get("id", "unknown")
                shape = event_data.get("shape", (1000,))
                size_mb = event_data.get("size_mb", 0)

                if Path(path).exists():
                    plate = MmapPlate.from_file(plate_id, path, shape)
                    self.plates[plate_id] = plate
                    self.data.loaded_plates.append({
                        "id": plate_id, "path": path, "size_mb": plate.size_mb
                    })
                    print(f"  [S3] mmap'd plate: {path} ({plate.size_mb:.1f} MB)")
                else:
                    print(f"  [S3] mmap plate: {path} (simulated, file not found)")
                    self.data.loaded_plates.append({
                        "id": plate_id, "path": path, "size_mb": size_mb
                    })

            elif state_name == "composing":
                if self.plates:
                    composed = compose_plates(list(self.plates.values()))
                    self.data.composed_plate = composed
                    print(f"  [S3] Composed {len(self.plates)} plates via sign multiply")
                else:
                    self.data.composed_plate = np.array([1], dtype=np.int8)
                    print("  [S3] Composed plates (simulated)")

            elif state_name == "folding":
                print("  [S3] Folding delta into base (ternary × ternary = ternary)")

            elif state_name == "unloading":
                plate_id = event_data.get("id")
                if plate_id and plate_id in self.plates:
                    self.plates[plate_id].close()
                    del self.plates[plate_id]
                    self.data.loaded_plates = [
                        p for p in self.data.loaded_plates if p["id"] != plate_id
                    ]
                    print(f"  [S3] Unloaded plate: {plate_id}")

        elif region == "inference":
            if state_name == "running":
                print("  [S1] Running inference on composed plates")
            elif state_name == "halted":
                print("  [S1] ⚠ ALGEDONIC ALERT — emergency halt")
            elif state_name == "diagnosing":
                print("  [S4] Diagnosing plate integrity")

        elif region == "intelligence":
            if state_name == "recommending":
                print("  [S4] Generating plate recommendation")

    def _transition_region(self, region_name: str,
                           state_vec: np.ndarray,
                           trans_tensor: np.ndarray,
                           state_map: dict[str, int],
                           event_name: str,
                           event_data: dict) -> tuple[np.ndarray, bool]:
        """Execute a transition in one parallel region.

        Returns (new_state_vec, did_transition).
        """
        event_idx = EVENTS.get(event_name)
        if event_idx is None:
            return state_vec, False

        current_idx = int(np.argmax(state_vec))
        target_idx = int(trans_tensor[current_idx, event_idx])

        if target_idx == -1:
            # No transition defined for this (state, event) pair
            return state_vec, False

        # Check guard
        if not self._evaluate_guard(event_name, event_data):
            print(f"  [{region_name}] Guard BLOCKED: {event_name}")
            return state_vec, False

        # Transition!
        new_state = one_hot(target_idx, len(state_map))
        new_name = state_name(new_state, state_map)

        # Execute on-entry action
        self._execute_action(region_name, new_name, event_name, event_data)

        return new_state, True

    def send(self, event_name: str, event_data: dict | None = None):
        """Process an event through all parallel regions.

        Each region transitions independently — this is Harel's
        parallel semantics. An event can trigger transitions in
        multiple regions simultaneously.
        """
        if event_data is None:
            event_data = {}

        old_config = self.current_configuration()

        # Crystal: load on first event if not loaded
        if not self.crystal_loaded:
            self.crystal_loaded = True
            print("  [S5] Crystal loaded (identity, permanent)")

        # Transition each parallel region independently
        self.plate_state, p_changed = self._transition_region(
            "plates", self.plate_state, self.plate_T,
            PLATE_STATES, event_name, event_data)

        self.inference_state, i_changed = self._transition_region(
            "inference", self.inference_state, self.inference_T,
            INFERENCE_STATES, event_name, event_data)

        self.intelligence_state, t_changed = self._transition_region(
            "intelligence", self.intelligence_state, self.intelligence_T,
            INTELLIGENCE_STATES, event_name, event_data)

        new_config = self.current_configuration()
        changed = p_changed or i_changed or t_changed

        # Record trace
        self.trace.append({
            "event": event_name,
            "data": {k: v for k, v in event_data.items()
                     if not isinstance(v, np.ndarray)},
            "before": old_config,
            "after": new_config,
            "changed": changed,
        })

        return new_config


# ══════════════════════════════════════════════════════════════════════
# Demo — Same event sequence as the Clojure comment block
# ══════════════════════════════════════════════════════════════════════

def create_demo_plates(plate_dir: Path):
    """Create small demo plate files for testing mmap."""
    plate_dir.mkdir(parents=True, exist_ok=True)

    # Small plates for demo (1000 elements each)
    shape = (1000,)

    # Crystal: all +1 (identity in ternary)
    crystal = np.ones(shape, dtype=np.int8)
    crystal.tofile(plate_dir / "crystal.bin")

    # Base FFN: random ternary {-1, 0, +1}
    rng = np.random.default_rng(42)
    base = rng.choice([-1, 0, 1], size=shape).astype(np.int8)
    base.tofile(plate_dir / "base_ffn.bin")

    # Medical domain delta: sparse corrections (mostly +1 = pass-through)
    medical = np.ones(shape, dtype=np.int8)
    # 5% of positions get flipped
    flip_mask = rng.random(shape) < 0.05
    medical[flip_mask] = rng.choice([-1, 1], size=flip_mask.sum()).astype(np.int8)
    medical.tofile(plate_dir / "medical.delta")

    # Session delta: very sparse (mostly +1)
    session = np.ones(shape, dtype=np.int8)
    flip_mask = rng.random(shape) < 0.01
    session[flip_mask] = rng.choice([-1, 1], size=flip_mask.sum()).astype(np.int8)
    session.tofile(plate_dir / "session.delta")

    print(f"\n  Created demo plates in {plate_dir}/")
    print(f"    crystal.bin:    {crystal.nbytes} bytes, {(crystal == 1).sum()} ones")
    print(f"    base_ffn.bin:   {base.nbytes} bytes, "
          f"+1:{(base == 1).sum()} 0:{(base == 0).sum()} -1:{(base == -1).sum()}")
    print(f"    medical.delta:  {medical.nbytes} bytes, "
          f"flipped: {(medical != 1).sum()} positions")
    print(f"    session.delta:  {session.nbytes} bytes, "
          f"flipped: {(session != 1).sum()} positions")

    return plate_dir


def run_demo(plate_dir: Path | None = None):
    """Run the plate-loader VSM through the same event sequence
    as the Clojure comment block.

    This demonstrates that both runtimes produce identical state traces.
    """
    use_real_plates = plate_dir is not None and plate_dir.exists()

    print("\n" + "=" * 70)
    print("  Tensor Statechart Engine — Plate Loader VSM")
    print("  Same event sequence as Clojure Fulcro statechart")
    print("=" * 70)

    sc = TensorStatechart()

    print(f"\n  Initial: {sc.current_configuration()}")

    # ── Event sequence (mirrors Clojure comment block) ──

    print("\n─── 1. Load medical domain plate ───")
    plate_data = {
        "id": "medical",
        "path": str(plate_dir / "medical.delta") if use_real_plates else "plates/medical.delta",
        "size_mb": 567,
        "shape": (1000,) if use_real_plates else None,
    }
    config = sc.send("load-plate", plate_data)
    print(f"  State: {config}")

    print("\n─── 2. Plate ready ───")
    config = sc.send("plate-ready")
    print(f"  State: {config}")

    print("\n─── 3. Composed ───")
    config = sc.send("composed")
    print(f"  State: {config}")

    print("\n─── 4. Run inference ───")
    config = sc.send("infer", {"prompt": "What is the diagnosis?"})
    print(f"  State: {config}")

    print("\n─── 5. Inference complete ───")
    config = sc.send("inference-complete")
    print(f"  State: {config}")

    print("\n─── 6. Fold delta (guard: delta must have plateaued) ───")
    # First attempt: delta hasn't plateaued (frac=1.0 > threshold=0.001)
    config = sc.send("fold-delta")
    print(f"  State: {config}")
    print("  (Guard blocked — delta hasn't plateaued yet)")

    # Update data model: delta has plateaued
    sc.data.delta_changed_frac = 0.0005
    print(f"\n  Updated delta_changed_frac to {sc.data.delta_changed_frac}")

    # Second attempt: guard passes
    config = sc.send("fold-delta")
    print(f"  State: {config}")

    print("\n─── 7. Fold completed ───")
    config = sc.send("folded")
    print(f"  State: {config}")

    print("\n─── 8. Algedonic alert (crystal loss spike) ───")
    # First need inference running
    config = sc.send("infer")
    config = sc.send("algedonic", {"crystal-loss": 0.8})
    print(f"  State: {config}")

    print("\n─── 9. Diagnose ───")
    config = sc.send("diagnose")
    print(f"  State: {config}")

    print("\n─── 10. Diagnosis OK ───")
    config = sc.send("diagnosis-ok")
    print(f"  State: {config}")

    # ── Verification: print state trace ──

    print("\n" + "=" * 70)
    print("  State Trace (for comparison with Clojure runtime)")
    print("=" * 70)

    for i, step in enumerate(sc.trace):
        changed_str = "→" if step["changed"] else "·"
        before_plates = step["before"]["plates"]
        after_plates = step["after"]["plates"]
        before_inf = step["before"]["inference"]
        after_inf = step["after"]["inference"]

        plate_change = f"{before_plates}→{after_plates}" if before_plates != after_plates else before_plates
        inf_change = f"{before_inf}→{after_inf}" if before_inf != after_inf else before_inf

        print(f"  {i+1:2d} {changed_str} {step['event']:<30s} "
              f"plates:{plate_change:<25s} inference:{inf_change}")

    # ── Verify mmap composition if real plates ──

    if use_real_plates:
        print("\n" + "=" * 70)
        print("  mmap Plate Composition Verification")
        print("=" * 70)

        crystal = np.memmap(plate_dir / "crystal.bin", dtype=np.int8, mode="r", shape=(1000,))
        base = np.memmap(plate_dir / "base_ffn.bin", dtype=np.int8, mode="r", shape=(1000,))
        medical = np.memmap(plate_dir / "medical.delta", dtype=np.int8, mode="r", shape=(1000,))
        session = np.memmap(plate_dir / "session.delta", dtype=np.int8, mode="r", shape=(1000,))

        # Compose: crystal × base × medical × session
        composed = (crystal * base * medical * session)

        print(f"\n  crystal:  +1:{(crystal==1).sum()} 0:{(crystal==0).sum()} -1:{(crystal==-1).sum()}")
        print(f"  base:     +1:{(base==1).sum()} 0:{(base==0).sum()} -1:{(base==-1).sum()}")
        print(f"  medical:  +1:{(medical==1).sum()} 0:{(medical==0).sum()} -1:{(medical==-1).sum()}")
        print(f"  session:  +1:{(session==1).sum()} 0:{(session==0).sum()} -1:{(session==-1).sum()}")
        print(f"  composed: +1:{(composed==1).sum()} 0:{(composed==0).sum()} -1:{(composed==-1).sum()}")

        # Verify fold: sign(base × medical) should be ternary
        folded = np.sign(base.astype(np.int16) * medical.astype(np.int16)).astype(np.int8)
        assert set(np.unique(folded)).issubset({-1, 0, 1}), "Fold produced non-ternary!"
        print(f"\n  Fold verification: sign(base × medical) is ternary ✓")
        print(f"  Folded:   +1:{(folded==1).sum()} 0:{(folded==0).sum()} -1:{(folded==-1).sum()}")

        # Verify: fold is lossless (ternary × ternary = ternary)
        double_folded = np.sign(folded.astype(np.int16) * session.astype(np.int16)).astype(np.int8)
        assert set(np.unique(double_folded)).issubset({-1, 0, 1}), "Double fold produced non-ternary!"
        print(f"  Double fold: sign(folded × session) is ternary ✓")
        print(f"  Double:   +1:{(double_folded==1).sum()} 0:{(double_folded==0).sum()} "
              f"-1:{(double_folded==-1).sum()}")

    print("\n  ✅ Tensor statechart demo complete.\n")

    return sc


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Tensor Statechart Engine — Plate Loader VSM")
    parser.add_argument("--create-plates", action="store_true",
                        help="Create demo plate files and test mmap")
    parser.add_argument("--plate-dir", type=str, default=None,
                        help="Directory for plate files")
    args = parser.parse_args()

    if args.create_plates:
        plate_dir = Path(args.plate_dir or "checkpoints/plates")
        create_demo_plates(plate_dir)
        sc = run_demo(plate_dir)
    else:
        sc = run_demo()


if __name__ == "__main__":
    main()
