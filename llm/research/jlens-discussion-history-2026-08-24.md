# Discussion History: Human-Readable Activation Vectors to Relational J-Lens Evaluation

Date: 2026-08-24
Purpose: Preserve the reasoning path, not merely the final proposal

## Starting intuition

Jason proposed teaching humans to read the vectors of numbers a neural network uses while making decisions—effectively watching the internal thought process by interpreting activation vectors. The knowledge-graph connection was that a readable internal representation might expose concepts and their relations at a micro level.

An important terminology correction followed: model neurons/parameters are normally created during training and fixed during inference; the changing objects to read are activations, residual-stream states, attention outputs, and related vectors. The practical goal became **latent-state literacy**: translating internal states into stable, human-readable descriptions without pretending that a single vector is a complete thought.

## First candidate: SAE feature frontiers

The first concrete direction used sparse autoencoders to identify interpretable features, examine how they changed across layers or tokens, and causally intervene on them. The concept was attractive because sparse features resemble nodes in a micro-level knowledge graph.

Jason then recalled that Neel Nanda might no longer be interested in SAEs and asked for the claim to be checked.

## SAE fact check and resulting correction

The current MATS document confirms the recollection in a narrower form:

- Neel lists SAE hill-climbing and basic science of SAEs among areas he is no longer interested in.
- He warns against using an SAE when prompting or a linear probe would suffice.
- He does not say SAEs have no value; they may remain useful as a supporting tool.

This made an SAE-centered application strategically weak. The discussion therefore moved toward the interpretability methods Neel explicitly names now: J-Lens, natural-language autoencoders, and activation oracles.

## Reformulated research gap

The J-Lens paper exposes vocabulary tokens associated with an activation. Its stated structural limitation is that a token list can be a bag of concepts without relational grammar or role binding.

That limitation aligned directly with Jason's knowledge-graph intuition. A graph is not just a collection of nodes; the typed edges and bindings carry the structure. The candidate question became:

> Can human-readable activation methods recover relational structure in hidden reasoning rather than merely producing a bag of concepts?

This was narrowed further into a testable MATS question:

> When paired prompts contain the same entities and concepts but swap their relational roles, can J-Lens identify the correct hidden intermediate—and does intervening on that representation causally change the answer?

## Experimental design decisions

The design uses counterfactually paired, synthetic two-hop prompts. Each pair contains the same concept inventory and answer candidates, with only the bindings changed. This prevents simple concept presence from masquerading as relational understanding.

Example structure:

- Variant A binds `Arin` to `Luma`, which maps to `zent`.
- Variant B binds `Arin` to `Nori`, which maps to `vark`.
- Both prompts contain Arin, Luma, Nori, zent, and vark.

The primary passive metric is pairwise binding accuracy: the correct intermediate must outrank the paired alternative in both variants, reversing appropriately when the facts reverse. The primary causal test swaps the intermediate representation toward the counterfactual and measures answer log-probability movement and flips.

Controls were added because attractive readouts are easy to overinterpret:

- vanilla logit lens;
- direct prompting for the intermediate;
- correct intermediate versus the equally relevant pair alternative;
- relation deletion;
- question truncation;
- label permutation or a shuffled-lens artifact if available;
- norm-matched random causal directions;
- fixed alternate prompt templates.

The design intentionally treats a validated null result as progress. If J-Lens shows both relevant entities but cannot identify which entity fills the queried role, that is evidence for the bag-of-concepts limitation rather than project failure.

## Anti-spin and time-budget decisions

Jason requested one-hour increments with a check every hour that the project was still making progress and did not need to pivot. A 16-hour core protocol was created with an artifact or metric required at every hour.

The no-spin rules are:

1. Every hour ends with a saved artifact, test, table, plot, or logged decision.
2. A single blocker gets no more than 20 minutes before using a predefined implementation fallback.
3. Fallbacks reduce model size, samples, layers, or method breadth; they do not change the relational-binding question.
4. Hypotheses and primary metrics freeze before held-out results are inspected.
5. Development prompts are used for debugging; held-out prompts are not tuned on.
6. A clean null after positive implementation checks is a substantive result.

The full schedule is stored in `llm/plan/jlens-relational-binding-experiment-design.md`.

## Topic classification

The candidate was mapped against Neel's current topic areas:

- **Primary:** improved interpretability methods / J-Lens evaluation.
- **Secondary:** model biology, because the test investigates internal relational representations.
- **Secondary motivation:** pragmatic interpretability and eventual monitoring.
- **Not currently model forensics:** there is no concerning action whose motive or cause is under investigation.

The recommended one-paragraph positioning is:

> This is primarily a red-team evaluation of J-Lens, with a model-biology question as the test case. We ask whether vocabulary-based activation readouts recover relational bindings during hidden two-hop reasoning, or merely surface an unstructured bag of relevant concepts.

## Relationship to the repository's accepted project

At the time this history was added, ADR-0002 selects a different candidate: measuring when CoT unfaithfulness emerges across the OLMo-3 post-training lineage. The J-Lens relational-binding design is therefore recorded as a competing candidate and possible future decision, not silently installed as the active project.

Accepting it would require:

1. A smoke test showing that a public J-Lens checkpoint works on an allowed current model.
2. A direct comparison against the accepted OLMo candidate using the repository's selection rubric.
3. An explicit ADR that supersedes ADR-0002 and records any clock consequence.

## Artifacts created from the discussion

- `llm/plan/jlens-relational-binding-experiment-design.md`
- `llm/research/jlens-project-research-and-positioning.md`
- `llm/research/jlens-discussion-history-2026-08-24.md`
- `docs/adr/0004-proposed-jlens-relational-binding-candidate.md`

