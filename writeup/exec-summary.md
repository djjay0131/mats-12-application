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
## What problem am I trying to solve?
J-Lens can show the bag of concepts at each layer, but can it read out the binding, or is it just predicting what the model is about to answer? Each prompt holds two facts, such as "Helen lives in Prague, and Mark lives in Oslo", plus a twin with the pairing swapped. Both cities appear in every prompt, so detecting concepts alone scores 50%, chance. Reading the binding beats that, but so does predicting the answer the model is about to give. My experiment tells the two apart. 
## Methodology 
I used Qwen3.5-4B with the released pre-fitted J-Lens. The dataset had 50 prompt pairs: 10 for development (40 records) and 40 held out (160 records), not looked at until the layers and positions were frozen. On development records I read the lens at four spots, measured the margin (correct city minus swapped city), and froze the best layer at each spot. While running the lens I also saved the model's own answer preference at each spot, to later check the lens where the model itself leaned wrong. Then I read the held-out records once at those settings. The logit lens is the same code with the Jacobian switched off. 
## Results
At the relation token J-Lens picked the correct city 0.781 of the time, against a 0.519 shuffled-label control. But the model's own next-token leaning was already right 0.800 of the time there, so beating the control alone does not show a read.  
![Direction score by position on frozen held-out data (n=160): both lenses rise at the token that pins down the answer and track the model's own next-token preference; the shuffled-label and random-transport controls stay at chance.](results/figures/stage3-frac-by-position.png){width=80%}
![J-Lens accuracy on held-out records, split by whether the model itself was leaning right or wrong. Where the model leaned wrong, every passive readout followed it below chance.](results/figures/stage3-discriminating-set.png){width=80%}
## Experiment 1 — Does J-Lens beat the logit lens at binding?
At the relation token J-Lens scored 0.781 and the logit lens 0.688; at the question mark the logit lens was ahead, 0.738 to 0.669. On picking the right city it is a wash. Where J-Lens clearly wins is ranking: it puts the correct city at rank 35, the logit lens near 1,000.
## Experiment 2 — Do the controls hold?
First, shuffled labels: I randomly reassigned which city counts as correct (fixed seed) and re-graded. That gave 0.52 and 0.556 at the two spots. Second, a random matrix in place of the J-Lens matrix, same pipeline: direction 0.475-0.537 everywhere and median rank 130K-206K, versus 35 for the real matrix.
## Experiment 3 — What replaced the causal test
The causal test could not run: the released code cannot separate the J-Lens part of the residual from the rest. Instead I used the 32 to 40 records where the model's own guess pointed to the wrong city. A lens that reads binding should still get these right. J-Lens got 0.344 and 0.125, below chance. An answer-key probe read 0.525 there, so no method found binding. So the lens was guessing the model's answer, not reading its memory.
## High-level takeaways
<!-- Bullets. The most interesting thing first, not the chronology. Each
     bullet is a claim you can defend, with the number in it. If a takeaway is
     speculative, say so in the bullet — do not bury the hedge below. -->
- On this task J-Lens does NOT read stored bindings: where the model leaned wrong it followed, 0.344 and 0.125 against 0.500 chance.  
- Standard scoring misses this; re-scoring only where the model leans wrong shows whether a reading says more than the output.
- A probe trained with the answer key read 0.525 at the frozen spot, chance: nothing there for any method to find.
- J-Lens beats the logit lens at ranking the right word: rank 35 versus about 1,000.  
## Biggest limitation
One model, one released lens, one small six-city task. The answer-key probe found nothing at the key position, so the binding may live somewhere I did not read. I did not test whether changing the residual changes the answer.
