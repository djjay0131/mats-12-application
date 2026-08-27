# Design audit against Neel's 600k context file

Date: 2026-08-26
Source: `context/default_600k.md` (2.24 MB, 41,360 lines), read in full.
Status: findings recorded; items 1–8 folded into the execution prompt, items
9–10 are open decisions for Jason.

## The headline finding

**The file predates J-Lens entirely.** Zero hits for `jacobian`, `j-lens`,
`jlens`, or `global workspace`; the only two `workspace` matches are
filesystem paths. Every lens in the file is logit lens (×20), tuned lens (×3),
attention lens, future lens, backward lens.

Content cut-off is ~mid-2025. Consequences:

1. It is **background, not a source of requirements.** The 121-requirement
   register from the application doc remains the authority.
2. **We cannot assume Neel knows what J-Lens computes.** The write-up must
   define it from first principles before red-teaming it. That is load-bearing
   word-count, not preamble. (L908: *"You have tons of context, your reader
   does not."*)
3. The closest prior statement of our target limitation is about **inter-feature
   geometry**, not role assignment (Open Problems L2111–2121, "bag of features").
   Say explicitly that we are not testing the geometry question, or a reader who
   knows that passage will judge our experiment mismatched to it.

**Better framing hook than the J-Lens paper's own limitation** — Open Problems
L3543 lists as an open problem: *"How can we develop attribution methods that
capture higher-order effects beyond first-order approximations of model
behavior?"* J-Lens is a Jacobian, a first-order object. "Does a first-order
readout recover second-order (relational) structure?" is a listed open problem
in a survey Neel co-authored. Lead with that.

## Ranked design deltas

| # | Change | Why | Source |
|---|---|---|---|
| 1 | **Eligibility screening moves to hour 1**, before any lens work | Highest-failure, lowest-cost step, currently downstream of everything. Nonce entities + invented predicates + chained two-hop is the opposite of IOI's "common grammatical structure"; a 4B model may simply not do it | Steinhardt L543–552 *"De-risk all components, then execute"*; L7308 |
| 2 | **Add a coverage positive control** — show J-Lens recovers something unambiguous on the same prompts, layer and code path | Without it, a null H4 cannot distinguish "Jacobian readouts can't do binding" from "the `n1000` checkpoint never saw `zent`/`Luma`". As written H4 is near-unfalsifiable | Open Problems L2144–2161; Neel L213 *"I see a simple and boring explanation... and they didn't test for it"* |
| 3 | **Add a supervised difference-in-means ceiling** as a third arm | Logit lens is documented as sometimes non-functional outside GPT-2, so "J-Lens vs logit lens" is uninformative in either direction. The ceiling says how much binding information is linearly available at all — without it no J-Lens number is interpretable | Ferrando L5320–5324; Neel L840–845 *"strive to have the strongest possible baselines"*; the Makelov & Lange MATS paper he calls a favourite does exactly this (L1239) |
| 4 | **Layer band becomes a pre-registered selection rule**, not a fixed 40–80% | Three independent sources place retrieval/attribute-extraction *later* than our band. IOI on 12 layers: *"almost all performance comes from attention layer 9"* — 75% depth | L12096; L5812–5816; L5929–5934 |
| 5 | **Add a fact-order-reversed variant** so role dissociates from position | In "Arin lives in Luma" vs "Arin lives in Nori", role is confounded with linear position. The IOI appendix found positional signal dominating token signal ~3:1. This is the control an IOI-literate reader asks for first | L37627, L37791–37798 |
| 6 | **Report a continuous paired margin** alongside binary pairwise success | 40 binary pairs bootstrapped is the weakest version of this experiment. IOI's endorsed analogue (logit difference) is continuous and closer to the model's objective | L32922; L7306–7307; L818 |
| 7 | **Verify TransformerLens-vs-HuggingFace activation equivalence at hour 2**, or bypass TL entirely | `from_pretrained` applies `fold_ln`, `center_writing_weights`, `center_unembed`, `fold_value_biases` **by default**. A lens fitted against HF-native activations will still produce numbers through processed TL. They will be wrong and nothing will error | L10452–10522; `from_pretrained_no_processing` L10395; comparator notebooks L16525, L16792 |
| 8 | **Verify entity tokenization, not just targets**; handle left-padding | Nonce names will likely be multi-token in Qwen BPE, smearing the "concept" across positions. `"Ralph"`→`['R','alph']`, `" Ralph"`→`[' Ralph']`. HF/nnsight left-pad by default, so index `-1` is right but only if padding is actually left | L17436–17449; L38365+ |
| 9 | **Open: promote H3 out of contingency** | Causal validity does **not** require intervening in J-space. Ferrando Eq. 20 (L4864–4904) gives a 1-D activation-space intervention in a few lines, and we already have paired prompts. Use a difference-in-means direction (sidesteps the DAS illusion) patched on the **residual stream, not a layer output** | L1275 Makelov & Lange illusion result; L2593 *"Probes detect correlations, rather than causal variables"* |
| 10 | **Open: cut two redundant controls** to pay for 2, 3 and 5 | Pair-alternative, relation deletion and question truncation are all "perturb the prompt, see if the readout moves" — mutually predictive. Neel wants *qualitatively different* lines of evidence, not many similar ones | L832–836 |

## Two hazards to pre-commit against

**Self-repair will manufacture a false negative on any causal arm.** The Hydra
effect is real without dropout, and up to 30% of it is a LayerNorm-scale
artefact (L1357–1359). Pre-commit to reporting the intervention's effect on the
downstream logit margin *as well as* argmax flip, plus a norm-preservation
check. Otherwise the artefact alone eats the effect.

**Relation deletion and question truncation take the model off-distribution**
(Ferrando L4829–4832; Neel L7317–7319 on zero-ablation being "arguably
unprincipled"). A readout that moves under deletion may only be reporting "this
prompt is now ungrammatical." Prefer resample-style controls where possible —
our pair-alternative comparison already is one.

## The two critiques that will be aimed at us

**Streetlight interpretability** (Open Problems L2727–2730; Neel L7301–7302,
who calls it *"a fairly legitimate criticism"*). Four synthetic templates with
invented vocabulary is about as streetlit as it gets. **The defence is that we
are not doing circuit discovery — we are evaluating a method, and a method
evaluation legitimately wants a controlled stimulus.** That defence only works
if made explicitly, in sentence one.

**"Not that much value in more manual IOI-style work in small models"**
(L1280). Our design is structurally IOI. Same escape hatch: the deliverable is
a **method evaluation using a narrow task as instrument**, never a
narrow-circuit finding.

**The novelty squeeze** (L764): we are testing a limitation the J-Lens paper
names itself, so his prior on H4 is already high — few bits from confirming it.
And *"projects can also fail due to researcher incompetence or bad luck,"* so a
null without a mechanism reads as ambiguous. Items 2 and 9 are what relieve
both sides: a positive control proves the pipeline works, and a causal arm
supplies the mechanism that makes a predicted negative informative.

## What the file says in our favour

The shape is one he demonstrably likes. He maintains a whole section called
**Paper Back-and-Forths** celebrating exactly this genre (L1293:
*"Interpretability is dark and full of terrors... Red-teaming your own work and
being on guard for this is a crucial skill"*). And L762: *"Rigorous, at-scale
replications of shaky results, negative results of seemingly promising
hypotheses... are all very valuable contributions. I would personally consider
these novel because they expand our knowledge."*

The risk is entirely in execution, not in the choice of project.

## Two practices worth adopting

**Keep a running log from hour 1.** He explicitly wants the tacit-knowledge
appendix — *"This was hard and here are the steps we had to follow"*, *"ways we
noticed our experiments catching fire and what we did to fix them"* (L1141–1155).
For a 20-hour project with a possibly modest technical result, **that appendix
may carry more signal about the researcher than the result does.**

**Do not under-weight writing.** L910: *"you should spend about the same amount
of time on each of: the abstract, the intro, the figures, and everything else
(I'm only half joking)."* Spending 18 hours on experiments and 2 on writing
optimises against his stated evaluation function.
