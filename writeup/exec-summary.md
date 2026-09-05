---
title: "Beyond a Bag of Concepts: does J-Lens recover relational binding?"
subtitle: "MATS 12.0 application — Neel Nanda stream"
author: "Jason Cusati"
date: "September 2026"
---

# Executive summary

<!-- HARD LIMITS, checked by scripts/conformance-check.mjs at --gate SUBMIT:
       * 600 words maximum (MEC-06)
       * 3 pages maximum, 1 page is ideal
       * at least one graph (MEC-07) — "Please include graphs!"
       * must name a model, an experiment, a number, and a limitation (SCR-07)
     WRITE THIS YOURSELF. Neel: "Answers that read like they were written by an
     LLM are a significant negative signal - I see hundreds of them, and they
     blur together." An agent may build the figures and check the limits. The
     prose is yours. -->

Are the thoughts exposed by an interpretability lens trustworthy enough to reveal what the model actually represents? J-Lens can show you the bag of concepts at each layer, but can it read out the binding information, or is it just predicting what the model is about to answer?

## Methodology

Each prompt contains a pair, such as "Helen lives in Prague, and Mark lives in Oslo", and for each prompt I swapped pairs, changing who goes with what. I then used J-Lens, partway through the computation, to see if it could tell which city goes with which person. Both cities appear in every prompt, so a method that only detects concepts scores 50%, chance. Binding-access beats chance — but so does predicting the answer the model is about to give. 50 prompt pairs: 10 for development (40 records) and 40 held out (160 records), not looked at until the layers and positions were frozen.

I used Qwen3.5-4B with the released pre-fitted J-Lens (layers 0-30). On the development set I probed at four positions in the prompt and froze the layer with the best margin at each. I also saved the model's own answer preference at the same spot, so I could later check the lens on the records where the model itself was leaning wrong. The interesting position is the word in the question that first pins down the answer; I call it the relation token.

**Experiment 1 — Does J-Lens beat the logit lens?** Both run on the held-out records at the frozen positions and layers. The logit lens is the same code with the Jacobian switched off, so the only thing that differs is the Jacobian.

**Experiment 2 — Do the controls hold?** Shuffled labels: for each held-out record I randomly reassigned which city is marked correct and re-graded the lens against the shuffled key. Random matrix: the prefit J-Lens matrix replaced by a random one, same pipeline.

**Experiment 3 — Does the lens still work when the model is wrong?** My original plan was a causal test, but the piece it needs wasn't in the released code, and building it was out of scope for 20 hours. Instead I graded the lens readings I already had on just the records where the model was leaning toward the wrong city. If the lens gets it wrong too, it is following the model's lean, not reading binding.

## Results

**Experiment 1.** At the relation token J-Lens scored 0.781 and the logit lens 0.688, against a 0.519 shuffled-label control; at the question mark the logit lens was ahead, 0.738 to 0.669. But the model's own next-token leaning was already right 0.800 of the time at that same spot, so beating the control does not show that the lens read anything. Where J-Lens clearly wins is ranking: the correct city at rank 35 of 248K on dev versus near 1,000 for the logit lens; 128 versus 393 on held-out.

**Experiment 2.** Shuffled labels: 0.52 at the relation token, 0.556 at the question mark, so nothing scores high without the real answer key. Random matrix: direction 0.475-0.537 everywhere, median rank 130K-206K versus 35 (dev) and 128 (held-out) for the real matrix. The trained matrix does the work.

![Figure 1. Direction score by position on frozen held-out data (n=160): both lenses rise at the relation token and track the model's own next-token preference; the controls stay at chance.](results/figures/stage3-frac-by-position.png){width=48%}
![Figure 2. Experiment 2 controls (n=160): shuffling the answer key drops J-Lens to chance; a random matrix drops direction to chance and median rank from about a hundred to over a hundred thousand.](results/figures/stage3-controls.png){width=48%}

**Experiment 3.** On the records where the model's own guess pointed to the wrong city (32 at the relation token, 40 at the question mark), a lens that reads binding should still get these right. J-Lens got 0.344 and 0.125, chance and below. A probe trained with the answer key read 0.525 at the same spot, so no method found a binding signal there. The simplest explanation that fits all three numbers is that the lens was guessing the model's answer, not reading its memory.

![Figure 3. J-Lens accuracy on held-out records, split by whether the model was leaning right or wrong. Where it leaned wrong, every passive readout followed it below chance.](results/figures/stage3-discriminating-set.png){width=48%}

## High-level takeaways

- On this task J-Lens does NOT read what the model has stored for bindings - it guesses what the model is about to say. Where the model leaned wrong, J-Lens followed it: 0.344 and 0.125 against 0.500 chance.
- The standard way of scoring a lens does not catch this; my method measures whether the readings say more than the model's output.
- Even a probe trained with the answer key found nothing to read at the frozen position and layers: 0.525, chance.
- J-Lens beats the logit lens at ranking the right words: 35 vs 1000 of 248K on dev, 128 vs 393 on held-out.

## Biggest limitation

One model, one released lens, one small task with six cities. At the position that matters most, even a probe trained with the answers found nothing, so I cannot say whether the binding is stored at some layer or position I did not read. I did not test whether changing the residual changes the answer, so my claims are correlation only.
