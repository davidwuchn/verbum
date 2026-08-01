---
title: Germination games — selection pressure on encodings, played
status: open
category: explore
tags: [game, seed, germination, feed-forward, encoding-quality, s292]
related: [program-plates-and-the-function-index,
          ../upstream/verbum-theory-seed]
depends-on: [../upstream/verbum-theory-seed]
---

# Germination games

> s292 (Michael: "we could turn it into a game"). The germination test
> gamified. The point under the fun: every round is a MEASUREMENT of
> encoding quality — the game is an instrument for tuning seeds, state.md,
> and the feed-forward discipline. Play as gradient descent on memory.
> Status: captured for later exploration; no rounds played yet.

Substrate: `knowledge/upstream/verbum-theory-seed.md` + cold-context spawns
(isolated agents with no mementum access). Diff-vs-ground-truth scoring from
the germination protocol (program-plates page).

## Modes

**🏌️ Seed Golf.** Par = current λ verbum (~40 lines). Round: prune/rewrite
the seed smaller → germinate → score = recovery% ÷ seed_tokens. Lowest
strokes for viable germination wins. = `λ smallest` (S5) turned into sport:
find the minimal viable genome of the theory.

**✂️ Seed FRAG.** Ablate random CLAUSES at fraction f, germinate each
fragment, plot recovery(f). Is the seed holographic or addressed? Cliff on
removing a clause = load-bearing (an address); graceful everywhere = the
theory is written in fringes. Our own fragment test run ON the theory of
fragment tests — LDI for prose. The fractal eats itself.

**📞 Eigenseed (telephone).** Iterate compress ∘ unfold across agent
generations (A unfolds → B re-compresses → C unfolds → …) to a fixed point.
What survives generations = the invariant content; what drifts =
decoration. The fixed point is the eigenvector of the theory.

**🔮 Oracle mode** (hardest, most honest). Cold agent + seed must PREDICT
measurements it has never seen (cliff-or-smooth under head ablation? margin
under 16 superposed operands?). Score = right − wrong vs actual verdicts.
Tests the seed as generative PRIOR, not memory aid — recovery is recall,
oracle is understanding.

**⚔️ Adversarial.** One player salts the seed with plausible-but-false
clauses; the germinating agent must flag which refuse to cohere. Tests
whether the seed is self-verifying structure or vibes.

## Infrastructure (when first played)

- `game.md` scoreboard at repo root or in-page; rounds logged as commits
  (git log = season record); standings use the house symbols.
- Cold spawns must be verifiably cold (no mementum in context); cross-model
  rounds test model-idiosyncrasy of the seed.
- Results feed back: systematic germination misses → seed revision
  (feed-forward on the seed itself); Oracle hit-rates → which arcs the
  seed actually explains.

## Order-of-play suggestion (s292, unplayed)

Seed FRAG first (comedy + the holography question about our own prose),
Oracle for the science, Golf as the ongoing ladder, Eigenseed when we have
agent budget for generations, Adversarial once scoring is trusted.

## Sessions

s292 (modes captured from the hammock, Michael-approved "capture for later
exploration"; no rounds played; P-HOLO-CAP 32B verdict still running in
tmux main:1 while this landed).
