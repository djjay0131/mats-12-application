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
