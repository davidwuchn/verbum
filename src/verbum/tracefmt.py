"""Per-token multi-register trace table (s350, style-3).

One row per emission: token | opcode (null-gated dominant) | z-bar of the
top crystal op | runner-up | 17-pole station | flags (frame-0 prefill
spike suspicion — the s350 I-probe caveat, marked honestly in every output).

Pure formatter: eats a Driver + Bounce, computes once into TraceRow data,
renders many ways. REPL: print(d.trace(b)) — repr IS the table.
Chat export: d.trace(b).md().
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

CRYSTAL_OPS = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]


@dataclass(frozen=True)
class TraceRow:
    k: int
    token: str
    op: str  # null-gated dominant crystal op, "·" if sub-threshold
    z: float  # mean-z (over calibrated layers) of the top op
    second: str  # runner-up op with its mean-z
    station: str  # late-band argmax 17-pole with cosine
    frame0: bool  # deciding frame came from prefill (spike-suspect)


@dataclass
class Trace:
    prompt: str
    rows: list[TraceRow]

    def table(self, max_tok: int = 14, width: int = 72) -> str:
        head = f"{'tok':{max_tok}}  {'op':4} {'z':>6}  {'2nd':9} {'station':16} flags"
        p = self.prompt.replace("\n", "⏎")
        avail = width - len("prompt: ")
        if len(p) > avail:
            p = "…" + p[-(avail - 1) :]
        lines = [f"prompt: {p}", head, "-" * len(head)]
        for r in self.rows:
            t = repr(r.token)
            if len(t) > max_tok:
                t = t[: max_tok - 1] + "…"
            flag = "⚑frame0" if r.frame0 else ""
            lines.append(
                f"{t:{max_tok}}  {r.op:4} {r.z:+6.1f}  "
                f"{r.second:9} {r.station:16} {flag}"
            )
        return "\n".join(lines)

    def md(self) -> str:
        return "```\n" + self.table() + "\n```"

    def __repr__(self) -> str:
        return self.table()


@dataclass(frozen=True)
class DepthRow:
    layer: int
    lens: str  # top-k logit-lens tokens (what the residual says here)
    op: str  # per-layer top crystal op with z
    station: str  # per-layer argmax 17-pole with cosine


@dataclass
class DepthTrace:
    prompt: str
    token: str
    step: int
    rows: list[DepthRow]

    def table(self, width: int = 72) -> str:
        p = self.prompt.replace("\n", "⏎")
        avail = width - len("prompt: ")
        if len(p) > avail:
            p = "…" + p[-(avail - 1) :]
        head = f"{'L':>3}  {'lens':34} {'op(z)':9} station"
        lines = [
            f"prompt: {p}",
            f"deciding pass for emission {self.step}: {self.token!r}",
            head,
            "-" * len(head),
        ]
        for r in self.rows:
            lines.append(f"{r.layer:>3}  {r.lens:34} {r.op:9} {r.station}")
        return "\n".join(lines)

    def md(self) -> str:
        return "```\n" + self.table() + "\n```"

    def __repr__(self) -> str:
        return self.table()


def build_depth_trace(driver, bounce, step: int = 0, top_k: int = 3) -> DepthTrace:
    """Vertical slice: per-layer lens ⊕ op ⊕ station of ONE deciding pass.

    The math lives in depth, not emissions (s350: 12+9+34 descends
    concept→magnitude→digit across L26-39). Needs hidden=True capture.
    """
    if driver._rcc is None:
        raise RuntimeError("run calibrate_opcodes() first")
    if bounce.hidden is None:
        raise ValueError("bounce captured no hidden states (hidden=False)")
    res = driver._rcc.classify(
        {li: bounce.signs[step, i] for i, li in enumerate(driver._rcc_layers)}
    )
    pl = res.per_layer
    r17 = driver.routes(bounce)  # [n, L, S]
    rows: list[DepthRow] = []
    for layer in range(driver.n_layers):
        try:
            lens = "".join(
                f"{t!r:11}"
                for t in driver.lens(bounce, step=step, layer=layer, top_k=top_k)
            )
        except Exception as e:  # lens can fail on odd hidden shapes
            lens = f"<{e}>"
        zl = pl.get(layer, {})
        op = ""
        if zl:
            name = max(zl, key=zl.get)
            op = f"{name}{zl[name]:+.1f}"
        s = int(np.argmax(r17[step, layer]))
        rows.append(
            DepthRow(
                layer=layer,
                lens=lens,
                op=op,
                station=f"{driver._pole_order[s]}({r17[step, layer, s]:+.2f})",
            )
        )
    return DepthTrace(
        prompt=bounce.prompt_text,
        token=bounce.tokens[step],
        step=step,
        rows=rows,
    )


def build_trace(driver, bounce, z_thresh: float = 3.0) -> Trace:
    """Compute the per-emission multi-register trace for a Bounce."""
    if driver._rcc is None:
        raise RuntimeError("run calibrate_opcodes() first")
    r17 = driver.routes(bounce)  # [n, L, S]
    lo = int(driver.n_layers * 0.75)
    late = r17[:, lo:, :].mean(axis=1)  # [n, S]
    n = bounce.signs.shape[0]
    text_path = n == len(bounce.new_ids)  # seal path has n-1 frames
    rows: list[TraceRow] = []
    for k in range(n):
        res = driver._rcc.classify(
            {li: bounce.signs[k, i] for i, li in enumerate(driver._rcc_layers)}
        )
        pl = res.per_layer
        m = np.array([[pl[li][op] for op in CRYSTAL_OPS] for li in sorted(pl)])
        mz = m.mean(axis=0)
        dom = getattr(res, "dominant", None)
        has_dom = bool(dom) and dom != "·"
        # z belongs to the dominant when one exists; 2nd is the best op
        # EXCLUDING it (never the same op twice). Dot rows: z of the
        # nearest sub-threshold op, named in the 2nd column.
        if has_dom:
            di = CRYSTAL_OPS.index(dom)
            z = float(mz[di])
            rest = [i for i in np.argsort(-mz) if i != di]
            second = f"{CRYSTAL_OPS[rest[0]]}{mz[rest[0]]:+.1f}"
        else:
            order = np.argsort(-mz)
            z = float(mz[order[0]])
            second = f"{CRYSTAL_OPS[order[0]]}{mz[order[0]]:+.1f}"
        s = int(np.argmax(late[k]))
        rows.append(
            TraceRow(
                k=k,
                token=bounce.tokens[k],
                op=dom if has_dom else "·",
                z=z,
                second=second,
                station=f"{driver._pole_order[s]}({late[k, s]:+.2f})",
                frame0=(k == 0 and text_path),
            )
        )
    return Trace(prompt=bounce.prompt_text, rows=rows)
