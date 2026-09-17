#!/usr/bin/env python3
"""Cross-reference (analysis only): J-Lens / logit-lens direction frac at the
query anchors at EVERY lens layer on the combined held-out, split by the
model's own preference at that anchor (from step 2's records). Prints a table
and writes outputs/step2-layercurve.json into the given step-2 run dir."""
import argparse, gzip, json
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True); args = ap.parse_args()
with gzip.open(Path(args.run) / "outputs" / "step2-records.json.gz", "rt") as fh:
    d = json.load(fh)
sh = {(e["split"], e["record_id"]): e["shadow"] for e in d["shadow"]}
out = {}
for k in ("prequery", "relcomp", "qmark", "final"):
    for arm in ("jlens", "logitlens"):
        rows = [e for e in d["records"] if e["split"] != "dev" and k in e["arms"][arm]]
        layers = rows[0]["arms"][arm][k]["CITY"]["layers"]
        res = []
        for li, l in enumerate(layers):
            def right(e, key="CITY"):
                s = e["arms"][arm][k][key]; return s["rank_correct"][li] < s["rank_incorrect"][li]
            allr = [right(e) for e in rows]; ctrl = [right(e, "CITY_ctrl") for e in rows]
            wrong = [e for e in rows if sh[(e["split"], e["record_id"])][k]["CITY"]["margin"] < 0]
            wr = [right(e) for e in wrong]
            ranks = sorted(e["arms"][arm][k]["CITY"]["rank_correct"][li] for e in rows)
            res.append({"layer": l, "frac": round(sum(allr) / len(allr), 4), "ctrl": round(sum(ctrl) / len(ctrl), 4),
                        "median_rank": ranks[len(ranks) // 2],
                        "model_wrong_acc": (round(sum(wr) / len(wr), 4) if wr else None), "n_model_wrong": len(wr), "n": len(rows)})
        out[f"{k}/{arm}"] = res
        print(f"{k:8s} {arm:9s} n={len(rows)} model-wrong n={res[0]['n_model_wrong']}")
        print("   frac       " + " ".join(f"L{r['layer']}:{r['frac']:.2f}" for r in res if r["layer"] % 3 == 0 or r["layer"] >= 27))
        print("   modelWRONG " + " ".join(f"L{r['layer']}:{r['model_wrong_acc']:.2f}" for r in res if r["layer"] % 3 == 0 or r["layer"] >= 27))
        best = max(res, key=lambda r: r["frac"]); bw = max(res, key=lambda r: r["model_wrong_acc"] or 0)
        print(f"   max frac L{best['layer']} {best['frac']:.3f} (ctrl {best['ctrl']:.3f}, medrank {best['median_rank']}); max model-wrong L{bw['layer']} {bw['model_wrong_acc']:.3f}")
(Path(args.run) / "outputs" / "step2-layercurve.json").write_text(json.dumps(out, indent=1))
print("wrote step2-layercurve.json")
