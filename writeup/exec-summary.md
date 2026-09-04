---
title: "Beyond a Bag of Concepts: does J-Lens recover relational binding?"
subtitle: "MATS 12.0 application — Neel Nanda stream"
author: "Jason Cusati"
date: "September 2026"
---
# Executive summary
## Research Question
J-Lens can show you the vocabulary and the bag of concepts at each step or layer, but is it able to read out the binding information, or is it just predicting what the model is about to answer?  
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
How do we know if the thoughts exposed by an interpretability lens are trustworthy enough to reveal what the model actually represents? I built a small task and experiment to measure, audit, and tell the difference between a guess and the actual answer.  
To answer this question, I built a dataset of prompts. Each prompt contains a pair, such as "Helen lives in Prague, and Mark lives in Oslo". For each prompt I swapped pairs changing who goes with what. I then used J-Lens, partway through the computation for the answer, to see if it could tell which city goes with which person. Both cities appear in every prompt, so a method that only detects concepts scores 50%, which is just chance. The intuition says that only binding-access beats chance.  However, there is a second way to beat chance, and that is by predicting the answer the model is about to give. My experiment is designed to distinguish between the two. 
## Methodology 
For my experiment I used Qwen3.5-4B with the released pre-fitted J-Lens. Qwen3.5-4B has 32 layers (0-31), with layer 31 being the final answer. J-Lens can read from any of the layers. Using the development dataset, I probed at various points in the prompt: after the facts, during the question, at the question mark, and right before the answer colon. At each of these points I measured the margin. I then froze the layer with the best margin at each position in the sentence. While running the lens I also saved the model's own answer preference at the same spot, so I could later check the lens on the records where the model itself was leaning wrong. 
Using the held-out data, I again probed at the frozen layers at each position to measure the margin. A positive value means the lens prefers the correct answer. The magnitude of that number measures how much it's preferred.  Of the 4 positions, the interesting one is just after the model is forced to start answering the question. 
## Results
J-Lens scored 0.781 vs 0.519 for a shuffled-label control at the end of the fact token. But the model's own next-token leaning was already right 0.800 of the time at that same spot. On the records where the model is wrong, the lens reduces to 0.344 and 0.125, well below chance. A probe trained with the answer key read 0.525 at the same spot where J-Lens read 0.781, so there was no binding signal there for it to find. My intuition here tells me the lens was guessing the model's answer, not reading its memory.  
![Direction score by position on frozen held-out data (n=160): both lenses rise at the token that pins down the answer and track the model's own next-token preference; the shuffled-label and random-transport controls stay at chance.](results/figures/stage3-frac-by-position.png){width=80%}
![J-Lens accuracy on held-out records, split by whether the model itself was leaning right or wrong. Where the model leaned wrong, every passive readout followed it below chance.](results/figures/stage3-discriminating-set.png){width=80%}
## Experiment 1 — Does J-Lens beat the logit lens at binding?
The dataset had 50 prompt pairs: 10 for development (40 records) and 40 held out (160 records), not looked at until the layers and positions were frozen. I ran J-Lens and the logit lens on the held-out records at the frozen positions and layers. The logit lens here is the same code with the Jacobian switched off, so the only thing that differs between the two is the Jacobian. At the relation token J-Lens scored 0.781 and the logit lens 0.688, both against a 0.519 shuffled-label control; at the question mark the logit lens was ahead, 0.738 to 0.669. Both beat the control, but the model's own next-token leaning was already right 80% of the time at that same spot. So on picking the right city it is a wash. Where J-Lens clearly wins is ranking: it puts the correct city at rank 35 of 248K, the logit lens near 1,000. Even so, it still does not appear to be reading any bindings at these layers.
## Experiment 2 — Do the controls hold?
In experiment 2, I used 2 controls. First I shuffled the labels. I took the 160 held-out records with the lens readings computed. For each record I randomly reassign which city is marked correct (drawn from the pool of 6 cities, using a fixed randomizer seed). Then I re-grade the lens reading against the shuffled key. The results were 0.52 at the relation token, 0.556 at the question mark, and 0.35 on the dev set (smaller number of cities). This rules out the model guessing based on unrelated info. The second control was a random matrix used in place of the prefit J-Lens matrix.  I ran the full pipeline with the same prompts and the random matrix using the same positions, layers, activations and scoring.  The resulting direction was 0.475-0.537 everywhere, and the correct city was a median rank of 130K-206K out of 248,320, versus 35 for the real matrix.
## Experiment 3 — What replaced the causal test
<!-- DRAFT by agent, plain words, for Jason to rewrite. Causal arm declared unavailable (V2); replaced by the discriminating set + supervised probe. -->
The causal test could not run: the released J-Lens code gives no way to separate its part of the residual from the rest. In its place I used the records where the model's own guess pointed to the wrong city (32 to 40 of the 160). A lens that reads binding should still get these right. J-Lens got 0.344 and 0.125, below chance. A probe trained with the answer key read 0.525 at the same spot, so no method found a binding signal there.
## High-level takeaways
<!-- Bullets. The most interesting thing first, not the chronology. Each
     bullet is a claim you can defend, with the number in it. If a takeaway is
     speculative, say so in the bullet — do not bury the hedge below. -->
- On the task I tested, J-Lens does NOT read what the model has stored for bindings - it simply guesses what the model is about to say. Where the model leaned wrong, J-Lens followed it: 0.344 and 0.125 against 0.500 chance.  
- J-Lens scoring used by most does not catch this; my method allows you to measure whether the readings are saying more than the model's output, making the use of a Lens more trustworthy.
- A probe trained with the answer key found nothing to read at the frozen position and layers I scored: 0.525, which is chance.
- J-Lens is better than previous lenses at ranking the right words. J-Lens vs Logit Lens had a ranking of 35 vs 1000 out of 248K words.  
## Biggest limitation
<!-- DRAFT by agent, plain words, for Jason to rewrite. Neel: name the real hole, not a decorative one. -->
One model, one released lens, one small task with six cities. At the position that matters most, even a probe trained with the answers found nothing, so I cannot say whether the binding is stored at some layer or position I did not read. I also did not test whether changing the residual changes the answer.
