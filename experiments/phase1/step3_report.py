#!/usr/bin/env python3
"""Step 3 tables + figure from a phase1-step3-patching run (analysis only).
Evaluates the pre-registered rule (agent's) at the primary cells on the
combined held-out and prints the layer curves."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from figstyle import apply_style, PALETTE, save_figure, chance_line

ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True); args = ap.parse_args()
d = json.loads((Path(args.run) / "outputs" / "step3-patching.json").read_text())
S = d["summary"]; PRIM = d["primary_cells"]; layers = d["layers"]
print(f"run {args.run}  layers={len(layers)}  skipped={d['skipped']}")
print(f"\n== primary cells (rule: twin flip >= 0.50 and >= 2x unrelated -> carries; <= unrelated+0.10 -> does not; else partial)")
print(f"{'set':9s} {'cell':13s} {'n':>4s} {'baseR':>5s} {'twin flip':>9s} {'d(all)':>7s} {'argmaxChg':>9s} | {'unrel flip':>10s} {'d(all)':>7s} | {'cos':>5s} | verdict")
verdict = {}
for name in ("dev", "heldout", "heldout2", "combined"):
    for k in ("prequery", "relcomp", "qmark", "final"):
        for l in PRIM[k]:
            g = S[name].get(f"{k}/{l}")
            if not g or not g["twin"]:
                continue
            t, u = g["twin"], g["unrelated"] or {}
            tf, uf = t["flip_rate"], u.get("flip_rate")
            v = ("carries" if (tf >= 0.5 and uf is not None and tf >= 2 * uf) else
                 "does not" if (uf is not None and tf <= uf + 0.10) else "partial")
            if name == "combined":
                verdict[f"{k}/{l}"] = v
            print(f"{name:9s} {k+'/L'+str(l):13s} {g['n']:4d} {g['n_base_right']:5d} {tf:9.3f} {g['twin_mean_delta_all']:+7.2f} {t['argmax_changed_rate']:9.3f} | "
                  f"{(uf if uf is not None else float('nan')):10.3f} {(g['unrelated_mean_delta_all'] if g['unrelated_mean_delta_all'] is not None else float('nan')):+7.2f} | {g['mean_cos_twin']:5.3f} | {v if name=='combined' else ''}")
print("\n== combined, layer curve: twin flip rate (unrelated flip rate) at every swept block")
for k in ("prequery", "relcomp", "qmark", "final"):
    row = []
    for l in layers:
        g = S["combined"].get(f"{k}/{l}")
        if g and g["twin"]:
            row.append(f"L{l}:{g['twin']['flip_rate']:.2f}({(g['unrelated'] or {}).get('flip_rate', float('nan')):.2f})")
    print(f"  {k:8s} " + " ".join(row))
print("\n== combined, mean margin change (twin) by block")
for k in ("prequery", "relcomp", "qmark", "final"):
    print(f"  {k:8s} " + " ".join(f"L{l}:{S['combined'][f'{k}/{l}']['twin_mean_delta_all']:+.2f}" for l in layers if f"{k}/{l}" in S["combined"]))
print("\n== combined, reverse flips on unpatched-wrong records (twin), primary blocks")
for k in ("prequery", "relcomp", "qmark", "final"):
    for l in PRIM[k]:
        g = S["combined"].get(f"{k}/{l}")
        if g:
            print(f"  {k}/L{l}: n_base_wrong={g['n_base_wrong']} reverse_flip={g['reverse_flip_rate_on_base_wrong']}")
print("\nverdicts (combined):", verdict)

apply_style()
fig, axes = plt.subplots(1, 4, figsize=(12, 3.2), sharey=True)
for ax, k in zip(axes, ("prequery", "relcomp", "qmark", "final")):
    ls = [l for l in layers if f"{k}/{l}" in S["combined"] and S["combined"][f"{k}/{l}"]["twin"]]
    ax.plot(ls, [S["combined"][f"{k}/{l}"]["twin"]["flip_rate"] for l in ls], color=PALETTE["jlens"], label="twin donor")
    ax.plot(ls, [(S["combined"][f"{k}/{l}"]["unrelated"] or {}).get("flip_rate", 0) for l in ls], color=PALETTE["control"], label="unrelated donor (norm-matched)")
    for l in PRIM[k]:
        ax.axvline(l, color=PALETTE["control"], linewidth=0.6, linestyle="--")
    ax.set_title(f"patch at {k}", fontsize=10); ax.set_xlabel("block"); ax.set_ylim(0, 1.02)
axes[0].set_ylabel("two-way flip rate (unpatched-right records)"); axes[0].legend(fontsize=7.5, frameon=False, loc="upper left")
fig.tight_layout()
path = save_figure(fig, "phase1-step3-patching",
                   caption="Twin activation patching on the combined held-out (n=400): fraction of unpatched-right "
                           "records whose answer flips to the twin's when one (anchor, block) residual is replaced; "
                           "grey = unrelated-record donor, norm-matched; dashed = frozen blocks.",
                   claim="phase1-step3", n="400 records", seed="20260827 (donor choice)",
                   notes="agent-unverified; layer curves reported, primary cells pre-registered")
print(f"wrote {path}")
