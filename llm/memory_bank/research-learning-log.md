# Research Learning Log

Per `llm/construction/jlens-design-verification-sprint.md`, one entry per
counted hour. Jason fills the prediction and the first interpretation before
the agent gives its assessment.

---

## Hour 1 — Behavioural eligibility screen (context-audit delta #1)

- Date/time: 2026-08-27, entered before execution (job queued, not yet run)
- Research stage: **Exploration**
- Stage north star: find out whether the instrument works at all, before
  spending anything on the method it is meant to evaluate
- Concrete objective: measure the rate at which the unmodified
  `Qwen/Qwen3.5-4B` answers **both** bindings of a paired two-hop item
  correctly, under deterministic decoding, across 4+ relation templates
- Expected artifact: `results/runs/<UTC>-eligibility-screen/outputs/eligibility-screen.json`
  plus a PASS / MARGINAL / STOP verdict against thresholds fixed in advance

### Pre-registered thresholds (fixed before the job was submitted)

| Outcome | Pair eligibility | Action |
|---|---|---|
| PASS | >= 80% | proceed to V1 |
| MARGINAL | 60-80% | report, propose a fix, do not silently continue |
| STOP | < 60% | halt; the design changes before anything else runs |

Note the arithmetic, because the bar is stricter than it reads: a *pair*
requires both bindings correct, so if per-variant errors are roughly
independent, an 80% pair rate demands about **90% per-variant accuracy**.

### Before execution — Jason

- **My prediction: none. Recorded as "no prior", deliberately.**
  Jason declined to put a number on this rather than invent one to fill the
  box. That is the honest entry: this is the first behavioural measurement on
  this task, this model and this vocabulary, and there is no prior run,
  published result or pilot to anchor on. A fabricated prediction would make
  the log look rigorous while teaching nothing, and would corrupt the one
  thing the log is for — checking calibration against real beliefs.
- Why this is still a legitimate entry: the *thresholds* were pre-registered
  before the job was submitted, which is what protects the decision from being
  renegotiated after the number appears. Pre-registration of the decision rule
  is the load-bearing part; the point prediction is the calibration exercise.
- Strongest alternative explanation (agent-supplied, flagged as such): a 4B
  model cannot hold two competing person->place bindings simultaneously and
  collapses to whichever binding is linearly closer or more recently stated.
- Predicted observation under that alternative: eligibility below 60%, **and**
  a high rate of the model returning the paired *alternative* answer rather
  than an unrelated token, with errors concentrated in one binding of each
  pair and sensitive to fact order (AB vs BA).
- Result that would most change our minds: >= 80% zero-shot with no fact-order
  sensitivity — which would mean the task is easier than the design assumed,
  and the metric may be too easy to be diagnostic.
- Why this action has high information gain per unit time: it is the cheapest
  kill-shot in the project, it is upstream of every other gate, and it costs
  one short batch job.
- Jason's prediction of the agent's advice: not recorded (see "no prior").

### Execution record

- Start/stop time: job 550555, node fal045 (NVIDIA L40S), 2026-08-27 09:04:37Z
  (eligibility) and 09:32:24Z (V1), one allocation, one model load each.
- Commands / run IDs: `sbatch experiments/design-verification/run_gate1.sbatch`
  -> `results/runs/20260827T090437Z-eligibility-screen/`
  and `results/runs/20260827T093224Z-v1-tooling-verification/`, commit 11aa27c.
- Raw artifact paths: `outputs/eligibility-screen.json` in the run directory
  above; slurm log at `results/slurm-logs/gate1-550555.out`.
- Third attempt. Attempts 1 and 2 were instrument failures, not results; see
  `results/runs/20260827T090437Z-eligibility-screen/NOTE.md`.

Raw numbers, real lexicon / zero-shot, n=30 pairs (120 variants):

| metric | value |
|---|---|
| pair_eligibility_AB | 0.900 |
| pair_eligibility_BA | 0.933 |
| pair_eligibility_all_four | 0.867 |
| variant_accuracy (content) | 0.950 |
| strict_accuracy (bolded span) | 0.883 |
| first_word_accuracy (the broken rule) | 0.108 |
| answer_present_rate | 1.000 |
| alt_answer_rate | 0.000 |
| fact_order_gap | -0.033 |
| think_mode_rate | 0.892 |
| first_token_agreement | 0.058 |

Other cells: rare/zero 0.867 PASS, pseudo/zero 0.700 MARGINAL, and all three
few-shot cells at or below 0.667. Full table in the run JSON.

Against the pre-registered threshold: PASS (>= 80%).

- Anomalies noticed without interpretation:
  1. `answer_present_rate` is exactly 1.000 on real/zero and rare/zero. A rate
     that saturates is usually a metric that cannot fail rather than a model
     that cannot err.
  2. `first_token_agreement` is 0.058. The next token after the prompt is a
     think tag, not the answer.
  3. Few-shot scores worse than zero-shot on content (0.750 vs 0.950) but
     better on first word (0.983 vs 0.108). The two orderings disagree.
  4. `think_mode_rate` is 0.892, not 1.000, on real/zero: roughly one in ten
     generations carries no `<think>` block at all.
  5. The batched-vs-unbatched padding control still fails 2 of 8. All numbers
     above were produced unbatched.
  6. V1 coverage control places the intermediate at median rank 3 with the
     optimum at layer 30 — the last fitted source layer, i.e. the edge of the
     lens's fitted range.

### First interpretation — Jason

*(to be filled after the run, before the agent comments)*

### Coach feedback — agent

*(withheld until Jason's first interpretation is recorded)*

### Hour gate — Jason confirms

- Decision: **CONTINUE** — never separately confirmed at the time; the work
  proceeded, and Jason's 2026-08-29 "CONTINUE." (recorded at Hour 4) ratifies
  the chain retroactively. Recorded as such rather than backdated.

---

## Note on how this entry came to exist

The screen was written, staged and submitted **before** this entry was
recorded, which inverts the intended order. The job had not started when the
entry was written, so no result influenced any field above — but the sequence
was wrong and is recorded rather than tidied away. From here, the entry is
written before the work is submitted.

---

## Hour 2 — Stage 1: passive J-Lens readout, dev split

- Date/time: 2026-08-27, entered **before** submission. The job had not been
  queued when this was written.
- Research stage: **Exploration → first measurement**
- Stage north star: find out whether J-Lens identifies the correct hidden
  intermediate when the same entities appear with their roles swapped — and,
  in the same pass, whether that readout is anything more than reading a
  selection the model has already made.
- Concrete objective: paired intermediate margin at two readout positions,
  three arms, on the 10 dev pairs (40 records). Held-out is not touched.
- Expected artifact:
  `results/runs/<UTC>-stage1-passive-readout/outputs/stage1-passive-readout.json`

### Pre-registered before submission

- **Layer-selection rule:** the reported layer is the argmax of mean paired
  intermediate margin **on the dev split**, then frozen. Held-out is evaluated
  at the frozen layer and nowhere else. There is deliberately no fixed 40–80%
  band: V1's coverage control put the optimum at layer 30, the *last* fitted
  source layer, so a band chosen by convention would already have been wrong.
- **Primary metric:** continuous paired margin, `logit[correct] −
  logit[incorrect]`, computed within a single forward pass so per-prompt scale
  cancels. Ranks are reported alongside because a rank is interpretable and a
  logit difference is not.
- **Positions:** `final` (last prompt token, post-selection) and `prequery`
  (last token of the facts block, before the query names a subject).
- **Controls:** label permutation (derangement, seed 20260827 — no record keeps
  its own labels) and norm-matched random transport (every `J_l` replaced by a
  Gaussian of matched Frobenius norm, identical code path). B3 stands: no
  shuffled-corpus control lens is published, and these two are the declared
  fallback.
- **Baseline arm:** logit lens through the identical extraction path
  (`use_jacobian=False`), verified live at V1 (argmax differs at 29/31 layers).

### Before execution — Jason

- **Prediction: none. Recorded as "no prior", deliberately.** Same as Hour 1.
- Agent's prediction, flagged as the agent's and not Jason's: the correct
  intermediate outranks the swapped-partner intermediate at some layer in the
  20–30 band, mean margin positive but with wide spread, most of the signal
  from a minority of pairs, best layer at or near 30.
- Strongest alternative explanation (agent-supplied, flagged as such): the
  `final` readout is post-selection. By the last prompt token the model has
  already chosen the subject, so a positive margin may show only that the
  *selected* intermediate is readable — not that the binding is. This is V3's
  weak-vs-strong distinction and it arrives here whether or not V3 has run.
- Predicted observation under that alternative: the margin holds at `final`
  and **collapses at `prequery`**.
- Result that would most change our minds: a positive margin at `prequery`.
  That would be the strong claim. The agent does not expect it.
- Kill condition: J-Lens margin indistinguishable from the label-permutation
  control. If the control matches, the number is not about J-Lens.
- Why this action has high information gain per unit time: both positions and
  all three arms come out of one allocation, and the pairing means the weak and
  strong claims are separated by the same run that produces either.

### Scope change carried into this stage

The causal arm (H3) is **declared unavailable**, not deferred. See
`results/design-verification/v2-decomposition-verification.md`. Decision taken
by Jason on 2026-08-27 after the vendor audit; the audit re-runs as step 0 of
this job so its evidence sits inside a job log rather than a login shell.

### Execution record

- Start/stop time: job 550690, node fal009 (NVIDIA A30), 2026-08-27. Three runs
  in one allocation: 15:39:25Z (dry run), 15:40:16Z (full dev), 15:41:43Z
  (arm 3). Walltime 25 min; the job took a fraction of it.
- Commands / run IDs: `sbatch experiments/stage1/run_stage1.sbatch`, commit
  `45158b0` ->
  `results/runs/20260827T153925Z-stage1-passive-readout/` (dry run + step-0 audit)
  `results/runs/20260827T154016Z-stage1-passive-readout/` (full dev, n=40)
  `results/runs/20260827T154143Z-stage1-supervised-reference/` (arm 3)
- Raw artifact paths: `outputs/*.json` in each; slurm log
  `results/slurm-logs/stage1-550690.out`.
- Third job id for this work: 550627 was cancelled before starting to add arm 3,
  550652 was cancelled after 90 minutes pending. Only 550690 ran.

**Position alignment**, verified rather than assumed, identical on the 4-record
dry run and the 40-record full run: `final` = index 29, token `':'`;
`prequery` = index 20, token `'.'`; `alignment_ok = true`.

**Passive readout, dev split, n = 40, final position:**

| arm | layer | margin intermediate | margin answer | label-perm control | frac correct outranks | median rank |
|---|---|---|---|---|---|---|
| J-Lens | 27 | +4.251 | +8.406 | -0.202 | 0.950 | 30 |
| logit lens | 27 | +2.957 | +6.422 | -0.005 | 0.850 | 1290 |
| random transport | 30 | +0.196 | +0.106 | -0.079 | 0.500 | 153149 |

**Pre-query position:**

| arm | layer | margin intermediate | label-perm control | frac | median rank |
|---|---|---|---|---|---|
| J-Lens | 26 | +0.022 | +0.020 | 0.450 | 393 |
| logit lens | 26 | +0.015 | +0.064 | 0.525 | 56930 |
| random transport | 26 | +0.033 | -0.010 | 0.550 | 194963 |

Unembedding width 248320 (B4: ranks taken over the full width).

**Arm 3, supervised difference-in-means reference:**

| position | layer | LOO margin | LOO accuracy | in-sample accuracy | scored | unscorable |
|---|---|---|---|---|---|---|
| final | 30 | +31.499 | 0.583 | 0.800 | 12 | 28 (`class_unseen_in_fit`) |
| prequery | 26 | +0.589 | 0.417 | 0.550 | 12 | 28 (`class_unseen_in_fit`) |

14 distinct intermediate classes across 10 pairs, 40 records.

**Step 0, vendor audit** (commit `581d398`, jlens 0.1.0, 1713 lines / 9 modules).
Zero matches for `nonneg|non_neg|non-neg|sparse|nnls|lasso|omp_|matching_pursuit|dictionary|decompos|reconstruct|j_space|jspace`
in the package, the README, the walkthrough notebook and the tests. Public API:
`ActivationRecorder, HFLensModel, JacobianLens, Layout, LensModel,
configure_logging, fit, from_hf, jacobian_for_prompt`.

- Anomalies noticed without interpretation:
  1. The **answer** margin (+8.406) is roughly twice the **intermediate** margin
     (+4.251) at the final position, for J-Lens and for the logit lens alike.
  2. Arm 3's leave-one-pair-out scored 12 of 40 records; the other 28 were
     unscorable because the class had no support once its pair was held out.
  3. Norm-matched random transport returns frac exactly 0.500 and median rank
     153149 of 248320.
  4. J-Lens `prequery` frac is 0.450 — below one half, not at it.
  5. At `prequery` the logit lens's label-permutation control (+0.064) is larger
     than its own signal (+0.015).
  6. J-Lens median rank of the correct intermediate at the final position is 30,
     not 0, while V1's degenerate single-binding control put the answer at
     rank 0.
  7. J-Lens and the logit lens both select layer 27; random transport selects 30.
  8. The 4-record dry run and the 40-record full run agree on layer 27 and on
     the direction of every arm; the J-Lens margin moves 5.000 -> 4.251 and
     frac 1.000 -> 0.950.
  9. Every `prequery` selected layer is 26, across all three arms.

All numbers `agent-unverified`.

### First interpretation — Jason

**No read offered.** Recorded rather than left blank, on the same principle as
the "no prior" entries: an honest absence is data about calibration, a blank
field is not.

### Coach feedback — agent

**1. The result is real, and the rank gap is the honest way to state it.**
J-Lens beats label permutation (-0.202), norm-matched random transport (frac
exactly 0.500, median rank 153149 of 248320) and the logit lens through the
identical path. But margins from different readouts sit on different logit
scales, so "+4.251 versus +2.957" is a weaker comparison than it looks. **Median
rank 30 versus 1290 is the number to lead with** — it is scale-free and it is a
43x difference on the same prompts at the same layer.

**2. The paired design is doing more work than the caveat gives it credit for.**
The obvious objection to a final-position readout is that it just reports
whatever is currently active, and `Perth` is active because it was recently
attended to. That objection does not survive the design: the **alternative**
intermediate is also in the prompt and equally recent. Preferring the correct
one over the swapped partner is not explained by mere presence. This is exactly
what the matched-pair construction was for, and it worked.

**3. The threat that does survive is the answer shadow.** The answer margin
(+8.406) is about double the intermediate margin (+4.251). At the final token
the model has computed its answer, and the answer is bound to the correct
intermediate. So the intermediate may be favoured as a *downstream consequence*
of the answer having been computed — a backwards shadow — rather than because
the readout sees the binding on the way through. The pre-query null does not
rule this out. **The resample control (control 10's replacement) is what would**,
and until it runs the paired margin should not be read as excluding it.

**4. The pre-query result is "no evidence", not "evidence of absence".**
frac 0.450 on n=40 is about 18 of 40 and is not distinguishable from chance. At
this sample size we cannot separate "bindings are not linearly readable before
the query" from "this readout is too weak to see them". Stating it as the
stronger claim would be the single easiest way to overclaim in this project.
Supporting detail worth keeping: at pre-query the logit lens's own control
(+0.064) **exceeds its signal** (+0.015) — the control beating the thing it
controls is what a noise floor looks like, and it is reassuring that the metric
says so rather than manufacturing a small positive.

**5. Arm 3's failure is the most consequential thing in this run.** It was the
instrument that would have told us whether point 4 is about the model or about
the readout, and whether the point-1 positive sits near a ceiling or far below
one. Scoring 12 of 40 records means it answered neither. Both the strongest
negative claim and the calibration of the positive claim are currently
unsupported. The fix is structural rather than a code bug — the closed set `V`
has to be shared across pairs by construction — and it should be the next GPU
job.

**6. Layer 27 is probably a property of the model, not of the metric.** Both
real readouts select it independently; only the randomised arm drifts to 30. V1's
coverage control peaked at 30, the *last fitted source layer* — the edge of the
lens's range. The binding readout peaking at 27, inside that range rather than
at its boundary, is mild evidence that we are measuring something about the
computation and not an artefact of where the lens stops.

**7. The cheapest high-value analysis needs no GPU at all.** frac 0.950 is 38 of
40, and behavioural eligibility was 0.900. **Cross-reference which records the
readout gets right against which ones the model answers correctly.** The two
outcomes are sharply diagnostic:

- If J-Lens recovers the correct intermediate on pairs the model *answers
  wrongly*, the readout is seeing something behaviour does not — a considerably
  stronger and more interesting claim than the current headline.
- If it fails exactly where the model fails, that is direct support for the
  answer-shadow account in point 3.

Both run off data already on disk. This should happen before any further compute.

**Recommended gate: CONTINUE**, with the order: (i) the free cross-reference in
point 7, (ii) rebuild the dataset vocabulary so arm 3 can run, (iii) the
resample control. Held-out stays untouched until the layer is frozen.

### Hour gate — Jason confirms

- Decision: **CONTINUE** — Jason, 2026-08-29, verbatim: "CONTINUE." Given after
  the full verification chain (answer-shadow result, prequery reframe,
  post-query sweep, cross-GPU replication) was on the table, so it ratifies the
  corrected framing, not the original headline.


## Hour 3 — Post-query sweep: is binding readable where it is determined but not yet emitted?

- Date/time: 2026-08-29, written **before** the sweep was coded or submitted.
- Research stage: **Interpretation → targeted re-measurement**
- Interpretation-first: Jason's reading of the Stage 2 result is recorded below
  verbatim, before any agent analysis of it.

### Jason's interpretation of the Stage 2 result (verbatim)

> "The prequery frac is 0.550 likely because, like the other lenses, it is
> simply reading ahead getting us the right answer. Both concepts are in each
> group, but the model still has to guess the final result."

### Coach sharpening, agreed with Jason

The prequery position (token index 20 on the T1 template) sits at the last token
of the facts block, **before the question names a subject**. At that point the
prompt does not determine which of the two entities is the correct intermediate.
So a directional readout there has nothing to be right about.

**0.550 is the control PASSING, not the lens failing.** It has been described in
this repo as J-Lens "failing to pick between the correct intermediate and its
role-swapped twin". That description is wrong and is corrected everywhere it
appears. What the prequery numbers do show is real and narrower: at a position
where neither entity is yet privileged, J-Lens puts the concept set two orders of
magnitude higher in the ranking than the logit lens does (median rank 346 against
78,525). That is a concept-availability result, not a binding result.

**The consequence is the reason for this hour.** `final` is contaminated — the
model is about to say the intermediate out loud, 38 of 40 generations name it.
`prequery` is uncontaminated but undetermined. **Binding has never been measured
at a position where it is determined but not yet emitted.** That span — from the
first token of the question to the final token — was never read.

### Pre-registered before the sweep is submitted

- **Positions:** every token from query onset (the first token after the facts
  block) through the final token, inclusive, plus the existing `prequery` and
  `final`. Resolved **per record** from the tokenizer's offset mapping.
  Note: `results/datasets/tokenization_report.json` records the tokenizer, the
  vocabulary width and a single demo prompt length; it carries **no per-record
  token indices**, so the indices cannot be read from it and are derived from
  the offset mapping instead, with the alignment against `apply()`'s own
  `input_ids` verified per record and reported.
- **Arms:** `jlens`, `logitlens`, `jlens_random_transport` (norm-matched), plus
  the supervised difference-in-means reference (arm 3) at every position.
- **Controls:** label permutation (derangement, seed 20260827) at every
  position, and the norm-matched random transport arm. Unchanged from Hour 2.
- **Metrics reported by position:** `frac_correct_outranks_incorrect` (the
  direction bit), median rank of the correct intermediate over the full
  248,320-wide unembedding (the concept-availability measure), and the mean
  paired margin, each at that position's argmax layer.
- **Split:** dev only. Held-out is not touched.

### Decision rule, pre-registered — the sweep decides the primary claim

1. **If J-Lens resolves direction in the post-query window** — `frac`
   meaningfully above the label-permutation control at some position in the
   window — then that position is the project's primary measurement position.
   ADR-0006's stimulus regeneration is then likely unnecessary. Report and hold
   for Jason's call; do not proceed to regeneration on the agent's own judgement.
2. **If concepts stay elevated but direction stays at chance across the window**
   — median rank far better than the logit lens while `frac` tracks the control
   — then that IS the bag-of-concepts result, measured with the output shadow
   excluded by construction. ADR-0006 regeneration then proceeds as the
   robustness check, one cycle, subject to its own accept/reject criterion.
3. Then freeze, then held-out. **The freeze must name the chosen position(s) and
   cite this sweep as the basis.**

"Meaningfully above" is deliberately not given a threshold here: with n=40 and a
0.500 floor, a single pre-set cut would be false precision. The control margin
and the control `frac` are reported at every position and the comparison is made
against them in the open.

### Before execution — Jason

- **Prediction: not offered.** Jason's interpretation above is of the *previous*
  result, not a prediction about this one, and is not recorded as one.
- Agent's prediction, flagged as the agent's and not Jason's: direction resolves
  somewhere in the window rather than at its start — the question has to be read
  before the subject is bound — and the logit lens resolves it later than J-Lens
  or not at all. Concept availability is expected to be flat and high across the
  whole window for J-Lens.

### Result

Falcon job **552322**, L40S, 6:02, commit `7adaad1`, dev split, `agent-unverified`.
Full table: `results/stage2/postquery-sweep-by-position.txt`, regenerated by
`experiments/analysis/position_sweep_report.py`. That script also computes the
label-permutation control's own **frac**, which the readout summary does not
carry — the summary reports the control only as a margin, and the pre-registered
rule is stated in terms of frac, so the comparison the rule names had to be
computed rather than read off.

Window resolved per record: `q00` What, `q01` is, `q02` used, `q03` where,
`q04` Helen, `q05` lives, `q06` ?, `q07` Answer.

J-Lens `frac` / label-permutation control `frac`, each position at its own
argmax-margin layer:

| pos | token | J-Lens | ctrl | logit lens | random transport |
|---|---|---|---|---|---|
| prequery | `.` | 0.550 | 0.400 | 0.525 | 0.475 |
| q00 | ` What` | 0.475 | 0.500 | 0.500 | 0.525 |
| q01 | ` is` | 0.450 | 0.500 | 0.500 | 0.500 |
| q02 | ` used` | 0.475 | 0.425 | 0.500 | 0.500 |
| q03 | ` where` | 0.500 | 0.450 | 0.500 | 0.500 |
| q04 | ` Helen` | 0.550 | 0.650 | 0.550 | 0.525 |
| **q05** | **` lives`** | **0.775** | **0.350** | 0.675 | 0.500 |
| **q06** | **`?`** | **0.675** | **0.350** | 0.725 | 0.500 |
| q07 | ` Answer` | 0.575 | 0.500 | 0.600 | 0.500 |
| final | `:` | 0.975 | 0.375 | 0.900 | 0.500 |

n=40, SE at chance 0.079. The shape survives at a **fixed** layer — L27 gives
q05 0.800 / q06 0.675, L30 gives 0.775 / 0.725 — so it is not the per-position
argmax rule selecting noise. The norm-matched random-transport arm is flat at
0.500 across the entire window.

**Direction appears at the token that completes the relation, not the one that
names the subject.** `q04` is ` Helen` and sits at chance, with the control
*above* it. ` lives` — which closes "where Helen lives" — is where it moves.

Arm 3, the supervised reference with the labels in hand, peaks at the same place
and **higher than at the final token**: LOO margin +32.850 / acc 0.700 at `q06`
against +24.199 / 0.625 at `final`.

### Decision-rule outcome

**Rule 1 fires.** J-Lens resolves direction inside the post-query window —
0.775 against a control of 0.350 at `q05`, roughly 3.9 SE. `q05`/`q06` is
therefore the primary measurement position and ADR-0006's stimulus regeneration
is likely unnecessary. Per the rule as written, this is **reported and held for
Jason's call**; no regeneration has been started and held-out has not been
touched.

**The complication that must go to Jason with it.** The logit lens resolves
direction at the same two positions and to a statistically indistinguishable
degree — 0.675 and 0.725 against J-Lens's 0.775 and 0.675, at n=40. *In the
window, J-Lens does not beat the logit lens on the direction bit.* Where it
leads is rank, and that lead is layer-dependent: at L27, q05 is 1,296 vs 103,481
and q06 is 116 vs 1,555; at L30 it narrows to 119 vs 272 and 15 vs 34.

### What this entry does NOT establish

`model_logits` is still captured only at `positions=[-1]`. So "the output shadow
is excluded at `q06`" is **structural reasoning, not a measurement**: the model
has emitted nothing at a prompt token, and what follows `?` is ` Answer` rather
than a city. Capturing `model_logits` across the window would settle it and is
one cheap re-run. It has not been done and the claim is not made.

### Cross-GPU replication — TinkerCliffs 7307558

It did eventually run: A100, node `tc-dgx003`, 6:15, exit 0, commit `c703dd7`.
It had sat in the queue about four hours and was left there rather than
cancelled, which turned out to be the right call. Table:
`results/stage2/postquery-sweep-by-position-tinkercliffs.txt`.

**The sweep replicates.** J-Lens frac / control frac, Falcon → TinkerCliffs:

| pos | J-Lens frac | ctrl frac | J-Lens median rank |
|---|---|---|---|
| prequery | .550 → .550 | .400 → .400 | 357 → 346 |
| q03 ` where` | .500 → .500 | .450 → .450 | 123 → 125 |
| q04 ` Helen` | .550 → .550 | .650 → .650 | 11,765 → 12,105 |
| **q05 ` lives`** | **.775 → .750** | **.350 → .350** | 119 → 123 |
| **q06 `?`** | **.675 → .675** | **.350 → .350** | 116 → 110 |
| q07 ` Answer` | .575 → .575 | .500 → .525 | 539 → 557 |
| final | .975 → .975 | .375 → .375 | 37 → 35 |

The logit lens matches too — q05 .675 → .700, q06 .725 → .725 — and the
norm-matched random-transport arm is flat at .500 across the whole window on
both machines. Arm 3 also peaks at `q06` on both, above the final token:
+32.850 / .700 → +33.865 / .700 at q06, against +24.199 / .625 → +24.717 / .650
at final.

**The one substantive difference is a single record.** `q05` moves .775 → .750,
which at n=40 is one record flipping. The conclusion — direction resolves at the
token completing the relation, far above a control that sits at .350 — is
unchanged.

**Where it does NOT replicate, and why that is expected.** The selected layer
differs at `q00` (L29 → L28) and `q02` (L27 → L19), and the median rank at those
two positions swings wildly: 5,186 → 29,916 and 181 → 26,232. Those are exactly
the positions where every layer's mean margin is ≈0.005, so the argmax-margin
layer rule is choosing between near-identical noise and a different GPU's
rounding picks a different winner. This is a property of the pre-registered rule
at positions with no signal, not a defect in the measurement and not a finding
about the lens. It is the reason the fixed-layer check at L27 and L30 is
reported alongside. **No position that carries signal changed its layer.**

### The eligibility split is deterministic by GPU architecture, not run-to-run noise

Job 7307558 ran on a preemptable partition and was **preempted and requeued
twice** before the attempt that finished. `sacct` keeps only the last attempt and
the requeue overwrote the log, so the two earlier attempts survive only as
orphaned run directories; each now carries a `NOTE.md` saying what it is, and
none of them has been back-filled into a manifest. The 6:15 elapsed time is the
final attempt, not the job's whole occupancy.

That accident is informative. It means the eligibility screen ran **three times
on A100 hardware** — 20:26:03, 20:34:51 and 20:52:45 — and returned
**AB = 0.900 every time**. Against that: 551581 on an A30 gave 1.000, and 551834
and 552322 on L40S gave 1.000 each.

| GPU | runs | eligibility AB |
|---|---|---|
| A30 | 1 | 1.000 |
| L40S | 2 | 1.000, 1.000 |
| A100 | 3 (+7298944 earlier, also 0.900) | 0.900 × 4 |

So the earlier characterisation — "one prompt in ten flips its behavioural label
between two GPUs" — was too weak, and in the direction of making it sound like
noise. It is not noise. **It is deterministic per architecture and reproducible
within one.** The same prompt is scored the same way every time on the same class
of card and differently on another, which is what greedy decoding over a
last-bit-different logit does. The Stage 2 write-up should say this rather than
the weaker version, and eligibility should be quoted with the architecture named.

`padding control batched==unbatched` follows the same split: 0/8 mismatched on
L40S, 2/8 on A100.


## Hour 4 — Stage 3: held-out at frozen settings

- Date/time: 2026-08-29, written **before** the code was submitted.
- Research stage: **Confirmation** — the first run in this project whose purpose
  is to confirm rather than explore.
- Gate context: this entry is also the record of the Hour 3 gate. Decision:
  **CONTINUE** (Jason, in discussion, after reviewing the sweep, the shadow
  result, the replication, and the keep-vs-pivot question directly). ADR-0006
  deferred by Jason the same day; the intervention arm is future work.

### Why this experiment and not another

The relcomp/qmark result was FOUND by a sweep over ten positions on dev — the
textbook forking-paths setup. Held-out at frozen settings is the only
experiment that converts "we found a position" into "there is a position."
Nothing else reachable in the remaining budget changes the strength of the
primary claim.

### The freeze (committed before this runs)

`experiments/stage3/freeze.json` + `results/stage2/FREEZE.md`. Positions by
ANCHOR (relcomp = token before the final '?'; qmark = '?'; prequery and final
as references), because held-out spans templates T1–T6 of varying length and a
frozen token index would silently misalign. Layers from the pre-registered dev
argmax, identical on both clusters: jlens relcomp L30 / qmark L27; logitlens
L30 / L29; random transport at the jlens layers; arm 3 at L30, fit on all of
dev, applied unchanged to held-out.

### What is measured that was previously argued

`model_logits` is kept at every scored position on both splits, so the output
shadow at relcomp/qmark becomes a per-record measurement. This adds recorded
data and tunes nothing.

### Held-out contact disclosure

Before the freeze: the `_meta` header, record count (160), pair count (40) and
template-id set (T1–T6) were read once, to design the anchoring. No prompt,
entity, vocabulary item or answer was read.

### Pre-registered predictions (agent's, flagged as the agent's)

- jlens frac at relcomp/qmark on held-out lands near dev (0.65–0.78), control
  near 0.35–0.50; logitlens at parity on direction; jlens ahead on median rank.
- shadow intermediate margin at relcomp/qmark near zero on both splits.
- arm 3 transfers: held-out accuracy at qmark above 0.60.
- eligibility on held-out lower than dev's (six templates, harder mix), and
  architecture-dependent as established.

### Failure condition, stated in advance

If held-out frac at BOTH frozen primary positions is at or near its
label-permutation control, the sweep result was forking paths. That outcome is
the finding and will be reported as such — the frozen settings make
re-selection impossible by construction.

### Result

Falcon 554591, A30, 37:10, exit 0, commit `62f5e75`. Runs
`results/runs/20260830T173157Z-eligibility-screen` (held-out screen, 95.0%
PASS) and `20260830T175149Z-stage3-heldout-frozen`; record-level attribution in
`20260830T182516Z-stage3-window-shadow-audit`
(`experiments/analysis/window_shadow_audit.py`). Anchor failures 0/0; all
positions resolved on every template.

**The failure condition did NOT fire.** Held-out at frozen settings, n=160:
jlens relcomp frac **0.781** vs control 0.519, qmark **0.669** vs 0.556;
random transport flat. The positions are real — not forking paths. Dev values
reproduced at the frozen layers (0.775 / 0.675), and even by template the
signal holds everywhere (relcomp T1 0.96 down to T5/T6 0.68 — the dev template
is inflated, the others still clear the control).

**But one pre-registered prediction was WRONG, and it is the important one.**
The prediction said the output shadow at relcomp/qmark would be near zero. The
measurement says otherwise: the model's own next-token distribution already
prefers the correct intermediate at **0.800** (relcomp) and **0.731** (qmark)
on held-out, mean margins +1.33 and +2.24. The window is NOT shadow-free.
"Reading ahead" — Jason's interpretation from the start — is what the model
itself is doing mid-question.

**The discriminating set settles the attribution.** With 32 (relcomp) and 40
(qmark) held-out records where the shadow points the WRONG way:

| | lens acc, shadow WRONG | lens acc, shadow right | r(lens, shadow) |
|---|---|---|---|
| jlens relcomp | **0.344** (n=32) | 0.891 | +0.884 |
| jlens qmark | **0.125** (n=40) | 0.872 | +0.917 |
| logitlens relcomp | 0.250 | 0.797 | +0.707 |
| logitlens qmark | 0.200 | 0.932 | +0.925 |

Below chance on every discriminating cell. Where the model's developing
preference is wrong about the intermediate, the lens is wrong WITH it — it is
reading the preference, not the binding.

**The mechanism, made explicit by arm 3.** At relcomp the supervised
difference-in-means probe on the SAME residual reads nothing (0.525) while
J-Lens reads 0.781. The binding is not linearly present in the residual there;
what J-Lens adds is its Jacobian — a linearization of the remaining
computation — which manufactures the output preference from the residual. At
qmark, arm 3 transfers dev→held-out at 0.725→**0.731**, exactly the shadow's
own frac: the linearly decodable signal at its best position IS the shadow.

**Supportable claim, final form:** J-Lens is a well-calibrated predictor of
what the model is about to say, at every position where direction is readable
— and an instrument for reading stored-but-unexpressed bindings nowhere on
this task. Its residual advantage over the logit lens on held-out is
concept-rank localization at early/mid positions (prequery 373 vs 76,276;
relcomp 128 vs 393) and largely vanishes by qmark (95 vs 82).

**Control caveat, measured:** with the six-city pool, only 65/160 held-out
label permutations are fully disjoint from the record's own pair (4 identical,
8 swapped, 83 share one city), which is why the held-out control frac sits
near 0.52 rather than dev's 0.35. The treatment-control gaps above stand, but
the control is weaker on held-out and is reported with this audit attached.

Eligibility on held-out: 95.0% (A30), below dev's 100% as predicted; the
architecture caveat carries over. All numbers `agent-unverified` except where
Jason's own re-derivations cover them.

### Hour gate — Jason confirms

- Decision: CONTINUE / CHANGE LOOP / RETURN TO EXPLORE / PIVOT CANDIDATE — *pending*

---

# Post-MATS continuation (Phase 1) — uncounted hours

The application clock closed at tag `mats12-submitted`. Entries below follow
`llm/plans/continuation-plan.md` and keep the same discipline: decision rules
written and committed BEFORE a job is queued; freeze untouched; one
verification-ledger row per claim. Interpretation is Jason's; the agent
records numbers and which pre-registered branch fired.

## Phase 1, step 1 — fresh held-out draw, scored once at frozen settings

- Date/time: 2026-09-17, written **before** the job is queued.
- Research stage: **Confirmation** (replication of the Stage 3 held-out
  result on stimuli that did not exist when the settings were frozen).
- Branch `research/phase1`. `writeup/main.md`, `experiments/stage3/freeze.json`
  and every directory under `results/runs/` from the application are not
  modified by this step.

### Why this experiment and not another

Every application number rests on one held-out draw of 40 pairs. The
discriminating set was n=32 / n=40. A second draw at the same frozen settings
is the cheapest test of whether those numbers are properties of the method or
of that draw, and it is the step in the plan with no new code path in the
scoring — so it goes first.

### What is fixed (identical to the application run)

- Generator `src/make_dataset.py`, lexicon `real`, shot `zero`, six templates
  T1–T6, six-city pool. The pool is sampled from `--pool-seed 20260827` — the
  ORIGINAL seed — so the six cities are the same six (this is what "same
  six-city pool" requires; the pool is otherwise a function of the seed).
- Scorer `experiments/stage3/heldout_frozen.py`, unchanged. Positions and
  layers from `experiments/stage3/freeze.json`: jlens relcomp L30 / qmark L27
  / final L27 / prequery L25; logitlens L30 / L29 / L30 / L24; random
  transport at the jlens layers; arm 3 L30 fit on all of dev (dev.jsonl
  unchanged) and applied unchanged. Label-permutation derangement seed
  20260827 within split; output shadow (`model_logits`) at every scored
  position.
- Eligibility screen `experiments/design-verification/eligibility_screen.py
  --dataset results/datasets/heldout2.jsonl --frozen-eval`, thresholds
  PASS ≥ 0.80 / MARGINAL 0.60–0.80 / STOP < 0.60, greedy decoding as before.

### What is new

- Seed **20260917**, `--n-dev 0 --n-heldout 60`: 60 pairs, 240 records,
  pair indices 0..59 of the seed-20260917 stream (per-pair seeds
  20260917+idx; the original used 20260827+idx for idx 0..49 — disjoint).
- `--id-prefix h2-` so record ids cannot collide with the original
  (`h2-real-zero-000-AAB` …).
- Output ONLY `results/datasets/heldout2.jsonl` (+ `heldout2-manifest.json`,
  `heldout2-tokenization_report.json`). `heldout.jsonl` is not touched; the
  job refuses to run if `heldout2.jsonl` already exists (one draw).
- Two flags added to `src/make_dataset.py` for this (`--pool-seed`,
  `--id-prefix`; commit below). Their defaults reproduce the old behaviour;
  the job's step 0 regenerates the original dev/heldout with default
  arguments and requires byte-identical sha256 against
  `results/datasets/dataset-manifest.json` before anything is drawn. If that
  check fails, nothing is drawn or scored and the step stops.
- Partition `l40s_normal_q` (per the continuation brief). The application run
  was on an A30; the GPU name is printed by the job and recorded in each run
  manifest, and the eligibility caveat about architecture carries over.
- Report script `experiments/phase1/step1_report.py` (new, analysis only):
  reads the original run `results/runs/20260830T175149Z-stage3-heldout-frozen`
  and the new run and tabulates `original`, `new`, `combined` separately.

### Commands (exact)

```
sbatch experiments/phase1/step1_heldout2.sbatch      # on ARC, from /scratch/djjay/mats12/repo at the commit named below
python experiments/phase1/step1_report.py \
    --original results/runs/20260830T175149Z-stage3-heldout-frozen \
    --new results/runs/<UTC>-stage3-heldout-frozen   # on the VM after rsync
```

### What is reported, for each of original (n=160), new (n=240), combined

Per arm (jlens, logitlens, jlens_random_transport) at prequery / relcomp /
qmark / final: direction frac vs its label-permutation control; median rank of
the correct intermediate; output-shadow frac; lens accuracy on records where
the model's own preference is wrong, with n; r(lens margin, model margin).
Arm 3 held-out accuracy per run and pooled by count. Duplicate-prompt screen
between heldout2 and dev / heldout (see rule R0).

### Pre-registered decision rules

- **R0 (contact).** Any heldout2 record whose prompt string appears in
  `dev.jsonl` is excluded from every heldout2 tally (arm 3's mu was fit on
  dev). Any heldout2 record whose prompt appears in `heldout.jsonl` stays in
  `new` but is dropped from `combined` so no prompt is counted twice. Counts
  are reported either way.
- **R1 (replication).** On `new`, jlens direction frac at relcomp exceeds its
  label-permutation control by ≥ 0.10 → the Stage 3 position result
  **replicates**. Otherwise → **does not replicate**, and that is the finding;
  no re-selection of positions or layers is permitted by construction. The
  qmark gap is reported alongside but does not decide R1 (its original gap
  was 0.11, inside noise for n=160).
- **R2 (the band, from the brief).** Combined jlens accuracy on model-wrong
  records at relcomp outside **0.25–0.45** → flagged plainly in the step
  note. Inside → "consistent with the application's 0.344 (n=32)".
- **R3 (the attribution).** If on `new` jlens accuracy on model-wrong records
  at relcomp is ≥ 0.60 with n ≥ 20, the "lens follows the model" reading is
  contradicted on fresh data and the step note says so; the application
  claim is then softened in the Phase 1 summary, not here.
- Eligibility on heldout2 below 0.60 → STOP for this step: report, do not
  score the readouts (the sbatch still runs them; the note then marks the
  readout numbers as not interpretable and the step is redone after Jason
  decides).

### Pre-registered predictions (agent's, flagged as the agent's)

- new jlens relcomp frac 0.70–0.85, control 0.45–0.55; qmark 0.60–0.75.
- shadow frac at relcomp 0.75–0.85; r(lens, model) > 0.80 at relcomp and qmark.
- jlens accuracy on model-wrong records at relcomp 0.20–0.50 (n ≈ 40–60).
- arm 3 at relcomp near chance (0.45–0.60); at qmark 0.65–0.80.
- median rank jlens < logitlens at relcomp.
- eligibility on heldout2 ≥ 0.85 (pair-level, both bindings).

### Held-out contact disclosure

heldout2 does not exist at the time of writing. The generator's stdout prints
only the aggregate class-support line for the held-out split (no prompts). The
agent will read `heldout2.jsonl` only inside the scoring job and the report
script; no prompt is inspected by a human or the agent before the numbers
are in.

### Amendment 1 (2026-09-17, before resubmission)

Job **587798** (L40S, commit `331e33a`) passed step 0 — the regenerated
original dev/heldout files were byte-identical to the manifest sha256s, so
`--pool-seed`/`--id-prefix` are inert for the old files — and then stopped
at step 1: the generator's own self-check refused the 60-pair draw because
**4 prompt strings were duplicated** within it (60 pairs over 15 city-pair
slots × 6 templates with 24 names collide by birthday arithmetic; the
original 40-pair draw happened not to). Nothing was written or scored; no
number was seen. The pre-registration above did not say what to do in this
case, so this amendment says it, and is committed before the job is
re-queued:

- `--dedupe-prompts` added to `src/make_dataset.py` (off by default; the
  original files do not use it): walk the same seed-20260917 stream from
  index 0, keep a pair unless one of its four prompts equals a prompt already
  kept, advance the index until 60 unique pairs are kept. Kept pairs are
  byte-identical to what the plain stream would produce at the same index;
  the manifest records the skipped indices. The job's step 0 regression
  check still runs first.
- Consequence to report: the round-robin city-pair balance can be off by
  one for the skipped slots (some city pairs 3 rather than 4 times). Reported
  in the step note; it changes nothing about the frozen scoring.
- Rules R0–R3 and the predictions are unchanged.

### Result

Falcon **587809**, L40S, 14:55, exit 0 on all four steps, commit `fe1ca16`.
Runs `20260917T192334Z-eligibility-screen` (heldout2, 0.900 PASS),
`20260917T193052Z-stage3-heldout-frozen` (scoring), and
`20260917T193922Z-phase1-step1-report` (tables). Draw: 60 pairs / 240
records, index 44 skipped, 0 duplicate prompts, 0 contact with dev or the
original held-out (R0: nothing excluded). Full note with every table:
`results/phase1/step1-heldout2.md`. All numbers agent-unverified.

- **R1 REPLICATES.** New draw, J-Lens at relcomp: frac **0.733** vs
  label-permutation control 0.496 (gap +0.237 ≥ 0.10), n=240; qmark 0.667
  vs 0.454. Random transport flat (0.50–0.53). Median rank 132 (logit lens
  367). Combined n=400: relcomp 0.752 vs 0.505, rank 129.
- **R2 inside the band, at its edge.** Combined J-Lens accuracy on
  model-wrong records at relcomp **0.258 (n=93)**; the new draw alone is
  **0.213 (n=61)** — below 0.25. qmark: new 0.089 (n=56), combined 0.104
  (n=96). r(lens margin, model margin) on the new draw +0.913 / +0.918.
- **R3 not contradicted** (0.213 ≪ 0.60).
- Arm 3 transfers as before: new relcomp 0.508, qmark 0.721 (original
  0.525 / 0.731).
- One prediction missed: shadow frac at relcomp was 0.733, just under the
  predicted 0.75–0.85. The other seven landed.

### Hour gate — Jason confirms

- Decision: CONTINUE to step 2 / other — *pending*

## Phase 1, steps 2–5 — pre-registered together, before any of the four jobs is queued

- Date/time: 2026-09-17, written after step 1's result and **before** the
  jobs for steps 2, 3, 4 are queued (they run in parallel on separate GPUs
  and cannot collide: separate scripts, separate run directories) and before
  step 5 is queued with a Slurm dependency on step 2.
- Research stage: **Confirmation / causal test** for steps 3–4;
  **Exploration under a fixed protocol** for steps 2 and 5 (every layer is
  reported; the only selection is dev-LOPO layer choice, the application's
  protocol, with the frozen L30 always reported beside it).
- Common to all four: code in `experiments/phase1/` (`common.py` reuses the
  application's `ranks_of`, `resolve_positions`, `derangement`,
  `randomize_lens`, `fit_centroids`, `margin_of`, and the stage-3 anchoring
  verbatim). Each job runs a 2–4-record smoke pass first and deletes that
  run directory; smoke runs are never reported. Model, revision, lens and
  the freeze are unchanged. Every number `agent-unverified`. Where the
  brief said "decision rule as specified" and the specification is not in
  the repo, the rule below is the agent's and is marked *(agent's rule)*.

### Step 2 — fact-token probes (`step2_fact_tokens.py`, `step2_fact_tokens.sbatch`)

- Positions per record: the four frozen anchors plus six fact tokens —
  person, city, period of the queried person's sentence (role q) and of the
  distractor's (role d) — located by offset mapping and verified token by
  token (failures counted, position dropped).
- Two-way targets: city token → PERSON (person stated in that sentence vs
  the other person); person token → CITY; period → both; query anchors →
  CITY (the application's "intermediate") and ANSWER. Label-permutation
  control: the deranged record's pair for the same target.
- Arm 3 (difference-in-means): classes = token ids; fit on dev pooled over
  roles q/d per token type; leave-one-PAIR-out on dev; applied unchanged to
  heldout and heldout2; every block 0..31; L30 (frozen) primary,
  dev-LOPO-selected layer secondary. J-Lens and logit lens at every lens
  layer 0..30 at the same positions and targets.
- Residuals at all 32 block outputs × 10 positions saved to
  `/scratch/djjay/mats12/phase1/residuals/` (outside the repo) for step 5.
- **Rules (from the brief, operationalised):**
  - R2.1 A probe cell (token type × target) counts as **linearly readable**
    if, on the combined held-out (n = 400 records, 800 fact-token samples),
    arm-3 accuracy at L30 ≥ 0.65 AND exceeds its label-permutation control by
    ≥ 0.15. If no fact-token cell clears this, the finding is "not linearly
    readable at any position we probed".
  - R2.2 For every cell that clears R2.1: J-Lens **reads it there** if its
    direction frac at the same position, at L30, exceeds its own
    label-permutation control by ≥ 0.15; otherwise it does not. The logit
    lens is reported beside it. This is the Phase 1 headline cell.
  - Causal-order note, stated in advance: in a sentence "P lives in C.", the
    city is to the right of the person token, so a CITY probe *at the person
    token* cannot read that sentence's city; a chance result there is
    expected and is not evidence about storage.
- **Predictions (agent's):** city→PERSON readable at most layers ≥ 0.85
  (the name is three tokens back); period→CITY ≥ 0.9; period→PERSON ≥ 0.8;
  person→CITY at chance. J-Lens at the period reads CITY above control;
  PERSON above control at the city token.

### Step 3 — twin activation patching (`step3_patching.py`, `step3_patching.sbatch`)

- For each record X and its swapped twin Y (same pair and fact order, other
  variant; prompts differ only in which city is in each person sentence),
  X's residual at one (anchor, block) is replaced by Y's; the model's answer
  margin at the final position, logit[X's answer] − logit[Y's answer], is
  re-read (Y's answer is X's alternative answer, so this is the
  application's `answer_margin`). Cells: prequery, relcomp, qmark, final ×
  every block 0..31; PRIMARY cells are the frozen layers per anchor (jlens,
  logitlens, arm 3: relcomp {30}, qmark {27, 29, 30}, prequery {24, 25, 30},
  final {27, 30}).
- Reported per cell: two-way flip rate over records whose unpatched margin is
  positive; mean margin change over all records; full-vocab argmax change
  rate; reverse-flip rate on unpatched-wrong records; mean cosine between
  X's and Y's residual at the cell.
- Controls: (a) same patch from an unrelated record (different pair, same
  template / fact order / variant, same token count), norm-matched to X's
  own residual; (b) the prequery-period row of the same table at the same
  block.
- Dev is processed and printed first; heldout and heldout2 once each in the
  same job.
- **Rule (agent's rule):** on the combined held-out at a primary cell:
  twin flip rate ≥ 0.50 AND ≥ 2 × the unrelated-donor flip rate → "the
  single-position state at this cell **carries the binding causally**";
  twin flip rate ≤ unrelated flip rate + 0.10 → "**does not**"; between →
  "partial". The prequery row is read with the same rule (control (b) is
  informative, not a nuisance).
- **Predictions (agent's):** final L27/L30 flips ≥ 0.8 (the output position);
  relcomp L30 ≤ 0.3 (only block 31 downstream); qmark L27 0.2–0.5; prequery
  L25 uncertain, 0.2–0.7. Unrelated donor ≤ 0.15 everywhere except final.

### Step 4 — resample control (`step4_resample.py`, `step4_resample.sbatch`)

- The correct intermediate's object fact "{city} uses {answer}." is rewritten
  with a fresh single-token object from `REAL_OBJECTS` that appears nowhere
  in the prompt (seeded per record, seed 20260917 + crc32(record_id)).
  Nothing else changes. J-Lens and logit lens re-read at the frozen anchors
  and layers; targets: NEW vs OLD object (primary, "the readout follows the
  stated fact"), NEW vs ALT object (both present in the prompt, so
  co-occurrence cannot decide it), OLD vs ALT, CITY (the rank result; should
  not move). Control: the same targets on the UNMODIFIED prompt (how often a
  fresh pool word outranks the stated answer anyway). The model's own
  preference NEW vs OLD is recorded at every anchor.
- **Rule (agent's rule):** on the combined held-out, J-Lens at relcomp
  (L30) and qmark (L27): NEW-vs-OLD frac ≥ 0.75 AND ≥ unmodified control +
  0.30 → "readout follows the stated fact; the co-occurrence door is closed
  at that position". ≤ 0.55 → "does not follow; §4.2 localization claim to
  be softened". Between → partial; §4.2 softened with the number attached.
  `final` is expected to follow trivially and is not a test.
- **Predictions (agent's):** final NEW-vs-OLD ≥ 0.9; relcomp 0.55–0.8;
  qmark 0.6–0.85; unmodified control ≤ 0.3 at relcomp/qmark; CITY frac
  unchanged within ±0.05 of step 1's combined values.

### Step 5 — trained linear probe (`step5_lr_probe.py`, `step5_lr_probe.sbatch`)

- On the combined held-out (heldout + heldout2, 100 pairs, 400 records),
  leave-one-pair-out: for each fold fit (i) logistic regression (sklearn,
  lbfgs, C = 1.0, max_iter 500, tol 1e-3, StandardScaler fit on the training
  fold, multinomial over the token-id classes present) and (ii)
  difference-in-means (`fit_centroids`/`margin_of`) on the same fold; score
  the held-out pair's records with the two-way margin correct − alternative
  (unscorable if either class is absent from the fold). Label-permutation
  control for both. Cells: query anchors (CITY) and fact tokens pooled over
  role (city→PERSON, person→CITY, period→PERSON, period→CITY), every block;
  L30 primary. Also LR accuracy on model-wrong records at relcomp/qmark
  (model CITY margin < 0 at that anchor, from step 2's shadow).
- **Rule (agent's rule):** at relcomp L30 on the combined held-out: LR
  accuracy − DiM accuracy ≥ 0.10 AND LR ≥ 0.65 → "the application's probe
  was too weak; the binding is linearly present at relcomp". LR ≤ 0.60 →
  "not the probe's weakness". Between → partial. Separately, LR on
  model-wrong records at relcomp ≥ 0.65 (n ≥ 60) → "a trained probe reads
  the binding where the model's preference is wrong" (this would reverse
  the application's attribution and is reported as such).
- **Predictions (agent's):** LR at relcomp L30 0.55–0.70; DiM 0.50–0.55;
  LR on model-wrong records at relcomp ≤ 0.6; LR at period→CITY ≥ 0.95.

### Commands (exact)

```
sbatch experiments/phase1/step2_fact_tokens.sbatch
sbatch experiments/phase1/step3_patching.sbatch
sbatch experiments/phase1/step4_resample.sbatch
sbatch --dependency=afterok:<step2 job id> experiments/phase1/step5_lr_probe.sbatch
```
Reports: one note per step in `results/phase1/step{2,3,4,5}-*.md`; figures
via `src/figstyle.py::save_figure` where helpful; then
`llm/plans/phase1-summary.md`.

### Result

*(filled after the runs; one block per step.)*
