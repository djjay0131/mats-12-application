#!/usr/bin/env python3
"""Step 2 tables + figure from a phase1-step2-fact-tokens run (analysis only)."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from figstyle import apply_style, PALETTE, DISPLAY, save_figure, chance_line

ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True); args = ap.parse_args()
d = json.loads((Path(args.run) / "outputs" / "step2-fact-tokens.json").read_text())
A3L = d["arm3_frozen_layer"]
GAP, ACC = 0.15, 0.65
print(f"run {args.run}  failures {d['fact_position_failures']}")
print("\n== arm 3 (diff-in-means, dev-fit, applied unchanged) -- combined held-out")
print(f"{'cell':16s} {'L30 acc':>8s} {'ctrl':>6s} {'n_sc':>5s} | {'devsel':>6s} {'acc':>6s} {'ctrl':>6s} | {'max L':>6s} {'acc':>6s} | dev LOPO L30 | R2.1")
verdict = {}
for cell, g in d["arm3"].items():
    pl = {int(k): v for k, v in g["per_layer"].items()}
    c = pl[A3L]["combined"]; sel = g["dev_selected_layer"]; cs = pl[sel]["combined"] if sel is not None else None
    best = max(pl, key=lambda l: (pl[l]["combined"]["acc"] or 0))
    ok = (c["acc"] or 0) >= ACC and ((c["acc"] or 0) - (c["ctrl_acc"] or 0)) >= GAP
    verdict[cell] = ok
    print(f"{cell:16s} {c['acc']:8.3f} {c['ctrl_acc']:6.3f} {c['n_scored']:5d} | L{sel:<5d} {cs['acc']:6.3f} {cs['ctrl_acc']:6.3f} | L{best:<5d} {pl[best]['combined']['acc']:6.3f} | {pl[A3L]['dev_lopo']['acc']:.3f} (n={pl[A3L]['dev_lopo']['n_scored']}) | {'READABLE' if ok else 'no'}")
print("\n== per split at L30 (arm 3): heldout / heldout2")
for cell, g in d["arm3"].items():
    pl = {int(k): v for k, v in g["per_layer"].items()}
    h, h2 = pl[A3L]["heldout"], pl[A3L]["heldout2"]
    print(f"{cell:16s} ho={h['acc']:.3f} (ctrl {h['ctrl_acc']:.3f}, n={h['n_scored']}/{h['n']})  ho2={h2['acc']:.3f} (ctrl {h2['ctrl_acc']:.3f}, n={h2['n_scored']}/{h2['n']})")
print("\n== lenses at fact tokens (pooled over roles), combined held-out")
P = d["lens_summary_pooled"]
for arm in ("jlens", "logitlens"):
    for typ, tn in (("city", "PERSON"), ("person", "CITY"), ("period", "PERSON"), ("period", "CITY")):
        pl = P[f"combined/{arm}/{typ}/{tn}"]
        x = pl[A3L]; best = max(pl, key=lambda z: z["frac"])
        r22 = (x["frac"] - x["ctrl_frac"]) >= GAP
        print(f"{arm:10s} {typ:7s} {tn:6s} L30 frac={x['frac']:.3f} ctrl={x['ctrl_frac']:.3f} n={x['n']} | max L{best['layer']} {best['frac']:.3f} (ctrl {best['ctrl_frac']:.3f}) | R2.2 at L30: {'READS' if r22 else 'no'}")
print("\n== lenses by sentence role at L30 (combined)")
S = d["lens_summary"]
for arm in ("jlens", "logitlens"):
    for k in ("city_q", "city_d", "period_q", "period_d", "person_q", "person_d"):
        for tn in (["PERSON"] if k.startswith("city") else ["CITY"] if k.startswith("person") else ["PERSON", "CITY"]):
            pl = S[f"combined/{arm}/{k}/{tn}"]; x = pl[A3L]
            print(f"{arm:10s} {k:9s} {tn:6s} frac={x['frac']:.3f} ctrl={x['ctrl_frac']:.3f} medrank={x['median_rank']} n={x['n']}")
print("\n== query anchors (combined), frozen layers")
FZ = d["freeze"]["layers"]
for arm in ("jlens", "logitlens"):
    for k in ("prequery", "relcomp", "qmark", "final"):
        l = int(FZ[arm][k]); x = S[f"combined/{arm}/{k}/CITY"][l]
        print(f"{arm:10s} {k:8s} L{l:<2d} CITY frac={x['frac']:.3f} ctrl={x['ctrl_frac']:.3f} medrank={x['median_rank']} n={x['n']}")

# figure: layer curves at the fact tokens
apply_style()
fig, axes = plt.subplots(1, 4, figsize=(12, 3.2), sharey=True)
cells = [("city", "PERSON"), ("person", "CITY"), ("period", "PERSON"), ("period", "CITY")]
for ax, (typ, tn) in zip(axes, cells):
    g = d["arm3"][f"{typ}/{tn}"]; pl = {int(k): v for k, v in g["per_layer"].items()}
    ls = sorted(pl); ax.plot(ls, [pl[l]["combined"]["acc"] or 0.5 for l in ls], color=PALETTE["prompting"], label="arm 3 (diff-in-means)")
    ax.plot(ls, [pl[l]["combined"]["ctrl_acc"] or 0.5 for l in ls], color=PALETTE["prompting"], linestyle=":", linewidth=1)
    for arm, col in (("jlens", PALETTE["jlens"]), ("logitlens", PALETTE["logit_lens"])):
        pl2 = P[f"combined/{arm}/{typ}/{tn}"]
        ax.plot([z["layer"] for z in pl2], [z["frac"] for z in pl2], color=col, label=DISPLAY["jlens" if arm == "jlens" else "logit_lens"])
        ax.plot([z["layer"] for z in pl2], [z["ctrl_frac"] for z in pl2], color=col, linestyle=":", linewidth=1)
    ax.axvline(A3L, color=PALETTE["control"], linewidth=0.8)
    ax.set_title(f"{typ} token -> {tn}", fontsize=10); ax.set_xlabel("block"); ax.set_ylim(0.2, 1.0)
    chance_line(ax)
axes[0].set_ylabel("two-way accuracy / direction frac"); axes[0].legend(fontsize=7.5, frameon=False, loc="upper left")
fig.tight_layout()
path = save_figure(fig, "phase1-step2-fact-tokens",
                   caption="Fact-token probes on the combined held-out (n=400 records, 800 fact tokens): arm 3 "
                           "(diff-in-means, dev-fit), J-Lens and logit lens at every block; dotted = "
                           "label-permutation control; vertical line = frozen L30.",
                   claim="phase1-step2", n="400 records / 800 tokens", seed="20260827 (control derangement)",
                   notes="agent-unverified; layer curves reported, not selected on")
print(f"wrote {path}")
