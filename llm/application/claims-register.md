# Claims Register

Every claim the write-up makes, typed. Checked by
`scripts/conformance-check.mjs` (SCR-22).

**Why typing matters.** Neel's doc pulls two ways on cherry-picking:

> "avoid relying only on a few cherry-picked qualitative examples — this is
> a major red flag"

> "Sometimes you want to give an existence proof (e.g., find an example of
> an interesting phenomenon), where cherry-picking is fine."

The resolution is to declare which kind of claim you are making, per claim.
An `existence-proof` may be cherry-picked **and must say so**. A
`method-claim` or `general-claim` requires random sampling with a recorded
seed **and** a baseline. An untagged cherry-pick carrying a general claim
is the failure mode he calls a red flag.

| ID | Claim (one sentence) | Type | Baseline / control | Evidence (figure, table, file) | Sampling |
|---|---|---|---|---|---|
| CL-01 | J-Lens's apparent recovery of the intermediate at the final token is the model's output forming, not binding recovery. | method-claim | Output-shadow control: the model's own next-token distribution in the same pass; independent hand re-derivation | writeup §4.2a; `results/verification/verify-shadow-554518.out` | all 40 dev pairs; 37/40 hand-verified |
| CL-02 | Direction resolves above chance at the relation-completing token and the question mark on unseen data. | method-claim | Label-permutation control per position; norm-matched random transport; anchors and layers frozen before the read | writeup §4.2c; `results/stage2/FREEZE.md`; fig `stage3-frac-by-position` | held-out n=160, read once, seed 20260827, all six templates |
| CL-03 | The window signal is the model's developing output preference, not latent binding. | method-claim | The model's own preference measured at those positions as the control; lenses scored on the discriminating-set records where that preference points wrong | writeup §4.2c; `experiments/analysis/window_shadow_audit.py`; fig `stage3-discriminating-set` | 32–40 discriminating records of the held-out 160 |
| CL-04 | J-Lens localizes the bound concepts far above the logit lens by rank. | method-claim | Random transport (rank ~150k); label permutation; coverage positive control (reference pass@10 0.350 vs 0.200) | writeup §4.4 | held-out n=160, seed 20260827; six-city collision caveat attached |
| CL-05 | Binding is not linearly present beyond the output preference at these positions. | method-claim | Supervised difference-in-means linear probe, fit on dev and applied unchanged to held-out | writeup §2.5, §4.2c | dev fit, held-out n=160 |
| CL-06 | "Just ask the model" upper-bounds this task, so prompting dominates every internal readout here. | general-claim | Direct prompting = the eligibility screen itself, run as the baseline | writeup §4.1 | eligibility screen, real lexicon, zero-shot |
| CL-07 | The five qualitative examples illustrate success, failure, and a boundary case. | existence-proof | None required; cherry-picking disclosed — but these are randomly drawn, not cherry-picked | writeup raw-examples section | random draw, seed 1337, over held-out record ids |

Types: `existence-proof` · `method-claim` · `general-claim`
