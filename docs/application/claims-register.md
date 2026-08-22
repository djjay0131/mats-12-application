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
| CL-01 | *(example — delete)* Faithfulness drops between the DPO and RLVR checkpoints. | method-claim | Instruct-branch arm at matched stages; random-hint control | `results/fig-01-stagewise.png`, `results/canonical.json#stagewise` | n=500/stage, seed=1337 |
| CL-02 | | | | | |

Types: `existence-proof` · `method-claim` · `general-claim`
