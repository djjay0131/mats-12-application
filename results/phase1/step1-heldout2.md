# Phase 1, step 1 — fresh held-out draw scored once at frozen settings

Status: **agent-unverified**. Numbers only; interpretation is Jason's.
Pre-registration: `llm/memory_bank/research-learning-log.md`, entry
"Phase 1, step 1" (commit `331e33a`) and Amendment 1 (commit `fe1ca16`),
both committed before the job that produced these numbers was queued.

## Provenance

| item | value |
|---|---|
| draw | `results/datasets/heldout2.jsonl` — seed 20260917, `--pool-seed 20260827`, `--n-dev 0 --n-heldout 60 --id-prefix h2- --dedupe-prompts`; 60 pairs, 240 records; sha256 `3a06138a80aaad16…`; index 44 skipped (duplicate prompt); class support 6 classes, min 19 pairs/class, 0 duplicate prompts |
| first attempt | Falcon job 587798, commit `331e33a`, L40S: step-0 regression passed (regenerated original `dev.jsonl` = `977b3d67…`, `heldout.jsonl` = `88f69b62…`, both identical to `dataset-manifest.json`); draw refused by the generator self-check (4 duplicate prompts); nothing written or scored |
| scoring job | Falcon job **587809**, commit `fe1ca16`, node fal046, **NVIDIA L40S** (application run was A30), 14:55 elapsed, all four steps exit 0; log `results/slurm-logs/phase1-step1-587809.out` |
| eligibility run | `results/runs/20260917T192334Z-eligibility-screen` |
| scoring run | `results/runs/20260917T193052Z-stage3-heldout-frozen` (`experiments/stage3/heldout_frozen.py --heldout results/datasets/heldout2.jsonl`, freeze unchanged) |
| report run | `results/runs/20260917T193922Z-phase1-step1-report` (`experiments/phase1/step1_report.py`) |
| original run (for comparison) | `results/runs/20260830T175149Z-stage3-heldout-frozen` (job 554591, A30) |
| figure | `results/figures/phase1-step1-heldout2.png` via `src/figstyle.py::save_figure` (`experiments/phase1/step1_figure.py`); rendered from `step1-report.json`, not visually inspected by the agent |

Anchor failures 0/0. R0 (contact): heldout2 prompts duplicated in `dev.jsonl`: **0**; in `heldout.jsonl`: **0**. Combined = 400 records with no exclusions.

## Eligibility (greedy, same script and thresholds)

heldout2, real/zero, 60 pairs: pair eligibility AB **0.900** (PASS ≥ 0.80), BA 0.850, all four variants 0.800; variant accuracy 0.938; alt-answer rate 0.000. Application held-out: 0.950 (A30). Padding control: 2/8 mismatched batched-vs-unbatched (application: 1/8).

## Dev re-scored on L40S (arm 3 fit only; reference)

Dev direction fracs at the frozen layers reproduce the A30 values exactly (jlens relcomp 0.775, qmark 0.675; logitlens 0.675 / 0.725). Per-record margins differ slightly by architecture (shadow negative at relcomp 9/40 vs 10/40 on A30). Dev is not part of any tally below.

## Results — original (n=160) / new (n=240) / combined (n=400)

Direction frac = fraction of records where the lens ranks the correct city above the alternative. ctrl = same, against the label-permutation key. rank = median rank of the correct city (of 248K). shadow = fraction of records where the model's own next-token preference at that position already favours the correct city. model-wrong acc = lens accuracy on the records where that preference is wrong (n in parentheses). r = Pearson r between lens margin and model margin over all records.

### J-Lens

| set | position | frac | ctrl | rank | shadow | model-wrong acc (n) | model-right acc | r |
|---|---|---|---|---|---|---|---|---|
| original | prequery | 0.512 | 0.519 | 373 | 0.481 | 0.282 (78) | — | +0.712 |
| original | relcomp | 0.781 | 0.519 | 128 | 0.800 | **0.344 (32)** | 0.891 | +0.884 |
| original | qmark | 0.669 | 0.556 | 95 | 0.731 | **0.125 (40)** | 0.872 | +0.916 |
| original | final | 0.956 | 0.544 | 21 | 0.931 | 0.667 (9) | — | +0.656 |
| new | prequery | 0.496 | 0.525 | 394 | 0.496 | 0.235 (119) | — | +0.696 |
| new | relcomp | 0.733 | 0.496 | 132 | 0.733 | **0.213 (61)** | 0.909 | +0.913 |
| new | qmark | 0.667 | 0.454 | 93 | 0.758 | **0.089 (56)** | 0.852 | +0.918 |
| new | final | 0.942 | 0.508 | 21 | 0.942 | 0.571 (14) | — | +0.737 |
| combined | prequery | 0.502 | 0.522 | 387 | 0.490 | 0.254 (197) | — | +0.702 |
| combined | relcomp | 0.752 | 0.505 | 129 | 0.760 | **0.258 (93)** | 0.901 | +0.903 |
| combined | qmark | 0.667 | 0.495 | 93 | 0.748 | **0.104 (96)** | 0.860 | +0.917 |
| combined | final | 0.948 | 0.522 | 21 | 0.938 | 0.609 (23) | — | +0.710 |

(model-right acc for prequery/final omitted; in `step1-report.json`.)

### Logit lens

| set | position | frac | ctrl | rank | model-wrong acc (n) | r |
|---|---|---|---|---|---|---|
| original | relcomp | 0.688 | 0.519 | 393 | 0.250 (32) | +0.707 |
| original | qmark | 0.738 | 0.544 | 82 | 0.200 (40) | +0.924 |
| new | relcomp | 0.692 | 0.504 | 367 | 0.246 (61) | +0.773 |
| new | qmark | 0.750 | 0.467 | 106 | 0.196 (56) | +0.919 |
| combined | relcomp | 0.690 | 0.510 | 380 | 0.247 (93) | +0.748 |
| combined | qmark | 0.745 | 0.497 | 98 | 0.198 (96) | +0.921 |
| new | prequery | 0.512 | 0.492 | 72,325 | 0.420 (119) | +0.295 |
| new | final | 0.900 | 0.479 | 15 | 0.286 (14) | +0.833 |

### Random-transport control (J-Lens layers, norm-matched random matrix)

new: prequery 0.504 / ctrl 0.508 / rank 135,039; relcomp 0.504 / 0.529 / 156,481; qmark 0.512 / 0.487 / 170,558; final 0.529 / 0.487 / 149,607. Combined: relcomp 0.513 / 0.498 / 160,954; qmark 0.510 / 0.475 / 170,491. Original: relcomp 0.525 / 0.450 / 167,252; qmark 0.506 / 0.456 / 170,491.

### Arm 3 (difference-in-means, L30, fit on all of dev, applied unchanged)

| position | original (160) | new (240) | combined (400, pooled by count) |
|---|---|---|---|
| prequery | 0.506 | 0.487 | 0.495 |
| relcomp | 0.525 | 0.508 | 0.515 |
| qmark | 0.731 | 0.721 | 0.725 |
| final | 0.725 | 0.617 | 0.660 |

### By template (J-Lens, new draw)

relcomp: T1 0.95 (n=44), T2 0.73 (40), T3 0.67 (36), T4 0.70 (40), T5 0.63 (40), T6 0.70 (40). qmark: T1 0.80, T2 0.55, T3 0.69, T4 0.75, T5 0.63, T6 0.58. (Original relcomp: T1 0.96 … T5/T6 0.68.)

### Label-permutation collision audit (six-city pool), new draw

n=240: identical pair 10, swapped 9, one shared city 134, fully disjoint 87 (36%). Original: 4 / 8 / 83 / 65 (41%). Same caveat as the application: the control is weaker than a fully disjoint permutation would be.

## Pre-registered rules — which branch fired

- **R0 (contact):** 0 heldout2 prompts in dev, 0 in the original held-out. Nothing excluded.
- **R1 (replication):** new-draw J-Lens frac − control at relcomp = 0.733 − 0.496 = **+0.237** (≥ 0.10 required) → **REPLICATES**. qmark gap (reported, not deciding): 0.667 − 0.454 = +0.213 (original +0.11).
- **R2 (band 0.25–0.45, combined, relcomp):** combined J-Lens accuracy on model-wrong records = **0.258 (n=93)** → **inside the band**, at its lower edge. Stated plainly, as the brief asks: the new draw alone is **0.213 (n=61)**, below the band's lower bound; the combined value sits inside only because the original 0.344 (n=32) pulls it up. The direction of the change vs the application's number is down, not up.
- **R3 (attribution):** new-draw accuracy on model-wrong records at relcomp is 0.213 (n=61), not ≥ 0.60 → the "lens follows the model" reading is **not contradicted** on fresh data.
- Eligibility 0.900 ≥ 0.60 → readouts are interpretable under the pre-registered STOP rule.

## Pre-registered predictions (agent's) — scored

| prediction | observed (new) | hit? |
|---|---|---|
| jlens relcomp frac 0.70–0.85, ctrl 0.45–0.55 | 0.733, 0.496 | yes |
| jlens qmark 0.60–0.75 | 0.667 | yes |
| shadow frac at relcomp 0.75–0.85 | 0.733 | **no** (just under) |
| r(lens, model) > 0.80 at relcomp and qmark | +0.913, +0.918 | yes |
| jlens acc on model-wrong at relcomp 0.20–0.50, n≈40–60 | 0.213, n=61 | yes (edge) |
| arm 3 relcomp 0.45–0.60; qmark 0.65–0.80 | 0.508; 0.721 | yes |
| median rank jlens < logitlens at relcomp | 132 vs 367 | yes |
| eligibility ≥ 0.85 | 0.900 | yes |

## Deviations from the pre-registration

1. Amendment 1 (dedupe within the draw) — logged and committed before job 587809; index 44 skipped; city-pair balance 19–21 pairs per class rather than exactly 20.
2. Arm 3 "combined" is pooled from the two runs' aggregate counts (exact for accuracy, since R0 excluded nothing).
3. GPU architecture differs from the application run (L40S vs A30). Dev direction fracs reproduce exactly; per-record margins differ at the bf16 level (see dev section).

## Three numbers for Jason to hand-check

1. new jlens relcomp frac **0.733**, ctrl **0.496** — `results/runs/20260917T193052Z-stage3-heldout-frozen/outputs/stage3-heldout-frozen.json`, `summary.heldout.jlens.relcomp.frac` / `.control_frac` (also stdout line "heldout  jlens  relcomp  L30").
2. new model-wrong n = **61** at relcomp — same file, `shadow_summary.heldout.relcomp.n_negative` (stdout "shadow heldout relcomp … neg=61/240"); the 0.213 is the fraction of those 61 records whose `records[].scores.relcomp.intermediate.rank_correct < rank_incorrect` for arm `jlens` — `results/runs/20260917T193922Z-phase1-step1-report/outputs/step1-report.json`, `table.new.jlens.relcomp.acc_model_wrong`.
3. combined **0.258 (n=93)** — same report file, `table.combined.jlens.relcomp.acc_model_wrong` / `.n_model_wrong`; 93 = 32 + 61.
