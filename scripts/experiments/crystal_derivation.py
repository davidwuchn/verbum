#!/usr/bin/env python3
"""
Crystal Derivation from Pure KIBC Combinatory Logic
====================================================

Can we DERIVE the crystal geometry that every LLM converges on,
purely from the mathematics of combinatory logic?

If the crystal is a mathematical constant (Church-Rosser guarantees
unique normal forms), then the eigenstructure of KIBC reduction
should reproduce the empirical crystal without any neural network
or training data.

Three analyses:
1. Combinator2vec: co-occurrence of combinators in normal forms
2. Transition matrix: Markov chain of head combinators during reduction
3. Full 8-vertex crystal: extending to D, Y, W, WHNF compounds

Empirical targets (from crystal-universality.md, sessions 139-157):
  Eigenvalues: [5.193, 3.535, 1.909, 1.300]
  λ₀/λ₁ = 1.469
  PC0 = composition (B,C,D,W,Y cluster)
  PC1 = selection (K,I cluster)
  PC2 = termination (WHNF)
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional
from enum import Enum, auto
from itertools import product
import time


# ============================================================
# 1. Expression Representation
# ============================================================

class Atom(Enum):
    """The four primitive combinators."""
    K = auto()  # K x y → x         (select first, discard second)
    I = auto()  # I x → x           (identity)
    B = auto()  # B f g x → f(g(x)) (compose)
    C = auto()  # C f x y → f(y)(x) (flip argument order)


@dataclass(frozen=True)
class Expr:
    """An expression in combinatory logic.

    Either an atom (K, I, B, C) or an application (left @ right).
    Immutable for safe reduction.
    """
    atom: Optional[Atom] = None
    left: Optional['Expr'] = None
    right: Optional['Expr'] = None

    def __post_init__(self):
        if self.atom is not None:
            assert self.left is None and self.right is None
        else:
            assert self.left is not None and self.right is not None

    @property
    def is_atom(self) -> bool:
        return self.atom is not None

    @property
    def is_app(self) -> bool:
        return not self.is_atom

    @property
    def size(self) -> int:
        """Count of atoms in the expression."""
        if self.is_atom:
            return 1
        return self.left.size + self.right.size

    @property
    def depth(self) -> int:
        """Nesting depth."""
        if self.is_atom:
            return 0
        return 1 + max(self.left.depth, self.right.depth)

    def __repr__(self):
        if self.is_atom:
            return self.atom.name
        # Left-associate applications: (f x) y prints as f x y
        if self.left.is_app:
            return f"({self.left} {self.right})"
        return f"({self.left} {self.right})"

    def __hash__(self):
        if self.is_atom:
            return hash(('atom', self.atom))
        return hash(('app', self.left, self.right))


# Convenience constructors
K = Expr(atom=Atom.K)
I = Expr(atom=Atom.I)
B = Expr(atom=Atom.B)
C = Expr(atom=Atom.C)
ATOMS = [K, I, B, C]

def App(f, x):
    """Application: f applied to x."""
    return Expr(left=f, right=x)


# ============================================================
# 2. Beta Reducer
# ============================================================

MAX_STEPS = 500
MAX_SIZE = 200  # Prevent size explosion


def spine(expr: Expr) -> tuple[list[Expr], Expr]:
    """Unwind the application spine.

    (((f x₁) x₂) x₃) → ([x₁, x₂, x₃], f)
    Returns (args, head) where args are in application order.
    """
    args = []
    while expr.is_app:
        args.append(expr.right)
        expr = expr.left
    args.reverse()
    return args, expr


def rebuild(head: Expr, args: list[Expr]) -> Expr:
    """Rebuild application spine from head and args."""
    result = head
    for arg in args:
        result = App(result, arg)
    return result


def reduce_head_once(expr: Expr) -> tuple[Optional[Expr], Optional[Atom]]:
    """Try one head reduction step.

    Returns (reduced_expr, head_combinator_that_fired) or (None, None)
    if no reduction is possible.
    """
    args, head = spine(expr)

    if not head.is_atom:
        return None, None

    combinator = head.atom

    # K x y → x
    if combinator == Atom.K and len(args) >= 2:
        x, y = args[0], args[1]
        rest = args[2:]
        return rebuild(x, rest), Atom.K

    # I x → x
    if combinator == Atom.I and len(args) >= 1:
        x = args[0]
        rest = args[1:]
        return rebuild(x, rest), Atom.I

    # B f g x → f (g x)
    if combinator == Atom.B and len(args) >= 3:
        f, g, x = args[0], args[1], args[2]
        rest = args[3:]
        result = App(f, App(g, x))
        return rebuild(result, rest), Atom.B

    # C f x y → f y x
    if combinator == Atom.C and len(args) >= 3:
        f, x, y = args[0], args[1], args[2]
        rest = args[3:]
        result = App(App(f, y), x)
        return rebuild(result, rest), Atom.C

    return None, None


@dataclass
class ReductionTrace:
    """Record of a complete reduction sequence."""
    original: Expr
    normal_form: Optional[Expr]
    steps: int
    head_sequence: list[Atom]  # Which combinator fired at each step
    diverged: bool
    size_exceeded: bool


def reduce_to_normal_form(expr: Expr) -> ReductionTrace:
    """Reduce an expression to head normal form, recording the trace.

    Head normal form: the head is a combinator with fewer args than it needs.
    We also reduce arguments (weak head normal form first, then args).
    """
    head_sequence = []
    steps = 0
    current = expr

    # Phase 1: Head reduction (WHNF)
    while steps < MAX_STEPS:
        if current.size > MAX_SIZE:
            return ReductionTrace(
                original=expr,
                normal_form=None,
                steps=steps,
                head_sequence=head_sequence,
                diverged=False,
                size_exceeded=True,
            )

        reduced, fired = reduce_head_once(current)
        if reduced is None:
            break  # Head normal form reached
        current = reduced
        head_sequence.append(fired)
        steps += 1

    if steps >= MAX_STEPS:
        return ReductionTrace(
            original=expr,
            normal_form=None,
            steps=steps,
            head_sequence=head_sequence,
            diverged=True,
            size_exceeded=False,
        )

    # Phase 2: Reduce arguments (full normal form)
    current = reduce_args(current, MAX_STEPS - steps, head_sequence)

    return ReductionTrace(
        original=expr,
        normal_form=current,
        steps=len(head_sequence),
        head_sequence=head_sequence,
        diverged=False,
        size_exceeded=False,
    )


def reduce_args(expr: Expr, budget: int, trace: list[Atom]) -> Expr:
    """Reduce arguments of a head-normal expression."""
    if expr.is_atom or budget <= 0:
        return expr

    # Try to reduce the subexpressions
    new_left = reduce_subexpr(expr.left, budget, trace)
    remaining = budget - (len(trace))
    new_right = reduce_subexpr(expr.right, remaining, trace)

    return Expr(left=new_left, right=new_right)


def reduce_subexpr(expr: Expr, budget: int, trace: list[Atom]) -> Expr:
    """Reduce a subexpression to normal form."""
    if budget <= 0:
        return expr

    steps = 0
    current = expr
    while steps < budget:
        reduced, fired = reduce_head_once(current)
        if reduced is None:
            break
        if reduced.size > MAX_SIZE:
            break
        current = reduced
        trace.append(fired)
        steps += 1

    # Recurse into arguments
    if current.is_app:
        new_left = reduce_subexpr(current.left, budget - steps, trace)
        new_right = reduce_subexpr(current.right, budget - steps, trace)
        current = Expr(left=new_left, right=new_right)

    return current


# ============================================================
# 3. Expression Enumerator
# ============================================================

def enumerate_expressions(max_size: int) -> dict[int, list[Expr]]:
    """Enumerate all KIBC expressions up to a given size.

    Size = number of atoms.
    Size 1: K, I, B, C (4 expressions)
    Size 2: all pairs X Y (16 expressions)
    Size N: all binary trees with N leaves from {K,I,B,C}

    Uses dynamic programming: expressions of size N are all
    (expr_of_size_a) applied to (expr_of_size_b) where a+b=N.
    """
    by_size: dict[int, list[Expr]] = {}

    # Size 1: atoms
    by_size[1] = list(ATOMS)

    for n in range(2, max_size + 1):
        exprs = []
        # Partition n into (a, b) where a + b = n, a >= 1, b >= 1
        for a in range(1, n):
            b = n - a
            for left in by_size[a]:
                for right in by_size[b]:
                    exprs.append(App(left, right))
        by_size[n] = exprs

    return by_size


# ============================================================
# 4. Analysis: Co-occurrence and Transition Matrices
# ============================================================

def collect_atom_occurrences(expr: Expr) -> list[Atom]:
    """Collect all atoms in an expression (DFS order)."""
    if expr.is_atom:
        return [expr.atom]
    return collect_atom_occurrences(expr.left) + collect_atom_occurrences(expr.right)


def head_combinator(expr: Expr) -> Optional[Atom]:
    """Get the head combinator of an expression."""
    _, head = spine(expr)
    if head.is_atom:
        return head.atom
    return None


def build_matrices(traces: list[ReductionTrace]) -> dict:
    """Build co-occurrence and transition matrices from reduction traces.

    Returns dict with:
      'cooccurrence': 4×4 matrix of combinator co-occurrence in normal forms
      'transition':   4×4 matrix of head-combinator transitions during reduction
      'head_freq':    4-vector of head combinator frequencies in normal forms
      'nf_freq':      4-vector of combinator frequencies in normal forms (all positions)
      'trace_counts': total transitions recorded
    """
    n = len(Atom)  # 4
    atom_idx = {a: i for i, a in enumerate(Atom)}

    cooccurrence = np.zeros((n, n), dtype=np.float64)
    transition = np.zeros((n, n), dtype=np.float64)
    head_freq = np.zeros(n, dtype=np.float64)
    nf_freq = np.zeros(n, dtype=np.float64)
    trace_count = 0

    for tr in traces:
        if tr.diverged or tr.size_exceeded or tr.normal_form is None:
            continue

        # Co-occurrence in normal form
        atoms = collect_atom_occurrences(tr.normal_form)
        for a in atoms:
            nf_freq[atom_idx[a]] += 1
        for i, a in enumerate(atoms):
            for b in atoms[i+1:]:
                cooccurrence[atom_idx[a], atom_idx[b]] += 1
                cooccurrence[atom_idx[b], atom_idx[a]] += 1
            # Self-co-occurrence (diagonal)
            cooccurrence[atom_idx[a], atom_idx[a]] += 1

        # Head combinator in normal form
        hc = head_combinator(tr.normal_form)
        if hc is not None:
            head_freq[atom_idx[hc]] += 1

        # Transition matrix from reduction trace
        for i in range(len(tr.head_sequence) - 1):
            src = atom_idx[tr.head_sequence[i]]
            dst = atom_idx[tr.head_sequence[i + 1]]
            transition[src, dst] += 1
            trace_count += 1

    # Normalize transition matrix (row-stochastic)
    row_sums = transition.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # Avoid division by zero
    transition_norm = transition / row_sums

    # Normalize frequencies
    total_nf = nf_freq.sum()
    if total_nf > 0:
        nf_freq_norm = nf_freq / total_nf
    else:
        nf_freq_norm = nf_freq

    total_head = head_freq.sum()
    if total_head > 0:
        head_freq_norm = head_freq / total_head
    else:
        head_freq_norm = head_freq

    return {
        'cooccurrence': cooccurrence,
        'transition_raw': transition,
        'transition': transition_norm,
        'head_freq': head_freq_norm,
        'head_freq_raw': head_freq,
        'nf_freq': nf_freq_norm,
        'nf_freq_raw': nf_freq,
        'trace_count': trace_count,
    }


# ============================================================
# 5. Eigenanalysis and Crystal Comparison
# ============================================================

# Empirical values from crystal-universality.md
EMPIRICAL_EIGENVALUES = np.array([5.193, 3.535, 1.909, 1.300])
EMPIRICAL_RATIO_01 = 5.193 / 3.535  # 1.469

COMBINATOR_NAMES = ['K', 'I', 'B', 'C']


def analyze_matrix(matrix: np.ndarray, name: str) -> dict:
    """Eigendecompose a matrix and compare to empirical crystal."""
    eigenvalues, eigenvectors = np.linalg.eig(matrix)

    # Sort by magnitude (descending)
    idx = np.argsort(-np.abs(eigenvalues))
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Take real parts (transition matrix may have complex eigenvalues)
    eigenvalues_real = np.real(eigenvalues)
    eigenvectors_real = np.real(eigenvectors)

    # Compute ratios
    if np.abs(eigenvalues_real[1]) > 1e-10:
        ratio_01 = np.abs(eigenvalues_real[0]) / np.abs(eigenvalues_real[1])
    else:
        ratio_01 = float('inf')

    # Normalize eigenvalues to match empirical scale
    if np.abs(eigenvalues_real[0]) > 1e-10:
        scale = EMPIRICAL_EIGENVALUES[0] / np.abs(eigenvalues_real[0])
        scaled = np.abs(eigenvalues_real) * scale
    else:
        scaled = np.abs(eigenvalues_real)

    return {
        'name': name,
        'eigenvalues': eigenvalues_real,
        'eigenvalues_abs': np.abs(eigenvalues_real),
        'eigenvectors': eigenvectors_real,
        'ratio_01': ratio_01,
        'empirical_ratio_01': EMPIRICAL_RATIO_01,
        'ratio_match': abs(ratio_01 - EMPIRICAL_RATIO_01) / EMPIRICAL_RATIO_01,
        'scaled_eigenvalues': scaled,
        'empirical_eigenvalues': EMPIRICAL_EIGENVALUES,
    }


def print_analysis(analysis: dict):
    """Pretty-print eigenanalysis results."""
    print(f"\n{'='*60}")
    print(f"  {analysis['name']}")
    print(f"{'='*60}")

    print(f"\n  Eigenvalues (raw):   {analysis['eigenvalues']}")
    print(f"  Eigenvalues (|abs|): {analysis['eigenvalues_abs']}")
    print(f"  λ₀/λ₁ ratio:        {analysis['ratio_01']:.4f}")
    print(f"  Empirical λ₀/λ₁:    {analysis['empirical_ratio_01']:.4f}")
    print(f"  Ratio match error:   {analysis['ratio_match']*100:.2f}%")

    print(f"\n  Scaled to empirical λ₀:")
    print(f"    Derived:   {analysis['scaled_eigenvalues'][:4]}")
    print(f"    Empirical: {analysis['empirical_eigenvalues']}")

    if len(analysis['eigenvalues']) >= 4:
        rel_errors = np.abs(analysis['scaled_eigenvalues'][:4] - EMPIRICAL_EIGENVALUES) / EMPIRICAL_EIGENVALUES
        print(f"    Rel error: {rel_errors}")
        print(f"    Mean error: {rel_errors.mean()*100:.2f}%")

    print(f"\n  Eigenvectors (columns = PCs, rows = {COMBINATOR_NAMES}):")
    ev = analysis['eigenvectors']
    for i, name in enumerate(COMBINATOR_NAMES):
        vals = '  '.join(f"{ev[i,j]:+.4f}" for j in range(min(4, ev.shape[1])))
        print(f"    {name}: {vals}")

    # Check clustering: do B,C cluster together? Do K,I cluster?
    if ev.shape[1] >= 2:
        print(f"\n  Cluster analysis (PC0):")
        pc0 = ev[:, 0]
        bc_mean = (pc0[2] + pc0[3]) / 2  # B, C
        ki_mean = (pc0[0] + pc0[1]) / 2  # K, I
        print(f"    B,C mean: {bc_mean:+.4f}")
        print(f"    K,I mean: {ki_mean:+.4f}")
        if abs(bc_mean - ki_mean) > 0.01:
            print(f"    Separation: {abs(bc_mean - ki_mean):.4f} ({'composition/selection SPLIT' if bc_mean != ki_mean else 'no split'})")
        else:
            print(f"    No composition/selection split in PC0")


# ============================================================
# 6. Main: Run the Experiment
# ============================================================

def run_experiment(max_size: int = 7):
    """Run the full crystal derivation experiment."""

    print("╔══════════════════════════════════════════════════════════╗")
    print("║  CRYSTAL DERIVATION FROM PURE KIBC COMBINATORY LOGIC   ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print("║  Can we derive the crystal geometry that every LLM     ║")
    print("║  converges on, purely from the mathematics?            ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # --- Sanity check: basic reductions ---
    print("\n" + "─"*60)
    print("  SANITY CHECKS")
    print("─"*60)

    tests = [
        (App(I, K), "I K → K"),
        (App(App(K, I), B), "K I B → I"),
        (App(App(App(B, K), I), C), "B K I C → K(I C) → I C → C"),
        (App(App(App(C, K), I), B), "C K I B → K B I → B"),
        (App(I, I), "I I → I"),
    ]

    for expr, description in tests:
        trace = reduce_to_normal_form(expr)
        nf = trace.normal_form
        fired = [a.name for a in trace.head_sequence]
        print(f"  {description}")
        print(f"    Result: {nf}  |  Steps: {trace.steps}  |  Fired: {' → '.join(fired)}")

    # --- Enumerate expressions ---
    print("\n" + "─"*60)
    print("  ENUMERATION")
    print("─"*60)

    t0 = time.time()
    by_size = enumerate_expressions(max_size)
    t_enum = time.time() - t0

    total = 0
    for size in sorted(by_size.keys()):
        n = len(by_size[size])
        total += n
        print(f"  Size {size}: {n:>8,} expressions")
    print(f"  Total:  {total:>8,} expressions")
    print(f"  Enumeration time: {t_enum:.2f}s")

    # --- Reduce all expressions ---
    print("\n" + "─"*60)
    print("  REDUCTION")
    print("─"*60)

    all_traces = []
    stats = {'normal': 0, 'diverged': 0, 'size_exceeded': 0}

    t0 = time.time()
    for size in sorted(by_size.keys()):
        size_traces = []
        for expr in by_size[size]:
            trace = reduce_to_normal_form(expr)
            size_traces.append(trace)
            if trace.diverged:
                stats['diverged'] += 1
            elif trace.size_exceeded:
                stats['size_exceeded'] += 1
            else:
                stats['normal'] += 1
        all_traces.extend(size_traces)

        # Progress
        n_done = len(all_traces)
        print(f"  Size {size}: {len(size_traces):>6,} reduced  "
              f"({stats['normal']} normal, {stats['diverged']} diverged, "
              f"{stats['size_exceeded']} size-exceeded)")

    t_reduce = time.time() - t0
    print(f"  Reduction time: {t_reduce:.2f}s")

    # --- Reduction statistics ---
    print("\n" + "─"*60)
    print("  REDUCTION STATISTICS")
    print("─"*60)

    normal_traces = [t for t in all_traces if not t.diverged and not t.size_exceeded and t.normal_form is not None]
    if normal_traces:
        steps = [t.steps for t in normal_traces]
        print(f"  Normal forms found: {len(normal_traces)}")
        print(f"  Steps — min: {min(steps)}, max: {max(steps)}, "
              f"mean: {np.mean(steps):.2f}, median: {np.median(steps):.1f}")

        # Distribution of head combinators that fired
        fire_counts = {a: 0 for a in Atom}
        for t in normal_traces:
            for a in t.head_sequence:
                fire_counts[a] += 1
        total_fires = sum(fire_counts.values())
        print(f"\n  Head combinator firing frequency:")
        for a in Atom:
            pct = fire_counts[a] / total_fires * 100 if total_fires > 0 else 0
            bar = '█' * int(pct / 2)
            print(f"    {a.name}: {fire_counts[a]:>8,} ({pct:5.1f}%)  {bar}")

        # Distribution of head combinators in normal forms
        head_counts = {a: 0 for a in Atom}
        headless = 0
        for t in normal_traces:
            hc = head_combinator(t.normal_form)
            if hc is not None:
                head_counts[hc] += 1
            else:
                headless += 1
        print(f"\n  Head combinator in normal forms:")
        for a in Atom:
            pct = head_counts[a] / len(normal_traces) * 100
            bar = '█' * int(pct / 2)
            print(f"    {a.name}: {head_counts[a]:>8,} ({pct:5.1f}%)  {bar}")
        if headless:
            print(f"    (no atom head): {headless}")

        # Normal form size distribution
        nf_sizes = [t.normal_form.size for t in normal_traces]
        print(f"\n  Normal form sizes — min: {min(nf_sizes)}, max: {max(nf_sizes)}, "
              f"mean: {np.mean(nf_sizes):.2f}")

    # --- Build matrices ---
    print("\n" + "─"*60)
    print("  MATRIX CONSTRUCTION")
    print("─"*60)

    matrices = build_matrices(normal_traces)

    print(f"\n  Co-occurrence matrix (combinator × combinator in normal forms):")
    print(f"         {'    '.join(COMBINATOR_NAMES)}")
    for i, name in enumerate(COMBINATOR_NAMES):
        vals = '  '.join(f"{matrices['cooccurrence'][i,j]:7.0f}" for j in range(4))
        print(f"    {name}: {vals}")

    print(f"\n  Transition matrix (row=from, col=to during reduction):")
    print(f"         {'    '.join(COMBINATOR_NAMES)}")
    for i, name in enumerate(COMBINATOR_NAMES):
        vals = '  '.join(f"{matrices['transition'][i,j]:7.4f}" for j in range(4))
        print(f"    {name}: {vals}")

    print(f"\n  Head frequency in normal forms: {dict(zip(COMBINATOR_NAMES, matrices['head_freq']))}")
    print(f"  Atom frequency in normal forms: {dict(zip(COMBINATOR_NAMES, matrices['nf_freq']))}")
    print(f"  Total transitions recorded: {matrices['trace_count']}")

    # --- Eigenanalysis ---
    print("\n" + "─"*60)
    print("  EIGENANALYSIS")
    print("─"*60)

    # Analyze transition matrix
    trans_analysis = analyze_matrix(matrices['transition'], "Transition Matrix T (Markov chain)")
    print_analysis(trans_analysis)

    # Analyze co-occurrence matrix
    cooc_analysis = analyze_matrix(matrices['cooccurrence'], "Co-occurrence Matrix (combinator2vec)")
    print_analysis(cooc_analysis)

    # Analyze symmetric co-occurrence (guaranteed real eigenvalues)
    sym_cooc = (matrices['cooccurrence'] + matrices['cooccurrence'].T) / 2
    sym_analysis = analyze_matrix(sym_cooc, "Symmetric Co-occurrence")
    print_analysis(sym_analysis)

    # --- Convergence analysis: eigenvalues by expression size ---
    print("\n" + "─"*60)
    print("  CONVERGENCE BY EXPRESSION SIZE")
    print("─"*60)
    print(f"\n  Do eigenvalue ratios stabilize as expression size grows?")
    print(f"  (If they converge, the crystal IS a mathematical constant)")
    print(f"\n  {'Size':>4}  {'λ₀/λ₁':>8}  {'Target':>8}  {'Error':>8}  {'Traces':>8}")
    print(f"  {'─'*4}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}")

    cumulative_traces = []
    for size in sorted(by_size.keys()):
        size_traces = [t for t in all_traces
                       if t.original.size == size
                       and not t.diverged
                       and not t.size_exceeded
                       and t.normal_form is not None]
        cumulative_traces.extend(size_traces)

        if len(cumulative_traces) < 10:
            continue

        m = build_matrices(cumulative_traces)

        # Use co-occurrence for convergence
        evals, _ = np.linalg.eig(m['cooccurrence'])
        evals = np.sort(np.abs(np.real(evals)))[::-1]

        if len(evals) >= 2 and evals[1] > 1e-10:
            ratio = evals[0] / evals[1]
            error = abs(ratio - EMPIRICAL_RATIO_01) / EMPIRICAL_RATIO_01 * 100
            print(f"  {size:>4}  {ratio:>8.4f}  {EMPIRICAL_RATIO_01:>8.4f}  {error:>7.2f}%  {len(cumulative_traces):>8,}")

    # --- Summary ---
    print("\n" + "═"*60)
    print("  SUMMARY")
    print("═"*60)

    best_ratio = trans_analysis['ratio_01']
    best_error = trans_analysis['ratio_match'] * 100
    print(f"\n  Transition matrix λ₀/λ₁: {best_ratio:.4f} (target: {EMPIRICAL_RATIO_01:.4f}, error: {best_error:.1f}%)")

    best_ratio_c = cooc_analysis['ratio_01']
    best_error_c = cooc_analysis['ratio_match'] * 100
    print(f"  Co-occurrence λ₀/λ₁:     {best_ratio_c:.4f} (target: {EMPIRICAL_RATIO_01:.4f}, error: {best_error_c:.1f}%)")

    # Check eigenvector structure
    ev = cooc_analysis['eigenvectors']
    if ev.shape[1] >= 2:
        pc0 = ev[:, 0]
        # Do B and C load similarly on PC0? Do K and I?
        bc_sim = 1 - abs(pc0[2] - pc0[3]) / (abs(pc0[2]) + abs(pc0[3]) + 1e-10)
        ki_sim = 1 - abs(pc0[0] - pc0[1]) / (abs(pc0[0]) + abs(pc0[1]) + 1e-10)
        bc_ki_sep = abs((pc0[2] + pc0[3])/2 - (pc0[0] + pc0[1])/2)

        print(f"\n  Eigenvector structure (co-occurrence PC0):")
        print(f"    B-C similarity:     {bc_sim:.4f} (1.0 = identical loading)")
        print(f"    K-I similarity:     {ki_sim:.4f} (1.0 = identical loading)")
        print(f"    (B,C)-(K,I) sep:    {bc_ki_sep:.4f} (>0 = composition/selection split)")

    print(f"\n  Total expressions:     {total:,}")
    print(f"  Normal forms:          {len(normal_traces):,}")
    print(f"  Diverged:              {stats['diverged']:,}")
    print(f"  Size exceeded:         {stats['size_exceeded']:,}")
    print(f"  Time (enum+reduce):    {t_enum + t_reduce:.2f}s")

    return {
        'matrices': matrices,
        'analyses': {
            'transition': trans_analysis,
            'cooccurrence': cooc_analysis,
            'symmetric': sym_analysis,
        },
        'traces': normal_traces,
        'stats': stats,
    }


if __name__ == '__main__':
    import sys
    max_size = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    results = run_experiment(max_size)
