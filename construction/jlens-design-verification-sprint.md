# J-Lens Design-Verification Sprint

Status: Ready to execute; candidate remains Proposed
Owner: Jason
Decision governed by: ADR-0004
Related issue/PR: #1 / #2

## Purpose

Determine whether the sharpened J-Lens project is sufficiently executable and scientifically identifiable to supersede the current project-selection decision.

This sprint must answer three questions:

1. Can a J-Lens be applied reliably to a current, allowed open-weight model within the project constraints?
2. Can the residual stream be separated into defensible J-space and non-J-space components with sanity checks?
3. Can the experiment distinguish relational-binding information from merely reading the already-selected intermediate concept?

This is a **verification sprint**, not the main experiment. Do not scale the dataset, tune for positive results, or draft application claims.

## Research-process interpretation

Use `construction/neel-research-process-learning-overlay.md` as an operative companion to this document. In Neel Nanda's framework, this is an **Explore → Understand transition sprint**, not verification of the scientific hypothesis:

- V1 explores the tool, positive control, and practical failure modes.
- V2 explores the operational meaning of J-space and rival explanations for apparent effects.
- V3 determines whether we now have explicit competing hypotheses and a tractable experiment that distinguishes them.
- GO means the project is ready to enter Understanding. It does not mean relational binding has been found in J-space.

For each counted hour, use `llm/memory_bank/research-learning-log-template.md`: Jason records the stage, prediction, strongest alternative, and expected agent/mentor advice before execution; Jason interprets the result before the agent gives feedback. Reserve the last five minutes for CONTINUE, CHANGE LOOP, RETURN TO EXPLORE, or PIVOT CANDIDATE. Only the last option changes the candidate, and it requires a failed load-bearing assumption with no bounded same-question fallback.

## Time accounting

Conservative interpretation of Neel's rules:

- Environment installation, model/lens download, queue time, and passive waiting are setup and do not count.
- Project-specific design, smoke-test analysis, coding, and decisions count toward the 20-hour research budget.
- Start the timer before V1. Record each segment in `llm/memory_bank/time-log.md`.
- Stop after three counted hours even if a gate remains unresolved. An unresolved gate is a NO-GO for selecting this candidate now.

## Non-negotiable boundaries

- Do not fit a production-quality lens merely to rescue the candidate.
- Do not use GPT-2, Pythia, Gemma 2, Qwen2.5, or Llama 3 as the primary substrate.
- Do not report agent-produced numbers as human-verified.
- Do not change ADR-0002 or accept ADR-0004 during the sprint.
- Development examples may be inspected. No held-out test set exists yet and none should be presented as a final result.
- Every gate produces a saved artifact even when it fails.

## Setup window — elapsed time only, maximum 60 minutes

### Work

- Confirm available GPU, storage, CUDA/PyTorch/Transformers versions, and Hugging Face access.
- Clone/install the official `anthropics/jacobian-lens` reference implementation.
- Locate a compatible pre-fitted lens on a current allowed model. Candidate priority:
  1. Qwen3.5 model with a matching published lens;
  2. another current model explicitly permitted by the application document;
  3. a small development-only model solely to validate the pipeline, never as the planned primary substrate.
- Record exact repository commits and model/lens identifiers.

### Stop rule

If dependency installation or model acquisition remains blocked after 60 elapsed minutes, record the blocker. Do not begin counted V1 until the environment is usable.

### Output

`results/design-verification/environment-manifest.md`

## V1 — Hour 1: Tooling and positive-control verification

### Question

Can this implementation produce a reproducible J-Lens readout on an official known-positive example, with a logit-lens baseline and feasible resource use?

### Required tests

1. Reproduce one official repository example or released evaluation item where an unspoken intermediate concept should appear.
2. Record top-10 J-Lens and logit-lens tokens at the exact position and layers used.
3. Rerun the same example and confirm deterministic agreement under the fixed seed/configuration.
4. Verify activation position and tokenizer alignment manually.
5. Record peak GPU memory and wall-clock time for apply; if fitting is required, estimate the 100-prompt fitting cost from a bounded pilot rather than completing a large fit.
6. Determine whether a shuffled-corpus lens, published control lens, or defensible label/permutation control can be run during the main experiment.

### PASS

All are true:

- A current allowed primary model and exactly matching lens are identified, or a bounded fit is demonstrably feasible.
- The official positive concept appears in the preregistered top-k/layer region and depends on the relevant prompt content.
- J-Lens and logit-lens paths both run.
- A negative-control path is available.
- Runtime and memory leave room for at least 20 paired examples plus controls.

### FAIL

Any is true:

- Only an old or prohibited primary model works.
- The lens/model/tokenizer pairing is uncertain.
- The positive control cannot be reproduced.
- A usable lens requires an open-ended fitting/debugging project.
- No meaningful negative control can be implemented.

### Output

`results/design-verification/v1-tooling-verification.md` plus raw machine-readable output.

## V2 — Hour 2: Representation-decomposition verification

### Question

Can we operationalize “J-space versus non-J-space” without smuggling the desired conclusion into the decomposition?

### Required tests

1. Implement or reuse the paper's sparse non-negative J-space reconstruction at one verified workspace layer and position.
2. Define:
   - `h_full`: original residual activation;
   - `h_J`: reconstructed J-space component;
   - `h_nonJ = h_full - h_J`.
3. Verify numerically that `h_full ≈ h_J + h_nonJ` within a recorded tolerance.
4. Record reconstruction error, sparsity `k`, normalization, and whether directions are non-orthogonal.
5. Compare against at least one matched control decomposition:
   - random directions with equal `k` and matched norms; or
   - label-permuted/shuffled J-Lens directions.
6. Run a positive-control intervention from the official multihop/sanity example. J-space removal should have a more targeted effect than the matched control; general output coherence must also be checked.
7. Write down exactly what the decomposition licenses us to claim—and what it does not.

### PASS

All are true:

- The decomposition is numerically correct and reproducible.
- The reconstruction procedure matches a documented paper/repository method or deviations are explicit.
- The positive control distinguishes J-space manipulation from the matched control without destroying general coherence.
- Full, J, and non-J representations can be exported consistently for downstream probes.

### FAIL

Any is true:

- “J-space” is implemented as an arbitrary top-token projection with no correspondence to the paper's sparse construction.
- Reconstruction is unstable across reruns or normalization choices.
- The matched random/control decomposition performs similarly on the positive control and the difference cannot be explained.
- Manipulation broadly damages the model, making causal interpretation impossible.

### Output

`results/design-verification/v2-decomposition-verification.md`, decomposition unit tests, and raw outputs.

## V3 — Hour 3: Binding-identifiability and decision review

### Question

Does the proposed dataset and metric test relational binding, or only whether the model has already selected the correct intermediate?

### Required design audit

Construct only 8–12 development pairs across at least two templates. For each pair verify:

- same entity and answer inventory;
- counterfactual reversal of bindings;
- exact tokenizer properties recorded;
- both variants solved behaviorally;
- no target can be inferred from entity frequency, absolute position, answer order, or lexical identity;
- template split prevents a probe from succeeding through fixed word order.

Compare three possible observation designs:

1. **Post-selection:** final prompt position after a query selects the subject/relation. This tests whether the selected intermediate is readable, not full graph structure.
2. **Pre-query graph state:** activation after facts but before the query. This tests whether stored bindings can be decoded, but may require pooling across positions.
3. **Role-conditioned state:** append a neutral subject/relation cue, then read before answer generation. This tests the result of retrieving a binding and must be labeled accordingly.

For each design, specify:

- activation positions used;
- whether a probe sees a single vector or multiple token positions;
- target label;
- full/J/non-J inputs;
- simplest baseline;
- shortcut controls;
- exact claim permitted by success or failure.

Prefer the smallest design that can separate these two claims:

- **Weak claim:** J-Lens exposes the intermediate selected by relational reasoning.
- **Strong claim:** relational-binding information itself is present in or absent from J-space.

### Probe feasibility check

Run only a development sanity check, not a result:

- use a simple regularized linear probe first;
- add a bilinear or relation-conditioned probe only if the linear formulation cannot express the registered target;
- compare `h_full`, `h_J`, `h_nonJ`, and matched random/control components;
- split by template, not random prompt rows;
- include a bag-of-entities lexical baseline.

### PASS

All are true:

- At least one observation design genuinely distinguishes binding information from selected-intermediate visibility.
- A template-held-out evaluation and shortcut controls are specified.
- The behavioral model solves at least 80% of both variants in the development pairs.
- The probe target and allowed claim can be stated in one sentence each.
- V1 and V2 passed.

### REVISE

- V1 and V2 pass, but only the weak post-selection claim is identifiable.
- A smaller, accurately named project is still possible, but it must not be sold as reading graph structure.

### FAIL

- No observation design separates relation binding from surface order or selected-intermediate visibility.
- Required probe complexity overwhelms the 20-hour project.
- Either V1 or V2 failed.

### Outputs

- `results/design-verification/v3-binding-identifiability.md`
- `experiments/design-verification/dev-binding-pairs.jsonl`
- `docs/plan/jlens-design-verification-decision.md`

## Final decision record

At the end of V3, record exactly one verdict:

### GO

Accept only if all three gates pass. Recommend a later ADR superseding ADR-0002, then revise the 16-hour experiment plan around full/J/non-J comparison before beginning the main run.

### REVISE

Tooling is viable, but the strong binding claim is not. Preserve J-Lens as a narrower selected-intermediate/readout reliability project and compare it again against C1 before selection.

### NO-GO

Any load-bearing gate failed or remained unresolved after its hour. Keep ADR-0004 Proposed or reject it and select C1 (eval-awareness contamination) as the preferred backup.

## Human verification checklist

Jason must personally verify before accepting GO:

- [ ] Model and lens identifiers match exactly.
- [ ] One positive-control readout was manually inspected.
- [ ] One activation position/token index was manually traced.
- [ ] The decomposition identity and reconstruction error were independently checked.
- [ ] At least four paired prompts were read in both variants.
- [ ] The final claim is not stronger than the observation design.
- [ ] Counted time is recorded.
