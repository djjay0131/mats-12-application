# mats-12-application

MATS 12.0 application to **Neel Nanda's mechanistic interpretability
stream** (Winter 2026–27 cohort). Due **Fri Sept 4, 2026, 11:59pm PT**.

The task: ~16 hours (max 20) of research progress on an AI safety problem,
plus a write-up and a 1–3 page executive summary. The write-up counts
against the 20; the executive summary gets a separate +2 hours.

## Start here

| Read | For |
|---|---|
| [`docs/adr/0005-accept-jlens-relational-binding.md`](docs/adr/0005-accept-jlens-relational-binding.md) | **The project.** Accepts the J-Lens relational-binding experiment, sets passive-primary scope, and rules on the clock |
| [`llm/plan/jlens-relational-binding-experiment-design.md`](llm/plan/jlens-relational-binding-experiment-design.md) | The design of record: hypotheses, metrics, eight controls, hour-by-hour plan |
| [`llm/plan/PLAN.md`](llm/plan/PLAN.md) | The phased plan, day-by-day timeline, time-budget rules, and gates |
| [`llm/plan/project-candidates.md`](llm/plan/project-candidates.md) | Five scored candidate projects and the recommendation |
| [`llm/research/literature-scan-2026-08-22.md`](llm/research/literature-scan-2026-08-22.md) | What's live and contested in CoT faithfulness and model biology, current open-weight reasoning models, tooling status |
| [`llm/application/conformance-register.md`](llm/application/conformance-register.md) | **All 121 requirements extracted from Neel's doc** — 38 blockers, 33 scored, 21 mechanics, 29 advice — each with its source quote, verification method, and gate |
| [`llm/application/selection-rubric.md`](llm/application/selection-rubric.md) | The 15 judgement criteria a script can't check. 28+/30 to submit |
| [`llm/application/mats12-application-instructions-distilled.md`](llm/application/mats12-application-instructions-distilled.md) | Neel's full instructions, structured — evaluation criteria, anti-patterns, the complete suggested-problem list |
| [`llm/application/mats12-instructions-raw.txt`](llm/application/mats12-instructions-raw.txt) | The source doc verbatim (125k chars) |
| [`docs/governance-delta.md`](docs/governance-delta.md) | How this repo is governed |

## Layout

All project-management and research material lives under `llm/`; `docs/`
carries only what governance fixes in place. Rule of thumb: if it describes
**what we will do or why**, it is under `llm/`. If it **is the work or its
output**, it is at the root.

```
docs/
  adr/           decision records (path fixed by agentic-governance)
  governance-delta.md
llm/
  memory_bank/   active context, progress, the 20-hour ledger, history
  plan/          PLAN.md, candidate scoring, the experiment design
  research/      literature scan, positioning notes
  application/   Neel's instructions, conformance register, rubric, ledgers
  construction/  verification sprints, prompts, process overlays
  features/      BACKLOG.md
experiments/     Slurm batch scripts and run definitions
results/         raw outputs, manifests, figures
writeup/         the report and executive summary
src/, notebooks/ experiment code
scripts/         conformance-check.mjs and repo tooling
```

## Governance

Adopts [`agentic-governance`](https://github.com/djjay0131/agentic-governance)
**v0.2**. Local facts live in [`docs/governance-delta.md`](docs/governance-delta.md).
Steward merge authority is INACTIVE. Given the 13-day clock, enforcement
here is convention-only by deliberate choice — recorded in the delta rather
than pretended away.

## Conformance

Neel's doc states a large number of things that are **individually
disqualifying** — a results table with no baseline, an unlabelled
cherry-picked example, a number no human re-derived, an exec summary that
drifts into LLM cadence. Reading it once and intending to comply is not a
control.

So it is treated as a requirements spec, checked in three layers
(ADR-0003):

```
node scripts/conformance-check.mjs --gate SELECT|EXECUTE|WRITEUP|SUBMIT
```

1. **The checker** — asserts everything assertable: banned models, dead
   research areas, exec-summary word count and figures, LLM-voice
   stylometry, baseline columns in every results table, claim typing,
   numeric traceability, the verification ledger, replication-before-
   building, narrative-vs-chronological structure, the hour budget.
2. **The rubric** — [`selection-rubric.md`](llm/application/selection-rubric.md),
   15 judgement criteria, 28+/30 with no zeros.
3. **The adversarial read** — the `neel-reviewer` agent, instructed to
   reject, in five passes.

The `conformance-audit` skill runs all three and emits GO/NO-GO. **No gate
advances with an open blocker.**

## The one rule that matters

Neel: *"if your write-up contains key results you clearly never verified,
or don't understand, that's disqualifying. I want scholars with value add
over prompting Claude myself."*

Agents draft. Humans verify. Every number in the write-up gets re-derived
by hand before it ships.
