# ADR-0002: Project selection for the 20-hour application task

Status: Superseded by ADR-0005
Date: 2026-08-24 (superseded 2026-08-26)
Deciders: Jason

## Context

Five candidates are scored in `llm/plan/project-candidates.md` against
fit to Neel's stated interests, originality, 20-hour feasibility, baseline
availability, and whether a null result is still interesting.

Recommendation going in: **C2** (CoT unfaithfulness across the Olmo 3
post-training lineage) primary, **C1** (does eval-awareness contaminate
faithfulness measurements) backup, **C4** fallback.

**Verified 2026-08-22 — the C2 gating fact is GO.** All four Think-branch
stage endpoints are public Apache-2.0 repos (`allenai/Olmo-3-1025-7B` →
`Olmo-3-7B-Think-SFT` → `Olmo-3-7B-Think-DPO` → `Olmo-3-7B-Think`), and 98
intermediate checkpoints exist as git branches (55 RL, 43 SFT). Dolci
SFT/DPO/RL datasets public. C2 scores 24/25 and is the recommendation.

One substituted risk to resolve before accepting: **`Think-SFT` ships a
different tokenizer and no chat template.** Confirm `<think>`/`</think>`
tokenize identically at all four stages, or every cross-stage comparison is
confounded.

## Decision

*To be written at Gate 1, after the 2-hour de-risk pilot.*

Record:
- The candidate chosen and why the others were not.
- The tokenizer-parity result across the four stages.
- Whether the de-risk pilot replicated the phenomenon in *this* setup
  (this model, these prompts, this dataset).
- The one-sentence claim the project is trying to establish.
- The single graph intended to carry the executive summary.
- Clock state: hours consumed so far, and whether a reset occurred.

## Consequences

*To be written.*

## Gate 1 exit criteria

Do not accept this ADR unless all three hold:

1. The phenomenon replicates in my setup.
2. The claim fits in one sentence.
3. I can name the graph that carries the executive summary.
4. `node scripts/conformance-check.mjs --gate SELECT` is green.

If any fails: switch to the backup candidate and **reset the 20-hour
clock** (explicitly permitted — *"If you decide your project is doomed,
you're welcome to give up and start a new one, and reset the timer"*).
Record the reset here.

## Outcome (2026-08-26)

Never accepted, never executed against. Superseded by
[ADR-0005](0005-accept-jlens-relational-binding.md), which selects the
J-Lens relational-binding project (C6). Candidate C2 remains the strongest
fallback: its checkpoints are verified public and it requires no lens.

The C2 gating fact (Olmo 3 Think stage checkpoints public — verified GO,
plus 98 intermediate checkpoints as git branches) stands and is preserved in
`llm/plan/project-candidates.md` should the fallback ever be needed.
