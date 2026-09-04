# Randomly selected raw examples

Examples below are drawn with `seed=1337` from the held-out set; they are
randomly selected, not chosen.

Selection rule, stated before the draw: a *success* has a positive J-Lens
`relcomp` margin, a *failure* a negative one; two of each drawn with
`random.Random(1337).sample` over sorted record ids, plus the single closest
call (smallest absolute margin, deterministic). The readout columns are ranks
of the correct and role-swapped intermediate in each lens's vocabulary
readout (the pipeline stores ranks and margins, not top-k dumps). Only the
two primary positions are shown; all four positions per record are in the run
outputs and in `writeup/main-full.md`. All numbers agent-derived from the
committed run output; agent-unverified.

### Example 1 — success (`real-zero-035-BBA`, T6)

> Facts: Clara paints at Bristol. Anna paints at Seattle. Bristol stores granite. Seattle stores bronze. What is stored where Anna paints? Answer:

Correct intermediate **Seattle** -> answer **bronze**; role-swapped alternative Bristol -> granite.

| position | J-Lens margin | J-Lens rank (corr/alt) | logit-lens margin | logit-lens rank (corr/alt) | model (shadow) margin |
|---|---|---|---|---|---|
| relcomp | +0.188 | 256 / 279 | +0.203 | 1233 / 1687 | +0.625 |
| qmark | +7.375 | 62 / 3315 | +7.578 | 40 / 56275 | +5.625 |

### Example 2 — success (`real-zero-047-ABA`, T6)

> Facts: Victor paints at Dublin. Simon paints at Seattle. Seattle stores wool. Dublin stores rubber. What is stored where Simon paints? Answer:

Correct intermediate **Seattle** -> answer **wool**; role-swapped alternative Dublin -> rubber.

| position | J-Lens margin | J-Lens rank (corr/alt) | logit-lens margin | logit-lens rank (corr/alt) | model (shadow) margin |
|---|---|---|---|---|---|
| relcomp | +4.156 | 106 / 1502 | +3.609 | 255 / 26145 | +3.500 |
| qmark | +6.531 | 26 / 718 | +4.938 | 49 / 6785 | +2.188 |

### Example 3 — failure (`real-zero-035-BAB`, T6)

> Facts: Anna paints at Seattle. Clara paints at Bristol. Bristol stores granite. Seattle stores bronze. What is stored where Anna paints? Answer:

Correct intermediate **Seattle** -> answer **bronze**; role-swapped alternative Bristol -> granite.

| position | J-Lens margin | J-Lens rank (corr/alt) | logit-lens margin | logit-lens rank (corr/alt) | model (shadow) margin |
|---|---|---|---|---|---|
| relcomp | -0.688 | 162 / 121 | -0.625 | 473 / 230 | -0.125 |
| qmark | +0.312 | 370 / 440 | +2.312 | 256 / 3638 | +1.875 |

### Example 4 — failure (`real-zero-023-BBA`, T6)

> Facts: Alice paints at Bristol. Anna paints at Athens. Bristol stores rubber. Athens stores linen. What is stored where Anna paints? Answer:

Correct intermediate **Athens** -> answer **linen**; role-swapped alternative Bristol -> rubber.

| position | J-Lens margin | J-Lens rank (corr/alt) | logit-lens margin | logit-lens rank (corr/alt) | model (shadow) margin |
|---|---|---|---|---|---|
| relcomp | -0.500 | 416 / 293 | -0.188 | 1365 / 1057 | -0.562 |
| qmark | +7.500 | 57 / 4011 | +7.453 | 26 / 32028 | +4.438 |

### Example 5 — closest call (`real-zero-038-ABA`, T3)

> Facts: Sarah studies at Athens. Iris studies at Bristol. Bristol teaches linen. Athens teaches timber. What is taught where Iris studies? Answer:

Correct intermediate **Bristol** -> answer **linen**; role-swapped alternative Athens -> timber.

| position | J-Lens margin | J-Lens rank (corr/alt) | logit-lens margin | logit-lens rank (corr/alt) | model (shadow) margin |
|---|---|---|---|---|---|
| relcomp | +0.000 | 143 / 143 | -0.094 | 321 / 284 | +0.125 |
| qmark | +5.375 | 95 / 1576 | +0.844 | 139 / 299 | +1.500 |

---

# 1. Motivation and research question

**Question.** When two prompts contain the same entities and concepts but
assign them different relational roles, does J-Lens identify the correct
hidden intermediate — and does changing that representation causally change
the model's answer?

## 1.1 What J-Lens is, briefly

J-Lens is defined from first principles in §2.1.

## 1.2 What binding is and why a lens struggles to see it

The question is not whether the model represents Paris; it is whether the
model represents *Paris-as-the-city-attached-to-Arin* — and whether an
unsupervised readout can see the difference. Two prompts —

> Arin lives in Paris. Bela lives in Tokyo.
> Arin lives in Tokyo. Bela lives in Paris.

— contain exactly the same four concepts. Only the pairing differs, and the
pairing is the binding. Every record in the dataset therefore carries a
role-swapped twin: both cities are in the context, equally salient, so a
bag-of-concepts readout scores exactly chance (frac = 0.500) by construction,
and only a readout that has recovered the relation can beat it. The distractor
is the experiment.

![The binding problem: two prompts, the same four concepts, opposite pairings. Only the pairing distinguishes them, so only a reader of the relation can tell them apart.](results/figures/binding-concept/fig1-binding-problem.png){width=82%}

Binding is structurally awkward for a lens. A lens maps a residual vector to
a ranking over vocabulary items, and vocabulary items are identities — no
token means "the-city-attached-to-Arin." A token-ranking instrument can only
express a binding by ranking Paris above Tokyo, once the model has resolved
the relation into a selection. That yields three phases at the readout
positions: **before the query**, both bindings are stored, neither selected —
"correct intermediate" is undefined, chance is the correct expected value, and
the Stage 2 prequery frac of 0.550 is the control passing; **during the
query**, the model resolves which binding the question selects — the only span
where a binding could be determined but not yet emitted; **at the final
token**, the answer is already forming, and a directional readout is dominated
by the output shadow (the model itself prefers the correct intermediate on
92.5% of records; J-Lens couples to the model's own margin at r = 0.771).

Stage 3 (§4.2) read the middle phase at frozen settings, with a supervised
difference-in-means probe on the same grid as a reference. The measured
answer: on this task the query window is not shadow-free either. The model's
own next-token preference is already directional inside it (frac 0.800 at the
relation-completing token, 0.731 at the question mark), both lenses track it
at r = 0.88–0.92, and the supervised probe reads chance (0.525) at the
relation-completing token — the window carries the model's developing
selection, not a linearly decodable stored binding.

## 1.3 The gap

The J-Lens release names the bag-of-concepts limitation itself: a readout can
list the right concepts without showing which entity fills which role. What no
one had done is quantify that limitation on a matched-pair task, against
baselines — or separate "reads stored structure" from "predicts the upcoming
output," two accounts that agree everywhere except where the model is wrong.
That separation is what this project supplies.

---

# 2. Method

This is a **method evaluation**, not circuit discovery. The object under test is
J-Lens; the two-hop binding task is an instrument, chosen because it is
controlled, not because the circuit behind it is interesting. Nothing below is
offered as a finding about how Qwen3.5-4B does relational reasoning, and no
claim here extends past a stated layer band and a single token position. The
synthetic templates and the small invented vocabulary are the point rather than
a concession: to ask whether a readout distinguishes *which entity fills which
role*, you need two stimuli whose entity inventories are identical and whose
bindings are not, and natural text does not supply matched pairs like that. A
method evaluation legitimately wants a controlled stimulus. If the instrument
turns out to be the interesting part, this project has failed.

## 2.1 What J-Lens computes, and why a first-order readout is the thing in question

Write `h_l[t]` for the residual stream at layer `l`, token position `t`, and
`unembed(·)` for the model's own output map (final normalisation plus `W_U`).
The **logit lens** applies the output map to an intermediate residual directly
— `unembed(h_l[t])` — assuming the layer-`l` basis is already close enough to
the final-layer basis to be read. **J-Lens** does not assume that: it fits, per
layer, an average input-output Jacobian

```
J_l  ~=  E_x [ d h_L[t] / d h_l[t] ]
```

— a learned `d_model x d_model` linear *transport* into the final-layer basis
— and reads `unembed(J_l @ h_l[t])`. In the pinned reference implementation,
calling the same code with `use_jacobian=False` substitutes the identity for
`J_l` and yields the logit lens through the *identical* extraction, hooking
and decoding path — so the J-Lens-versus-logit-lens comparison isolates
exactly one thing, the learned transport, and cannot be contaminated by a
difference in capture, indexing or scoring (Control 1 in §2.5).

**Why this is worth testing.** `J_l` is a *first-order* object: an averaged
linear approximation of a map that is not linear. "Open Problems in
Mechanistic Interpretability" asks how attribution methods can capture
"higher-order effects beyond first-order approximations of model behavior."
Binding is a conjunctive property — not of Arin being present or Luma being
present, but of the pairing between them — so this project tests an instance
of that open problem: does an averaged first-order readout preserve structure
that is, by construction, not carried by either constituent alone? I am not
claiming binding is literally a second-order Taylor term; the claim is the
weaker, testable one — whether a single averaged linear operator, applied
identically to every input, preserves a conjunctive property is an empirical
question with no obvious answer in either direction.

## 2.2 Substrate: model, lens, and environment

Every identifier below is taken from `results/design-verification/environment-manifest.md`,
which records them as verified on the execution GPU rather than from memory.

| | |
|---|---|
| Model (pinned) | `Qwen/Qwen3.5-4B` @ `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`, resolved as `Qwen3_5ForCausalLM` (text tower), `torch.bfloat16` |
| Layers / `d_model` / unembedding width | **32** / **2560** / **248320** (`Qwen2Tokenizer`, `len(tokenizer)=248077`) |
| Lens (pinned) | `neuronpedia/jacobian-lens` @ `16a01f30`, file `..._n1000.pt` (sha256 `1f9a8f8f…`, n_prompts=1000) |
| Lens `source_layers` | `0..30` (31 layers); model layer 31 is the lens's output row |
| Reference implementation | `anthropics/jacobian-lens` @ `581d398` (Apache-2.0); test suite 32/32 passing on the execution GPU |

**Provenance and compatibility.** The lens was fit by Neuronpedia with
`fit_lens.py Qwen/Qwen3.5-4B` on `Salesforce/wikitext` (train split,
`max_seq_len=128`, bfloat16) — a generic-corpus lens, not fit on anything
resembling this task's prompts, which is why the coverage control in §2.5
exists. One ambiguity resolved rather than glossed: the lens directory's
`config.yaml` describes its *other* checkpoint (`prompts_fitted: 417`); the
loaded `..._n1000.pt` reports `n_prompts=1000` internally and is the
checkpoint the reference walkthrough selects. Compatibility was asserted on
the execution GPU, not assumed (`COMPAT_ASSERTIONS: PASS`): the lens records
this exact model ID, `d_model` 2560 == 2560, `max(source_layers)` 30 < 32.

**Activations are read from the HuggingFace modules directly; TransformerLens
is not in the path.** `HookedTransformer.from_pretrained` folds LayerNorm and
centers weights by default; a lens fit on HF-native activations handed
processed activations returns wrong numbers without raising. The HF path the
lens was fit through is the path used.

**Hardware.** VT ARC Falcon, NVIDIA L40S, CUDA 13.0, PyTorch 2.13.0+cu130,
transformers 5.16.1, Python 3.12.3. Model load 13.6 s; peak GPU allocation
8.51 GB of 47.7 GB — headroom is not a constraint on this design.

## 2.3 Dataset: matched pairs, and the order-reversed variant

**The paired construction is the whole method.** Each item is a pair of prompts
built from an identical inventory of entities, relations and answer candidates.
Only the binding differs.

| | Prompt | Correct intermediate | Correct answer |
|---|---|---|---|
| Variant A | Arin lives in Luma. Bex lives in Nori. Luma uses zent. Nori uses vark. What is used where Arin lives? Answer: | `Luma` | `zent` |
| Variant B | Arin lives in Nori. Bex lives in Luma. Luma uses zent. Nori uses vark. What is used where Arin lives? Answer: | `Nori` | `vark` |

The two prompts contain the same four proper nouns, the same two relations and
the same two answer candidates. Any readout that responds to *which concepts are
present* returns the same thing for both. So a readout can only score above
floor on the metric in 2.5 by representing which entity is bound to which — that
is what makes the pair, and not the individual prompt, the unit of analysis.

**The order-reversed variant dissociates role from linear position.** In
Variant A the correct intermediate is also the first-mentioned location; in
Variant B it is the second. A readout that merely prefers the first-mentioned
location would therefore look like it had learned binding — and on IOI,
positional signal dominated token signal roughly 3:1. Each item is rendered
twice, canonical and fact-order-reversed; the binding is unchanged, the linear
position of the correct intermediate moves, and both renderings are scored. A
position-tracking readout scores at floor across the reversal; a role-tracking
readout is invariant to it.

**Templates, tokenization, indexing.** Six relation templates (T1–T6),
generated with seed 20260827 by the committed generator
(`src/make_dataset.py`). Every scored intermediate and answer is a single
token under `Qwen2Tokenizer` in the exact surface form in which it is scored
(leading whitespace changes tokenization, so the spaced form is checked);
entity names are checked too, since a multi-token name smears the concept
across positions. Batches are left-padded, and the index `-1` convention is
verified on a batch of mixed lengths rather than assumed.

**Behavioral eligibility, screened first.** Before any lens work, both
variants of a pair must be answered correctly by the unmodified model under
deterministic (greedy) decoding. Nonce entities plus invented predicates plus
a chained two-hop query is close to the opposite of IOI's "common grammatical
structure," and a 4B model might simply not do the task — the
highest-probability, lowest-cost failure in the design, so it was de-risked
first. Result (`results/runs/20260827T090437Z-eligibility-screen/`): real
lexicon, zero-shot, `pair_eligibility(AB) = 0.900` against the pre-registered
0.80 threshold; `alt_answer_rate = 0.000`; `fact_order_gap = −0.033`. Few-shot
was dropped because it scores worse under content-based scoring (0.750) than
zero-shot (0.950). `[agent-unverified]`

**Split.** 10 development pairs and 40 held-out pairs, spread across the
templates. Development pairs carry all debugging, all pipeline validation and
the layer selection in §2.4. **The 40 held-out pairs are not looked at, in
any form, until after the Hour 7 freeze**, and are never tuned on.

## 2.4 Observation point and the layer-selection rule

**Observation point: the residual stream at the final prompt token** — the
position the method's own authors score at. The reference repository's
lens-quality evaluation (`data/evaluations/lens-eval-multihop.json`) reads the
single token immediately preceding `target`, so a reader who doubts the
position can check it against the reference eval rather than my judgement.

**The layer band is not pre-declared; the selection rule is** — pre-declaring
a band from depths measured in a 12-layer model risks scoring a 32-layer model
at the wrong depth and calling that a method failure. The rule, frozen at Hour
7 before any held-out prompt was scored: sweep all 31 source layers on
development pairs; score each by the mean paired J-Lens margin (§2.5); take
the argmax; score every arm at layers selected on J-Lens — the choice that
disadvantages J-Lens least, so if it loses, it loses on ground chosen in its
favour; publish the full 31-layer development curve, so a reader can see
whether the selection sat on a plateau or a spike.

**Result, and a deviation stated.** The written rule also allowed growing a
band of near-peak layers; the implemented pipeline scores at the single
selected layer per position — a simplification made before any held-out
contact, applied identically to every arm, recorded here rather than silently
reconciled. Selected layers, identical on both clusters at every position
carrying signal, frozen in `experiments/stage3/freeze.json`: J-Lens L30 at
the relation-completing token, L27 at the question mark, L27 at the final
token, L25 at prequery; logit lens L30/L29/L30/L24. Where no layer carries
signal the argmax selects noise and different GPUs round differently (q00:
L29 vs L28, median rank swinging 5,186 → 29,916) — visible because the full
curve is published.

**The observation point evolved, under pre-registration, and the final token
did not survive as primary.** Verification showed the final prompt token is
output-contaminated (38/40 dev generations name the intermediate; §4.2), and
the pre-query token precedes the question naming a subject, so no entity is
yet the correct intermediate there — its chance-level score is the control
*passing*. A position sweep over the query window, with its decision rule
committed before the sweep job was submitted (learning log, Hour 3), moved the
primary positions to the **relation-completing token** and the **question
mark**, frozen by anchor in `results/stage2/FREEZE.md` before any code that
reads held-out was committed. Final and pre-query are retained as the
contaminated and undetermined references respectively.

## 2.5 Arms, metrics, and controls

![Three instruments on the same residual: the supervised difference-in-means probe as ceiling, J-Lens as the unsupervised reader, and the logit lens as floor.](results/figures/binding-concept/fig3-three-instruments.png){width=82%}

### Three arms

**Arm 1 — J-Lens.** `unembed(J_l @ h_l[t])` at the selected layer.

**Arm 2 — logit lens.** The same call with `use_jacobian=False`: the identity
substituted for `J_l` through the identical extraction path (§2.1). Isolates
the learned transport and nothing else.

**Arm 3 — supervised difference-in-means reference.** A two-arm comparison
is uninformative: if J-Lens beats logit lens, that may only say logit lens
does not work on Qwen3.5; if both sit at floor, "J-Lens cannot read binding"
and "binding is not linearly there at all" produce identical numbers. Arm 3
separates them cheaply: a nearest-centroid (isotropic LDA) readout over the
closed set of intermediate tokens — dev-mean centering, per-class centroids,
score `dot(x, mu_v) - 0.5*||mu_v||^2`, margin = score(correct) −
score(alternative); twenty lines, no optimiser. Centroids are fit on
development prompts only and applied unchanged to held-out (leave-one-pair-out
reported as a memorisation check). It is a *reference level*, not a ceiling —
it under-estimates linear availability and over-states what an unsupervised
readout should reach. Near floor, the conclusion is about the model or layer;
high while both lenses sit at floor, about the readouts.

**Arm 3 result.** A first run was uninterpretable (fourteen classes over ten
pairs left nine without leave-one-pair-out support), which forced the shared
six-word vocabulary now used by both splits — a dataset fix, recorded as such.
Regenerated, it scores all records (LOO 0.625–0.650 at the final token across
three GPU runs) and transfers dev→held-out unchanged: **0.725 → 0.731 at the
question mark** — exactly the model's own next-token preference rate at that
position — and **0.525 at the relation-completing token where J-Lens reads
0.781**. Both numbers are load-bearing in §4.2. (The Stage 1 manifests emit
`jlens`, `logitlens` and `jlens_random_transport`; the last is control 8a run
through the same harness, not a fourth arm, and arm 3 runs outside the Stage 1
passive script.)

### Metrics

**(a) Pairwise binding success — binary, conjunctive.** A pair succeeds only
if the readout prefers the correct intermediate in Variant A *and* the
ordering reverses correctly in Variant B. Because the two variants have
identical entity inventories, **any readout that responds only to concept
presence scores exactly zero on this metric** — it must return the same
preference for both variants, and one of them is wrong. An independent
unbiased coin scores 25%. Both floors are reported; which one is the relevant
null depends on the failure mode being argued against.

**(b) Paired binding margin — continuous.** `m(p, l) = s_l(correct) −
s_l(alternative)`, averaged over the two variants of a pair. For arms 1 and 2,
`s_l` is the raw pre-softmax logit in the model's own unembedding basis — the
direct analogue of IOI's logit difference; for arm 3, the nearest-centroid
score. Margins are comparable within an arm, never across arms (the arms do
not share units): cross-arm comparison uses the sign-based accuracy in (a) and
a standardised effect size (`mean(M) / sd(M)` within arm) only.

**(c) Recall@10**, pre-registered, secondary. **Uncertainty:** paired
bootstrap resampling *pairs*, 10,000 resamples, seed in the run manifest, 95%
intervals throughout. **Rank width (blocker B4):** `len(tokenizer) = 248077`
but the unembedding is 248,320 wide, so ~243 output ids have no tokenizer
string. All rank metrics use the full 248,320 width — the conservative choice,
since the unaddressable ids can only worsen a correct token's rank — with the
tokenizer-width ranking reported as a robustness line. Metrics (a) and (b)
never form a vocabulary rank and are unaffected.

### Baselines and controls

| # | Control | What it rules out | Status |
|---|---|---|---|
| 1 | Logit lens, same code path, `use_jacobian=False` | Any advantage comes from the transport `J_l`, not the pipeline | Primary arm |
| 2 | Supervised difference-in-means reference (arm 3) | "Neither lens can read binding" confused with "binding is not linearly there" | Primary arm |
| 3 | Order-reversed fact rendering | A readout that tracks linear position rather than role | Applied to every item |
| 4 | Coverage positive control | A null caused by the lens never having seen this vocabulary | Required before any null |
| 5 | Direct prompting | The task being legible without any internal method | Held-out |
| 6 | Pair alternative, not arbitrary distractor tokens | An easy comparison against irrelevant vocabulary | Built into the metric |
| 7 | Label permutation | Attractive token lists that do not depend on the label mapping | Held-out |
| 8 | Norm-matched random *transport* (passive) / *direction* (causal) | Margins or effects any norm-matched perturbation would produce | 8a in Stage 1; 8b unavailable with the causal arm |
| 9 | Prompt-template robustness | A result specific to one phrasing | Wording fixed before held-out |
| 10, 11 | Relation deletion / question truncation | Co-occurrence tracking; target-independent selectivity | **Cut** before any result — see note |

**Control 4 result: PASS.** Before any negative result is reported, J-Lens
must be shown to recover *something* unambiguous through the same prompts and
code path. V1 ran the reference multihop evaluation through the pinned lens at
Gate 1 (jobs 550510/550548/550555, verdicts in
`results/slurm-logs/README.md`): 8/8 tooling checks pass; J-Lens
pass@10 = **0.350** against the logit lens's **0.200** through the identical
path, with the lens argmax differing from the logit-lens argmax at 29/31
layers — the transport is live, so the null results elsewhere in this report
are not a coverage artifact.

**Controls 10 and 11 — cut before any result (2026-08-27), reasoning
stated.** They repeat control 6's move (perturb the prompt, watch the readout)
and take the model off-distribution, so a moved readout may only report a
broken prompt. The pre-query position performs control 11 positionally and
in-distribution — though it measures concept availability (median rank 346 vs
the logit lens's 78,525), not binding selectivity (correction, 2026-08-29).
The honest cost is control 10, the one control that directly threatens a
positive headline; offered in its place is a **resample** variant (`Perth uses
granite` → `Perth uses basalt`, readout must follow) — in-distribution and
sharper than deletion. It has not run (§7), and the paired margin should not
be read as excluding a co-occurrence account until it does.

**Negative controls available.** No published shuffled-corpus control lens
exists — all 40+ released J-Lens checkpoints are wikitext-fit — so the
negative controls are label permutation (7) plus a locally implemented
norm-matched random *transport* (8a): every `J_l` replaced by a Gaussian
matrix of matched Frobenius norm, re-run through the identical extraction
path. **Result: the control behaves** — direction 0.475–0.537 (chance) at
every position on both splits and every GPU, median rank of the correct
intermediate ~130,000–206,000 of 248,320, against the fitted transport's
11–357 at its selected layers.

### The causal arm is unavailable, and that is itself a method-evaluation finding

ADR-0005 scoped this project passive-primary; the causal arm (H3) would run
only if a faithful sparse non-negative J-space reconstruction existed in the
released artifact. It does not: an audit of the pinned vendor tree
(`scripts/v2_decomposition_audit.sh`, step 0 of the Stage 1 job; run
`results/runs/20260827T153925Z-stage1-passive-readout/`) found zero matches
for sparse / non-negative / NNLS / lasso / dictionary / decomposition /
reconstruction across the package, README, walkthrough and tests — full
documented negative in
`results/design-verification/v2-decomposition-verification.md`. Stated
plainly: the capability the method's framing implies is not supported by its
released artifact. That is reported as a finding about the method under test,
not as a gap in execution. Substituting an arbitrary top-token projection and
calling it J-space is this project's declared FAIL condition and was not done.

---

# 3. Preregistration and what was frozen when

Each freeze is a commit that precedes the run it governs; the repository
history is the timestamp.

| Frozen thing | Where | Before |
|---|---|---|
| Dataset generator, seed 20260827, eligibility thresholds | `src/make_dataset.py` | any GPU run |
| Layer-selection rule (argmax on dev, publish full curve) | Hour 2 log entry | the dev sweep |
| Position-sweep decision rule | Hour 3 log entry, `7adaad1` | the sweep job |
| Positions (by anchor) and per-position layers | `results/stage2/FREEZE.md`, `experiments/stage3/freeze.json`, `c5e9a5a` | any held-out-reading code (`62dc94b`) |
| Failure condition ("frac at both primary positions ≈ control = forking paths, and that is the finding") | Hour 4 log entry | the held-out read |

The held-out split was read **once**, by job 554591, after all of the above.
Contact before the freeze, disclosed in `FREEZE.md`: its `_meta` header, record
count, pair count and template-id set — no prompt, entity or answer. Two
pre-registered predictions in the Hour 4 entry were wrong (the output shadow at
the window positions is not near zero; see §4.2), and the entry records that
rather than the predictions being revised.

---

# 4. Results

## 4.1 Behavioral eligibility

The screen is a *label*, not a filter: no record was dropped, and every readout
row joins to its behavioural label by `record_id` within the same job.

| Split | GPU | pair eligibility (AB, real/zero) |
|---|---|---|
| dev (n=40) | A30, L40S ×2 | 1.000 |
| dev (n=40) | A100 ×4 (incl. two preempted re-runs) | 0.900 |
| held-out (n=160, T1–T6) | A30 | 0.950 |

Eligibility is **deterministic per GPU architecture and reproducible within
one** (1.000 on every L40S/A30 run, 0.900 on every A100 run): greedy decoding
turns last-bit floating-point differences into different tokens, so
eligibility percentages always name the architecture. This is also control 5
run at full scale — "just ask the model" solves the task at 90–100%, which is
precisely what makes a passive readout worth interrogating: the answer is
already on its way.

## 4.2 Primary result: what the readout is actually reading

The result did not survive in the form the project set out to test, and the
path from the apparent result to the real one is the finding. Three stages,
each with its control.

**(a) At the final token, the "recovered intermediate" is the model's output
forming.** The first full run looked like a headline: J-Lens places the
correct intermediate at median rank ~35 of 248,320 at its selected layer,
preferring it to its role-swapped twin on 39/40 dev records. Capturing the
model's own next-token distribution in the same forward pass dissolved it: the
model itself already prefers the correct intermediate on **37/40** records
(mean margin +2.77 — independently re-derived by hand,
`results/verification/verify-shadow-554518.out`), 38/40 generations name the
intermediate in plain text before answering, and the J-Lens margin tracks the
model's own margin at r = 0.77 against an anchor of 0.81 for a bare logit lens
one block below the output. Reading the residual there is reading the model's
next few words.

**(b) The query window is where the question is well-posed — and direction
does appear there.** Between the undetermined pre-query position and the
contaminated final token lies the span where the binding is determined but not
yet emitted. Sweeping it (pre-registered rule, both clusters): direction
appears at the token that *completes the relation* (" lives": 0.775/0.750
across GPUs against a label-permutation control at 0.350) and at the question
mark (0.675), not at the token naming the subject (" Helen" sits at chance
with the control above it). The randomised transport stays at chance across
the whole window.

**(c) Frozen held-out confirms the positions — and the measured shadow
settles the attribution.** At frozen anchors and layers, on 160 records the
lens had never seen, across six templates:

![Direction score by position on frozen held-out: both lenses rise at the
relation-completing token and track the model's own next-token preference;
the randomised transport stays at chance.](results/figures/stage3-frac-by-position.png){width=82%}

| held-out, frozen | frac | label-perm control | median rank |
|---|---|---|---|
| J-Lens, relation-completer (L30) | **0.781** | 0.519 | 128 |
| J-Lens, question mark (L27) | **0.669** | 0.556 | 95 |
| logit lens, same positions | 0.688 / 0.738 | 0.519 / 0.544 | 393 / 82 |
| randomised transport | 0.494–0.537 | — | ~131k–171k |

The pre-registered failure condition did not fire: the sweep's positions are
real, not forking paths. But the same run measured, for the first time, the
model's own next-token distribution *at* those positions — and the Hour 4
prediction that it would be near zero was wrong. The model already prefers the
correct intermediate at **0.800** (relation-completer) and **0.731** (question
mark): it reads ahead, mid-question. That creates, at last, a discriminating
set of usable size — 32 and 40 held-out records where the model's developing
preference points the *wrong* way — and on it:

![On records where the model's own developing preference is wrong, every
passive readout is wrong with it.](results/figures/stage3-discriminating-set.png){width=82%}

| held-out | lens acc, preference wrong | lens acc, preference right | r(lens, preference) |
|---|---|---|---|
| J-Lens, relation-completer | **0.344** (n=32) | 0.891 | +0.88 |
| J-Lens, question mark | **0.125** (n=40) | 0.872 | +0.92 |
| logit lens | 0.250 / 0.200 | 0.797 / 0.932 | +0.71 / +0.93 |

Below chance in every cell. Where the model's developing preference is wrong
about the intermediate, the lens is wrong *with* it. Arm 3 closes the
mechanism: on the same residual at the relation-completer the supervised probe
reads nothing (0.525) while J-Lens reads 0.781 — the binding is not linearly
present in the residual there; the Jacobian, a linearization of the remaining
computation, manufactures the preference from it. At the question mark the
supervised probe transfers dev→held-out at 0.725→0.731, exactly the
preference rate.

**The supportable claim.** *J-Lens is a well-calibrated predictor of what the
model is about to say, at every position where direction is readable — and an
instrument for reading stored-but-unexpressed bindings nowhere on this task.*
Its surviving edge over the logit lens is concept-rank localization at
early/mid positions (pre-query median rank 346–373 against 76,000+; 128 vs 393
at the relation-completer), largely gone by the question mark (95 vs 82).

**What this does not claim.** The model demonstrably *computes* the binding —
it answers at 90–100%. This report establishes neither the existence of a
binding representation at any particular locus nor its exclusion: it
establishes that a family of passive linear readouts at four single positions
sees nothing beyond the developing output preference. The places binding most
plausibly lives — fact-token residuals, attention QK structure, nonlinear or
low-magnitude encodings — were not probed. The conclusion is about the
instrument, not the model.

## 4.3 Layerwise structure

Full 31-layer curves for every arm and position ship in the run records.
Selected layers sit inside the fitted range (final-token peak at L27, not the
L30 boundary) — mild evidence the selection tracks computation rather than
the lens's edge. One indexing fact, caught by hand-verification and confirmed
from vendor source (`results/verification/readout-convention.md`): lens layer
*i* is the residual **after** block *i*, so L30 is the penultimate block —
earlier drafts said "last layer"; corrected. The gap between the logit lens at
L30 and the model's own distribution therefore isolates the final block: ~11
points of direction at the relation-completer (0.688 → 0.800), nothing at the
question mark (0.738 → 0.731) — the final selection happens at the
relation-completing token and is finished by the question mark.

## 4.4 Controls

| Control (§2.5) | Outcome |
|---|---|
| 1 logit lens, identical path | Parity on direction everywhere that matters; J-Lens leads on rank at early/mid positions only |
| 2 supervised reference | Transfers dev→held-out (0.725→0.731 at qmark = the preference rate); reads nothing at relcomp (0.525) |
| 3 order-reversed rendering | Applied to every item; margins flat across all four AB/BA cells |
| 4 coverage positive control | PASS — reference eval pass@10 0.350 vs 0.200, 8/8 tooling checks |
| 5 direct prompting | 90–100% by architecture (§4.1) |
| 7 label permutation | 0.35 on dev; **0.45–0.56 on held-out**, audited: with a six-word pool only 65/160 permuted label pairs are fully disjoint from the record's own (4 identical, 8 swapped, 83 share a city). The control is weaker on held-out and every held-out gap is read against this |
| 8a norm-matched random transport | Chance direction, rank ~150k, both splits, all GPUs |
| 9 template robustness | Signal above control on all six templates; T1 (the dev template) inflated — §5 |
| 10, 11 | Cut before results, reasoning and correction in §2.5; the resample variant of 10 remains unrun and is listed in §7 |

## 4.5 Causal arm

Unavailable, as ADR-0005 anticipated it might be, and for the reason
verified rather than assumed: the reference implementation ships **no sparse
non-negative J-space reconstruction** (blocker B2 — zero matches for any
decomposition machinery across the vendored package, README, walkthrough and
tests; `results/design-verification/v2-decomposition-verification.md`). No
top-token projection was substituted — that is this project's declared failure
condition. The supervised reference (arm 3) carries the "is it linearly there
at all" question the causal arm would have addressed more strongly, and
activation patching between order-swapped twins is the first item of §8.

---

# 5. Error analysis

**By template** (J-Lens, frozen positions, held-out; n=24–28 per cell):
relation-completer T1 0.96, T2 0.79, T4 0.83, T3 0.75, T5 0.68, T6 0.68;
question mark T1 0.82, T4 0.75, T2 0.64, T5 0.64, T3 0.62, T6 0.54. The dev
template travels with an ~0.15–0.20 bonus; every template still clears its
control. Dev-split numbers should be read as the optimistic end of the range.

**The principled error taxonomy is the discriminating set** — selected by a
seed-fixed criterion (the model's own preference sign), not by narrative
appeal: 32 relation-completer and 40 question-mark held-out records where
preference and truth diverge, on which every passive readout scores 0.125–
0.344. Their record ids and per-record margins are in the Stage 3 run JSON;
the three dev cases (`real-zero-002-BAB`, `-004-BBA`, `-009-AAB`) were
additionally hand-verified. The failure mode is uniform: the readout follows
the preference. No second failure mode was found — which is itself the
finding, since a latent-binding reader should have produced one.

---

# 6. Sanity checks and red-teaming

| # | How this could be false | What was done | Verdict |
|---|---|---|---|
| 1 | The final-token "recovery" is the output leaking in | Model's own distribution captured in the same pass; hand re-derived (37/40, +2.77) | **True — headline retired**, §4.2a |
| 2 | The window positions are forking-paths artifacts | Decision rule pre-sweep; anchors/layers frozen pre-read; held-out read once | Ruled out: 0.781/0.669 vs control, 160 unseen records |
| 3 | The pre-query null means J-Lens "fails" | Position precedes the subject being named; chance is the control passing | Corrected in place, §2.5 |
| 4 | The window signal is the shadow again | Preference measured at every position; discriminating set built | **True** — below chance on preference-wrong records |
| 5 | Layer indexing off by one; "L30" wrong | Independent re-derivation caught it; vendor source read | True — L30 is penultimate; corrections dated in place |
| 6 | Numbers are GPU luck | Same commit on A30/L40S/A100, two clusters; lens numbers replicate to ~5% | Quantified; architecture named with every eligibility |
| 7 | Label-perm control weakened by six-word pool | Collision audit: 65/160 disjoint | True — caveat on every held-out gap |
| 8 | Instrument bugs shape results | Three invalid runs kept with NOTE.md, none cited | Recorded, `results/slurm-logs/README.md` |
| 9 | Preempted runs contaminate the record | Preemption reconstructed from timestamps, nothing back-filled | Recorded |

The one not ruled out: binding encoded nonlinearly, at fact-token positions,
or in attention QK structure. Nothing in this report touches it.

---

# 7. Limitations

The claim boundary first, because it is the one a reader needs: **neither the
existence nor the exclusion of a binding representation is established.**
Behavioural competence proves the model computes the binding; this report
shows only that passive linear readouts at four single positions read the
developing output preference and nothing beyond it. Fact-token residuals,
attention structure, nonlinear and low-magnitude encodings were not probed.

Also real, in order of weight: one model, one lens checkpoint, one language,
synthetic six-word single-token prompts; n=40 dev / 160 held-out; the held-out
label-permutation control weakened by vocabulary collisions (measured, §4.4);
no published shuffled-corpus control lens (B3); the resample variant of
control 10 never ran, so a co-occurrence account of the *rank* results is
constrained only by label permutation; and the causal arm is absent (B2), so
every claim about the readouts is correlational.

---

# 8. What I would do next

Ordered: (1) **probe the construction site** — arm 3 at the fact tokens
(does "Prague"'s residual in "Helen lives in Prague" encode *Helen*?), the
first position where binding must exist in some form; (2) **activation
patching between order-swapped twins** at the frozen positions — the causal
test passive readouts cannot supply; (3) the deferred stimulus-format test
(ADR-0006); (4) the published multi-token template lens for the 27B model,
since the single-token restriction bounds everything here; (5) inside the
final block, whose contribution (§4.3) localises the final selection.

---

# 9. Reproducibility

| | |
|---|---|
| Repository | `github.com/djjay0131/mats-12-application`, branch `exp/v1-v3-verification` |
| Model | `Qwen/Qwen3.5-4B` @ `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a` |
| Lens | `neuronpedia/jacobian-lens` @ `16a01f309fcec900fdcec3f4cd5b64f3d00e4d5a` (branch `qwen-n1000`, resolved and pinned on both clusters) |
| Vendored lens source | commit `581d398`, diff-identical on both clusters |
| Datasets | `results/datasets/dev.jsonl`, `heldout.jsonl` (seed 20260827, generator committed) |
| Freeze | `results/stage2/FREEZE.md` + `experiments/stage3/freeze.json` |
| Run records | `results/runs/<UTC>-<slug>/` — manifest, command, stdout, outputs; invalid runs kept with NOTE.md |
| Environments | Falcon `/scratch` and a from-scratch TinkerCliffs rebuild, 61 packages bit-identical (`experiments/stage2/tinkercliffs-env/README.md`) |
| Independent checks | `results/verification/` — Jason's re-derivations (shadow: exact match; ranks: exposed the layer-indexing convention) |

Every pipeline number is `agent-unverified` unless covered by an independent
re-derivation in `results/verification/`; the dev shadow figures and the
readout convention are so covered.

---

# 10. Time accounting

Clock ruling (ADR-0005): wall-clock time, not summed agent-hours; setup,
queue waits and bridge outages uncounted. `llm/memory_bank/time-log.md` is
the record; each block is marked Verified (artifacts at both ends) or
Estimated.

| Bucket | Hours |
|---|---|
| Experiments, code, analysis (incl. Jason's independent verification) | 15.3 |
| Project-specific reading | 0.0 (literature scan predates the project lock; uncounted) |
| Write-up drafting (agent, this document) | 1.4 |
| **Total counted (limit 20)** | **16.7** — 7.1 verified, 9.6 estimated |
| Executive summary (separate +2 budget) | not started — Jason's prose |

---

# Appendix — Where everything lives

`results/figures/FIGURE-REGISTRY.md` is the figure registry of record (sha256,
generating commit, claim per figure). Per-record scores, per-layer curves and
shadow margins are machine-readable in `results/runs/*/outputs/*.json`; the
aggregation scripts (`experiments/analysis/`) run from a cold interpreter
against committed inputs. Raw examples beyond §0 can be checked against the
committed dataset files by `record_id`; generations are in the eligibility run
outputs. A fuller, unabridged version of this document is preserved at
`writeup/main-full.md`.
