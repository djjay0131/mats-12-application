# J-Lens Relational-Binding Candidate: Research and Positioning

Status: Research note; no empirical claims
Date: 2026-08-24

## Executive finding

The candidate is best classified as **improved interpretability methods / J-Lens evaluation**, using a **model-biology question** as its test case. It is not currently model forensics, though reliable relational readouts could later become an instrument for model forensics or monitoring.

## Why the project moved away from SAEs

The original idea was to help humans read the high-dimensional activation vectors used by a model during inference. Sparse autoencoders were initially considered because they can convert dense activations into a sparse set of human-labeled features.

Neel Nanda's current MATS document changes the strategic fit:

- It lists "SAE hill-climbing/basic science of SAEs" among areas he is no longer interested in.
- It warns that fancy methods such as SAEs can waste effort when prompting or a linear probe would answer the question.
- It still allows SAEs as tools when they are justified; this is not a claim that SAEs are scientifically useless.
- His current emphasis is pragmatic interpretability, model biology, model forensics, monitoring, J-Lens, natural-language autoencoders, and activation oracles.

A coauthored SAE progress update likewise deprioritizes fundamental SAE research while retaining SAEs as potentially useful instruments. Therefore the candidate was reformulated around evaluating J-Lens rather than developing or benchmarking SAEs.

## Why J-Lens is a direct fit

J-Lens maps residual-stream activations into a vocabulary-ranked readout using an average Jacobian. The official work explicitly identifies a structural limitation: a list containing the right concepts may still be only a "bag of concepts." Tokens such as `spider`, `legs`, and `eight` do not reveal which roles or relations bind those concepts together.

This supplies the project gap:

> Can a vocabulary-based activation readout recover the binding between entities and roles when the same entities appear in two counterfactually paired prompts?

Neel's current suggested J-Lens questions include what the method can do, how it compares with logit/tuned lenses, whether the single-token restriction is crippling, and how often the readout hallucinates or misleads. The proposed design tests all four in one controlled setting.

## Topic-area mapping

| Topic area | Fit | Rationale |
|---|---:|---|
| Improved interpretability methods / J-Lens | Primary | The project evaluates capability, failure modes, baselines, and causal validity of J-Lens. |
| Model biology | Secondary | The scientific object is how a model represents entity-role binding during two-hop reasoning. |
| Pragmatic/applied interpretability | Secondary | The experiment asks whether a readable internal signal adds value beyond prompting and a logit lens. |
| Model forensics | Not current | There is no concerning action whose cause must be distinguished among deception, confusion, shortcutting, or benign error. |
| Monitoring | Future application | A validated relational readout might monitor whom or what a model associates with an intention or action, but deployment monitoring is not tested here. |
| SAE research | No | SAEs are neither the object nor a required method. |

Recommended application description:

> This is primarily a red-team evaluation of J-Lens, with a model-biology question as the test case. We ask whether vocabulary-based activation readouts recover relational bindings during hidden two-hop reasoning, or merely surface an unstructured bag of relevant concepts.

## External evidence affecting the design

### Official J-Lens paper and repository

- J-Lens is intended to expose intermediate model concepts rather than merely predict the final output.
- Reported evaluation includes readout performance and causal swap performance.
- The paper explicitly describes the bag-of-concepts and single-token limitations.
- The reference implementation exposes a vanilla logit-lens baseline by disabling the Jacobian transformation.
- Pre-fitted public artifacts should be used; fitting a new lens is outside the time budget.

### Template lens

The J-Lens appendix describes phrase templates that can read and intervene on predefined multi-token concepts. This is relevant to relations, but it requires predefined vocabulary and additional computation and can prematurely reveal the answer. It is an optional extension, not part of the minimum viable experiment.

### Activation oracles and natural-language methods

These may express relations more naturally than token lists but introduce cost, vagueness, and confabulation risk. They should only be compared if a pre-existing inference pipeline loads quickly after the primary J-Lens result is complete.

### Preliminary independent replication

A recent independent repository reports null-heavy passive J-Lens results under shuffled controls and weak causal effects on one tested Qwen model, with stronger effects on a Gemma model. This is preliminary rather than authoritative, but it motivates shuffled-label or shuffled-lens controls, prompt truncation, and causal testing instead of trusting visually plausible readouts.

## Strategic limitations

- The repository already has an accepted OLMo-3/CoT-faithfulness candidate in ADR-0002. This note does not supersede it.
- Compatibility between a current Qwen3.5 model and a public pre-fitted J-Lens checkpoint must be smoke-tested before this candidate can be accepted.
- The project must claim only what occurs at a specified layer/position in a controlled task, not that it reads the model's complete thoughts.
- A null binding result is useful only after validating the implementation on an official positive example and running semantic controls.

## Sources

- Neel Nanda, current MATS research interests: https://docs.google.com/document/d/1p-ggQV3vVWIQuCccXEl1fD0thJOgXimlbBpGk6FI32I/edit
- Anthropic, J-Lens paper: https://transformer-circuits.pub/2026/workspace/index.html
- Official J-Lens implementation: https://github.com/anthropics/jacobian-lens
- Minimal Qwen3.5-4B implementation: https://github.com/idhantgulati/j-lens
- SAE progress update: https://www.alignmentforum.org/posts/4uXCAJNuPKtKBsi28/sae-progress-update-2-draft
- Bauer et al., Building Better Activation Oracles: https://arxiv.org/abs/2606.02609
- Preliminary independent replication: https://github.com/amaljithkuttamath/jlens-replication
- Model Forensics: https://arxiv.org/abs/2606.26071

