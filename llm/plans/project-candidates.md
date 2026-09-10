# Candidate Projects — Scored

Status: Decision pending
Owner: Jason
Decision deadline: **Mon Aug 24, 2026** (ADR-0002 records the choice)

Scored against Neel's stated criteria, the 20-hour budget, and the
literature scan (`llm/research/literature-scan-2026-08-22.md`).

## Scoring dimensions

| Dim | What it measures |
|---|---|
| **Fit** | Does it sit inside a direction Neel *names in the doc*? |
| **Orig** | Would he have seen 20 of these? |
| **Feas** | Can a real result land in ~15h of experiments? |
| **Base** | Is there an obvious cheap baseline to beat/compare? |
| **Neg** | Is a null result still publishable/interesting? |
| **Risk** | What kills it |

Scale 1–5. **Neg is weighted heavily** — Neel: *"Negative or inconclusive
results that are well-analysed are much better than a poorly supported
positive result."*

---

## C1 — Does eval-awareness contaminate CoT-faithfulness measurements?

**Question.** Hint-injection faithfulness evals use conspicuously
artificial prompts. Goodfire/UK AISI showed models verbalize
eval-awareness in reasoning chains 95% of the time, and that this
*causally* shifts behavior by 8–34%. So: are we measuring unfaithfulness,
or measuring models behaving differently because they know they're being
tested?

**Why it's open.** The two literatures have never been crossed. The
faithfulness literature treats prompts as neutral stimuli; the
eval-awareness literature never applies its findings to faithfulness
metrics.

**Neel's doc, Model Forensics §6, verbatim:** *"One major issue in
forensics is eval awareness. Can you better characterize eval awareness in
the best open source models? ... How well can we probe for it in real
models?"* — this is a direct hit.

**Experiment.** Hint-injection faithfulness eval (MMLU / GPQA-Diamond,
~6 hint types) on 3 open reasoning models. Classify every rollout for
verbalized eval-awareness. Apply Goodfire's realism interventions
(automated paraphrasing — cuts eval awareness 75%; removal of unrealistic
cues). Re-measure faithfulness. **Primary result: does measured
faithfulness move when eval-awareness is suppressed?**

**Baselines/controls.** Unmodified prompts; paraphrase-without-realism
control (separates paraphrasing from realism); ≥2 faithfulness metrics
(BONAFIDE says one number is meaningless); "just ask the model if it
noticed the hint."

| Fit | Orig | Feas | Base | Neg | Total |
|---|---|---|---|---|---|
| 5 | 4 | 4 | 5 | 5 | **23/25** |

**Risk.** LLM-judge classification of eval-awareness is the load-bearing
step and is exactly what BONAFIDE warns about → must hand-label a
validation subset and put randomly-selected raw examples in the write-up.

---

## C2 — When in post-training does CoT unfaithfulness appear? (Olmo 3 lineage)

**Question.** At what stage of post-training does CoT unfaithfulness
emerge — base → SFT → DPO → RL — using the only open *reasoning* model
that ships its full lineage plus training data.

**Why it's open.** Until Olmo 3 no open reasoning model shipped
intermediate checkpoints at every training stage with the data. No one has
measured faithfulness across them. Sharpened by two adjacent findings:
instruction tuning (not scale, not reasoning) is the dominant lever for
eval-awareness; and only 8% of reasoning-distillation adapter features are
reasoning-related.

**Neel's doc, Science of Post-training §2, verbatim:** *"What does each
stage do? Most of Gemini's safety behaviour comes from SFT, not RL! What
else about the pretraining/SFT/RL division of labour is not what we
assume?* ***Olmo 3 think is a good model to study here***.*" — he names
the model.

**Experiment.** Olmo-3-7B Base / Think-SFT / Think-DPO / Think(RL), plus
the Instruct branch as a control arm. Hint injection + resampling-based
counterfactual importance (Thought Branches methodology) at each stage. If
unfaithfulness jumps at one stage, use the Dolci datasets to identify the
responsible data.

**✅ Verified 2026-08-22 — GO, and upgraded.** All four stage endpoints are
public Apache-2.0 repos. Better: intermediate checkpoints exist as git
*branches* — **55 RL steps** on `Olmo-3-7B-Think` (`step_0025`…`step_1375`)
and **43 SFT steps** on `Think-SFT`. So the headline figure is a
**continuous faithfulness curve across RLVR training**, not a four-point
bar chart. Ai2 also ships six `Olmo-3-7B-RL-Zero-*` models trained straight
from base with no SFT/DPO — a free "does the SFT stage matter" ablation.
See PLAN §2b for repo IDs and the three download/tokenizer gotchas.

**Baselines/controls.** The Instruct branch; ≥2 faithfulness metrics;
capability control (does accuracy move too, confounding the result?).

| Fit | Orig | Feas | Base | Neg | Total |
|---|---|---|---|---|---|
| 5 | 5 | 5 | 4 | 5 | **24/25** ⬆ |

**Risk.** The checkpoint risk is **retired** — verified public. The
remaining risks:

- ⚠️ **`Think-SFT` ships a different tokenizer and no chat template.** If
  `<think>`/`</think>` don't tokenize identically across stages, every
  cross-stage comparison is confounded. Check this first, Aug 23.
- A purely descriptive "it appears at RL" result. Mitigate by pre-committing
  to the follow-up (*which data?* via the public Dolci SFT/DPO/RL sets — do
  **not** rely on OlmoTrace, which is hosted-only and attached to the 32B).

---

## C3 — Positive controls for model forensics

**Question.** Neel's Model Forensics protocol infers *why* a model
misbehaved, and the paper states plainly they lack positive controls
confirming the test is sensitive. Can the protocol recover a *known*
motivation that was deliberately implanted — and discriminate two models
that behave identically for different implanted reasons?

**Why it's open.** Named as a limitation in a two-month-old paper by the
mentor. The companion post lists "creating covertly misaligned model
organisms" and "discriminating between behaviorally identical models with
different internal motivations" as open problems.

**Experiment.** LoRA-implant 2 motivations into Olmo-3-7B-Think producing
the *same* surface behavior via different routes (e.g. shortcut-taking
from low-effort disposition vs. from believing the grader is lenient). Run
the published protocol blind with pre-registered hypotheses. Measure
recovery and discrimination rate. Baseline: black-box behavioral probing
without the protocol.

| Fit | Orig | Feas | Base | Neg | Total |
|---|---|---|---|---|---|
| 5 | 5 | **2** | 4 | 5 | **21/25** |

**Risk.** **Highest fit, worst schedule risk.** Model-organism
construction can eat the entire 20 hours before any forensics happens.
Only viable if the implants stay trivially simple, or if AuditBench
organisms are borrowed and only the reasoning-trace dimension is added.
Not recommended as a first project under a 13-day clock.

---

## C4 — Does CoT/refusal steering entanglement generalize?

**Question.** One 2026 paper found the CoT actively counteracts refusal
steering (39% flip rate with steering alone → 94% when reasoning is
regenerated under steering). Does this hold beyond
DeepSeek-R1-Distill-Llama-8B?

**Experiment.** Replicate on Olmo-3-7B-Think, gpt-oss-20b, Qwen3.5-9B
(residual-stream steering only, given the DeltaNet caveat). Add the
missing causal test via *on-policy resampling* rather than the off-policy
hand-edits the original used — which is exactly what Thought Branches
shows produces unstable effects. So it is a generalization study **plus** a
methodological correction.

| Fit | Orig | Feas | Base | Neg | Total |
|---|---|---|---|---|---|
| 4 | 3 | 5 | 5 | 4 | **21/25** |

**Risk.** Reads as "replication" unless framed around the methodological
upgrade. Cheapest and safest of the five — a good **fallback** if the
Aug 24 de-risk gate fails on C1/C2.

---

## C5 — Resolve the thinking-channel vs answer-channel divergence claim

**Question.** Is it true that hints are acknowledged ~87.5% in thinking
tokens but only ~28.6% in visible answers — meaning answer-only CoT
monitoring misses over half of hint-influenced reasoning?

**Why it's open.** The claim exists only in unreplicated single-author
preprints using LLM-judge classification, in a domain where BONAFIDE just
showed the metrics mostly don't work. If true it undercuts deployed CoT
monitoring; if false it should be retired before it propagates.

**Experiment.** Re-run on 3 current open reasoning models with multiple
judge models (judge choice demonstrably matters), a human-labeled
validation subset, and a BONAFIDE-style ground-truth task. Code is public.

| Fit | Orig | Feas | Base | Neg | Total |
|---|---|---|---|---|---|
| 4 | 3 | 5 | 4 | 5 | **21/25** |

**Risk.** Framing-sensitive — must be pitched as *"resolving a contested
claim with proper controls,"* never as replication. **Combines naturally
with C1** (same harness, same rollouts).

---

## C6 — Does J-Lens recover relational binding, or only a bag of concepts?

**Origin.** Jason's own idea, developed 2026-08-24. Full specification in
`docs/adr/0004-proposed-jlens-relational-binding-candidate.md`,
`llm/plan/jlens-relational-binding-experiment-design.md`, and
`llm/research/jlens-project-research-and-positioning.md`.

**Question.** When two prompts contain the same entities and concepts but
assign them different relational roles, does J-Lens identify the correct
hidden intermediate — and does changing that representation causally change
the model's answer?

**Why it's open.** The J-Lens paper names the limitation itself: a readout
listing `spider`, `legs`, `eight` shows the right concepts without showing
which entity fills which role. Nobody has quantified how bad that is against
a matched alternative.

**Neel's doc, Improved Interpretability Methods §5, verbatim:** *"From a
scientific perspective, what is J-Lens actually doing? How much better is it
really than logit lens and tuned lens and why? How much does it hallucinate?"*
and *"Being single token is a crippling limitation."* He also names J-Lens in
his summary of what his interests have become: *"building and better
understanding generally useful interp techniques (e.g. J-Lens)."* Three of his
four stated J-Lens questions are tested in one controlled setting.

**Experiment.** Synthetic paired two-hop prompts — identical vocabulary,
swapped bindings (`Arin lives in Luma` / `Arin lives in Nori`). Score the
correct intermediate against the *pair's own alternative*, not against
arbitrary tokens. 10 development pairs, 40 held-out, ≥4 relation templates.
Primary metric: pairwise binding success, requiring the ordering to reverse
correctly in both variants. Causal arm: swap the J-space coordinate toward
the counterfactual intermediate, versus a norm-matched random direction.

**Baselines/controls — eight of them.** Logit lens through the same code path
(Jacobian disabled); direct prompting; pair-alternative comparison; relation
deletion; question truncation; label permutation; norm-matched random causal
direction; prompt-template robustness. This is the strongest control
structure of any candidate here.

**✅ ARC environment verified 2026-08-24 — the substrate risk is retired.**
Job 550088 on `falcon1`, L40S: `Qwen/Qwen3.5-4B` and the
`neuronpedia/jacobian-lens` lens (`qwen-n1000`, commit `16a01f3`, 406 MB)
both staged to scratch. `COMPAT_ASSERTIONS: PASS`, `LAYOUT_ASSERTIONS: PASS`,
reference suite 32/32 passing, model load 13.6 s, **peak GPU 8.51 GB of
47.7 GB**. Lens fit against exactly this model; `d_model` 2560 and
`max(source_layers)=30 < 32` both check out. Compute is not a constraint.

| Fit | Orig | Feas | Base | Neg | Total |
|---|---|---|---|---|---|
| 5 | 5 | 4 | 5 | 5 | **24/25** |

**Risks.**

- ⚠️ **B2 — the reference implementation ships no sparse non-negative J-space
  reconstruction.** The pinned commit exposes `fit`/`apply`/`transport`/
  visualisation only; no NNLS, sparse coding, dictionary or reconstruction
  routine. The causal arm (H3) depends on it. Implementing the paper's
  decomposition is exactly the open-ended work the sprint forbids, and
  faking it invites the design's own FAIL condition — *"'J-space' is
  implemented as an arbitrary top-token projection with no correspondence to
  the paper's sparse construction."* **This is the most likely cause of a
  NO-GO on the causal arm.** It degrades gracefully: Hour 11 freezes causal
  work as unavailable and reallocates to stronger passive controls. A scope
  reduction, not a topic pivot.
- ⚠️ **B3 — no published shuffled-corpus control lens exists.** All 40+
  Neuronpedia lenses are fit on `Salesforce/wikitext`. The negative control
  falls back to label permutation plus norm-matched random directions —
  defensible, and it matches Controls 6 and 7, but weaker than hoped.
- ⚠️ **B4 — tokenizer/vocab width mismatch.** `len(tokenizer)=248077` against
  a 248320-wide unembedding: ~243 ids have no tokenizer string. Rank metrics
  must state which width they rank over.
- ⚠️ **Crowding.** Neel gave J-Lens a full section, six sub-questions, and a
  bolded **"Key resource"** link to the open-source lenses. Expect many
  J-Lens applications. The relational-binding framing with matched
  counterfactual pairs is specific enough to stand apart from generic "what
  can you do with J-Lens" exploration — but the framing has to do that work.
- Queue latency ~23 min on L40S with 17/20 nodes draining; `a30_normal_q` is
  an unrestricted fallback. Setup time, not counted time.

**What a null looks like.** J-Lens retrieves both entities but ranks the
correctly-bound intermediate no better than the logit lens, with controls
ruling out a broken pipeline. That is a quantified confirmation of the
paper's own stated limitation — directly useful to the person who wants to
know how much his flagship new method hallucinates.

---

## Recommendation

**Updated 2026-08-26. 9 days to the deadline.**

| # | Candidate | Fit | Orig | Feas | Base | Neg | Total |
|---|---|---|---|---|---|---|---|
| **C6** | J-Lens relational binding | 5 | 5 | 4 | 5 | 5 | **24** |
| **C2** | CoT unfaithfulness across the Olmo 3 lineage | 5 | 5 | 5 | 4 | 5 | **24** |
| C1 | Eval-awareness contaminating faithfulness measurement | 5 | 4 | 4 | 5 | 5 | 23 |
| C3 | Positive controls for model forensics | 5 | 5 | 2 | 4 | 5 | 21 |
| C4 | CoT/refusal steering entanglement | 4 | 3 | 5 | 5 | 4 | 21 |
| C5 | Thinking-vs-answer channel divergence | 4 | 3 | 5 | 4 | 5 | 21 |

C6 and C2 tie on the rubric. The rubric does not break it. These do.

### Recommendation: C6

**1. The head start is large and it cost nothing.** C6 has a verified ARC
environment, a staged model and lens with `COMPAT_ASSERTIONS: PASS`, 32/32
reference tests green, an hour-by-hour plan with a named fallback per hour,
pre-registered hypotheses, and eight controls. All of it is setup and
ideation — uncounted under Neel's rules, and the manifest correctly logs
**0.0 counted hours**. C2 has a verified checkpoint list and nothing else.
With 9 days left that gap is the single biggest practical difference.

**2. The open risks are not comparable in severity.** C6's B2 threatens the
*causal arm*; the design already routes around it at Hour 11 and the passive
result still stands on its own. C2's open risk — `Think-SFT` shipping a
different tokenizer and no chat template — threatens the *primary
comparison*. If `<think>` tokenizes differently across stages, every
cross-stage number is confounded and there is no graceful degradation. C6
degrades; C2 breaks.

**3. C6 has the better control structure.** Eight controls, including three
that specifically distinguish *entity presence* from *correct binding* —
relation deletion, question truncation, label permutation. Neel lists
"failing to compare to baselines" among the disqualifying mistakes and
rewards discovering that an objection was already checked. C6 scores 5 on
baselines; C2 scores 4.

**4. It teaches him more.** His ideal application "teaches me something new."
A quantified answer to *how much does J-Lens hallucinate* informs whether his
flagship new method does what readers will assume it does. C2's result — "it
appears at RL" — is interesting but more descriptive.

**5. It is authentically Jason's.** The relational-binding intuition comes
from his knowledge-graph work, and the positioning note handles the "pet
interest" trap correctly by making J-Lens evaluation primary and the KG
intuition the source of the question rather than the subject. Neel weights
curiosity and says applications that are fun to read get bonus points.

### The argument for C2, honestly stated

C2 is the safer project. It is inference-only, the checkpoints are verified
public, and its headline figure — a continuous faithfulness curve across 55
RLVR checkpoints — is more immediately legible than a binding-accuracy bar
chart. J-Lens is also the more crowded field: Neel promoted it with a bolded
"Key resource" link, so he will see many J-Lens applications and few Olmo-3
post-training ones. If the B2 blocker turns out to sink the causal arm *and*
the passive result comes back flat, C6 ends as a single negative finding with
no causal counterweight. That is still publishable, but it is thinner than
C2's likely outcome.

**If Jason wants the lower-variance path, C2 is defensible and this note
should not be read as ruling it out.** The recommendation is C6 on the
strength of the head start and the graceful-degradation asymmetry.

### Do not attempt

C3 under a 9-day clock. Note as future work.

### Before ADR-0004 can be accepted

ADR-0004 sets four conditions. Status as of 2026-08-26:

| # | Condition | Status |
|---|---|---|
| 1 | Smoke test of J-Lens **and its logit-lens baseline** on a current allowed model | ⚠️ **Partial.** Compat and layout assertions pass, 32/32 tests green — but the setup log does not show the logit-lens switch being exercised. Close this in V1. |
| 2 | Confirm causal interventions can run, **or** declare explicit passive-only scope | ❌ **Open — B2.** This is the decision that most changes the project's shape. Decide it before counting an hour. |
| 3 | Comparison against the accepted candidate using the selection rubric | ✅ **This document.** |
| 4 | Clock ruling: what counts, and whether a pivot resets the timer | ❌ **Open.** See below. |

### Proposed clock ruling

Neel's rules: setup, general prep, and time waiting are not counted;
"writing code for your project", "thinking and planning time", and
project-specific reading are. And: *"If you decide your project is doomed,
you're welcome to give up and start a new one, and reset the timer"* — a
genuine pivot resets.

- Everything through 2026-08-26 — ARC access, environment build, model and
  lens staging, compatibility assertions, the design documents themselves —
  is **ideation and setup. Not counted.** The manifest's 0.0 h is correct.
- V1, V2 and V3 are **project-specific verification: 1 counted hour each**,
  as the sprint already declares. Log them.
- ADR-0002 was never executed against — no code, no data, no findings. So
  moving from C2 to C6 is not a mid-project pivot; it is the Gate 1 selection
  decision arriving late. **No reset is needed because no clock has started.**
- Record this ruling in the ADR that accepts C6, so the write-up can state
  the accounting plainly if asked.

