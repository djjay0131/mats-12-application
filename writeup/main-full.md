# Randomly selected raw examples

<!-- Neel asks for these "ideally just after the executive summary", and names
     cherry-picking as a major red flag. Selection must be by seed, and the
     seed must appear in the text (BLK-10 checks for it).

     Include: 2 successes, 2 failures, and 1 case the pipeline scored as
     ambiguous. Show the full prompt, the top-k J-Lens readout, the logit-lens
     readout, and the model's answer. Raw. Do not clean them up. -->

Examples below are drawn with `seed=1337` from the held-out set; they are
randomly selected, not chosen.

Selection rule, stated before the draw: among the 200 held-out records, a
*success* is a record whose J-Lens intermediate margin at `relcomp` is
positive, a *failure* one where it is negative; two of each are drawn with
`random.Random(1337).sample` over record ids in sorted order, and the fifth
example is the single closest call (smallest absolute `relcomp` margin,
deterministic, no draw). The pipeline stores candidate ranks and margins,
not full top-k token dumps, so the readout columns below are ranks of the
correct and role-swapped intermediate in each lens vocabulary readout; a
top-k dump would need one further GPU pass and is listed in Section 8. The
generations for the first records of each split are in the eligibility run
outputs, keyed by `record_id`. All numbers agent-derived from the committed
run output; agent-unverified.

### Example 1 — success (`real-zero-035-BBA`, T6)

> Facts: Clara paints at Bristol. Anna paints at Seattle. Bristol stores granite. Seattle stores bronze. What is stored where Anna paints? Answer:

Correct intermediate **Seattle** -> answer **bronze**; role-swapped alternative Bristol -> granite.

| position | J-Lens margin | J-Lens rank (corr/alt) | logit-lens margin | logit-lens rank (corr/alt) | model (shadow) margin |
|---|---|---|---|---|---|
| prequery | -0.562 | 1050 / 622 | -0.764 | 172929 / 123042 | -1.062 |
| relcomp | +0.188 | 256 / 279 | +0.203 | 1233 / 1687 | +0.625 |
| qmark | +7.375 | 62 / 3315 | +7.578 | 40 / 56275 | +5.625 |
| final | +0.688 | 24 / 40 | +3.719 | 15 / 229 | +2.312 |

### Example 2 — success (`real-zero-047-ABA`, T6)

> Facts: Victor paints at Dublin. Simon paints at Seattle. Seattle stores wool. Dublin stores rubber. What is stored where Simon paints? Answer:

Correct intermediate **Seattle** -> answer **wool**; role-swapped alternative Dublin -> rubber.

| position | J-Lens margin | J-Lens rank (corr/alt) | logit-lens margin | logit-lens rank (corr/alt) | model (shadow) margin |
|---|---|---|---|---|---|
| prequery | +0.875 | 55 / 119 | -0.967 | 109750 / 51197 | -0.188 |
| relcomp | +4.156 | 106 / 1502 | +3.609 | 255 / 26145 | +3.500 |
| qmark | +6.531 | 26 / 718 | +4.938 | 49 / 6785 | +2.188 |
| final | +4.625 | 3 / 13 | +3.125 | 6 / 37 | +1.312 |

### Example 3 — failure (`real-zero-035-BAB`, T6)

> Facts: Anna paints at Seattle. Clara paints at Bristol. Bristol stores granite. Seattle stores bronze. What is stored where Anna paints? Answer:

Correct intermediate **Seattle** -> answer **bronze**; role-swapped alternative Bristol -> granite.

| position | J-Lens margin | J-Lens rank (corr/alt) | logit-lens margin | logit-lens rank (corr/alt) | model (shadow) margin |
|---|---|---|---|---|---|
| prequery | -0.094 | 240 / 203 | -0.791 | 156057 / 103212 | +0.125 |
| relcomp | -0.688 | 162 / 121 | -0.625 | 473 / 230 | -0.125 |
| qmark | +0.312 | 370 / 440 | +2.312 | 256 / 3638 | +1.875 |
| final | +1.062 | 12 / 18 | +3.688 | 13 / 109 | +2.312 |

### Example 4 — failure (`real-zero-023-BBA`, T6)

> Facts: Alice paints at Bristol. Anna paints at Athens. Bristol stores rubber. Athens stores linen. What is stored where Anna paints? Answer:

Correct intermediate **Athens** -> answer **linen**; role-swapped alternative Bristol -> rubber.

| position | J-Lens margin | J-Lens rank (corr/alt) | logit-lens margin | logit-lens rank (corr/alt) | model (shadow) margin |
|---|---|---|---|---|---|
| prequery | +0.062 | 79 / 84 | +0.789 | 19343 / 47560 | -3.438 |
| relcomp | -0.500 | 416 / 293 | -0.188 | 1365 / 1057 | -0.562 |
| qmark | +7.500 | 57 / 4011 | +7.453 | 26 / 32028 | +4.438 |
| final | +2.250 | 20 / 49 | +2.625 | 3 / 22 | +0.375 |

### Example 5 — closest call (`real-zero-038-ABA`, T3)

> Facts: Sarah studies at Athens. Iris studies at Bristol. Bristol teaches linen. Athens teaches timber. What is taught where Iris studies? Answer:

Correct intermediate **Bristol** -> answer **linen**; role-swapped alternative Athens -> timber.

| position | J-Lens margin | J-Lens rank (corr/alt) | logit-lens margin | logit-lens rank (corr/alt) | model (shadow) margin |
|---|---|---|---|---|---|
| prequery | +0.438 | 47 / 77 | +0.371 | 41353 / 59422 | -0.250 |
| relcomp | +0.000 | 143 / 143 | -0.094 | 321 / 284 | +0.125 |
| qmark | +5.375 | 95 / 1576 | +0.844 | 139 / 299 | +1.500 |
| final | +5.625 | 14 / 245 | +1.188 | 10 / 18 | +1.875 |


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

## 1.2 What binding is and why a lens struggles to see it

<!-- Inserted from writeup/drafts/binding-section-draft.md (2026-08-29 coach
     draft), updated 2026-09-03 for the Stage 3 result. Per the draft's own
     STATUS note: rewrite in your voice; keep the structure and numbers. -->

The question this project asks is not whether the model represents Paris. It is
whether the model represents *Paris-as-the-city-attached-to-Arin* — and whether
an unsupervised readout can see the difference.

The distinction is the classic binding problem. Two prompts —

> Arin lives in Paris. Bela lives in Tokyo.
> Arin lives in Tokyo. Bela lives in Paris.

— contain exactly the same four concepts: Arin, Bela, Paris, Tokyo. A readout
that only detects which concepts are present cannot tell these prompts apart.
What differs is the pairing, and the pairing is the binding (Figure below).
This is why every record in the dataset carries a role-swapped twin: both
cities are in the context, equally salient, so a bag-of-concepts readout scores
exactly chance (frac = 0.500) by construction, and only a readout that has
recovered the relation can beat it. The distractor is the experiment.

![The binding problem: two prompts, the same four concepts, opposite pairings. Only the pairing distinguishes them, so only a reader of the relation can tell them apart.](results/figures/binding-concept/fig1-binding-problem.png)

Binding is structurally awkward for a lens. A lens maps a residual vector to a
ranking over the vocabulary, and vocabulary items are identities — there is no
token that means "the-city-attached-to-Arin." A token-ranking instrument can
therefore only express a binding indirectly, by ranking Paris above Tokyo, and
it can only do that once the model has resolved the relation into a selection.
That yields a three-phase account of the forward pass at the readout positions
(Figure below):

1. **Before the query** (the prequery position): both bindings are stored,
   neither is selected. "Correct intermediate" is undefined — it is a property
   of the query, which has not been seen. Chance is the correct expected value
   here, and a directional readout above chance would indicate a leak, not
   binding. This is the reframe of the Stage 2 prequery result: frac 0.550 is
   the control passing, not the lens failing.
2. **During the query** (query onset to the final token): the model resolves
   which binding the question selects. This is the only span where a binding
   could be determined but not yet emitted — the only place a token-ranking
   readout could, in principle, see a binding rather than an output.
3. **At the final token**: the answer is computed. The model's own output
   distribution already prefers the correct intermediate on 92.5% of records,
   so a directional readout here is dominated by the output shadow (Stage 2:
   J-Lens final-position margin couples to the model's own intermediate margin
   at r = 0.771 against a shadow anchor of 0.811).

![Where a binding is visible to a token-ranking readout: stored before the query, resolving inside the query window, emitted at the final token. The readout positions used in Stage 3 are marked.](results/figures/binding-concept/fig2-where-binding-is-visible.png)

Stages 1 and 2 of this project measured phases 1 and 3 — the two phases where,
for opposite reasons, a directional binding readout is uninformative. Stage 3
(Section 4.2) read phase 2 at frozen settings, with a supervised
difference-in-means probe on the same grid as a ceiling. The measured answer,
stated here so the three-phase account is not left implying an untested
prediction: on this task phase 2 is not shadow-free either. The model's own
next-token preference is already directional inside the query window (frac
0.800 at the relation-completing token, 0.731 at the question mark), both
lenses track it at r = 0.88–0.92, and the supervised ceiling reads chance
(0.525) at the relation-completing token — so the window carries the model's
developing selection, not a linearly decodable stored binding. The three-phase
account survives; the hoped-for shadow-free middle band, on this task, does
not.

## 1.3 The gap

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

**Result, and a deviation stated.** The implemented pipeline applies steps 1-3
and 8 of this rule — per-position argmax of the mean paired intermediate margin
on dev, full 31-layer curve published in every run record — and does **not**
implement the band-growth of steps 4-7: scoring is at the single selected layer
per position. This is a simplification of the written rule, made before any
held-out contact and applied identically to every arm; it is recorded here
rather than silently reconciled. Selected layers, identical on both clusters at
every position carrying signal, frozen in `experiments/stage3/freeze.json`:
J-Lens L30 at the relation-completing token, L27 at the question mark, L27 at
the final token, L25 at prequery; logit lens L30/L29/L30/L24. At positions
where every layer's margin is ~0.005 the argmax selects noise and a different
GPU rounds to a different layer (q00: L29 vs L28 across clusters, median rank
swinging 5,186 to 29,916) — a property of the rule where there is no signal,
visible because the full curve is published.

**The observation point evolved, under pre-registration, and the final token
did not survive as primary.** Verification showed the final prompt token is
output-contaminated (38/40 dev generations name the intermediate; §4.2), and
the pre-query token precedes the question naming a subject, so no entity is yet
the correct intermediate there — its chance-level direction score is the
control *passing*. A position sweep over the query window, with its decision
rule committed before submission (learning log, Hour 3), moved the primary
measurement positions to the **relation-completing token** and the **question
mark**, frozen by anchor in `results/stage2/FREEZE.md` before any code that
reads held-out was committed. The final and pre-query positions are retained
as the contaminated and undetermined references respectively.

## 2.5 Arms, metrics, and controls

![Three instruments on the same residual: the supervised difference-in-means probe as ceiling, J-Lens as the unsupervised reader, and the logit lens as floor.](results/figures/binding-concept/fig3-three-instruments.png)


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

**Result.** Arm 3 first returned an uninterpretable number (12 of 40 records
scorable: fourteen classes over ten pairs left nine classes with support in
only one pair, so leave-one-pair-out deleted their support), which forced the
shared six-word vocabulary now used by both splits — a dataset fix, recorded
as such. On the regenerated dev split it scores all 40 records
(leave-one-pair-out 0.625-0.650 at the final token across three GPU runs), and
in the frozen evaluation it transfers dev-fit to held-out unchanged:
**0.725 → 0.731 at the question mark** — which turned out to equal the model's
own next-token preference rate at that position exactly, and **0.525 at the
relation-completing token where J-Lens reads 0.781**. Both numbers turned out
to be load-bearing for the attribution in §4.2: the first says the linearly
decodable signal at the best position *is* the output preference; the second
says the residual there does not linearly separate the binding — what J-Lens
adds is its Jacobian, a linearization of the remaining computation.

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
| 10 | Relation deletion | The readout tracking co-occurrence rather than binding | **Cut** — off-distribution; a resample variant is offered instead, see note |
| 11 | Question truncation | Selectivity that does not depend on knowing the target entity | **Cut** — superseded by the pre-query readout position, see note |

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
**Result: PASS.** V1 ran the reference evaluation through the pinned lens and
code path at Gate 1 (jobs 550510/550548/550555, verdicts in
`results/slurm-logs/README.md`): 8/8 tooling checks pass, and on the reference
multihop eval J-Lens pass@10 = **0.350** against the logit lens's **0.200**
through the identical path — the lens demonstrably recovers *something*
through these tokens and this machinery, so the null results elsewhere in this
report are not a coverage artifact. The lens argmax differs from the logit
lens argmax at 29/31 layers, confirming the transport is live.

**Note on controls 10 and 11 — cut, with the reasoning stated.** Decision taken
2026-08-27. Both were planned and neither was run; they are cut on methodology,
not dropped after an inconvenient number.

Three reasons.

*They are not independent evidence.* Controls 6, 10 and 11 are the same move —
perturb the prompt, see whether the readout follows. They largely predict one
another, so running all three buys far less than three controls' worth of
confidence.

*Deletion and truncation take the model off-distribution.* Remove a fact
sentence and the prompt becomes incoherent. A readout that moves may only be
reporting that the prompt is now broken, not that the binding is gone. This is
the standard objection to zero-ablation-style perturbation and it applies
directly here. Control 6 scores against the pair's own alternative — a
resample-style control on an in-distribution token — and does not have the
problem.

*Control 11's question is already answered, better.* The pre-query readout in
§2.4 reads at the last token **before the query names a subject**. That is
question truncation performed positionally rather than by mutilating the prompt,
and it is fully in-distribution. Running control 11 as designed would be a
worse-instrumented rerun of a measurement already in hand.

*Correction (2026-08-29), kept alongside rather than rewritten away:* the
pre-query position turned out to answer a narrower question than this note
implies. Before the query names a subject, no entity is yet the correct
intermediate — so the pre-query readout measures **concept availability**
(median rank 346 against the logit lens's 78,525), not binding selectivity,
and its chance-level direction score is the control passing. The positional
form of control 11 stands; what it certifies changed. The post-query sweep in
§4.2 is the measurement that supersedes both.

**The honest objection, stated rather than avoided.** Control 10 is the one
control here that directly threatens the headline: if the readout tracked mere
co-occurrence of the entities rather than their binding, control 10 is what
would expose it, and cutting it removes a live threat to a positive result.
That is a real cost and it is not offset by the redundancy argument alone. What
is offered in its place is a **resample** variant rather than a deletion: swap
`Perth uses granite` for `Perth uses basalt` and require the readout to follow
the swap. Grammatical, in-distribution, and a sharper test of binding versus
co-occurrence than deletion would have been. It is listed as a limitation until
it runs, and the paired margin should not be read as excluding a co-occurrence
account until it does.

The time released goes to controls 2, 3 and 4.

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
**Result: the control behaves.** The randomised-transport arm is flat at
direction 0.475-0.537 (chance) at every position on both splits and every GPU,
with median rank of the correct intermediate ~130,000-206,000 of 248,320 —
against the fitted transport's 11-357 at its selected layers. Whatever the
fitted `J_l` does, a norm-matched random matrix through the identical code
path does none of it.

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

Each freeze is a commit that precedes the run it governs; the repository
history is the timestamp.

| Frozen thing | Where | When (commit) | Before |
|---|---|---|---|
| Dataset generator, seed 20260827, eligibility thresholds | `src/make_dataset.py` | pre-Gate-1 | any GPU run |
| Layer-selection rule (argmax on dev, publish full curve) | Hour 2 log entry | before Stage 1 submission | the dev sweep |
| Position-sweep decision rule (what would move the primary position, and what would not) | Hour 3 log entry, `7adaad1` | before the sweep job was submitted | the sweep |
| Positions (by anchor) and per-position layers | `results/stage2/FREEZE.md`, `experiments/stage3/freeze.json`, `c5e9a5a` | before any code that reads held-out existed (`62dc94b`) | the held-out read |
| Failure condition ("frac at both primary positions at/near control = forking paths, and that is the finding") | Hour 4 log entry, same commit | same | same |

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

The dev split's eligibility is **deterministic per GPU architecture and
reproducible within one**: 1.000 on every sm_8x-L40S/A30 run, 0.900 on every
A100 run, with the screen's own batched-vs-unbatched padding control moving 0/8
→ 2/8 mismatched on the same boundary. Greedy decoding turns last-bit
floating-point differences into different tokens; the same prompt flips the
same way every time on the same silicon. Eligibility percentages in this
report therefore always name the architecture. This is also control 5 from
§2.5 run at full scale: "just ask the model" solves the task at 90–100%, which
is precisely what makes a passive readout worth interrogating — the answer is
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
the randomised transport stays at chance.](results/figures/stage3-frac-by-position.png)

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
passive readout is wrong with it.](results/figures/stage3-discriminating-set.png)

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

Full 31-layer curves for every arm and position ship in the run records
(`results/runs/*stage1-passive-readout/`, `*stage3-heldout-frozen/`). Selected
layers sit inside the fitted range (final-token peak at L27, not at the L30
boundary), which is mild evidence the selection tracks computation rather
than the lens's edge. One indexing fact, caught by hand-verification and
confirmed from vendor source (`results/verification/readout-convention.md`):
lens layer *i* is the residual **after** block *i*, and this 32-block model's
final block is never read by either lens arm — L30 is the penultimate block.
Earlier drafts called L30 "the last layer"; corrected. The gap between the
logit lens at L30 and the model's own distribution therefore isolates the
final block in logit space: it adds ~11 points of direction at the
relation-completer (0.688 → 0.800) and nothing at the question mark
(0.738 → 0.731) — the final selection happens at the relation-completing
token and is finished by the question mark.

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
| 1 | The final-token "recovery" is the model's output leaking into the readout | Captured the model's own distribution in the same pass; hand re-derived (37/40, mean +2.77) | **True — headline retired**, §4.2a |
| 2 | The window positions were found by sweeping and are forking-paths artifacts | Decision rule committed pre-sweep; anchors and layers frozen pre-read; held-out read once | Ruled out: 0.781/0.669 vs control on 160 unseen records |
| 3 | The pre-query null means J-Lens "fails" | Realised the position precedes the subject being named; chance there is the control passing | Corrected in place, §2.5 |
| 4 | The window signal is the shadow again | Measured the preference at every position; built the discriminating set | **True** — below-chance on preference-wrong records; attribution goes to the preference |
| 5 | Layer indexing is off by one and "L30" claims are wrong | Independent rank re-derivation caught a mismatch; vendor source read line-by-line | True — L30 is the penultimate block; corrections dated in place |
| 6 | Numbers are GPU luck | Same commit on A30, L40S, A100 across two clusters; lens numbers replicate to ~5%, eligibility splits deterministically by architecture | Quantified; architecture named wherever eligibility is quoted |
| 7 | The label-permutation control is weakened by the six-word vocabulary | Collision audit: 65/160 disjoint | True — caveat attached to every held-out gap |
| 8 | Instrument bugs shape results | Three instrument failures occurred; all three invalid runs kept with NOTE.md, none cited | Recorded, `results/slurm-logs/README.md` |
| 9 | Preempted/orphaned runs contaminate the record | Preemption reconstructed from timestamps, noted per directory, nothing back-filled into manifests | Recorded |

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

Also real, in order of how much each should move a reader: one model, one
lens checkpoint, one language, synthetic six-word single-token prompts;
n=40 dev / 160 held-out; the held-out label-permutation control weakened by
vocabulary collisions (measured, §4.4); no published shuffled-corpus control
lens exists (B3), so the negative controls are label permutation plus local
norm-matched random transport; the resample variant of control 10 never ran,
so a co-occurrence account of the *rank* (not direction) results is
constrained only by the label permutation; and the causal arm is absent (B2),
so every claim here is correlational about the readouts.

---

# 8. What I would do next

Ordered: (1) **probe the construction site** — arm 3 at the fact tokens
(does "Prague"'s residual in "Helen lives in Prague" encode *Helen*?), one
job on the existing pipeline, the first position where binding must exist in
some form; (2) **activation patching between order-swapped twins** at the
frozen positions — the causal test of whether any single-position state
carries the binding, and the experiment that could prove existence where
passive readouts cannot; (3) the deferred stimulus-format test (ADR-0006) as
a robustness check on the shadow mechanism; (4) the published multi-token
template lens for the 27B model, since the single-token restriction bounds
everything here; (5) inside the final block, whose logit-space contribution
(§4.3) localises the final selection to one token.

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

Clock ruling (ADR-0005): wall-clock time, not summed agent-hours; parallel
agent work is bonus; environment setup, queue waits and bridge outages are
uncounted, and the second-cluster rebuild was ruled ARC setup. No Toggl record
exists; `llm/memory_bank/time-log.md` is the substitute and says so — each
block is marked Verified (artifacts at both ends) or Estimated.

| Bucket | Hours |
|---|---|
| Experiments, code, analysis (incl. Jason's independent verification) | 15.3 |
| Project-specific reading | 0.0 (literature scan predates the project lock; uncounted) |
| Write-up drafting (agent, this document) | 1.4 |
| **Total counted (limit 20)** | **16.7** — 7.1 verified, 9.6 estimated |
| Executive summary (separate +2 budget) | not started — Jason's prose |

---

# Appendix A — Additional figures

`results/figures/FIGURE-REGISTRY.md` is the registry of record: every figure
carries its sha256, generating commit and claim. The by-position sweep tables
(both clusters) are in `results/stage2/postquery-sweep-by-position*.txt`.

# Appendix B — Full result tables

Per-record scores, per-layer curves, shadow margins and the window/shadow
attribution tables are machine-readable in `results/runs/*/outputs/*.json`;
the analysis scripts that aggregate them (`experiments/analysis/`) run from a
cold interpreter against committed inputs only.

# Appendix C — Further raw examples

The first records of each split, verbatim, with generations, are in the
eligibility run outputs (`results/runs/*eligibility-screen/outputs/`); the
dataset files themselves are committed, so any example in this document can be
checked against its source line by `record_id`.
