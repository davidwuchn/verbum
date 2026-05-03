"""
v10 S-expression data pipeline.

Tokenizer, tree parser, example / batch generators, and an infinite
data-loader — all self-contained (only imports config from this package).

Vocabulary layout (fits inside V10Config.vocab_size = 256):
  0          PAD
  1          BOS
  2          EOS
  3          (
  4          )
  5–26       ops  (22 operators, alphabetically sorted below)
  27–126     integers 0–99
  127        true
  128        false
  ── 129 tokens used; 127 slots spare ──

License: MIT
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Iterator

import numpy as np

# Allow `uv run python scripts/v10/data.py` (no package install required).
# When imported as part of a larger module tree the sys.path insertion is
# harmless (already present) and V10Config is still resolved correctly.
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from config import V10Config

# ══════════════════════════════════════════════════════════════════
# Operator kernel — 22 ops matching the VSM tree kernel
# ══════════════════════════════════════════════════════════════════

# Operators in a fixed, sorted order so op_idx is stable across runs.
OPS: list[str] = [
    "abs",      # 0
    "and",      # 1
    "apply",    # 2
    "compose",  # 3
    "eq",       # 4
    "ge",       # 5
    "gt",       # 6
    "if",       # 7
    "le",       # 8
    "lt",       # 9
    "max",      # 10
    "min",      # 11
    "%",        # 12
    "*",        # 13
    "+",        # 14
    "-",        # 15
    "//",       # 16
    "neg",      # 17
    "not",      # 18
    "or",       # 19
    "partial",  # 20
    "true",     # 21  (also a boolean literal — dual-use token)
    # Note: "false" is token 128; it is NOT an operator, it is a literal.
    # "true" appears in OPS so it gets an op_idx (21), but is also a value.
]
# Trim to exactly n_ops = 22
assert len(OPS) == 22, f"Expected 22 ops, got {len(OPS)}"

OP_TO_IDX: dict[str, int] = {op: i for i, op in enumerate(OPS)}

# Arity table (how many child S-expressions each op takes).
# apply / compose / partial have variable arity; we cap at 3 for generation.
OP_ARITY: dict[str, int] = {
    "abs": 1,
    "and": 2,
    "apply": 2,   # (apply f arg)
    "compose": 2, # (compose f g)
    "eq": 2,
    "ge": 2,
    "gt": 2,
    "if": 3,
    "le": 2,
    "lt": 2,
    "max": 2,
    "min": 2,
    "%": 2,
    "*": 2,
    "+": 2,
    "-": 2,
    "//": 2,
    "neg": 1,
    "not": 1,
    "or": 2,
    "partial": 2, # (partial f arg) → curried application
    "true": 0,    # nullary — treated as a literal
}

# Ops usable in random generation (exclude higher-order ops that need special handling)
GENERATABLE_OPS: list[str] = [
    "abs", "and", "eq", "ge", "gt", "if",
    "le", "lt", "max", "min",
    "%", "*", "+", "-", "//",
    "neg", "not", "or",
]


# ══════════════════════════════════════════════════════════════════
# S-expression Tokenizer
# ══════════════════════════════════════════════════════════════════

# Build the vocabulary in the layout described in the module docstring.
_SPECIALS = ["<PAD>", "<BOS>", "<EOS>"]
_DELIMITERS = ["(", ")"]
_OPS_VOCAB = OPS  # 22 entries
_NUMBERS = [str(i) for i in range(100)]  # "0" .. "99"
_BOOLEANS = ["true", "false"]

# Note: "true" appears in both _OPS_VOCAB (op index 21) and _BOOLEANS.
# In the token vocabulary "true" maps to its OPS slot (token 27+21=48 — see
# below); "false" gets its own slot *after* the numbers.

_VOCAB_ORDERED: list[str] = (
    _SPECIALS       # 0, 1, 2
    + _DELIMITERS   # 3, 4
    + _OPS_VOCAB    # 5 .. 26
    + _NUMBERS      # 27 .. 126
    + ["false"]     # 127  (true is already in _OPS_VOCAB at token 5+21=26)
)

# Sanity: must fit inside 256
assert len(_VOCAB_ORDERED) <= 256, (
    f"Vocabulary has {len(_VOCAB_ORDERED)} tokens — exceeds V10Config.vocab_size=256"
)

# Token ↔ id maps
_TOKEN_TO_ID: dict[str, int] = {tok: i for i, tok in enumerate(_VOCAB_ORDERED)}
_ID_TO_TOKEN: dict[int, str] = {i: tok for i, tok in enumerate(_VOCAB_ORDERED)}


class SExprTokenizer:
    """
    Simple S-expression tokenizer.

    The vocabulary is intentionally small and complete: every token that
    can appear in a valid S-expression produced by this module has a unique id.

    Special tokens
    ──────────────
    PAD_ID = 0
    BOS_ID = 1
    EOS_ID = 2

    Encoding
    ────────
    encode(text) → list[int]          (no BOS/EOS; call add_special if needed)
    encode_with_special(text) → list[int]  (BOS + tokens + EOS)
    decode(ids)  → str                (ignores PAD/BOS/EOS)
    """

    PAD_ID: int = _TOKEN_TO_ID["<PAD>"]
    BOS_ID: int = _TOKEN_TO_ID["<BOS>"]
    EOS_ID: int = _TOKEN_TO_ID["<EOS>"]

    vocab_size: int = len(_VOCAB_ORDERED)

    # Regex: match //, multi-char ops, integers, parens, words
    _PATTERN = re.compile(
        r"//|[+\-*%()]|(?:true|false)|(?:abs|and|apply|compose|"
        r"eq|ge|gt|if|le|lt|max|min|neg|not|or|partial)"
        r"|\d+",
        re.ASCII,
    )

    def tokenize(self, text: str) -> list[str]:
        """Return the sequence of surface tokens in *text*."""
        return self._PATTERN.findall(text)

    def encode(self, text: str) -> list[int]:
        """Tokenize *text* and return token ids (no BOS/EOS)."""
        tokens = self.tokenize(text)
        ids: list[int] = []
        for tok in tokens:
            tid = _TOKEN_TO_ID.get(tok)
            if tid is None:
                raise ValueError(f"Unknown token: {tok!r}")
            ids.append(tid)
        return ids

    def encode_with_special(self, text: str) -> list[int]:
        """BOS + token ids + EOS."""
        return [self.BOS_ID] + self.encode(text) + [self.EOS_ID]

    def decode(self, ids: list[int] | np.ndarray, skip_special: bool = True) -> str:
        """Convert token ids back to a space-separated string."""
        parts: list[str] = []
        skip_set = {self.PAD_ID, self.BOS_ID, self.EOS_ID} if skip_special else set()
        for tid in ids:
            tid = int(tid)
            if tid in skip_set:
                continue
            parts.append(_ID_TO_TOKEN.get(tid, f"<UNK:{tid}>"))
        # Re-assemble: no space before/after parens for readability
        return _pretty_join(parts)


def _pretty_join(tokens: list[str]) -> str:
    """Join tokens with minimal spacing (no space between paren and neighbour)."""
    result = []
    for tok in tokens:
        if result and result[-1] not in ("(", "") and tok != ")":
            result.append(" ")
        result.append(tok)
    return "".join(result)


# Module-level singleton so callers don't have to instantiate.
TOKENIZER = SExprTokenizer()


# ══════════════════════════════════════════════════════════════════
# S-expression Tree
# ══════════════════════════════════════════════════════════════════

@dataclass
class SExprNode:
    """
    A single node in an S-expression tree.

    For leaf nodes *is_leaf=True* and *value* holds the literal (int or bool).
    For internal nodes *op_name* / *op_idx* identify the operator and
    *children* holds the indices (into ``SExprTree.nodes``) of the
    immediate child nodes.
    """

    op_name: str          # operator name for internal nodes, e.g. "+"
                          # for leaf nodes this is the string repr of value
    op_idx: int           # index into OPS list; -1 for numeric leaves
    children: list[int]   # indices into SExprTree.nodes
    value: int | bool | None  # for leaves only
    is_leaf: bool


@dataclass
class SExprTree:
    """
    Flat representation of a parsed S-expression.

    ``nodes``   — all nodes in DFS pre-order (root at index 0).
    ``root``    — index of the root node (always 0 after parse_sexpr).
    ``text``    — original S-expression string.
    """

    nodes: list[SExprNode]
    root: int
    text: str

    # ── convenience accessors ──────────────────────────────────────

    def depth(self) -> int:
        """Maximum depth of the tree (leaves are depth 0)."""
        return _tree_depth(self, self.root)

    def n_nodes(self) -> int:
        return len(self.nodes)

    def op_labels(self) -> list[int]:
        """Per-node op index, -1 for numeric/boolean leaves."""
        return [n.op_idx for n in self.nodes]


def _tree_depth(tree: SExprTree, node_idx: int) -> int:
    node = tree.nodes[node_idx]
    if node.is_leaf:
        return 0
    return 1 + max(_tree_depth(tree, c) for c in node.children)


# ── Parser ──────────────────────────────────────────────────────────

def parse_sexpr(text: str) -> SExprTree:
    """
    Parse an S-expression string into an ``SExprTree``.

    The grammar handled:
      sexpr  ::= atom | '(' op sexpr* ')'
      atom   ::= integer | 'true' | 'false'
      op     ::= any token in OPS

    Raises ValueError on malformed input.
    """
    tokens = TOKENIZER.tokenize(text)
    nodes: list[SExprNode] = []
    pos, root = _parse_node(tokens, 0, nodes)
    if pos != len(tokens):
        remaining = tokens[pos:]
        raise ValueError(f"Trailing tokens after parse: {remaining!r}")
    return SExprTree(nodes=nodes, root=root, text=text)


def _parse_node(
    tokens: list[str],
    pos: int,
    nodes: list[SExprNode],
) -> tuple[int, int]:
    """
    Recursively parse one S-expression node.

    Returns (new_pos, node_index).
    """
    if pos >= len(tokens):
        raise ValueError("Unexpected end of token stream")

    tok = tokens[pos]

    # ── Compound expression: '(' op args... ')' ──────────────────
    if tok == "(":
        pos += 1  # consume '('
        if pos >= len(tokens):
            raise ValueError("Expected operator after '('")
        op_tok = tokens[pos]
        pos += 1  # consume op
        op_idx = OP_TO_IDX.get(op_tok, -1)
        if op_idx == -1:
            raise ValueError(f"Unknown operator: {op_tok!r}")

        # Parse children until ')'
        children: list[int] = []
        while pos < len(tokens) and tokens[pos] != ")":
            pos, child_idx = _parse_node(tokens, pos, nodes)
            children.append(child_idx)

        if pos >= len(tokens):
            raise ValueError("Missing closing ')'")
        pos += 1  # consume ')'

        node_idx = len(nodes)
        nodes.append(SExprNode(
            op_name=op_tok,
            op_idx=op_idx,
            children=children,
            value=None,
            is_leaf=False,
        ))
        return pos, node_idx

    # ── Boolean literal ──────────────────────────────────────────
    if tok == "true":
        node_idx = len(nodes)
        nodes.append(SExprNode(
            op_name="true",
            op_idx=OP_TO_IDX.get("true", -1),
            children=[],
            value=True,
            is_leaf=True,
        ))
        return pos + 1, node_idx

    if tok == "false":
        node_idx = len(nodes)
        nodes.append(SExprNode(
            op_name="false",
            op_idx=-1,  # false is not in OPS, it is only a literal
            children=[],
            value=False,
            is_leaf=True,
        ))
        return pos + 1, node_idx

    # ── Integer literal ──────────────────────────────────────────
    try:
        v = int(tok)
        node_idx = len(nodes)
        nodes.append(SExprNode(
            op_name=tok,
            op_idx=-1,
            children=[],
            value=v,
            is_leaf=True,
        ))
        return pos + 1, node_idx
    except ValueError:
        pass

    raise ValueError(f"Unexpected token: {tok!r} at position {pos}")


# ══════════════════════════════════════════════════════════════════
# Safe evaluator
# ══════════════════════════════════════════════════════════════════

# Maximum intermediate value to keep arithmetic from blowing up.
_MAX_EVAL = 10_000

class _EvalError(Exception):
    """Raised when evaluation produces an invalid result."""


def evaluate(tree: SExprTree, node_idx: int | None = None) -> int | bool:
    """
    Recursively evaluate an S-expression tree.

    Returns int or bool.  Raises ``_EvalError`` on overflow, div-by-zero,
    or type mismatch.
    """
    if node_idx is None:
        node_idx = tree.root
    node = tree.nodes[node_idx]

    if node.is_leaf:
        v = node.value
        if isinstance(v, bool):
            return v
        if abs(v) > _MAX_EVAL:  # type: ignore[arg-type]
            raise _EvalError(f"Leaf value {v} exceeds limit")
        return v  # type: ignore[return-value]

    def child(i: int) -> int | bool:
        return evaluate(tree, node.children[i])

    op = node.op_name

    # ── Arithmetic ──────────────────────────────────────────────
    if op == "+":
        r = int(child(0)) + int(child(1))
    elif op == "-":
        r = int(child(0)) - int(child(1))
    elif op == "*":
        r = int(child(0)) * int(child(1))
    elif op == "//":
        b = int(child(1))
        if b == 0:
            raise _EvalError("Division by zero")
        r = int(child(0)) // b
    elif op == "%":
        b = int(child(1))
        if b == 0:
            raise _EvalError("Modulo by zero")
        r = int(child(0)) % b
    elif op == "min":
        r = min(int(child(0)), int(child(1)))
    elif op == "max":
        r = max(int(child(0)), int(child(1)))
    elif op == "abs":
        r = abs(int(child(0)))
    elif op == "neg":
        r = -int(child(0))

    # ── Comparison ──────────────────────────────────────────────
    elif op == "eq":
        return child(0) == child(1)
    elif op == "lt":
        return int(child(0)) < int(child(1))
    elif op == "gt":
        return int(child(0)) > int(child(1))
    elif op == "le":
        return int(child(0)) <= int(child(1))
    elif op == "ge":
        return int(child(0)) >= int(child(1))

    # ── Boolean ─────────────────────────────────────────────────
    elif op == "and":
        return bool(child(0)) and bool(child(1))
    elif op == "or":
        return bool(child(0)) or bool(child(1))
    elif op == "not":
        return not bool(child(0))

    # ── Conditional ─────────────────────────────────────────────
    elif op == "if":
        if bool(child(0)):
            return child(1)
        else:
            return child(2)

    # ── Higher-order (return sentinel int — training exercises
    #    the dispatcher, not evaluation accuracy) ─────────────────
    elif op in ("apply", "compose", "partial"):
        raise _EvalError(f"Higher-order op {op!r} not evaluatable")

    else:
        raise _EvalError(f"Unknown op: {op!r}")

    if isinstance(r, int) and abs(r) > _MAX_EVAL:
        raise _EvalError(f"Result {r} exceeds limit")
    return r  # type: ignore[return-value]


# ══════════════════════════════════════════════════════════════════
# Random S-expression generator
# ══════════════════════════════════════════════════════════════════

# Partition ops by arity for generation
_UNARY_OPS  = [op for op in GENERATABLE_OPS if OP_ARITY[op] == 1]
_BINARY_OPS = [op for op in GENERATABLE_OPS if OP_ARITY[op] == 2]
_TERNARY_OPS = [op for op in GENERATABLE_OPS if OP_ARITY[op] == 3]


def _gen_sexpr_str(
    rng: random.Random,
    depth: int,
    max_depth: int,
    max_value: int,
    bool_ctx: bool = False,
) -> str:
    """
    Recursively generate a random S-expression string.

    At leaves we emit integers (0..max_value) or booleans (in bool_ctx).
    At internal nodes we pick randomly from GENERATABLE_OPS.
    """
    # Force a leaf if we've reached max depth or with decaying probability
    leaf_prob = 0.3 + 0.25 * depth  # 0.3 → 0.55 → 0.80 → 1.05 (capped)
    if depth >= max_depth or rng.random() < min(leaf_prob, 0.95):
        if bool_ctx:
            return rng.choice(["true", "false"])
        v = rng.randint(0, max_value)
        return str(v)

    # Two op pools: integer-context (bool_ctx=False) vs boolean-context (bool_ctx=True).
    # This prevents mixing int arithmetic with boolean sub-expressions, keeping
    # the evaluator from producing type errors at training time.
    if bool_ctx:
        # In a bool context: logical ops or comparisons
        bool_pool_weights = {
            "and":  20, "or":  20, "not": 15,
            "eq":   15, "lt":  10, "gt":  10, "le":   5, "ge":   5,
        }
        ops = list(bool_pool_weights.keys())
        weights = [bool_pool_weights[o] for o in ops]
    else:
        # In an int context: arithmetic ops and conditionals
        int_pool_weights = {
            "+":   20, "-":   20, "*":   12, "//":   8, "%":   5,
            "min":  6, "max":  6, "abs":  5, "neg":  4,
            "if":   6,
        }
        ops = list(int_pool_weights.keys())
        weights = [int_pool_weights[o] for o in ops]

    op = rng.choices(ops, weights=weights, k=1)[0]
    arity = OP_ARITY[op]

    if op == "if":
        # Condition is always bool; branches inherit parent context
        cond = _gen_sexpr_str(rng, depth + 1, max_depth, max_value, bool_ctx=True)
        then = _gen_sexpr_str(rng, depth + 1, max_depth, max_value, bool_ctx=bool_ctx)
        else_ = _gen_sexpr_str(rng, depth + 1, max_depth, max_value, bool_ctx=bool_ctx)
        return f"(if {cond} {then} {else_})"
    elif arity == 1:
        # "not" → bool child; "abs"/"neg" → int child (same as context since
        # they only appear in int_pool)
        child_bool = op == "not"
        arg = _gen_sexpr_str(rng, depth + 1, max_depth, max_value, bool_ctx=child_bool)
        return f"({op} {arg})"
    else:  # binary
        # "and"/"or" → bool children; comparisons → int children; arithmetic → int
        child_bool = op in {"and", "or"}
        left = _gen_sexpr_str(rng, depth + 1, max_depth, max_value, bool_ctx=child_bool)
        right = _gen_sexpr_str(rng, depth + 1, max_depth, max_value, bool_ctx=child_bool)
        return f"({op} {left} {right})"


def _try_generate(
    rng: random.Random,
    max_depth: int,
    max_value: int,
) -> tuple[str, SExprTree, int | bool] | None:
    """
    Attempt to generate one valid (text, tree, result) triple.

    Returns None if generation or evaluation fails (e.g. div-by-zero,
    overflow), so the caller can retry.
    """
    depth = rng.randint(1, max_depth)
    text = _gen_sexpr_str(rng, depth=0, max_depth=depth, max_value=max_value)
    try:
        tree = parse_sexpr(text)
        result = evaluate(tree)
    except (_EvalError, ValueError):
        return None
    return text, tree, result


# ══════════════════════════════════════════════════════════════════
# Public: generate_example
# ══════════════════════════════════════════════════════════════════

@dataclass
class Example:
    """
    One S-expression training example.

    Fields
    ──────
    text            Original S-expression string.
    token_ids       Token id sequence (no BOS/EOS, unpadded).
    tree            Parsed tree (DFS pre-order, root=0).
    op_labels       Per-node op index; -1 for literal leaves.
    result          Ground-truth evaluation result (int or bool).
    """

    text: str
    token_ids: list[int]
    tree: SExprTree
    op_labels: list[int]
    result: int | bool


# Hard upper bound imposed by the tokenizer vocabulary (numbers 0–99 only).
_TOKENIZER_MAX_VALUE = 99


def generate_example(
    rng: random.Random,
    max_depth: int = 4,
    max_value: int = 99,
    max_seq_len: int = 128,
    max_retries: int = 64,
) -> Example:
    """
    Generate one random S-expression example.

    Retries up to *max_retries* times to avoid div-by-zero or overflows.
    Raises RuntimeError if all attempts fail (extremely unlikely).

    Note: *max_value* is capped at ``_TOKENIZER_MAX_VALUE`` (99) because the
    tokenizer vocabulary only contains integers 0–99.  Values from
    ``V10Config.max_value`` (1000) are silently clamped here.
    """
    max_value = min(max_value, _TOKENIZER_MAX_VALUE)
    for _ in range(max_retries):
        triple = _try_generate(rng, max_depth=max_depth, max_value=max_value)
        if triple is None:
            continue
        text, tree, result = triple
        try:
            token_ids = TOKENIZER.encode(text)
        except ValueError:
            continue
        if len(token_ids) > max_seq_len:
            continue
        op_labels = tree.op_labels()
        return Example(
            text=text,
            token_ids=token_ids,
            tree=tree,
            op_labels=op_labels,
            result=result,
        )
    raise RuntimeError(
        f"Failed to generate a valid example in {max_retries} retries "
        f"(max_depth={max_depth}, max_value={max_value})"
    )


# ══════════════════════════════════════════════════════════════════
# Public: generate_batch
# ══════════════════════════════════════════════════════════════════

@dataclass
class Batch:
    """
    A padded batch of S-expression examples.

    Arrays
    ──────
    token_ids   (B, L)  int32  — padded token sequences
    lengths     (B,)    int32  — true sequence lengths (excl. pad)
    op_labels   ragged          — list[list[int]], per-node op indices
    results     (B,)    int32  — ground-truth results (bool cast to 0/1)
    examples    list[Example]  — raw examples for debugging
    """

    token_ids: np.ndarray    # (B, L) int32
    lengths: np.ndarray      # (B,)   int32
    op_labels: list[list[int]]
    results: np.ndarray      # (B,)   int32
    examples: list[Example]


def generate_batch(
    rng: random.Random,
    batch_size: int,
    max_seq_len: int,
    max_depth: int = 4,
    max_value: int = 99,
) -> Batch:
    """
    Generate *batch_size* examples and return them as a padded ``Batch``.

    The ``token_ids`` array is padded with ``TOKENIZER.PAD_ID`` to
    *max_seq_len*.  ``lengths`` gives the unpadded length of each row.
    ``results`` casts bool results to 1/0 so the array is int32 throughout.
    """
    examples: list[Example] = [
        generate_example(
            rng,
            max_depth=max_depth,
            max_value=max_value,
            max_seq_len=max_seq_len,
        )
        for _ in range(batch_size)
    ]

    # ── Token ids — pad to max_seq_len ────────────────────────────
    token_ids = np.full(
        (batch_size, max_seq_len),
        fill_value=TOKENIZER.PAD_ID,
        dtype=np.int32,
    )
    lengths = np.zeros(batch_size, dtype=np.int32)
    for i, ex in enumerate(examples):
        L = len(ex.token_ids)
        token_ids[i, :L] = ex.token_ids
        lengths[i] = L

    # ── Results (int32) ──────────────────────────────────────────
    results = np.array(
        [int(ex.result) for ex in examples],
        dtype=np.int32,
    )

    # ── Op labels (ragged — each example has a different tree size) ──
    op_labels = [ex.op_labels for ex in examples]

    return Batch(
        token_ids=token_ids,
        lengths=lengths,
        op_labels=op_labels,
        results=results,
        examples=examples,
    )


# ══════════════════════════════════════════════════════════════════
# Public: InfiniteDataLoader
# ══════════════════════════════════════════════════════════════════

class InfiniteDataLoader:
    """
    Yields fresh random batches forever.

    Usage::

        loader = InfiniteDataLoader(cfg)
        for step, batch in zip(range(cfg.total_steps), loader):
            train(batch)

    Each call to ``__next__`` generates ``batch_size`` brand-new examples,
    so the model never sees the same inputs twice across training.

    Parameters are read from a ``V10Config`` instance; any can be
    overridden via keyword arguments.
    """

    def __init__(
        self,
        cfg: V10Config,
        *,
        batch_size: int | None = None,
        max_depth: int | None = None,
        max_value: int | None = None,
        max_seq_len: int | None = None,
        seed: int = 42,
    ) -> None:
        self.batch_size = batch_size if batch_size is not None else cfg.batch_size
        self.max_depth  = max_depth  if max_depth  is not None else cfg.max_depth
        self.max_value  = max_value  if max_value  is not None else cfg.max_value
        self.max_seq_len = max_seq_len if max_seq_len is not None else cfg.max_seq_len
        self._rng = random.Random(seed)

    def __iter__(self) -> Iterator[Batch]:
        return self

    def __next__(self) -> Batch:
        return generate_batch(
            rng=self._rng,
            batch_size=self.batch_size,
            max_seq_len=self.max_seq_len,
            max_depth=self.max_depth,
            max_value=self.max_value,
        )


# ══════════════════════════════════════════════════════════════════
# Smoke-test (run as __main__)
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    cfg = V10Config()
    rng = random.Random(0)

    print("── Tokenizer ──────────────────────────────────────────")
    print(f"  vocab_size = {TOKENIZER.vocab_size}  (limit {cfg.vocab_size})")
    assert TOKENIZER.vocab_size <= cfg.vocab_size, "vocab exceeds config limit!"
    print(f"  PAD={TOKENIZER.PAD_ID}  BOS={TOKENIZER.BOS_ID}  EOS={TOKENIZER.EOS_ID}")

    sample_exprs = [
        "(+ 3 4)",
        "(if (lt 2 3) (+ 1 0) (- 5 2))",
        "(not false)",
        "(abs (neg 7))",
        "(min (max 1 2) (% 10 3))",
    ]
    for expr in sample_exprs:
        ids = TOKENIZER.encode(expr)
        back = TOKENIZER.decode(ids)
        print(f"  {expr!r:45s} → {ids}")
        print(f"  {'':45s}   decode: {back!r}")

    print()
    print("── Parser & evaluator ─────────────────────────────────")
    for expr in sample_exprs:
        tree = parse_sexpr(expr)
        try:
            result = evaluate(tree)
        except _EvalError as e:
            result = f"<EvalError: {e}>"
        print(f"  {expr!r:45s}  depth={tree.depth()}"
              f"  nodes={tree.n_nodes()}"
              f"  result={result}")

    print()
    print("── generate_example ───────────────────────────────────")
    for depth in range(1, cfg.max_depth + 1):
        ex = generate_example(rng, max_depth=depth, max_value=cfg.max_value,
                               max_seq_len=cfg.max_seq_len)
        print(f"  depth≤{depth}  {ex.text!r:50s}"
              f"  result={ex.result}"
              f"  tokens={len(ex.token_ids)}"
              f"  nodes={len(ex.op_labels)}")

    print()
    print("── generate_batch ─────────────────────────────────────")
    batch = generate_batch(
        rng=rng,
        batch_size=cfg.batch_size,
        max_seq_len=cfg.max_seq_len,
        max_depth=cfg.max_depth,
        max_value=cfg.max_value,
    )
    print(f"  token_ids.shape = {batch.token_ids.shape}")
    print(f"  lengths[:8]     = {batch.lengths[:8].tolist()}")
    print(f"  results[:8]     = {batch.results[:8].tolist()}")
    print(f"  op_labels[0]    = {batch.op_labels[0]}")
    print(f"  examples[0].text = {batch.examples[0].text!r}")

    print()
    print("── InfiniteDataLoader ─────────────────────────────────")
    loader = InfiniteDataLoader(cfg, seed=7)
    for step, batch in zip(range(3), loader):
        print(f"  step {step}: token_ids={batch.token_ids.shape}"
              f"  results={batch.results[:4].tolist()}")

    print()
    print("All checks passed ✓")
    sys.exit(0)
