#!/usr/bin/env python3
"""Phase 1, step 5 -- a trained (logistic-regression) linear probe beside
difference-in-means, leave-one-pair-out on the COMBINED held-out set.

Pre-registered in llm/memory_bank/research-learning-log.md ("Phase 1, step 5")
before this job is queued. Reads the residuals step 2 saved outside the repo
(all 32 block outputs x 10 positions per record) and the step-2 record file
(position validity, the model's own preference per position).

Protocol, identical for both probes: 100 folds, one held-out PAIR per fold
(heldout 40 pairs + heldout2 60 pairs = all pairs of the combined set);
fit on the other pairs' records; score the held-out pair's records with the
two-way margin correct-vs-alternative (unscorable if either class is absent
from the training fold). Logistic regression: sklearn, lbfgs, C=1.0,
standardised features (scaler fit on the training fold only), multinomial
over the token-id classes present in the fold. Difference-in-means: the
application's fit_centroids / margin_of. Label-permutation control for both.

Cells: query anchors (prequery, relcomp, qmark, final; target CITY) and fact
tokens pooled over sentence role (city -> PERSON, person -> CITY, period ->
PERSON and CITY), at every block output. The FROZEN block (arm 3, L30) is
primary; the layer curve is reported. Every number agent-unverified.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import torch
from joblib import Parallel, delayed
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (QPOS, FPOS, FACT_TARGETS, FREEZE, load_all, person_ids,  # noqa: E402
                    targets_for, derangement, fit_centroids, margin_of)
from runlog import start_run                                   # noqa: E402

A3L = int(FREEZE["layers"]["arm3"])
ALLPOS = QPOS + FPOS


def fold_eval(layer, items, pairs, seed):
    """items: list of dicts(pair, label, alt, ctrl, h(np), rid, pos). Returns per-item results."""
    warnings.filterwarnings("ignore")
    X = np.stack([it["h"] for it in items]).astype(np.float32)
    y = np.array([it["label"] for it in items])
    out = []
    for p in pairs:
        te = [i for i, it in enumerate(items) if it["pair"] == p]
        tr = [i for i, it in enumerate(items) if it["pair"] != p]
        if not te:
            continue
        classes = sorted(set(y[tr].tolist()))
        if len(classes) < 2:
            continue
        sc = StandardScaler().fit(X[tr])
        Xtr = sc.transform(X[tr]); Xte = sc.transform(X[te])
        clf = LogisticRegression(C=1.0, max_iter=500, tol=1e-3)
        clf.fit(Xtr, y[tr])
        dec = clf.decision_function(Xte)
        if dec.ndim == 1:                        # binary: expand to 2 columns
            dec = np.stack([-dec, dec], axis=1)
        cidx = {c: j for j, c in enumerate(clf.classes_.tolist())}
        # difference-in-means on the same fold
        h_bar, mu, _ = fit_centroids([(int(y[i]), torch.from_numpy(X[i])) for i in tr])
        for j, i in enumerate(te):
            it = items[i]
            def lr_margin(a, b):
                if a in cidx and b in cidx:
                    return float(dec[j, cidx[a]] - dec[j, cidx[b]])
                return None
            hv = torch.from_numpy(X[i])
            out.append({"rid": it["rid"], "pos": it["pos"], "layer": layer,
                        "lr": lr_margin(it["label"], it["alt"]),
                        "lr_ctrl": lr_margin(*it["ctrl"]),
                        "dim": margin_of(hv, h_bar, mu, it["label"], it["alt"]),
                        "dim_ctrl": margin_of(hv, h_bar, mu, *it["ctrl"])})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--residual-dir", required=True)
    ap.add_argument("--step2-run", required=True, help="phase1-step2-fact-tokens run dir")
    ap.add_argument("--seed", type=int, default=20260827)
    ap.add_argument("--jobs", type=int, default=16)
    ap.add_argument("--layers", default="all")
    args = ap.parse_args()

    from transformers import AutoTokenizer
    from common import MODEL_ID, MODEL_REV
    tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV)

    run = start_run("phase1-step5-lr-probe", seed=args.seed,
                    residual_dir=args.residual_dir, step2_run=args.step2_run,
                    note="LR vs diff-in-means, leave-one-pair-out on combined held-out; no selection")
    t0 = time.time()
    splits = dict(load_all())
    with gzip.open(Path(args.step2_run) / "outputs" / "step2-records.json.gz", "rt") as fh:
        s2 = json.load(fh)
    positions = {(e["split"], e["record_id"]): e["positions"] for e in s2["records"]}
    shadow = {(e["split"], e["record_id"]): e["shadow"] for e in s2["shadow"]}

    # combined held-out residuals
    R, recs, tags = [], [], []
    for split in ("heldout", "heldout2"):
        d = torch.load(Path(args.residual_dir) / f"{split}.pt")
        assert d["positions"] == ALLPOS
        ids = d["record_ids"]
        by_id = {r["record_id"]: r for r in splits[split]}
        for i, rid in enumerate(ids):
            R.append(d["resid"][i]); recs.append(by_id[rid]); tags.append(split)
    n_layers = R[0].shape[1]
    layers = (list(range(n_layers)) if args.layers == "all"
              else [int(x) for x in args.layers.split(",")])
    perm = derangement(len(recs), args.seed)
    pids = [person_ids(tok, r) for r in recs]
    tag_of = {r["record_id"]: t for r, t in zip(recs, tags)}
    print(f"[step5] combined n={len(recs)} layers={len(layers)} load={time.time()-t0:.0f}s", flush=True)

    cells = [(k, "CITY") for k in QPOS] + [("city", "PERSON"), ("person", "CITY"),
                                           ("period", "PERSON"), ("period", "CITY")]

    def build_items(tokentype, target, layer):
        items = []
        for i, r in enumerate(recs):
            tg = targets_for(r, *pids[i])
            o = perm[i]
            tg_o = targets_for(recs[o], *pids[o])
            keys = [tokentype] if tokentype in QPOS else [f"{tokentype}_q", f"{tokentype}_d"]
            for k in keys:
                if positions[(tags[i], r["record_id"])][k] is None:
                    continue
                fam = "query" if k in QPOS else k.split("_")[1]
                good, bad = tg["query"][target] if fam == "query" else tg[fam][target]
                g_o, b_o = tg_o["query"][target] if fam == "query" else tg_o[fam][target]
                items.append({"pair": r["pair_id"], "rid": r["record_id"], "pos": k,
                              "label": good, "alt": bad, "ctrl": (g_o, b_o),
                              "h": R[i][ALLPOS.index(k), layer].float().numpy()})
        return items

    def summ(rows, key):
        sc = [x[key] for x in rows if x[key] is not None]
        return {"n": len(rows), "n_scored": len(sc),
                "acc": (round(sum(m > 0 for m in sc) / len(sc), 4) if sc else None),
                "mean_margin": (round(float(np.mean(sc)), 4) if sc else None)}

    results = {}
    for tokentype, target in cells:
        tasks = []
        for l in layers:
            items = build_items(tokentype, target, l)
            pairs = sorted({it["pair"] for it in items})
            tasks.append((l, items, pairs))
        outs = Parallel(n_jobs=args.jobs)(delayed(fold_eval)(l, items, pairs, args.seed)
                                          for l, items, pairs in tasks)
        per_layer = {}
        for (l, items, pairs), rows in zip(tasks, outs):
            cell = {m: summ(rows, m) for m in ("lr", "lr_ctrl", "dim", "dim_ctrl")}
            # model-wrong split at query positions (model CITY preference < 0)
            if tokentype in QPOS:
                wrong = [x for x in rows
                         if shadow.get((tag_of[x["rid"]], x["rid"]), {})
                         .get(tokentype, {}).get("CITY", {}).get("margin", 0) < 0]
                cell["model_wrong"] = {m: summ(wrong, m) for m in ("lr", "dim")}
            per_layer[l] = cell
        results[f"{tokentype}/{target}"] = {"per_layer": per_layer, "frozen_layer": A3L}
        g = per_layer[A3L]
        print(f"[step5] {tokentype:8s} {target:6s} L{A3L}: LR acc={g['lr']['acc']} "
              f"(ctrl {g['lr_ctrl']['acc']}) DiM acc={g['dim']['acc']} (ctrl {g['dim_ctrl']['acc']}) "
              f"n_scored={g['lr']['n_scored']}/{g['lr']['n']}"
              + (f"  model-wrong LR={g['model_wrong']['lr']['acc']} n={g['model_wrong']['lr']['n_scored']}"
                 if "model_wrong" in g else "")
              + f"   best LR layer: L{max(per_layer, key=lambda x: per_layer[x]['lr']['acc'] or 0)}"
              f"={max(v['lr']['acc'] or 0 for v in per_layer.values()):.3f}   {time.time()-t0:.0f}s",
              flush=True)

    payload = {"framing": "method evaluation using a narrow task as instrument; not circuit discovery",
               "status": "agent-unverified", "freeze": FREEZE, "frozen_layer": A3L,
               "protocol": {"folds": "leave-one-pair-out on combined held-out (heldout + heldout2)",
                            "lr": "sklearn LogisticRegression(C=1.0, lbfgs, max_iter=500, tol=1e-3), "
                                  "StandardScaler fit on the training fold",
                            "dim": "supervised_reference.fit_centroids / margin_of on the same fold",
                            "control": "label permutation (derangement, seed %d)" % args.seed},
               "n_records": len(recs), "layers": layers, "results": results,
               "seconds": round(time.time() - t0, 1)}
    out = run.outputs / "step5-lr-probe.json"
    out.write_text(json.dumps(payload, indent=1))
    print(f"wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
