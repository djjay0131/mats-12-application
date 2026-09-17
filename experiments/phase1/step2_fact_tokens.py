#!/usr/bin/env python3
"""Phase 1, step 2 -- probe the FACT tokens (and re-read the query positions).

Pre-registered in llm/memory_bank/research-learning-log.md ("Phase 1, step 2")
before this job is queued. No selection happens on held-out data; the only
selection is the dev-LOPO layer choice for arm 3, exactly the application's
protocol, and the frozen layer L30 is reported alongside regardless.

Positions per record (10): the four frozen query anchors (prequery, relcomp,
qmark, final) and six fact tokens -- person, city, period of the queried
person's sentence (role q) and of the distractor's (role d).

Readouts at every lens layer 0..30, both arms (J-Lens, logit lens), with the
label-permutation control. Two-way targets: at a city token PERSON (the
person stated in that sentence vs the other person); at a person token CITY;
at a period both; at query positions CITY (= the application's
"intermediate") and ANSWER.

Arm 3 (difference-in-means, nearest centroid): fit on dev, pooled over the
two sentence roles per token type; leave-one-PAIR-out on dev; applied
unchanged to heldout and heldout2; at every layer; label-permutation control.

Residuals at all 32 block outputs x 10 positions are saved OUTSIDE the repo
(--residual-dir) for step 5's trained probe. Every number agent-unverified.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (QPOS, FPOS, FACT_TARGETS, FREEZE, load_all,  # noqa: E402
                    load_model_and_lens, anchored_positions, fact_positions,
                    person_ids, targets_for, two_way, derangement,
                    fit_centroids, margin_of, MODEL_ID, MODEL_REV, LENS_REPO,
                    LENS_REV)
from jlens.hooks import ActivationRecorder                    # noqa: E402
from runlog import start_run                                   # noqa: E402

ARMS = [("jlens", True), ("logitlens", False)]
A3L = int(FREEZE["layers"]["arm3"])


def pos_family(k):
    if k in QPOS:
        return "query", None
    typ, role = k.split("_")
    return typ, role


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260827)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--residual-dir", required=True,
                    help="OUTSIDE the repo; residuals for step 5")
    ap.add_argument("--max-records", type=int, default=0, help="smoke test only")
    args = ap.parse_args()

    splits = load_all()
    if args.max_records:
        splits = [(s, r[:args.max_records]) for s, r in splits]
    run = start_run("phase1-step2-fact-tokens", seed=args.seed,
                    model_repo=MODEL_ID, model_revision=MODEL_REV,
                    lens_repo=LENS_REPO, lens_revision=LENS_REV,
                    freeze="experiments/stage3/freeze.json",
                    residual_dir=args.residual_dir,
                    note="fact-token probes at all layers; arm 3 dev-fit LOPO; no held-out selection")
    rdir = Path(args.residual_dir)
    rdir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    tok, hf, lm, lens = load_model_and_lens(args.device)
    n_layers = lm.n_layers                       # 32 blocks: 0..31
    lens_layers = list(lens.source_layers)       # 0..30
    print(f"[step2] {lens!r} n_layers={n_layers} load={time.time()-t0:.1f}s", flush=True)

    perms = {s: derangement(len(r), args.seed) for s, r in splits}
    records = []            # per record, per arm: two-way scores at every layer
    shadow = []
    resid = {}              # split -> list of [10, n_layers, d] fp16
    fails = defaultdict(int)
    ALLPOS = QPOS + FPOS

    for split, recs in splits:
        resid[split] = []
        pids = [person_ids(tok, r) for r in recs]
        for i, r in enumerate(recs):
            prompt = r["prompt"]
            ids = lm.encode(prompt)
            qpos, qtoks, align = anchored_positions(tok, prompt, ids)
            fpos, ftoks, ffail = fact_positions(tok, prompt, r, ids, align["bos_offset"])
            for f in ffail:
                fails[f"{split}:{f.split(':')[0]}"] += 1
            pos = {**qpos, **fpos}
            with ActivationRecorder(lm.layers, at=list(range(n_layers))) as rec:
                with torch.no_grad():
                    lm.forward(ids)
                acts = {l: rec.activations[l][0].detach() for l in range(n_layers)}
            # residual store [10, n_layers, d] (None positions -> zeros, flagged)
            store = torch.zeros(len(ALLPOS), n_layers, lm.d_model, dtype=torch.float16)
            for pi, k in enumerate(ALLPOS):
                if pos[k] is not None:
                    for l in range(n_layers):
                        store[pi, l] = acts[l][pos[k]].to(torch.float16).cpu()
            resid[split].append(store)
            model_row = lm.unembed(acts[n_layers - 1].float()).float().cpu()  # [seq, vocab]

            tg = targets_for(r, *pids[i])
            other = recs[perms[split][i]]
            tg_o = targets_for(other, *pids[perms[split][i]])
            entry = {"split": split, "record_id": r["record_id"], "pair_id": r["pair_id"],
                     "template_id": r["template_id"], "fact_order": r["fact_order"],
                     "variant": r["variant"], "permuted_from": other["record_id"],
                     "positions": pos, "position_tokens": {**qtoks, **ftoks},
                     "fact_failures": ffail, "arms": {}}
            for arm, use_j in ARMS:
                arm_scores = {}
                for l in lens_layers:
                    want = [k for k in ALLPOS if pos[k] is not None]
                    res = acts[l][[pos[k] for k in want]].float()
                    if use_j:
                        res = lens.transport(res, l)
                    with torch.no_grad():
                        rows = lm.unembed(res).float().cpu()
                    for k, row in zip(want, rows):
                        fam, role = pos_family(k)
                        if fam == "query":
                            tl = {"CITY": tg["query"]["CITY"], "ANSWER": tg["query"]["ANSWER"],
                                  "CITY_ctrl": tg_o["query"]["CITY"]}
                        else:
                            tl = {}
                            for tname in FACT_TARGETS[fam]:
                                tl[tname] = tg[role][tname]
                                tl[f"{tname}_ctrl"] = tg_o[role][tname]
                        d = arm_scores.setdefault(k, {})
                        for tname, (good, bad) in tl.items():
                            s = two_way(row, good, bad)
                            dd = d.setdefault(tname, {"rank_correct": [], "rank_incorrect": [],
                                                      "margin": [], "layers": []})
                            dd["rank_correct"].append(s["rank_correct"])
                            dd["rank_incorrect"].append(s["rank_incorrect"])
                            dd["margin"].append(round(s["margin"], 4))
                            dd["layers"].append(l)
                entry["arms"][arm] = arm_scores
            # the model's own next-token preference at each position
            sh = {}
            for k in ALLPOS:
                if pos[k] is None:
                    continue
                row = model_row[pos[k]]
                fam, role = pos_family(k)
                if fam == "query":
                    tl = {"CITY": tg["query"]["CITY"], "ANSWER": tg["query"]["ANSWER"]}
                else:
                    tl = {t: tg[role][t] for t in FACT_TARGETS[fam]}
                sh[k] = {t: two_way(row, g, b) for t, (g, b) in tl.items()}
            shadow.append({"split": split, "record_id": r["record_id"], "shadow": sh})
            records.append(entry)
            if (i + 1) % 40 == 0:
                print(f"[step2] {split} {i+1}/{len(recs)}  {time.time()-t0:.0f}s", flush=True)
        torch.save({"positions": ALLPOS, "layers": list(range(n_layers)),
                    "record_ids": [r["record_id"] for r in recs],
                    "pair_ids": [r["pair_id"] for r in recs],
                    "resid": torch.stack(resid[split])}, rdir / f"{split}.pt")
        print(f"[step2] saved residuals {split} -> {rdir / (split + '.pt')}", flush=True)

    # ------------------------------------------------------------- arm 3
    # items per (token_type, target): pooled over roles q/d; labels = token ids
    def items_for(split, recs, tokentype, target, layer):
        R = resid[split]
        out = []
        for i, r in enumerate(recs):
            pq, pd = person_ids(tok, r)
            tg = targets_for(r, pq, pd)
            other = recs[perms[split][i]]
            tg_o = targets_for(other, *person_ids(tok, other))
            keys = ([tokentype] if tokentype in QPOS
                    else [f"{tokentype}_q", f"{tokentype}_d"])
            for k in keys:
                pi = ALLPOS.index(k)
                if records_pos[(split, r["record_id"])][k] is None:
                    continue
                fam, role = pos_family(k)
                good, bad = (tg["query"][target] if fam == "query" else tg[role][target])
                g_o, b_o = (tg_o["query"][target] if fam == "query" else tg_o[role][target])
                out.append({"pair": r["pair_id"], "rid": r["record_id"], "pos": k,
                            "label": good, "alt": bad, "ctrl": (g_o, b_o),
                            "h": R[i][pi, layer].float()})
        return out

    records_pos = {(e["split"], e["record_id"]): e["positions"] for e in records}
    dev = dict(splits)["dev"]
    a3 = {}
    cells = [(k, "CITY") for k in QPOS] + [("city", "PERSON"), ("person", "CITY"),
                                           ("period", "PERSON"), ("period", "CITY")]
    for tokentype, target in cells:
        per_layer = {}
        for l in range(n_layers):
            dev_items = items_for("dev", dev, tokentype, target, l)
            # LOPO on dev
            pairs = sorted({it["pair"] for it in dev_items})
            loo = []
            for p in pairs:
                train = [(it["label"], it["h"]) for it in dev_items if it["pair"] != p]
                if len({lab for lab, _ in train}) < 2:
                    continue
                h_bar, mu, _ = fit_centroids(train)
                for it in dev_items:
                    if it["pair"] != p:
                        continue
                    m = margin_of(it["h"], h_bar, mu, it["label"], it["alt"])
                    mc = margin_of(it["h"], h_bar, mu, *it["ctrl"])
                    loo.append((m, mc))
            def summ(ms):
                sc = [m for m, _ in ms if m is not None]
                cc = [c for _, c in ms if c is not None]
                return {"n": len(ms), "n_scored": len(sc),
                        "acc": (round(sum(m > 0 for m in sc) / len(sc), 4) if sc else None),
                        "mean_margin": (round(sum(sc) / len(sc), 4) if sc else None),
                        "ctrl_n_scored": len(cc),
                        "ctrl_acc": (round(sum(c > 0 for c in cc) / len(cc), 4) if cc else None)}
            # dev fit on ALL dev, apply unchanged to the held-out sets
            all_train = [(it["label"], it["h"]) for it in dev_items]
            h_bar, mu, counts = fit_centroids(all_train)
            held = {}
            for split, recs in splits:
                if split == "dev":
                    continue
                its = items_for(split, recs, tokentype, target, l)
                held[split] = summ([(margin_of(it["h"], h_bar, mu, it["label"], it["alt"]),
                                     margin_of(it["h"], h_bar, mu, *it["ctrl"])) for it in its])
            comb_ms = []
            for split, recs in splits:
                if split == "dev":
                    continue
                its = items_for(split, recs, tokentype, target, l)
                comb_ms += [(margin_of(it["h"], h_bar, mu, it["label"], it["alt"]),
                             margin_of(it["h"], h_bar, mu, *it["ctrl"])) for it in its]
            held["combined"] = summ(comb_ms)
            per_layer[l] = {"dev_lopo": summ(loo), "dev_classes": len(counts), **held}
        usable = {l: v for l, v in per_layer.items()
                  if v["dev_lopo"]["mean_margin"] is not None}
        sel = (max(usable, key=lambda l: usable[l]["dev_lopo"]["mean_margin"])
               if usable else None)
        a3[f"{tokentype}/{target}"] = {
            "per_layer": per_layer, "dev_selected_layer": sel,
            "selection_rule": "argmax mean dev leave-one-pair-out margin (application protocol)",
            "frozen_layer": A3L}
        print(f"[arm3] {tokentype:8s} {target:6s} devsel=L{sel} "
              f"L{A3L}: devLOPO={per_layer[A3L]['dev_lopo']['acc']} "
              f"ho={per_layer[A3L]['heldout']['acc']} ho2={per_layer[A3L]['heldout2']['acc']} "
              f"comb={per_layer[A3L]['combined']['acc']} ctrl={per_layer[A3L]['combined']['ctrl_acc']}",
              flush=True)

    # ------------------------------------------------------------- lens summaries
    def lens_summary():
        out = {}
        for split, recs in splits + [("combined", None)]:
            ents = [e for e in records if (split == "combined" and e["split"] != "dev")
                    or e["split"] == split]
            for arm, _ in ARMS:
                for k in ALLPOS:
                    fam, role = pos_family(k)
                    # pool roles q/d for fact tokens under the token type
                    tnames = (["CITY", "ANSWER"] if fam == "query" else FACT_TARGETS[fam])
                    for tname in tnames:
                        rows = [e["arms"][arm][k][tname] for e in ents
                                if k in e["arms"][arm] and tname in e["arms"][arm][k]]
                        if not rows:
                            continue
                        ctrl = [e["arms"][arm][k][f"{tname}_ctrl"] for e in ents
                                if k in e["arms"][arm] and f"{tname}_ctrl" in e["arms"][arm][k]]
                        per_layer = []
                        for li, l in enumerate(rows[0]["layers"]):
                            fr = sum(x["rank_correct"][li] < x["rank_incorrect"][li] for x in rows) / len(rows)
                            cf = (sum(x["rank_correct"][li] < x["rank_incorrect"][li] for x in ctrl) / len(ctrl)
                                  if ctrl else None)
                            ranks = sorted(x["rank_correct"][li] for x in rows)
                            per_layer.append({"layer": l, "frac": round(fr, 4),
                                              "ctrl_frac": (round(cf, 4) if cf is not None else None),
                                              "median_rank": ranks[len(ranks) // 2],
                                              "n": len(rows)})
                        out[f"{split}/{arm}/{k}/{tname}"] = per_layer
        return out

    summary = lens_summary()
    # pooled-by-token-type view for fact tokens (q and d together)
    pooled = {}
    for split in ("heldout", "heldout2", "combined", "dev"):
        for arm, _ in ARMS:
            for typ in ("person", "city", "period"):
                for tname in FACT_TARGETS[typ]:
                    a = summary.get(f"{split}/{arm}/{typ}_q/{tname}")
                    b = summary.get(f"{split}/{arm}/{typ}_d/{tname}")
                    if not a or not b:
                        continue
                    pl = []
                    for x, y in zip(a, b):
                        n = x["n"] + y["n"]
                        pl.append({"layer": x["layer"],
                                   "frac": round((x["frac"] * x["n"] + y["frac"] * y["n"]) / n, 4),
                                   "ctrl_frac": (round((x["ctrl_frac"] * x["n"] + y["ctrl_frac"] * y["n"]) / n, 4)
                                                 if x["ctrl_frac"] is not None else None),
                                   "n": n})
                    pooled[f"{split}/{arm}/{typ}/{tname}"] = pl

    payload = {"framing": "method evaluation using a narrow task as instrument; not circuit discovery",
               "status": "agent-unverified",
               "freeze": FREEZE, "arm3_frozen_layer": A3L,
               "n_layers_model": n_layers, "lens_layers": lens_layers,
               "fact_position_failures": dict(fails),
               "residual_dir": str(rdir),
               "arm3": a3, "lens_summary": summary, "lens_summary_pooled": pooled,
               "records_file": "step2-records.json.gz",
               "seconds": round(time.time() - t0, 1)}
    out = run.outputs / "step2-fact-tokens.json"
    out.write_text(json.dumps(payload))
    import gzip
    with gzip.open(run.outputs / "step2-records.json.gz", "wt") as fh:
        json.dump({"records": records, "shadow": shadow}, fh)
    print("=" * 70)
    print(f"fact-position failures: {dict(fails)}")
    for key in ("combined/jlens/city/PERSON", "combined/jlens/person/CITY",
                "combined/jlens/period/PERSON", "combined/jlens/period/CITY",
                "combined/logitlens/city/PERSON", "combined/logitlens/period/CITY"):
        pl = pooled.get(key)
        if pl:
            x = pl[A3L]
            best = max(pl, key=lambda z: z["frac"])
            print(f"  {key:36s} L{A3L}: frac={x['frac']:.3f} ctrl={x['ctrl_frac']:.3f} n={x['n']}"
                  f"   max L{best['layer']}: {best['frac']:.3f}")
    for key in ("combined/jlens/relcomp/CITY", "combined/jlens/qmark/CITY",
                "combined/logitlens/relcomp/CITY"):
        pl = summary.get(key)
        if pl:
            l = int(FREEZE["layers"]["jlens" if "jlens" in key else "logitlens"][key.split("/")[2]])
            x = pl[l]
            print(f"  {key:36s} L{l}: frac={x['frac']:.3f} ctrl={x['ctrl_frac']:.3f} "
                  f"medrank={x['median_rank']} n={x['n']}")
    print(f"wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
