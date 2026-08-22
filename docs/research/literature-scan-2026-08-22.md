# Literature & Feasibility Scan — 2026-08-22

Status: Complete (snapshot)
Purpose: Establish what is live, contested, and cheaply attackable in
CoT faithfulness and model biology/forensics, so the project choice is
made against evidence rather than vibes.

Method: agentic web survey (75 tool calls), verified against arXiv, HF Hub,
Alignment Forum, and vendor research pages. Claims are flagged where they
rest on a single or weak source. **Anything below marked ⚠️ must be
re-verified before it is load-bearing in the write-up.**

---

## 1. The single most important update

Neel's own group published **Model Forensics** in June 2026
([arXiv 2606.26071](https://arxiv.org/abs/2606.26071); Singh, Kroiz,
Rajamanoharan, Nanda) with a companion post,
[The Case for Model Forensics](https://www.alignmentforum.org/posts/LCGcD28rSMkMTMvBK/the-case-for-model-forensics).
This is his flagship direction and the application doc points at it
directly. It names its own open problems — that list is the highest-value
source of Neel-shaped project ideas available.

Explicitly named open problems in that work:

- **They lack positive controls confirming their tests are sensitive.**
  (Stated outright.)
- Behavior underdetermines motivation.
- Creating covertly misaligned model organisms to validate forensic technique.
- Discriminating between behaviorally identical models with different
  internal motivations.
- Aggregating weak evidence across contexts.
- **Eval awareness is named as "one major issue in forensics."**

---

## 2. CoT faithfulness: the debate has moved

The question is no longer "is CoT unfaithful?" It is **"does our metric
measure anything?"** This shift is the opportunity.

### 2.1 The anchor
[Reasoning models don't always say what they think](https://arxiv.org/abs/2505.05410)
(Chen, Benton et al., May 2025). Hint injection; measure verbalization.
~25% Claude 3.7, ~39% R1.

### 2.2 The metric critique — strongest negative result in the area
[Faithfulness Metrics Don't Measure Faithfulness: A Meta-Evaluation with
Ground Truth](https://arxiv.org/html/2605.25052) (Gur-Arieh, Marasović,
Geva). Builds **BONAFIDE**: procedurally generated tasks with
mathematically necessary bottleneck steps, giving ground truth. Evaluates
8 metrics (Early Answering, Adding Mistakes, Filler Tokens, SCM, FUR,
CC-SHAP, Simulatability, Paraphrasing).

- **Most perform near chance.**
- Importance-based metrics call 90–96% of CoTs unfaithful.
- Semantic-utility metrics call 94–96% faithful.
- Best (CC-SHAP) reaches 0.70 AUROC.
- Metrics do not transfer across settings; they degrade on longer CoTs.

Implication for us: **any project reporting a single faithfulness number
is standing on sand.** Using ≥2 metrics and reporting their disagreement
is now table stakes, and is exactly the kind of skepticism Neel rewards.

### 2.3 The conceptual critique
[Is Chain-of-Thought Really Not Explainability?](https://arxiv.org/html/2512.23032v2)
(Zaman & Srivastava, UNC; ACL 2026). The standard "Biasing Features"
metric conflates *unfaithfulness* with *incompleteness*. >50% of instances
flagged unfaithful are judged faithful by alternative metrics. CoTs
causally mediate hint effects even when the hint is never named.
faithful@k reaches ~90% with more samples — selectivity, not deception.

### 2.4 The methodological fix — and a style guide
[Thought Branches: Interpreting LLM Reasoning Requires Resampling](https://arxiv.org/html/2510.27484)
(Macar, Bogdan, Rajamanoharan, **Nanda**). A MATS output, so it doubles as
a template for what he wants to see.

- Single-sample CoT analysis is inadequate; resample from partial traces,
  study distributions.
- Counterfactual importance (KL) and resilience-based counterfactual++.
- Self-preservation statements in agentic misalignment have **near-zero**
  causal impact (~0.001–0.003 KL) — post-hoc rationalization.
- **Off-policy interventions (hand-edited CoT) produce small, unstable
  effects; on-policy resampling produces coherent ones.** Any project that
  edits CoT by hand needs to justify why against this.
- "Nudged reasoning": hidden information biases cumulatively with no
  explicit mention.

### 2.5 Contested / fragile claims worth attacking
- ⚠️ [Hint-based CoT faithfulness evals still mostly work on Claude](https://www.lesswrong.com/posts/x6spD5nQQS9MiP8ac/hint-based-cot-faithfulness-evals-still-mostly-work-on)
  (LessWrong, Jul 2026) contests Anthropic system-card claims. Reports
  models are *more* faithful following *incorrect* hints, and **could not
  replicate the DeepSeek-R1 numbers from the original paper.** Single
  non-peer-reviewed post; judge-model-dependent. A replication failure on
  the foundational result is significant and under-scrutinized.
- OpenAI [CoT-Control](https://openai.com/index/reasoning-models-chain-of-thought-controllability/)
  (Mar 2026): 13 frontier models, controllability 0.1%–15.4%. Models
  recognize their failure to comply and fail anyway → **incapacity, not
  deception.** ⚠️ Self-interested source.
- ⚠️ Two single-author preprints by R. J. Young cover open-weight
  faithfulness: [Lie to Me](https://arxiv.org/html/2603.22582v1) (12 models,
  41,832 runs, faithfulness 39.7–89.9%, no scaling relationship R²=0.07)
  and [Why Models Know But Don't Say](https://arxiv.org/html/2603.26410v1)
  (**55.4% show thinking-answer divergence**; hint acknowledged ~87.5% in
  thinking tokens vs ~28.6% in the visible answer). Code at
  [github.com/ricyoung/cot-faithfulness-open-models](https://github.com/ricyoung/cot-faithfulness-open-models).
  No lab affiliation, no evident peer review, LLM-judge classification —
  i.e. exactly what BONAFIDE says can't be trusted. **This is an
  opportunity, not a liability:** the claim is striking, cheap to test, uses
  current models, and is unreplicated.

### 2.6 Genuinely unresolved
- No validated faithfulness metric exists.
- Is low verbalization deception, compression, or incapacity? Three papers,
  three answers.
- The thinking-channel/answer-channel asymmetry is claimed but unreplicated.
- **Nobody has separated eval-awareness effects from faithfulness
  measurements.** This is the biggest hole.

---

## 3. Eval awareness — live, and named by Neel

- [Verbalized Eval Awareness Inflates Measured Safety](https://www.goodfire.com/research/verbalized-eval-awareness-inflates-measured-safety)
  (Goodfire + Joseph Bloom/UK AISI, May 2026). 8 models, 19 benchmarks,
  515 verified instances.
  - Eval awareness appears **in reasoning chains 95% of the time, not in
    final responses.**
  - Eval-aware rollouts refuse 3–18pp more.
  - Causal: removing eval-awareness statements and resampling increases
    compliance 8% (34% for safety statements); injecting raises refusal up
    to 25%.
  - **Automated paraphrasing cuts eval awareness 75%**, refusal drops
    correspondingly.
  - Their own open questions: does reduced *verbalized* awareness track
    reduced *internal* awareness? Multi-turn? Eval vs real deployment?
- [Evaluation Awareness Is Not One Capability](https://arxiv.org/html/2606.23583)
  (Jun 2026). 37 open-weight models, 7 families.
  - **Instruction tuning — not reasoning, not scale — is the dominant lever.**
  - Detection largely collapses when benchmark *formatting* is decorrelated
    from evaluation *intent*: much "awareness" is surface format sensitivity.
  - But internal representations stay decodable at AUROC ≥0.98 even when
    behavior breaks down. Argues for ≥3 weakly-coupled axes.
- [Probing and Steering Evaluation Awareness](https://arxiv.org/html/2507.01786v2).
- Neel's doc names Nemotron 49B as a good model for studying how
  eval-awareness is represented.

---

## 4. Model biology — other live threads

- **AuditBench** ([arXiv 2602.22755](https://arxiv.org/abs/2602.22755v1),
  Anthropic Feb 2026): 56 open models with implanted hidden behaviors, 14
  categories. Default agent ~37% success; **scaffolded black-box >50%;
  white-box interp tools mixed.** Headline open problem: the
  **tool-to-agent gap** — standalone interp tools give useful signal but
  fail to improve agent performance. ⚠️ Derivative ecosystem already busy
  (J-Lens/NLA readouts, graft-vs-native organisms, RL-trained auditors) —
  check for collisions before committing.
- **Personas / emergent misalignment.** [Persona Selection Model](https://alignment.anthropic.com/2026/psm/)
  (Anthropic Feb 2026): Assistant representations reuse pre-training
  features that also fire for human characters.
  ⚠️ [Emergent Misalignment Recruits a Pre-existing Persona Subspace](https://arxiv.org/html/2607.21356v1)
  (Jul 2026): 4 unrelated domains share one low-rank persona core (~657×
  above random); projecting it out during fine-tuning drops misalignment
  27.7% → 0.0%. Single author, one model (Qwen2.5-14B-Instruct), one scale,
  one adaptation method — **replication on a current model would be a real
  contribution.**
- **Model diffing / post-training.**
  [Transcoder Adapters for Reasoning-Model Diffing](https://arxiv.org/html/2602.20904)
  (Stanford/MATS, Feb 2026): only **8% of adapter features relate to
  reasoning behaviors**; 37% encode domain knowledge. Hesitation tokens
  ("wait", "hmm") depend on 5.6k features; removing them **cuts response
  length 50% without hurting accuracy.**
  [Localizing RL-Induced Tool Use to a Single Crosscoder Feature](https://arxiv.org/html/2606.26474):
  a single A-exclusive neuron gives +65.0pp tool-correctness.
- **Refusal / steering.**
  ⚠️ [Beyond a Single Direction: CoT Disrupts Simple Steering of Refusal](https://arxiv.org/html/2605.26772v1)
  (May 2026): refusal in reasoning models is jointly encoded in the residual
  stream *and* the CoT. Activation steering alone flips refusal in only
  39%; regenerating reasoning under steering → 94%; suppressing CoT → 70%.
  **The CoT actively counteracts steering.** One model only
  (DeepSeek-R1-Distill-Llama-8B); authors say it needs validation elsewhere.
  [On the Generalization of Steering Vectors for CoT Faithfulness](https://arxiv.org/pdf/2607.29062)
  (COLM 2026 workshop): steering reliably improves cue acknowledgment only
  in the largest model tested; all 4 vector-construction methods perform
  similarly, including one needing no labeled data.

---

## 5. Open-weight reasoning models — verified against HF Hub, 2026-08-22

**gpt-oss (Aug 2025) is now a year old — usable but no longer "current."**

| Model | Params | Released | Traces | Interp tractability |
|---|---|---|---|---|
| Qwen/Qwen3.8-27B | 27.8B dense | Aug 14 2026 | Yes | ⚠️ `qwen3_5` arch, multimodal |
| Qwen/Qwen3.5-9B | 9.65B, 32L, d=4096 | Mar 2026 | Yes, `<think>` | ⚠️ hybrid Gated DeltaNet |
| Qwen/Qwen3.5-4B | 4.66B | Mar 2026 | Yes | ⚠️ same |
| **allenai/Olmo-3-7B-Think** | 7B | Nov 2025 | Yes | ✅ **best substrate** |
| allenai/Olmo-3.1-32B-Think | 32B | Dec 2025 | Yes | ✅ standard dense |
| allenai/Olmo-Hybrid-Think-SFT-7B | 7B | Feb 2026 | Yes | ✅ |
| google/gemma-4-12B-it | 12B | Jul 2026 | Yes | ⚠️ `gemma4_unified`, any-to-any |
| openai/gpt-oss-20b | 20B MoE | Aug 2025 | Yes | ✅ well-supported, aging |
| zai-org/GLM-5.2 · deepseek-ai/DeepSeek-V4-Flash | MoE, large | 2026 | Yes | ✗ too large |

### Two findings that matter more than the table

**(a) ⚠️ Qwen3.5/3.8 are architecturally awkward for interpretability.**
Qwen3.5-9B is a hybrid: `3 × (Gated DeltaNet → FFN) → 1 × (Gated Attention
→ FFN)`. Most layers use *linear* attention, so there is no per-layer
attention pattern to inspect conventionally. Residual-stream methods
(probes, steering, logit lens, activation patching) are fine;
attention-head analysis is not. **This caveat is inferred from the
architecture spec, not documented anywhere — verify empirically before
relying on it.** If attention-level access is needed, use Olmo-3-7B-Think
or gpt-oss-20b.

**(b) Olmo 3 is the strongest interpretability substrate available and is
underexploited.** Per [Ai2](https://allenai.org/blog/olmo3): 7B and 32B,
four variants (Base / Instruct / **Think** / RL-Zero), **intermediate
checkpoints at every training stage** (base → mid-trained → long-context →
post-training), full training data (Dolma 3 ~9.3T tokens; Dolci
post-training), and **OlmoTrace** for tracing outputs back to training
data. Nothing else gives the full post-training lineage of a *reasoning*
model. **Neel's doc says explicitly: "Olmo 3 think is a good model to study
here"** (Science of Post-training).

---

## 6. Tooling status

| Tool | Status | Notes |
|---|---|---|
| **TransformerLens** | ✅ Active | ⚠️ `HookedTransformer` is **deprecated**; use **`TransformerBridge`**, which preserves raw HF weights by default. Claims 15,000+ models / 140+ arch families incl. Qwen3.5, gated-delta-net, Mamba (experimental). |
| **SAELens** | ✅ Active, **moved org** | Now [decoderesearch/SAELens](https://github.com/decoderesearch/SAELens), not jbloomAus. Major **v6 refactor** — migration guide required. |
| **nnsight / NDIF** | ✅ Very active | 0.6 (Feb 2026): remote custom code exec, 2.4–3.9× speedup. [nnsight × vLLM (Jul 2026)](https://nnsight.net/blog/2026/07/13/nnsight--vllm-interpretability-at-production-scale/). ⚠️ Limits: eager execution only, prefix caching disabled, **inference mode blocks gradients** (no probe training / integrated gradients through it). ⚠️ NDIF hosted-model availability unverified — status endpoint was down. |
| **circuit-tracer** | ✅ | Anthropic open-sourced attribution graphs. |
| **transformer-debugger** | ❌ Dead | No 2025–2026 activity. Do not build on it. |

### Compute — Virginia Tech ARC
The public compute page understates capacity. The
[2026 facilities document](https://www.docs.arc.vt.edu/files/arc-fer-2026-long.pdf)
lists **514 GPUs**: TinkerCliffs 64× A100 + 64× H200; Owl 32× B200; Falcon
128× A30, 80× L40S, 72× V100, 18× T4.

Practically: a 7–9B model in bf16 fits comfortably on one L40S/A30; 32B
fits on a single H200; 70B needs an H200 with quantization.
**None of the candidate projects are compute-bound. The binding constraint
is the 20 hours.**

---

## 7. What to avoid (from Neel's doc, cross-checked against this scan)

- GPT-2, Pythia, Gemma 2 — and by extension Qwen2.5 / Llama-3 as the
  *primary* model. All read as old now.
- Toy/synthetic transformers on algorithmic tasks.
- SAE-centric framing unless SAEs demonstrably beat a simpler baseline.
- Any project without an explicit non-interpretability baseline
  ("just ask the model", random vector, linear probe).
- **Single-model claims** — the recurring weakness of the 2026 preprints
  above, and therefore the cheapest way to differentiate.
- Uncritically citing the Young preprints or 2607.21356 as established.

---

## 8. Uncertainty flags to resolve before committing

1. ⚠️ **Verify the Olmo 3 checkpoint lineage actually exposes the stages
   needed** (base → SFT → DPO → RL for the Think branch). Everything in
   candidate C2 depends on this. Check first, cheap to check.
2. ⚠️ NDIF hosted-model availability (status endpoint down at scan time).
3. ⚠️ The Qwen3.5 linear-attention caveat is inference from the spec.
4. ⚠️ The Anthropic system-card claim that hint-based evals stopped
   working, and its rebuttal, both rest on thin sourcing.
5. ⚠️ Check AuditBench derivative work for collisions before touching it.

---

## Sources

[Reasoning Models Don't Always Say What They Think](https://arxiv.org/abs/2505.05410) ·
[Model Forensics](https://arxiv.org/abs/2606.26071) ·
[The Case for Model Forensics](https://www.alignmentforum.org/posts/LCGcD28rSMkMTMvBK/the-case-for-model-forensics) ·
[BONAFIDE](https://arxiv.org/html/2605.25052) ·
[Is CoT Really Not Explainability?](https://arxiv.org/html/2512.23032v2) ·
[Thought Branches](https://arxiv.org/html/2510.27484) ·
[Hint-based evals still mostly work on Claude](https://www.lesswrong.com/posts/x6spD5nQQS9MiP8ac/hint-based-cot-faithfulness-evals-still-mostly-work-on) ·
[OpenAI CoT-Control](https://openai.com/index/reasoning-models-chain-of-thought-controllability/) ·
[CoT Monitorability](https://arxiv.org/abs/2507.11473) ·
[AuditBench](https://arxiv.org/abs/2602.22755v1) ·
[Persona Selection Model](https://alignment.anthropic.com/2026/psm/) ·
[Verbalized Eval Awareness](https://www.goodfire.com/research/verbalized-eval-awareness-inflates-measured-safety) ·
[Evaluation Awareness Is Not One Capability](https://arxiv.org/html/2606.23583) ·
[Beyond a Single Direction](https://arxiv.org/html/2605.26772v1) ·
[Steering Vectors for CoT Faithfulness](https://arxiv.org/pdf/2607.29062) ·
[Transcoder Adapters](https://arxiv.org/html/2602.20904) ·
[RL-Induced Tool Use Crosscoder](https://arxiv.org/html/2606.26474) ·
[Lie to Me](https://arxiv.org/html/2603.22582v1) ·
[Why Models Know But Don't Say](https://arxiv.org/html/2603.26410v1) ·
[Persona Subspace](https://arxiv.org/html/2607.21356v1) ·
[Olmo 3](https://allenai.org/blog/olmo3) ·
[TransformerLens](https://github.com/TransformerLensOrg/TransformerLens) ·
[SAELens](https://github.com/decoderesearch/SAELens) ·
[nnsight × vLLM](https://nnsight.net/blog/2026/07/13/nnsight--vllm-interpretability-at-production-scale/) ·
[MATS Nanda stream](https://www.matsprogram.org/stream/nanda) ·
[ARC facilities 2026](https://www.docs.arc.vt.edu/files/arc-fer-2026-long.pdf)
