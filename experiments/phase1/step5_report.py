#!/usr/bin/env python3
"""Step 5 tables + figure from a phase1-step5-lr-probe run (analysis only)."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from figstyle import apply_style, PALETTE, save_figure, chance_line

ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True); args = ap.parse_args()
d = json.loads((Path(args.run) / "outputs" / "step5-lr-probe.json").read_text())
L = d["frozen_layer"]
print(f"run {args.run}  n_records={d['n_records']}  protocol={d['protocol']}")
print(f"\n{'cell':16s} {'LR L30':>7s} {'ctrl':>6s} {'DiM L30':>8s} {'ctrl':>6s} {'n_sc':>5s} | {'LR best':>8s} {'acc':>6s} | model-wrong LR (n) | DiM |  LR-DiM")
for cell, g in d["results"].items():
    pl = {int(k): v for k, v in g["per_layer"].items()}
    x = pl[L]; best = max(pl, key=lambda l: pl[l]["lr"]["acc"] or 0)
    mw = x.get("model_wrong")
    mws = (f"{mw['lr']['acc']:.3f} ({mw['lr']['n_scored']})   {mw['dim']['acc']:.3f}" if mw else "—")
    print(f"{cell:16s} {x['lr']['acc']:7.3f} {x['lr_ctrl']['acc']:6.3f} {x['dim']['acc']:8.3f} {x['dim_ctrl']['acc']:6.3f} {x['lr']['n_scored']:5d} | L{best:<7d} {pl[best]['lr']['acc']:6.3f} | {mws:22s} | {x['lr']['acc']-x['dim']['acc']:+.3f}")
print("\nlayer curve (LR acc / DiM acc) at relcomp and qmark, every 5 blocks + 30, 31:")
for cell in ("relcomp/CITY", "qmark/CITY", "period/CITY", "city/PERSON"):
    pl = {int(k): v for k, v in d["results"][cell]["per_layer"].items()}
    print(f"  {cell:14s} " + "  ".join(f"L{l}:{pl[l]['lr']['acc']:.2f}/{pl[l]['dim']['acc']:.2f}" for l in sorted(pl) if l % 5 == 0 or l >= 30))
print("\nmodel-wrong LR at relcomp by layer (every 5 + 30):")
pl = {int(k): v for k, v in d["results"]["relcomp/CITY"]["per_layer"].items()}
print("  " + "  ".join(f"L{l}:{pl[l]['model_wrong']['lr']['acc']:.2f}" for l in sorted(pl) if l % 5 == 0 or l >= 30))

apply_style()
fig, axes = plt.subplots(1, 4, figsize=(12, 3.2), sharey=True)
for ax, cell in zip(axes, ("relcomp/CITY", "qmark/CITY", "period/CITY", "city/PERSON")):
    pl = {int(k): v for k, v in d["results"][cell]["per_layer"].items()}; ls = sorted(pl)
    ax.plot(ls, [pl[l]["lr"]["acc"] or 0.5 for l in ls], color=PALETTE["jlens"], label="logistic regression")
    ax.plot(ls, [pl[l]["lr_ctrl"]["acc"] or 0.5 for l in ls], color=PALETTE["jlens"], linestyle=":", linewidth=1)
    ax.plot(ls, [pl[l]["dim"]["acc"] or 0.5 for l in ls], color=PALETTE["prompting"], label="difference-in-means")
    ax.plot(ls, [pl[l]["dim_ctrl"]["acc"] or 0.5 for l in ls], color=PALETTE["prompting"], linestyle=":", linewidth=1)
    if "model_wrong" in pl[ls[0]]:
        ax.plot(ls, [pl[l]["model_wrong"]["lr"]["acc"] or 0.5 for l in ls], color=PALETTE["logit_lens"], label="LR on model-wrong records")
    ax.axvline(L, color=PALETTE["control"], linewidth=0.8); ax.set_title(cell.replace("/", " -> "), fontsize=10)
    ax.set_xlabel("block"); ax.set_ylim(0.3, 1.02); chance_line(ax)
axes[0].set_ylabel("two-way accuracy (leave-one-pair-out)"); axes[0].legend(fontsize=7.5, frameon=False, loc="lower right")
fig.tight_layout()
path = save_figure(fig, "phase1-step5-lr-probe",
                   caption="Trained logistic-regression probe vs difference-in-means, leave-one-pair-out on the "
                           "combined held-out (n=400 records), every block; dotted = label-permutation control; "
                           "orange = LR accuracy on records where the model's own preference is wrong; vertical line = frozen L30.",
                   claim="phase1-step5", n="400 records / 100 pairs", seed="20260827 (control derangement)",
                   notes="agent-unverified; layer curves reported, not selected on")
print(f"wrote {path}")
