"""Hologram Reader VSM — Read the full opcode map from a teacher model.

Session 172. A self-directing VSM tensor statechart that systematically
reads the holographic program from a language model's weights. Not a
linear pipeline — a state machine that adapts its probing strategy
based on what it discovers.

Architecture (VSM, Beer 1972):
  S5(identity):     combinator basis {K,I,B,C,D,Y,W,WHNF,β_K,β_I,β_apply,β_compose}
  S4(intelligence): adaptive probing — decides what to probe next
  S3(control):      compute budget — prioritizes layers by zone
  S2(coordination): canonical accumulator — consistent cross-layer measurements
  S1(operations):   fingerprint, overlay, classify, moiré, map, emit

State machine:
  DORMANT → FINGERPRINT → SCAN → CLASSIFY → MOIRÉ → MAP → EMIT → DONE
  S4 can inject probe_deeper events that loop back to SCAN.

Output: structured opcode map (JSON + NPZ) — the hologram readout.

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/hologram_reader.py --model Qwen/Qwen3-0.6B
    uv run python scripts/experiments/hologram_reader.py --model Qwen/Qwen3-0.6B --skip-moire
    uv run python scripts/experiments/hologram_reader.py --model Qwen/Qwen3-0.6B --skip-trace

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


# ══════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════

RESULTS_BASE = Path(__file__).parent.parent.parent / "results" / "hologram-reader"
PROBES_DIR = Path(__file__).parent.parent.parent / "probes"

COMPILE_GATE = (
    "You are a lambda calculus compiler. Convert natural language to "
    "typed lambda calculus.\nInput a combinator expression. Output its "
    "beta-normal form.\nBe terse. Output ONLY the reduced expression."
)

# Combinator basis — S5 identity
COMBINATOR_NAMES = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]
BETA_NAMES = ["beta_K", "beta_I", "beta_apply", "beta_compose"]
ALL_OP_NAMES = COMBINATOR_NAMES + BETA_NAMES
N_OPS = len(ALL_OP_NAMES)


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# S5 — Identity: Model Detection
# ══════════════════════════════════════════════════════════════════════

@dataclass
class ModelConfig:
    """Detected model architecture parameters."""
    name: str
    n_layers: int
    d_model: int
    d_ff: int
    n_heads: int
    n_kv_heads: int
    arch_type: str  # "qwen2", "llama", "gpt_neox", "mistral", etc.
    device: str = "cpu"

    @classmethod
    def detect(cls, model, model_name: str, device: str) -> "ModelConfig":
        """Auto-detect model architecture from the loaded model."""
        config = model.config

        # Get core dimensions
        d_model = config.hidden_size
        n_layers = config.num_hidden_layers
        n_heads = config.num_attention_heads
        n_kv_heads = getattr(config, "num_key_value_heads", n_heads)

        # FFN dimension — different names across architectures
        d_ff = getattr(config, "intermediate_size", None)
        if d_ff is None:
            d_ff = getattr(config, "ffn_dim", d_model * 4)

        # Architecture type from model class name
        model_type = getattr(config, "model_type", "unknown")
        arch_map = {
            "qwen2": "qwen2", "qwen3": "qwen2", "qwen3_5": "qwen2",
            "llama": "llama", "mistral": "mistral",
            "gpt_neox": "gpt_neox", "phi": "phi",
            "olmo": "olmo", "olmo2": "olmo",
        }
        arch_type = arch_map.get(model_type, model_type)

        return cls(
            name=model_name, n_layers=n_layers, d_model=d_model,
            d_ff=d_ff, n_heads=n_heads, n_kv_heads=n_kv_heads,
            arch_type=arch_type, device=device,
        )

    def slug(self) -> str:
        return self.name.replace("/", "_")


def get_layers(model) -> list:
    """Get the transformer layers list from any architecture."""
    # Try common attribute paths
    for attr_path in [
        "model.layers",           # Qwen, LLaMA, Mistral, OLMo
        "transformer.h",          # GPT-2 style
        "gpt_neox.layers",        # GPT-NeoX / Pythia
        "model.model.layers",     # Some wrapped models
    ]:
        obj = model
        try:
            for part in attr_path.split("."):
                obj = getattr(obj, part)
            return list(obj)
        except AttributeError:
            continue
    raise RuntimeError(f"Cannot find transformer layers in {type(model)}")


def get_mlp(layer) -> tuple:
    """Get (gate_proj, up_proj, down_proj) from a transformer layer's MLP.

    Returns weight tensors as numpy arrays.
    Handles SwiGLU (gate + up + down) and standard MLP (fc1 + fc2).
    """
    mlp = layer.mlp if hasattr(layer, "mlp") else layer

    # SwiGLU style: gate_proj, up_proj, down_proj (Qwen, LLaMA, Mistral)
    if hasattr(mlp, "gate_proj"):
        gate_w = mlp.gate_proj.weight.detach().cpu().float().numpy()
        up_w = mlp.up_proj.weight.detach().cpu().float().numpy()
        down_w = mlp.down_proj.weight.detach().cpu().float().numpy()
        return gate_w, up_w, down_w

    # GPT-NeoX / Pythia: dense_h_to_4h (combined gate+up), dense_4h_to_h
    if hasattr(mlp, "dense_h_to_4h"):
        combined = mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()
        # Split combined into gate and up halves
        d_ff_half = combined.shape[0] // 2
        gate_w = combined[:d_ff_half]
        up_w = combined[d_ff_half:]
        down_w = mlp.dense_4h_to_h.weight.detach().cpu().float().numpy()
        return gate_w, up_w, down_w

    # OLMo style
    if hasattr(mlp, "gate_up_proj"):
        combined = mlp.gate_up_proj.weight.detach().cpu().float().numpy()
        d_ff_half = combined.shape[0] // 2
        gate_w = combined[:d_ff_half]
        up_w = combined[d_ff_half:]
        down_w = mlp.down_proj.weight.detach().cpu().float().numpy()
        return gate_w, up_w, down_w

    raise RuntimeError(f"Cannot find MLP projections in {type(mlp)}")


# ══════════════════════════════════════════════════════════════════════
# S2 — Coordination: Data Structures
# ══════════════════════════════════════════════════════════════════════

@dataclass
class LayerDescriptor:
    """Complete description of one layer's holographic content."""
    layer_idx: int
    # Overlay matrix (combinator-space transform)
    overlay: Optional[list] = None  # [12, 12] serialized
    dominant_opcode: str = ""
    dominant_strength: float = 0.0
    dominant_transform: Optional[tuple] = None  # (from, to, strength)
    transform_strength: float = 0.0
    pass_through_strength: float = 0.0
    selectivity: str = ""  # "pass" | "transform" | "mixed"
    # Zone classification
    compute_zone: str = ""  # "A" | "B" | "C"
    retrieval_zone: str = ""  # "SILENT" | "ENRICH" | "SUPPRESS" | "COMMIT"
    pipeline_phase: str = ""  # "build" | "execute" | "emit"
    # Moiré measurements (if ENRICH layer)
    moire_selectivity: Optional[float] = None
    moire_rank: Optional[int] = None
    moire_relation_coherence: Optional[float] = None

    def to_dict(self) -> dict:
        d = {}
        for k, v in self.__dict__.items():
            if v is not None and v != "" and v != 0.0:
                d[k] = v
        return d


@dataclass
class OpcodeMap:
    """The complete hologram readout — S2 accumulator."""
    model_config: Optional[dict] = None
    layers: list = field(default_factory=list)  # list of LayerDescriptor dicts
    overlay_tensor: Optional[np.ndarray] = None  # [n_layers, 12, 12]
    zone_boundaries: dict = field(default_factory=dict)
    phase_boundaries: dict = field(default_factory=dict)
    opcode_census: dict = field(default_factory=dict)
    relation_census: dict = field(default_factory=dict)
    invariant_checks: dict = field(default_factory=dict)
    scan_metadata: dict = field(default_factory=dict)


# ══════════════════════════════════════════════════════════════════════
# VSM State Machine
# ══════════════════════════════════════════════════════════════════════

class State(Enum):
    DORMANT = auto()
    FINGERPRINT = auto()
    SCAN = auto()
    CLASSIFY = auto()
    MOIRE = auto()
    MAP = auto()
    EMIT = auto()
    DONE = auto()


TRANSITIONS = {
    (State.DORMANT, "load"):               State.FINGERPRINT,
    (State.FINGERPRINT, "fingerprints_ready"): State.SCAN,
    (State.SCAN, "scan_complete"):          State.CLASSIFY,
    (State.CLASSIFY, "classified"):         State.MOIRE,
    (State.MOIRE, "moire_complete"):        State.MAP,
    (State.MOIRE, "probe_deeper"):          State.SCAN,
    (State.MAP, "map_complete"):            State.EMIT,
    (State.MAP, "probe_deeper"):            State.SCAN,
    (State.EMIT, "complete"):              State.DONE,
}


class HologramReader:
    """VSM tensor statechart for reading the hologram from a teacher model.

    S5: combinator basis (the mathematical invariant)
    S4: adaptive probe strategy
    S3: compute budget and layer priority
    S2: canonical accumulator (OpcodeMap)
    S1: measurement operations
    """

    def __init__(
        self,
        model_name: str,
        device: str = "auto",
        skip_moire: bool = False,
        skip_trace: bool = False,
        max_iterations: int = 2,
        probe_file: str = "fact_recall_extended.json",
    ):
        self.model_name = model_name
        self.raw_device = device
        self.skip_moire = skip_moire
        self.skip_trace = skip_trace
        self.max_iterations = max_iterations
        self.probe_file = probe_file

        # State machine
        self.state = State.DORMANT
        self.iteration = 0
        self.trace: list[dict] = []

        # S5: loaded by FINGERPRINT phase
        self.fingerprints: dict[str, np.ndarray] = {}

        # S2: accumulator
        self.opcode_map = OpcodeMap()
        self.layer_descriptors: list[LayerDescriptor] = []

        # Model references (loaded on demand)
        self.model = None
        self.tokenizer = None
        self.model_config: Optional[ModelConfig] = None
        self.layers = None

        # Output directory
        self.results_dir: Optional[Path] = None

    # ── State Machine ──

    def _transition(self, event: str):
        """Execute a state transition."""
        key = (self.state, event)
        if key not in TRANSITIONS:
            log(f"  ⚠ No transition for ({self.state.name}, {event})")
            return False

        old = self.state
        self.state = TRANSITIONS[key]
        self.trace.append({
            "from": old.name, "event": event, "to": self.state.name,
            "time": time.time(),
        })
        log(f"\n{'═' * 70}")
        log(f"  [{old.name}] ──({event})──▶ [{self.state.name}]")
        log(f"{'═' * 70}")
        return True

    def run(self):
        """Execute the full VSM scan."""
        t0 = time.time()
        log(f"\n{'═' * 70}")
        log(f"  Hologram Reader VSM — {self.model_name}")
        log(f"  State: {self.state.name}")
        log(f"{'═' * 70}")

        # DORMANT → FINGERPRINT
        self._load_model()
        self._transition("load")
        self._phase_fingerprint()
        self._transition("fingerprints_ready")

        # Main scan loop (S4 can loop back)
        while self.state != State.DONE:
            if self.state == State.SCAN:
                self._phase_scan()
                self._transition("scan_complete")

            elif self.state == State.CLASSIFY:
                self._phase_classify()
                self._transition("classified")

            elif self.state == State.MOIRE:
                if self.skip_moire:
                    log("  [S3] Skipping moiré (--skip-moire)")
                    self._transition("moire_complete")
                else:
                    self._phase_moire()
                    # S4: check if we need to probe deeper
                    event = self._s4_evaluate_moire()
                    self._transition(event)

            elif self.state == State.MAP:
                self._phase_map()
                # S4: final coverage check
                event = self._s4_evaluate_map()
                self._transition(event)

            elif self.state == State.EMIT:
                self._phase_emit()
                self._transition("complete")

            else:
                log(f"  ⚠ Unexpected state: {self.state.name}")
                break

        elapsed = time.time() - t0
        log(f"\n  ✅ Hologram Reader complete in {elapsed:.1f}s")
        log(f"  Output: {self.results_dir}")

        # Cleanup
        self._unload_model()

    # ── Model Loading ──

    def _load_model(self):
        """Load the model and detect its architecture."""
        log(f"\n  Loading {self.model_name}...")
        t0 = time.time()

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, trust_remote_code=True
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Determine device
        if self.raw_device == "auto":
            if torch.cuda.is_available():
                device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
        else:
            device = self.raw_device

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,
            device_map=device if device != "mps" else "auto",
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        )
        self.model.eval()

        self.model_config = ModelConfig.detect(self.model, self.model_name, device)
        self.layers = get_layers(self.model)

        # Setup results directory
        self.results_dir = RESULTS_BASE / self.model_config.slug()
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Initialize layer descriptors
        self.layer_descriptors = [
            LayerDescriptor(layer_idx=i) for i in range(self.model_config.n_layers)
        ]

        log(f"  Loaded in {time.time()-t0:.1f}s")
        log(f"  Architecture: {self.model_config.arch_type}")
        log(f"  Layers: {self.model_config.n_layers}, d_model: {self.model_config.d_model}, d_ff: {self.model_config.d_ff}")

    def _unload_model(self):
        """Release model memory."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        self.layers = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # ── S1 Operations ──

    def _capture_ffn(self, text: str, layer_indices: list[int]) -> dict[int, np.ndarray]:
        """Capture FFN down_proj output at specified layers, last token."""
        ids = self.tokenizer.encode(text, return_tensors="pt")
        device = next(self.model.parameters()).device
        ids = ids.to(device)

        captures = {}
        hooks = []

        for li in layer_indices:
            layer = self.layers[li]
            mlp = layer.mlp if hasattr(layer, "mlp") else layer

            # Find the down projection module
            if hasattr(mlp, "down_proj"):
                target = mlp.down_proj
            elif hasattr(mlp, "dense_4h_to_h"):
                target = mlp.dense_4h_to_h
            else:
                continue

            def make_hook(idx):
                def hook(m, inp, out):
                    captures[idx] = out[0, -1, :].detach().cpu().float().numpy()
                return hook
            hooks.append(target.register_forward_hook(make_hook(li)))

        with torch.no_grad():
            _ = self.model(input_ids=ids)

        for h in hooks:
            h.remove()
        return captures

    # ── Phase: FINGERPRINT ──

    def _build_fingerprint_pairs(self) -> dict[str, list[tuple[str, str]]]:
        """Minimal pairs for each combinator."""
        pairs = {}
        pairs["K"] = [
            (f"K {a} {b}", f"{a}")
            for a in ["x", "y", "a", "b", "f", "g"]
            for b in ["z", "w", "c", "d"]
            if a != b
        ][:10]
        pairs["I"] = [(f"I {v}", f"{v}") for v in ["x", "y", "a", "b", "f", "g", "z", "w"]]
        pairs["B"] = [
            (f"B {f} {g} {x}", f"{f} ({g} {x})")
            for f in ["f", "g", "h", "p"]
            for g in ["q", "r", "s"]
            if f != g
            for x in ["x", "a"]
        ][:10]
        pairs["C"] = [
            (f"C {f} {x} {y}", f"{f} {y} {x}")
            for f in ["f", "g", "h"]
            for x in ["x", "a", "m"]
            for y in ["y", "b", "n"]
            if x != y
        ][:10]
        pairs["D"] = [
            (f"D {f} {g} {h} {x}", f"{f} ({g} ({h} {x}))")
            for f in ["f", "p"]
            for g in ["g", "q"]
            for h in ["h", "r"]
            if f != g and g != h
            for x in ["x", "a"]
        ][:8]
        pairs["Y"] = [(f"Y {f}", f"{f} (Y {f})") for f in ["f", "g", "h", "p", "q", "r"]]
        pairs["W"] = [
            (f"W {f} {x}", f"{f} {x} {x}")
            for f in ["f", "g", "h", "p"]
            for x in ["x", "a", "b"]
        ][:8]
        pairs["WHNF"] = [
            (f"λx. {b}", f"λx. {b}")
            for b in ["x", "f x", "g (h x)", "x y", "f (g x) y"]
        ][:6]
        pairs["beta_K"] = [
            (f"(λx. λy. x) {a} {b}", f"{a}")
            for a in ["a", "b", "x", "m"]
            for b in ["c", "y", "n"]
            if a != b
        ][:8]
        pairs["beta_I"] = [
            (f"(λx. x) {v}", f"{v}")
            for v in ["a", "b", "x", "y", "f", "g", "z", "w"]
        ]
        pairs["beta_apply"] = [
            (f"(λx. {f} x) {v}", f"{f} {v}")
            for f in ["f", "g", "h", "p", "q"]
            for v in ["a", "x", "m"]
        ][:10]
        pairs["beta_compose"] = [
            (f"(λx. {f} ({g} x)) {v}", f"{f} ({g} {v})")
            for f in ["f", "g", "h"]
            for g in ["p", "q", "r"]
            if f != g
            for v in ["a", "x"]
        ][:8]
        return pairs

    def _phase_fingerprint(self):
        """S1: Build or load combinator fingerprints."""
        fp_file = self.results_dir / f"fingerprints_{self.model_config.slug()}.npz"

        if fp_file.exists():
            log(f"  [S1] Loading cached fingerprints: {fp_file}")
            data = np.load(fp_file)
            self.fingerprints = {op: data[op] for op in ALL_OP_NAMES if op in data}
            if len(self.fingerprints) == N_OPS:
                log(f"  ✓ Loaded {N_OPS} ops × {self.fingerprints['K'].shape[0]} layers")
                return
            log(f"  ⚠ Incomplete ({len(self.fingerprints)}/{N_OPS}), rebuilding...")

        log(f"  [S1] Building fingerprints ({N_OPS} ops × {self.model_config.n_layers} layers)")
        pairs = self._build_fingerprint_pairs()
        all_layers = list(range(self.model_config.n_layers))

        for op_name, op_pairs in pairs.items():
            log(f"    {op_name}: {len(op_pairs)} pairs")
            layer_deltas: dict[int, list] = {li: [] for li in all_layers}

            for pi, (pre_expr, post_expr) in enumerate(op_pairs):
                pre_text = f"{COMPILE_GATE}\n\n{pre_expr} ="
                post_text = f"{COMPILE_GATE}\n\n{post_expr} ="
                pre_caps = self._capture_ffn(pre_text, all_layers)
                post_caps = self._capture_ffn(post_text, all_layers)

                for li in all_layers:
                    if li in pre_caps and li in post_caps:
                        layer_deltas[li].append(pre_caps[li] - post_caps[li])

                if (pi + 1) % 5 == 0:
                    log(f"      pair {pi + 1}/{len(op_pairs)}")

            # Build (n_layers, d_model) fingerprint
            fp_array = np.zeros((self.model_config.n_layers, self.model_config.d_model), dtype=np.float32)
            for li in all_layers:
                vecs = layer_deltas[li]
                if vecs:
                    mean = np.mean(vecs, axis=0)
                    norm = np.linalg.norm(mean)
                    if norm > 1e-10:
                        fp_array[li] = mean / norm
            self.fingerprints[op_name] = fp_array
            log(f"    ✓ {op_name}")

        # Cache
        np.savez_compressed(fp_file, **self.fingerprints)
        log(f"  [S1] Saved fingerprints to {fp_file}")

    # ── Phase: SCAN ──

    def _phase_scan(self):
        """S1: Read static program from all layers (overlay matrices)."""
        log(f"  [S1] Scanning {self.model_config.n_layers} layers (overlay decode)")

        n_layers = self.model_config.n_layers
        overlay_tensor = np.zeros((n_layers, N_OPS, N_OPS), dtype=np.float32)

        for li in range(n_layers):
            layer = self.layers[li]
            try:
                gate_w, up_w, down_w = get_mlp(layer)
            except RuntimeError as e:
                log(f"    L{li:02d}: ⚠ {e}")
                continue

            # Build fingerprint matrix for this layer
            fp_vecs = []
            valid_ops = []
            for op in ALL_OP_NAMES:
                v = self.fingerprints[op][li]
                norm = np.linalg.norm(v)
                if norm > 1e-10:
                    fp_vecs.append(v / norm)
                    valid_ops.append(op)

            if len(fp_vecs) < 2:
                continue

            fp_matrix = np.array(fp_vecs)  # (n_valid, d_model)

            # Project fingerprint directions through SwiGLU
            gate_resp = fp_matrix @ gate_w.T  # (n_ops, d_ff)
            up_resp = fp_matrix @ up_w.T

            overlay = np.zeros((len(valid_ops), len(valid_ops)))
            for i in range(len(valid_ops)):
                sig = 1.0 / (1.0 + np.exp(-np.clip(gate_resp[i], -20, 20)))
                silu = gate_resp[i] * sig
                combined = silu * up_resp[i]
                output = combined @ down_w.T
                out_norm = np.linalg.norm(output)
                if out_norm > 1e-10:
                    output_unit = output / out_norm
                    for j in range(len(valid_ops)):
                        overlay[i][j] = float(np.dot(output_unit, fp_matrix[j]))

            # Store in full-size tensor (padding if some ops were invalid)
            for i, op_i in enumerate(valid_ops):
                ii = ALL_OP_NAMES.index(op_i)
                for j, op_j in enumerate(valid_ops):
                    jj = ALL_OP_NAMES.index(op_j)
                    overlay_tensor[li, ii, jj] = overlay[i][j]

            # Characterize
            diag = {valid_ops[i]: float(overlay[i][i]) for i in range(len(valid_ops))}
            pass_strength = float(np.mean(np.abs(np.diag(overlay))))

            off_diag = overlay.copy()
            np.fill_diagonal(off_diag, 0)
            xform_strength = float(np.linalg.norm(off_diag))

            # Dominant opcode
            sorted_diag = sorted(diag.items(), key=lambda x: abs(x[1]), reverse=True)
            dom_op = sorted_diag[0][0] if sorted_diag else ""
            dom_str = sorted_diag[0][1] if sorted_diag else 0.0

            # Dominant transform (strongest off-diagonal)
            dom_xform = None
            if off_diag.size > 0:
                idx = np.unravel_index(np.argmax(np.abs(off_diag)), off_diag.shape)
                val = float(off_diag[idx])
                if abs(val) > 0.03:
                    dom_xform = (valid_ops[idx[0]], valid_ops[idx[1]], val)

            # Selectivity
            if pass_strength > xform_strength * 1.5:
                sel = "pass"
            elif xform_strength > pass_strength * 1.5:
                sel = "transform"
            else:
                sel = "mixed"

            # Update layer descriptor
            ld = self.layer_descriptors[li]
            ld.overlay = overlay.tolist()
            ld.dominant_opcode = dom_op
            ld.dominant_strength = dom_str
            ld.dominant_transform = dom_xform
            ld.transform_strength = xform_strength
            ld.pass_through_strength = pass_strength
            ld.selectivity = sel

            if li % max(1, n_layers // 8) == 0:
                diag_str = " ".join(f"{op}:{v:+.2f}" for op, v in sorted_diag[:3])
                log(f"    L{li:02d}: [{sel:>9}] {diag_str}")

            # Free weight memory
            del gate_w, up_w, down_w

        self.opcode_map.overlay_tensor = overlay_tensor
        log(f"  ✓ Scanned {n_layers} layers")

    # ── Phase: CLASSIFY ──

    def _phase_classify(self):
        """S1: Classify each layer into compute zone, retrieval zone, pipeline phase."""
        n = self.model_config.n_layers

        # Compute transform strength profile
        xform_strengths = [ld.transform_strength for ld in self.layer_descriptors]
        max_xform = max(xform_strengths) if xform_strengths else 1.0

        for i, ld in enumerate(self.layer_descriptors):
            depth_frac = i / max(1, n - 1)

            # Pipeline phase from transform strength (three-phase)
            if max_xform > 0:
                rel_strength = ld.transform_strength / max_xform
            else:
                rel_strength = 0

            if depth_frac < 0.33:
                ld.pipeline_phase = "build"
            elif depth_frac < 0.67:
                ld.pipeline_phase = "execute"
            else:
                ld.pipeline_phase = "emit"

            # Compute zone (based on depth)
            if depth_frac < 0.08:
                ld.compute_zone = "A"  # aperture
            elif depth_frac > 0.88:
                ld.compute_zone = "C"  # converge
            else:
                ld.compute_zone = "B"  # fan/compute

            # Retrieval zone (based on depth — universal lattice)
            if depth_frac < 0.50:
                ld.retrieval_zone = "SILENT"
            elif depth_frac < 0.85:
                ld.retrieval_zone = "ENRICH"
            elif depth_frac < 0.93:
                ld.retrieval_zone = "SUPPRESS"
            else:
                ld.retrieval_zone = "COMMIT"

        # Log classification summary
        zones = {}
        for ld in self.layer_descriptors:
            z = ld.retrieval_zone
            zones.setdefault(z, []).append(ld.layer_idx)

        log(f"  [S1] Classification:")
        for zone_name in ["SILENT", "ENRICH", "SUPPRESS", "COMMIT"]:
            layers = zones.get(zone_name, [])
            if layers:
                log(f"    {zone_name:>8}: L{min(layers):02d}–L{max(layers):02d} ({len(layers)} layers)")

        phases = {}
        for ld in self.layer_descriptors:
            p = ld.pipeline_phase
            phases.setdefault(p, []).append(ld.layer_idx)
        for phase_name in ["build", "execute", "emit"]:
            layers = phases.get(phase_name, [])
            if layers:
                avg_str = np.mean([self.layer_descriptors[l].transform_strength for l in layers])
                log(f"    {phase_name:>8}: L{min(layers):02d}–L{max(layers):02d} (avg xform: {avg_str:.2f})")

    # ── Phase: MOIRÉ ──

    def _phase_moire(self):
        """S1: Moiré decomposition on ENRICH layers."""
        # Find ENRICH layers
        enrich_layers = [ld.layer_idx for ld in self.layer_descriptors if ld.retrieval_zone == "ENRICH"]

        if not enrich_layers:
            log("  [S1] No ENRICH layers identified — skipping moiré")
            return

        # Load probe set
        probe_path = PROBES_DIR / self.probe_file
        if not probe_path.exists():
            # Fall back to smaller probe set
            probe_path = PROBES_DIR / "fact_recall.json"
        if not probe_path.exists():
            log(f"  [S1] No probe set found at {probe_path} — skipping moiré")
            return

        with open(probe_path) as f:
            probe_data = json.load(f)

        probes = probe_data.get("probes", [])
        if not probes:
            log("  [S1] Empty probe set — skipping moiré")
            return

        log(f"  [S1] Moiré decomposition: {len(probes)} probes × {len(enrich_layers)} ENRICH layers")

        # For each ENRICH layer, capture moiré patterns
        for li in enrich_layers:
            layer = self.layers[li]
            moire_patterns = []
            categories = []

            # Hook to capture gate and up activations
            gate_cap = {}
            up_cap = {}

            mlp = layer.mlp if hasattr(layer, "mlp") else layer

            def make_gate_hook():
                def hook(m, inp, out):
                    gate_cap["out"] = out[0, -1, :].detach().cpu().float().numpy()
                return hook

            def make_up_hook():
                def hook(m, inp, out):
                    up_cap["out"] = out[0, -1, :].detach().cpu().float().numpy()
                return hook

            # Attach hooks
            hooks = []
            if hasattr(mlp, "gate_proj"):
                hooks.append(mlp.gate_proj.register_forward_hook(make_gate_hook()))
                hooks.append(mlp.up_proj.register_forward_hook(make_up_hook()))
            elif hasattr(mlp, "dense_h_to_4h"):
                # Pythia: need to split the combined output
                def make_combined_hook():
                    def hook(m, inp, out):
                        half = out.shape[-1] // 2
                        gate_cap["out"] = out[0, -1, :half].detach().cpu().float().numpy()
                        up_cap["out"] = out[0, -1, half:].detach().cpu().float().numpy()
                    return hook
                hooks.append(mlp.dense_h_to_4h.register_forward_hook(make_combined_hook()))
            else:
                log(f"    L{li:02d}: ⚠ Cannot hook MLP for moiré capture")
                continue

            for pi, probe in enumerate(probes):
                prompt = probe.get("prompt", "")
                category = probe.get("category", "unknown")

                ids = self.tokenizer.encode(prompt, return_tensors="pt")
                device = next(self.model.parameters()).device
                ids = ids.to(device)

                gate_cap.clear()
                up_cap.clear()
                with torch.no_grad():
                    _ = self.model(input_ids=ids)

                if "out" in gate_cap and "out" in up_cap:
                    gate_act = gate_cap["out"]
                    up_act = up_cap["out"]
                    # Moiré = silu(gate) × up
                    sig = 1.0 / (1.0 + np.exp(-np.clip(gate_act, -20, 20)))
                    silu = gate_act * sig
                    moire = silu * up_act
                    moire_patterns.append(moire)
                    categories.append(category)

            for h in hooks:
                h.remove()

            if not moire_patterns:
                continue

            moire_matrix = np.array(moire_patterns)  # (n_probes, d_ff)

            # Compute selectivity: mean pairwise cosine
            norms = np.linalg.norm(moire_matrix, axis=1, keepdims=True)
            norms = np.clip(norms, 1e-10, None)
            moire_unit = moire_matrix / norms
            cos_matrix = moire_unit @ moire_unit.T
            n_probes = len(moire_patterns)
            mask = ~np.eye(n_probes, dtype=bool)
            mean_cos = float(np.mean(np.abs(cos_matrix[mask])))

            # Effective rank
            _, s, _ = np.linalg.svd(moire_matrix, full_matrices=False)
            s_norm = s / (s.sum() + 1e-10)
            entropy = -np.sum(s_norm * np.log(s_norm + 1e-10))
            eff_rank = int(np.exp(entropy))

            # Relation coherence
            unique_cats = sorted(set(categories))
            if len(unique_cats) > 1:
                within_cos = []
                cross_cos = []
                for i in range(n_probes):
                    for j in range(i + 1, n_probes):
                        c = abs(float(cos_matrix[i, j]))
                        if categories[i] == categories[j]:
                            within_cos.append(c)
                        else:
                            cross_cos.append(c)
                if within_cos and cross_cos:
                    rel_coherence = float(np.mean(within_cos) / max(np.mean(cross_cos), 1e-10))
                else:
                    rel_coherence = 1.0
            else:
                rel_coherence = 1.0

            # Update descriptor
            ld = self.layer_descriptors[li]
            ld.moire_selectivity = round(mean_cos, 4)
            ld.moire_rank = eff_rank
            ld.moire_relation_coherence = round(rel_coherence, 2)

            log(f"    L{li:02d}: selectivity={mean_cos:.3f}  rank={eff_rank}  "
                f"rel_coherence={rel_coherence:.2f}")

        log(f"  ✓ Moiré decomposition complete")

    # ── S4: Intelligence (adaptive evaluation) ──

    def _s4_evaluate_moire(self) -> str:
        """S4: Evaluate moiré results and decide whether to probe deeper."""
        enrich_layers = [ld for ld in self.layer_descriptors if ld.retrieval_zone == "ENRICH"]
        measured = [ld for ld in enrich_layers if ld.moire_rank is not None]

        if not measured:
            log("  [S4] No moiré measurements — proceeding to MAP")
            return "moire_complete"

        # Check coverage
        coverage = len(measured) / max(len(enrich_layers), 1)
        avg_rank = np.mean([ld.moire_rank for ld in measured])
        avg_coherence = np.mean([ld.moire_relation_coherence for ld in measured])

        log(f"  [S4] Moiré coverage: {coverage:.0%} ({len(measured)}/{len(enrich_layers)} layers)")
        log(f"       Avg rank: {avg_rank:.0f}  Avg relation coherence: {avg_coherence:.2f}")

        # S4 decision: probe deeper if coverage insufficient and budget remains
        if coverage < 0.80 and self.iteration < self.max_iterations:
            self.iteration += 1
            log(f"  [S4] Coverage below 80% — requesting deeper probe (iteration {self.iteration})")
            return "probe_deeper"

        return "moire_complete"

    def _s4_evaluate_map(self) -> str:
        """S4: Evaluate assembled map for completeness."""
        # Check opcode coverage: how many unique dominant opcodes?
        unique_ops = set(ld.dominant_opcode for ld in self.layer_descriptors if ld.dominant_opcode)
        coverage = len(unique_ops) / N_OPS

        log(f"  [S4] Opcode coverage: {len(unique_ops)}/{N_OPS} unique dominant opcodes ({coverage:.0%})")

        if coverage < 0.50 and self.iteration < self.max_iterations:
            self.iteration += 1
            log(f"  [S4] Low opcode diversity — requesting deeper probe (iteration {self.iteration})")
            return "probe_deeper"

        return "map_complete"

    # ── Phase: MAP ──

    def _phase_map(self):
        """S1: Assemble the complete opcode map."""
        log("  [S1] Assembling opcode map")

        n = self.model_config.n_layers

        # Zone boundaries
        zones = {"SILENT": [], "ENRICH": [], "SUPPRESS": [], "COMMIT": []}
        for ld in self.layer_descriptors:
            zones[ld.retrieval_zone].append(ld.layer_idx)
        zone_boundaries = {
            k: {"start": min(v), "end": max(v), "count": len(v)}
            for k, v in zones.items() if v
        }

        # Phase boundaries
        phases = {"build": [], "execute": [], "emit": []}
        for ld in self.layer_descriptors:
            phases[ld.pipeline_phase].append(ld.layer_idx)
        phase_boundaries = {}
        for k, v in phases.items():
            if v:
                avg_xform = float(np.mean([self.layer_descriptors[l].transform_strength for l in v]))
                phase_boundaries[k] = {
                    "start": min(v), "end": max(v), "count": len(v),
                    "avg_transform_strength": round(avg_xform, 3),
                }

        # Opcode census
        opcode_census = {}
        overlay_tensor = self.opcode_map.overlay_tensor
        for oi, op in enumerate(ALL_OP_NAMES):
            dominant_layers = [
                ld.layer_idx for ld in self.layer_descriptors
                if ld.dominant_opcode == op
            ]
            avg_diag = float(np.mean(np.abs(overlay_tensor[:, oi, oi]))) if overlay_tensor is not None else 0
            opcode_census[op] = {
                "dominant_in_layers": len(dominant_layers),
                "layers": dominant_layers,
                "avg_diagonal_strength": round(avg_diag, 4),
            }

        # Relation census (from moiré)
        relation_census = {}
        enrich_with_moire = [ld for ld in self.layer_descriptors if ld.moire_rank is not None]
        if enrich_with_moire:
            relation_census["_summary"] = {
                "n_enrich_layers_measured": len(enrich_with_moire),
                "avg_moire_rank": round(float(np.mean([ld.moire_rank for ld in enrich_with_moire])), 1),
                "avg_relation_coherence": round(float(np.mean([ld.moire_relation_coherence for ld in enrich_with_moire])), 2),
                "avg_selectivity": round(float(np.mean([ld.moire_selectivity for ld in enrich_with_moire])), 4),
            }

        # Invariant checks
        invariant_checks = {}
        # Combinator ordering
        if opcode_census:
            op_strengths = {
                op: opcode_census[op]["avg_diagonal_strength"]
                for op in COMBINATOR_NAMES
                if op in opcode_census
            }
            sorted_ops = sorted(op_strengths.items(), key=lambda x: x[1], reverse=True)
            invariant_checks["combinator_ordering"] = " ≥ ".join(f"{op}({s:.3f})" for op, s in sorted_ops)

        # Assemble
        self.opcode_map.model_config = {
            "name": self.model_config.name,
            "n_layers": self.model_config.n_layers,
            "d_model": self.model_config.d_model,
            "d_ff": self.model_config.d_ff,
            "n_heads": self.model_config.n_heads,
            "arch_type": self.model_config.arch_type,
        }
        self.opcode_map.layers = [ld.to_dict() for ld in self.layer_descriptors]
        self.opcode_map.zone_boundaries = zone_boundaries
        self.opcode_map.phase_boundaries = phase_boundaries
        self.opcode_map.opcode_census = opcode_census
        self.opcode_map.relation_census = relation_census
        self.opcode_map.invariant_checks = invariant_checks

        log(f"  ✓ Opcode map assembled: {n} layers, {len(opcode_census)} opcodes")

    # ── Phase: EMIT ──

    def _phase_emit(self):
        """S1: Write the opcode map to disk."""
        log(f"  [S1] Emitting opcode map to {self.results_dir}")

        # Scan metadata
        self.opcode_map.scan_metadata = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "iterations": self.iteration,
            "phases_completed": [t["to"] for t in self.trace],
            "state_trace": self.trace,
            "skip_moire": self.skip_moire,
            "skip_trace": self.skip_trace,
            "probe_file": self.probe_file,
        }

        # JSON output (human-readable)
        summary = {
            "model": self.opcode_map.model_config,
            "zone_boundaries": self.opcode_map.zone_boundaries,
            "phase_boundaries": self.opcode_map.phase_boundaries,
            "opcode_census": self.opcode_map.opcode_census,
            "relation_census": self.opcode_map.relation_census,
            "invariant_checks": self.opcode_map.invariant_checks,
            "scan_metadata": self.opcode_map.scan_metadata,
        }
        with open(self.results_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        log(f"    summary.json ✓")

        # Per-layer details
        with open(self.results_dir / "layers.json", "w") as f:
            json.dump(self.opcode_map.layers, f, indent=2, default=str)
        log(f"    layers.json ✓")

        # NPZ output (machine-readable)
        npz_data = {}
        if self.opcode_map.overlay_tensor is not None:
            npz_data["overlay"] = self.opcode_map.overlay_tensor
        npz_data["op_names"] = np.array(ALL_OP_NAMES)

        # Save fingerprints alongside
        for op, fp in self.fingerprints.items():
            npz_data[f"fp_{op}"] = fp

        np.savez_compressed(self.results_dir / "opcode_map.npz", **npz_data)
        log(f"    opcode_map.npz ✓")

        # State trace
        with open(self.results_dir / "state_trace.json", "w") as f:
            json.dump(self.trace, f, indent=2, default=str)
        log(f"    state_trace.json ✓")

        # Print summary to stdout
        print(f"\n{'═' * 70}")
        print(f"  HOLOGRAM READOUT: {self.model_config.name}")
        print(f"{'═' * 70}")
        print(f"  Layers: {self.model_config.n_layers}  d_model: {self.model_config.d_model}  d_ff: {self.model_config.d_ff}")
        print()

        # Zone summary
        print("  Retrieval Zones:")
        for zone_name in ["SILENT", "ENRICH", "SUPPRESS", "COMMIT"]:
            zb = self.opcode_map.zone_boundaries.get(zone_name)
            if zb:
                print(f"    {zone_name:>8}: L{zb['start']:02d}–L{zb['end']:02d} ({zb['count']} layers)")
        print()

        # Pipeline phases
        print("  Pipeline Phases:")
        for phase_name in ["build", "execute", "emit"]:
            pb = self.opcode_map.phase_boundaries.get(phase_name)
            if pb:
                print(f"    {phase_name:>8}: L{pb['start']:02d}–L{pb['end']:02d} "
                      f"(avg xform: {pb['avg_transform_strength']:.3f})")
        print()

        # Opcode census
        print("  Opcode Census:")
        sorted_ops = sorted(
            self.opcode_map.opcode_census.items(),
            key=lambda x: x[1]["dominant_in_layers"],
            reverse=True,
        )
        for op, info in sorted_ops:
            if info["dominant_in_layers"] > 0:
                layers_str = ",".join(str(l) for l in info["layers"][:5])
                if len(info["layers"]) > 5:
                    layers_str += ",..."
                print(f"    {op:>12}: dominant in {info['dominant_in_layers']:2d} layers "
                      f"(avg diag: {info['avg_diagonal_strength']:.3f})  [{layers_str}]")
        print()

        # Invariant checks
        if self.opcode_map.invariant_checks:
            print("  Invariant Checks:")
            for k, v in self.opcode_map.invariant_checks.items():
                print(f"    {k}: {v}")
            print()

        # Moiré summary
        rel_summary = self.opcode_map.relation_census.get("_summary")
        if rel_summary:
            print("  Moiré Summary (ENRICH zone):")
            print(f"    Measured layers: {rel_summary['n_enrich_layers_measured']}")
            print(f"    Avg rank:        {rel_summary['avg_moire_rank']}")
            print(f"    Avg coherence:   {rel_summary['avg_relation_coherence']}")
            print(f"    Avg selectivity: {rel_summary['avg_selectivity']}")
            print()

        print(f"  Output: {self.results_dir}")
        print(f"{'═' * 70}\n")


# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Hologram Reader VSM — Read the full opcode map from a teacher model"
    )
    parser.add_argument(
        "--model", type=str, default="Qwen/Qwen3-0.6B",
        help="HuggingFace model name (default: Qwen/Qwen3-0.6B)"
    )
    parser.add_argument(
        "--device", type=str, default="auto",
        help="Device: auto, cpu, cuda, mps (default: auto)"
    )
    parser.add_argument(
        "--skip-moire", action="store_true",
        help="Skip moiré decomposition (faster, compute ISA only)"
    )
    parser.add_argument(
        "--skip-trace", action="store_true",
        help="Skip dynamic activation tracing"
    )
    parser.add_argument(
        "--max-iterations", type=int, default=2,
        help="Max S4 probe-deeper iterations (default: 2)"
    )
    parser.add_argument(
        "--probes", type=str, default="fact_recall_extended.json",
        help="Probe set file in probes/ (default: fact_recall_extended.json)"
    )
    args = parser.parse_args()

    reader = HologramReader(
        model_name=args.model,
        device=args.device,
        skip_moire=args.skip_moire,
        skip_trace=args.skip_trace,
        max_iterations=args.max_iterations,
        probe_file=args.probes,
    )
    reader.run()


if __name__ == "__main__":
    main()
