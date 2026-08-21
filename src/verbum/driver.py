"""Live REPL driver — model-in-the-loop exploration (stage 1, s346, Michael GO).

The nREPL move: hold the model resident, bounce it one transition at a time,
seal/fork KV continuations, and read the registers live — explore BEFORE
freezing a probe, exactly like poking Clojure in nREPL before writing to disk.

DISCIPLINE (queue §P-REPL-DRIVER stage 1):
  - REPL ≡ explore, NOT record (λ record): anything real gets re-run as a
    named, committed, reproducible harness. No verdicts from this module.
  - Capture-euphoria guard: REPL output FEEDS the next freeze; it never
    opens or closes a claim.
  - Validity gate before trust: `Driver.validity()` — greedy determinism,
    fork-identity plant (fork-with-no-change ≡ original continuation),
    append law (incremental KV ≡ full-pass teacher forcing).

CAPTURE SEMANTICS: signs[k] / hidden[k] / attn[k] = machine state at the
forward pass that EMITTED tokens[k] (the deciding position), i.e. the
read-head view while choosing that token. Frame 0 is the final prompt
position; frame k>0 is the forward of tokens[k-1].

Usage (tmux IPython, `uv run --group level1 --with ipython ipython`):

    from verbum.driver import Driver
    d = Driver()                        # loads Qwen/Qwen3-14B on MPS, resident
    d.validity()                        # gate: run once before believing reads
    s = d.prefill("The reduction of (K a b) is")
    b = d.bounce(s, n=24)               # greedy continuation with captures
    b.text                              # what it wrote to the tape
    r = d.routes(b)                     # [n_tok, L, 17] pole cosines
    d.stations(b)                       # per-token argmax pole, top band
    d.lens(b, step=0, layer=30)         # logit-lens of the deciding state
    f = d.fork(s, " K discards y.", n=24)   # counterfactual tape write
    d.read_mass(b, step=0)              # [L, T] attention read over the tape

KV law (s334): APPEND only — a Seal's cache is never mutated; every use
clones. Canonical text is the bus; KV is model-private.
"""

from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.cache_utils import DynamicCache

_ROOT = Path(__file__).resolve().parents[2]
_CENTROIDS_NPZ = _ROOT / "results" / "expanded-gram" / "qwen3-14b" / "centroids.npz"
_OPCODES_DIR = _ROOT / "opcodes"

CRYSTAL9 = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
WHNF_STATES = [f"whnf:{o}" for o in ["K", "I", "B", "C", "S", "D", "W"]]
BASIS17 = [*CRYSTAL9, *WHNF_STATES, "div:Y"]

_GATE_PAT = re.compile(r"\.(\d+)\.mlp\.(gate_proj|dense_h_to_4h)$")


def _find_gate_modules(model) -> list[tuple[int, str, torch.nn.Module]]:
    """Locate per-layer FFN gate modules (same regex as combinator_relationship_map)."""
    hits = []
    for name, mod in model.named_modules():
        m = _GATE_PAT.search(name)
        if m:
            hits.append((int(m.group(1)), name, mod))
    hits.sort(key=lambda x: x[0])
    return hits


def _clone_cache(cache: DynamicCache) -> DynamicCache:
    """Deep-copy a DynamicCache (APPEND law: seals are immutable, uses clone)."""
    new = DynamicCache()
    if hasattr(cache, "layers"):  # transformers >= 5: DynamicLayer objects
        for li, layer in enumerate(cache.layers):
            new.update(layer.keys.clone(), layer.values.clone(), li)
    elif hasattr(cache, "key_cache"):  # transformers 4.x
        pairs = zip(cache.key_cache, cache.value_cache, strict=True)
        for li, (k, v) in enumerate(pairs):
            new.update(k.clone(), v.clone(), li)
    else:
        raise TypeError(f"unknown cache layout: {type(cache).__name__}")
    return new


@dataclass
class Seal:
    """An immutable KV continuation: ids + cache + the pending next-token logits."""

    sid: int
    ids: list[int]
    text: str
    cache: DynamicCache = field(repr=False)
    logits_last: torch.Tensor = field(repr=False)  # [vocab] float32 cpu

    def __len__(self) -> int:
        return len(self.ids)


@dataclass
class Bounce:
    """One driver bounce: emitted tokens + per-emission register captures."""

    prompt_text: str
    prompt_ids: list[int]
    new_ids: list[int]
    tokens: list[str]
    signs: np.ndarray = field(repr=False)  # [n, L, d] int8, sign(gate_proj)
    hidden: np.ndarray | None = field(repr=False)  # [n, L+1, d] float16
    attn: list[np.ndarray] | None = field(repr=False)  # per step [L, T_k] float16
    end_seal: Seal | None = None

    @property
    def text(self) -> str:
        return "".join(self.tokens)

    def __repr__(self) -> str:  # keep REPL output small
        return f"Bounce(n={len(self.new_ids)}, text={self.text!r:.80})"


class Driver:
    """Resident-model trampoline with register captures. One instance per kernel."""

    def __init__(
        self,
        model_id: str = "Qwen/Qwen3-14B",
        device: str = "mps",
        dtype: str = "bfloat16",
    ):
        t0 = time.time()
        self.model_id = model_id
        self.device = device
        self.tok = AutoTokenizer.from_pretrained(model_id)
        self.model = (
            AutoModelForCausalLM.from_pretrained(
                model_id,
                dtype=getattr(torch, dtype),
                low_cpu_mem_usage=True,
                attn_implementation="eager",  # hooks + output_attentions
            )
            .to(device)
            .eval()
        )
        self._gates = _find_gate_modules(self.model)
        self.n_layers = len(self._gates)
        self.d_model = int(self.model.config.hidden_size)
        eos = self.model.generation_config.eos_token_id
        self._eos = set(eos if isinstance(eos, (list, tuple)) else [eos])
        self._sign_buf: dict[int, np.ndarray] = {}
        self._hooks = [
            mod.register_forward_hook(self._mk_hook(li)) for li, _, mod in self._gates
        ]
        self.seals: dict[int, Seal] = {}
        self._next_sid = 0
        self._pole_P: np.ndarray | None = None  # [L, S, d] unit CMR'd centroids
        self._pole_mu: np.ndarray | None = None  # [L, d]
        self._pole_order: list[str] = []
        self._rcc = None  # lazy opcode classifier
        self._rcc_layers: list[int] = []
        print(
            f"driver: {model_id} on {device} — {self.n_layers} layers, "
            f"d={self.d_model}, load {time.time() - t0:.0f}s"
        )

    # ---------------------------------------------------------------- hooks

    def _mk_hook(self, li: int):
        def hook(_m, _inp, out):
            v = out[0, -1].detach().float().cpu().numpy()  # emitting position
            self._sign_buf[li] = np.sign(v).astype(np.int8)

        return hook

    def _grab_signs(self) -> np.ndarray:
        return np.stack([self._sign_buf[li] for li, _, _ in self._gates])  # [L, d]

    # ------------------------------------------------------------- forwards

    @torch.no_grad()
    def _forward(self, ids: list[int], cache: DynamicCache, hidden: bool, attn: bool):
        t = torch.tensor([ids], device=self.device)
        return self.model(
            input_ids=t,
            past_key_values=cache,
            use_cache=True,
            output_hidden_states=hidden,
            output_attentions=attn,
        )

    @staticmethod
    def _frame_hidden(out) -> np.ndarray:
        return np.stack(
            [h[0, -1].detach().float().cpu().numpy() for h in out.hidden_states]
        ).astype(np.float16)  # [L+1, d]

    @staticmethod
    def _frame_attn(out) -> np.ndarray:
        rows = [
            a[0, :, -1, :].mean(0).detach().float().cpu().numpy()
            for a in out.attentions
        ]
        return np.stack(rows).astype(np.float16)  # [L, T_k]

    # ------------------------------------------------------------------ api

    def _register(self, ids: list[int], text: str, cache, logits) -> Seal:
        s = Seal(self._next_sid, list(ids), text, cache, logits)
        self.seals[s.sid] = s
        self._next_sid += 1
        return s

    def prefill(self, text: str, chat: bool = False) -> Seal:
        """Compile text onto the tape: one forward, returns an immutable Seal."""
        if chat:
            text = self.tok.apply_chat_template(
                [{"role": "user", "content": text}],
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
        ids = self.tok(text, return_tensors="pt").input_ids[0].tolist()
        cache = DynamicCache()
        out = self._forward(ids, cache, hidden=False, attn=False)
        logits = out.logits[0, -1].detach().float().cpu()
        return self._register(ids, text, cache, logits)

    def bounce(
        self,
        src: str | Seal,
        n: int = 32,
        hidden: bool = True,
        attn: bool = False,
        stop_at_eos: bool = True,
        keep_seal: bool = True,
    ) -> Bounce:
        """Greedy-decode n tokens from text or a Seal, capturing per-emission state.

        A Seal's cache is CLONED before use (append law) — the seal survives.
        """
        signs, hiddens, attns, new_ids, toks = [], [], [], [], []
        if isinstance(src, Seal):
            cache = _clone_cache(src.cache)
            ids = list(src.ids)
            text = src.text
            logits = src.logits_last.clone()
            # frame 0 (the deciding state of the sealed position) is not
            # re-run; captures start at the first step forward. To get frame
            # 0 captures, bounce from text instead.
            first_frame_pending = False
        else:
            text = src
            ids = self.tok(src, return_tensors="pt").input_ids[0].tolist()
            cache = DynamicCache()
            out = self._forward(ids, cache, hidden=hidden, attn=attn)
            logits = out.logits[0, -1].detach().float().cpu()
            signs.append(self._grab_signs())
            if hidden:
                hiddens.append(self._frame_hidden(out))
            if attn:
                attns.append(self._frame_attn(out))
            first_frame_pending = True

        for _k in range(n):
            nxt = int(torch.argmax(logits).item())
            new_ids.append(nxt)
            toks.append(self.tok.decode([nxt]))
            if stop_at_eos and nxt in self._eos:
                break
            out = self._forward([nxt], cache, hidden=hidden, attn=attn)
            logits = out.logits[0, -1].detach().float().cpu()
            signs.append(self._grab_signs())
            if hidden:
                hiddens.append(self._frame_hidden(out))
            if attn:
                attns.append(self._frame_attn(out))

        # align: frame k emitted token k; drop the trailing frame (it decides
        # the (n+1)th token, which we did not take).
        n_emit = len(new_ids)
        if first_frame_pending:
            frames = signs[:n_emit]
            hframes = hiddens[:n_emit] if hidden else None
            aframes = attns[:n_emit] if attn else None
        else:  # seal path: frame k-1 (step forwards) emitted token k; frame
            # for token 0 lives in the seal's pending logits (no capture).
            frames = signs[: max(n_emit - 1, 0)]
            hframes = hiddens[: max(n_emit - 1, 0)] if hidden else None
            aframes = attns[: max(n_emit - 1, 0)] if attn else None

        end_seal = None
        if keep_seal:
            end_seal = self._register(
                ids + new_ids, text + "".join(toks), cache, logits
            )
        return Bounce(
            prompt_text=text,
            prompt_ids=ids,
            new_ids=new_ids,
            tokens=toks,
            signs=np.stack(frames)
            if frames
            else np.zeros((0, self.n_layers, 0), dtype=np.int8),
            hidden=np.stack(hframes) if hidden and hframes else None,
            attn=aframes if attn else None,
            end_seal=end_seal,
        )

    def fork(self, seal: Seal, alt_text: str = "", n: int = 32, **kw) -> Bounce:
        """Branch a sealed continuation: append alt_text (may be empty), decode n.

        fork(seal, "") is the identity plant — must reproduce bounce(seal).
        """
        if not alt_text:
            return self.bounce(seal, n=n, **kw)
        cache = _clone_cache(seal.cache)
        alt_ids = (
            self.tok(alt_text, add_special_tokens=False, return_tensors="pt")
            .input_ids[0]
            .tolist()
        )
        out = self._forward(alt_ids, cache, hidden=False, attn=False)
        logits = out.logits[0, -1].detach().float().cpu()
        branched = self._register(
            seal.ids + alt_ids, seal.text + alt_text, cache, logits
        )
        return self.bounce(branched, n=n, **kw)

    def drop_seal(self, sid: int) -> None:
        self.seals.pop(sid, None)

    # ---------------------------------------------------------------- views

    def _load_pole_frame(self, order: list[str] | None = None) -> None:
        z = np.load(_CENTROIDS_NPZ)
        basis = [str(b) for b in z["basis"]]
        order = order or [s for s in BASIS17 if s in basis]
        missing = [s for s in (order or []) if s not in basis]
        if missing:
            raise ValueError(f"states not in committed basis: {missing}")
        idx = [basis.index(s) for s in order]
        cent = z["centroids"][:, idx, :].astype(np.float32)  # [L, S, d]
        mu = cent.mean(axis=1)  # [L, d]
        centc = cent - mu[:, None, :]
        nrm = np.linalg.norm(centc, axis=2, keepdims=True)
        self._pole_P = centc / np.where(nrm < 1e-9, 1.0, nrm)
        self._pole_mu = mu
        self._pole_order = order

    def routes(self, b: Bounce | np.ndarray) -> np.ndarray:
        """Per-emission pole cosines [n, L, S] against the committed 17-frame."""
        if self._pole_P is None:
            self._load_pole_frame()
        signs = b.signs if isinstance(b, Bounce) else b
        x = signs.astype(np.float32) - self._pole_mu[None]
        nrm = np.linalg.norm(x, axis=2, keepdims=True)
        xn = x / np.where(nrm < 1e-9, 1.0, nrm)
        return np.einsum("nld,lsd->nls", xn, self._pole_P).astype(np.float32)

    def stations(self, b: Bounce, band: tuple[int, int] | None = None) -> list[str]:
        """Per-token argmax pole averaged over a layer band (default: top 25%)."""
        r = self.routes(b)
        lo, hi = band or (int(self.n_layers * 0.75), self.n_layers)
        top = r[:, lo:hi, :].mean(axis=1)  # [n, S]
        out = []
        for k in range(top.shape[0]):
            s = int(np.argmax(top[k]))
            out.append(f"{b.tokens[k]!r} → {self._pole_order[s]} ({top[k, s]:+.3f})")
        return out

    def lens(self, b: Bounce, step: int = -1, layer: int = -1, top_k: int = 8):
        """Logit-lens the deciding state of emission `step` at `layer`."""
        from verbum.jlens import logit_lens

        if b.hidden is None:
            raise ValueError("bounce captured no hidden states (hidden=False)")
        h = torch.from_numpy(b.hidden[step, layer].astype(np.float32))
        logits = logit_lens(self.model, h)
        idx = torch.topk(logits, top_k).indices.tolist()
        return [self.tok.decode([i]) for i in idx]

    def read_mass(self, b: Bounce, step: int = -1) -> np.ndarray:
        """[L, T_k] head-averaged attention of emission `step` over the tape."""
        if b.attn is None:
            raise ValueError("bounce captured no attention (attn=False)")
        return b.attn[step].astype(np.float32)

    def trace(self, b: Bounce, z_thresh: float = 3.0):
        """Style-3 multi-register trace table: op ⊕ station per emission.

        print(d.trace(b)) for the table; d.trace(b).md() for chat export.
        """
        from verbum.tracefmt import build_trace

        return build_trace(self, b, z_thresh)

    def deptrace(self, b: Bounce, step: int = 0, top_k: int = 3):
        """Depth trace: per-layer lens ⊕ op ⊕ station of one deciding pass.

        The vertical companion to trace() — emissions are time, the math
        is depth. Needs a bounce captured with hidden=True.
        """
        from verbum.tracefmt import build_depth_trace

        return build_depth_trace(self, b, step, top_k)

    # -------------------------------------------------------------- opcodes

    def calibrate_opcodes(
        self, probes_per_comb: int = 6, n_perm: int = 300, z_thresh: float = 3.0
    ):
        """Lazy: calibrate the opcodes/ crystal classifier on this model (minutes)."""
        sys.path.insert(0, str(_OPCODES_DIR))
        from trace import calibrate_register

        import topology as topo_mod

        topo = topo_mod.detect_topology(self.model, self.model.config)
        layers = [li for li, _, _ in self._gates]
        self._rcc, summ, _ = calibrate_register(
            self.model,
            self.tok,
            topo,
            "gate",
            layers,
            probes_per_comb,
            n_perm,
            z_thresh,
        )
        self._rcc_layers = layers
        return summ

    def opcodes(self, b: Bounce, z_thresh: float = 3.0) -> list[str]:
        """Per-emission dominant combinator (needs calibrate_opcodes first)."""
        if self._rcc is None:
            raise RuntimeError("run calibrate_opcodes() first")
        out = []
        for k in range(b.signs.shape[0]):
            res = self._rcc.classify(
                {li: b.signs[k, i] for i, li in enumerate(self._rcc_layers)}
            )
            zmap = getattr(res, "z", None) or getattr(res, "zmap", None) or {}
            if zmap:
                op = max(zmap, key=zmap.get)
                lab = op if zmap[op] > z_thresh else "·"
            else:
                lab = getattr(res, "dominant", "·")
            out.append(f"{b.tokens[k]!r} → {lab}")
        return out

    # ------------------------------------------------------------- validity

    def validity(self, prompt: str | None = None, n: int = 16) -> dict:
        """Gate before trust: determinism, fork-identity plant, append law."""
        prompt = prompt or "The SKI combinator calculus reduces (K a b) to"
        rep: dict[str, object] = {}

        b1 = self.bounce(prompt, n=n, hidden=False, keep_seal=False)
        b2 = self.bounce(prompt, n=n, hidden=False, keep_seal=False)
        rep["determinism_ids"] = b1.new_ids == b2.new_ids
        rep["determinism_sign_dev"] = (
            int(np.abs(b1.signs.astype(np.int16) - b2.signs.astype(np.int16)).max())
            if b1.signs.size and b1.signs.shape == b2.signs.shape
            else None
        )

        s = self.prefill(prompt)
        c1 = self.bounce(s, n=n, hidden=False, keep_seal=False)
        c2 = self.fork(s, "", n=n, hidden=False, keep_seal=False)
        rep["fork_identity"] = c1.new_ids == c2.new_ids
        rep["seal_matches_fresh"] = c1.new_ids == b1.new_ids

        full_ids = b1.prompt_ids + b1.new_ids
        with torch.no_grad():
            out = self.model(
                input_ids=torch.tensor([full_ids], device=self.device),
                use_cache=False,
            )
        pred = out.logits[0].float().cpu().argmax(dim=-1)
        base = len(b1.prompt_ids)
        mism = sum(
            int(pred[base - 1 + k].item()) != b1.new_ids[k]
            for k in range(len(b1.new_ids))
        )
        rep["append_law_mismatches"] = mism
        rep["ok"] = bool(
            rep["determinism_ids"]
            and (rep["determinism_sign_dev"] in (0, None))
            and rep["fork_identity"]
            and rep["seal_matches_fresh"]
            and mism == 0
        )
        self.drop_seal(s.sid)
        status = "PASS" if rep["ok"] else "FAIL"
        print(f"validity: {status} — {rep}")
        return rep
