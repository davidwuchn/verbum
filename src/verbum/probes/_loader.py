"""Probe-set loading and validation.

Canonical form per AGENTS.md S2 λ probe_format:

    probes/*.json   — one file per probe set, git-tracked
    gates/*.txt     — gate content, one file per gate, referenced by ID

Set fields:  {id, version, description, created, author, default_gate}
Probe fields: {id, category, gate, prompt, ground_truth, metadata}

Gate IDs are filename stems in the ``gates/`` directory. A probe can
override the set-level ``default_gate`` with its own ``gate`` field.

Versioning: append-and-tag (``v2`` ≻ in-place edit once results exist).
Ground truth: verbatim string, no grammar enforcement at boundary.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import structlog
from pydantic import BaseModel, ConfigDict, Field

from verbum.results import content_hash

__all__ = [
    "Gate",
    "Probe",
    "ProbeSet",
    "ResolvedProbe",
    "gate_hash",
    "load_gate",
    "load_probe_set",
    "probe_set_hash",
    "resolve_probes",
]

_LOG = structlog.get_logger(__name__)


# ─────────────────────────── models ───────────────────────────────────


class Probe(BaseModel):
    """One probe within a probe set.

    ``category`` is conventionally one of {compile, decompile, null} but
    any string is accepted (extensible per S2 λ probe_format).

    ``gate`` overrides the set-level ``default_gate`` when present.
    ``ground_truth`` is a verbatim string — no grammar enforcement.
    """

    model_config = ConfigDict(extra="allow")

    id: str
    category: str
    gate: str | None = None  # overrides ProbeSet.default_gate
    prompt: str
    ground_truth: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProbeSet(BaseModel):
    """A complete probe set — the unit loaded from ``probes/*.json``.

    ``default_gate`` is applied to any probe whose ``gate`` is ``None``.
    """

    model_config = ConfigDict(extra="allow")

    id: str
    version: int = 1
    description: str = ""
    created: str = ""  # ISO-8601 preferred
    author: str = ""
    default_gate: str
    probes: list[Probe] = Field(default_factory=list)


# ─────────────────────────── gate loading ─────────────────────────────


class Gate(BaseModel):
    """A loaded gate — ID, content, and content hash."""

    model_config = ConfigDict(frozen=True)

    id: str
    content: str
    hash: str


def load_gate(gate_id: str, gates_dir: Path | str) -> Gate:
    """Read ``gates/{gate_id}.txt`` and return a ``Gate``.

    Raises ``FileNotFoundError`` if the gate file does not exist.
    """
    gates_dir = Path(gates_dir)
    path = gates_dir / f"{gate_id}.txt"
    text = path.read_text("utf-8")
    return Gate(id=gate_id, content=text, hash=content_hash(text))


def gate_hash(gate_id: str, gates_dir: Path | str) -> str:
    """Return the ``content_hash`` of a gate file without loading fully.

    (In practice we read the file either way, but the return is just
    the hash string — useful for provenance without retaining content.)
    """
    return load_gate(gate_id, gates_dir).hash


# ─────────────────────────── probe-set loading ────────────────────────


def load_probe_set(path: Path | str) -> ProbeSet:
    """Load and validate a probe-set JSON file.

    Raises ``FileNotFoundError`` if the file is missing and
    ``pydantic.ValidationError`` if the JSON doesn't match the schema.
    """
    path = Path(path)
    raw = path.read_text("utf-8")
    data = json.loads(raw)
    ps = ProbeSet.model_validate(data)
    _LOG.info(
        "probe_set.loaded",
        id=ps.id,
        version=ps.version,
        n_probes=len(ps.probes),
        path=str(path),
    )
    return ps


def probe_set_hash(path: Path | str) -> str:
    """Return the ``content_hash`` of a probe-set file (byte-level)."""
    path = Path(path)
    return content_hash(path.read_text("utf-8"))


# ─────────────────────────── resolved probes ──────────────────────────


class ResolvedProbe(BaseModel):
    """A probe with its gate content resolved — ready to fire.

    ``full_prompt`` is ``gate_content + prompt`` (the actual string sent
    to the model).  ``gate_id`` and ``gate_hash`` are recorded for
    provenance so the result row can reference them.
    """

    model_config = ConfigDict(frozen=True)

    probe_id: str
    category: str
    gate_id: str
    gate_hash: str
    prompt: str  # original probe prompt
    gate_content: str
    full_prompt: str  # gate_content + prompt
    prompt_hash: str  # content_hash(full_prompt)
    ground_truth: str
    metadata: dict[str, Any] = Field(default_factory=dict)


def resolve_probes(
    probe_set: ProbeSet,
    gates_dir: Path | str,
) -> list[ResolvedProbe]:
    """Resolve all probes in a set — load gates, build full prompts.

    Each probe's effective gate is ``probe.gate or probe_set.default_gate``.
    Gate files are cached within the call (loaded once per unique ID).

    Raises ``FileNotFoundError`` if any referenced gate file is missing.
    """
    gates_dir = Path(gates_dir)
    gate_cache: dict[str, Gate] = {}
    resolved: list[ResolvedProbe] = []

    for probe in probe_set.probes:
        gid = probe.gate or probe_set.default_gate

        if gid not in gate_cache:
            gate_cache[gid] = load_gate(gid, gates_dir)

        gate = gate_cache[gid]
        full = gate.content + probe.prompt
        resolved.append(
            ResolvedProbe(
                probe_id=probe.id,
                category=probe.category,
                gate_id=gid,
                gate_hash=gate.hash,
                prompt=probe.prompt,
                gate_content=gate.content,
                full_prompt=full,
                prompt_hash=content_hash(full),
                ground_truth=probe.ground_truth,
                metadata=probe.metadata,
            )
        )

    _LOG.info(
        "probes.resolved",
        probe_set=probe_set.id,
        n_resolved=len(resolved),
        gates_loaded=len(gate_cache),
    )
    return resolved
