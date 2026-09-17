# Application form worksheet — fill in, then copy/paste into Airtable

Form: <https://airtable.com/appnMboxg76F1QIDc/pagqu7wWWrUCZkNVI/form>
Deadline: **Fri Sept 4, 11:59 PM PT** · Questions read verbatim from the live
form on 2026-08-31. Every ★ field is required.

**How to use this file.** Write your answer inside each `ANSWER` block, in
your own voice — he filters on these first and penalises LLM-cadence prose.
The NOTES under each question are lookups so you don't have to dig: exact
identifiers, the numbers, and where each fact lives. Suggested lengths are
guesses at his patience, not form limits (only the evidence question states
one: ~100 words).

Time accounting: writing these form answers is **uncounted**. The +2h budget
covers the executive summary; the form Qs are outside the clock entirely.

---

## Before you open the form — mechanics checklist

- [ ] **Resume PDF** ready (required upload)
- [ ] Google Doc: exec summary is pages 1–3, sharing = anyone with the link
- [ ] Open the doc link in an **incognito window** and confirm it renders
- [ ] LinkedIn URL handy
- [ ] If linking the repo under "other outputs": **remove
      `context/default_600k.md` first**, then flip to public
- [ ] Radio: "definitely able to join research phase full-time (Jan 19–Apr 10)?"
      — decide before you're in the form

---

## ★ ~16 hour research task — Google Doc link

> Please link a Google Doc with your executive summary and main project write
> up. Make sure to let anyone view it! Applications without a doc will be
> rejected.

```ANSWER
<paste doc URL>
```

## (Optional) Link to any other relevant outputs (code, colab, etc)

NOTES · The repo, once the 600k file is removed and it's public:
`https://github.com/djjay0131/mats-12-application`. He feeds code to his
agents and asks them what you actually did — the run manifests under
`results/runs/` are the strongest thing in there.

```ANSWER

```

## ★ Checkboxes

- [ ] The first 1–3 pages of the attached doc are an executive summary
- [ ] Permissions set so anyone with the link can see it

---

## ★ What question did you try to answer?

Suggested length: 1–2 sentences. This is the first substantive thing he reads.

NOTES
- The honed version: when two prompts contain the same entities and concepts
  but assign them different relational roles, can J-Lens identify the correct
  hidden intermediate — or only a bag of concepts?
- Keep the framing: a **method evaluation** using a controlled task as the
  instrument. Not circuit discovery.

```ANSWER
J-Lens can show you the vocabulary and the bag of concepts at each step or layer, but is it able to read out the binding information, or is it just predicting what the model is about to answer?
Does J-Lens beat the logit lens at binding?
Do the controls hold — is the score coming from the lens, or from the pipeline?
Does the lens still work when the model is wrong?
```

## ★ Why is this question interesting / why did you choose it?

Suggested length: 3–5 sentences.

NOTES
- The J-Lens paper names the bag-of-concepts limitation itself; nobody had
  quantified it against a matched alternative.
- J-Lens is a Jacobian — first-order. "Can attribution methods capture
  higher-order effects beyond first-order approximations?" is a listed open
  problem in Open Problems in Mech Interp (Sharkey et al., §attribution).
- Monitoring relevance: a readout that knows the model is "thinking about
  Prague and wool" without knowing who-lives-where is a weaker instrument
  than its readability suggests.
- Your origin story (only you can tell it): the knowledge-graph intuition —
  a KG is typed edges, not a node set.

```ANSWER
I chose this question because it scored the highest (well, tied) in the matrix I used to determine which problem to try. I had Claude come up with five ideas, and then Claude and I came up with a sixth that was tied to one of my interests. I think I scored them on six dimensions: Fit, Originality, Feasibility, Baseline, Negative Result, and Risk. Fit being mostly: does this fit with what Neel is interested in? Does it fit with what I am interested in? My idea spawned from an idea I have had in my head for some time. The operators in the Matrix read the characters streaming across the screen. While researching MI, it made me think: if the internals of AI are all vectors of numbers, could we teach humans to read it? If we could, that would be just like reading the mind of AI. Obviously, it's not as simple as just teaching it; we need to first learn how to understand it. Another aspect of my research is knowlege graphs, which then led me to learn more about lenses, and your questions about J-Lens and lenses in general and what they really do. It was a weakness that has been mentioned in the J-Lens paper as well. What was interesting is that the lens appears to be answering a different question than everyone assumed.
```

## ★ What conclusions have you reached about this research problem?

Suggested length: 4–6 sentences or tight bullets. Lead with the strongest.

NOTES — the four claims, with numbers (all held-out n=160, six templates,
replicated Falcon L40S + TinkerCliffs A100 unless marked dev):
1. Direction readout ≈ output prediction: coupling r = 0.88–0.92 to the
   model's own next-token preference; on the 32 records where the model's
   preference is wrong at the relation-completing token, J-Lens follows it —
   11/32 = 0.344 correct; at "?": 5/40 = 0.125. Degrades with shadow
   strength: model margin < −1.2 → lens wrong 11/11.
2. The Jacobian computes rather than reads: supervised difference-in-means
   probe on the same residual reads 0.525 (nothing) at relcomp where J-Lens
   reads 0.781.
3. Direction appears at the token that completes the relation, not the one
   naming the subject: q04 "Helen" at chance; q05 "lives" 0.781 vs 0.519
   label-permutation control (~3.9 SE on dev).
4. Surviving edge = concept-rank localization: median rank of the correct
   intermediate 35 of 248,320 at L27 (logit lens: 1,022); ~227× at prequery.
   Concepts recovered, binding not — the limitation, measured.

```ANSWER
I have concluded that J-Lens does not read what the model has stored, it predicts what the model is about to say. I have also concluded via the probe that there was nothing there to read.  The normal way of scoring a lens can't tell the difference between reading stored data and prediction. We have provied a simple method that works. Both J-Lens and Logit Lens report the answer correctly, however, J-Lens does a better job of ranking the words at each step.  Before the model reads the word that answers the question, the lens reads chance.  
```

## ★ Technical setup: what do you quantify, how defined and measured? Models, datasets, prompts, metrics.

Suggested length: bullets are fine here; he asks for key technical details.

NOTES — exact identifiers (from the run manifests):
- Model `Qwen/Qwen3.5-4B` @ `851bf6e` · lens `neuronpedia/jacobian-lens`
  rev `qwen-n1000` @ `16a01f3` (fit by Neuronpedia against this exact model;
  we fit nothing).
- Stimuli: paired two-hop prompts, identical vocabulary, swapped bindings
  ("Helen lives in Prague / Oslo. Prague uses wool…"). 6 templates, closed
  6-city pool, single-token targets verified under the tokenizer, fixed seed.
  Dev 40 records (10 pairs) for all development; held-out 160, generated
  once, never inspected before the frozen run. Eligibility gate: both
  variants answered correctly, deterministic decoding — 90% pass.
- Quantified: (a) binding direction — lens margin, correct intermediate vs
  role-swapped twin, as frac against a label-permutation control at matched
  position and layer; (b) concept recovery — median rank over the full
  248,320-wide unembedding; (c) output shadow — the model's own next-token
  margin for the same tokens, same forward pass, plus record-level r.
- Positions per record by anchor: prequery "." · each query token · the
  relation-completing token · "?" · final ":".
- Arms: J-Lens · logit lens through the same code path (Jacobian disabled) ·
  supervised difference-in-means reference (leave-one-pair-out) ·
  norm-matched random transport · label permutation.
- Pre-registered freeze committed before the held-out run; VT ARC, two
  clusters.

```ANSWER
I used Qwen3.5-4B with the released, pre-fit J-Lens (the Neuronpedia checkpoint, fit on wikitext — I did not fit a lens), and the logit lens as the baseline, which is the same code with the Jacobian switched off. The dataset is 50 pairs of short two-hop prompts across six templates: each pair is the same words with the pairings swapped ("Helen lives in Prague. Mark lives in Oslo." vs. Prague and Oslo swapped), so a method that only spots which words are present scores exactly 50%. Ten pairs (40 records) were for development, 40 pairs (160 records) were held out and scored once after everything was frozen. I read the lens at four points in each prompt — after the facts, at the word in the question that pins down the answer, at the question mark, and at the final colon — at the layer that scored best on development data. Three things get measured: direction, the fraction of records where the lens prefers the correct city over the swapped one (the margin is score for the correct city minus score for the swapped one, averaged across the pair so token biases cancel); localization, the median rank of the correct city across the full 248K-token vocabulary; and reading vs. predicting, which uses the model's own next-token preference for the same two cities, saved from the same forward pass, to split records into "model leaning right" and "model leaning wrong" and score the lens on each group separately. Controls were a shuffled answer key, a random matrix in place of the trained one, fact-order reversal on every item, and a probe trained with the answer key to check whether anything was readable there at all.

```

## ★ What is the strongest evidence you found against these hypotheses?

Suggested length: 3–5 sentences. Your home turf — the design exists to attack
its own headline. Pick, don't list.

NOTES
- Against "J-Lens recovers binding" (the apparent 0.975 at the final token):
  the model writes the intermediate into its own generation in 38/40 records;
  its own logits score 0.925 on the same statistic; on the discriminating
  records the lens goes below chance with it (0.344 / 0.125).
- Against "readouts see nothing": relcomp 0.781 vs 0.519 control, every
  template, held-out, both clusters — and a rank gap the shadow can't explain
  (35 vs 1,022 at matched mid-stack layers).
- Against our own instrument, disclosed: one pre-registered prediction was
  wrong (window shadow was 0.800, not ≈0) and is recorded as wrong; the
  label-permutation control's weakness is itself measured (65/160 fully
  disjoint under the 6-city pool → control sits ≈0.52).

```ANSWER
The strongest evidence I found against my hypothesis is that the records the model got wrong, might be the records where the fact itself was scrambled, not just the output.  I chose the records that were wrong because the model was leaning wrong, and a model tends to lean wrong with the internal state is off. So it's possible my pairings were weak or corrupted. However, I did also use the probe, and it found nothing on ALL 160 records, not just the model-wrong records.  
```

## ★ What are the biggest limitations to your results? Could you have addressed them?

Suggested length: 4–6 sentences. He says flagging beats being caught.

NOTES — real ones, each with the could-we-have line:
- One model, one lens checkpoint, one synthetic task family → second
  model/lens and naturalistic prompts were the obvious extensions; cut for
  the 20h budget.
- 6-city pool weakens label permutation (measured, 65/160 disjoint) → larger
  pool fixes the control but breaks the shared-vocab fix that made the
  supervised reference readable; genuine trade-off, chose measurability.
- n=40 discriminating power: J-Lens-vs-logit-lens direction difference not
  resolvable (SE ≈ 0.08) — pre-registered as out of scope, not discovered
  after.
- No causal arm: the released implementation ships no sparse non-negative
  J-space reconstruction (verified absence — 0 matches across 1,713 lines);
  declared unavailable rather than approximated. All claims correlational.
- Window shadow measured only in the final stage; dev-stage exclusion at q06
  was structural reasoning until then, and the log says so.

```ANSWER
I only used one model, one lens checkpoint, one task family. A larger pools of cities could have given us better control, but that would have made it less readable. I wanted to do a causal study experiment, however that would have required writing updates to the lens that was not in the budgeted time.  This is something we can do in the next part of the project. It's possible that I did not find any bindings in the storage because I did not lok in the right places.  
```

## ★ How did you use LLMs in this research task and write-up? Which LLMs? How exactly did you make sure they weren't just giving you slop?

Helper text: which parts you did and didn't check, how you prioritized, and
how surprised you'd be to discover a major error in each part.
Suggested length: this one earns a real paragraph or two. ~3× acceptance
correlation for agentic use described well.

NOTES — the factual inventory; the calibration sentences must be yours:
- Setup: Claude (Fable) as orchestrator/coach in one session; a second Claude
  session driving VT ARC through a persistent tmux+IPython kernel on a GPU
  node, Slurm batch for anything long; both worked against a shared repo.
- Controls built before results existed: his instructions distilled to a
  121-requirement register with a gated mechanical checker; three ledgers
  (claims typed existence-proof vs method-claim; controls with results;
  verification); every run writes a manifest (Slurm job id, commit, model
  and lens revisions) plus raw outputs, committed; figures self-register with
  claim id, seed, sha; reproduce.sh; preregistration + freeze before
  held-out.
- Every agent number labelled `agent-unverified` until re-derived. What was
  checked: the headline aggregation independently re-derived from committed
  per-record JSON (0.344 and 0.125 reproduced exactly); rank spot-checks
  against the vendor readout — which caught an off-by-one layer convention
  (hooks capture block output; L30 is not the final layer); eligibility
  labels hand-counted; correlations re-derived; full two-cluster replication.
- Things the process caught: an eligibility screen scoring the parser instead
  of the model (two instrument fixes, invalid runs kept with notes); the
  answer-shadow confound itself.
- YOURS to add: which parts you personally interpreted (prequery = control
  passing; the gate decisions; the ADR rulings), what you did NOT check, and
  the per-part "how surprised would I be" calibration.

```ANSWER
I used both Claude and ChatGPT, and I tended to stick with the highest models for this project.  I initially used ChatGPT to discuss the project and my ideas. I then used claude desktop to setup my experiment harness, which is a github repository, with my agentic-goverance and agentic-research skills that I have developed.  From here, I did the initial setup and housekeeping tasks, such as getting access to ARC Servers at my institution.  I used claude to help me setup a framework for the application inside the repo, from a scoring system for ideas, through confirming that I followed all of your instructions and advice as best I could.  Claude even helped me keep track of my time.

As far as validation goes, I hand-counted the data in the first set of experiments.  I ran scripts by hand on the ARC servers to check the data.  Until it became too complicated to do by hand.  In experiments 2 and 3 I did more of an integergation with claude on the experiments and the results, which scanning the outputs and conclusions.  
```

## ★ What, if any, prior experience do you have with mechanistic interpretability?

NOTES · Yours alone. If this project is the first hands-on MI work, say it
plainly — his doc: a good application task is enough, whatever the
background.

```ANSWER
None really.  I did try to build my own GPT and then use transformer lens from your older MI resarch from 2025, but I did not get as far as I would have liked.  This could be my opportunity to really get my hands dirty and dig deeply into MI. That said, I always have new ideas, and I alway want to find ways to understand both the physchology of humans and comptuers at the same time.  Why was that done that way? What was that person or machine thinking when they made that choice? How can we ensure future tasks are done with pure provenance?
```

## ★ Other than your research task, what are 1–3 pieces of evidence that you'd be able to do good research in the program? (~100 words)

Constraint: explicitly NOT the project above. Unusual backgrounds welcome.

NOTES · Candidates only you can rank: the knowledge-graph research line
(pick the strongest single artifact); the PhD work; evidence of the shape
"built the instrument, changed my mind on the data"; running research
infrastructure (ARC orchestration) if you can tie it to research judgment
rather than ops.

```ANSWER

```

## ★ Why are you interested in Neel's stream specifically?

NOTES · Honest hooks that happen to be true: pragmatic interpretability over
pure reverse-engineering matches how you work; his research-process posts
were literally the operating system of this project (the stage gates and
prediction-first loop are committed in the repo); the culture of red-teaming
your own result. Two or three sentences beats a page.

```ANSWER
I have been interested in your work since someone did a presentation on MI at a conference in SC last year.  I just have not set aside the time to dig in.  I really love the way you talk about things, simplify things, and I believe if I am going to learn to make a difference in AI Saftey, that you are the person to learn from.  I have been targetting Anthropic when I graduate, but I would also love to work with you at google!  
```

## ★ What is the likelihood you will join Neel Nanda's training program (Sept 28 – Oct 30) if accepted?

NOTES · Free text. One plain sentence; note the exploration phase is
part-time-compatible if that's load-bearing for you.

```ANSWER
100%
```

## (Optional) Anything else important about your application project not covered above?

NOTES · Best candidates: full provenance is public (manifests,
preregistration, freeze, invalid runs kept with notes, time ledger with
verified/estimated split); the wrong pre-registered prediction and where
it's recorded. Skip it if the answers above already carried these.

```ANSWER
Everything I did for this application is in the repo history. I did use claude heavily, but I did not just sit back and prompt. The repo is shared above you can look at both the code, experiments, and the rest of the project harness. 
```
