"""Control frac by position: the comparison the pre-registered rule names.

The summary reports the label-permutation control as a MARGIN. The rule says
"frac meaningfully above the label-perm control", so the control's own frac is
computed here on the same records, at the same selected layer, by the same
rule (rank_correct < rank_incorrect).

Reported two ways and both are labelled:
  A. PRE-REGISTERED -- at each position's own argmax-margin layer. This is the
     rule as written. Where every layer's margin is near zero the argmax is
     picking noise, so the selected layer wanders; that is a property of the
     rule, not a finding, and it is flagged.
  B. FIXED-LAYER sanity check at L27 and L30 -- NOT pre-registered, reported
     only to show whether A's shape survives holding the layer still.
"""
import json, sys, math
from pathlib import Path

RUN = sys.argv[1] if len(sys.argv) > 1 else "results/runs/20260829T155822Z-stage1-passive-readout"
SRC = Path(RUN) / "outputs" / "stage1-passive-readout.json"
print(f"source: {SRC}")
d = json.loads(SRC.read_text())
recs = d["records"]
summ = d["summary"]
ORDER = ["prequery"] + [f"q{i:02d}" for i in range(20)] + ["final"]
positions = [p for p in ORDER if p in recs[0]["scores"]]
arms = ["jlens", "logitlens", "jlens_random_transport"]

def frac2(rows, pos, layer, target):
    ok = [r["scores"][pos][str(layer)][target] for r in rows if r["scores"].get(pos)]
    if not ok:
        return None, 0
    hit = sum(1 for c in ok if c["rank_correct"] < c["rank_incorrect"])
    return hit / len(ok), len(ok)

def se(p, n):
    return math.sqrt(p * (1 - p) / n) if n else None

win = None
for r in recs:
    w = r.get("alignment", {}).get("query_window")
    if w:
        win = w
        break

print("query window tokens:")
print("  " + "  ".join(f"{k}={v['token']}" for k, v in (win or {}).items()))
print()
print("A. PRE-REGISTERED: each position at its own argmax-margin layer")
print(f"{'pos':9s} {'token':10s} | " + " | ".join(f"{a[:12]:>28s}" for a in arms))
print(f"{'':9s} {'':10s} | " + " | ".join(f"{'L   frac  ctrlfrac  medrank':>28s}" for a in arms))
for pos in positions:
    tok = "'.'" if pos == "prequery" else ("':'" if pos == "final"
           else (win or {}).get(pos, {}).get("token", "?"))
    cells = []
    for a in arms:
        s = summ[a].get(pos)
        if not s:
            cells.append(f"{'--':>28s}")
            continue
        L = s["selected_layer"]
        rows = [r for r in recs if r["arm"] == a]
        f_int, n = frac2(rows, pos, L, "intermediate")
        f_ctl, _ = frac2(rows, pos, L, "control_label_permutation")
        mr = s["at_selected_layer"]["median_rank_correct_intermediate"]
        cells.append(f"L{L:<3d} {f_int:.3f}  {f_ctl:.3f}  {mr:>9d}")
    print(f"{pos:9s} {tok:10s} | " + " | ".join(cells))

print()
print(f"n=40, chance floor 0.500, SE at 0.5 = {se(0.5,40):.3f}")
print()
for fixed in (27, 30):
    print(f"B. FIXED LAYER L{fixed} (NOT pre-registered; shape check only)")
    print(f"{'pos':9s} | " + " | ".join(f"{a[:20]:>22s}" for a in arms))
    for pos in positions:
        cells = []
        for a in arms:
            rows = [r for r in recs if r["arm"] == a]
            f_int, n = frac2(rows, pos, fixed, "intermediate")
            f_ctl, _ = frac2(rows, pos, fixed, "control_label_permutation")
            mrs = sorted(r["scores"][pos][str(fixed)]["intermediate"]["rank_correct"]
                         for r in rows if r["scores"].get(pos))
            cells.append(f"{f_int:.3f} ctl {f_ctl:.3f} r{mrs[len(mrs)//2]:>7d}")
        print(f"{pos:9s} | " + " | ".join(cells))
    print()
