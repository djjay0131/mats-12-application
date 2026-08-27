# System Patterns

Last updated: 2026-08-26

How this repository is organised and the conventions that hold it together.

## Repository layout

Planning and research material lives under `llm/`; `docs/` holds only what
agentic-governance fixes in place. Rule of thumb: if it describes **what we
will do or why**, it is under `llm/`. If it **is the work or its output**, it
is at the root. Full table: `docs/governance-delta.md` §Repository Layout.

```
docs/adr/          decision records (path fixed by governance)
docs/governance-delta.md
llm/memory_bank/   living state — this directory
llm/plan/          PLAN.md, candidate scoring, the experiment design
llm/research/      literature scan, positioning, discussion history
llm/application/   Neel's instructions, conformance register, rubric, ledgers
llm/construction/  verification sprints, prompts, process overlays
llm/features/      BACKLOG.md
experiments/       Slurm batch scripts
results/           raw outputs, manifests, figures
writeup/           report source and build output
src/, notebooks/   experiment code
scripts/           conformance-check.mjs, build-report.sh
```

## Conformance in three layers

Neel's instructions are treated as a requirements specification, not prose to
remember (ADR-0003).

1. **Register** — `llm/application/conformance-register.md`, 121 requirements
   with source quotes, classed BLOCKER / SCORED / MECHANIC / ADVICE. 38 are
   individually disqualifying. This is the source of truth.
2. **Checker** — `scripts/conformance-check.mjs --gate SELECT|EXECUTE|WRITEUP|SUBMIT`
   asserts everything assertable and exits non-zero on failure.
3. **Judgement** — `llm/application/selection-rubric.md` (15 criteria, 28+/30)
   and the `neel-reviewer` agent, which reviews adversarially in five passes.

The `conformance-audit` skill runs all three and emits GO/NO-GO. No gate
advances with an open blocker.

## The three ledgers

Evidence discipline is kept in files, not intentions. Each is checked
mechanically.

| Ledger | Holds | Enforces |
|---|---|---|
| `llm/application/claims-register.md` | Every claim, typed `existence-proof` or `method-claim` | Cherry-picking is legal only under an explicit existence-proof tag |
| `llm/application/controls-ledger.md` | The cheap control actually run, and its result | "Failing to compare to baselines" is disqualifying |
| `llm/application/verification-ledger.md` | Every headline number, re-derived by a human via a path not sharing the pipeline's code | Unverified agent output is disqualifying |

Re-running the same script is not verification.

## Figures register themselves

Every figure goes through `src/figstyle.py::save_figure`, which writes the
PNG and appends a row to `results/figures/FIGURE-REGISTRY.md` carrying claim
id, n, seed, sha-256 and commit. A figure with no claim id prints a warning:
if it supports no registered claim, it does not belong in the report.

Palette is slots 1–3 of the validated categorical set (blue `#2a78d6`,
orange `#eb6834`, aqua `#1baf7a`) plus neutral for controls, in fixed order,
never cycled. Aqua sits below 3:1 contrast, so bar charts carry direct value
labels — identity never rests on colour alone.

## The report is built, not edited

Authored as markdown in `writeup/exec-summary.md` and `writeup/main.md`;
compiled by `scripts/build-report.sh` to `writeup/mats12-report.docx` via
pandoc. The source stays diffable in git, figures are re-collected on every
build, and the conformance checker reads the same two files.

**`writeup/mats12-report.docx` is a build artifact.** Do not hand-edit it;
the next build overwrites it.

The build gates the two hard mechanical limits itself — exec-summary word
count (600) and figure presence — then runs `--gate WRITEUP`. Missing figures
warn rather than fail, since the report is built repeatedly while results
arrive.

## Governance flow

Adopts `agentic-governance` v0.2; local facts in `docs/governance-delta.md`.
Issue → branch → PR with a declared governance level → review → merge. No
direct commits to `main`. Steward merge authority is **INACTIVE**, and branch
protection is unavailable on this plan (verified 403), so enforcement is
convention plus the checkers — recorded honestly rather than assumed.
