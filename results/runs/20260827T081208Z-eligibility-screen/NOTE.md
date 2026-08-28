# INVALID RUN — do not cite the eligibility numbers in this directory

Written 2026-08-27, after the fact, by the agent that produced the run. The
run's own artifacts are unaltered; this file is an annotation, not a correction.

## What is wrong

This is the **second** of three eligibility screens. The token budget from
attempt 1 was fixed here (`max_new_tokens` raised, `</think>` handled), and the
numbers came out **near-identical to attempt 1 anyway**.

That coincidence is what made it convincing, and it was wrong for a second,
independent reason: scoring took the **first word** of the generation. The
model's first word is `"Based"`, from:

    <think>

    </think>

    Based on the facts provided:

    1.  Helen lives in **Perth**.
    2.  The fact states that **Perth uses granite**.

    Therefore, what is used where Helen lives is **granite**.

The answer is right there, at the end, in bold. The scorer never looked at it.
**This run measured the parser, not the model.**

It was caught by reading raw generations after an implausibly stable number,
not by any automated check — worth knowing, because no test would have flagged
it.

## Where the valid result is

`results/runs/20260827T090437Z-eligibility-screen/` (job 550555, commit
11aa27c). It scores by content AND, independently, by the last bolded span. The
two agree (0.950 / 0.883), which is the actual evidence that the model is being
measured. `first_word_accuracy = 0.108` is retained in that run's output as the
permanent record of this broken rule.

## What else is in this allocation

Job 550548 also ran V1 tooling verification
(`results/runs/20260827T082947Z-v1-tooling-verification/`). **V1 is valid** —
it does not generate text, so neither scoring bug can reach it.

## Why this run is kept

Because two independent bugs producing the same wrong number is the most
instructive thing that happened in this project, and it is only legible if both
attempts survive.
