"""Quantization-ladder analysis: per-vertex Gram fidelity FP → ternary → 1-bit.

    λ ladder(fp, rungs). ∀vertex k: fid_k(rung) = corr(fp_row_k, rung_row_k)
                         | null-gated: shuffled-vertex-label permutation
                         | pre-reg (a): selective K degradation at 1-bit
                         | pre-reg (b): degradation concentrates in deep-middle band
                         | register-resolved (gate ⊥ attn, s260 routing⊥value)

Register of the claims (λ measure): relational-geometry register — per-vertex
rows of the 9x9 crystal Gram. The probe (row-wise Pearson over 8 off-diagonal
entries) matches the register. Gate failure of a rung layer is itself data.

Usage:
    uv run python opcodes/ladder.py \
        --fp results/opcode-trace/qwen3-6-27b \
        --rung ternary=results/opcode-trace/bonsai27b-unpacked \
        --rung 1bit=results/opcode-trace/bonsai-27b-unpacked \
        --out results/opcode-trace/ladder_analysis.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from vsm import VSMNode, load_tree  # noqa: E402

REGISTERS = ("gate", "attn")
BAND = (0.375, 0.625)  # deep-middle band (s267 50%-dip pre-registration)
N_PERM = 10_000
RNG = np.random.default_rng(268)


# ── fidelity primitives ──────────────────────────────────────────────────────


def vertex_fidelity(fp_gram: np.ndarray, rung_gram: np.ndarray) -> np.ndarray:
    """Per-vertex row-wise Pearson corr over the 8 off-diagonal entries."""
    n = fp_gram.shape[0]
    out = np.full(n, np.nan)
    for k in range(n):
        idx = [j for j in range(n) if j != k]
        x, y = fp_gram[k, idx], rung_gram[k, idx]
        if x.std() < 1e-9 or y.std() < 1e-9:
            out[k] = 0.0
        else:
            out[k] = float(np.corrcoef(x, y)[0, 1])
    return out


def shuffled_label_null(
    fp_gram: np.ndarray, rung_gram: np.ndarray, n_perm: int = 1000
) -> np.ndarray:
    """Null distribution of mean vertex fidelity under joint row/col permutation
    of the rung Gram (destroys vertex identity, preserves spectrum)."""
    n = fp_gram.shape[0]
    means = np.empty(n_perm)
    for i in range(n_perm):
        p = RNG.permutation(n)
        means[i] = np.nanmean(vertex_fidelity(fp_gram, rung_gram[np.ix_(p, p)]))
    return means


# ── tree walkers ─────────────────────────────────────────────────────────────


def layer_grams(tree: VSMNode, register: str) -> dict[int, tuple[np.ndarray, bool]]:
    """{layer_index: (gram, gated)} for one register."""
    reg = tree.child(register)
    if reg is None:
        return {}
    out = {}
    for c in reg.children:
        if c.level == "layer" and c.gram is not None:
            out[int(c.name.lstrip("L"))] = (np.asarray(c.gram), bool(c.gated))
    return out


# ── pre-registered tests ─────────────────────────────────────────────────────


def selective_k_test(
    drops: np.ndarray, basis: list[str], n_perm: int = N_PERM
) -> dict:
    """drops: [n_layers, 9] per-layer per-vertex fidelity drop (tern - 1bit,
    or fp-fid - rung-fid). Statistic: mean drop of K minus mean drop of the
    other vertices. Null: permute vertex labels independently within layers."""
    k_idx = basis.index("K")
    obs = float(np.nanmean(drops[:, k_idx]) - np.nanmean(np.delete(drops, k_idx, 1)))
    null = np.empty(n_perm)
    for i in range(n_perm):
        perm = np.stack([RNG.permutation(row) for row in drops])
        null[i] = np.nanmean(perm[:, k_idx]) - np.nanmean(np.delete(perm, k_idx, 1))
    p = float((np.sum(null >= obs) + 1) / (n_perm + 1))
    return {
        "obs_k_excess_drop": obs,
        "null_mean": float(null.mean()),
        "null_std": float(null.std()),
        "z": float((obs - null.mean()) / (null.std() + 1e-12)),
        "p_perm": p,
    }


def per_vertex_excess(
    drops: np.ndarray, basis: list[str], n_perm: int = N_PERM
) -> dict:
    """Same statistic as selective_k_test but for every vertex (exploratory,
    not pre-registered — reported for context around the K claim)."""
    out = {}
    for name in basis:
        idx = basis.index(name)
        obs = float(
            np.nanmean(drops[:, idx]) - np.nanmean(np.delete(drops, idx, 1))
        )
        out[name] = round(obs, 4)
    return out


def band_concentration_test(
    per_layer_deg: np.ndarray, n_perm: int = N_PERM
) -> dict:
    """per_layer_deg: [n_layers] mean degradation (1 - mean vertex fidelity).
    Statistic: mean degradation inside deep-middle band minus outside.
    Null: circular shifts of the depth profile (preserves autocorrelation)."""
    n = len(per_layer_deg)
    depth = np.arange(n) / max(n - 1, 1)
    in_band = (depth >= BAND[0]) & (depth <= BAND[1])
    obs = float(
        np.nanmean(per_layer_deg[in_band]) - np.nanmean(per_layer_deg[~in_band])
    )
    null = np.empty(n_perm)
    for i in range(n_perm):
        shifted = np.roll(per_layer_deg, RNG.integers(1, n))
        null[i] = np.nanmean(shifted[in_band]) - np.nanmean(shifted[~in_band])
    p = float((np.sum(null >= obs) + 1) / (n_perm + 1))
    return {
        "band": list(BAND),
        "obs_band_excess": obs,
        "null_mean": float(null.mean()),
        "null_std": float(null.std()),
        "z": float((obs - null.mean()) / (null.std() + 1e-12)),
        "p_perm": p,
    }


# ── main ─────────────────────────────────────────────────────────────────────


def analyze(fp_dir: Path, rungs: dict[str, Path], out_path: Path) -> dict:
    fp = load_tree(fp_dir / "model_vsm.json")
    basis = list(fp.basis)
    report: dict = {
        "fp_parent": fp.name,
        "basis": basis,
        "band": list(BAND),
        "n_perm": N_PERM,
        "rungs": {},
    }

    fp_layers = {r: layer_grams(fp, r) for r in REGISTERS}
    rung_layer_fids: dict[str, dict[str, np.ndarray]] = {}

    for rung_name, rung_dir in rungs.items():
        tree = load_tree(rung_dir / "model_vsm.json")
        entry: dict = {"model": tree.name, "registers": {}}

        # model-level per-vertex fidelity + shuffled-label null
        mfid = vertex_fidelity(np.asarray(fp.gram), np.asarray(tree.gram))
        null = shuffled_label_null(np.asarray(fp.gram), np.asarray(tree.gram))
        obs_mean = float(np.nanmean(mfid))
        entry["model_level"] = {
            "per_vertex_fidelity": {
                b: round(float(v), 4) for b, v in zip(basis, mfid, strict=True)
            },
            "mean_fidelity": obs_mean,
            "null_mean": float(null.mean()),
            "null_std": float(null.std()),
            "z": float((obs_mean - null.mean()) / (null.std() + 1e-12)),
            "p_perm": float((np.sum(null >= obs_mean) + 1) / (len(null) + 1)),
        }

        rung_layer_fids[rung_name] = {}
        for reg in REGISTERS:
            rl = layer_grams(tree, reg)
            common = sorted(set(fp_layers[reg]) & set(rl))
            # restrict to layers where the FP parent crystal is gated
            fp_gated = [i for i in common if fp_layers[reg][i][1]]
            fids = np.full((len(fp_gated), len(basis)), np.nan)
            rung_gate_fail = []
            for row, i in enumerate(fp_gated):
                fids[row] = vertex_fidelity(fp_layers[reg][i][0], rl[i][0])
                if not rl[i][1]:
                    rung_gate_fail.append(i)
            rung_layer_fids[rung_name][reg] = (np.array(fp_gated), fids)
            per_layer_deg = 1.0 - np.nanmean(fids, axis=1)
            entry["registers"][reg] = {
                "n_fp_gated_layers": len(fp_gated),
                "rung_gate_failures": rung_gate_fail,
                "mean_vertex_fidelity": {
                    b: round(float(v), 4)
                    for b, v in zip(basis, np.nanmean(fids, axis=0), strict=True)
                },
                "selective_k_vs_fp": selective_k_test(1.0 - fids, basis),
                "per_vertex_excess_drop_vs_fp": per_vertex_excess(1.0 - fids, basis),
                "band_concentration": band_concentration_test(per_layer_deg),
                "per_layer_mean_fidelity": [
                    round(float(v), 4) for v in np.nanmean(fids, axis=1)
                ],
                "fp_gated_layer_ids": [int(i) for i in fp_gated],
            }
        report["rungs"][rung_name] = entry

    # ── ladder contrast: ternary - 1bit (the pre-registered K test) ──────────
    if {"ternary", "1bit"} <= set(rung_layer_fids):
        contrast: dict = {}
        for reg in REGISTERS:
            l_t, f_t = rung_layer_fids["ternary"][reg]
            l_b, f_b = rung_layer_fids["1bit"][reg]
            common = sorted(set(l_t.tolist()) & set(l_b.tolist()))
            it = [list(l_t).index(i) for i in common]
            ib = [list(l_b).index(i) for i in common]
            drops = f_t[it] - f_b[ib]  # positive = worse at 1-bit
            contrast[reg] = {
                "n_layers": len(common),
                "mean_drop_per_vertex": {
                    b: round(float(v), 4)
                    for b, v in zip(basis, np.nanmean(drops, axis=0), strict=True)
                },
                "selective_k_1bit": selective_k_test(drops, basis),
                "per_vertex_excess_drop": per_vertex_excess(drops, basis),
                "band_concentration_of_drop": band_concentration_test(
                    np.nanmean(drops, axis=1)
                ),
            }
        report["ladder_contrast_ternary_minus_1bit"] = contrast

    out_path.write_text(json.dumps(report, indent=1))
    return report


def _print_report(rep: dict) -> None:
    basis = rep["basis"]
    print(f"FP parent: {rep['fp_parent']}   basis: {basis}")
    for rung, e in rep["rungs"].items():
        ml = e["model_level"]
        print(f"\n━━ rung: {rung} ({e['model']})")
        print(
            f"  model-level mean fidelity {ml['mean_fidelity']:.4f} "
            f"(null {ml['null_mean']:.3f}±{ml['null_std']:.3f}, "
            f"z={ml['z']:.1f}, p={ml['p_perm']:.4f})"
        )
        print("  per-vertex:", " ".join(
            f"{b}={ml['per_vertex_fidelity'][b]:.3f}" for b in basis))
        for reg, r in e["registers"].items():
            sk = r["selective_k_vs_fp"]
            bc = r["band_concentration"]
            print(
                f"  [{reg}] {r['n_fp_gated_layers']} FP-gated layers, "
                f"rung gate failures: {len(r['rung_gate_failures'])} "
                f"{r['rung_gate_failures'] if r['rung_gate_failures'] else ''}"
            )
            print("    mean vertex fid:", " ".join(
                f"{b}={r['mean_vertex_fidelity'][b]:.3f}" for b in basis))
            print(
                f"    K-excess-drop vs FP: {sk['obs_k_excess_drop']:+.4f} "
                f"(z={sk['z']:.2f}, p={sk['p_perm']:.4f})"
            )
            print(
                f"    band[{bc['band'][0]}-{bc['band'][1]}] excess deg: "
                f"{bc['obs_band_excess']:+.4f} (z={bc['z']:.2f}, p={bc['p_perm']:.4f})"
            )
    c = rep.get("ladder_contrast_ternary_minus_1bit")
    if c:
        print("\n━━ ladder contrast (ternary - 1bit): + = worse at 1-bit")
        for reg, r in c.items():
            sk = r["selective_k_1bit"]
            bc = r["band_concentration_of_drop"]
            print(f"  [{reg}] n={r['n_layers']} layers")
            print("    mean drop:", " ".join(
                f"{b}={r['mean_drop_per_vertex'][b]:+.3f}" for b in basis))
            print(
                f"    PRE-REG (a) selective K at 1-bit: "
                f"excess {sk['obs_k_excess_drop']:+.4f} "
                f"(z={sk['z']:.2f}, p={sk['p_perm']:.4f})"
            )
            print(
                f"    PRE-REG (b) deep-middle concentration: "
                f"{bc['obs_band_excess']:+.4f} "
                f"(z={bc['z']:.2f}, p={bc['p_perm']:.4f})"
            )


def main() -> None:
    ap = argparse.ArgumentParser(description="Quantization-ladder Gram fidelity")
    ap.add_argument("--fp", required=True, help="FP parent trace dir")
    ap.add_argument(
        "--rung", action="append", required=True,
        help="name=dir (e.g. ternary=results/opcode-trace/bonsai27b-unpacked)",
    )
    ap.add_argument("--out", default="results/opcode-trace/ladder_analysis.json")
    args = ap.parse_args()
    rungs = {}
    for spec in args.rung:
        name, _, d = spec.partition("=")
        rungs[name] = Path(d)
    rep = analyze(Path(args.fp), rungs, Path(args.out))
    _print_report(rep)
    print(f"\n[ladder] wrote {args.out}")


if __name__ == "__main__":
    main()
