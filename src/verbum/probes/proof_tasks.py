r"""Proof-as-inhabitation probes — Curry-Howard theorem proving (session 228).

THE QUESTION. If proof-checking is type-checking and proof normalization is the
continuation (β-reduction → WHNF), can a model PROVE a proposition by emitting a
closed combinator term whose principal type the kernel certifies as the goal?

Each task is a proposition of the implicational fragment of intuitionistic
propositional logic. POSITIVES are theorems, each shipped with a kernel-certifiable
reference proof term over the SOUND basis {S,K,I,B,C,W,D}. NEGATIVES are non-theorems
(no closed simply-typed inhabitant) — they guard the checker against rubber-stamping
and probe whether the prover over-claims.

The basis members ARE the Hilbert axiom schemes (K, S) plus derived theorem
combinators (I, B, C, W, D). The Y-trap negative `(A->A)->A` is special: lambda_ast
TYPES the fixed-point Y as (a→a)→a, so a kernel that admitted recursion would "prove"
it — the sound-basis gate must reject Y. That is the consistency firewall, made into a
test case (y_trap=True).

Accessors: proof_tasks() · positives() · negatives() · by_complexity().

License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "ProofTask",
    "by_complexity",
    "negatives",
    "positives",
    "proof_tasks",
]


@dataclass(frozen=True, slots=True)
class ProofTask:
    id: str
    prop: str             # the proposition (implicational logic, '->' right-assoc)
    provable: bool        # intuitionistic implicational theorem?
    ref_proof: str | None  # kernel-certifiable proof term (positives only)
    note: str
    y_trap: bool = False  # negative that Y would falsely "prove" (consistency demo)

    @property
    def complexity(self) -> int:
        """Implication depth = number of '->' in the proposition."""
        return self.prop.count("->")


# --- POSITIVES: implicational theorems with reference proofs ------------------
# Every ref_proof is verified by the kernel in tests/--mode kernel (the 100% floor).
_POSITIVES: tuple[ProofTask, ...] = (
    ProofTask("pos_I", "A -> A", True, "I",
              "identity — the trivial proof"),
    ProofTask("pos_K", "A -> B -> A", True, "K",
              "the K axiom (weakening)"),
    ProofTask("pos_KI", "A -> B -> B", True, "K I",
              "discard first, keep second"),
    ProofTask("pos_B", "(B -> C) -> (A -> B) -> A -> C", True, "B",
              "→-transitivity / hypothetical syllogism (compose)"),
    ProofTask("pos_compose", "(A -> B) -> (C -> A) -> C -> B", True, "B",
              "function composition, renamed"),
    ProofTask("pos_S", "(A -> B -> C) -> (A -> B) -> A -> C", True, "S",
              "the S axiom (distribution)"),
    ProofTask("pos_C", "(A -> B -> C) -> B -> A -> C", True, "C",
              "premise permutation (flip)"),
    ProofTask("pos_flipcompose", "(A -> B) -> (B -> C) -> A -> C", True, "C B",
              "compose with premises flipped"),
    ProofTask("pos_W", "(A -> A -> B) -> A -> B", True, "W",
              "contraction (duplicate the hypothesis)"),
    ProofTask("pos_apply", "A -> (A -> B) -> B", True, "C I",
              "modus-ponens, subject-first (apply)"),
    ProofTask("pos_funcid", "(A -> B) -> A -> B", True, "I",
              "identity on a function type"),
    ProofTask("pos_const_chain", "A -> B -> C -> A", True, "B K K",
              "weaken twice — keep the first of three"),
)

# --- NEGATIVES: non-theorems (no closed simply-typed inhabitant) --------------
_NEGATIVES: tuple[ProofTask, ...] = (
    ProofTask("neg_atom", "A", False, None,
              "a bare atom — unprovable from nothing"),
    ProofTask("neg_weaken", "A -> B", False, None,
              "cannot conjure B from A"),
    ProofTask("neg_getC", "A -> B -> C", False, None,
              "cannot conjure a third atom"),
    ProofTask("neg_elim", "(A -> B) -> B", False, None,
              "no A in hand to feed the function"),
    ProofTask("neg_retA", "(A -> B) -> A", False, None,
              "cannot extract the antecedent"),
    ProofTask("neg_peirce", "((A -> B) -> A) -> A", False, None,
              "Peirce's law — classical, NOT intuitionistic"),
    ProofTask("neg_dne", "((A -> B) -> B) -> A", False, None,
              "double-negation-elimination shape — not intuitionistic"),
    ProofTask("neg_y_trap", "(A -> A) -> A", False, None,
              "the Y-trap: lambda_ast types Y as (a->a)->a, but this is NOT a "
              "theorem; admitting Y would make the logic inconsistent",
              y_trap=True),
)


def proof_tasks() -> list[ProofTask]:
    return [*_POSITIVES, *_NEGATIVES]


def positives() -> list[ProofTask]:
    return list(_POSITIVES)


def negatives() -> list[ProofTask]:
    return list(_NEGATIVES)


def by_complexity() -> dict[int, int]:
    out: dict[int, int] = {}
    for t in proof_tasks():
        out[t.complexity] = out.get(t.complexity, 0) + 1
    return dict(sorted(out.items()))


if __name__ == "__main__":
    import json
    print(json.dumps({
        "n": len(proof_tasks()),
        "positives": len(_POSITIVES),
        "negatives": len(_NEGATIVES),
        "by_complexity": by_complexity(),
    }, indent=2))
    for t in proof_tasks():
        tag = "+" if t.provable else "-"
        print(f"  [{tag}] {t.id:18} {t.prop:34} ref={t.ref_proof}")
