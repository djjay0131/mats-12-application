#!/usr/bin/env python
"""Real-data figures from the frozen held-out run (job 554591, n=160).

Reads results/runs/20260830T175149Z-stage3-heldout-frozen/outputs/
stage3-heldout-frozen.json and renders honest figures through figstyle
(auto-registered with a real sha/commit; notes left blank = not placeholder).

Three figures, telling both halves of the result:
  localization-by-position   J-Lens localizes the concept far better than the
                             logit lens (median rank, lower = better).  [win]
  direction-vs-shadow        the direction score tracks the model's own output
                             preference at every position.              [complication]
  supervised-ceiling         even a label-fit probe cannot recover binding off
                             the output-contaminated final token.       [why]
"""
import json, pathlib, sys
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from figstyle import apply_style, PALETTE, DISPLAY, save_figure, chance_line

RUN = ("results/runs/20260830T175149Z-stage3-heldout-frozen/outputs/"
       "stage3-heldout-frozen.json")
d = json.load(open(RUN))
H = d["summary"]["heldout"]
SH = d["shadow_summary"]["heldout"]
A3 = d["arm3"]

POS = ["prequery", "relcomp", "qmark", "final"]
XLAB = ["pre-query\n(reference)", "relation\ncompletes",
        "question\nmark", "final token\n(shadowed)"]
apply_style()

# ---- 1. localization: median rank, J-Lens vs logit lens (log scale) --------
fig, ax = plt.subplots()
x = np.arange(len(POS)); w = 0.38
jl = [H["jlens"][p]["median_rank"] for p in POS]
ll = [H["logitlens"][p]["median_rank"] for p in POS]
ax.bar(x - w/2, jl, w, label=DISPLAY["jlens"], color=PALETTE["jlens"])
ax.bar(x + w/2, ll, w, label=DISPLAY["logit_lens"], color=PALETTE["logit_lens"])
ax.set_yscale("log")
ax.set_ylim(8, 300000)
for xi, v in zip(x - w/2, jl):
    ax.annotate(f"{v:,}", (xi, v), ha="center", va="bottom", fontsize=8,
                color=PALETTE["ink_soft"])
for xi, v in zip(x + w/2, ll):
    ax.annotate(f"{v:,}", (xi, v), ha="center", va="bottom", fontsize=8,
                color=PALETTE["ink_soft"])
ax.set_xticks(x); ax.set_xticklabels(XLAB)
ax.set_ylabel("median rank of the correct concept\n(lower is better, of 248,320)")
ax.set_title("J-Lens localizes the bound concept far better than the logit lens")
ax.legend(loc="upper right")
save_figure(fig, "localization-by-position",
            "Median rank of the correct intermediate over the full vocabulary, "
            "J-Lens vs logit lens, at each readout position on the frozen "
            "held-out split. Lower is better. J-Lens's advantage is largest "
            "before the query (373 vs 76,276) and narrows as the model's own "
            "output preference arrives.",
            claim="CL-02", n="160", seed="20260827")
plt.close(fig)

# ---- 2. direction score tracks the output shadow ---------------------------
fig, ax = plt.subplots()
jl = [H["jlens"][p]["frac"] for p in POS]
ll = [H["logitlens"][p]["frac"] for p in POS]
rt = [H["jlens_random_transport"][p]["frac"] for p in POS]
shadow = [SH[p]["frac_positive"] for p in POS]
ax.plot(x, shadow, color=PALETTE["ink_soft"], linestyle=(0, (5, 2)), linewidth=1.8,
        marker="D", label="model's own next-token preference")
ax.plot(x, jl, color=PALETTE["jlens"], marker="o", label=DISPLAY["jlens"])
ax.plot(x, ll, color=PALETTE["logit_lens"], marker="s", label=DISPLAY["logit_lens"])
ax.plot(x, rt, color=PALETTE["control"], marker="^", linewidth=1.5,
        label="random transport (control)")
chance_line(ax, 0.5)
ax.set_xticks(x); ax.set_xticklabels(XLAB)
ax.set_ylim(0.4, 1.0)
ax.set_ylabel("direction score (fraction correct > alternative)")
ax.set_title("The lens direction score tracks the model's own output preference")
ax.legend(loc="upper left")
save_figure(fig, "direction-vs-shadow",
            "Direction score (correct intermediate outranks its role-swapped "
            "twin) by position, held-out n=160. J-Lens and the logit lens both "
            "rise with, and to, the model's own next-token preference (dashed); "
            "the norm-matched random transport stays at chance. The apparent "
            "binding signal is an output shadow, not recovered binding.",
            claim="CL-03", n="160", seed="20260827")
plt.close(fig)

# ---- 3. supervised ceiling: even labels can't recover binding off 'final' ---
fig, ax = plt.subplots()
acc = [A3[p]["heldout"]["accuracy"] for p in POS]
bars = ax.bar(x, acc, 0.55, color=PALETTE["prompting"])
for xi, v in zip(x, acc):
    ax.annotate(f"{v:.0%}", (xi, v), ha="center", va="bottom", fontsize=9,
                color=PALETTE["ink_soft"])
chance_line(ax, 0.5)
ax.set_xticks(x); ax.set_xticklabels(XLAB)
ax.set_ylim(0.0, 1.0)
ax.set_ylabel("held-out accuracy")
ax.set_title("Supervised ceiling: a label-fit probe barely beats chance until the shadow")
save_figure(fig, "supervised-ceiling",
            "Difference-in-means supervised probe (arm 3), fit on all dev "
            "records with labels in hand and applied unchanged to held-out "
            "(n=160). At the relation-completing token it reaches only 0.525 — "
            "chance — so binding is not linearly decodable there by any method; "
            "the accuracy it gains toward the final token is the same output "
            "shadow the passive readouts see.",
            claim="CL-03", n="160", seed="20260827")
plt.close(fig)
print("wrote 3 figures")
