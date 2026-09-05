# Randomly selected raw examples

Drawn with `seed=1337` from the held-out set — randomly selected, not
chosen. Rule, stated before the draw: a *success* has a positive J-Lens
`relcomp` margin, a *failure* a negative one; two of each drawn with
`random.Random(1337).sample` over sorted record ids, plus the single closest
call (smallest absolute margin, deterministic). Ranks and other positions
are in `writeup/main-full.md`. All numbers agent-derived; agent-unverified.

| # (record, T) | Prompt | Correct -> answer / swapped | J-Lens relcomp / qmark | logit lens relcomp / qmark | model relcomp / qmark |
|---|---|---|---|---|---|
| 1 success (`real-zero-035-BBA`, T6) | Facts: Clara paints at Bristol. Anna paints at Seattle. Bristol stores granite. Seattle stores bronze. What is stored where Anna paints? Answer: | **Seattle** -> **bronze** / Bristol -> granite | +0.188 / +7.375 | +0.203 / +7.578 | +0.625 / +5.625 |
| 2 success (`real-zero-047-ABA`, T6) | Facts: Victor paints at Dublin. Simon paints at Seattle. Seattle stores wool. Dublin stores rubber. What is stored where Simon paints? Answer: | **Seattle** -> **wool** / Dublin -> rubber | +4.156 / +6.531 | +3.609 / +4.938 | +3.500 / +2.188 |
| 3 failure (`real-zero-035-BAB`, T6) | Facts: Anna paints at Seattle. Clara paints at Bristol. Bristol stores granite. Seattle stores bronze. What is stored where Anna paints? Answer: | **Seattle** -> **bronze** / Bristol -> granite | -0.688 / +0.312 | -0.625 / +2.312 | -0.125 / +1.875 |
| 4 failure (`real-zero-023-BBA`, T6) | Facts: Alice paints at Bristol. Anna paints at Athens. Bristol stores rubber. Athens stores linen. What is stored where Anna paints? Answer: | **Athens** -> **linen** / Bristol -> rubber | -0.500 / +7.500 | -0.188 / +7.453 | -0.562 / +4.438 |
| 5 closest call (`real-zero-038-ABA`, T3) | Facts: Sarah studies at Athens. Iris studies at Bristol. Bristol teaches linen. Athens teaches timber. What is taught where Iris studies? Answer: | **Bristol** -> **linen** / Athens -> timber | +0.000 / +5.375 | -0.094 / +0.844 | +0.125 / +1.500 |

---

# 1. Motivation and research question

**Question.** When two prompts contain the same entities and concepts but
assign them different relational roles, does J-Lens identify the correct
hidden intermediate — and does changing that representation causally change
the model's answer?

## 1.1 What J-Lens is, briefly

J-Lens is defined from first principles in §2.1.

## 1.2 What binding is and why a lens struggles to see it

The question is whether the model represents
*Paris-as-the-city-attached-to-Arin*, not whether it represents Paris:

> Arin lives in Paris. Bela lives in Tokyo.
> Arin lives in Tokyo. Bela lives in Paris.

Only the pairing differs, and the pairing is the binding; every record
carries such a role-swapped twin.

![The binding problem: two prompts, the same four concepts, opposite pairings. Only the pairing distinguishes them, so only a reader of the relation can tell them apart.](results/figures/binding-concept/fig1-binding-problem.png){width=82%}

No token means "the-city-attached-to-Arin", so three phases follow:
**before the query**, both bindings stored, neither selected — chance is
correct; **during the query**, the only span where a binding could be
determined but not yet emitted; **at the final token**, the output shadow
dominates.

Stage 3 (§4.2) read the middle phase. Measured answer: it is not shadow-free
either — the model's next-token preference is already directional there
(0.800 / 0.731 at the two primary positions), both lenses track it, and a
supervised probe reads chance (0.525) at the relation-completing token: the
model's developing selection, not a stored binding.

## 1.3 The gap

Nobody had quantified the bag-of-concepts limitation on a matched-pair task,
or separated "reads stored structure" from "predicts the upcoming output".

---

# 2. Method

This is a **method evaluation**, not circuit discovery. The object under test is
J-Lens; the two-hop binding task is an instrument, chosen because it is
controlled, not because the circuit behind it is interesting. If the
instrument turns out to be the interesting part, this project has failed.

## 2.1 What J-Lens computes, and why a first-order readout is the thing in question

Write `h_l[t]` for the residual at layer `l`, position `t`, and `unembed(·)`
for the model's output map. The **logit lens** reads `unembed(h_l[t])`
directly; **J-Lens** first fits, per layer, an average input-output Jacobian

```
J_l  ~=  E_x [ d h_L[t] / d h_l[t] ]
```

— a learned linear *transport* into the final-layer basis — and reads
`unembed(J_l @ h_l[t])`. In the pinned reference implementation, the same
code with `use_jacobian=False` substitutes the identity for `J_l`, yielding
the logit lens through the *identical* extraction and decoding path — the
comparison isolates the learned transport alone (Control 1).

**Why test it.** `J_l` is a *first-order* object — an averaged linear
approximation of a non-linear map — while binding is conjunctive.

## 2.2 Substrate: model, lens, and environment

Identifiers verified on the execution GPU.

| | |
|---|---|
| Model (pinned) | `Qwen/Qwen3.5-4B` @ `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`, resolved as `Qwen3_5ForCausalLM` (text tower), `torch.bfloat16` |
| Layers / `d_model` / unembedding width | **32** / **2560** / **248320** (`Qwen2Tokenizer`, `len(tokenizer)=248077`) |
| Lens (pinned) | `neuronpedia/jacobian-lens` @ `16a01f30`, file `..._n1000.pt` (sha256 `1f9a8f8f…`, n_prompts=1000) |
| Lens `source_layers` | `0..30` (31 layers); model layer 31 is the lens's output row |
| Reference implementation | `anthropics/jacobian-lens` @ `581d398` (Apache-2.0); test suite 32/32 passing on the execution GPU |

The lens is a generic wikitext fit — hence the coverage control in §2.5.
**Activations are read from the HuggingFace modules directly; TransformerLens
is not in the path** — the lens was fit on HF-native activations.

## 2.3 Dataset: matched pairs, and the order-reversed variant

**The paired construction is the whole method.** Each item is a pair of
prompts with identical entities, relations and answer candidates; only the
binding differs.

| | Prompt | Correct intermediate | Correct answer |
|---|---|---|---|
| Variant A | Arin lives in Luma. Bex lives in Nori. Luma uses zent. Nori uses vark. What is used where Arin lives? Answer: | `Luma` | `zent` |
| Variant B | Arin lives in Nori. Bex lives in Luma. Luma uses zent. Nori uses vark. What is used where Arin lives? Answer: | `Nori` | `vark` |

**The order-reversed variant dissociates role from linear position.** Each
item is also rendered fact-order-reversed and both renderings scored: a
position-tracking readout falls to floor across the reversal; a
role-tracking one is invariant.

**Templates and eligibility.** Six templates (T1–T6), seed 20260827; every
scored intermediate, answer and entity is a single token. Both variants
must be answered correctly by the unmodified model under greedy decoding —
screened first (`results/runs/20260827T090437Z-eligibility-screen/`): `pair_eligibility(AB) = 0.900` against the pre-registered
0.80 threshold. `[agent-unverified]`

**Split.** 10 development pairs, 40 held-out. **The 40 held-out pairs are
not looked at, in any form, until after the Hour 7 freeze**, and are never
tuned on.

## 2.4 Observation point and the layer-selection rule

**The layer band is not pre-declared; the selection rule is**, frozen at Hour
7 before any held-out prompt was scored: sweep all 31 source layers on
development pairs; take the argmax of mean paired J-Lens margin; score every
arm at layers selected on J-Lens; publish the full curve.

**Result, and a deviation stated.** The written rule also allowed growing a
band of near-peak layers; the implemented pipeline scores at the single
selected layer per position — a simplification made before any held-out
contact, applied identically to every arm, recorded here rather than silently
reconciled. Selected layers, frozen in `experiments/stage3/freeze.json`:
J-Lens L30 at the relation-completing token, L27 at the question mark.

**The final prompt token — where the method's own authors score — did not
survive as primary.** It is output-contaminated (§4.2), and the pre-query
token precedes the question naming a subject, so its chance-level score is
the control *passing*. A position sweep over the query window, decision rule
committed before the sweep job (Hour 3), moved the primary positions to the
**relation-completing token** and the **question mark**, frozen in `results/stage2/FREEZE.md` before any
held-out-reading code.

## 2.5 Arms, metrics, and controls

![Three instruments on the same residual: the supervised difference-in-means probe as ceiling, J-Lens as the unsupervised reader, and the logit lens as floor.](results/figures/binding-concept/fig3-three-instruments.png){width=82%}

**Arm 1 — J-Lens.** `unembed(J_l @ h_l[t])` at the selected layer.

**Arm 2 — logit lens.** The same call with `use_jacobian=False` (§2.1).

**Arm 3 — supervised difference-in-means reference.** Separates "J-Lens
cannot read binding" from "binding is not linearly there": a
nearest-centroid readout over the closed set of intermediate tokens, fit on
development prompts only and applied unchanged to held-out — a *reference
level*, not a ceiling. It transfers
dev→held-out unchanged: **0.725 → 0.731 at the question mark**, exactly
the model's next-token preference rate there, and **0.525 at the
relation-completing token where J-Lens reads 0.781**.

**Metrics.** (a) *Pairwise binding success*, binary and conjunctive: a pair
succeeds only if the readout prefers the correct intermediate in Variant A
*and* reverses in Variant B. **Any readout responding only to concept
presence scores exactly zero**. (b) *Paired
binding margin*, `m(p, l) = s_l(correct) − s_l(alternative)` averaged over the pair;
comparable within an arm, never across. (c) *Recall@10*, secondary. Paired
bootstrap over pairs throughout.

| # | Control | What it rules out | Status |
|---|---|---|---|
| 4 | Coverage positive control | A null caused by the lens never having seen this vocabulary | Required before any null |
| 7 | Label permutation | Attractive token lists that do not depend on the label mapping | Held-out |
| 8 | Norm-matched random *transport* (passive) / *direction* (causal) | Margins or effects any norm-matched perturbation would produce | 8a in Stage 1; 8b unavailable with the causal arm |

Others are reported where they arise.

**Control 4: PASS.** The reference multihop evaluation through the pinned
lens: J-Lens pass@10 **0.350** against the logit lens's **0.200** through
the identical path. The transport is live; the nulls below are not a
coverage artifact.

**Controls 10 and 11 (relation deletion, question truncation) were cut
before any result (2026-08-27).** They take the model off-distribution, so a
moved readout may only report a broken prompt; the pre-query position
performs control 11 in-distribution. The honest
cost is control 10, the one control that directly threatens a positive
headline; a **resample** variant is offered instead but unrun (§7), so the
paired margin should not be read as excluding a co-occurrence account.

**Negative controls.** No shuffled-corpus control lens is published; the
norm-matched random *transport* (8a, each `J_l` replaced by a Gaussian
matrix of matched norm) sits at chance everywhere, median rank
~130,000–206,000 against the fitted transport's 11–357.

**The causal arm is unavailable, and that is itself a method-evaluation
finding.** ADR-0005 scoped the project passive-primary; the causal arm (H3)
would run only if a faithful sparse non-negative J-space reconstruction
existed in the released artifact. It does not: an audit of the pinned vendor
tree (`scripts/v2_decomposition_audit.sh`, run record `results/runs/20260827T153925Z-stage1-passive-readout/`) found no decomposition machinery
anywhere. Stated plainly: the
capability the method's framing implies is not supported by its released
artifact — a finding about the method under test, not a gap in execution.
Substituting an arbitrary top-token projection and calling it J-space is
this project's declared FAIL condition and was not done.

---

# 3. Preregistration and what was frozen when

| Frozen thing | Where | Before |
|---|---|---|
| Dataset generator, seed 20260827, eligibility thresholds | `src/make_dataset.py` | any GPU run |
| Layer-selection rule (argmax on dev, publish full curve) | Hour 2 log entry | the dev sweep |
| Position-sweep decision rule | Hour 3 log entry, `7adaad1` | the sweep job |
| Positions (by anchor) and per-position layers | `results/stage2/FREEZE.md`, `experiments/stage3/freeze.json`, `c5e9a5a` | any held-out-reading code (`62dc94b`) |
| Failure condition ("frac at both primary positions ≈ control = forking paths, and that is the finding") | Hour 4 log entry | the held-out read |

Held-out was read **once** (job 554591) after all of the above. Two
pre-registered predictions in the Hour 4 entry were wrong (the output shadow
at the window positions is not near zero; §4.2); the entry records that
rather than revising them.

---

# 4. Results

## 4.1 Behavioral eligibility

The screen is a *label*, not a filter: no record was dropped.

| Split | GPU | pair eligibility (AB, real/zero) |
|---|---|---|
| dev (n=40) | A30, L40S ×2 | 1.000 |
| dev (n=40) | A100 ×4 (incl. two preempted re-runs) | 0.900 |
| held-out (n=160, T1–T6) | A30 | 0.950 |

Eligibility is **deterministic per GPU architecture**. This is also control
5 — "just ask the model" solves the task at 90–100%.

## 4.2 Primary result: what the readout is actually reading

**(a) At the final token, the "recovered intermediate" is the model's output
forming.** The first full run looked like a headline: median rank ~35,
correct intermediate preferred to its twin on 39/40 dev records. Capturing
the model's own next-token distribution in the same forward pass dissolved
it: the model already prefers the correct intermediate on **37/40** records
(mean margin +2.77, re-derived by hand) and the J-Lens margin tracks the
model's. Reading the residual there is reading the model's next few words.

**(b) Direction appears in the query window, where the question is
well-posed.** Sweeping it (pre-registered rule, both clusters): direction at
the relation-completing token (0.775/0.750 against a label-permutation
control at 0.350) and the question mark (0.675), not at the subject token.

**(c) Frozen held-out confirms the positions; the measured shadow settles
the attribution.** On 160 unseen records (job 554591, `results/runs/20260830T175149Z-stage3-heldout-frozen/`):

![Direction score by position on frozen held-out: both lenses rise at the
relation-completing token and track the model's own next-token preference;
the randomised transport stays at chance.](results/figures/stage3-frac-by-position.png){width=82%}

| held-out, frozen | frac | label-perm control | median rank |
|---|---|---|---|
| J-Lens, relation-completer (L30) | **0.781** | 0.519 | 128 |
| J-Lens, question mark (L27) | **0.669** | 0.556 | 95 |
| logit lens, same positions | 0.688 / 0.738 | 0.519 / 0.544 | 393 / 82 |

The pre-registered failure condition did not fire: the positions are real,
not forking paths. But the same run measured the model's own next-token
distribution *at* those positions, and the Hour 4 prediction that it would
be near zero was wrong: the model already prefers the correct intermediate
at **0.800** and **0.731** — it reads ahead, mid-question. Hence a
discriminating set: held-out records where that preference is *wrong*.

![On records where the model's own developing preference is wrong, every
passive readout is wrong with it.](results/figures/stage3-discriminating-set.png){width=82%}

| held-out | lens acc, preference wrong | lens acc, preference right | r(lens, preference) |
|---|---|---|---|
| J-Lens, relation-completer | **0.344** (n=32) | 0.891 | +0.88 |
| J-Lens, question mark | **0.125** (n=40) | 0.872 | +0.92 |
| logit lens | 0.250 / 0.200 | 0.797 / 0.932 | +0.71 / +0.93 |

Below chance in every cell: where the model's developing preference is
wrong, the lens is wrong *with* it. Arm 3 closes the mechanism: the
supervised probe reads nothing at the relation-completer (0.525) while
J-Lens reads 0.781 — the binding is not linearly present there; the
Jacobian manufactures the preference.

**The supportable claim.** *J-Lens is a well-calibrated predictor of what the
model is about to say, at every position where direction is readable — and an
instrument for reading stored-but-unexpressed bindings nowhere on this task.*
Its surviving edge over the logit lens is concept-rank localization at
early/mid positions, largely gone by the question mark.

**What this does not claim.** The model demonstrably *computes* the binding —
it answers at 90–100%. This report establishes neither the existence of a
binding representation at any particular locus nor its exclusion: it
establishes that a family of passive linear readouts at four single positions
sees nothing beyond the developing output preference. The places binding most
plausibly lives — fact-token residuals, attention QK structure, nonlinear or
low-magnitude encodings — were not probed. The conclusion is about the
instrument, not the model.

## 4.3 Layerwise structure

One indexing fact, caught by hand-verification and confirmed from vendor
source: lens layer *i* is the residual **after** block *i*, so L30 is the
penultimate block (earlier drafts said "last layer"; corrected). The gap
between the logit lens at L30 and the model's own distribution therefore
isolates the final block: ~11 points at the relation-completer, nothing at
the question mark.

## 4.4 Controls

![Experiment 2 controls on frozen held-out data (n=160): shuffling the answer key drops J-Lens to chance, and a random matrix in place of the trained one drops both the direction score to chance and the median rank of the correct city from about a hundred to over a hundred thousand.](results/figures/stage3-controls.png){width=82%}

Remaining outcomes:

| Control (§2.5) | Outcome |
|---|---|
| 3 order-reversed rendering | Applied to every item; margins flat across all four AB/BA cells |
| 7 label permutation | 0.35 on dev; **0.45–0.56 on held-out**, audited: with a six-word pool only 65/160 permuted label pairs are fully disjoint from the record's own (4 identical, 8 swapped, 83 share a city). The control is weaker on held-out and every held-out gap is read against this |

## 4.5 Causal arm

Unavailable, for the reason verified in §2.5: the reference implementation
ships **no sparse non-negative J-space reconstruction** (blocker B2). No
top-token projection was substituted — that is this project's declared
failure condition.

---

# 5. Error analysis

**By template** (J-Lens, frozen positions, held-out): every template clears
its control; the dev template (T1) carries an ~0.15–0.20 bonus.

**The principled error taxonomy is the discriminating set**, selected by a
seed-fixed criterion (the model's own preference sign), on which every
passive readout scores 0.125–0.344. The failure mode is uniform — the readout
follows the preference — and no second one was found, which is itself the
finding: a latent-binding reader should have produced one.

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

The claim boundary first: **neither the existence nor the exclusion of a
binding representation is established.** Behavioural competence proves the
model computes the binding; this report shows only that passive linear
readouts at four single positions read the developing output preference and
nothing beyond it.

Also real, in order of weight: one model, one lens checkpoint, one language,
synthetic single-token prompts; n=40 dev / 160 held-out; a weakened held-out
label-permutation control (§4.4); no shuffled-corpus control lens (B3);
control 10's resample variant unrun; the causal arm absent (B2), so every
readout claim is correlational.

---

# 8. What I would do next

Ordered: (1) **probe the construction site** — arm 3 at the fact tokens,
where binding must exist in some form; (2) **activation patching between
order-swapped twins** at the frozen positions — the causal test passive
readouts cannot supply; (3) the deferred stimulus-format test (ADR-0006);
(4) the multi-token template lens for the 27B model.

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

Clock ruling (ADR-0005): wall-clock time, not summed agent-hours; setup and
queue waits uncounted. `llm/memory_bank/time-log.md` is the record.

| Bucket | Hours |
|---|---|
| Experiments, code, analysis (incl. Jason's independent verification) | 15.3 |
| Project-specific reading | 0.0 (literature scan predates the project lock; uncounted) |
| Write-up drafting (agent, this document) | 1.4 |
| **Total counted (limit 20)** | **16.7** — 7.1 verified, 9.6 estimated |
| Executive summary (separate +2 budget) | not started — Jason's prose |

---

# Appendix — Where everything lives

`results/figures/FIGURE-REGISTRY.md` is the figure registry of record;
per-record outputs are in `results/runs/*/outputs/*.json`. The unabridged version is
`writeup/main-full.md`.
