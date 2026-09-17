# Active Context

Last updated: 2026-09-05

Current focus, next actions and live risks only. Durable environment facts
are in `techContext.md`; conventions in `systemPatterns.md`; scope in
`projectbrief.md`; the counted-hours ledger is `time-log.md`.

## Where we are

**Execution is finished; the write-up is in final assembly.** Stage 3
(frozen held-out, job 554591) is the primary result: J-Lens reads the
model's developing output preference at every position where direction is
readable, and reads no stored-but-unexpressed binding anywhere on this task
(discriminating set 0.344 / 0.125; supervised probe 0.525 at the
relation-completing token). The causal arm was unavailable (blocker B2) and
is reported as a method-evaluation finding, not a gap.

**Clock: 19.3 / 20 counted hours** (7.1 verified, 8.2 estimated, 4.0
Jason-stated; `time-log.md`). Executive summary: 2.0 / 2.0, Jason-stated. Budget is effectively spent:
further agent write-up work must be formatting or verification, not new
drafting.

**Deadline: Fri 2026-09-04 23:59 PT** (this note is written on the far side
of it — the application form submission is Jason's).

## Where the write-up lives (three copies)

- **Google Doc** "MATS 12.0 Application - Jason Cusati - Beyond a Bag of
  Concepts" (djjay0131@gmail.com Drive) is the copy Neel reads. The
  executive summary there is Jason's; the body is `writeup/main.md`
  rendered through pandoc → HTML → clipboard paste (see
  `claude/writeup-status-2026-09-05.md` in the Cowork project for the
  procedure).
- **Repo** `exp/v1-v3-verification`: `writeup/exec-summary.md` mirrors the
  Doc's executive summary; `writeup/main.md` is the condensed body (~3.2k
  words); `writeup/main-full.md` keeps the unabridged text. `scripts/
  build-report.sh` rebuilds `writeup/mats12-report.docx` and runs the
  WRITEUP gate (11 pass / 2 warn / 0 fail).
- **agents4research** clone at `~/code/mats-12-application` and the Mac clone
  at `~/code/mats-12-application` track the same branch head.

## Immediate next actions

1. Jason: final read of the Google Doc; cut the executive summary from
   ~800 words toward the 600-word rule if he chooses (3-page limit is met).
3. Submit the form (`llm/application/form-answers-worksheet.md` holds the
   draft answers; it is Jason's file and uncommitted by design).
4. After submission: merge `exp/v1-v3-verification` to `main`.

## Live risks

- Counted hours sit at 19.3 / 20; any further drafting risks the budget.
  Formatting, transport and verification are uncounted by the standing
  ruling.
- The Google Doc and `writeup/exec-summary.md` drift whenever Jason edits
  the Doc directly; re-export before any rebuild that must match it.
- Estimated ledger rows could each be wrong by roughly an hour; they are
  labelled, never folded into the verified figure.

## Governance layout — migrated 2026-09-10

This repo is on the **agentic-governance v0.5 two-plane layout** (PR
#7). `llm/` is the control plane; `docs/` is the data plane and holds no
source of truth. What changes for anyone working here:

- The delta is at `llm/governance/governance-delta.md`, the ADRs at
  `llm/governance/adr/`. Not under `docs/`.
- The plans directory is `llm/plans/` — plural. `llm/plan/` is gone.
- Declared paths are in the delta's `## Repository Layout`; the routing rule
  agents must follow is at the end of `CLAUDE.md`. Do not invent a location
  for a new document — answer Q1, then Q2.
- The check command now requires `--layout`:
  `node ~/code/agentic-governance/plugin/scripts/governance-checks.mjs --layout`.
- `experiments/`, `results/`, `writeup/`, `src/`, `notebooks/`, `scripts/`
  and `context/` did not move and are not going to. They are declared data
  plane.
- **Open:** this repo has no CI workflow, so nothing runs the check command
  on push or PR. The layout rule holds by operator discipline only. Recorded
  rather than pretended away.
- **Open:** ADR-0001 records the v0.2 adoption and stays accurate as
  history. The v0.5 upgrade has no ADR of its own; a back-fill is a
  reasonable candidate if this repo outlives the application.
