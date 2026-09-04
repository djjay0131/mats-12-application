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
For my experiment I used Qwen3.5-4B with the released pre-fitted J-Lens. Qwen3.5-4B has 32 layers (0-31), with layer 31 being the final answer. J-Lens can read from any of the layers. Using the development dataset, I probed at various points in the prompt: after the facts, during the question, at the question mark, and right before the answer colon. At each of these point I measured the margin. I then froze the layer with the best margin at each position in the sentence. 
Using the held-out data, I again probed at the frozen layers at each position to measure the margin. A positive value means the lens prefers the correct answer. The magnitude of that number measures how much it's preferred.  Of the 4 popsitions, the interesting one is just after the model is forced to start answering the question. 
## Results
J-Lens scoore 0.781 vs 0.519 for a shuffled-label control end of the fact token. But the next token for the same position is 0.800. On the records where the model is wrong, the lnes redcues to 0.344 and 0.125, well below chance.  
![Direction score by position on frozen held-out data (n=160): both lenses rise at the token that pins down the answer and track the model's own next-token preference; the shuffled-label and random-transport controls stay at chance.](results/figures/stage3-frac-by-position.png){width=80%}
![J-Lens accuracy on held-out records, split by whether the model itself was leaning right or wrong. Where the model leaned wrong, every passive readout followed it below chance.](results/figures/stage3-discriminating-set.png){width=80%}
## High-level takeaways
<!-- Bullets. The most interesting thing first, not the chronology. Each
     bullet is a claim you can defend, with the number in it. If a takeaway is
     speculative, say so in the bullet — do not bury the hedge below. -->
- On the task I tested, J-Lens does NOT read what the model has stored for bindings - it simply guesses what the model is about to say.  
- J-Lens scoring used by most does not catch this; my method allows you to measure whether the readings are saying more than the model's output, making the use of a Lens more trustworthy.
- A probe trained with the answer key found nothing to read at the frozen position and layers I scored.
- J-Lens is better than previous lenses at ranking the right words. J-Lens vs Logit Lens had a ranking of 35 vs 1000 out of 248K words.  
- Key Limitaion: I tested just one model (Qwen3.5.4B), only tested on fitted lens, and only tested on small task.
