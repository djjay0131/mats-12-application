# PREEMPTED ATTEMPT of job 7307558 — superseded, do not cite as a separate run

This directory was produced by TinkerCliffs job **7307558**, the post-query
position sweep, and its `manifest.json` names the same log
(`results/slurm-logs/sweeptc-7307558.out`) as the run directories that are cited.
It is **not** a separate experiment.

The job ran on `a100_preemptable_q`. It was started and preempted twice before
the attempt that finished. Slurm's accounting keeps only the final attempt —
`sacct -j 7307558` reports a single COMPLETED run of 6:15 starting 16:52:11
local — and the requeue overwrote the job's log, so the earlier attempts survive
only as these directories. That is why they appear with no matching log output.

Reconstructed from the directory timestamps, which is the only evidence there is:

| attempt | start (UTC) | what it got through |
|---|---|---|
| 1 | 20:26:03 | eligibility screen |
| 2 | 20:34:51 | eligibility screen, then the readout at 20:37:42, killed mid-run |
| 3 | 20:52:45 | eligibility, readout, arm 3 — **this is the cited run** |

**This directory is: attempt 2, passive readout — KILLED mid-run, no outputs.**

The cited results are `results/runs/20260829T205245Z-eligibility-screen`,
`.../20260829T205531Z-stage1-passive-readout` and
`.../20260829T205800Z-stage1-supervised-reference`.

These directories are kept rather than deleted because they are real output that
really ran, and because the two completed eligibility attempts are independently
useful — see the Hour 3 entry in `llm/memory_bank/research-learning-log.md`.
Nothing here has been back-filled or reconstructed into a manifest; the note is
the record of what is known and what is not.
