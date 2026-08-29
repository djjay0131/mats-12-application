# Stage 2 — the answer-shadow test and the cross-cluster replication

**This is a method evaluation using a narrow task as an instrument. It is not circuit
discovery.** The question is what J-Lens can and cannot be credited with reading, and
the answer below is mostly about what it cannot.

Runs: Falcon job **551834** (L40S, `results/runs/20260828T2051*`–`20260828T2054*`) and
TinkerCliffs job **7298944** (A100, `results/runs/20260828T2040*`–`20260828T2045*`).
Both at repo commit `06ef3a5`, lens `neuronpedia/jacobian-lens` @
`16a01f309fcec900fdcec3f4cd5b64f3d00e4d5a`, model `Qwen/Qwen3.5-4B` @
`851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`, dev split n=40 / 10 pairs /
`vocab_pool=6` / seed 20260827. See `experiments/stage2/tinkercliffs-env/README.md`
for what was pinned across the two clusters and what was deliberately allowed to differ.

> **CORRECTION, 2026-08-29 — read before any prequery number below.** The
> prequery position sits at the last token of the facts block, *before the
> question names a subject*. At that point the prompt does not determine which
> entity is the correct intermediate, so a directional readout there has nothing
> to be right about: **`frac` 0.550 is the control passing, not the lens
> failing.** Earlier wording in this document described it as J-Lens failing to
> pick between the correct intermediate and its twin. That was wrong. The
> prequery median-rank result (346 against the logit lens's 78,525) stands and is
> a **concept-availability** finding, not a binding finding. The consequence is
> that binding had never been measured at a position where it is determined but
> not yet emitted, which is what the post-query sweep exists to do — see
> `llm/memory_bank/research-learning-log.md`, Hour 3.

**Every number here is `agent-unverified`.** They come from this pipeline and share its
code. Nothing below should enter the write-up as settled until it has been re-derived by
a path that does not.

## The test

`experiments/stage1/passive_readout.py` now keeps `model_logits` from the same
`lens.apply()` call, at the same readout position (`positions=[-1]`, the final `:`).
That makes it possible to ask the question the headline depended on: **when J-Lens
"finds" the correct intermediate at the final position, is it reading a hidden
intermediate, or a shadow of what is already in the model's own output distribution?**

## The answer

The model's own final-layer logits, 40 dev records:

| quantity | value |
|---|---|
| records where correct intermediate outranks the alternative | **37 / 40 = 0.925** |
| mean intermediate margin | **+2.766** |
| records where correct answer outranks the alternative answer | 40 / 40 = 1.000 |
| mean answer margin | +2.442 |
| `rank_answer == 1` | 30 / 40 |
| `argmax_is_answer` | 3 / 40 (the rest is `<think>`-style continuation) |

**The direction bit is a shadow.** "The correct intermediate outranks the alternative"
is true of the model's own output 92.5% of the time at that position. J-Lens's
best pre-registered final-position layer scores 0.975 on exactly that statistic.
The 0.975 is therefore *not* evidence of a recovered hidden intermediate — the
output already carries almost all of it.

Internal consistency check that this is measuring what it claims: the logit lens
at L30 (the last layer) scores 0.900 with mean margin +2.854, which is the model's
own output reached by a different code path. It agrees with the direct read.

## What survives

Rank, not direction, and at matched layers. Median rank of the correct intermediate
over the full 248,320-wide unembedding, final position:

| layer | J-Lens frac / median rank | logit lens frac / median rank |
|---|---|---|
| 25 | 0.800 / **2,280** | 0.675 / 90,652 |
| 26 | 0.775 / **2,257** | 0.700 / 62,877 |
| 27 | 0.975 / **35** | 0.950 / 1,022 |
| 28 | 0.950 / **49** | 0.925 / 869 |
| 29 | 0.950 / **14** | 0.900 / 32 |
| 30 | 0.925 / **11** | 0.900 / 19 |

Read down the table: the two methods converge at L30, which is what they should do,
because at the last layer both are approximately the model's output. The gap opens
as you move earlier — 29× at L27, 40× at L25 — and that gap is the part of the
result the output shadow does not explain.

The prequery position is the cleaner version of the same claim, because the model's
next-token distribution at the final position cannot be the explanation there:

| position | J-Lens | logit lens |
|---|---|---|
| prequery (best layer) | frac 0.550 / median rank **346** | frac 0.525 / median rank 78,525 |

227× on rank. `frac` is 0.550 against a 0.500 floor, and that is the **expected and
correct** value: at prequery the question has not yet named a subject, so neither entity
is the correct intermediate and there is no direction to recover. The chance-level `frac`
is the control passing. What the position does show is that J-Lens puts the concept set
two orders of magnitude higher in the ranking than the logit lens does at a point where
neither concept is privileged — **concept availability, not binding.**

## The claim that is supportable

Not "J-Lens recovers binding." Not "J-Lens identifies the correct hidden intermediate."

Supportable, as a method claim about localization rather than about binding:
**at matched layers, J-Lens places the correct intermediate one to two orders of
magnitude higher in a 248,320-token ranking than the logit lens does, including at a
position where the model's own output distribution cannot account for it — while the
directional bit ("correct intermediate beats its role-swapped twin") is, at the final
position, already 92.5% present in the model's output and therefore not J-Lens's to
claim.**

## Two things that must not be quietly folded in

**1. The headline number moved because the dataset moved, not because the cluster did.**
Stage 1's framing was J-Lens median rank 30 vs logit lens 1290. Here the logit lens
reads 19 at the final position. The dev split was regenerated with `--vocab-pool 6`
so that arm 3 had class support outside every held-out pair, which means the
intermediate is now one of six frequent city names instead of one of fourteen. That
makes the task easier for *every* method, the logit lens most of all. The two numbers
are not comparable and must not be presented as if they were.

**2. The cross-platform replication is not clean.** Same commit, same dataset, same
lens and model revisions; the behavioural eligibility screen scores **AB = 0.900 on
TinkerCliffs (A100)** against **AB = 1.000 on Falcon (551834, L40S)**, and the screen's
own padding control moves from 2/8 mismatched to 0/8 between them. One prompt out of ten
flips its behavioural label between two GPUs. That is small, and it is not nothing: it is
a direct measurement of how much of the eligibility number is floating-point luck, and it
needs to be stated wherever eligibility is quoted rather than reconciled away. Part 2
gives the full side-by-side.

## Arm 3, same job

| | TinkerCliffs 7298944 | Falcon 551581 |
|---|---|---|
| final L30 LOO margin | +24.717 | +24.775 |
| final L30 LOO accuracy | 0.650 | 0.625 |
| final L30 in-sample accuracy | 0.750 | 0.800 |
| prequery L30 LOO accuracy | 0.525 | 0.525 |

Leave-one-pair-out now scores all 40 records with zero `class_unseen_in_fit`, which
was the point of the dataset regeneration. The supervised reference reaching only
0.650 leave-one-pair-out at the final position is itself load-bearing for section 2.5:
a supervised difference-in-means probe with the answer in hand does barely better
than J-Lens does, which bounds how much linearly-decodable binding is in that residual
at all.

## Next

Part 2 below adds the record-level join this section could not do on its own, plus
the Falcon comparison. Read both parts before quoting any number from either.

---

# Part 2 — the record-level join, and the cross-cluster replication

## Falcon 551834 (L40S) against TinkerCliffs 7298944 (A100)

Same commit `06ef3a5`, same dataset, same revisions. Falcon = L40S, TinkerCliffs = A100.

| | Falcon 551834 | TinkerCliffs 7298944 |
|---|---|---|
| selected layers (jlens final / prequery, logitlens final / prequery) | 27 / 25 / 30 / 24 | 27 / 25 / 30 / 24 |
| jlens final: margin, frac, median rank | +3.794, 0.975, 37 | +3.848, 0.975, 35 |
| jlens prequery: margin, frac, median rank | +0.068, 0.550, 357 | +0.070, 0.550, 346 |
| logitlens final: margin, frac, median rank | +2.823, 0.900, 20 | +2.854, 0.900, 19 |
| logitlens prequery median rank | 78,568 | 78,525 |
| random-transport control, final median rank | 128,589 | 128,084 |
| arm 3 final L30 LOO margin / acc | +24.199 / 0.625 | +24.717 / 0.650 |
| **eligibility AB** | **1.000** | **0.900** |
| **padding control batched==unbatched** | **True (0/8)** | **False (2/8)** |

Every layer selection is identical, every `frac` is identical, and the median ranks agree
to within about 5%. **The passive readout replicates across GPU architectures.** That is
a real and non-trivial result for a method-evaluation write-up: the numbers are a property
of the method, not of one node.

The behavioural eligibility screen does not replicate: 100.0% on the L40S, 90.0% on the
A100, and the internal padding control flips from 0/8 mismatched to 2/8. This is the
expected shape of the failure — the screen decodes greedily, and greedy decoding turns
last-bit floating-point differences into different tokens. It means the eligibility
percentage should be quoted with that instability attached, and it means **the binary
readout-vs-behaviour contingency table is not a usable instrument on this split**, because
on Falcon it has zero discriminating cases by construction.

## The contingency table, built on the TinkerCliffs run because it is the only one with any disagreement

Joined on `record_id`, n=40, J-Lens arm, final position, selected layer 27. Readout correct
:= `rank_correct < rank_incorrect` for the intermediate. Model correct := `text_match`.

| | readout correct | readout wrong |
|---|---|---|
| model correct (39) | 38 | 1 |
| model wrong (1) | 1 | 0 |

**One discriminating case.** n=1 supports nothing; reporting it as "the readout recovers
the intermediate on the record the model gets wrong" would be a single coin flip dressed
as a result. Prequery, same join: 22/39 correct where the model is correct, 0/1 where it
is not.

## So the graded measure, which is what the question actually needs

Pearson correlations over the 40 dev records, J-Lens intermediate margin against the
model's own final-layer margins:

| pair | r |
|---|---|
| J-Lens L27 (final) margin **vs model's intermediate margin** | **+0.771** |
| J-Lens L27 (final) margin vs model's *answer* margin | −0.016 |
| logit lens L30 (final) margin vs model's intermediate margin | +0.811 |
| J-Lens L25 (**prequery**) margin vs model's intermediate margin | +0.445 |

The third row is the anchor, and it is why this measurement can be interpreted at all.
The last-layer logit lens is about as close to "just reading the output" as a lens gets,
and it scores 0.811 — not 1.000, because the lens reads the residual through its own path.
So 0.811 is roughly what a pure shadow looks like on this data.

**J-Lens at its selected final-position layer scores 0.771. That is a shadow, to within
the resolution of this measurement.** Its readout at the final position moves with the
model's own output preference for the intermediate, and is uncorrelated with how well the
model answers.

At the prequery position the coupling drops to 0.445 — the readout there is substantially
not a function of the final-position output. That is what makes the position clean. It is
also why the position cannot carry the primary claim: it is clean *because* nothing has
been determined yet.

## Where the shadow and the truth disagree

Only 3 of 40 records have the model's own output preferring the *wrong* intermediate.
On those, J-Lens at L27 goes with the truth on 2 and follows the output down on 1 — and
the one it gets wrong is the record where the output is most wrong (model margin −1.19,
J-Lens margin −0.19). **n=3.** That is the entire discriminating set on this split, and it
is the strongest argument for a larger held-out split: the question this project is asking
is only answerable on records where the output shadow and the correct intermediate come
apart, and this dataset produces three of them.

Readout accuracy by quartile of the model's own intermediate margin (n=10 each):

| quartile | mean model intermediate margin | final readout acc | prequery readout acc |
|---|---|---|---|
| Q1 | +0.59 | 0.90 | 0.10 |
| Q2 | +2.17 | 1.00 | 0.80 |
| Q3 | +3.40 | 1.00 | 0.50 |
| Q4 | +4.91 | 1.00 | 0.80 |

Final-position accuracy is flat at ceiling and tells us nothing. Prequery is not monotone
and at n=10 per cell is noise. Neither table changes the conclusion the correlations give.

## Revised statement of what this run supports

1. The passive readout replicates across two GPU architectures. **Method claim, supported.**
2. At the final position, J-Lens's preference for the correct intermediate is coupled to the
   model's own output preference at r=0.771 against a shadow anchor of 0.811. **The
   directional finding at the final position is not evidence of a hidden intermediate.**
3. At matched layers J-Lens still localizes the intermediate 30–250× higher in the ranking
   than the logit lens, and at the prequery position the output coupling falls to 0.445.
   **Concept-availability claim, supported. Binding claim, NOT MEASURED** — not "not
   supported". The final position is contaminated and the prequery position is
   undetermined; neither can answer it. See the correction at the top.
4. The binary behaviour-vs-readout contingency table is dead on this split — one
   discriminating case on one cluster, zero on the other. It should be dropped from the
   write-up rather than reported with n=1.
5. The dataset yields three records where the shadow and the truth disagree. Any strong
   version of the project's question needs a split built to produce more of them.

All numbers `agent-unverified`.

---

# Part 3 — why the discriminating set is three records

Added 2026-08-29. Produced by `experiments/analysis/output_shadow_audit.py`, a
committed script with a run record, not by ad-hoc inspection. Run on both
clusters' Stage 2 records; the audit itself replicates.

## The measurement

| | TinkerCliffs 7298944 | Falcon 551834 |
|---|---|---|
| generation names the intermediate in plain text | **38 / 40 (0.95)** | **38 / 40 (0.95)** |
| generation names the answer | 40 / 40 | 40 / 40 |
| generation names the *alternative* intermediate | 1 / 40 | 1 / 40 |
| `<think>`-mode generations | 37 / 40 | 37 / 40 |
| model's own final-layer intermediate margin, mean | +2.766 | +2.728 |
| records with a **negative** such margin | **3 / 40** | **3 / 40** |
| r(J-Lens final margin, model's intermediate margin) | +0.771 | +0.773 |
| shadow anchor: r(last-layer logit lens, same) | +0.811 | +0.810 |
| r(J-Lens final margin, model's **answer** margin) | −0.016 | −0.032 |
| r at the **prequery** position | +0.445 | +0.445 |

95% Wilson interval on 3/40: **[0.026, 0.199]**. The rate itself is barely
estimated, which is a further reason not to build a claim on those three records.

## What it says

**The intermediate is not hidden at the readout position.** The model writes it
out: "Helen lives in **Prague**. The fact states that **Prague uses wool**." So
the final-position next-token distribution carries the intermediate because the
model is about to say it. Recovering it from the residual there is close to
reading the model's next few words, and that is what the r=0.771 against a 0.811
shadow anchor is measuring.

**It is not the items, and not the task shape.** Mean model intermediate margin
by cell: A/AB 2.31, A/BA 3.66, B/AB 2.58, B/BA 2.52. The three negatives fall in
three different pairs. The margin distribution is smooth and unimodal from −1.19
to +5.75 — 3 records below 0, 5 below +1.0, 12 below +2.0. Nothing clusters. The
AB/BA role-swap structure, the six-word vocabulary and the pair construction are
all behaving as designed; the shortage is a global shift, not a structural defect.

**The eligibility screen and the discriminating criterion are near-complements.**
Eligibility keeps records the model handles correctly. The audit needs records
where the output does not already contain the intermediate. Those two sets are
close to complementary, so the filter that makes a stimulus valid is close to the
negation of the filter that makes it informative. That is why neither scaling n
(linear: 400 records buys about 30) nor making the task harder (harder items fail
eligibility and are excluded) fixes it.

This is the most transferable observation in the project, and it generalizes past
this task: **any passive-readout design that reads at a position on the model's
own generation path, and that screens stimuli on behavioural correctness, will
have this problem.** Models that reason in text put their intermediates on the
surface, and a lens that reports them is not thereby reporting a latent.

## The one thing that argues against the mechanism

The two records whose generations do **not** name the intermediate still have
model intermediate margins of +3.31 and +1.31, and the readout gets both right.
If surface restatement were the whole story those two should sit near zero. They
do not. n=2 supports no conclusion, but it is enough to say the output
distribution may carry the intermediate whether or not the text names it — in
which case suppressing the chain of thought would move the discriminating set
very little.

That is a testable disagreement, and it is the subject of `docs/adr/0006-*`,
which proposes exactly that test and commits in advance to rejecting the change
if the discriminating set does not grow.

## Provenance

`results/runs/20260829T033500Z-output-shadow-audit/` (TinkerCliffs records) and
`results/runs/20260829T033509Z-output-shadow-audit/` (Falcon records). Both read
committed run records and `results/datasets/dev.jsonl`, join on `record_id`, load
no model and use no GPU. Run on the agents4research VM, not on an ARC login node.

All numbers `agent-unverified`.
