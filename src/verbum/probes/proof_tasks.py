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
    # --- b2 (s247): +23 distinct implicational theorems, each ref auto-solved
    #     (proof_search.solve) and kernel-certified (check_proof == VALID).
    ProofTask("pos_idem_K", "A -> A -> A", True, "K",
              "project the first of two same-typed args (instance of K)"),
    ProofTask("pos_mid3", "A -> B -> C -> B", True, "K K",
              "keep the middle of three"),
    ProofTask("pos_last3", "A -> B -> C -> C", True, "K (K I)",
              "keep the last of three"),
    ProofTask("pos_ignfun", "(A -> B) -> A -> A", True, "K I",
              "ignore the function, return the argument"),
    ProofTask("pos_id2ary", "(A -> B -> C) -> A -> B -> C", True, "I",
              "identity on a 2-ary function type"),
    ProofTask("pos_apply2", "A -> B -> (A -> B -> C) -> C", True, "B C (C I)",
              "supply both arguments to a held 2-ary function"),
    ProofTask("pos_weakdup", "(A -> B) -> (A -> A -> B)", True, "K",
              "weaken into a duplicated argument slot (K)"),
    ProofTask("pos_constfun", "((A -> B) -> C) -> B -> C", True, "C B K",
              "feed a constant function to a higher-order premise"),
    ProofTask("pos_compose2", "(A -> B) -> (C -> D -> A) -> C -> D -> B", True,
              "B B B", "compose under two arguments"),
    ProofTask("pos_precompose", "(A -> B -> C) -> (D -> B) -> A -> D -> C", True,
              "B C (B B)", "pre-compose the second argument"),
    ProofTask("pos_compose3", "(A -> B) -> (B -> C) -> (C -> D) -> A -> D", True,
              "B (B (C B)) (C B)", "triple composition (the hardest chain)"),
    ProofTask("pos_dropfirst", "A -> (B -> C) -> B -> C", True, "K I",
              "discard a leading premise"),
    ProofTask("pos_weak24", "A -> B -> A -> B", True, "K K",
              "weaken twice in a two-atom signature"),
    ProofTask("pos_deepS", "A -> ((A -> B) -> (A -> C)) -> ((A -> B) -> C)", True,
              "C C", "deep S-shape (distribution under a hypothesis)"),
    ProofTask("pos_applyweak", "(A -> B) -> A -> (C -> B)", True, "B K",
              "apply, then weaken the result"),
    ProofTask("pos_thread", "(A -> B -> C) -> A -> (D -> B) -> D -> C", True,
              "B B", "thread the second argument through a converter"),
    ProofTask("pos_first3", "A -> A -> B -> A", True, "B K K",
              "two same-typed copies in, project the first atom"),
    ProofTask("pos_selfapply", "((A -> B) -> A) -> (A -> B) -> B", True, "S I",
              "intuitionistic self-apply — the PROVABLE cousin of Peirce"),
    ProofTask("pos_sprime", "(A -> B) -> (A -> B -> C) -> A -> C", True, "C S",
              "S-prime: share the argument between two functions"),
    ProofTask("pos_threadfwd", "(A -> B -> C) -> (A -> C -> D) -> A -> B -> D",
              True, "C (B S (B B))", "thread a result forward through a 2nd fn"),
    ProofTask("pos_first4", "A -> B -> C -> D -> A", True, "B K (B K K)",
              "keep the first of four"),
    ProofTask("pos_diag", "A -> (A -> A -> B) -> B", True, "S (B C (C I)) I",
              "feed one value to a binary hypothesis twice (diagonal)"),
    ProofTask("pos_midweak", "(A -> B) -> C -> A -> B", True, "K",
              "an unused premise C between a function and its argument"),
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
    # --- b2 (s247): +5 distinct non-theorems (solve -> None; no tempting term proves)
    ProofTask("neg_nodbneg", "((A -> B) -> B) -> ((B -> A) -> A)", False, None,
              "double-negation transfer — no intuitionistic derivation"),
    ProofTask("neg_symm", "(A -> B) -> (B -> A)", False, None,
              "implication is not symmetric"),
    ProofTask("neg_hoatom", "((A -> B) -> C) -> C", False, None,
              "cannot conjure the antecedent function to extract C"),
    ProofTask("neg_converse", "(A -> B) -> B -> A", False, None,
              "the converse — unprovable"),
    ProofTask("neg_conjB", "A -> (A -> B)", False, None,
              "cannot conjure B from A alone"),
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
