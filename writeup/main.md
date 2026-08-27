# Randomly selected raw examples

<!-- Neel asks for these "ideally just after the executive summary", and names
     cherry-picking as a major red flag. Selection must be by seed, and the
     seed must appear in the text (BLK-10 checks for it).

     Include: 2 successes, 2 failures, and 1 case the pipeline scored as
     ambiguous. Show the full prompt, the top-k J-Lens readout, the logit-lens
     readout, and the model's answer. Raw. Do not clean them up. -->

Examples below are drawn with `seed=1337` from the held-out set; they are
randomly selected, not chosen.

---

# 1. Motivation and research question

<!-- Why this matters, in the terms a mech interp reader already holds. The
     safety framing is real but should not be inflated: a readable internal
     signal that cannot distinguish *who did what to whom* is a weaker
     monitoring instrument than its qualitative readability suggests. -->

**Question.** When two prompts contain the same entities and concepts but
assign them different relational roles, does J-Lens identify the correct
hidden intermediate — and does changing that representation causally change
the model's answer?

## 1.1 What J-Lens is, briefly

<!-- Three or four sentences, for a reader who knows logit lens but may not
     have read the workspace paper. Define terms at first use (SCR-04). -->

## 1.2 The gap

<!-- The bag-of-concepts limitation, quoted from the source rather than
     paraphrased. Then: nobody has quantified it against a matched
     alternative. That is the hole this fills. -->

---

# 2. Method

## 2.1 Dataset construction

<!-- The paired design is the heart of the method — explain it before anything
     else. Same entities, same relations, same answer candidates; only the
     bindings differ. Surface-level concept detection therefore cannot solve
     the task. Include the worked example. -->

| | Prompt | Correct intermediate | Correct answer |
|---|---|---|---|
| Variant A | Arin lives in Luma. Bex lives in Nori. Luma uses zent. Nori uses vark. What is used where Arin lives? | `Luma` | `zent` |
| Variant B | Arin lives in Nori. Bex lives in Luma. Luma uses zent. Nori uses vark. What is used where Arin lives? | `Nori` | `vark` |

<!-- State: number of templates, how pairs were generated, the seed,
     single-token verification under the tokenizer, and the eligibility rule. -->

## 2.2 Model, lens, and environment

<!-- Pin everything. This is where a skeptical reader checks whether you knew
     what you were running. Pull the identifiers from
     results/design-verification/environment-manifest.md — do not retype them
     from memory. -->

| | |
|---|---|
| Model | `Qwen/Qwen3.5-4B` — 32 layers, d_model 2560, vocab 248320 |
| Lens | `neuronpedia/jacobian-lens`, revision `qwen-n1000`, commit `16a01f3` |
| Lens provenance | fit by Neuronpedia against this exact model on `Salesforce/wikitext` |
| Hardware | Virginia Tech ARC, NVIDIA L40S (47.7 GB); peak allocation 8.51 GB |
| Precision | bfloat16 |

## 2.3 Observation point and layer band

<!-- Final prompt token before answer generation. State the layer band and
     that it was fixed before looking at held-out results. If the checkpoint
     does not declare a workspace band, say you used the middle 40-80%. -->

## 2.4 Metrics

<!-- Pairwise binding success requires BOTH orderings to be correct — say why
     that is a stricter and more honest test than per-prompt accuracy.
     Secondary: Recall@10. Report bootstrap 95% CIs.

     B4 applies here: len(tokenizer)=248077 against a 248320-wide unembedding.
     State which width you rank over. -->

## 2.5 Baselines and controls

<!-- Eight of them. Neel lists "failing to compare to baselines" among the
     disqualifying mistakes, so this section earns its length. One line each:
     what it is, and what it would show if the result were spurious. Mirror
     llm/application/controls-ledger.md — that ledger is the source of truth. -->

| # | Control | What it rules out |
|---|---|---|
| 1 | Logit lens (same code path, Jacobian disabled) | The advantage is the lens, not the pipeline |
| 2 | Direct prompting | The task is not already legible without an internal method |
| 3 | Pair alternative, not arbitrary tokens | Scoring against an equally relevant distractor |
| 4 | Relation deletion | The readout tracks the binding, not mere co-occurrence |
| 5 | Question truncation | Selectivity depends on knowing the target entity |
| 6 | Label permutation | Attractive token lists that do not depend on the learned mapping |
| 7 | Norm-matched random direction | Causal effects that any perturbation would produce |
| 8 | Prompt-template robustness | A result specific to one phrasing |

---

# 3. Preregistration and what was frozen when

<!-- Hypotheses H1-H4, the primary metric, and the layer band, with the
     timestamp at which each froze. Then state plainly that the 40 held-out
     pairs were never tuned on. This section is cheap to write and it is the
     one that makes a skeptical reader relax. -->

---

# 4. Results

## 4.1 Behavioral eligibility

<!-- How many pairs the model actually solved. Report the total generated set
     AND the retained set — not just the retained one. If eligibility came in
     under 80%, say what you changed and why. -->

## 4.2 Primary result: binding recovery

![Pairwise binding accuracy by method, with bootstrap 95% CIs. Chance is 50%.](results/figures/binding-accuracy-by-method.png)

## 4.3 Layerwise structure

![Correct-minus-alternative margin across the layer band, J-Lens vs logit lens.](results/figures/layerwise-margin.png)

## 4.4 Controls

![Binding advantage collapses under relation deletion and label permutation.](results/figures/controls-panel.png)

## 4.5 Causal arm

<!-- ADR-0005 scopes this project passive-primary. If V2 did not clear blocker
     B2 — the reference implementation ships no sparse non-negative J-space
     reconstruction — then say so here, plainly, and say what ran instead.

     Do NOT present a passive-only result as though causal work was never
     intended. Do NOT substitute an arbitrary top-token projection and call it
     J-space; that is this project's own declared failure condition. -->

---

# 5. Error analysis

<!-- Stratify by relation template. Inspect a seeded random sample of
     successes and failures — seeded, not chosen for narrative appeal (BLK-10).
     Produce a taxonomy with counts, not anecdotes. -->

---

# 6. Sanity checks and red-teaming

<!-- The highest-value section in the document. Neel: "A really *positive*
     sign about an application is when I think of a way the results could be
     false, then discover you've already checked it!"

     Structure it as: here are N ways this could be false; here is what I did
     about each; here is the one I could not rule out. Include the ones that
     came back clean AND the ones that did not. -->

| # | How this could be false | What I checked | Verdict |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

---

# 7. Limitations

<!-- State them as plainly as the findings. Candidates, all real:
       * single model, single lens, one language
       * one observation point — the final prompt token
       * synthetic prompts, not natural text
       * no published shuffled-corpus control lens exists (B3), so the negative
         control is label permutation plus norm-matched random directions
       * whatever the causal-arm outcome forces
     Do not pad this with decorative caveats; name the ones that would change
     a reader's confidence. -->

---

# 8. What I would do next

<!-- Concrete and ordered. The multi-token template lens is the obvious first
     extension — Neel calls the single-token restriction "a crippling
     limitation" and there is a published template lens for qwen3.6-27b. -->

---

# 9. Reproducibility

| | |
|---|---|
| Repository | <!-- URL, made link-shareable --> |
| Commit | <!-- short sha of the frozen state --> |
| Environment manifest | `results/design-verification/environment-manifest.md` |
| Figure registry | `results/figures/FIGURE-REGISTRY.md` |
| Dataset | <!-- path + generation seed --> |
| Batch scripts | `experiments/` |

<!-- Neel: "You're encouraged to include code, but it's not required, I'll
     largely use it to give my agents context." Make it easy for an agent to
     answer questions about what you actually ran. -->

---

# 10. Time accounting

<!-- Pull from llm/memory_bank/time-log.md. Include the Toggl screenshot
     (MEC-20) — encouraged, and cheap credibility on a rule-bound task.

     State the ADR-0005 clock ruling in one sentence if it needs explaining:
     environment setup and design work preceded the counted window; V1/V2/V3
     counted one hour each. -->

| Bucket | Hours |
|---|---|
| Experiments, code, analysis | |
| Project-specific reading | |
| Write-up | |
| **Total (limit 20)** | |
| Executive summary (separate +2) | |

---

# Appendix A — Additional figures

# Appendix B — Full result tables

# Appendix C — Further raw examples
