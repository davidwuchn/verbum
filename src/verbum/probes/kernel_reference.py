# register: topological/routing
"""Kernel-reference symbolic combinator probes (s233, v5 lead 2).

The model-invariant for the opcode audit: a symbolic combinator PROGRAM whose reduction
the kernel (`lambda_ast`) CERTIFIES — the exact ordered fired-combinator trace. Reads
don't transfer across model scale (s232/s233 lead 1: 8B≠14B≠32B, gated-guard contrast
itself model-dependent), so instead of comparing models to each other, we anchor each
model's routing trajectory against this fixed kernel reference.

Two families, certified by `lambda_ast.fired_sequence`:

  • SATURATED  — the target combinator is fully applied, so the kernel FIRES it
                 (e.g. "B f g x" -> fires B). certified_fired_seq contains the target.
  • INERT      — the SAME target is UNDER-APPLIED, so it reaches normal form and FIRES
                 NOTHING (e.g. "B f g" -> normal form). The target SYMBOL is present but
                 the kernel certifies no reduction.

The saturated⊗inert pair is the specificity control: does the model's opcode routing
track certified REDUCIBILITY (a live redex) or mere SYMBOL PRESENCE? Plus COMPOSITE
programs (multi-fire, certified order) for the trace-ORDER alignment question.

Atoms are lowercase (parser: uppercase SKIBCWDYM = combinators, everything else = atom).

License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass, field

from verbum.lambda_ast import fired_sequence, parse, pretty, reduce

# kernel combinators we probe (arity from lambda_ast.REDUCTIONS)
_ARITY = {"I": 1, "K": 2, "W": 2, "C": 3, "B": 3, "S": 3, "D": 4}
_ATOMS = ["f", "g", "h", "x", "y", "z", "a", "b"]


@dataclass(frozen=True, slots=True)
class KernelRefProbe:
    """A symbolic combinator program with its kernel-certified reduction trace."""

    id: str
    program_text: str            # what is fed to the model
    target_combinator: str       # the combinator under test
    saturated: bool              # True => kernel fires the target; False => inert
    composite: bool              # True => multi-fire program (trace-order target)
    certified_fired_seq: list[str] = field(default_factory=list)
    certified_present: list[str] = field(default_factory=list)  # combinator syms
    normal_form: str = ""
    status: str = ""


def _present_combinators(text: str) -> list[str]:
    """Combinator symbols literally present in the program text (appearance order)."""
    seen: list[str] = []
    for tok in text.replace("(", " ").replace(")", " ").split():
        if tok in _ARITY or tok in ("Y", "M"):
            if tok not in seen:
                seen.append(tok)
    return seen


def _certify(text: str) -> tuple[list[str], str, str]:
    """Run the kernel: (fired_seq, normal_form_pretty, status)."""
    t = parse(text)
    red = reduce(t)
    return fired_sequence(t), pretty(red.normal_form), red.status.value


def _saturated_program(comb: str) -> str:
    """Target head applied to exactly `arity` fresh atoms -> fires once."""
    args = " ".join(_ATOMS[: _ARITY[comb]])
    return f"{comb} {args}"


def _inert_program(comb: str) -> str:
    """Target head applied to arity-1 atoms -> under-applied -> normal form, no fire."""
    n = _ARITY[comb] - 1
    args = " ".join(_ATOMS[:n])
    return f"{comb} {args}".strip()


# COMPOSITE multi-fire skeletons (certified order checked at build time). Chosen so the
# fired sequence is unambiguous and spans >=2 distinct combinators for trace-ORDER.
_COMPOSITES = [
    "B K I x y",      # B, K, I
    "C B f x y",      # C then B
    "B (C f) g x y",  # B then C
    "S K K x",        # S then K (the I-by-SKK identity)
    "C K x y z",      # C then K
    "B W f x",        # B then W
    "S B K x y",      # S, then ...
    "W (K x) y",      # W then K
]


def _build() -> list[KernelRefProbe]:
    probes: list[KernelRefProbe] = []
    # single-target saturated⊗inert pairs
    for comb in _ARITY:
        for saturated in (True, False):
            text = _saturated_program(comb) if saturated else _inert_program(comb)
            fired, nf, status = _certify(text)
            tag = "sat" if saturated else "inert"
            probes.append(KernelRefProbe(
                id=f"{comb}_{tag}",
                program_text=text,
                target_combinator=comb,
                saturated=saturated,
                composite=False,
                certified_fired_seq=fired,
                certified_present=_present_combinators(text),
                normal_form=nf,
                status=status,
            ))
    # composite multi-fire programs
    for i, text in enumerate(_COMPOSITES):
        fired, nf, status = _certify(text)
        target = fired[0] if fired else "?"
        probes.append(KernelRefProbe(
            id=f"composite_{i}_{target}",
            program_text=text,
            target_combinator=target,
            saturated=True,
            composite=True,
            certified_fired_seq=fired,
            certified_present=_present_combinators(text),
            normal_form=nf,
            status=status,
        ))
    return probes


_PROBES: tuple[KernelRefProbe, ...] | None = None


def all_probes() -> tuple[KernelRefProbe, ...]:
    """Cached kernel-reference probe set."""
    global _PROBES
    if _PROBES is None:
        _PROBES = tuple(_build())
    return _PROBES


def saturated_probes() -> tuple[KernelRefProbe, ...]:
    return tuple(p for p in all_probes() if p.saturated and not p.composite)


def inert_probes() -> tuple[KernelRefProbe, ...]:
    return tuple(p for p in all_probes() if not p.saturated)


def composite_probes() -> tuple[KernelRefProbe, ...]:
    return tuple(p for p in all_probes() if p.composite)


# ── powered saturated⊗inert battery (P-CTL-6 reader-SNR) ─────────────────────
# The single-target pairs above give n=1 per combinator — enough for the
# original opcode audit (s233), too few for a per-combinator d' SNR estimate.
# This generator emits multiple kernel-certified fresh-atom variants per
# combinator so the reader-SNR instrument can pool within a cell. ADDITIVE:
# it does not touch _build()/all_probes(); the canonical set is unchanged.


def _atom_window(size: int, offset: int) -> list[str]:
    """`size` distinct atoms starting at `offset` (wraps the atom pool)."""
    return [_ATOMS[(offset + i) % len(_ATOMS)] for i in range(size)]


def saturated_inert_battery(n_fillers: int = 4) -> list[KernelRefProbe]:
    """Powered saturated⊗inert battery: up to ``n_fillers`` certified variants
    per combinator, for a per-combinator SNR estimate.

    For each combinator ``c`` (K,I,W,C,B,S,D) emit:
      • SATURATED — ``c`` applied to exactly ``arity(c)`` fresh atoms. All
        fillers are atoms, so the kernel fires ``c`` once at the LAST token
        (the firing site) and reaches normal form: ``fired_seq == [c]``.
      • INERT — ``c`` under-applied by one (``arity-1`` atoms; the bare symbol
        when arity is 1). Symbol present, no redex: ``fired_seq == []``.

    Distinct atom windows give textually distinct programs without accidental
    combinator behaviour. Every returned probe is certified against the kernel
    at build time (a variant that does not meet its fired-sequence contract is
    skipped, never emitted).

    The saturated/inert length differs by one token by construction (that IS
    the specificity control — inert is a normal form). The reader-SNR
    instrument additionally checks target-vs-off-target channel separation to
    rule out a generic length/position effect.
    """
    probes: list[KernelRefProbe] = []
    for comb, arity in _ARITY.items():
        # SATURATED — exactly `arity` fresh-atom slots
        made, offset = 0, 0
        while made < n_fillers and offset < len(_ATOMS):
            text = f"{comb} " + " ".join(_atom_window(arity, offset))
            fired, nf, status = _certify(text)
            offset += 1
            if fired == [comb]:
                probes.append(KernelRefProbe(
                    id=f"{comb}_sat_v{made}",
                    program_text=text,
                    target_combinator=comb,
                    saturated=True,
                    composite=False,
                    certified_fired_seq=fired,
                    certified_present=_present_combinators(text),
                    normal_form=nf,
                    status=status,
                ))
                made += 1
        # INERT — under-applied by one (bare symbol when arity == 1)
        n_slots = arity - 1
        made, offset = 0, 0
        max_offset = len(_ATOMS) if n_slots > 0 else 1
        while made < n_fillers and offset < max_offset:
            args = _atom_window(n_slots, offset) if n_slots > 0 else []
            text = (f"{comb} " + " ".join(args)).strip()
            fired, nf, status = _certify(text)
            offset += 1
            if fired == []:
                probes.append(KernelRefProbe(
                    id=f"{comb}_inert_v{made}",
                    program_text=text,
                    target_combinator=comb,
                    saturated=False,
                    composite=False,
                    certified_fired_seq=fired,
                    certified_present=_present_combinators(text),
                    normal_form=nf,
                    status=status,
                ))
                made += 1
    return probes


# ── position-matched battery (P-CTL-6 v3, s273) ──────────────────────────────
# The saturated/inert pairs above differ in LENGTH (saturation adds a token) —
# a confound that fooled the raw WHNF halt read (length sinks onto the halt
# pole). This battery isolates redex LIVENESS from both symbol-presence AND
# length: the SAME combinator + atoms, combinator in HEAD position (saturated
# redex, fires) vs an ARGUMENT position (normal form, no fire). Same tokens,
# same length, matched last-token read locus (arity >= 2).


def position_battery(n_fillers: int = 4) -> list[KernelRefProbe]:
    """Length- and token-matched minimal pairs (redex vs non-redex position).

    redex:  ``c a1 .. an``       head = c, saturated  -> kernel fires ``[c]``
    inert:  ``a1 .. c .. an``    head = atom, c in arg -> normal form ``[]``
            (c inserted at a non-head slot; for arity >= 2 the last token stays
             an atom, matched to the redex's last atom. Arity 1 is the sole
             edge: ``c a`` vs ``a c`` — last token differs, id-tagged.)

    Only the redex-vs-argument POSITION of ``c`` differs; length and the token
    multiset are identical, so a length/common-mode effect cannot masquerade as
    a liveness signal. Every probe is kernel-certified at build time.
    """
    probes: list[KernelRefProbe] = []
    for comb, arity in _ARITY.items():
        made, offset = 0, 0
        while made < n_fillers and offset < len(_ATOMS):
            atoms = _atom_window(arity, offset)
            offset += 1
            rtext = f"{comb} " + " ".join(atoms)
            rf, rnf, rst = _certify(rtext)
            if rf != [comb]:
                continue
            probes.append(KernelRefProbe(
                id=f"{comb}_redex_v{made}",
                program_text=rtext, target_combinator=comb,
                saturated=True, composite=False,
                certified_fired_seq=rf,
                certified_present=_present_combinators(rtext),
                normal_form=rnf, status=rst,
            ))
            slots = range(1, arity) if arity >= 2 else [1]
            iv = 0
            for j in slots:
                toks = [*atoms[:j], comb, *atoms[j:]]
                itext = " ".join(toks)
                f, nf, st = _certify(itext)
                if f != []:
                    continue
                probes.append(KernelRefProbe(
                    id=f"{comb}_argpos_v{made}_{iv}",
                    program_text=itext, target_combinator=comb,
                    saturated=False, composite=False,
                    certified_fired_seq=f,
                    certified_present=_present_combinators(itext),
                    normal_form=nf, status=st,
                ))
                iv += 1
            made += 1
    return probes


if __name__ == "__main__":
    for p in all_probes():
        kind = "COMPOSITE" if p.composite else ("SAT" if p.saturated else "INERT")
        print(f"[{kind:9}] {p.id:14} {p.program_text:14} "
              f"fired={p.certified_fired_seq} nf={p.normal_form!r} ({p.status})")
