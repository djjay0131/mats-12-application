# Counted-Hours Ledger

Budget: **20 counted hours**, plus **2 separate hours** for the executive
summary only.

**Counts:** writing project code · reading papers chosen for the project ·
analysing data and results · thinking and planning · writing the main
write-up.

**Does not count:** general prep and tutorials you'd have done anyway ·
generic tech setup (renting/configuring a GPU) · breaks · time waiting on
training while doing something else · filling in the application form.

Reading papers and tutorials should stay under **5 of the 20**.

A genuine pivot permits a **clock reset** — record it here and in an ADR.

## How this ledger was reconstructed

It was not kept live. It read 0.0/20.0 while the learning log recorded two
completed hours, and it is reconstructed here on 2026-08-28 from evidence in
the repo rather than from memory. **From this entry onward it is updated in the
same commit as the work it records.**

Two sources, and the ledger says which applies to every row:

- **Verified.** A contiguous run of commits with no gap over ~60 minutes, timed
  by `git log --date`. The span is bounded at both ends by an artifact. Work
  before the first commit of a block is not counted, so these under-count.
- **Estimated.** A gap between commit blocks in which artifacts prove work
  happened — a run manifest, a fixed bug, a script that did not exist before —
  but whose active fraction is unknown. Marked with `~`. Slurm queue waiting is
  explicitly uncounted by the rules, and those gaps contain a great deal of it,
  so the estimates are deliberately conservative.

Clock ruling in force (Jason, 2026-08-27): **wall-clock time, not summed agent
hours.** Parallel subagent work is a bonus, not a multiplier on the budget.

| Date | Block | Description | Hours | Basis |
|---|---|---|---|---|
| 2026-08-22 | prep | Repo, governance, doc retrieval, literature scan, candidate scoring | 0.0 | Uncounted — before the project was locked (ADR-0005) |
| 2026-08-26 | 22:08–22:49 | Agent context contract, execution topology, design audit against the 600k file | 0.7 | Verified |
| 2026-08-27 | 04:39–05:26 | Run-manifest system, `reproduce.sh`, BLK-36 checks, dataset generator, eligibility screen, V1 script | 0.8 | Verified |
| 2026-08-27 | 05:26–08:02 | Gate 1 attempt 1; diagnosing the thinking-mode confound | ~1.0 | Estimated — 2.6h span containing one GPU run and a long queue wait |
| 2026-08-27 | 08:02–09:47 | Second instrument fix (first-word scorer), attempts 2 and 3, Gate 1 clears | 1.7 | Verified |
| 2026-08-27 | 09:47–13:05 | Stage 1 passive-readout script, two readout positions, controls, pre-registration | ~1.5 | Estimated — 3.3h span; the script did not exist at its start |
| 2026-08-27 | 13:05–15:05 | Method section §2.1–2.5 integrated; arm 3 written; accounting fix; job tuning | 2.0 | Verified |
| 2026-08-27 | 15:05–03:45 | Stage 1 executes; device bridge drops mid-commit | ~0.5 | Estimated — 12.7h span, almost all idle and queue wait |
| 2026-08-28 | 03:45–05:41 | Run records committed, V2 documented negative, notes on the invalid runs, controls 10/11 cut, Hour 2 log filled, coach interpretation, cross-reference attempted, shared-vocabulary dataset | 1.9 | Verified |

| 2026-08-28 | 16:13–16:29 | TinkerCliffs environment rebuilt from scratch: venv, HF cache, pinned model and lens revisions, smoke job | 0.0 | Uncounted — ARC setup, by Jason's ruling |
| 2026-08-28 | 20:36–22:10 | Stage 2 on both clusters: environment verification, partition fix, submission, answer-shadow analysis, record-level join, cross-cluster comparison, run records committed, results doc, conformance-check repair | ~1.0 | Estimated — 1.6h span containing two device-bridge outages totalling roughly 50 min |

**Running total: 11.1 / 20.0** — 7.1 verified, 4.0 estimated.
**Verified with artifacts at both ends: 7.1h.** The estimated blocks are
labelled, never folded in.
**Exec summary: 0.0 / 2.0**
**Paper reading: 0.0 of the 5.0 allowance** (the 2026-08-22 literature scan
predates the project lock and is not counted).

## What is deliberately NOT counted

- Slurm queue waiting. Jobs 550627 and 550652 were cancelled after 90 minutes
  pending and never ran; job 550652's wait alone was ~1.5h. The rules exclude
  waiting on compute.
- The device-bridge outages on 2026-08-28 (three of them, roughly 50 min in
  the evening alone) and the overnight gap.
- Environment setup: node install, SSH plumbing, ControlMaster, the transport
  protocol. Generic tech setup by the rules.
- Time before the first commit of any verified block.

The estimates could each be wrong by roughly an hour in either direction. They
are labelled rather than smoothed into the verified figures, and the total is
reported as a split rather than a single number, so a reader can discount the
estimated portion entirely and still see 7.1 hours with artifacts at both ends.

Track with [Toggl](https://toggl.com/) — Neel encourages attaching a
screenshot to the write-up. **No Toggl record exists for this project; this
ledger is the substitute and says so.**
