# Candidate Projects — Scored

Status: Decision pending
Owner: Jason
Decision deadline: **Mon Aug 24, 2026** (ADR-0002 records the choice)

Scored against Neel's stated criteria, the 20-hour budget, and the
literature scan (`docs/research/literature-scan-2026-08-22.md`).

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

## Recommendation

**Primary: C2 — now the clear leader at 24/25.** Neel names the exact model
in the doc, nobody has used the Olmo 3 lineage this way, the experiment is
inference-only and cheap, and the 98 intermediate checkpoints turn the
headline figure into a continuous curve — legible in one glance, which is
exactly what a 1-page executive summary needs.

**Backup: C1.** Still strong, still named in the doc. Now a genuine backup
rather than a coin-flip, since C2's gating risk has been retired.

**Fallback if the Aug 24 de-risk gate fails on both: C4.** Cheapest,
safest, still real.

**Do not attempt C3** under a 13-day clock. Note it as future work.

### On combining C1 + C2

Tempting: *"does CoT unfaithfulness emerge at the same post-training stage
as eval-awareness — are they the same phenomenon?"* One harness, two
metrics, genuinely original. **But** it doubles the scope, and Neel's doc
is explicit that spreading thin is a common failure. Decide at the Aug 24
gate only if the C2 harness comes up fast, and treat the eval-awareness
axis as a stretch goal that can be cut without harming the narrative.
