"""Experiment 2 figure: the two negative controls against the real J-Lens
readout on frozen held-out data. Run from repo root."""
import json, sys, pathlib
sys.path.insert(0, "src")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from figstyle import save_figure

RUN = "results/runs/20260830T175149Z-stage3-heldout-frozen/outputs/stage3-heldout-frozen.json"
d = json.load(open(RUN))
H = d["summary"]["heldout"]
POS = ["relcomp", "qmark"]
XLAB = ["relation token", "question mark"]

real = [H["jlens"][p]["frac"] for p in POS]
perm = [H["jlens"][p]["control_frac"] for p in POS]
rand = [H["jlens_random_transport"][p]["frac"] for p in POS]
rank_real = [H["jlens"][p]["median_rank"] for p in POS]
rank_rand = [H["jlens_random_transport"][p]["median_rank"] for p in POS]

fig, ax = plt.subplots(figsize=(7.2, 4.2))
w = 0.26
xs = range(len(POS))
b1 = ax.bar([i - w for i in xs], real, w, color="#0072B2", label="J-Lens, real answer key")
b2 = ax.bar([i for i in xs], perm, w, color="#555555", label="J-Lens, shuffled answer key")
b3 = ax.bar([i + w for i in xs], rand, w, color="#999999", label="random matrix in place of J-Lens")
ax.axhline(0.5, color="#D55E00", linestyle=":", linewidth=1.4)
ax.text(len(POS) - 0.55, 0.505, "chance", color="#D55E00", fontsize=8, va="bottom", ha="right")
for bars, vals in ((b1, real), (b2, perm), (b3, rand)):
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.012, f"{v:.3f}", ha="center", fontsize=8)
for i in xs:
    ax.text(i - w, 0.06, f"median rank\n{rank_real[i]:,}", ha="center", fontsize=7.5, color="white")
    ax.text(i + w, 0.06, f"median rank\n{rank_rand[i]:,}", ha="center", fontsize=7.5, color="white")
ax.set_xticks(list(xs)); ax.set_xticklabels(XLAB)
ax.set_ylim(0, 1.0)
ax.set_ylabel("direction score (fraction correct city > swapped city)")
ax.set_title("Experiment 2: both controls sit at chance; the trained matrix does the work")
ax.legend(fontsize=8, loc="upper left", frameon=False)
fig.tight_layout()
p = save_figure(fig, "stage3-controls",
    "Experiment 2 controls on frozen held-out data (n=160). Shuffling the answer key drops J-Lens to chance; replacing the trained matrix with a random one drops both the direction score to chance and the median rank of the correct city from about a hundred to over a hundred thousand.",
    claim="CL-02, CL-04", n="160", seed="20260827",
    notes="job 554591; label-permutation control and norm-matched random transport")
print("wrote", p)
