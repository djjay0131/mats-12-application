# Binding section — draft for writeup/main.md — 2026-08-29

> STATUS: coach draft. Neel explicitly penalizes prose that reads like an LLM
> wrote it. Rewrite every sentence in your own voice before it goes in the
> Google Doc; keep the structure and the numbers, not the wording.
> Figure references point to results/figures/binding-concept/.

---

## For the BODY (proposed §1.2, "What binding is and why a lens struggles to see it")

The question this project asks is not whether the model represents Paris. It is
whether the model represents *Paris-as-the-city-attached-to-Arin* — and whether
an unsupervised readout can see the difference.

The distinction is the classic binding problem. Two prompts —

> Arin lives in Paris. Bela lives in Tokyo.
> Arin lives in Tokyo. Bela lives in Paris.

— contain exactly the same four concepts: Arin, Bela, Paris, Tokyo. A readout
that only detects which concepts are present cannot tell these prompts apart.
What differs is the pairing, and the pairing is the binding (Figure 1). This is
why every record in the dataset carries a role-swapped twin: both cities are in
the context, equally salient, so a bag-of-concepts readout scores exactly
chance (frac = 0.500) by construction, and only a readout that has recovered
the relation can beat it. The distractor is the experiment.

Binding is structurally awkward for a lens. A lens maps a residual vector to a
ranking over the vocabulary, and vocabulary items are identities — there is no
token that means "the-city-attached-to-Arin." A token-ranking instrument can
therefore only express a binding indirectly, by ranking Paris above Tokyo, and
it can only do that once the model has resolved the relation into a selection.
That yields a three-phase account of the forward pass at the readout positions
(Figure 2):

1. **Before the query** (the prequery position, index 20): both bindings are
   stored, neither is selected. "Correct intermediate" is undefined — it is a
   property of the query, which has not been seen. Chance is the correct
   expected value here, and a directional readout above chance would indicate a
   leak, not binding. [This is the reframe of the Stage 2 prequery result:
   frac 0.550 is the control passing, not the lens failing.]
2. **During the query** (query onset → final token): the model resolves which
   binding the question selects. This is the only span where a binding is
   determined but not yet emitted — the only place a token-ranking readout
   could, in principle, see a binding rather than an output.
3. **At the final token**: the answer is computed. The model's own output
   distribution already prefers the correct intermediate on 92.5% of records,
   so a directional readout here is dominated by the output shadow (Stage 2:
   J-Lens final-position margin couples to the model's own intermediate margin
   at r = 0.771 against a shadow anchor of 0.811).

Stages 1 and 2 of this project measured phases 1 and 3 — the two phases where,
for opposite reasons, a directional binding readout is uninformative. The
post-query sweep (§X) reads phase 2 for the first time, and adds a supervised
difference-in-means probe on the same layer × position grid as a ceiling: the
probe answers whether the binding is linearly decodable in the residual at all,
and the gap between the probe and J-Lens is the measured limit of unsupervised
reading.

## For the EXECUTIVE SUMMARY (insert, 3–4 sentences, near the top)

A model that has read "Arin lives in Paris. Bela lives in Tokyo" represents
four concepts, but its answer depends on a relation: which city is bound to
which person. Detecting the concepts is the solved half of interpretability;
reading the binding is the hard half, and it is what this project measures.
Every test prompt contains a role-swapped twin (both cities present, pairing
reversed), so a readout that only sees concepts scores exactly chance by
construction, and only recovery of the relation can beat it. Our finding, in
one line: J-Lens localizes the bound concepts one to two orders of magnitude
better than the logit lens, but [pending sweep: whether any unsupervised
readout resolves the binding itself at positions where it is determined but
not yet emitted].

## Placement notes

- Figure 1 next to the twin-prompt example in the body section.
- Figure 2 next to the three-phase list.
- Figure 3 belongs with the sweep design section (§X), not here.
- The bracketed clause in the exec summary is a placeholder until the sweep
  reports; do not resolve it optimistically.
- Cross-reference: the prequery reframe must also land in §2 wherever
  frac 0.550 currently reads as a failure (see project doc
  claude/hour-interpretation-prequery-reframe-2026-08-29.md §2).
