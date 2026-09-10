# ADR-0005: Accept the J-Lens relational-binding project; supersede ADR-0002

Status: Accepted
Date: 2026-08-26
Deciders: Jason
Supersedes: ADR-0002 (project selection)
Resolves: ADR-0004 (proposed J-Lens candidate)

## Context

ADR-0002 selected candidate C2 — measuring CoT unfaithfulness across the
Olmo 3 Think post-training lineage — but was never moved past **Proposed**,
and no work was ever executed against it. No code, no dataset, no findings.

ADR-0004 recorded a competing candidate (C6): does J-Lens recover relational
binding, or only a bag of concepts? It deliberately did not supersede
ADR-0002, and set four conditions to be met first. Three are now resolved;
the fourth is decided here.

Both candidates score **24/25** on the selection rubric
(`llm/plan/project-candidates.md`). The rubric does not separate them.

Two asymmetries do.

**Preparation.** C6 has a verified execution environment. ARC job 550088 on
`falcon1` (L40S) staged `Qwen/Qwen3.5-4B` and the `neuronpedia/jacobian-lens`
lens (revision `qwen-n1000`, commit `16a01f3`) and asserted exact
compatibility: `COMPAT_ASSERTIONS: PASS`, `LAYOUT_ASSERTIONS: PASS`, 32/32
reference tests green, `d_model` 2560 matching on both axes,
`max(source_layers)=30 < 32`, model load 13.6 s, peak GPU allocation
**8.51 GB of 47.7 GB**. C2 has a verified list of public checkpoints and
nothing else. With nine days remaining, that difference is decisive.

**Failure mode.** C6's principal open risk (B2 — the reference
implementation ships no sparse non-negative J-space reconstruction)
threatens only the causal arm; the passive comparison stands without it.
C2's principal open risk — `Olmo-3-7B-Think-SFT` shipping a different
tokenizer and no chat template — threatens the *primary* comparison, with no
graceful degradation. If `<think>` tokenizes differently across stages,
every cross-stage number is confounded. C6 degrades; C2 breaks.

## Decision

**1. Accept C6 as the project.** ADR-0002 is superseded. The question is:

> When two prompts contain the same entities and concepts but assign them
> different relational roles, does J-Lens identify the correct hidden
> intermediate — and does changing that representation causally change the
> model's answer?

Design of record: `llm/plan/jlens-relational-binding-experiment-design.md`.

**2. Scope: passive-primary. The causal arm is a contingent extension, not a
deliverable.**

This is the substantive call, and it is made *before* counting an hour
rather than discovered at Hour 11. B2 is real: a search of the pinned commit
finds no sparse coding, NNLS, non-negative solver, dictionary, or
reconstruction routine — the shipped API is `fit`/`apply`/`transport`/
visualisation only. Implementing the paper's decomposition is precisely the
open-ended work the sprint forbids, and approximating it invites the design's
own FAIL condition: *"'J-space' is implemented as an arbitrary top-token
projection with no correspondence to the paper's sparse construction."*

Therefore:

- H1, H2 and H4 (concept recovery, binding recovery, the limitation
  hypothesis) are the **primary claims**. They require no J-space
  decomposition.
- H3 (causal validity) is **contingent**. It is attempted only if V2
  establishes that a faithful J-space reconstruction is available or
  reproducible inside its one-hour box. If V2 does not clear, causal work is
  declared unavailable and the reclaimed hours go to stronger passive
  controls and a second prompt template — as the design's Hour 11 fallback
  already specifies.
- The write-up must state plainly which arm ran and why, rather than
  presenting a passive-only result as though causal work was never intended.

Choosing this now converts an unbounded risk into a scoped one.

**3. Clock ruling.**

Grounded in the application rules: setup, general preparation, and time spent
waiting are not counted; writing project code, project-specific reading,
analysis, thinking and planning, and the main write-up are. A genuine pivot
permits a reset.

- All work through **2026-08-26** — ARC access, environment build, model and
  lens staging, compatibility assertions, and the design and positioning
  documents — is **ideation and setup. Not counted.** The environment
  manifest's `0.0 h` stands.
- **V1, V2 and V3 count one hour each**, as the verification sprint already
  declares. Log them in `llm/memory_bank/time-log.md` when run.
- **No reset is required.** ADR-0002 was never executed against, so moving to
  C6 is not a mid-project pivot — it is the Gate 1 selection decision
  arriving late. There is no clock to reset because no clock has started.
- Record this accounting in the write-up if the question arises. It should be
  legible without special pleading.

**4. Standing constraints for this project.**

- The primary claim is bounded to a specified layer band and token position
  in a controlled two-hop task. It is **not** a claim about reading the
  model's thoughts. Language to that effect is a write-up defect.
- Development pairs are for debugging and layer selection. The 40 held-out
  pairs are never tuned on.
- Hypotheses and primary metrics freeze at the Hour 7 Explore→Understand
  gate, before any held-out result is examined.
- Every reported number is re-derived by a human via a path not sharing the
  original pipeline's code, and logged in the verification ledger.
- A clean null on H2 is a result, not a failure. The project fails only if
  the pipeline is never validated and no interpretable comparison is
  produced.

## Consequences

**Positive.** Execution can begin against a verified substrate rather than an
unverified one. The most likely blocker is scoped in advance instead of
consuming an hour mid-sprint. The control structure — logit lens through the
same code path, direct prompting, pair-alternative comparison, relation
deletion, question truncation, label permutation, norm-matched random
direction, template robustness — is the strongest of any candidate
considered, which matters because failing to compare against baselines is
explicitly disqualifying.

**Negative.** J-Lens is the more crowded field: it was promoted with a bolded
"Key resource" link to open-source lenses, so many applications will use it.
The relational-binding framing with matched counterfactual pairs must carry
the differentiation, and the write-up has to make that framing obvious in the
first paragraph. Declaring passive-primary also forfeits, by default, the
causal evidence that would most strengthen a positive finding — if H2 comes
back positive, the result will be suggestive rather than causally
established. That is the price of not gambling an hour on B2.

**Residual risks carried forward.** B3 (no published shuffled-corpus control
lens; falls back to label permutation plus norm-matched random directions).
B4 (`len(tokenizer)=248077` against a 248320-wide unembedding — rank metrics
must state which width they rank over). Queue latency on L40S with 17/20
nodes draining; `a30_normal_q` is an unrestricted fallback.

## Alternatives considered

- **Keep C2.** Rejected on the two asymmetries above. It remains the
  strongest fallback if V1 or V3 fails outright — its checkpoints are
  verified public and it needs no lens.
- **Run both.** Rejected. Spreading thin across two projects is a named
  failure mode, and nine days does not support it.
- **Attempt the causal arm as a primary deliverable.** Rejected as decision 2
  above: it makes the headline result depend on a component that does not
  exist in the reference implementation.

## Related artifacts

- `docs/adr/0004-proposed-jlens-relational-binding-candidate.md`
- `llm/plan/project-candidates.md` (C6 scoring and the tie-break)
- `llm/plan/jlens-relational-binding-experiment-design.md`
- `llm/research/jlens-project-research-and-positioning.md`
- `results/design-verification/environment-manifest.md`
- `llm/construction/jlens-design-verification-sprint.md`
