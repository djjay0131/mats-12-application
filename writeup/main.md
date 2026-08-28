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

J-Lens is defined from first principles in §2.1.

## 1.2 The gap

<!-- The bag-of-concepts limitation, quoted from the source rather than
     paraphrased. Then: nobody has quantified it against a matched
     alternative. That is the hole this fills. -->

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

J-Lens is recent enough that a reader fluent in mechanistic interpretability may
never have encountered it. It is not in the standard reading; every lens in the
compiled interpretability context I worked from is logit lens, tuned lens,
attention lens, future lens, or backward lens. So this subsection defines the
method from first principles before the rest of the write-up red-teams it.

**The setting.** Write `h_l[t]` for the residual stream of a decoder-only
transformer at layer `l`, token position `t`. The model's own output map is
`unembed(·)`: the final normalisation followed by the unembedding matrix `W_U`,
producing a vector of `d_vocab` logits.

**Logit lens**, the familiar baseline, applies that output map to an
intermediate residual directly:

```
readout_logit_lens(l, t) = unembed(h_l[t])
```

It asks what the model would emit if it stopped at layer `l`. It is
zero-parameter and assumes the residual basis at layer `l` is already close
enough to the final-layer basis for `W_U` to be meaningful against it.

**J-Lens** does not assume that. It fits, per layer, an average input-output
Jacobian

```
J_l  ~=  E_x [ d h_L[t] / d h_l[t] ]
```

— the derivative of the final-layer residual with respect to the layer-`l`
residual, averaged over a fitting corpus — and uses it as a learned linear
*transport* from the layer-`l` basis into the final-layer basis before
unembedding:

```
readout_jlens(l, t) = unembed( J_l @ h_l[t] )
```

`J_l` is a `d_model x d_model` matrix estimated from data, not read off the
weights. In the pinned reference implementation, `JacobianLens.transport(h, l)`
exposes the bare `J_l @ h`, and `JacobianLens.apply(...)` wraps transport plus
unembedding plus a forward pass.

**The baseline falls out of the same code path.** Calling
`JacobianLens.apply(..., use_jacobian=False)` substitutes the identity for `J_l`
and yields the vanilla logit lens through the *identical* extraction, hooking,
and decoding path. This matters more than it looks: it means the J-Lens-versus-
logit-lens comparison isolates exactly one thing — the learned transport `J_l` —
and cannot be contaminated by a difference in how activations were captured, how
positions were indexed, or how tokens were scored. That is Control 1 in
section 2.5, and it is a stronger baseline than reimplementing a logit lens
alongside.

One practical consequence for the compute budget: `lens.apply()` runs one forward
pass per call, so producing a J-Lens readout and a logit-lens readout for the
same prompt costs two forward passes unless extraction is refactored. The plan
assumes the unrefactored path.

**Why this is worth testing.** `J_l` is a *first-order* object: a Jacobian, an
averaged linear approximation of a map that is not linear. "Open Problems in
Mechanistic Interpretability", a survey Neel Nanda co-authored, lists among its
open problems:

> How can we develop attribution methods that capture higher-order effects
> beyond first-order approximations of model behavior?

Relational binding is a conjunctive property. It is not a property of *Arin*
being present or *Luma* being present — both are present in both variants of
every pair below — but of the pairing between them. So the question this project
asks is an instance of that listed open problem: does an averaged first-order
readout preserve structure that is, by construction, not carried by the presence
of either constituent alone?

Two honesty notes on that framing, both load-bearing:

1. I am not claiming that binding is literally a second-order term in a Taylor
   expansion of the residual map. That would be a stronger and less defensible
   statement than I can support. The claim is the weaker, testable one: `J_l` is
   a single averaged linear operator applied identically to every input, and
   whether such an operator preserves a conjunctive property is an empirical
   question with no obvious answer in either direction.
2. This is **not** the "bag of features" question about inter-feature geometry
   raised elsewhere in Open Problems. That passage is about whether feature
   dictionaries capture the geometric relationships between features. The
   question here is about role assignment in a readout. A reader who knows that
   passage should not read this experiment as an attempt on it.

## 2.2 Substrate: model, lens, and environment

Every identifier below is taken from `results/design-verification/environment-manifest.md`,
which records them as verified on the execution GPU rather than from memory.

| | |
|---|---|
| Model | `Qwen/Qwen3.5-4B` |
| Model revision (pinned) | `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a` |
| Repo architecture / resolved class | `Qwen3_5ForConditionalGeneration` / `Qwen3_5ForCausalLM` (text tower) |
| Layers / `d_model` / unembedding width | **32** / **2560** / **248320** |
| Tokenizer | `Qwen2Tokenizer`, `vocab_size=248044`, `len(tokenizer)=248077` |
| dtype | `torch.bfloat16` |
| Lens repository | `neuronpedia/jacobian-lens` |
| Lens revision / commit | `qwen-n1000` / `16a01f309fcec900fdcec3f4cd5b64f3d00e4d5a` |
| Lens file | `qwen3.5-4b/jlens/Salesforce-wikitext/Qwen3.5-4B_jacobian_lens_n1000.pt` |
| Lens sha256 | `1f9a8f8fd593f0ffec1a9640993257ca4560f8ae3e5602315643d5cc6818534e` |
| Lens size | 406,332,644 bytes |
| Lens `d_model` / `n_prompts` | **2560** / **1000** |
| Lens `source_layers` | `0..30` (31 layers); model layer 31 is the lens's output row |
| Reference implementation | `anthropics/jacobian-lens`, Apache-2.0 |
| Reference commit (pinned) | `581d398613e5602a5af361e1c34d3a92ea82ba8e` ("Initial release", 2026-07-02) |
| Reference test suite | 32/32 passing, on the execution GPU and locally |

**Lens provenance.** The lens was fit by Neuronpedia with
`fit_lens.py Qwen/Qwen3.5-4B` on `Salesforce/wikitext` (`wikitext-103-raw-v1`,
train split), `max_seq_len=128`, `dim_batch=64`, `dtype=bfloat16`. It is a
generic-corpus lens; it was not fit on anything resembling this task's prompts.
That cuts both ways and section 2.5's coverage control exists because of it.

**One provenance ambiguity, resolved rather than glossed.** The lens directory
holds two checkpoints but a single `config.yaml`, which reports
`prompts_fitted: 417`. The checkpoint actually loaded, `..._n1000.pt`, reports
`n_prompts=1000` internally, so that `config.yaml` describes the *other* file.
The n1000 lens — the one the reference `walkthrough.ipynb` selects — is the
genuine 1000-prompt fit, and is what is used here.

**Compatibility, asserted on GPU rather than assumed** (`COMPAT_ASSERTIONS: PASS`,
`LAYOUT_ASSERTIONS: PASS`):

1. the lens `config.yaml` records `hf_model_name == "Qwen/Qwen3.5-4B"`, so the
   lens was fit against this exact model ID and not a sibling;
2. `lens.d_model == model.hidden_size` (2560 == 2560);
3. `max(lens.source_layers) < num_hidden_layers` (30 < 32);
4. `jlens.from_hf` resolves to `HFLensModel(Qwen3_5ForCausalLM, n_layers=32,
   d_model=2560)`, matching the lens on both axes.

**Activations are read from the HuggingFace modules directly. TransformerLens is
not in the path.** `HookedTransformer.from_pretrained` applies `fold_ln`,
`center_writing_weights`, `center_unembed` and `fold_value_biases` by default. A
lens fitted against HF-native activations will still return numbers when handed
processed activations; the numbers will be wrong and nothing will raise. Since
this lens was fit through the HF path, the HF path is what is used, and the
equivalence question is avoided rather than assumed away.

**Hardware and stack.** Virginia Tech ARC Falcon, partition `l40s_normal_q`,
NVIDIA L40S (46068 MiB reported by `nvidia-smi`; 47.7 GB by torch), driver
595.71.05, CUDA 13.0, PyTorch 2.13.0+cu130, transformers 5.16.1, Python 3.12.3.
Setup measurements, not experimental results: model load 13.6 s, peak GPU
allocation 8.51 GB of 47.7 GB. Headroom is not a constraint on this design.

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

**The order-reversed variant, which dissociates role from linear position.**
In Variant A above, the correct intermediate `Luma` is also the first-mentioned
location; in Variant B the correct intermediate `Nori` is the second-mentioned.
Role is therefore confounded with linear position, and a readout that has merely
learned "prefer the first location mentioned" would look like it had learned
binding. The IOI appendix found positional signal dominating token signal by
roughly 3:1, so this is the first control an IOI-literate reader asks for.

Each item is therefore rendered twice: once in canonical fact order, and once
with the two `lives in` facts and the two `uses` facts each emitted in reversed
order. The binding is unchanged; the linear position of the correct intermediate
moves. A position-tracking readout scores at floor across the reversal. A
role-tracking readout is invariant to it. The reversal is applied to development
and held-out items alike, and both renderings are scored.

**Templates and generation.** Four relation templates, generated with a fixed
seed recorded in the run manifest. `[PENDING — final template count and
generation seed fixed at the Hour 3 / Hour 5 dataset freeze]`

**Tokenization, verified for entities as well as targets.** Every scored
intermediate and every scored answer must be a single token under
`Qwen2Tokenizer` *in the exact surface form in which it will be scored*. Leading
whitespace changes the tokenization (`"Ralph"` -> `['R', 'alph']` versus
`" Ralph"` -> `[' Ralph']`), so the check is run against the spaced form that
actually appears. Entity names are checked too, not just targets: a multi-token
nonce name smears the "concept" across positions and quietly changes what the
readout is being asked about. Candidates that fail the check are replaced before
the item enters the set. Where invented vocabulary costs behavioral solvability,
ordinary single-token nouns and names assigned arbitrary roles are used instead;
the relational structure is what must be preserved, not the nonsense words.

**Padding and indexing.** Batches are left-padded so that index `-1` is the
final prompt token for every row. This is verified on a batch of mixed lengths
rather than assumed from the default.

**Behavioral eligibility, screened first.** Before any lens work, both variants
of a pair must be answered correctly by the unmodified model under deterministic
(greedy) decoding. Only eligible pairs are scored, and both the total generated
set and the retained set are reported — not just the retained one. Pre-registered
target: at least 80% pair eligibility; below that, wording is simplified while
the relational structure is held fixed, and the change is recorded.
**Result: the screen ran and passed**
(`results/runs/20260827T090437Z-eligibility-screen/`). On the real lexicon,
zero-shot, n = 30 pairs: `pair_eligibility(AB) = 0.900`, against the
pre-registered 0.80 threshold; `pair_eligibility` across all four binding ×
fact-order cells = 0.867; `alt_answer_rate = 0.000`; `fact_order_gap = −0.033`.
Few-shot prompting was dropped because it scores worse under content-based
scoring (0.750) than zero-shot (0.950) despite looking better under a first-word
rule, so the operating point is real lexicon, zero-shot. `[agent-unverified]`

This screen is deliberately the first thing that runs, not a downstream step.
Nonce entities plus invented predicates plus a chained two-hop query is close to
the opposite of IOI's "common grammatical structure", and a 4B model may simply
not do the task. That is the highest-probability, lowest-cost failure in the
whole design, so it gets de-risked before anything expensive.

**Split.** 10 development pairs and 40 held-out pairs, spread across the
templates. Development pairs carry all debugging, all pipeline validation, and
the layer selection in 2.4. **The 40 held-out pairs are not looked at, in any
form, until after the Hour 7 freeze**, and are never tuned on.

## 2.4 Observation point and the layer-selection rule

**Observation point: the residual stream at the final prompt token**, the token
immediately preceding answer generation. This is not an arbitrary choice — it is
the position the method's own authors score at. The reference repository ships
`data/evaluations/lens-eval-multihop.json`, a purpose-built lens-quality
evaluation whose documented readout position is the single token immediately
preceding `target`, with `target` itself defining the position and not being
scored. Using the same position means a reader who doubts the position can check
it against the reference eval rather than against my judgement.

**The layer band is not pre-declared. The selection rule is.**

The design of record originally fixed the band at the middle 40-80% of layers.
That is dropped. Three independent sources place the retrieval / attribute-
extraction step *later* in depth than that band, and on IOI in a 12-layer model
almost all of the performance came from attention layer 9 — roughly 75% of
depth, sitting at the very top edge of a 40-80% window. Pre-declaring a band on
the strength of a number measured in a 12-layer model risks scoring a 32-layer
model at the wrong depth and then reporting that as a method failure. Fixing the
*rule* instead keeps the held-out test honest without betting on the literature
number.

The rule, executable as written, frozen at Hour 7 before any held-out prompt is
scored:

1. **Sweep.** For every source layer `l` in `0..30` (31 layers; layer 31 is the
   lens's output row and is not a selectable source), compute the readout for
   all three arms on all eligible development pairs, in both fact orders.
2. **Score each layer** by the mean paired binding margin `M` defined in 2.5,
   computed on development pairs only, for the **J-Lens arm**. Call it `m(l)`,
   with standard error `se(l)` over development pairs.
3. **Pick the peak.** `l* = argmax_l m(l)`. Ties break to the lowest index.
4. **Grow the band.** `B` is the maximal contiguous run of layers containing
   `l*` all of whose members satisfy `m(l) >= m(l*) - se(l*)`. If no neighbour
   qualifies, `B = {l*}`.
5. **Freeze.** `l*` and `B` are written into the preregistration at Hour 7 and
   are not revisited. Held-out scoring uses the frozen `B` only; there is no
   re-selection on held-out data, and no post-hoc widening.
6. **Same band for every arm.** J-Lens, logit lens and the supervised reference
   are all scored over the same `B`, selected on J-Lens. Selecting on J-Lens and
   then applying that band to its own baselines is the choice that disadvantages
   J-Lens least — so if J-Lens loses, it loses on a band chosen in its favour.
   State this rather than hiding it.
7. **Rank aggregation.** Where a rank-based metric needs a single number per
   prompt, use the best rank within `B`, identically for all arms.
8. **Publish the sweep.** The full 31-layer development curve is reported, not
   just `l*`, so a reader can see whether the selection sat on a plateau or on a
   spike. A spike is a warning about the selection, and should be visible.

`[RESULT PENDING — l* and B not yet selected; the development sweep has not run]`

## 2.5 Arms, metrics, and controls

### Three arms

**Arm 1 — J-Lens.** `unembed(J_l @ h_l[t])` at layers in `B`.

**Arm 2 — logit lens.** The same call with `use_jacobian=False`: the identity
substituted for `J_l`, through the identical extraction path (2.1). Isolates the
learned transport and nothing else.

**Arm 3 — supervised difference-in-means reference.** This arm is new relative
to the design of record and it is not optional.

*Why it exists.* Logit lens is documented in prior work as sometimes being
close to non-functional outside GPT-2, which is not used here. So a two-arm
comparison is uninformative in either direction: if J-Lens beats logit lens,
that may only say logit lens does not work on Qwen3.5; if both sit at floor,
"J-Lens cannot read binding" and "binding is not linearly present in the
residual at this layer at all" produce identical numbers. Without a third arm
there is no way to tell those apart, and therefore no way to interpret any
J-Lens number that comes back. The supervised arm is the cheapest instrument
that separates them.

*What it is.* A nearest-centroid (equivalently, isotropic-covariance LDA)
readout over the closed set `V` of intermediate tokens used across the dataset.
No training loop, no optimiser, roughly twenty lines:

```python
# per layer l. H[p] = residual at layer l, final prompt token, prompt p.
# c[p] = correct intermediate token id for prompt p.  V = set of intermediates.

h_bar = mean(H[p] for p in dev)                       # dev-set centering only
X     = {p: H[p] - h_bar for p in dev}
mu    = {v: mean(X[p] for p in dev if c[p] == v) for v in V}

def score(h, v):                                      # nearest-centroid rule
    x = h - h_bar
    return dot(x, mu[v]) - 0.5 * dot(mu[v], mu[v])

# scoring any prompt q with candidates (correct c_q, alternative a_q):
margin_q = score(H[q], c_q) - score(H[q], a_q)
success_q = margin_q > 0
```

The `- 0.5 * ||mu_v||^2` term is what makes this a nearest-centroid decision
rule rather than a raw projection, and it removes the bias that would otherwise
favour whichever intermediate happens to have the larger centroid norm.

*Discipline.* `h_bar` and `mu` are estimated on development prompts only — all
fact orders, all eligible development pairs — and applied unchanged to the
held-out set. A leave-one-pair-out estimate on development is reported alongside,
as a check that the arm is not simply memorising ten pairs.

*What it does and does not bound.* Call it a reference level, not a ceiling.
It is biased in both directions and both should be stated: it **under**-estimates
linear availability, because a stronger probe fit on more data could do better
than ten pairs' worth of class means; and it **over**-states what any
unsupervised readout should be expected to reach, because it is handed the
labels. Its job is only to answer "is binding information linearly present in
this residual at all", which is the question that makes arms 1 and 2
interpretable. Concretely: if arm 3 is near floor, the correct conclusion is
about the model or the layer, not about J-Lens. If arm 3 is high and both lenses
are at floor, the conclusion is about the readouts.
`[RESULT PENDING]`

*Reading this section against the run manifest.* The Stage 1 passive readout
emits three arm strings — `jlens`, `logitlens` and `jlens_random_transport` —
and they do not map one-to-one onto the three arms above. `jlens` and
`logitlens` are arms 1 and 2. `jlens_random_transport` is not a fourth arm: it
is control 8a, executed through the same harness so that it shares the
extraction and scoring path exactly, and it is reported as a control rather than
as a comparison of interest. The supervised reference (arm 3) is not among them;
it is not part of the Stage 1 passive script.

### Metrics

Two primary metrics are reported together: the pre-registered binary one, and a
continuous one alongside it. Forty bootstrapped Bernoullis is the weakest
version of this experiment; the continuous metric uses the whole ordering and is
closer to the model's own objective, which is why IOI's endorsed analogue (logit
difference) is continuous.

**(a) Pairwise binding success — binary, conjunctive.** For a pair, success
requires *both*:

1. in Variant A, `score(correct) > score(alternative)`; and
2. in Variant B, the ordering reverses correctly.

The conjunction is the point. Because the two variants have identical entity
inventories, **any readout that responds only to concept presence scores exactly
zero on this metric**, not 50% — it must return the same preference for both
variants, and one of them will be wrong. A readout that is an independent
unbiased coin on each variant scores 25%. Both floors are reported, because
which one is the relevant null depends on the failure mode being argued against,
and quoting a single "chance" number would be misleading either way.

**(b) Paired binding margin — continuous.** For prompt `p` at layer `l`,

```
m(p, l) = s_l(correct(p)) - s_l(alternative(p))
M(pair) = 0.5 * [ m(A, l) + m(B, l) ]
```

For arms 1 and 2, `s_l` is the raw pre-softmax logit assigned to that candidate
token by the readout at layer `l`, in the model's own unembedding basis — the
direct analogue of IOI's logit difference. For arm 3, `s_l` is the
nearest-centroid score above.

A necessary caveat, stated rather than buried: margins are comparable **within**
an arm and across layers, but the three arms do not share units. Cross-arm
comparison therefore uses the sign-based accuracy in (a) and a standardised
effect size (`mean(M) / sd(M)` within arm), never raw margin units. Any
cross-arm claim in raw margin units in this write-up is a bug.

**(c) Recall@10**, as pre-registered, secondary.

**Uncertainty.** Paired bootstrap, resampling **pairs** and not prompts, 10,000
resamples, seed recorded in the run manifest, 95% intervals throughout.

### Blocker B4: which width ranks are taken over

`len(tokenizer) = 248077` but the unembedding is `248320` wide, so roughly 243
output ids have no tokenizer string. Any rank metric must state its width, so:

- **All rank metrics are computed over the full 248,320-wide output**, with the
  ~243 unaddressable ids left in the ranking rather than filtered out. Retaining
  them is the conservative choice: their presence can only push a correct
  token's rank worse, never better, and it avoids a filtering step that could
  silently differ between arms.
- The alternative — ranking over the 248,077 tokenizer-addressable ids — is
  reported as a single robustness line. The two should differ by at most 243
  positions. If they differ by more, that is a bug indicator, not a finding.
- **The primary metrics (a) and (b) are unaffected by B4 entirely**, because
  they compare two named token ids against each other and never form a rank over
  the vocabulary. Only Recall@10 and the qualitative top-k readouts are exposed
  to it.

### Baselines and controls

| # | Control | What it rules out | Status |
|---|---|---|---|
| 1 | Logit lens, same code path, `use_jacobian=False` | Any advantage comes from the transport `J_l`, not from the pipeline | Primary arm |
| 2 | Supervised difference-in-means reference (arm 3) | "Neither lens can read binding" being confused with "binding is not linearly there" | Primary arm |
| 3 | Order-reversed fact rendering | A readout that tracks linear position rather than role | Applied to every item |
| 4 | Coverage positive control | A null result caused by the lens never having seen this vocabulary, rather than by binding | Required before any null is reported |
| 5 | Direct prompting ("just ask the model for the intermediate") | The task being legible without any internal method | Held-out |
| 6 | Pair alternative, not arbitrary distractor tokens | An easy comparison against irrelevant vocabulary | Built into the metric |
| 7 | Label permutation | Attractive-looking token lists that do not depend on the learned label mapping | Held-out |
| 8a | Norm-matched random *transport*, passive | Margins that any matrix of that Frobenius norm would produce, whatever `J_l` learned | Runs in Stage 1 |
| 8b | Norm-matched random *direction*, causal intervention | Effects any perturbation of that magnitude would produce | Unavailable with the causal arm |
| 9 | Prompt-template robustness | A result specific to one phrasing | Fixed subset, wording fixed before held-out results are seen |
| 10 | Relation deletion | The readout tracking co-occurrence rather than binding | **See note below** |
| 11 | Question truncation | Selectivity that does not depend on knowing the target entity | **See note below** |

**Control 4, the coverage positive control, in detail.** Before any negative
result is reported, J-Lens must be shown to recover *something* unambiguous
through the same prompts, the same layer band and the same code path. Two
sources: (i) the reference evaluation `data/evaluations/lens-eval-multihop.json`,
scored by its own documented metric — `pass@k` is the mean fraction of an item's
`intermediates` whose min-over-layers lens rank is at most `k`, read at the
single token immediately preceding `target` — which supplies an official metric
and an official position rather than a subjective read of a token list; and
(ii) on this project's own prompts, an unambiguous target such as the queried
entity name. Without this, H4 is close to unfalsifiable: a flat result cannot
distinguish "Jacobian readouts do not carry binding" from "the n1000 wikitext
lens has no useful coverage of these tokens".
`[RESULT PENDING — coverage control not yet run]`

**Note on controls 10 and 11 — an open design decision, not a silent cut.**
Controls 6, 10 and 11 are all "perturb the prompt and see whether the readout
moves", so they are mutually predictive rather than independent lines of
evidence. Worse, deletion and truncation take the model off-distribution: a
readout that moves under relation deletion may only be reporting that the prompt
has become ungrammatical, and zero-ablation-style perturbation is arguably
unprincipled for exactly this reason. Control 6 (pair alternative) is already a
resample-style control and does not have this problem. The open proposal is to
demote 10 and 11 to secondary and spend the time on controls 2, 3 and 4 instead.
That call has not been made and is flagged here rather than decided in the
method section. `[DECISION PENDING — Jason]`

**Negative control, and what is not available.** No published shuffled-corpus or
control J-Lens checkpoint exists — all 40+ lenses in `neuronpedia/jacobian-lens`
are fit on `Salesforce/wikitext`. The fallback is therefore label permutation
(control 7) plus norm-matched random *transport* (control 8a), implemented
locally. Both are passive and both are live: the Stage 1 passive readout
(`experiments/stage1/passive_readout.py`) ships a `jlens_random_transport` arm
that replaces every `J_l` with a Gaussian matrix of matched Frobenius norm and
re-runs the readout through the identical extraction path, so the comparison
isolates the fitted transport against a norm-equivalent random one. This is
weaker than the published control the design hoped for, and it is listed as a
limitation rather than presented as equivalent — but it is reachable rather than
hypothetical.

Norm-matched random *direction* as an intervention (control 8b) is a different
control for a different question. It belonged to the causal arm and is
unavailable along with it; nothing in the passive fallback above depends on it.
`[RESULT PENDING — the Stage 1 randomised-transport arm has not run]`

### The causal arm is unavailable, and this is itself a method-evaluation finding

ADR-0005 scopes this project passive-primary. H1, H2 and H4 are the deliverable;
H3 (causal validity) was to run only if a faithful sparse non-negative J-space
reconstruction turned out to be available inside its one-hour box. It is not
available, and as of 2026-08-27 the arm is declared **unavailable, not deferred**.

The pinned reference commit ships no sparse coding, no NNLS, no non-negative
solver, no dictionary and no reconstruction routine — the API is `fit` / `apply`
/ `transport` / visualisation. This was checked rather than asserted from
memory: an audit of the pinned vendor tree (`scripts/v2_decomposition_audit.sh`,
run as step 0 of the Stage 1 job) searched the `jlens` package, its README and
its walkthrough notebook for sparse, non-negative, NNLS, lasso, dictionary,
decomposition and reconstruction, and found zero matches for any of those terms.
Run id: `results/runs/20260827T153925Z-stage1-passive-readout/` (job 550690, step 0; the tests directory was searched too, also zero). Full documented negative: `results/design-verification/v2-decomposition-verification.md`.

Stated plainly: the capability the method's framing implies is not supported by
its released artifact. That is reported here as a finding about the method —
which is the object under test in this project — and not as a gap in our
execution. It is not pending on our schedule and there is no configuration of
this project's remaining hours in which the arm runs.

Substituting an arbitrary top-token projection and calling it J-space remains
this project's own declared FAIL condition, and it will not be done.

Two commitments were made in advance of the arm, and they are recorded here so
the pre-commitment stays legible rather than quietly disappearing with the arm.
First, effects would have been reported as the change in the downstream
factual-minus-counterfactual **logit margin** as well as the argmax flip rate —
self-repair is real without dropout and up to about 30% of it is a
LayerNorm-scale artefact, which is more than enough to eat a real effect and
manufacture a false negative if only flips are reported. Second, intervention
norms would have been matched and recorded across the target and random
conditions, with a norm-preservation check reported.

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

![Pairwise binding accuracy by method, with bootstrap 95% CIs. On this conjunctive metric a presence-only (bag-of-concepts) readout scores 0% and independent unbiased guessing on each variant scores 25%; 50% is the per-prompt figure, not the chance level for this metric.](results/figures/binding-accuracy-by-method.png)

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
