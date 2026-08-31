# FREEZE — 2026-08-29

**Method evaluation using a narrow task as instrument; not circuit discovery.**

This file, together with `experiments/stage3/freeze.json` (the machine-readable
copy the evaluation script actually loads), fixes every evaluative choice before
the held-out split is read. After this commit, no threshold, position, layer,
template, vocabulary item or hyperparameter may be chosen by looking at
held-out. Held-out is read once, by `experiments/stage3/heldout_frozen.py` and
the `--frozen-eval` eligibility screen, at evaluation time.

## What is frozen, and where each choice comes from

**Positions**, by anchor rather than token index, because held-out spans
templates T1–T6 of varying length: `relcomp` (the token immediately preceding
the final `?` — the token that completes the relation; ` lives` on dev T1) and
`qmark` (the `?` itself) are the **primary measurement positions**. `prequery`
and `final` are carried as references only: prequery is undetermined (the
question has not yet named a subject) and final is output-contaminated (38/40
dev generations name the intermediate; the Stage 2 answer-shadow result).

These positions come from the post-query sweep — Falcon **552322** and
TinkerCliffs **7307558**, commit `7adaad1`, tables in
`results/stage2/postquery-sweep-by-position*.txt` — whose pre-registered
decision rule (Hour 3 entry of the learning log, committed before submission)
fired on rule 1: J-Lens resolves direction at these positions, 0.750–0.775
against a label-permutation control at 0.350, on both GPU architectures.

**Layers**, from the pre-registered dev rule (argmax mean paired intermediate
margin), identical on both clusters at every position carrying signal:

| arm | relcomp | qmark | final | prequery |
|---|---|---|---|---|
| J-Lens | L30 | L27 | L27 | L25 |
| logit lens | L30 | L29 | L30 | L24 |
| random transport | at the J-Lens layers | | | |
| arm 3 (supervised) | L30 | L30 | L30 | L30 |

**Arm 3** is fit on all 40 dev records and applied unchanged to held-out — the
promise §2.5 of the write-up makes, which the shared six-word vocabulary exists
to keep.

**Controls:** label permutation (derangement, seed 20260827, within each split)
and norm-matched random transport, unchanged from Stage 1.

**New measurement, not a new choice:** the model's own next-token distribution
(`model_logits`) is recorded at every scored position on both splits, so the
output-shadow question at the primary positions becomes a per-record
measurement rather than structural reasoning. This adds recorded data and tunes
nothing.

## Contact with held-out before this freeze

Its `_meta` header, the record count (160), the pair count (40) and the
template-id set (T1–T6) were read once, to design the position anchoring.
No prompt, entity, vocabulary item or answer was read.

## Failure condition, stated in advance

If held-out `frac` at **both** primary positions sits at or near its
label-permutation control, the sweep result was forking paths. That outcome is
the finding and will be reported as such; the frozen settings make re-selection
impossible by construction.

All downstream numbers `agent-unverified` until independently re-derived.
