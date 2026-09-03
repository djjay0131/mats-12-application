---
title: "Beyond a Bag of Concepts: does J-Lens recover relational binding?"
subtitle: "MATS 12.0 application — Neel Nanda stream"
author: "Jason Cusati"
date: "September 2026"
---

# Executive summary

Let's start with how I got here. For a while I have been thinking about how the screens that the operators are reading in the matrix relates to AI today or in the near future. I have had this idea that machines would write code, and execute the code in real time to do new things or in order to learn or invent new ways of doing things. And I viewed the operators terminal as this code flying by the AI's internal eyes. As I dug into your interests, and started reading the current research on Chain of Thought, a new idea spawned. 

The data inside of the brain of AI is made up of vectors of numbers. What if we could train humans to read those representations, just as the operators read the screens in the matrix? With that as the North Star, I began to understand how this could be done. 

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

<!-- 2-4 sentences. The J-Lens paper names its own limitation: a readout can
     list the right concepts without showing which entity fills which role —
     `spider`, `legs`, `eight` does not tell you what has eight of what. State
     the question and why a reader with mech interp experience should care.
     Assume zero context on this project; assume full context on the field. -->

## High-level takeaways

<!-- Bullets. The most interesting thing first, not the chronology. Each
     bullet is a claim you can defend, with the number in it. If a takeaway is
     speculative, say so in the bullet — do not bury the hedge below. -->

-
-
-

## Experiment 1 — Does J-Lens beat the logit lens at binding?

<!-- One paragraph: what it was, what you found, why it supports the takeaway.
     Then the figure. -->

![Direction score — correct intermediate outranks its role-swapped twin — by position, frozen held-out split, n=160. Both lenses rise with, and to, the model's own next-token preference (dashed); norm-matched random transport stays at chance.](results/figures/direction-vs-shadow.png)

## Experiment 2 — Do the controls hold?

![Median rank of the correct intermediate over the 248,320-token vocabulary at each readout position, held-out n=160, log scale. J-Lens's localization advantage is largest before the query (373 vs 76,276) and narrows as the model's own preference arrives.](results/figures/localization-by-position.png)

## Experiment 3 — <!-- causal arm, or the stronger passive control that replaced it -->

![Supervised difference-in-means probe (arm 3), fit on dev, applied unchanged to held-out (n=160). At the relation-completing token it reads chance (0.525) — binding is not linearly decodable there — and its later gains match the output shadow.](results/figures/supervised-ceiling.png)

## Biggest limitation

<!-- One short paragraph. Neel: "It's OK if you show self-awareness of where
     the holes are... If you seem overconfident in shaky results, that is not."
     Name the real one, not a decorative one. -->

