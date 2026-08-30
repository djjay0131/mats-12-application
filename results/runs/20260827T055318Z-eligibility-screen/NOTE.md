# INVALID RUN — do not cite the eligibility numbers in this directory

Written 2026-08-27, after the fact, by the agent that produced the run. Nothing
in the run's own artifacts has been altered: `manifest.json`, `command.txt`,
`stdout.log` and `outputs/` are exactly as the job wrote them. This file is an
annotation, not a correction.

## What is wrong

This is the **first** of three eligibility screens. It ran with
`max_new_tokens=4`.

Qwen3.5 opens a zero-shot raw completion with a `<think>` tag. Four tokens were
consumed by that tag before any answer token could appear, so **every zero-shot
cell scored near zero by construction**. Few-shot demonstrations suppress
thinking mode and make the model terse, so few-shot cells got real answer tokens
and scored high.

The table this produced:

    real   zero  AB=0.067   [STOP]
    real   few   AB=0.967   [PASS]

reads as "few-shot works, zero-shot is hopeless". The valid run says the
opposite: **real/zero = 0.900 PASS, real/few = 0.667 MARGINAL**. The ordering
inverts completely. This run measured the token budget, not the model.

## Where the valid result is

`results/runs/20260827T090437Z-eligibility-screen/` (job 550555, commit
11aa27c). Its own `NOTE.md` describes all three attempts.

## What else is in this allocation

Job 550510 also ran V1 tooling verification
(`results/runs/20260827T055404Z-v1-tooling-verification/`). **V1 is valid.** It
does not generate text, so the token-budget bug cannot reach it, and its numbers
reproduced exactly in the two later allocations (jlens pass@10 0.350, logit lens
0.200). The shared slurm log `results/slurm-logs/gate1-550510.out` therefore
contains one invalid block and one valid one.

## Two other things visible here, both real

- `git=b138b886... DIRTY` is a genuine dirty tree, not the self-inflicted kind
  fixed later in `src/runlog.py`. ARC was sitting at the branch point with the
  work uncommitted when this ran. It was fixed by rsyncing `.git` across before
  the next run.
- `[padding control] batched==unbatched: False (1/8 mismatched)` was already
  failing at this point. It is still not root-caused. Every reported number
  since has been produced unbatched, and the control is retained as a diagnostic
  rather than dropped.

## Why this run is kept

Deleting it would leave a gap between attempt and result that a reader could not
audit. The failure is part of the record: two successive instrumentation bugs
were caught, the second only because a suspiciously stable number prompted
reading the raw generations. That is worth more on the record than a clean
directory listing.
