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

- Start/stop time: **pending** — not yet submitted at time of writing
- Commands / run IDs: `sbatch experiments/stage1/run_stage1.sbatch`
- Raw artifact paths: `results/runs/` (written by `src/runlog.py`)
- Anomalies noticed without interpretation: **pending**

### First interpretation — Jason

*(to be filled after the run, before the agent comments)*

### Coach feedback — agent

*(withheld until Jason's first interpretation is recorded)*

### Hour gate — Jason confirms

- Decision: CONTINUE / CHANGE LOOP / RETURN TO EXPLORE / PIVOT CANDIDATE — *pending*
