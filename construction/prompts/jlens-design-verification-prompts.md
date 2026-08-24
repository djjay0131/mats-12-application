# Copy-Ready Prompts: J-Lens Design Verification

These prompts are for Claude Code or another repository-aware coding agent. Run them sequentially. Do not run later prompts when an earlier gate returns FAIL.

## Prompt 0 — Orchestrate the verification sprint

```text
You are the Design Verification Lead for djjay0131/mats-12-application.

Mission: execute the bounded J-Lens design-verification sprint defined in construction/jlens-design-verification-sprint.md. This is not the main experiment. Your job is to determine GO, REVISE, or NO-GO without expanding scope or manufacturing a positive result.

Read, in order:
1. CLAUDE.md
2. docs/plan/PLAN.md
3. llm/memory_bank/activeContext.md
4. docs/adr/0002-project-selection.md
5. docs/adr/0004-proposed-jlens-relational-binding-candidate.md
6. docs/plan/jlens-relational-binding-experiment-design.md
7. docs/research/jlens-project-research-and-positioning.md
8. construction/jlens-design-verification-sprint.md

Governance:
- Create or use a research issue and a dedicated branch. Declare governance level L1.
- Do not change ADR-0002 or mark ADR-0004 Accepted.
- Before counted work begins, explicitly tell Jason to start the timer. Treat V1, V2, and V3 as one counted hour each. Installation/download/waiting is not counted.
- Update llm/memory_bank/time-log.md only with time Jason confirms.
- Never call agent output human-verified. Mark produced measurements agent-unverified until Jason independently checks them.
- Every metric needs a baseline/control. Save raw outputs before summaries.

Execution:
1. Run only the bounded setup window.
2. Execute V1. Stop on FAIL and write the decision record.
3. Execute V2 only after V1 PASS. Stop on FAIL.
4. Execute V3 only after V2 PASS.
5. Produce docs/plan/jlens-design-verification-decision.md with GO, REVISE, or NO-GO and evidence paths.

At every hour boundary, answer:
- What artifact now exists?
- What uncertainty was retired?
- What remains load-bearing?
- Did the gate pass?

Do not begin the 16-hour main experiment. Open a PR containing only verification artifacts, code, raw outputs, tests, and the decision record.
```

## Prompt 1 — V1 tooling and positive control

```text
Act as the J-Lens Tooling Verifier for djjay0131/mats-12-application.

Execute only Setup and V1 from construction/jlens-design-verification-sprint.md. Do not perform V2 or V3.

Primary objective: determine whether the official anthropics/jacobian-lens implementation can produce a reproducible readout on an official positive-control example using a current allowed model and exactly matching lens.

Requirements:
- Pin and record all repository commits, packages, model IDs, tokenizer IDs, lens file IDs, dtype, device, seed, positions, and layers.
- Prefer a pre-fitted lens. Do not start an open-ended full lens fit.
- If fitting is unavoidable, run only a bounded cost-estimation pilot and stop.
- Run the vanilla logit-lens baseline through the same extraction path.
- Manually print tokenized prompt indices and identify the inspected position.
- Rerun once for determinism.
- Record peak memory and wall time.
- Identify a feasible shuffled-corpus, published shuffled-lens, or permutation control.
- Save raw JSON/JSONL before writing conclusions.
- Mark all produced numbers agent-unverified.

PASS or FAIL must follow the exact gate in construction/jlens-design-verification-sprint.md. Do not soften a failed requirement into “promising.”

Outputs:
- results/design-verification/environment-manifest.md
- results/design-verification/v1-tooling-verification.md
- results/design-verification/raw/v1-*.json
- minimal reproducible script and test under experiments/design-verification/ or scripts/

End by stating PASS or FAIL and stop.
```

## Prompt 2 — V2 J-space decomposition

```text
Act as the Representation Decomposition Verifier for djjay0131/mats-12-application.

Precondition: results/design-verification/v1-tooling-verification.md must say PASS. If it does not, stop without making changes.

Execute only V2 from construction/jlens-design-verification-sprint.md.

Objective: establish whether the project can defensibly compare the full residual stream, the paper-style sparse non-negative J-space component, and the non-J-space residual.

Implementation requirements:
- Reuse the exact model/lens pair and verified layer/position from V1.
- Follow the official paper/repository sparse reconstruction method where available.
- Define h_full, h_J, and h_nonJ = h_full - h_J.
- Unit-test reconstruction identity within a stated numeric tolerance.
- Record sparsity k, normalization, reconstruction loss, ranks/norms, and non-orthogonality caveats.
- Implement a matched random-direction or shuffled/label-permuted control with equal dimensionality and norm treatment.
- Run one official positive-control intervention and compare targeted behavioral/log-probability change against the matched control.
- Check general coherence or a non-target prediction so broad damage is not mistaken for causal specificity.
- Save raw arrays or reproducible summaries sufficient for Jason to independently re-derive the headline checks.
- Mark measurements agent-unverified.

Do not train a relational probe and do not inspect main-experiment outcomes.

Outputs:
- results/design-verification/v2-decomposition-verification.md
- results/design-verification/raw/v2-*.json or safe tensor artifacts
- decomposition implementation and unit tests

Apply the exact PASS/FAIL gate. End with PASS or FAIL and stop.
```

## Prompt 3 — V3 binding-identifiability audit

```text
Act as the Experimental Identifiability Reviewer for djjay0131/mats-12-application.

Preconditions: V1 and V2 verification reports must both say PASS. Otherwise write a NO-GO decision record and stop.

Execute only V3 from construction/jlens-design-verification-sprint.md.

Central adversarial question: does the proposed experiment measure relational-binding information, or merely expose an intermediate concept after the model has already selected it?

Tasks:
1. Create only 8–12 paired development items across at least two templates.
2. Verify identical entity/answer inventories and counterfactual reversal.
3. Audit tokenizer, frequency, position, word-order, answer-order, and template shortcuts.
4. Compare post-selection, pre-query graph-state, and role-conditioned observation designs.
5. For each design, state the exact claim it licenses and the confounds that remain.
6. Specify template-held-out evaluation; never use a random row split.
7. Use a regularized linear probe first. Use a more complex probe only with a written necessity argument.
8. Compare full, J, non-J, matched-control, and lexical bag-of-entities inputs.
9. Run only a development sanity check. Do not characterize it as the research result.
10. Select GO, REVISE, or NO-GO using the exact sprint gates.

Required outputs:
- experiments/design-verification/dev-binding-pairs.jsonl
- results/design-verification/v3-binding-identifiability.md
- docs/plan/jlens-design-verification-decision.md

The decision record must include:
- verdict;
- evidence paths;
- strongest defensible one-sentence research question;
- strongest claim the design cannot support;
- estimated remaining counted hours;
- whether ADR-0004 should remain Proposed, be rejected, or be considered for acceptance by Jason.

Do not edit ADR status yourself. Mark all measurements agent-unverified. Stop after writing the decision.
```

## Prompt 4 — Human verification handoff

```text
Act as a verification clerk, not a research agent.

Using the artifacts in results/design-verification/, prepare a short step-by-step checklist for Jason to independently verify:
- exact model/lens/tokenizer match;
- inspected token position;
- positive-control top-k readout;
- J-space reconstruction identity;
- random/shuffled control comparison;
- four paired development prompts;
- the wording of the final allowed claim;
- recorded counted time.

Do not recompute the same numbers with the same code and call that independent verification. Where an independent path is unavailable, label the item UNVERIFIED and say what Jason must do manually.

Update docs/application/verification-ledger.md only with checks Jason explicitly confirms. Otherwise create results/design-verification/human-verification-pending.md.
```

