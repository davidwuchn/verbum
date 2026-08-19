#!/usr/bin/env python3
"""Route-map v0 READER — LOOK at what the model does (s344, exploratory).

Consumes a route_map_v0 run (routes.npz + summary.json + meta.json) and produces
the observation record: plots + a text summary. NO verdicts (capture-euphoria
guard): the output FEEDS the next special-probe design, it does not close a claim.

The headline read: the prose->symbolic gradient. Do plain-prose routes resemble
nl-combinator / formal-lambda routes (the reducer runs on ALL language) or diverge
(notation activates something)? Plus: where do bands converge/diverge over depth,
does everything collapse toward emission at the top (s343 transform->output flip),
which station-transitions dominate.

Usage:
    uv run python scripts/explore/route_map_read.py results/route_map_v0_s344/run

License: MIT.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

BAND_ORDER = ("plain_prose", "prose_structured", "nl_combinator",
              "symbolic_formal", "cross_domain")
BAND_COLOR = {"plain_prose": "#1f77b4", "prose_structured": "#2ca02c",
              "nl_combinator": "#ff7f0e", "symbolic_formal": "#d62728",
              "cross_domain": "#9467bd"}


def _load(run: Path):
    z = np.load(run / "routes.npz", allow_pickle=True)
    meta = json.loads((run / "meta.json").read_text())
    route17 = z["route17"].astype(np.float32)     # (n, L, 17)
    route3 = z["route3"].astype(np.float32)       # (n, L, 3)
    band = z["band"].astype(str)
    kind = z["kind"].astype(str)
    basis17 = z["basis17"].astype(str)
    return z, meta, route17, route3, band, kind, basis17


def _unit(x, axis=-1):
    return x / (np.linalg.norm(x, axis=axis, keepdims=True) + 1e-9)


def _band_centroids(route17, band):
    """(B, L, 17) mean route per band."""
    bands = [b for b in BAND_ORDER if (band == b).any()]
    cent = np.stack([route17[band == b].mean(axis=0) for b in bands])
    return bands, cent


def observe(run: Path) -> None:
    z, meta, route17, route3, band, _kind, basis17 = _load(run)
    n, L, _S = route17.shape
    print(f"\n=== route-map v0 READ: {run} ===")
    print(f"model={meta.get('model_id')} n_diverse={n} layers={L} "
          f"det_ok={meta.get('det_ok')} g0={meta.get('g0_coherence', {}).get('my_pr')}")
    bands, cent = _band_centroids(route17, band)    # (B, L, 17)

    # (1) prose->symbolic: per-layer cosine of each band centroid to plain_prose
    print("\n[1] PROSE->SYMBOLIC — cosine(band route, plain_prose route) by depth")
    if "plain_prose" in bands:
        ref = cent[bands.index("plain_prose")]      # (L, 17)
        seg = [0, L // 3, 2 * L // 3, L]
        hdr = "  band              " + "".join(
            f" L{seg[i]:02d}-{seg[i + 1] - 1:02d}" for i in range(3))
        print(hdr)
        for bi, b in enumerate(bands):
            cs = (_unit(cent[bi]) * _unit(ref)).sum(axis=1)   # (L,)
            thirds = [float(cs[seg[i]:seg[i + 1]].mean()) for i in range(3)]
            print(f"  {b:16s}  " + "  ".join(f"{t:+.3f}" for t in thirds))

    # (2) band separation over depth: mean pairwise centroid distance per layer
    print("\n[2] BAND SEPARATION by depth (mean pairwise 1-cos of band centroids)")
    cu = _unit(cent)                                 # (B, L, 17)
    sep = []
    for li in range(L):
        v = cu[:, li]                                # (B, 17)
        sim = v @ v.T
        iu = np.triu_indices(len(bands), 1)
        sep.append(1 - sim[iu].mean())
    sep = np.array(sep)
    marks = [0, L // 4, L // 2, 3 * L // 4, L - 1]
    print("  layer:  " + "  ".join(f"L{m:02d}" for m in marks))
    print("  sep:    " + "  ".join(f"{sep[m]:.3f}" for m in marks))
    print(f"  peak separation @ L{int(sep.argmax())} ({sep.max():.3f}); "
          f"min @ L{int(sep.argmin())} ({sep.min():.3f})")

    # (3) top-of-stack: does everything collapse to one station? (s343 flip)
    print("\n[3] TOP-OF-STACK collapse (dominant station per band, last 3 layers)")
    stations = z["stations"].astype(int)
    for b in bands:
        st = stations[band == b][:, -3:].ravel()
        vals, cnts = np.unique(st, return_counts=True)
        top = vals[cnts.argmax()]
        print(f"  {b:16s} -> {basis17[top]:8s} "
              f"({cnts.max() / cnts.sum() * 100:.0f}% of last-3-layer stations)")

    # (4) dominant stations by band across ALL depth (occupancy argmax share)
    print("\n[4] DOMINANT STATIONS by band (argmax-station share over all layers)")
    for b in bands:
        st = stations[band == b].ravel()
        vals, cnts = np.unique(st, return_counts=True)
        order = cnts.argsort()[::-1][:4]
        share = "  ".join(f"{basis17[vals[o]]}:{cnts[o] / cnts.sum() * 100:.0f}%"
                          for o in order)
        print(f"  {b:16s} {share}")

    _plots(run, route3, cent, cu, sep, bands, basis17, z)
    print(f"\nwrote plots -> {run}/plots/")


def _plots(run, route3, cent, cu, sep, bands, basis17, z):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pd = run / "plots"
    pd.mkdir(parents=True, exist_ok=True)
    L = cent.shape[1]

    band_arr = z["band"].astype(str)

    # A: band mean route3 trajectory in the fire/halt/diverge simplex (axes 0,1)
    fig, ax = plt.subplots(figsize=(7, 6))
    for b in bands:
        r3 = route3[band_arr == b].mean(axis=0)      # (L,3)
        ax.plot(r3[:, 0], r3[:, 1], "-", color=BAND_COLOR.get(b), label=b, lw=1.5)
        ax.scatter(r3[0, 0], r3[0, 1], color=BAND_COLOR.get(b), marker="o", s=30)
        ax.scatter(r3[-1, 0], r3[-1, 1], color=BAND_COLOR.get(b), marker="*", s=90)
    ax.set_xlabel("pole axis 1")
    ax.set_ylabel("pole axis 2")
    ax.set_title("Band mean routes in rank-3 pole space (o=L0 *=top)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(pd / "band_routes_simplex.png", dpi=110)
    plt.close(fig)

    # B: per-band occupancy heatmaps (layer x 17 poles)
    fig, axes = plt.subplots(1, len(bands), figsize=(3.2 * len(bands), 5),
                             sharey=True)
    if len(bands) == 1:
        axes = [axes]
    vmax = float(np.abs(cent).max())
    im = None
    for bi, (b, ax) in enumerate(zip(bands, axes, strict=True)):
        im = ax.imshow(cent[bi], aspect="auto", cmap="RdBu_r",
                       vmin=-vmax, vmax=vmax, origin="lower")
        ax.set_title(b, fontsize=9)
        ax.set_xticks(range(17))
        ax.set_xticklabels(basis17, rotation=90, fontsize=6)
        if bi == 0:
            ax.set_ylabel("layer")
    fig.colorbar(im, ax=axes, fraction=0.02)
    fig.suptitle("Per-band pole occupancy over depth (route17 centroid)")
    fig.savefig(pd / "band_occupancy.png", dpi=110)
    plt.close(fig)

    # C: band separation over depth
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(range(L), sep, "-k", lw=2)
    ax.set_xlabel("layer")
    ax.set_ylabel("mean pairwise 1-cos of band centroids")
    ax.set_title("Band separation over depth (high=bands diverge, low=converge)")
    fig.tight_layout()
    fig.savefig(pd / "band_separation.png", dpi=110)
    plt.close(fig)

    # D: station transition graph (17x17)
    summ = json.loads((run / "summary.json").read_text())
    trans = np.array(summ["station_transitions"], float)
    tn = trans / (trans.sum(axis=1, keepdims=True) + 1e-9)
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(tn, cmap="magma", aspect="auto")
    ax.set_xticks(range(17))
    ax.set_xticklabels(basis17, rotation=90, fontsize=7)
    ax.set_yticks(range(17))
    ax.set_yticklabels(basis17, fontsize=7)
    ax.set_xlabel("to")
    ax.set_ylabel("from")
    ax.set_title("Station transition graph (row-normalized)")
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(pd / "station_transitions.png", dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    run = Path(sys.argv[1] if len(sys.argv) > 1 else "results/route_map_v0_s344/run")
    observe(run)
