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

![Pairwise binding accuracy by method, with bootstrap 95% CIs. Chance is 50%.](results/figures/binding-accuracy-by-method.png)

## Experiment 2 — Do the controls hold?

![Binding advantage under relation deletion, question truncation, and label permutation.](results/figures/controls-panel.png)

## Experiment 3 — <!-- causal arm, or the stronger passive control that replaced it -->

![](results/figures/layerwise-margin.png)

## Biggest limitation

<!-- One short paragraph. Neel: "It's OK if you show self-awareness of where
     the holes are... If you seem overconfident in shaky results, that is not."
     Name the real one, not a decorative one. -->

