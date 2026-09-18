# Phase 1 summary — what changed, in numbers

Written 2026-09-17/18 by the agent after steps 1–5; every number
`agent-unverified` until Jason's hand-check. Branch `research/phase1`, not
merged. Interpretation is Jason's; this is the table and the pointers.

## The five results

| step | question | pre-registered rule | what fired | headline number (combined held-out unless stated) |
|---|---|---|---|---|
| 1 fresh draw (`step1-heldout2.md`) | does the Stage 3 result replicate on 60 new pairs? | R1 gap ≥ 0.10 at relcomp; R2 band 0.25–0.45 | **replicates**; band edge | J-Lens relcomp 0.733 vs ctrl 0.496 (n=240); combined acc on model-wrong records 0.258 (n=93), new draw alone 0.213 (n=61) |
| 2 fact tokens (`step2-fact-tokens.md`) | is the pairing linearly stored where the fact is stated? | R2.1 arm 3 ≥ 0.65 and ≥ ctrl+0.15 at L30; R2.2 J-Lens gap ≥ 0.15 | **readable at period → CITY**; J-Lens **does not read it** at L30 | arm 3 period → CITY 0.664 (ctrl 0.502) at L30, 0.994 at block 0; J-Lens there 0.559 (ctrl 0.507) at L30, 0.871 at L9 |
| 3 twin patching (`step3-patching.md`) | does any single-position state carry the binding causally? | flip ≥ 0.50 and ≥ 2× unrelated donor | **does not** at relcomp / qmark / prequery at any block; **carries** at final (with a 0.45 unrelated-donor flip rate attached) | twin flip 0.000 at relcomp L30, 0.005 at qmark L27 (n=382 base-right); max 0.05 at qmark L16; final L30 0.935 vs unrelated 0.450 |
| 4 resample (`step4-resample.md`) | does the readout follow the stated fact? | NEW-vs-OLD ≥ 0.75 and ≥ ctrl+0.30 | **follows** | J-Lens 0.970 (relcomp) / 0.993 (qmark) vs 0.045 / 0.000 unmodified; model 0.983 / 1.000 |
| 5 trained probe (`step5-lr-probe.md`) | was the application's probe just too weak? | LR − DiM ≥ 0.10 and LR ≥ 0.65; LR on model-wrong ≥ 0.65 | **both fired** | LR relcomp L30 0.897 (ctrl 0.520) vs DiM 0.620; on the 93 model-wrong records 0.850 (0.98 at L15); J-Lens on the same records ≤ 0.634 at any block |

## What changes relative to the application's claims

| application claim (writeup/main.md, exec summary) | Phase 1 status | pointer |
|---|---|---|
| The relcomp / qmark positions are real, not forking paths (held-out 0.781 / 0.669 vs ~0.52 control) | **Confirmed** on a fresh draw (0.733 / 0.667 vs 0.496 / 0.454, n=240) and on the pool (0.752 / 0.667, n=400). | step 1 |
| J-Lens follows the model's preference; on model-wrong records it is below chance (0.344 / 0.125) | **Confirmed and sharpened**: 0.213 / 0.089 on the new draw (n=61 / 56); 0.258 / 0.104 on the pool (n=93 / 96); r(lens, model) +0.91 / +0.92. | step 1 |
| "Even a probe trained with the answer key found nothing at the frozen position: 0.525, chance" — i.e. the binding is not linearly present at relcomp | **Reversed.** The difference-in-means probe fit on 10 dev pairs was the limitation, not the residual: a logistic-regression probe (LOPO, 100 pairs) reads the queried city at relcomp at 0.897 (L30) and 0.99 (L15–L20), and 0.850 / 0.98 on the records where the model's preference is wrong. Difference-in-means fit on 99 pairs reaches 0.620. | step 5 |
| Therefore "no method found a binding signal there" / "the lens is guessing the model's answer, not reading its memory" | First half **withdrawn** (a method does find it). Second half **strengthened**: J-Lens at relcomp is at chance (0.53) at the very blocks where the trained probe reads 0.99, rises only with the model's own preference from L24, and never exceeds 0.634 on the model-wrong records at any block. | steps 2, 5 |
| Rank localisation (J-Lens median rank 128 vs 393 for the logit lens at relcomp) survives; §4.2 | **Confirmed** (129 vs 380 on the pool) and the co-occurrence door is closed: the readout follows a rewritten fact 0.970 / 0.993 of the time against 0.045 / 0.000 when the word is absent. | steps 1, 4 |
| The pairing must be stored somewhere at construction; never looked | **Looked.** At the period ending each person sentence the city is linearly present (arm 3 0.664 at L30, 0.994 at block 0; LR 1.000 at every block) and the person is (LR 0.927); at the city token the person is (LR 0.740); at the person token the city is readable only in the second sentence (0.918 vs 0.500), as token order dictates. J-Lens at the period reads the city at L9 (0.871) but not at L30 (0.559). | steps 2, 5 |
| Claims are correlational only; no causal test | **Causal test run.** Replacing the residual at ONE (anchor, block) with the swapped twin's flips the answer in 0.000 of records at relcomp L30, ≤ 0.005 at the qmark cells and 0.000 at prequery, at every block (max 0.05 at qmark L16; margin moves −0.5 logits at relcomp L15–L16 and nowhere else); the twin residuals at those anchors have cosine 0.97–0.995. Only the final position flips (0.935 at L30), and a norm-matched unrelated donor flips 0.45 there. So the linearly readable binding at relcomp (step 5) is not carried by that single position's state in a way that a single-position swap can move. | step 3 |
| Six-city pool weakens the label-permutation control | Still true (87/240 fully disjoint on the new draw); the trained-probe control (0.48–0.56) and the unmodified-prompt control in step 4 are the cleaner nulls. | steps 1, 4, 5 |

Smaller corrections: the application's dev arm-3 selection layer was L30; on the combined held-out the dev-LOPO argmax is L31 for most cells (reported, not used).

## Where Phase 2 starts (agent's suggestion, for Jason to accept or change)

The method claim the plan set out to build — "a cheap check that tells whether a lens reads stored facts or predicts the upcoming output" — now has its positive control: on this task and model there IS a linearly readable binding at relcomp mid-stack (LR 0.99, robust on model-wrong records), and J-Lens does not read it while a trained probe does. The audit script for Phase 2 should therefore report, per (position, block): the lens's accuracy on model-wrong records, r(lens margin, model margin), AND a leave-one-pair-out logistic-regression ceiling on the same residuals — the third column is what separates "not stored" from "not read". Step 3 adds the caveat that goes with it: a linearly readable single-position state need not be a single-position causal state (0.000 flips at relcomp), so the audit's "stored" column is about readability, not about what the model uses. Phase 2 items (second model with a released lens; second task family; tuned lens or trained probe as the readout under audit) apply unchanged; the fact-token positions and the resample control should be part of the standard battery, and the patching sweep is cheap enough (3.6 GPU-hours here) to keep.

Hours: Phase 1 took one agent session (2026-09-17 → 18, ~9 h wall clock; ~6.5 GPU-hours on Falcon across jobs 587809, 587865–587868, 587883, 587888); uncounted.

## The three most load-bearing numbers — hand-check these first

1. **LR on model-wrong records at relcomp, L30 = 0.8495 (n = 93)** — `results/runs/20260917T203740Z-phase1-step5-lr-probe/outputs/step5-lr-probe.json`, `results["relcomp/CITY"].per_layer["30"].model_wrong.lr.acc`. This is the number that reverses the application's "no method finds it". Re-derive: fold_eval in `experiments/phase1/step5_lr_probe.py`, folds by `pair_id`, residuals in `/scratch/djjay/mats12/phase1/residuals/{heldout,heldout2}.pt` position index 1 (`relcomp`), block 30; "model-wrong" = `shadow[...]["relcomp"]["CITY"]["margin"] < 0` in the step-2 records file.
2. **J-Lens on the same 93 records at relcomp, max over blocks = 0.634 (L18), L30 = 0.26** — `results/runs/20260917T202900Z-phase1-step2-fact-tokens/outputs/step2-layercurve.json`, `["relcomp/jlens"][18].model_wrong_acc`, `[30]`. Same records, same forward pass, lens logits from `lens.transport` + `lm.unembed`.
3. **New-draw J-Lens relcomp frac 0.733 vs control 0.496 (n = 240)** — `results/runs/20260917T193052Z-stage3-heldout-frozen/outputs/stage3-heldout-frozen.json`, `summary.heldout.jlens.relcomp.frac` / `.control_frac`. This is the replication the rest stands on.

Fourth, for the causal claim: **twin flip rate at relcomp L30 = 0.000 (n = 382 base-right), unrelated donor 0.000** — `results/runs/20260917T202907Z-phase1-step3-patching/outputs/step3-patching.json`, `summary.combined["relcomp/30"].twin.flip_rate`; and the one place anything moves, `summary.combined["relcomp/16"].twin_mean_delta_all` = −0.53.

## Housekeeping

Run directories, Slurm logs, notes and figures are committed on `research/phase1` (`results/phase1/step{1,2,3,4,5}-*.md`, `results/figures/phase1-step*.png`, `FIGURE-REGISTRY.md`). Residuals for step 5 live outside the repo at `/scratch/djjay/mats12/phase1/residuals/` (720 MB). Every step's learning-log entry has a filled "Result" block. Nothing under the application's `results/runs/`, `experiments/stage3/freeze.json` or `writeup/main.md` was modified. Hours are uncounted (post-MATS section of the time log).
