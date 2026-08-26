"""Figure generators for the write-up.

Each function takes a tidy structure and returns a registered PNG. Run with
`--placeholder` to render every figure from dummy data, watermarked so it can
never be mistaken for a result; that mode exists to keep the report building
end-to-end while experiments are still running.

    python src/make_figures.py --placeholder     # scaffold, watermarked
    python src/make_figures.py                   # real data from results/

Data contracts are documented on each function. Wire them to the real
pipeline as results land; do not change the report to match the figures.
"""
from __future__ import annotations

import argparse
import numpy as np
import matplotlib.pyplot as plt

from figstyle import (PALETTE, DISPLAY, apply_style, save_figure,
                      label_bars, chance_line)

PLACEHOLDER = False


def _watermark(ax):
    if not PLACEHOLDER:
        return
    ax.text(0.5, 0.5, "PLACEHOLDER\nNOT A RESULT", transform=ax.transAxes,
            ha="center", va="center", fontsize=22, fontweight="bold",
            color="#d94a48", alpha=0.20, rotation=24, zorder=10)


def fig_binding_accuracy(data: dict[str, tuple[float, float, float]]):
    """Primary result.

    data: {method_key: (accuracy, ci_low, ci_high)} for keys in
    ("jlens", "logit_lens", "prompting"). Accuracy is *pairwise* binding
    success — both orderings correct — so chance is 0.5, not 0.25.
    """
    apply_style()
    keys = [k for k in ("jlens", "logit_lens", "prompting") if k in data]
    vals = [data[k][0] for k in keys]
    lo = [data[k][0] - data[k][1] for k in keys]
    hi = [data[k][2] - data[k][0] for k in keys]

    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    ax.bar(range(len(keys)), vals, width=0.52,
           color=[PALETTE[k] for k in keys],
           yerr=[lo, hi], capsize=0,
           error_kw=dict(ecolor=PALETTE["ink_soft"], elinewidth=1.4))
    chance_line(ax, 0.5)
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels([DISPLAY[k] for k in keys])
    ax.set_ylabel("Pairwise binding accuracy")
    ax.set_ylim(0, 1.0)
    ax.set_title("Does the readout recover which entity fills which role?")
    ax.grid(axis="x", visible=False)
    label_bars(ax)
    _watermark(ax)
    return save_figure(
        fig, "binding-accuracy-by-method",
        caption="Pairwise binding accuracy by method, bootstrap 95% CIs. Chance 50%.",
        claim="CL-02", n="40 held-out pairs", seed=1337,
        notes="PLACEHOLDER DATA" if PLACEHOLDER else "")


def fig_layerwise_margin(layers, jlens, logit):
    """Correct-minus-alternative margin across the layer band.

    layers: list[int]; jlens/logit: same-length sequences of mean margin.
    """
    apply_style()
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.plot(layers, jlens, color=PALETTE["jlens"], label=DISPLAY["jlens"])
    ax.plot(layers, logit, color=PALETTE["logit_lens"], label=DISPLAY["logit_lens"])
    ax.axhline(0, color=PALETTE["control"], linewidth=1.0, linestyle=(0, (4, 3)))
    ax.set_xlabel("Layer")
    ax.set_ylabel("Correct − alternative margin")
    ax.set_title("Where in the stack does binding information appear?")
    ax.legend(loc="upper left")
    # Direct-label the final point of each series rather than every point.
    for series, key in ((jlens, "jlens"), (logit, "logit_lens")):
        ax.annotate(DISPLAY[key], xy=(layers[-1], series[-1]),
                    xytext=(6, 0), textcoords="offset points",
                    fontsize=8.5, color=PALETTE["ink_soft"], va="center")
    _watermark(ax)
    return save_figure(
        fig, "layerwise-margin",
        caption="Correct-minus-alternative margin across the layer band.",
        claim="CL-03", n="40 held-out pairs", seed=1337,
        notes="PLACEHOLDER DATA" if PLACEHOLDER else "")


def fig_controls_panel(controls: dict[str, tuple[float, float, float]]):
    """Falsification controls.

    controls: {label: (accuracy, ci_low, ci_high)}. Include the intact
    condition first so the collapse is visible against it.
    """
    apply_style()
    labels = list(controls)
    vals = [controls[k][0] for k in labels]
    lo = [controls[k][0] - controls[k][1] for k in labels]
    hi = [controls[k][2] - controls[k][0] for k in labels]
    colors = [PALETTE["jlens"]] + [PALETTE["control"]] * (len(labels) - 1)

    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.bar(range(len(labels)), vals, width=0.55, color=colors,
           yerr=[lo, hi], capsize=0,
           error_kw=dict(ecolor=PALETTE["ink_soft"], elinewidth=1.4))
    chance_line(ax, 0.5)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylabel("Pairwise binding accuracy")
    ax.set_ylim(0, 1.0)
    ax.set_title("A real binding signal should collapse under these")
    ax.grid(axis="x", visible=False)
    label_bars(ax)
    _watermark(ax)
    return save_figure(
        fig, "controls-panel",
        caption="Binding accuracy under relation deletion, truncation, and label permutation.",
        claim="CL-04", n="40 held-out pairs", seed=1337,
        notes="PLACEHOLDER DATA" if PLACEHOLDER else "")


def _placeholders():
    rng = np.random.default_rng(0)
    fig_binding_accuracy({
        "jlens":      (0.62, 0.50, 0.74),
        "logit_lens": (0.55, 0.43, 0.67),
        "prompting":  (0.71, 0.60, 0.82),
    })
    layers = list(range(12, 27))
    fig_layerwise_margin(
        layers,
        list(np.linspace(0.02, 0.30, len(layers)) + rng.normal(0, .02, len(layers))),
        list(np.linspace(0.01, 0.12, len(layers)) + rng.normal(0, .02, len(layers))))
    fig_controls_panel({
        "Intact":            (0.62, 0.50, 0.74),
        "Relation deleted":  (0.51, 0.39, 0.63),
        "Question truncated":(0.53, 0.41, 0.65),
        "Labels permuted":   (0.49, 0.37, 0.61),
    })


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--placeholder", action="store_true",
                    help="render every figure from dummy watermarked data")
    a = ap.parse_args()
    if a.placeholder:
        PLACEHOLDER = True
        globals()["PLACEHOLDER"] = True
        _placeholders()
    else:
        raise SystemExit("Real-data mode not wired yet. Call the fig_* functions "
                         "from your analysis notebook, or run --placeholder.")
