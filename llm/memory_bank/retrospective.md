# Retrospective — MATS 12.0 application project

Written 2026-09-17, after the decision (not accepted). One page, mine.

## What this was

This was my first project in mechanistic interpretability, and my first step
toward a longer goal: humans being able to read the mind of an AI. The
question was small on purpose. Can J-Lens read which city goes with which
person out of the residual, or is it only predicting what the model is about
to say?

## What we found

At every point we checked, there was no binding information in the lens
reading. J-Lens beat the shuffled-label control (0.781 vs 0.519 at the
relation token), but the model itself was already leaning the right way 0.800
of the time at that spot, and on the records where the model leaned wrong the
lens went wrong with it (0.344 and 0.125 against 0.500 chance). A probe
trained with the answer key read 0.525 at the same spot. So we concluded that
the lens is predicting what the model will answer, not putting the answer
together from stored binding data. The one thing J-Lens clearly did better
than the logit lens was rank the right word higher (median rank 128 vs 393 on
held-out).

## What worked

- Pre-registering the decision rules and freezing positions and layers before
  touching the held-out set. When the first headline dissolved (the
  final-token result was the output leaking in), the record showed it was
  caught, not hidden.
- Saving the model's own next-token preference in the same forward pass. That
  one extra column turned "the lens beats the control" into "the lens follows
  the model", and it is the part that travels to other lenses.
- The run manifests, the claims / controls / verification ledgers, and the
  time ledger. They cost time up front and paid it back at write-up.
- Keeping the agent's numbers separate from my own re-derivations. The rank
  spot-check is what caught the off-by-one layer convention.

## What did not work

- The causal test. The released code did not have the piece it needed and I
  ran out of budget, so every claim is correlational.
- The six-city pool. It kept the probe readable but weakened the
  shuffled-label control: only 65 of 160 shuffled keys were fully different
  from the real one.
- One pre-registered prediction was wrong. I expected the model's own leaning
  to be near zero mid-question; it was 0.800. Recorded, not revised.
- Time. The executive summary came together at the very end and had to be
  cut hard the night before the deadline.
- The write-up was too long for what it said and was condensed three times
  (27 pages to 15). Writing short is cheaper than cutting long.

## What I would do differently

- Write the executive summary from day one, one paragraph per experiment,
  and update it as results land.
- Draw the held-out set larger up front. n=32 / 40 on the discriminating set
  is too small to separate the two lenses from each other.
- Probe the fact tokens first. The pairing has to exist somewhere, and I never
  looked where it is built.
- Start the causal test early enough that a missing piece in someone else's
  code is a task, not a blocker.

## Next

To get closer to the truth we keep probing: the fact tokens, activation
patching between swapped twins, the resample control, a fresh held-out draw,
and a trained probe (Phase 1 of `llm/plans/continuation-plan.md`). We expect
there is binding data somewhere we can reach; we are not sure the lens can
expose it. Either answer is a result.
