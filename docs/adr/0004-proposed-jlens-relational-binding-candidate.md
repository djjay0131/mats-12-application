# ADR-0004: Consider J-Lens Relational-Binding Evaluation

Status: Superseded by ADR-0005
Date: 2026-08-24 (resolved 2026-08-26)
Issue: #1

## Context

ADR-0002 currently accepts the OLMo-3 post-training/CoT-faithfulness candidate. A subsequent design discussion produced another strongly aligned candidate: evaluating whether J-Lens distinguishes relationally different hidden states that contain the same concepts.

The candidate directly addresses J-Lens's documented bag-of-concepts limitation and Neel Nanda's current interest in determining what J-Lens can do, comparing it with simpler lenses and prompting, and red-teaming misleading readouts. It also connects to Jason's knowledge-graph research through relational bindings rather than feature inventories.

However, a compatible public J-Lens checkpoint on a current allowed model has not yet been verified in this repository. Accepting the candidate now would silently displace an already de-risked project.

## Proposed decision

Record the J-Lens relational-binding experiment as a fully specified competing candidate, but do **not** supersede ADR-0002 at this time.

Before acceptance, require:

1. A smoke test of J-Lens and its logit-lens baseline on a current allowed model.
2. Confirmation that causal interventions can be run or an explicit passive-only scope.
3. A comparison against the accepted candidate using the selection rubric.
4. A clock ruling: whether any work counts and whether a genuine pivot resets the timer.

## Consequences

- The design and research history are preserved and available for review.
- The repository's active project remains the ADR-0002 candidate.
- No empirical J-Lens claim is considered verified.
- A later ADR must explicitly accept, reject, or supersede this proposal.

## Related artifacts

- `llm/plan/jlens-relational-binding-experiment-design.md`
- `llm/research/jlens-project-research-and-positioning.md`
- `llm/memory_bank/jlens-discussion-history-2026-08-24.md`


## Resolution (2026-08-26)

Accepted by [ADR-0005](0005-accept-jlens-relational-binding.md), which
supersedes ADR-0002. Status of the four conditions this ADR required:

| # | Condition | Outcome |
|---|---|---|
| 1 | Smoke test of J-Lens and its logit-lens baseline on a current allowed model | **Partial.** Compatibility and layout assertions pass; 32/32 reference tests green. The logit-lens switch was not exercised in setup — it closes in V1. |
| 2 | Confirm causal interventions can run, or declare explicit passive-only scope | **Decided.** ADR-0005 §2 declares passive-primary; the causal arm is contingent on V2. |
| 3 | Comparison against the accepted candidate using the selection rubric | **Done.** `llm/plan/project-candidates.md` — both score 24/25; tie broken on preparation and failure-mode asymmetry. |
| 4 | Clock ruling | **Decided.** ADR-0005 §3: nothing counted through 2026-08-26; V1/V2/V3 one hour each; no reset required. |
