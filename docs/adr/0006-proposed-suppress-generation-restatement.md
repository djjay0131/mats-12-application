# ADR-0006: Suppress the model's own restatement of the intermediate before the held-out freeze

Status: Deferred — not actioned; kept as future work or pivot (Jason, 2026-08-29)

Resolution: the post-query sweep ran and rule 1 of its pre-registered decision
rule fired — J-Lens resolves direction at q05/q06, inside the window, on both
clusters (Falcon 552322, TinkerCliffs 7307558). The regeneration this ADR
proposes is therefore not needed for the primary claim, and Jason ruled on
2026-08-29 not to action it. It is deliberately kept rather than rejected:
it becomes relevant again if the q05/q06 result weakens on held-out, or as
the robustness check it was originally designed to be, and its accept/reject
criterion and self-falsification evidence remain as written.
Date: 2026-08-29

This ADR does not change the research question, the substrate, the lens, or the
task family. It changes ONE thing about the instrument — the prompt format — and
it is written as an ADR rather than done quietly because it must be decided
BEFORE the held-out split is frozen, and because it moves what the primary
number means.

## Context

Stage 2 produced a result that looks strong and is not what it appears to be.
At the final readout position, at its pre-registered layer, J-Lens prefers the
correct intermediate over its role-swapped twin on 39 of 40 dev records.

`experiments/analysis/output_shadow_audit.py` was written to test whether that
means anything, and run against both clusters' Stage 2 records. It replicates:

| | TinkerCliffs 7298944 | Falcon 551834 |
|---|---|---|
| generation names the intermediate in plain text | **38 / 40 (0.95)** | **38 / 40 (0.95)** |
| generation names the answer | 40 / 40 | 40 / 40 |
| generation names the *alternative* intermediate | 1 / 40 | 1 / 40 |
| model's own final-layer intermediate margin, mean | +2.766 | +2.728 |
| records where that margin is **negative** | **3 / 40** | **3 / 40** |
| coupling r(J-Lens final margin, model's intermediate margin) | +0.771 | +0.773 |
| shadow anchor: r(last-layer logit lens, same) | +0.811 | +0.810 |
| r(J-Lens final margin, model's **answer** margin) | −0.016 | −0.032 |
| coupling at the **prequery** position | +0.445 | +0.445 |

The 95% Wilson interval on 3/40 is [0.026, 0.199].

Three readings follow, and they are the reason for this ADR.

**The intermediate is not hidden at the readout position.** In 38 of 40 records
the model writes the intermediate city into its own output — "Helen lives in
**Prague**. The fact states that **Prague uses wool**." 37 of 40 generations are
`<think>`-mode. So at the final `:` the intermediate is not a latent the lens
recovered; it is a token the model is queued to emit. Reading it out of the
residual there is close to reading the model's next few words.

**The discriminating set is three records.** A passive readout at this position
can only be distinguished from an output shadow on records where the output
preference and the correct intermediate disagree. There are three. On those
three J-Lens goes with the truth twice and follows the output down once, and the
one it misses is the record where the output is most wrong.

**It is not the items and not the task shape.** Mean model intermediate margin
by cell is A/AB 2.31, A/BA 3.66, B/AB 2.58, B/BA 2.52; the three negatives fall
in three different pairs; the margin distribution is smooth and unimodal from
−1.19 to +5.75. The AB/BA role-swap structure is behaving exactly as designed.
The shortage is global, not structural, and it is not fixed by changing which
entities appear or how the pairs are built.

## Decision

Before the held-out freeze, regenerate the stimuli with a prompt format that
does not license the model to restate the intermediate before answering: answer
with the object alone, no chain of thought, no explanatory preamble. Run the
eligibility screen and the passive readout unchanged against it, and report the
same audit.

Accept the change only if the audit shows the discriminating set grow. Report
the audit either way, including if it does not.

## Rationale

Two other ways of getting more discriminating records were considered and both
fail on inspection:

**Scale n.** At the observed rate, 400 records buys about 30 discriminating
ones. That is linear in GPU time, and 30 is still thin for the claim. It also
does not address the reason the rate is low.

**Make the task harder.** Harder items make the model fail; failing items are
excluded by the eligibility screen; the discriminating set does not grow. This
is the sharp form of the problem: **the eligibility criterion and the
discriminating criterion are close to complements.** Eligibility keeps records
the model handles correctly. The audit needs records where the output does not
already contain the intermediate. Selecting hard for the first selects against
the second. No amount of stimulus engineering escapes that while the readout
position sits on the model's generation path.

Changing the prompt format attacks the position rather than the stimuli. If the
model never emits the intermediate, the final-position output has much less
reason to carry it, and records that are currently non-discriminating become
discriminating without becoming ineligible.

## What would falsify the premise

Deliberately recorded, because the mechanism is a hypothesis and not established:

The two records whose generations do **not** name the intermediate still have
model intermediate margins of **+3.31** and **+1.31**, and the readout gets both
right. If surface restatement were the whole mechanism those two should sit near
zero. They do not. n=2 is far too small to conclude anything, but it is enough to
say that the output distribution may carry the intermediate whether or not the
text names it — in which case suppressing the chain of thought will move the
discriminating set very little, and this ADR should be rejected on its own
evidence rather than defended.

That is precisely why the decision is "accept only if the audit shows the set
grow," and why the audit is a committed script rather than a judgement call.

## Alternatives Considered

**Do nothing and report the prequery position as the primary result.** Now known to
be unavailable, and the reason supersedes part of this ADR. The prequery position
precedes the question, so no entity is yet the correct intermediate and its
chance-level `frac` of 0.550 is the control passing rather than a lens failure. It
can report concept availability — median rank 346 against the logit lens's 78,525 —
but it cannot report binding, because at that position there is no binding to report.

**Read the post-query window first.** Between the undetermined prequery position and
the contaminated final position lies the span from query onset to the last token,
where the binding is determined but not yet emitted. That span was never read. The
sweep over it is cheap, uses the same stimuli and the same runs, and it decides
whether this ADR is needed at all: if J-Lens resolves direction in that window, the
regeneration proposed here is likely unnecessary. The pre-registered decision rule
is in the Hour 3 entry of `llm/memory_bank/research-learning-log.md`. **This ADR is
therefore held pending the sweep**, and its status stays Proposed.

**Intervene rather than read.** Patch the intermediate and check whether the
answer moves. This removes the confound completely, because it does not depend
on what the output distribution happens to contain. It is also a different arm,
a different cost, and outside the remaining budget — it belongs in the write-up
as the obvious next experiment, not in this project.

## Consequences

**If accepted.** The dev numbers currently in `results/stage2/` are superseded
as the primary result and must be reported as the contaminated-position
measurement they are, not deleted. The pre-registered layer rule must be re-run
on the new dev split, and that must be stated. One additional GPU job, roughly
four minutes of compute at the observed Stage 2 runtime.

**If rejected.** The write-up reports the shadow finding as the primary
methodological result and the prequery position as the uncontaminated
measurement, and states plainly that the final-position number is not evidence
of recovered binding. This is a smaller claim than the project set out to make
and a more defensible one.

**Either way.** The write-up states that the eligibility screen and the
discriminating criterion are near-complementary filters. That is a general
observation about passive-readout designs on models that reason in text, it is
measured rather than asserted, and it is the most transferable thing this
project has produced.
