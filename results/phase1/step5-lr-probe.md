# Phase 1, step 5 — trained linear probe beside difference-in-means

Status: **agent-unverified**. Numbers only; interpretation is Jason's.
Pre-registration: `llm/memory_bank/research-learning-log.md`, entry "Phase 1,
steps 2–5" (commit `7c55733`); Amendment 2 (reporting breakdown, `6c8e7f3`)
committed before any breakdown number existed.

## Provenance

| item | value |
|---|---|
| main job | Falcon **587868** (dependency on step 2's 587865), commit `7c55733`, L40S node (CPU work; sklearn 1.9.0); smoke pass (blocks 30, 31) deleted; full run exit 0; log `results/slurm-logs/phase1-step5-587868.out` |
| main run | `results/runs/20260917T203740Z-phase1-step5-lr-probe` (`experiments/phase1/step5_lr_probe.py --residual-dir /scratch/djjay/mats12/phase1/residuals --step2-run results/runs/20260917T202900Z-phase1-step2-fact-tokens --jobs 16`); output `outputs/step5-lr-probe.json` |
| breakdown job (Amendment 2) | Falcon **587883**, commit `6c8e7f3`; run `results/runs/20260917T205754Z-phase1-step5-breakdown` (`step5_breakdown.py`, same folds and fits at L30, per-record margins saved) |
| inputs | residuals from step 2 (all 32 block outputs × 10 positions, fp16, outside the repo) for the combined held-out: heldout 160 + heldout2 240 = 400 records, 100 pairs |
| protocol | leave-one-pair-out (100 folds). LR: sklearn `LogisticRegression(C=1.0, lbfgs, max_iter=500, tol=1e-3)`, `StandardScaler` fit on the training fold, multinomial over the token-id classes present. DiM: `supervised_reference.fit_centroids` / `margin_of` on the same fold. Two-way margin correct − alternative; label-permutation control (derangement, seed 20260827) for both. All records scorable in every cell. |
| tables / figure | `experiments/phase1/step5_report.py`; `results/figures/phase1-step5-lr-probe.png` via `figstyle.save_figure` (rendered, not visually inspected by the agent) |

## Results at the frozen block L30 (combined held-out)

| cell | LR acc | LR ctrl | DiM acc | DiM ctrl | n | LR − DiM | LR on model-wrong records (n) | DiM on model-wrong |
|---|---|---|---|---|---|---|---|---|
| prequery → CITY | 0.477 | 0.555 | 0.507 | 0.492 | 400 | −0.030 | 0.419 (198) | 0.273 |
| relcomp → CITY | **0.897** | 0.520 | 0.620 | 0.463 | 400 | +0.277 | **0.850 (93)** | 0.570 |
| qmark → CITY | **0.945** | 0.520 | 0.700 | 0.500 | 400 | +0.245 | **0.888 (98)** | 0.225 |
| final → CITY | 0.998 | 0.537 | 0.868 | 0.477 | 400 | +0.130 | 1.000 (24) | 0.375 |
| city → PERSON | 0.740 | 0.537 | 0.514 | 0.482 | 800 | +0.226 | — | — |
| person → CITY | 0.705 | 0.480 | 0.520 | 0.516 | 800 | +0.185 | — | — |
| period → PERSON | 0.927 | 0.519 | 0.525 | 0.506 | 800 | +0.402 | — | — |
| period → CITY | **1.000** | 0.494 | 0.606 | 0.490 | 800 | +0.394 | — | — |

"model-wrong" = records where the model's own next-token preference at that anchor favours the wrong city, re-measured in step 2's forward pass: 93 at relcomp (step 1's combined count was also 93) and 98 at qmark (step 1: 96; a two-record bf16 difference between runs).

DiM here is fit on 99 pairs per fold (the application's arm 3 was fit on dev's 10 pairs and read 0.515 at relcomp on the same 400 records in step 2).

## Layer curves (LR / DiM accuracy, combined held-out; reported, not selected on)

| cell | L0 | L5 | L10 | L15 | L20 | L25 | L30 | L31 | best LR block |
|---|---|---|---|---|---|---|---|---|---|
| relcomp → CITY | 0.50/0.50 | 0.61/0.50 | 0.93/0.54 | **0.99**/0.59 | 0.99/0.54 | 0.97/0.51 | 0.90/0.62 | 0.89/0.65 | L19 0.993 |
| qmark → CITY | 0.51/0.50 | 0.60/0.50 | 0.91/0.57 | 0.96/0.61 | 0.95/0.68 | 0.95/0.70 | 0.94/0.70 | 0.93/0.71 | L17 0.975 |
| period → CITY | 1.00/1.00 | 1.00/0.82 | 1.00/0.87 | 1.00/0.82 | 1.00/0.77 | 0.99/0.78 | 1.00/0.61 | 1.00/0.61 | L0 1.000 |
| city → PERSON | 0.88/0.50 | 0.79/0.53 | 0.80/0.54 | 0.81/0.55 | 0.82/0.52 | 0.80/0.52 | 0.74/0.51 | 0.77/0.52 | L2 0.882 |

LR accuracy on model-wrong records at relcomp by block: L0 0.49, L5 0.67, L10 0.92, L15 **0.98**, L20 0.99, L25 0.97, L30 0.85, L31 0.80 (n = 93).

## Breakdown at L30 (Amendment 2; same folds and fits)

| cell | AB / BA fact order | heldout / heldout2 | first / second sentence (fact tokens) | by template (LR) |
|---|---|---|---|---|
| relcomp → CITY (LR) | 0.870 / 0.925 | 0.863 / 0.921 | — | T1 1.00, T2 0.94, T3 0.88, T4 0.95, T5 0.88, **T6 0.72** |
| qmark → CITY (LR) | 0.935 / 0.955 | 0.950 / 0.942 | — | T1 1.00 … T6 0.79 |
| prequery → CITY (LR / DiM) | 0.495 / 0.460 (DiM **0.725 / 0.290**) | 0.494 / 0.467 | — | 0.43–0.50 |
| person → CITY (LR) | 0.708 / 0.710 | 0.713 / 0.706 | **0.500 / 0.918** | 0.70–0.72 |
| period → PERSON (LR / DiM) | 0.938 / 0.918 | 0.934 / 0.923 | **1.000 / 0.855** (DiM 1.000 / **0.050**) | 0.86–0.98 |
| period → CITY (LR / DiM) | 1.000 / 1.000 | 1.000 / 1.000 | 1.000 / 1.000 (DiM 1.000 / **0.213**) | 1.00 |
| city → PERSON (LR) | 0.753 / 0.728 | 0.747 / 0.735 | 0.763 / 0.718 | 0.71–0.79 |

Raw-data observations, no interpretation: (i) at the person token of the FIRST sentence the LR probe is at chance for CITY (0.500) and at the second sentence's person token it is 0.918; (ii) at prequery DiM is 0.725 in AB order and 0.290 in BA order while LR is at chance in both; (iii) at the second sentence's period DiM picks the wrong person / city (0.050 / 0.213) while LR reads 0.855 / 1.000.

## Cross-reference: what J-Lens reads at the same anchors, by block (from step 2's records; `experiments/phase1/step2_layercurve.py`, `outputs/step2-layercurve.json` in the step-2 run)

J-Lens direction frac at relcomp, combined held-out (n = 400): L0 0.49, L9 0.52, L15 0.53, L18 0.52, L21 0.59, L24 0.65, L27 0.71, L29 0.76, L30 0.75. On the 93 model-wrong records: L9 0.38, L15 0.37, L18 0.63, L21 0.47, L24 0.53, L27 0.42, L30 0.26; maximum over blocks 0.634 (L18). Logit lens at relcomp on model-wrong records: maximum 0.699 (L24), L30 0.25. At qmark, J-Lens on the 98 model-wrong records: L0–L6 0.66, L18–L30 0.10–0.31.

## Pre-registered rules — which branch fired

- **R5 primary (relcomp L30: LR − DiM ≥ 0.10 and LR ≥ 0.65):** 0.897 − 0.620 = +0.277, LR 0.897 → **fires: "the application's probe was too weak; the binding is linearly present at relcomp."**
- **R5 attribution (LR on model-wrong records at relcomp ≥ 0.65, n ≥ 60):** 0.850 (n = 93) → **fires: "a trained probe reads the binding where the model's preference is wrong"** — reported, as pre-registered, as reversing the application's attribution that no method finds binding at relcomp.
- "Not the probe's weakness" (LR ≤ 0.60) did not fire.

## Predictions (agent's) — scored

| prediction | observed | hit? |
|---|---|---|
| LR at relcomp L30 0.55–0.70 | 0.897 | **no** (higher) |
| DiM 0.50–0.55 | 0.620 | no (higher) |
| LR on model-wrong at relcomp ≤ 0.6 | 0.850 | **no** |
| LR at period → CITY ≥ 0.95 | 1.000 | yes |

## Deviations / caveats

1. The breakdown (Amendment 2) is a reporting addition; no rule depends on it.
2. LR is fit with 2560 features on ~396 training records per fold; the label-permutation control (0.48–0.56 everywhere) is the check that it does not fit noise. The pair-level fold means the held-out pair's two cities are never seen with the held-out pair's names, but the six city classes are shared across pairs by construction of the pool.
3. Template T6 ("paints at / stores") is the weakest cell for LR at relcomp (0.72) and qmark (0.79); it was also among the weakest for J-Lens in the application's by-template table (relcomp 0.68, qmark 0.54).

## Three numbers for Jason to hand-check

1. LR at relcomp L30, combined = **0.8975** (ctrl 0.520), n = 400 — `outputs/step5-lr-probe.json`, `results["relcomp/CITY"].per_layer["30"].lr.acc` / `.lr_ctrl.acc`.
2. LR on model-wrong records at relcomp L30 = **0.8495**, n_scored = 93 — same file, `results["relcomp/CITY"].per_layer["30"].model_wrong.lr.acc`; and at L15 = **0.98** (`per_layer["15"]`).
3. J-Lens at relcomp on the same 93 records, L30 = **0.26**, maximum over blocks **0.634** at L18 — step-2 run `outputs/step2-layercurve.json`, `["relcomp/jlens"][30].model_wrong_acc` and `[18]`.
