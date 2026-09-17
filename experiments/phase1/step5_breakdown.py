#!/usr/bin/env python3
"""Step 5 addendum (reporting only, no rule): per-record LR / DiM margins at
the frozen block L30, broken down by fact order, sentence position, template
and the model's own preference. Same folds, same fits as step5_lr_probe.py
(imports fold_eval from it). Agent-unverified.
"""
from __future__ import annotations
import argparse, gzip, json, sys, time
from collections import defaultdict
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import QPOS, FPOS, FREEZE, load_all, person_ids, targets_for, derangement, MODEL_ID, MODEL_REV
from step5_lr_probe import fold_eval
from runlog import start_run

ALLPOS = QPOS + FPOS
A3L = int(FREEZE["layers"]["arm3"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--residual-dir", required=True); ap.add_argument("--step2-run", required=True)
    ap.add_argument("--seed", type=int, default=20260827); ap.add_argument("--layer", type=int, default=A3L)
    args = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV)
    run = start_run("phase1-step5-breakdown", seed=args.seed, layer=args.layer,
                    residual_dir=args.residual_dir, step2_run=args.step2_run,
                    note="reporting addendum: per-record LR/DiM margins at one block, breakdowns; no rule")
    t0 = time.time()
    splits = dict(load_all())
    with gzip.open(Path(args.step2_run) / "outputs" / "step2-records.json.gz", "rt") as fh:
        s2 = json.load(fh)
    positions = {(e["split"], e["record_id"]): e["positions"] for e in s2["records"]}
    shadow = {(e["split"], e["record_id"]): e["shadow"] for e in s2["shadow"]}
    R, recs, tags = [], [], []
    for split in ("heldout", "heldout2"):
        d = torch.load(Path(args.residual_dir) / f"{split}.pt"); by_id = {r["record_id"]: r for r in splits[split]}
        for i, rid in enumerate(d["record_ids"]):
            R.append(d["resid"][i]); recs.append(by_id[rid]); tags.append(split)
    perm = derangement(len(recs), args.seed); pids = [person_ids(tok, r) for r in recs]
    rec_of = {r["record_id"]: (r, t) for r, t in zip(recs, tags)}
    cells = [(k, "CITY") for k in QPOS] + [("city", "PERSON"), ("person", "CITY"), ("period", "PERSON"), ("period", "CITY")]
    out = {"layer": args.layer, "cells": {}}
    for tokentype, target in cells:
        items = []
        for i, r in enumerate(recs):
            tg = targets_for(r, *pids[i]); o = perm[i]; tg_o = targets_for(recs[o], *pids[o])
            keys = [tokentype] if tokentype in QPOS else [f"{tokentype}_q", f"{tokentype}_d"]
            for k in keys:
                if positions[(tags[i], r["record_id"])][k] is None:
                    continue
                fam = "query" if k in QPOS else k.split("_")[1]
                good, bad = tg["query"][target] if fam == "query" else tg[fam][target]
                g_o, b_o = tg_o["query"][target] if fam == "query" else tg_o[fam][target]
                items.append({"pair": r["pair_id"], "rid": r["record_id"], "pos": k, "label": good, "alt": bad,
                              "ctrl": (g_o, b_o), "h": R[i][ALLPOS.index(k), args.layer].float().numpy()})
        rows = fold_eval(args.layer, items, sorted({it["pair"] for it in items}), args.seed)
        # annotate
        for x in rows:
            r, t = rec_of[x["rid"]]
            x["fact_order"] = r["fact_order"]; x["template"] = r["template_id"]; x["variant"] = r["variant"]; x["split"] = t
            role = x["pos"].split("_")[1] if "_" in x["pos"] else None
            # sentence position: role q is first iff fact_order == AB
            x["sentence"] = None if role is None else ("first" if (role == "q") == (r["fact_order"] == "AB") else "second")
            if tokentype in QPOS:
                x["model_city_margin"] = shadow[(t, x["rid"])].get(tokentype, {}).get("CITY", {}).get("margin")
        def acc(sub, key):
            v = [x[key] for x in sub if x[key] is not None]
            return (round(sum(m > 0 for m in v) / len(v), 4), len(v)) if v else (None, 0)
        groups = {"all": rows,
                  "AB": [x for x in rows if x["fact_order"] == "AB"], "BA": [x for x in rows if x["fact_order"] == "BA"],
                  "heldout": [x for x in rows if x["split"] == "heldout"], "heldout2": [x for x in rows if x["split"] == "heldout2"]}
        for tpl in sorted({x["template"] for x in rows}):
            groups[f"template_{tpl}"] = [x for x in rows if x["template"] == tpl]
        if tokentype not in QPOS:
            groups["first_sentence"] = [x for x in rows if x["sentence"] == "first"]
            groups["second_sentence"] = [x for x in rows if x["sentence"] == "second"]
            groups["role_q"] = [x for x in rows if x["pos"].endswith("_q")]
            groups["role_d"] = [x for x in rows if x["pos"].endswith("_d")]
        else:
            groups["model_wrong"] = [x for x in rows if (x["model_city_margin"] or 0) < 0]
            groups["model_right"] = [x for x in rows if (x["model_city_margin"] or 0) > 0]
        summ = {g: {"lr": acc(sub, "lr"), "lr_ctrl": acc(sub, "lr_ctrl"), "dim": acc(sub, "dim"), "dim_ctrl": acc(sub, "dim_ctrl")}
                for g, sub in groups.items()}
        out["cells"][f"{tokentype}/{target}"] = {"summary": summ, "rows": rows}
        print(f"[{tokentype}/{target}] " + "  ".join(f"{g}: LR {v['lr'][0]} ({v['lr'][1]}) DiM {v['dim'][0]}"
                                                     for g, v in summ.items() if not g.startswith("template")), flush=True)
        print("    by template: " + "  ".join(f"{g[9:]}: {v['lr'][0]}" for g, v in summ.items() if g.startswith("template")), flush=True)
    (run.outputs / "step5-breakdown.json").write_text(json.dumps(out))
    print(f"wrote {run.outputs / 'step5-breakdown.json'}  {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
