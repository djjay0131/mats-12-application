# Phase 1, step 3 — activation patching between swapped twins

Status: **agent-unverified**. Numbers only; interpretation is Jason's.
Pre-registration: `llm/memory_bank/research-learning-log.md`, entry "Phase 1,
steps 2–5" (commit `7c55733`); Amendment 3 (`eee944f`, backup-run precedence)
committed before any held-out number existed. The rule for this step is the
agent's (the brief's "as specified" text was not available) and is marked so
in the log.

## Provenance

| item | value |
|---|---|
| job | Falcon **587866**, commit `7c55733`, NVIDIA L40S (fal044), **3:35:41** of a 4:00:00 limit, exit 0; smoke pass (4 records/split, blocks 30–31) deleted; log `results/slurm-logs/phase1-step3-587866.out` |
| run | `results/runs/20260917T202907Z-phase1-step3-patching` (`experiments/phase1/step3_patching.py`, full sweep: 4 anchors × 32 blocks × 2 donors per record) |
| outputs | `outputs/step3-patching.json` (per-cell summaries per split and combined), `outputs/step3-records.json.gz` (every record × cell: margin after, delta, flip, argmax change, cosine) |
| backup | job 587888 (reduced sweep) completed too; per Amendment 3 its run directory `20260917T210404Z-phase1-step3-patching` was deleted unread, and only its Slurm log is kept (`phase1-step3b-587888.out`) |
| tables / figure | `experiments/phase1/step3_report.py`; `results/figures/phase1-step3-patching.png` via `figstyle.save_figure` (rendered, not visually inspected by the agent) |
| data | dev 40, heldout 160, heldout2 240 records; every record has a twin (same pair and fact order, other variant; identical token count and anchor positions — 0 mismatches); unrelated donors found for all held-out records and 32/40 dev records (`skipped: dev:no-unrelated-donor: 8`) |

Measure: at the final position, margin = logit[X's answer] − logit[Y's answer] (Y = twin; Y's answer is X's alternative answer). Unpatched, the margin is positive for 382/400 held-out records ("base-right"; dev 40/40). "flip" = margin > 0 before and < 0 after, over base-right records. Δ = mean change in margin over all records. Control (a): the same cell patched from an unrelated record of the same template / fact order / variant, norm-matched to X's own residual. Control (b): the prequery row.

## Primary (frozen) cells — combined held-out (n = 400, base-right 382)

| cell | twin flip | twin Δ (all) | full-vocab argmax changed | unrelated flip | unrelated Δ | cos(X, Y) at cell | rule |
|---|---|---|---|---|---|---|---|
| prequery L24 | 0.000 | +0.00 | 0.005 | 0.000 | −0.00 | 0.988 | does not carry |
| prequery L25 | 0.000 | +0.00 | 0.011 | 0.000 | −0.00 | 0.989 | does not carry |
| prequery L30 | 0.000 | −0.00 | 0.005 | 0.000 | −0.00 | 0.987 | does not carry |
| **relcomp L30** | **0.000** | +0.00 | 0.000 | 0.000 | −0.00 | 0.995 | **does not carry** |
| **qmark L27** | **0.005** | −0.20 | 0.021 | 0.003 | −0.03 | 0.970 | **does not carry** |
| qmark L29 | 0.000 | −0.08 | 0.013 | 0.003 | −0.02 | 0.971 | does not carry |
| qmark L30 | 0.000 | +0.00 | 0.008 | 0.000 | −0.01 | 0.971 | does not carry |
| final L27 | 0.924 | −4.36 | 0.118 | 0.432 | −1.79 | 0.951 | carries (0.924 ≥ 2 × 0.432) |
| final L30 | 0.935 | −4.59 | 0.120 | 0.450 | −2.01 | 0.959 | carries (0.935 ≥ 2 × 0.450) |

Per split (twin flip at relcomp L30 / qmark L27 / final L30): dev 0.000 / 0.000 / 1.000 (n = 40); heldout 0.000 / 0.000 / 0.934 (n = 160, base-right 151); heldout2 0.000 / 0.009 / 0.935 (n = 240, base-right 231). Unrelated-donor flips at final L30: dev 0.500 (n = 32 with a donor), heldout 0.470, heldout2 0.437. Reverse flips (unpatched-wrong → right after the twin patch) on the 18 base-wrong held-out records: 0.000 at every primary cell.

## Layer sweep (combined held-out; reported, not selected on)

Twin flip rate by block (unrelated donor in parentheses where non-zero):

- prequery: 0.00 at every block (max 0.01 at L14, L16).
- relcomp: 0.00 at L0–L10; 0.01 at L11–L14; **0.04 at L15–L16** (unrelated 0.01); 0.00 from L17 on.
- qmark: 0.00 at L0–L12; 0.01 at L13–L14; **0.04–0.05 at L15–L16** (unrelated 0.01); 0.02 L17, 0.01 L18, then ≤ 0.01.
- final: 0.00 to L16; 0.09 L17; 0.14 L18; 0.41–0.45 L19–L22 (unrelated 0.08–0.09); 0.58–0.60 L23–L26 (unrelated 0.24–0.26); 0.92–0.95 L27–L31 (unrelated 0.43–0.50).

Mean margin change by block (twin): relcomp −0.46 at L15 and −0.53 at L16, ≤ 0.11 in magnitude elsewhere; qmark −0.37 / −0.44 / −0.33 at L15–L17, −0.20 at L27, ≤ 0.13 elsewhere; final from −0.99 (L17) to −4.85 (L31); prequery ≤ 0.09 everywhere.

Raw-data observation, no interpretation: the only blocks at which patching relcomp or qmark moves the answer margin at all (−0.5 logits, 4–5 % flips) are L15–L16, the blocks at which step 5's trained probe reads the binding at relcomp at 0.99; the twin residuals at those anchors are nearly identical (cosine 0.97–0.995 at the frozen blocks).

## Pre-registered rule — which branch fired

Rule (agent's): twin flip ≥ 0.50 and ≥ 2 × unrelated → "carries the binding causally"; twin flip ≤ unrelated + 0.10 → "does not"; else "partial".

- **relcomp L30: does not carry** (0.000 vs 0.000). **qmark L27 / L29 / L30: does not carry** (≤ 0.005 vs ≤ 0.003). **prequery L24 / L25 / L30: does not carry** (0.000). No cell at these three anchors is "partial" at any block: the maximum twin flip rate is 0.05 (qmark L16).
- **final L27 / L30: carries** by the rule (0.924 / 0.935 vs 0.432 / 0.450) — reported with its control attached: the norm-matched unrelated donor flips 43–50 % of records at the same cells, and the rule's 2× threshold is met with 0.06 / 0.04 to spare.
- Control (b), the prequery row, is flat at every block.

## Predictions (agent's) — scored

| prediction | observed (combined) | hit? |
|---|---|---|
| final L27/L30 flips ≥ 0.8 | 0.924 / 0.935 | yes |
| relcomp L30 ≤ 0.3 | 0.000 | yes (trivially) |
| qmark L27 0.2–0.5 | 0.005 | **no** (lower) |
| prequery L25 0.2–0.7 | 0.000 | **no** (lower) |
| unrelated donor ≤ 0.15 everywhere except final | ≤ 0.01 | yes |

## Deviations / caveats

1. Dev's unrelated-donor control covers 32/40 records (8 records had no other pair with the same template, fact order and variant); held-out coverage is complete.
2. Per-record dev results were printed before the held-out splits were processed (same job), as pre-registered; the dev-first ordering had no consequence for the rule.
3. The backup run (Amendment 3) completed but was deleted unread because the primary job completed; only its Slurm log remains.

## Three numbers for Jason to hand-check

1. relcomp L30 twin flip = **0.000** over 382 base-right records, unrelated 0.000 — `outputs/step3-patching.json`, `summary.combined["relcomp/30"].twin.flip_rate` / `.unrelated.flip_rate`, `.n_base_right`.
2. final L30 twin flip **0.935** and unrelated **0.450** — `summary.combined["final/30"].twin.flip_rate`, `.unrelated.flip_rate`.
3. relcomp L16 twin mean Δmargin **−0.53** and flip 0.04 — `summary.combined["relcomp/16"].twin_mean_delta_all`, `.twin.flip_rate` (the only non-final blocks where anything moves).
