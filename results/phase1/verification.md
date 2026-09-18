# Phase 1 — agent verification pass and manual-check list

Status: this is the **agent's** pass (2026-09-18). It raises no number
above `agent-unverified`; that happens only when Jason completes the manual
list at the end. Everything here is reproducible from the repo plus the
residual files on `/scratch`.

## What the pass did

Two scripts, written fresh for this purpose and importing nothing from the
experiment or report code:

- `experiments/phase1/verify_vm.py` (run on agents4research, read-only):
  re-derives every load-bearing number in the five step notes from the raw
  per-record run outputs (`stage3-heldout-frozen.json`,
  `step2-records.json.gz`, `step3-records.json.gz`, `step4-resample.json`,
  `step5-breakdown.json`), and checks provenance: manifest git SHA = the
  pre-registration commit, Slurm job id, run status, dataset sha256, record
  and pair counts, prompt-level contact between heldout2 and dev/heldout,
  and `git diff mats12-submitted..HEAD` on `freeze.json`, `writeup/main.md`
  and the application's run directories (must be empty).
- `experiments/phase1/verify_arc.py` (Falcon jobs 588470 → timed out after
  three lines; 588537 with a 2 h limit, log
  `results/slurm-logs/phase1-verify-588537.out`): re-fits the step-5 probe
  from the saved residuals with its own fold code and three estimators, adds
  a label-permutation null and a first-mentioned-city proxy, and re-derives
  arm 3 at the period from raw residuals.

## Part 1 — re-derivation from raw outputs (67 checks)

**66 pass, 1 rounding.** Every number below was recomputed independently and
matched the note to the precision the note states:

| step | numbers re-derived (all matched) |
|---|---|
| provenance | six run manifests at commits `fe1ca16` / `7c55733` / `6c8e7f3` with job ids 587809, 587865–587868, 587883, status ok; `heldout2.jsonl` sha256 = manifest; 240 records, 60 pairs, 0 duplicate prompts, 0 prompts shared with dev or heldout; **freeze.json, writeup/main.md and the application run dirs are byte-identical to tag `mats12-submitted`** |
| 1 | new draw n=240; J-Lens relcomp frac 0.733, ctrl 0.496, median rank 132; model-wrong n=61, acc 0.213; combined model-wrong n=93, acc 0.258; original 0.344 reproduced from the application run file |
| 2 | 400 records, 0 fact-position failures; J-Lens period→CITY pooled n=800, L30 0.559 (ctrl 0.507), L9 0.871; relcomp L30 0.752, L15 0.53; model-wrong n=93 and **the same 93 record ids as step 1** (independent forward passes); J-Lens on them L30 0.26, L18 0.634, and L18 is the maximum over all 31 blocks |
| 3 | n=400, base-right 382; twin flip relcomp/30 = 0.000, qmark/27 = 0.005, final/30 = 0.935, unrelated final/30 = 0.450; relcomp/16 mean Δ −0.53; every twin shares its record's pair_id. *Rounding*: the maximum non-final flip rate is **0.047** (qmark L16), written as 0.05 in the note |
| 4 | n=400; J-Lens NEW>OLD relcomp modified 0.970 / unmodified 0.045, qmark 0.993; for every record the replacement word is absent from the original prompt and the token count is unchanged; 21 distinct replacements |
| 5 | LR relcomp L30 0.8975; model-wrong n=93, acc 0.8495; L15 model-wrong 0.98; DiM 0.62; breakdown reproduces the main run exactly (0.8975; AB 0.87, BA 0.925; model-wrong ids identical to steps 1/2) |

## Part 2 — independent re-fit of the probe (combined held-out, LOPO by pair)

| relcomp, block 30 | overall (n=400) | on the 93 model-wrong records |
|---|---|---|
| LR lbfgs multinomial C=1 — the step-5 estimator, fresh fold code | **0.8975** | **0.8495** |
| LR liblinear one-vs-rest C=0.05 | 0.985 | 0.968 |
| Ridge classifier α=100 | 0.980 | 0.968 |
| **null**: labels permuted across records | **0.528** | 0.484 |
| proxy: first-mentioned city as the label | 0.923 | 0.914 |
| binding probe by fact order | AB 0.870 / BA 0.925 | — |

| relcomp, block 15 | overall | model-wrong |
|---|---|---|
| LR lbfgs C=1 | 0.9875 | 0.9785 |
| LR liblinear OvR C=0.05 | 0.995 | 0.989 |
| Ridge α=100 | 0.9975 | 0.989 |
| **null**: labels permuted across records | **0.4525** | 0.409 |
| proxy: first-mentioned city as the label | 0.9925 | 1.000 |
| binding probe by fact order | AB 0.975 / BA 1.000 | — |

Arm 3 at the period re-derived from raw residuals (dev-fit centroids, pooled over roles, n=800): **block 30 = 0.6637, block 0 = 0.9938** (step 2 reported 0.664 and 0.994). Job 588537 ran 1:46; the VM pass's full output is in `results/slurm-logs/phase1-verify-vm.txt`.

What this establishes and what it does not:

- The step-5 numbers are not an artifact of my fold code or of lbfgs: two unrelated estimators land higher, not lower (0.98 overall, 0.97 on model-wrong at L30; 0.99+ at L15), so if anything step 5 under-reports.
- The probe fails the label-permutation null at chance (0.528), so it is not fitting noise or class marginals.
- The probe's accuracy is high in both fact orders under one linear map (L30: AB 0.87, BA 0.925; L15: AB 0.975, BA 1.000). A "first-mentioned-city" proxy is *also* linearly readable — 0.92 at L30 and 0.99 at L15 — so the residual at relcomp carries positional-slot identity as well as the queried city. The binding probe cannot be reduced to that proxy: the proxy's label is the queried city only in AB and the distractor in BA, and a single linear map over a slot code alone cannot score 0.9–1.0 in both orders. But both readings coexist at L15 at 0.99, which is the point a sceptical reader will press on ("is the model's 'queried city' just 'slot × which person was asked about'?"). That is Jason's to argue; the numbers are here, and item 1 of the manual list is where to look.

## What Jason needs to verify manually (in this order)

Each item is a re-derivation you do without my scripts, or a check of
something no script can settle. Estimated total: about two hours.

1. **The one number that reverses an application claim** — LR on model-wrong records at relcomp = 0.8495 (n=93). Load
   `/scratch/djjay/mats12/phase1/residuals/heldout.pt` and `heldout2.pt`
   (`resid[i, 1, 30]` is record i at relcomp, block 30), take
   `intermediate_id` / `alt_intermediate_id` from the dataset jsonl, fold by
   `pair_id`, fit any multinomial classifier you like with the scaler fit on
   the training fold, score correct-vs-alternative, and restrict to the
   records whose `shadow[...]["relcomp"]["CITY"]["margin"] < 0` in
   `results/runs/20260917T202900Z-phase1-step2-fact-tokens/outputs/step2-records.json.gz`.
   You should get ≥ 0.85; the ridge classifier gives 0.97. If you get chance,
   stop and tell me — everything downstream depends on this.
2. **That the 93 "model-wrong" records are what the note says they are.** Pick five of them by id (the set is in `step5-breakdown.json`, rows with `model_city_margin < 0`), print the prompt and the model's top next-token logits at relcomp from `step2-records.json.gz` (`shadow[...]["relcomp"]`), and confirm the alternative city really outranks the correct one there. This is a raw-data look, not a computation.
3. **That J-Lens reads at chance where the probe reads 0.99.** From `step2-records.json.gz`, for arm `jlens`, position `relcomp`, target `CITY`, compute the fraction of records with `rank_correct < rank_incorrect` at layer index 15 and 18 (the `layers` list gives the block for each index). Expect 0.53 overall at L15 and 0.634 on the 93 records at L18. If you want it from a fresh forward pass instead, `lens.apply(lm, prompt, positions=[relcomp], layers=[15,18])` on ten records is enough to see the ranks.
4. **The replication.** `results/runs/20260917T193052Z-stage3-heldout-frozen/outputs/stage3-heldout-frozen.json`, `summary.heldout.jlens.relcomp`: frac 0.733, control_frac 0.496, n 240. Then confirm `results/datasets/heldout2.jsonl` has 60 pairs you have never looked at: open ten prompts at random and check they are well-formed and use only the six pool cities (Prague, Seattle, Athens, Bristol, Dublin, Oslo).
5. **The causal null.** `results/runs/20260917T202907Z-phase1-step3-patching/outputs/step3-patching.json`, `summary.combined["relcomp/30"]`: `twin.flip_rate` 0.000, `n_base_right` 382, and `summary.combined["final/30"]`: twin 0.935, unrelated 0.450. Then one raw record from `step3-records.json.gz`: confirm `margin_before` is positive and `cells["relcomp/30"]["twin"]["margin_after"]` is essentially unchanged while `cells["final/30"]["twin"]["margin_after"]` is negative.
6. **The three rules that were mine, not the brief's.** Read the "Phase 1, steps 2–5" entry in the learning log and decide whether R3 (patching), R4 (resample) and R5 (probe) are rules you would have written. If you would set a threshold differently, say so in the log; none of the branches that fired are close to their thresholds except R2 (0.258 against a 0.25 lower bound) and the step-3 final-position "carries" (0.935 against 2 × 0.450 = 0.90), so the verdicts are unlikely to move, but the rules should be yours.
7. **The figures.** I never looked at the four PNGs (`results/figures/phase1-step{1,2,3,5}-*.png`). Open them and check they show what their FIGURE-REGISTRY captions say; fix or drop any that do not.
8. **The hour gates.** Two lines in the learning log are "pending" (step 1; Phase 1 close). Fill them.

Items 1–3 are the ones that matter; 4–8 are hygiene. When 1–3 pass, change the status line in `results/phase1/step5-lr-probe.md` and `llm/plans/phase1-summary.md` from `agent-unverified` to verified with your initials and the date, and add the verification-ledger rows.
