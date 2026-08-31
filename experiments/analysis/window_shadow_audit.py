"""Window-shadow audit over the Stage 3 frozen run: was the query-window
direction signal a recovered latent, or the model reading ahead?

METHOD EVALUATION using a narrow task as instrument; not circuit discovery.

The Stage 3 run measured, for the first time, the model's own next-token
distribution at relcomp and qmark. The Hour 4 pre-registered prediction said
that shadow would be near zero there. This script checks that prediction per
record and, where it fails, asks the only question that then matters: on the
records where the shadow points the WRONG way (the discriminating set), does
the lens follow the shadow down, or does it beat it?

Also audits the label-permutation control for vocabulary collisions: with a
six-city pool, a deranged record's label pair can coincide with the record's
own pair (same or swapped order), which changes what the control means.

No GPU. Reads one committed Stage 3 run record. Every number agent-unverified.
"""
from __future__ import annotations

import argparse
import json
import sys
from math import sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from runlog import start_run  # noqa: E402

POS = ["prequery", "relcomp", "qmark", "final"]


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / sqrt(sxx * syy)


ap = argparse.ArgumentParser()
ap.add_argument("--run", required=True, help="stage3-heldout-frozen run dir")
args = ap.parse_args()

src = Path(args.run) / "outputs" / "stage3-heldout-frozen.json"
d = json.loads(src.read_text())
recs = d["records"]
shadow = {(x["split"], x["record_id"], x["position"]): x for x in d["shadow"]}
dev_ids = {}
for line in Path("results/datasets/dev.jsonl").read_text().splitlines():
    r = json.loads(line)
    if not r.get("_meta"):
        dev_ids[r["record_id"]] = (r["intermediate_id"], r["alt_intermediate_id"])
ho_ids = {}
for line in Path("results/datasets/heldout.jsonl").read_text().splitlines():
    r = json.loads(line)
    if not r.get("_meta"):
        ho_ids[r["record_id"]] = (r["intermediate_id"], r["alt_intermediate_id"])
ids = {"dev": dev_ids, "heldout": ho_ids}

run = start_run("stage3-window-shadow-audit", seed=d["dev_meta"].get("seed"),
                source_run=args.run,
                note="record-level attribution of the query-window direction signal")

out = {"framing": d["framing"], "status": "agent-unverified",
       "source_run": args.run, "coupling": {}, "discriminating": {},
       "control_collisions": {}, "prediction_check": {}}

print(f"source: {src}")
print()
print("A. shadow at each position (prediction said ~0 at relcomp/qmark)")
for s in ("dev", "heldout"):
    for k in POS:
        rows = [x for x in d["shadow"] if x["split"] == s and x["position"] == k]
        if not rows:
            continue
        ms = [x["intermediate_margin"] for x in rows]
        pos_frac = sum(m > 0 for m in ms) / len(ms)
        out["prediction_check"][f"{s}/{k}"] = {
            "mean": round(sum(ms) / len(ms), 4), "frac_positive": round(pos_frac, 4),
            "n_negative": sum(m < 0 for m in ms), "n": len(ms)}
        print(f"  {s:8s} {k:8s} mean={sum(ms)/len(ms):+.3f} "
              f"shadowFracPositive={pos_frac:.3f} neg={sum(m<0 for m in ms)}/{len(ms)}")
print()
print("B. lens frac vs the shadow's own frac, and per-record coupling r")
for s in ("dev", "heldout"):
    for arm in ("jlens", "logitlens"):
        for k in POS:
            rows = [x for x in recs if x["split"] == s and x["arm"] == arm
                    and x["scores"].get(k)
                    and (s, x["record_id"], k) in shadow]
            if not rows:
                continue
            lm = [x["scores"][k]["intermediate"]["margin"] for x in rows]
            sm = [shadow[(s, x["record_id"], k)]["intermediate_margin"] for x in rows]
            lens_frac = sum(x["scores"][k]["intermediate"]["rank_correct"]
                            < x["scores"][k]["intermediate"]["rank_incorrect"]
                            for x in rows) / len(rows)
            shad_frac = sum(m > 0 for m in sm) / len(sm)
            r = pearson(lm, sm)
            out["coupling"][f"{s}/{arm}/{k}"] = {
                "lens_frac": round(lens_frac, 4), "shadow_frac": round(shad_frac, 4),
                "r_lens_vs_shadow": (round(r, 4) if r is not None else None),
                "n": len(rows)}
            print(f"  {s:8s} {arm:10s} {k:8s} lensFrac={lens_frac:.3f} "
                  f"shadowFrac={shad_frac:.3f} r={r:+.3f} n={len(rows)}")
print()
print("C. THE DISCRIMINATING SET: records where the shadow points the wrong way")
for s in ("dev", "heldout"):
    for arm in ("jlens", "logitlens"):
        for k in ("relcomp", "qmark", "final"):
            rows = [x for x in recs if x["split"] == s and x["arm"] == arm
                    and x["scores"].get(k)
                    and (s, x["record_id"], k) in shadow]
            neg = [x for x in rows
                   if shadow[(s, x["record_id"], k)]["intermediate_margin"] < 0]
            posr = [x for x in rows
                    if shadow[(s, x["record_id"], k)]["intermediate_margin"] > 0]
            def acc(g):
                if not g:
                    return None
                return sum(x["scores"][k]["intermediate"]["rank_correct"]
                           < x["scores"][k]["intermediate"]["rank_incorrect"]
                           for x in g) / len(g)
            out["discriminating"][f"{s}/{arm}/{k}"] = {
                "n_shadow_wrong": len(neg),
                "lens_acc_on_shadow_wrong": (round(acc(neg), 4) if neg else None),
                "n_shadow_right": len(posr),
                "lens_acc_on_shadow_right": (round(acc(posr), 4) if posr else None)}
            a_n = acc(neg); a_p = acc(posr)
            print(f"  {s:8s} {arm:10s} {k:8s} shadowWRONG n={len(neg):3d} "
                  f"lensAcc={'--' if a_n is None else f'{a_n:.3f}'}   "
                  f"shadowRIGHT n={len(posr):3d} "
                  f"lensAcc={'--' if a_p is None else f'{a_p:.3f}'}")
print()
print("D. label-permutation control collision audit (six-city pool)")
for s in ("dev", "heldout"):
    rows = [x for x in recs if x["split"] == s and x["arm"] == "jlens"]
    same = swapped = disjoint = overlap1 = 0
    for x in rows:
        own = ids[s][x["record_id"]]
        other = ids[s][x["permuted_from"]]
        if other == own:
            same += 1
        elif (other[1], other[0]) == own:
            swapped += 1
        elif set(other) & set(own):
            overlap1 += 1
        else:
            disjoint += 1
    n = len(rows)
    out["control_collisions"][s] = {"n": n, "identical_pair": same,
                                    "swapped_pair": swapped,
                                    "one_shared_city": overlap1,
                                    "disjoint": disjoint}
    print(f"  {s:8s} n={n} identical={same} swapped={swapped} "
          f"oneShared={overlap1} disjoint={disjoint}")
print()
print("E. held-out by template (jlens, primary positions)")
bt = d.get("heldout_by_template_jlens", {})
for k, g in bt.items():
    print(f"  {k}: " + "  ".join(f"{t}={v['frac']:.2f}(n={v['n']})"
                                 for t, v in sorted(g.items())))
out["heldout_by_template_jlens"] = bt

(run.outputs / "window-shadow-audit.json").write_text(json.dumps(out, indent=1))
print(f"\nwrote {run.outputs / 'window-shadow-audit.json'}")
