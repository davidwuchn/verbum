r"""Scratch generator (b2): certify candidate implicational theorems for the expanded
proof probe set. Proposes props, auto-solves (proof_search.solve), reconstructs the
combinator term (bracket abstraction), and kernel-verifies (check_proof). Prints a
curation table. NOT a committed experiment — a one-shot authoring aid.

Run: uv run python scripts/experiments/_gen_proof_tasks.py
"""

from __future__ import annotations

from verbum.lambda_ast import pretty
from verbum.proof_kernel import check_proof
from verbum.proof_search import reconstruct, solve

# Candidate NEW positive theorems (distinct from the existing 12). Natural
# implicational tautologies spanning complexity; the solver finds a certified term.
POS_CANDIDATES: list[tuple[str, str]] = [
    ("A -> A -> A", "either-projection at one atom (instance of K)"),
    ("A -> B -> C -> B", "keep the middle of three"),
    ("A -> B -> C -> C", "keep the last of three"),
    ("(A -> B) -> A -> A", "ignore the function, return the argument"),
    ("(A -> B -> C) -> A -> B -> C", "identity on a 2-ary function type"),
    ("A -> B -> (A -> B -> C) -> C", "supply both args to a held function"),
    ("(A -> B) -> (A -> A -> B)", "duplicate the argument slot"),
    ("((A -> B) -> C) -> B -> C", "feed a constant function"),
    ("(A -> B) -> (C -> D -> A) -> C -> D -> B", "compose under two arguments"),
    ("(A -> B -> C) -> (D -> B) -> A -> D -> C", "pre-compose the second argument"),
    ("(A -> B) -> (B -> C) -> (C -> D) -> A -> D", "triple composition"),
    ("A -> (B -> C) -> B -> C", "discard a leading premise"),
    ("(A -> B -> C) -> B -> A -> C", "flip (C, re-stated)"),
    ("(A -> B) -> (C -> A) -> (C -> B)", "compose on the right (B, re-stated)"),
    ("A -> B -> A -> B", "K-weaken then identity-ish (project 2nd & 4th-shape)"),
    ("(A -> B -> C) -> (A -> B) -> (A -> C)", "S, re-stated fully parenthesised"),
    ("A -> ((A -> B) -> (A -> C)) -> ((A -> B) -> C)", "deep S-shape"),
    ("(A -> B) -> A -> (C -> B)", "apply then weaken the result"),
    ("(A -> B -> C) -> A -> (D -> B) -> D -> C", "thread through a converter"),
    ("A -> A -> B -> A", "two copies in, project the first atom"),
    ("(B -> C) -> (A -> B) -> A -> C", "B, re-stated"),
    ("A -> B -> C -> A", "keep the first of three (re-stated, ref B K K)"),
    ("((A -> B) -> A) -> (A -> B) -> B", "self-apply (intuitionistic, not Peirce)"),
    ("(A -> B) -> (A -> B -> C) -> A -> C", "S-prime: share the argument"),
    ("(A -> B -> C) -> (A -> C -> D) -> A -> B -> D", "thread a result forward"),
    ("A -> B -> C -> D -> A", "keep the first of four"),
    ("A -> (A -> A -> B) -> B", "feed one value to a binary hypothesis twice"),
    ("(A -> B) -> C -> A -> B", "insert an unused premise in the middle"),
    ("(A -> B -> C) -> (B -> A -> C)", "flip fully parenthesised tail"),
]

# Candidate negatives — must be genuine non-theorems (solve -> None). The first
# group are the existing/classical traps; the rest extend the failure surface.
NEG_CANDIDATES: list[tuple[str, str]] = [
    ("((A -> B) -> A) -> A", "Peirce — classical, not intuitionistic"),
    ("((A -> B) -> B) -> A", "DNE shape"),
    ("(A -> A) -> A", "the Y-trap (consistency firewall)"),
    ("((A -> B) -> B) -> ((B -> A) -> A)", "no intuitionistic derivation"),
    ("(A -> B) -> (B -> A)", "implication is not symmetric"),
    ("((A -> B) -> C) -> C", "cannot conjure the antecedent function"),
    ("(A -> B) -> B -> A", "converse — unprovable"),
    ("A -> (A -> B)", "cannot conjure B"),
]


def main() -> None:
    print("=== POSITIVE CANDIDATES (auto-solve + kernel-certify) ===")
    certified: list[tuple[str, str, str]] = []
    for prop, note in POS_CANDIDATES:
        st = solve(prop)
        if st is None:
            print(f"  [UNSOLVED] {prop:55} (solver found none)")
            continue
        term = pretty(reconstruct(st))
        chk = check_proof(term, prop)
        ok = "VALID" if chk.valid else chk.verdict
        depth = prop.count("->")
        print(f"  [{ok:13}] d={depth} {prop:52} -> {term:18} | {note}")
        if chk.valid:
            certified.append((prop, term, note))

    print(f"\n  {len(certified)}/{len(POS_CANDIDATES)} positives certified")

    print("\n=== NEGATIVE CANDIDATES (must be UNSOLVED + tempting terms rejected) ===")
    good_negs: list[tuple[str, str]] = []
    tempting = ["I", "K", "S", "C", "B", "W", "K I", "C I", "C B", "S I I",
                "B K K", "S K K", "K K"]
    for prop, note in NEG_CANDIDATES:
        st = solve(prop)
        solved = st is not None
        # also confirm no tempting closed term proves it
        bluffed = [t for t in tempting if check_proof(t, prop).valid]
        status = "THEOREM!" if solved else ("BLUFFED" if bluffed else "ok-nonthm")
        extra = f" solver={pretty(reconstruct(st))}" if solved else (
            f" bluff={bluffed}" if bluffed else "")
        print(f"  [{status:9}] {prop:48} | {note}{extra}")
        if not solved and not bluffed:
            good_negs.append((prop, note))

    print(f"\n  {len(good_negs)}/{len(NEG_CANDIDATES)} negatives clean")

    # Emit ready-to-paste ProofTask tuples for the certified set
    print("\n=== READY-TO-PASTE (certified positives) ===")
    for i, (prop, term, note) in enumerate(certified):
        pid = f"pos_x{i:02d}"
        print(f'    ProofTask("{pid}", "{prop}", True, "{term}",\n'
              f'              "{note}"),')
    print("\n=== READY-TO-PASTE (clean negatives) ===")
    for i, (prop, note) in enumerate(good_negs):
        pid = f"neg_x{i:02d}"
        yt = ", y_trap=True" if "Y-trap" in note else ""
        print(f'    ProofTask("{pid}", "{prop}", False, None,\n'
              f'              "{note}"{yt}),')


if __name__ == "__main__":
    main()
