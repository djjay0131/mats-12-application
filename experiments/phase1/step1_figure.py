#!/usr/bin/env python3
"""Phase 1 step 1 figure: original vs new vs combined at the frozen settings.

Two panels from a phase1-step1-report run's step1-report.json:
  left  -- J-Lens direction frac vs its label-permutation control at the two
           primary positions, for original (n=160), new (n=240), combined (n=400)
  right -- lens accuracy on the records where the model's own next-token
           preference is wrong (with n), J-Lens and logit lens, same three sets
Rendered through src/figstyle.py::save_figure. Agent-unverified.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from figstyle import apply_style, PALETTE, DISPLAY, save_figure, chance_line, label_bars  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--report", required=True, help="phase1-step1-report run dir")
args = ap.parse_args()
rep = json.loads((Path(args.report) / "outputs" / "step1-report.json").read_text())
T = rep["table"]
SETS = ["original", "new", "combined"]
POS = ["relcomp", "qmark"]
PNAME = {"relcomp": "relation token", "qmark": "question mark"}

apply_style()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.6))

# left: frac vs control, grouped by set, one pair of bars per position
w = 0.36
xs = list(range(len(SETS) * len(POS)))
labels = []
for i, s in enumerate(SETS):
    for j, k in enumerate(POS):
        g = T[s]["jlens"][k]
        x = i * len(POS) + j
        ax1.bar(x - w / 2, g["frac"], w, color=PALETTE["jlens"],
                label=DISPLAY["jlens"] if (i, j) == (0, 0) else None)
        ax1.bar(x + w / 2, g["control_frac"], w, color=PALETTE["control"],
                label="label-permutation control" if (i, j) == (0, 0) else None)
        labels.append(f"{PNAME[k]}\n{s} n={g['n']}")
ax1.set_xticks(xs)
ax1.set_xticklabels(labels, fontsize=7.5)
ax1.set_ylim(0, 1.0)
ax1.set_ylabel("direction frac (correct city ranked above alternative)")
chance_line(ax1)
label_bars(ax1, fmt="{:.2f}", fontsize=7.5)
ax1.legend(loc="upper left", fontsize=8, frameon=False)
ax1.set_title("J-Lens vs control at the frozen positions", fontsize=10)

# right: accuracy on model-wrong records, jlens and logitlens
labels = []
for i, s in enumerate(SETS):
    for j, k in enumerate(POS):
        x = i * len(POS) + j
        gj = T[s]["jlens"][k]
        gl = T[s]["logitlens"][k]
        ax2.bar(x - w / 2, gj["acc_model_wrong"], w, color=PALETTE["jlens"],
                label=DISPLAY["jlens"] if (i, j) == (0, 0) else None)
        ax2.bar(x + w / 2, gl["acc_model_wrong"], w, color=PALETTE["logit_lens"],
                label=DISPLAY["logit_lens"] if (i, j) == (0, 0) else None)
        labels.append(f"{PNAME[k]}\n{s} n={gj['n_model_wrong']}")
ax2.set_xticks(xs)
ax2.set_xticklabels(labels, fontsize=7.5)
ax2.set_ylim(0, 1.0)
ax2.set_ylabel("lens accuracy on model-wrong records")
chance_line(ax2)
label_bars(ax2, fmt="{:.2f}", fontsize=7.5)
ax2.legend(loc="upper left", fontsize=8, frameon=False)
ax2.set_title("Where the model's own preference is wrong", fontsize=10)

fig.tight_layout()
v = rep["verdict"]
path = save_figure(
    fig, "phase1-step1-heldout2",
    caption=("Fresh held-out draw (seed 20260917, 60 pairs) scored once at the "
             "frozen settings, beside the application's draw and the pool. Left: "
             "J-Lens direction frac vs label-permutation control. Right: lens "
             "accuracy on records where the model's own next-token preference "
             "is wrong."),
    claim="phase1-step1",
    n="160 / 240 / 400",
    seed="20260917 (new draw); 20260827 (original, pool)",
    notes=(f"R1 gap(new, relcomp)={v['relcomp_gap_new']}; R2 combined "
           f"acc(model-wrong, relcomp)={v['combined_relcomp_acc_model_wrong']} "
           f"n={v['combined_relcomp_n_model_wrong']}; agent-unverified"))
print(f"wrote {path}")
