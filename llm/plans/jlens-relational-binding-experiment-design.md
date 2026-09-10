# Beyond a Bag of Concepts

## A 16-hour MATS experiment on relational information in J-Lens readouts

### One-sentence question

When two prompts contain the same entities and concepts but assign them different relational roles, can J-Lens identify the correct hidden intermediate—and does changing that representation causally change the model’s answer?

## Why this project

This targets an explicit limitation in the J-Lens work: vocabulary readouts can expose a “bag of concepts” without showing which entity fills which role. It is also tightly aligned with Neel Nanda’s current interests: testing J-Lens in realistic use cases, comparing it with simpler baselines, measuring hallucination or misleading readouts, and studying reasoning models pragmatically rather than doing basic SAE research.

The project keeps the knowledge-graph intuition, but makes it mechanistic and falsifiable. A knowledge graph is not just a set of nodes; it contains typed edges and bindings. The experiment asks whether a human-readable activation method recovers those bindings.

## Fixed scope

- **Model:** the smallest current Qwen3.5 model for which a public J-Lens checkpoint and intervention code work reliably. A minimal external implementation targets Qwen3.5-4B; this repository currently prefers Qwen3.5-9B. Verify checkpoint compatibility before locking the substrate.
- **Primary method:** public, pre-fitted J-Lens. Do not spend project time fitting a new lens.
- **Baselines:** vanilla logit lens, direct prompting, and permutation/deletion controls.
- **Dataset:** synthetic paired two-hop questions whose two variants use the same vocabulary but swap the intermediate binding.
- **Primary observation point:** the final prompt token immediately before answer generation.
- **Primary claim:** about relational binding at that observation point, not about reconstructing the model’s complete “thought process.”
- **Primary sample:** 10 development pairs and 40 held-out test pairs, spread across at least four relation templates.

If compute is limited, reduce the number of pairs or layers. Do not change the research question.

## Example paired item

Variant A:

> Arin lives in Luma. Bex lives in Nori. Luma uses zent. Nori uses vark. What is used where Arin lives? Answer:

Correct intermediate: `Luma`. Correct answer: `zent`.

Variant B:

> Arin lives in Nori. Bex lives in Luma. Luma uses zent. Nori uses vark. What is used where Arin lives? Answer:

Correct intermediate: `Nori`. Correct answer: `vark`.

The pair contains the same entities, relations, and answer candidates. Only the bindings differ. Surface-level concept detection therefore cannot solve the interpretability task.

Before inclusion, verify that every scored intermediate and answer is a single token under the chosen tokenizer. Prefer arbitrary but pronounceable tokens only if the model can solve the task behaviorally; otherwise use ordinary single-token nouns and names assigned arbitrary roles.

## Pre-registered hypotheses

- **H1 — concept recovery:** J-Lens will rank both relevant entities more highly than unrelated entities.
- **H2 — binding recovery:** J-Lens will rank the correctly bound intermediate above the pair’s alternative more often than the logit lens.
- **H3 — causal validity:** swapping the J-Lens coordinate associated with the intermediate toward the counterfactual intermediate will increase the counterfactual answer’s log probability more than a norm-matched random intervention.
- **H4 — likely limitation:** token lists may recover entities yet remain substantially worse at bindings than their apparent qualitative readability suggests.

A clean null result on H2 or H3 is informative. It would directly substantiate the “bag of concepts” limitation rather than count as project failure.

## Metrics

### Behavioral eligibility

Only score a test pair if the unmodified model answers both variants correctly under deterministic decoding. Report both the total generated set and the retained set. Target at least 80% pair eligibility. If eligibility is lower, simplify wording while preserving the same relational structure.

### Primary readout metric

For every prompt, compare the J-Lens score or rank of the correct intermediate with the alternative intermediate from its paired prompt.

**Pairwise binding success** requires both:

1. Correct intermediate ranks above the alternative in Variant A.
2. The ordering reverses correctly in Variant B.

Report pairwise binding accuracy with a paired bootstrap 95% confidence interval. Pre-register `Recall@10` as a secondary metric. Use the same predeclared layer band for all methods; if the public checkpoint does not specify a workspace band, use the middle 40%–80% of layers. For rank-based aggregation, use the best rank within that band for both J-Lens and logit lens.

### Causal metric

For each eligible pair, intervene from the factual intermediate toward the counterfactual intermediate at the layer selected without looking at test outcomes. Measure:

- change in log probability of the counterfactual answer;
- change in the factual-minus-counterfactual answer margin;
- answer flip rate.

Compare against a norm-matched random vocabulary direction and the reverse intervention. Report paired bootstrap confidence intervals rather than relying only on example traces.

## Controls

1. **Logit lens:** run through the same code path by disabling the Jacobian transformation.
2. **Direct-prompting baseline:** ask the model explicitly for the intermediate. This tests whether the task itself is legible without an internal method.
3. **Pair alternative:** compare the correct intermediate only with the equally relevant alternative from the matched prompt, not with arbitrary tokens.
4. **Relation deletion:** remove the fact that determines the queried binding. A valid readout advantage should collapse.
5. **Question truncation:** inspect before the question identifies the target entity. Binding selectivity should weaken or disappear.
6. **Label permutation:** permute the mapping between readout rows and vocabulary labels. This detects attractive-looking token lists that do not depend on the learned mapping.
7. **Random causal direction:** match intervention norm and layer while replacing the target direction.
8. **Prompt-template robustness:** repeat a subset with alternate wording fixed before viewing the test results.

If a published shuffled-corpus J-Lens checkpoint is readily available, add it as a stronger negative control. Do not spend more than one hour building one.

## Anti-spin rules

Every hour ends with a saved artifact: a note, dataset, passing test, result table, plot, or report section. “Read more,” “debugged,” and “thought about it” do not count.

- Limit any single blocker to 20 minutes before taking the listed fallback.
- Preserve the question and hypotheses; simplify model size, sample size, or method breadth instead.
- Freeze hypotheses and primary metrics before examining held-out results.
- Do not add a new interpretability method before the primary J-Lens and logit-lens results exist.
- Use development pairs for debugging and layer selection. Never tune on the 40 held-out pairs.
- End the project with a calibrated claim even if the answer is null.

## Research-process stage map

This plan follows Neel Nanda's Ideation → Exploration → Understanding → Distillation process. The operative coaching and transition rules are in `llm/construction/neel-research-process-learning-overlay.md`.

- **Hour 1 — Ideation exit:** verify the open gap, importance, literature fit, and tractability.
- **Hours 2–6 — Exploration:** hypotheses remain provisional while we gain surface area, visualize outputs, and collect anomalies. Hour 2 creates a hypothesis-and-prediction memo, not a final preregistration.
- **Hour 7 — Explore → Understand gate:** use development controls to complete rival hypotheses and their distinguishing predictions, then freeze the analysis and claim boundaries.
- **Hours 8–14 — Understanding:** seek evidence for and against the frozen hypotheses with held-out tests, strong baselines, bug checks, and alternative explanations.
- **Hours 15–16 — Distillation:** compress the evidence into scoped claims, red-team them, and communicate limitations.

Every counted hour uses a 5-minute prediction, a bounded execution loop, Jason's first interpretation, then agent/mentor feedback. Use `llm/construction/research-learning-log-template.md`. A GO from design verification means the candidate is ready to enter Understanding; it does not mean the scientific claim has been verified.

## Hour-by-hour plan

| Hour | Work | Required output and progress gate | Same-question fallback if blocked |
|---:|---|---|---|
| 1 | Read the current MATS research-interests document, J-Lens paper sections on limitations/evaluation, and official repository README. | A one-page source memo containing the exact research gap, available checkpoint/model, and three evaluation precedents. **Pass:** each design choice has a source or explicit rationale. | Stop browsing after 60 minutes; unresolved details become assumptions in a risk log. |
| 2 | Draft the question, provisional hypotheses (including alternatives), claim boundaries, likely primary metric, and predictions. | A timestamped hypothesis-and-prediction memo. **Pass:** it names at least two rival explanations and what would distinguish them; a null would still teach us something. Do not freeze yet. | Narrow the observation point while retaining rival hypotheses; unresolved choices stay in the exploration risk log. |
| 3 | Design four or five relational templates and all controls. Manually write 10 development pairs. | Dataset specification plus 10 paired examples. **Pass:** each pair uses the same concept inventory and differs only in bindings. | Use two templates initially, retaining the four-template test specification. |
| 4 | Install/run the official or minimal public J-Lens implementation with a pre-fitted current-Qwen checkpoint. Reproduce one repository example and verify the logit-lens switch. | Saved smoke-test output with model, commit, checkpoint, layer, position, and top tokens. **Pass:** J-Lens and logit-lens outputs differ and are reproducible. | Use the smaller compatible public implementation/checkpoint; do not fit a lens. If still blocked, run in the repository’s supported notebook environment. |
| 5 | Generate 50 candidate pairs with a fixed seed, tokenize all target words, and measure unmodified model accuracy. | `dataset_dev` with 10 pairs, untouched `dataset_test` with 40 eligible pairs if possible, and an eligibility table. **Pass:** at least 80% behavioral pair accuracy or a documented wording revision. | Simplify syntax, reduce distractors, or retain fewer eligible pairs; preserve two-hop binding. |
| 6 | Instrument activation capture/readout at the final prompt token over the fixed layer band. Run all 10 development pairs through J-Lens and logit lens. | Tidy table with prompt ID, variant, layer, correct/alternative scores and ranks. **Pass:** manual inspection confirms token/position alignment on three examples. | Run fewer layers or prompts and cache activations; do not change the metric. |
| 7 | Validate the pipeline using development controls: relation deletion, question truncation, and label permutation. Complete the rival-hypothesis table and cross the Explore → Understand gate before freezing. | Control table, Jason's prediction review, completed hypothesis table, and signed preregistration/analysis freeze. **Pass:** the experiment distinguishes plausible hypotheses, the official smoke test still works, and every held-out interpretation has a prewritten claim boundary. | Fix extraction bugs only. If the hypotheses remain ill-posed, return to bounded Exploration rather than freezing a weak test; if controls remain null but the official example passes, retain that as a genuine method-failure hypothesis. |
| 8 | Run the frozen passive-readout pipeline on all held-out eligible pairs. Do not inspect individual examples during the run. | Complete cached test table plus run manifest. **Pass:** no missing prompt-layer-method cells and deterministic rerun agrees on a sample. | Reduce to a balanced minimum of 20 test pairs and report the lower precision. |
| 9 | Compute primary J-Lens versus logit-lens results and confidence intervals. | One primary result table and two plots: binding accuracy by method; layerwise correct-minus-alternative margin. **Pass:** every plotted point can be traced to the frozen table. | Use bootstrap intervals and descriptive statistics; do not spend time on elaborate significance tests. |
| 10 | Run passive falsification controls across the held-out set. | Plot/table for deletion, truncation, and label permutation. **Pass:** conclusions explicitly distinguish entity presence from correct binding. | Run controls on a fixed 20-pair subset if compute is tight. |
| 11 | Reproduce one known causal intervention from the public code, then implement the factual-to-counterfactual intermediate swap on five development pairs. | Causal smoke-test table with answer log-probabilities before/after. **Pass:** intervention lands at the intended layer/position and norm is recorded. | If the public intervention API cannot be made reliable within the hour, freeze causal work as unavailable and reallocate Hours 12–13 to stronger passive controls and robustness. This is a scope reduction, not a topic pivot. |
| 12 | Run causal swaps, reverse swaps, and norm-matched random controls on the held-out set. | Complete intervention table. **Pass:** equal sample counts and intervention norms across target and random conditions. | Use a preregistered 20-pair subset or one fixed layer. |
| 13 | Analyze causal effects and connect them to passive readout quality. | Causal result plot plus correlation/scatter between binding margin and intervention effect. **Pass:** aggregate effects are reported alongside flip rate and two randomly selected traces. | If causal work was unavailable, test an additional prompt template and a shuffled-label/readout control instead. |
| 14 | Perform robustness and error analysis without changing the primary result. Stratify by relation template and inspect a fixed random sample of successes/failures. | Robustness table and an error taxonomy with counts. **Pass:** examples were selected by seed, not narrative appeal. | Limit to template stratification and five seeded errors. |
| 15 | Draft methods and results first, including negative findings and limitations. | Near-complete report with methods, results, figures, controls, and reproducibility details. **Pass:** every empirical sentence points to a table, plot, or log. | Remove optional prose; preserve the evidence chain. |
| 16 | Write the introduction, discussion, and MATS-facing conclusion. Audit every claim against the preregistration. | Submission-ready report, code/data manifest, and a five-sentence executive summary. **Pass:** a skeptical reader can state what was tested, what happened, and what remains unknown. | Cut breadth, not rigor: one question, one primary table, one causal/control table, two representative traces. |

## Optional extension hours 17–20

Only use these if the 16-hour deliverable is already complete. They are not rescue time.

| Hour | Extension | Continue only if… |
|---:|---|---|
| 17 | Add multi-token intermediates and test the published template-lens approach. | Compatible code/checkpoint loads within 20 minutes. |
| 18 | Compare free-text activation-oracle or natural-language-autoencoder descriptions on a 10-pair subset. | A pre-existing inference pipeline is available; no model training is required. |
| 19 | Add a second current model or a stronger shuffled-lens control. | It can run with the frozen dataset and metrics unchanged. |
| 20 | Replication and packaging: rerun from a clean environment and improve the public notebook. | Core conclusions are already frozen. |

## Two additional write-up hours

If the application rules permit two hours specifically for the executive summary/application response:

- **Write-up hour A:** compress the project into problem, method, result, surprise, and next experiment; insert exact numbers only.
- **Write-up hour B:** adversarial edit. Remove inflated claims such as “read the model’s thoughts,” verify links and reproducibility, and ensure the answer explains why Neel should update from the result.

## Stop conditions that still count as success

Stop adding experiments when any one of these is true:

- The primary held-out comparison, its controls, and a calibrated conclusion are complete.
- The evidence shows J-Lens retrieves entities but not bindings, and the controls rule out a broken pipeline.
- The evidence shows binding accuracy above the logit lens and causal swaps outperform random controls.
- Compute prevents further scale, but at least 20 balanced test pairs and all essential controls are complete.

The project fails only if the pipeline is never validated and no interpretable comparison is produced—not if the hypothesis is false.

## Expected submission shape

1. A paired-prompt diagram showing identical concepts and swapped bindings.
2. One table comparing behavioral prompting, logit lens, and J-Lens.
3. One plot of pairwise binding accuracy with uncertainty.
4. One causal/control plot, or a stronger passive-control plot if interventions were unavailable.
5. Two seeded examples: one success and one failure.
6. A conclusion phrased as: “At the final prompt position in this controlled two-hop setting, J-Lens [did/did not] recover relational binding beyond simpler baselines.”

## Sources

- Neel Nanda, current MATS research interests and application advice: https://docs.google.com/document/d/1p-ggQV3vVWIQuCccXEl1fD0thJOgXimlbBpGk6FI32I/edit
- Anthropic, *J-Lens: A Jacobian-based vocabulary lens*: https://transformer-circuits.pub/2026/workspace/index.html
- Official J-Lens reference implementation: https://github.com/anthropics/jacobian-lens
- Minimal Qwen3.5-4B implementation: https://github.com/idhantgulati/j-lens
- Google DeepMind/Neel Nanda et al., SAE progress update: https://www.alignmentforum.org/posts/4uXCAJNuPKtKBsi28/sae-progress-update-2-draft
- Bauer et al., *Building Better Activation Oracles*: https://arxiv.org/abs/2606.02609
- Recent independent J-Lens replication motivating shuffled controls (treat as preliminary, not authoritative): https://github.com/amaljithkuttamath/jlens-replication
- Neel Nanda, research process: https://www.alignmentforum.org/posts/hjMy4ZxS5ogA9cTYK/how-i-think-about-my-research-process-explore-understand
