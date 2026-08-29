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

- Decision: CONTINUE / CHANGE LOOP / RETURN TO EXPLORE / PIVOT CANDIDATE — *pending*

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

- Decision: CONTINUE / CHANGE LOOP / RETURN TO EXPLORE / PIVOT CANDIDATE — *pending*


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

- *pending — this entry was written before submission.*
