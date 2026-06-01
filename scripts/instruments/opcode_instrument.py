"""Opcode Instrument — Live VSM for Watching a Model Think.

A VSM add-on that wraps any HuggingFace language model and shows its
opcodes executing in real-time. Like a CPU debugger for an LLM.

Architecture (VSM, Beer 1972):
  S5(identity):     combinator basis + zone map (from hologram reader)
  S4(intelligence): anomaly detection — energy spikes, mode shifts, retrieval events
  S3(control):      overhead governor — sampling rate, layer selection
  S2(coordination): canonical trace format, accumulator
  S1(operations):   hook manager, projector, classifier, emitter

State machine: DORMANT → CALIBRATE → MONITOR → EMIT → DONE

Usage:
    from scripts.instruments.opcode_instrument import OpcodeInstrument

    instrument = OpcodeInstrument(model, tokenizer)
    instrument.attach()

    output = model.generate(input_ids, max_new_tokens=50)

    for trace in instrument.traces:
        print(trace)

    instrument.detach()

CLI Usage:
    uv run python scripts/instruments/opcode_instrument.py \\
        --model EleutherAI/pythia-160m-deduped \\
        --prompt "The capital of France is"

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np
import torch

# ══════════════════════════════════════════════════════════════════════
# Reuse hologram reader utilities
# ══════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).resolve().parent.parent
RESULTS_BASE = SCRIPT_DIR.parent / "results" / "hologram-reader"

# Inline the architecture-agnostic helpers (avoid import dependency)

def get_layers(model) -> list:
    """Get transformer layers list from any architecture."""
    for attr_path in ["model.layers", "transformer.h", "gpt_neox.layers",
                      "model.model.layers"]:
        obj = model
        try:
            for part in attr_path.split("."):
                obj = getattr(obj, part)
            return list(obj)
        except AttributeError:
            continue
    raise RuntimeError(f"Cannot find transformer layers in {type(model)}")


def get_gate_and_down(layer):
    """Get gate_proj and down_proj modules from a layer's MLP."""
    mlp = layer.mlp if hasattr(layer, "mlp") else layer

    if hasattr(mlp, "gate_proj"):
        return mlp.gate_proj, mlp.down_proj, "swiglu"
    if hasattr(mlp, "dense_h_to_4h"):
        return mlp.dense_h_to_4h, mlp.dense_4h_to_h, "gpt_neox"
    if hasattr(mlp, "gate_up_proj"):
        return mlp.gate_up_proj, mlp.down_proj, "fused"
    raise RuntimeError(f"Cannot find MLP projections in {type(mlp)}")


# Combinator basis
ALL_OPS = ["K", "I", "B", "C", "D", "Y", "W", "WHNF",
           "beta_K", "beta_I", "beta_apply", "beta_compose"]
TOP4_OPS = ["K", "I", "B", "C"]


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# S2 — Coordination: Data Structures
# ══════════════════════════════════════════════════════════════════════

@dataclass
class LayerSnapshot:
    """One layer's measurements for one token."""
    layer_idx: int
    zone: str = ""            # SILENT / ENRICH / SUPPRESS / COMMIT
    phase: str = ""           # build / execute / emit
    opcode_energy: dict = field(default_factory=dict)   # op → cosine projection
    dominant_op: str = ""
    dominant_energy: float = 0.0
    gate_survival: float = 0.0   # fraction of neurons that fired
    total_energy: float = 0.0    # L2 norm of FFN output


@dataclass
class TraceRecord:
    """One token's complete instrumentation trace."""
    token_idx: int
    token_text: str = ""
    token_id: int = 0
    timestamp_ms: float = 0.0
    layers: list = field(default_factory=list)   # list[LayerSnapshot]
    s4_flags: list = field(default_factory=list)  # S4 annotations
    overhead_ms: float = 0.0

    def dominant_op(self) -> str:
        """Overall dominant opcode across all layers."""
        energy_totals: dict[str, float] = {}
        for snap in self.layers:
            for op, e in snap.opcode_energy.items():
                energy_totals[op] = energy_totals.get(op, 0.0) + abs(e)
        if not energy_totals:
            return "?"
        return max(energy_totals, key=energy_totals.get)

    def total_energy(self) -> float:
        return sum(s.total_energy for s in self.layers)


# ══════════════════════════════════════════════════════════════════════
# S3 — Control: Configuration and Overhead Governor
# ══════════════════════════════════════════════════════════════════════

class SamplingMode(Enum):
    FULL = auto()       # all layers, all 12 ops
    STANDARD = auto()   # all layers, top-4 ops (K,I,B,C)
    LIGHT = auto()      # every 4th layer + boundaries, top-4
    MINIMAL = auto()    # first + last + enrich boundary only


@dataclass
class InstrumentConfig:
    """S3 configuration for the instrument."""
    sampling_mode: SamplingMode = SamplingMode.STANDARD
    max_overhead: float = 0.5        # max fraction overhead (0.5 = 2× slower)
    active_ops: list = field(default_factory=lambda: list(TOP4_OPS))
    auto_downgrade: bool = True      # auto-reduce resolution if overhead exceeded
    renderer: str = "terminal"       # "terminal", "jsonl", "none", or callable


# ══════════════════════════════════════════════════════════════════════
# State Machine
# ══════════════════════════════════════════════════════════════════════

class State(Enum):
    DORMANT = auto()
    CALIBRATE = auto()
    MONITOR = auto()
    EMIT = auto()
    DONE = auto()


TRANSITIONS = {
    (State.DORMANT, "attach"):              State.CALIBRATE,
    (State.CALIBRATE, "ready"):             State.MONITOR,
    (State.CALIBRATE, "no_fingerprints"):   State.CALIBRATE,
    (State.MONITOR, "detach"):              State.EMIT,
    (State.MONITOR, "overhead_exceeded"):   State.CALIBRATE,
    (State.EMIT, "complete"):               State.DONE,
    (State.DONE, "attach"):                 State.CALIBRATE,
}


# ══════════════════════════════════════════════════════════════════════
# The Instrument
# ══════════════════════════════════════════════════════════════════════

class OpcodeInstrument:
    """VSM instrument that wraps a language model and traces opcodes.

    S5: combinator fingerprints + zone map
    S4: anomaly detector (energy spikes, mode shifts)
    S3: overhead governor
    S2: trace accumulator
    S1: hooks, projector, emitter
    """

    def __init__(
        self,
        model,
        tokenizer,
        config: InstrumentConfig | None = None,
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.config = config or InstrumentConfig()
        self.state = State.DORMANT

        # S5: basis (loaded during CALIBRATE)
        self.fingerprints: dict[str, np.ndarray] = {}
        self.zone_map: dict[int, dict] = {}
        self.n_layers: int = 0
        self.d_model: int = 0

        # S2: accumulator
        self.traces: list[TraceRecord] = []
        self._token_counter: int = 0

        # S1: hooks
        self._hooks: list = []
        self._captures: dict[int, dict] = {}  # layer_idx → {gate, ffn}
        self._hooked_layers: list[int] = []

        # S3: overhead tracking
        self._overhead_history: list[float] = []

        # S4: running stats
        self._energy_history: list[float] = []
        self._mode_history: list[str] = []

        # Internal
        self._layers = None
        self._model_slug = ""
        self._state_trace: list[dict] = []

    # ── State Machine ──────────────────────────────────────────

    def _transition(self, event: str) -> bool:
        key = (self.state, event)
        if key not in TRANSITIONS:
            return False
        old = self.state
        self.state = TRANSITIONS[key]
        self._state_trace.append({
            "from": old.name, "event": event, "to": self.state.name,
            "time": time.time(),
        })
        return True

    # ── Public API ─────────────────────────────────────────────

    def attach(self, renderer: str | None = None):
        """Attach instrument to the model. DORMANT → CALIBRATE → MONITOR."""
        if renderer:
            self.config.renderer = renderer

        self._transition("attach")
        self._calibrate()
        self._transition("ready")
        self._install_hooks()
        log(f"  ✅ Instrument attached [{self.config.sampling_mode.name}] "
            f"— {len(self._hooked_layers)}/{self.n_layers} layers hooked")

    def detach(self):
        """Detach instrument. MONITOR → EMIT → DONE."""
        self._remove_hooks()
        self._transition("detach")
        self._emit_session()
        self._transition("complete")
        log(f"  ✅ Instrument detached — {len(self.traces)} tokens traced")

    def trace_prompt(self, prompt: str):
        """Trace the model processing each token in the prompt (prefill).

        Runs a separate forward pass per prefix to capture the FFN
        output for each token position as the model reads the prompt.
        """
        if self.state != State.MONITOR:
            return

        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids
        device = next(self.model.parameters()).device
        input_ids = input_ids.to(device)
        tokens = [self.tokenizer.decode([tid]) for tid in input_ids[0]]

        print(f"\n  ── PREFILL: reading prompt ({len(tokens)} tokens) ──")

        for pos in range(len(tokens)):
            # Forward pass with prefix up to this position
            prefix = input_ids[:, :pos + 1]
            self._captures.clear()
            with torch.no_grad():
                _ = self.model(input_ids=prefix)

            self.on_token(
                token_id=input_ids[0, pos].item(),
                token_text=tokens[pos],
            )

        print(f"  ── PREFILL COMPLETE ──\n")

    def on_token(self, token_id: int, token_text: str = ""):
        """Call after each forward pass to process captured activations.

        Typically called from a generate callback or manually after
        model forward.
        """
        if self.state != State.MONITOR:
            return

        t0 = time.time()

        if not token_text and token_id >= 0:
            token_text = self.tokenizer.decode([token_id])

        # S1: project captures onto fingerprints
        snapshots = self._project_captures()

        # S4: anomaly detection
        flags = self._s4_analyze(snapshots, token_text)

        overhead_ms = (time.time() - t0) * 1000

        record = TraceRecord(
            token_idx=self._token_counter,
            token_text=token_text,
            token_id=token_id,
            timestamp_ms=time.time() * 1000,
            layers=snapshots,
            s4_flags=flags,
            overhead_ms=overhead_ms,
        )
        self.traces.append(record)
        self._token_counter += 1

        # S3: overhead check
        self._overhead_history.append(overhead_ms)
        if (self.config.auto_downgrade and len(self._overhead_history) > 5
                and self._check_overhead()):
            self._transition("overhead_exceeded")
            self._remove_hooks()
            self._downgrade_sampling()
            self._transition("ready")
            self._install_hooks()

        # Render
        self._render(record)

        # Clear captures for next token
        self._captures.clear()

    # ── S5: Calibrate (load basis) ─────────────────────────────

    def _calibrate(self):
        """Load fingerprints and zone map. Build fingerprints if needed."""
        self._layers = get_layers(self.model)
        self.n_layers = len(self._layers)
        self.d_model = self.model.config.hidden_size
        model_name = getattr(self.model.config, '_name_or_path', 'unknown')
        self._model_slug = model_name.replace("/", "_")

        log(f"\n  [CALIBRATE] {model_name}: {self.n_layers}L × d={self.d_model}")

        # Try loading fingerprints from hologram reader cache
        fp_path = RESULTS_BASE / self._model_slug / f"fingerprints_{self._model_slug}.npz"
        if fp_path.exists():
            data = np.load(fp_path)
            self.fingerprints = {
                op: data[op] for op in ALL_OPS if op in data
            }
            log(f"  [S5] Loaded {len(self.fingerprints)} fingerprints from {fp_path}")
        else:
            log(f"  [S5] No cached fingerprints at {fp_path}")
            log(f"  [S5] Building fingerprints (this takes a few minutes first time)...")
            self._build_fingerprints()

        # Load or auto-detect zone map
        summary_path = RESULTS_BASE / self._model_slug / "summary.json"
        if summary_path.exists():
            with open(summary_path) as f:
                summary = json.load(f)
            zones = summary.get("zone_boundaries", {})
            for zone_name, bounds in zones.items():
                for li in range(bounds["start"], bounds["end"] + 1):
                    self.zone_map[li] = {"zone": zone_name}
            log(f"  [S5] Loaded zone map from {summary_path}")
        else:
            # Universal heuristic: classify by depth fraction
            for li in range(self.n_layers):
                frac = li / max(1, self.n_layers - 1)
                if frac < 0.50:
                    zone = "SILENT"
                elif frac < 0.85:
                    zone = "ENRICH"
                elif frac < 0.93:
                    zone = "SUPPRESS"
                else:
                    zone = "COMMIT"
                self.zone_map[li] = {"zone": zone}
            log(f"  [S5] Auto-detected zones by depth heuristic")

        # Determine which layers to hook based on sampling mode
        self._compute_hooked_layers()

    def _compute_hooked_layers(self):
        """S3: decide which layers to hook based on sampling mode."""
        mode = self.config.sampling_mode
        enrich_start = None
        for li in range(self.n_layers):
            if self.zone_map.get(li, {}).get("zone") == "ENRICH":
                enrich_start = li
                break

        if mode == SamplingMode.FULL or mode == SamplingMode.STANDARD:
            self._hooked_layers = list(range(self.n_layers))
        elif mode == SamplingMode.LIGHT:
            layers = set(range(0, self.n_layers, 4))
            layers.add(0)
            layers.add(self.n_layers - 1)
            if enrich_start is not None:
                layers.add(enrich_start)
            self._hooked_layers = sorted(layers)
        elif mode == SamplingMode.MINIMAL:
            layers = {0, self.n_layers - 1}
            if enrich_start is not None:
                layers.add(enrich_start)
            self._hooked_layers = sorted(layers)

    # ── S1: Hook Manager ───────────────────────────────────────

    def _install_hooks(self):
        """Install forward hooks on selected layers."""
        self._remove_hooks()
        self._captures.clear()

        for li in self._hooked_layers:
            layer = self._layers[li]
            try:
                gate_mod, down_mod, mlp_type = get_gate_and_down(layer)
            except RuntimeError:
                continue

            # Hook gate projection output
            def make_gate_hook(idx, mtype):
                def hook(m, inp, out):
                    t = out.detach()
                    if mtype == "gpt_neox" or mtype == "fused":
                        half = t.shape[-1] // 2
                        gate_val = t[0, -1, :half].cpu().float().numpy()
                    else:
                        gate_val = t[0, -1, :].cpu().float().numpy()
                    self._captures.setdefault(idx, {})["gate"] = gate_val
                return hook
            self._hooks.append(gate_mod.register_forward_hook(
                make_gate_hook(li, mlp_type)))

            # Hook down projection output (FFN output)
            def make_down_hook(idx):
                def hook(m, inp, out):
                    self._captures.setdefault(idx, {})["ffn"] = (
                        out[0, -1, :].detach().cpu().float().numpy()
                    )
                return hook
            self._hooks.append(down_mod.register_forward_hook(make_down_hook(li)))

    def _remove_hooks(self):
        for h in self._hooks:
            h.remove()
        self._hooks.clear()

    # ── S1: Projector ──────────────────────────────────────────

    def _project_captures(self) -> list[LayerSnapshot]:
        """Project captured FFN outputs onto combinator fingerprints."""
        ops = self.config.active_ops
        snapshots = []

        for li in self._hooked_layers:
            cap = self._captures.get(li)
            if cap is None or "ffn" not in cap:
                continue

            ffn_vec = cap["ffn"]
            ffn_norm = float(np.linalg.norm(ffn_vec))

            # Project onto fingerprints
            energy = {}
            if ffn_norm > 1e-10:
                ffn_unit = ffn_vec / ffn_norm
                for op in ops:
                    fp = self.fingerprints.get(op)
                    if fp is not None and li < fp.shape[0]:
                        fp_vec = fp[li]
                        fp_norm = np.linalg.norm(fp_vec)
                        if fp_norm > 1e-10:
                            energy[op] = float(np.dot(ffn_unit, fp_vec / fp_norm))

            # Gate survival
            gate_survival = 0.0
            if "gate" in cap:
                gate = cap["gate"]
                sig = 1.0 / (1.0 + np.exp(-np.clip(gate, -20, 20)))
                gate_survival = float(np.mean(sig > 0.5))

            # Dominant op
            dom_op = max(energy, key=lambda k: abs(energy[k])) if energy else "?"
            dom_energy = abs(energy.get(dom_op, 0.0))

            # Zone
            zone_info = self.zone_map.get(li, {})
            zone = zone_info.get("zone", "?")

            # Phase (by depth fraction)
            frac = li / max(1, self.n_layers - 1)
            phase = "build" if frac < 0.33 else "execute" if frac < 0.67 else "emit"

            snapshots.append(LayerSnapshot(
                layer_idx=li, zone=zone, phase=phase,
                opcode_energy=energy, dominant_op=dom_op,
                dominant_energy=dom_energy,
                gate_survival=gate_survival,
                total_energy=ffn_norm,
            ))

        return snapshots

    # ── S4: Intelligence (anomaly detection) ───────────────────

    def _s4_analyze(self, snapshots: list[LayerSnapshot], token_text: str) -> list[str]:
        """Detect anomalies in the current trace."""
        flags = []
        if not snapshots:
            return flags

        # Total energy this token
        total_e = sum(s.total_energy for s in snapshots)
        self._energy_history.append(total_e)

        # Overall dominant mode
        dom = max(
            set(s.dominant_op for s in snapshots if s.dominant_op != "?"),
            key=lambda op: sum(abs(s.opcode_energy.get(op, 0))
                              for s in snapshots),
            default="?",
        )
        self._mode_history.append(dom)

        # Energy spike detection (after 5 tokens of history)
        if len(self._energy_history) > 5:
            recent = self._energy_history[-6:-1]
            mean_e = np.mean(recent)
            std_e = np.std(recent) + 1e-10
            if total_e > mean_e + 2 * std_e:
                flags.append(f"⚡ energy spike: {total_e:.0f} (mean={mean_e:.0f})")

        # Mode shift detection
        if len(self._mode_history) >= 2:
            prev = self._mode_history[-2]
            if dom != prev and dom != "?" and prev != "?":
                flags.append(f"🔄 mode shift: {prev}→{dom}")

        # ENRICH zone activity
        enrich_snaps = [s for s in snapshots if s.zone == "ENRICH"]
        if enrich_snaps:
            enrich_e = sum(s.total_energy for s in enrich_snaps)
            silent_snaps = [s for s in snapshots if s.zone == "SILENT"]
            silent_e = sum(s.total_energy for s in silent_snaps) if silent_snaps else 1
            if enrich_e > silent_e * 1.5 and len(self._energy_history) > 3:
                flags.append(f"🔍 retrieval event: ENRICH={enrich_e:.0f} >> SILENT={silent_e:.0f}")

        return flags

    # ── S3: Overhead Governor ──────────────────────────────────

    def _check_overhead(self) -> bool:
        """Check if overhead exceeds budget. Return True if downgrade needed."""
        if len(self._overhead_history) < 5:
            return False
        recent = self._overhead_history[-5:]
        mean_overhead = np.mean(recent)
        # Rough heuristic: if instrumentation takes >50% of a typical token time
        return mean_overhead > 100  # >100ms per token = too much on CPU

    def _downgrade_sampling(self):
        """S3: reduce resolution to stay within overhead budget."""
        mode = self.config.sampling_mode
        if mode == SamplingMode.FULL:
            self.config.sampling_mode = SamplingMode.STANDARD
        elif mode == SamplingMode.STANDARD:
            self.config.sampling_mode = SamplingMode.LIGHT
        elif mode == SamplingMode.LIGHT:
            self.config.sampling_mode = SamplingMode.MINIMAL
        log(f"  [S3] Downgraded to {self.config.sampling_mode.name}")
        self._compute_hooked_layers()

    # ── S1: Emitter ────────────────────────────────────────────

    def _emit_session(self):
        """Emit accumulated session data."""
        if not self.traces:
            return
        log(f"\n  [EMIT] {len(self.traces)} tokens traced, "
            f"{sum(len(t.s4_flags) for t in self.traces)} S4 flags")

    # ── Rendering ──────────────────────────────────────────────

    def _render(self, record: TraceRecord):
        """Render a trace record based on configured renderer."""
        r = self.config.renderer
        if r == "none":
            return
        elif r == "terminal":
            self._render_terminal(record)
        elif r == "jsonl":
            self._render_jsonl(record)
        elif callable(r):
            r(record)

    def _render_terminal(self, record: TraceRecord):
        """Colorful terminal output for one token."""
        # Token header
        text = record.token_text.replace("\n", "\\n")
        print(f"\n  Token {record.token_idx:>3}: \"{text}\"")

        for snap in record.layers:
            # Energy bar (max 12 chars)
            max_e = max(abs(v) for v in snap.opcode_energy.values()) if snap.opcode_energy else 0
            bar_len = min(12, int(max_e * 12 / 0.5)) if max_e > 0 else 0
            bar = "█" * bar_len + "░" * (12 - bar_len)

            # Opcode energies (top 4)
            ops_str = "  ".join(
                f"{op}:{snap.opcode_energy.get(op, 0):+.2f}"
                for op in TOP4_OPS
                if op in snap.opcode_energy
            )

            zone_str = f"{snap.zone:<8}"
            phase_str = f"{snap.phase:<7}"
            gate_str = f"gate:{snap.gate_survival*100:.1f}%"

            print(f"    L{snap.layer_idx:02d} [{zone_str}/{phase_str}] "
                  f"{bar}  {ops_str}  {gate_str}")

        # S4 flags
        for flag in record.s4_flags:
            print(f"    {flag}")

    def _render_jsonl(self, record: TraceRecord):
        """One JSON line per token to stdout."""
        obj = {
            "token_idx": record.token_idx,
            "token": record.token_text,
            "token_id": record.token_id,
            "layers": [
                {
                    "layer": s.layer_idx, "zone": s.zone, "phase": s.phase,
                    "energy": s.opcode_energy, "dominant": s.dominant_op,
                    "gate_survival": round(s.gate_survival, 4),
                    "total_energy": round(s.total_energy, 2),
                }
                for s in record.layers
            ],
            "flags": record.s4_flags,
            "overhead_ms": round(record.overhead_ms, 2),
        }
        print(json.dumps(obj), flush=True)

    # ── Fingerprint Building ───────────────────────────────────

    def _build_fingerprints(self):
        """Build combinator fingerprints from minimal pairs (S5 bootstrap).

        Delegates to the hologram reader. If the import fails (e.g., running
        from a different working directory), falls back to sys.path manipulation.
        """
        # Add the project scripts directory to sys.path for the import
        experiments_dir = SCRIPT_DIR / "experiments"
        if str(experiments_dir.parent) not in sys.path:
            sys.path.insert(0, str(experiments_dir.parent))

        try:
            from experiments.hologram_reader import HologramReader, ModelConfig
        except ImportError:
            # Direct path fallback
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "hologram_reader", experiments_dir / "hologram_reader.py")
            hr_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(hr_mod)
            HologramReader = hr_mod.HologramReader
            ModelConfig = hr_mod.ModelConfig

        model_name = getattr(self.model.config, '_name_or_path', 'unknown')
        reader = HologramReader(
            model_name=model_name,
            skip_moire=True, skip_trace=True,
        )
        reader.model = self.model
        reader.tokenizer = self.tokenizer
        reader.layers = self._layers
        reader.model_config = ModelConfig.detect(
            self.model, model_name,
            str(next(self.model.parameters()).device),
        )
        reader.results_dir = RESULTS_BASE / reader.model_config.slug()
        reader.results_dir.mkdir(parents=True, exist_ok=True)
        reader.layer_descriptors = [None] * self.n_layers

        reader._phase_fingerprint()
        self.fingerprints = reader.fingerprints
        log(f"  [S5] Built {len(self.fingerprints)} fingerprints")


# ══════════════════════════════════════════════════════════════════════
# Generate callback — bridges model.generate() to the instrument
# ══════════════════════════════════════════════════════════════════════

class InstrumentedGenerate:
    """Wrapper that calls instrument.on_token() during generation."""

    def __init__(self, instrument: OpcodeInstrument):
        self.instrument = instrument

    def __call__(self, model, tokenizer, input_ids, **kwargs):
        """Generate tokens with instrumented tracing."""
        max_new = kwargs.pop("max_new_tokens", 20)
        device = input_ids.device

        generated = input_ids.clone()
        for i in range(max_new):
            with torch.no_grad():
                outputs = model(input_ids=generated)
            logits = outputs.logits[:, -1, :]
            next_token = logits.argmax(dim=-1, keepdim=True)
            generated = torch.cat([generated, next_token], dim=1)

            token_id = next_token.item()
            token_text = tokenizer.decode([token_id])
            self.instrument.on_token(token_id, token_text)

            # Stop on EOS
            if token_id == tokenizer.eos_token_id:
                break

        return generated


# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════

def main():
    import argparse
    from transformers import AutoModelForCausalLM, AutoTokenizer

    parser = argparse.ArgumentParser(
        description="Opcode Instrument — Watch a model think")
    parser.add_argument("--model", default="EleutherAI/pythia-160m-deduped")
    parser.add_argument("--prompt", default="The capital of France is")
    parser.add_argument("--max-tokens", type=int, default=20)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--mode", default="standard",
                        choices=["full", "standard", "light", "minimal"])
    parser.add_argument("--renderer", default="terminal",
                        choices=["terminal", "jsonl", "none"])
    parser.add_argument("--no-prefill", action="store_true",
                        help="Skip prompt tracing, only trace generation")
    parser.add_argument("--prefill-only", action="store_true",
                        help="Trace prompt only, don't generate")
    args = parser.parse_args()

    mode_map = {
        "full": SamplingMode.FULL, "standard": SamplingMode.STANDARD,
        "light": SamplingMode.LIGHT, "minimal": SamplingMode.MINIMAL,
    }

    log(f"\n  Loading {args.model}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.float32, device_map=args.device)
    model.eval()

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    config = InstrumentConfig(
        sampling_mode=mode_map[args.mode],
        renderer=args.renderer,
    )

    instrument = OpcodeInstrument(model, tokenizer, config)
    instrument.attach()

    # Phase 1: trace the prompt (prefill)
    if not args.no_prefill:
        instrument.trace_prompt(args.prompt)

    # Phase 2: generate new tokens
    if not args.prefill_only:
        log(f"  ── GENERATE: {args.max_tokens} new tokens ──\n")
        input_ids = tokenizer(args.prompt, return_tensors="pt").input_ids
        input_ids = input_ids.to(args.device)

        gen = InstrumentedGenerate(instrument)
        output_ids = gen(model, tokenizer, input_ids, max_new_tokens=args.max_tokens)

        generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        log(f"\n  Generated: {generated_text}")

    instrument.detach()


if __name__ == "__main__":
    main()
