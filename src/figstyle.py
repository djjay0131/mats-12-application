"""House figure style for the MATS 12.0 write-up.

Every figure in the report goes through `save_figure`, which writes a
deterministic PNG into results/figures/ and appends a row to the figure
registry. That registry is what makes "record charts as we go" real: a
figure that is not registered does not exist as far as the report is
concerned, and every registered figure names the claim it supports.

Palette: slots 1-3 of the validated categorical set, which clear the
all-pairs CVD and normal-vision floors in light mode. Aqua sits below 3:1
against the surface, so `label_bars` writes visible value labels - identity
is never carried by colour alone.

Usage
-----
    from figstyle import apply_style, PALETTE, save_figure, label_bars
    apply_style()
    fig, ax = plt.subplots()
    ...
    save_figure(fig, "binding-accuracy-by-method",
                caption="Pairwise binding accuracy, J-Lens vs baselines.",
                claim="CL-02", n="40 held-out pairs", seed=1337)
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import pathlib
import subprocess

import matplotlib as mpl
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIGDIR = ROOT / "results" / "figures"
REGISTRY = FIGDIR / "FIGURE-REGISTRY.md"

# Validated categorical slots (light mode, all-pairs).
PALETTE = {
    "jlens":      "#2a78d6",  # slot 1 blue   - the method under test
    "logit_lens": "#eb6834",  # slot 2 orange - the baseline that matters
    "prompting":  "#1baf7a",  # slot 3 aqua   - the black-box baseline
    "control":    "#8a8a85",  # neutral       - random / chance / permuted
    "ink":        "#0b0b0b",
    "ink_soft":   "#52514e",
    "grid":       "#e3e3df",
    "surface":    "#ffffff",
}

# Fixed order. Never cycle; a fourth method folds into "Other" or a facet.
SERIES_ORDER = ["jlens", "logit_lens", "prompting", "control"]

DISPLAY = {
    "jlens": "J-Lens",
    "logit_lens": "Logit lens",
    "prompting": "Direct prompting",
    "control": "Chance / control",
}


def apply_style() -> None:
    """Recessive grid, thin marks, text in ink tokens rather than series colour."""
    mpl.rcParams.update({
        "figure.figsize": (6.4, 4.0),
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "figure.facecolor": PALETTE["surface"],
        "axes.facecolor": PALETTE["surface"],
        "axes.edgecolor": PALETTE["grid"],
        "axes.linewidth": 0.8,
        "axes.labelcolor": PALETTE["ink_soft"],
        "axes.titlecolor": PALETTE["ink"],
        "axes.titlesize": 11,
        "axes.titleweight": "semibold",
        "axes.titlelocation": "left",
        "axes.titlepad": 10,
        "axes.labelsize": 9.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": PALETTE["grid"],
        "grid.linewidth": 0.7,
        "xtick.color": PALETTE["ink_soft"],
        "ytick.color": PALETTE["ink_soft"],
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "legend.frameon": False,
        "legend.fontsize": 9,
        "lines.linewidth": 2.0,
        "lines.markersize": 5.5,
        "font.size": 10,
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    })


def label_bars(ax, fmt="{:.0%}", pad=3, fontsize=9) -> None:
    """Direct value labels. Required: this discharges the contrast relief rule."""
    from matplotlib.container import BarContainer
    for container in ax.containers:
        if not isinstance(container, BarContainer):
            continue                            # skip ErrorbarContainer
        labels = [fmt.format(p.get_height()) for p in container.patches]
        ax.bar_label(container, labels=labels, padding=pad,
                     fontsize=fontsize, color=PALETTE["ink_soft"])


def chance_line(ax, y=0.5, label="chance") -> None:
    """A binding-accuracy chart without its chance line invites overreading."""
    ax.axhline(y, color=PALETTE["control"], linewidth=1.2, linestyle=(0, (4, 3)), zorder=1)
    ax.annotate(label, xy=(1.0, y), xycoords=("axes fraction", "data"),
                xytext=(4, 0), textcoords="offset points",
                va="center", fontsize=8.5, color=PALETTE["ink_soft"])


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
            stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def save_figure(fig, slug: str, caption: str, claim: str = "",
                n: str = "", seed: str | int = "", notes: str = "") -> pathlib.Path:
    """Write the PNG and register it. Returns the path.

    `claim` should be the CL-nn id from llm/application/claims-register.md.
    A figure with no claim is a figure with no reason to be in the report.
    """
    FIGDIR.mkdir(parents=True, exist_ok=True)
    path = FIGDIR / f"{slug}.png"
    fig.savefig(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]

    row = (f"| `{slug}` | {caption} | {claim or '—'} | {n or '—'} | "
           f"{seed if seed != '' else '—'} | `{digest}` | {_git_commit()} | "
           f"{_dt.date.today().isoformat()} | {notes or ''} |")

    if not REGISTRY.exists():
        REGISTRY.write_text(_REGISTRY_HEADER)
    text = REGISTRY.read_text()
    lines, replaced = [], False
    for line in text.splitlines():
        if line.startswith(f"| `{slug}` |"):
            lines.append(row); replaced = True
        else:
            lines.append(line)
    if not replaced:
        lines.append(row)
    REGISTRY.write_text("\n".join(lines) + "\n")

    print(f"[figure] {path.relative_to(ROOT)}  sha={digest}  claim={claim or 'UNASSIGNED'}")
    if not claim:
        print("[figure] WARNING: no claim id. Register the claim or drop the figure.")
    return path


_REGISTRY_HEADER = """# Figure Registry

Every figure in the write-up, written by `src/figstyle.py::save_figure`.
Rows are rewritten in place when a figure is regenerated, so the sha and
commit always describe the file currently on disk.

A figure with no claim id has no reason to be in the report. A number in
the report that traces to no figure or table is caught separately by
`scripts/conformance-check.mjs` (BLK-24).

| Slug | Caption | Claim | n | Seed | SHA-256 (12) | Commit | Date | Notes |
|---|---|---|---|---|---|---|---|---|
"""
