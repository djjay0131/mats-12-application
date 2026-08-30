"""Stage 3: held-out evaluation at FROZEN settings.

METHOD EVALUATION using a narrow task as instrument; not circuit discovery.

The post-query sweep FOUND the informative positions on dev, which is the
textbook forking-paths setup. This run is what turns "we found a position" into
"there is a position": every evaluative choice is frozen in
experiments/stage3/freeze.json and results/stage2/FREEZE.md BEFORE this script
reads held-out. There is no argmax over layers here and no per-position
selection -- the script evaluates at the frozen settings and reports.

Positions are frozen by ANCHOR, not index (held-out spans templates T1-T6):
  relcomp  = token immediately preceding the final '?'   (primary)
  qmark    = the final '?'                                (primary)
  prequery = last token of the facts block                (reference: undetermined)
  final    = last prompt token                            (reference: contaminated)

The model's own next-token distribution is kept at EVERY scored position on
BOTH splits, so the output shadow at the primary positions is measured per
record here, not argued structurally.

Arm 3 is fit on ALL dev records and applied unchanged to held-out, at its
frozen layer.

Every number agent-unverified.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import jlens
from jlens import JacobianLens
from jlens.hooks import ActivationRecorder
from runlog import start_run

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "stage1"))
from passive_readout import (MODEL_ID, MODEL_REV, LENS_REPO, LENS_REV,  # noqa: E402
                             LENS_FILE, ranks_of, resolve_positions,
                             randomize_lens, derangement)
from supervised_reference import fit_centroids, margin_of               # noqa: E402

FREEZE = json.loads((Path(__file__).parent / "freeze.json").read_text())
POS = ["prequery", "relcomp", "qmark", "final"]
ARMS = [("jlens", True, False), ("logitlens", False, False),
        ("jlens_random_transport", True, True)]


def anchored_positions(tok, prompt, input_ids):
    """Anchor-resolved positions, verified against apply()'s own ids."""
    align = resolve_positions(tok, prompt, input_ids)
    qmark = None
    qc = prompt.rfind("?")
    if qc >= 0:
        enc = tok(prompt, return_offsets_mapping=True, add_special_tokens=False)
        for i, (a, b) in enumerate(enc["offset_mapping"]):
            if a <= qc < b:
                qmark = i + align["bos_offset"]
                break
    relcomp = qmark - 1 if qmark is not None and qmark >= 1 else None
    pos = {"prequery": align["prequery_idx"], "relcomp": relcomp,
           "qmark": qmark, "final": align["final_idx"]}
    ids = input_ids[0].tolist()
    toks = {k: (tok.convert_ids_to_tokens(ids[p]) if p is not None else None)
            for k, p in pos.items()}
    return pos, toks, align


def read_split(path, want):
    rows = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    meta = next((r for r in rows if r.get("_meta")), {})
    recs = [r for r in rows if not r.get("_meta")]
    if meta.get("split") != want:
        sys.exit(f"REFUSING: {path} split is {meta.get('split')!r}, wanted {want!r}")
    return meta, recs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev", default="results/datasets/dev.jsonl")
    ap.add_argument("--heldout", default="results/datasets/heldout.jsonl")
    ap.add_argument("--seed", type=int, default=20260827)
    ap.add_argument("--device", default="cuda")
    args = ap.parse_args()

    dev_meta, dev = read_split(args.dev, "dev")
    ho_meta, ho = read_split(args.heldout, "heldout")

    run = start_run("stage3-heldout-frozen", seed=args.seed,
                    model_repo=MODEL_ID, model_revision=MODEL_REV,
                    lens_repo=LENS_REPO, lens_revision=LENS_REV,
                    datasets=[args.dev, args.heldout],
                    freeze="experiments/stage3/freeze.json",
                    note="frozen evaluation; no selection happens in this run")

    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV)
    if hasattr(tok, "add_bos_token"):
        tok.add_bos_token = True
    try:
        hf = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REV,
                                                  dtype=torch.bfloat16)
    except TypeError:
        hf = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REV,
                                                  torch_dtype=torch.bfloat16)
    hf.to(args.device).eval()
    lm = jlens.from_hf(hf, tok)
    lens = JacobianLens.from_pretrained(LENS_REPO, filename=LENS_FILE,
                                        revision=LENS_REV)
    print(f"[stage3] {lens!r}  model_load={time.time()-t0:.1f}s  "
          f"dev n={len(dev)}  heldout n={len(ho)}", flush=True)

    JL = {k: int(v) for k, v in FREEZE["layers"]["jlens"].items()}
    LL = {k: int(v) for k, v in FREEZE["layers"]["logitlens"].items()}
    ARM_L = {"jlens": JL, "logitlens": LL, "jlens_random_transport": JL}
    A3L = int(FREEZE["layers"]["arm3"])

    splits = [("dev", dev), ("heldout", ho)]
    perms = {s: derangement(len(r), args.seed) for s, r in splits}
    results, shadow = [], []
    h_store = {s: [] for s, _ in splits}
    anchor_fail = {s: 0 for s, _ in splits}

    for arm_name, use_j, rand in ARMS:
        saved = randomize_lens(lens, args.seed) if rand else None
        try:
            for split, recs in splits:
                for i, r in enumerate(recs):
                    prompt = r["prompt"]
                    _, _, ids0 = lens.apply(lm, prompt, positions=[-1],
                                            use_jacobian=use_j)
                    pos, toks, align = anchored_positions(tok, prompt, ids0)
                    if pos["qmark"] is None and arm_name == "jlens":
                        anchor_fail[split] += 1
                    want, seen = [], set()
                    for k in POS:
                        p = pos[k]
                        if p is not None and p not in seen:
                            want.append(p); seen.add(p)
                    if arm_name == "jlens":
                        with ActivationRecorder(lm.layers, at=[A3L]) as rec:
                            with torch.no_grad():
                                lens_logits, model_logits, _ = lens.apply(
                                    lm, prompt, positions=want, use_jacobian=use_j)
                        act = rec.activations[A3L][0].detach().float().cpu()
                        h_store[split].append(
                            {k: (act[pos[k]].clone() if pos[k] is not None else None)
                             for k in POS})
                    else:
                        with torch.no_grad():
                            lens_logits, model_logits, _ = lens.apply(
                                lm, prompt, positions=want, use_jacobian=use_j)
                    ll = {int(l): v for l, v in lens_logits.items()}
                    other = recs[perms[split][i]]
                    targets = {
                        "intermediate": (r["intermediate_id"], r["alt_intermediate_id"]),
                        "answer": (r["answer_id"], r["alt_answer_id"]),
                        "control_label_permutation": (other["intermediate_id"],
                                                      other["alt_intermediate_id"]),
                    }
                    scores = {}
                    for k in POS:
                        p = pos[k]
                        if p is None:
                            scores[k] = None
                            continue
                        row = ll[ARM_L[arm_name][k]][want.index(p)]
                        rec_s = {}
                        for label, (good, bad) in targets.items():
                            rec_s[label] = {
                                "rank_correct": ranks_of(row, good),
                                "rank_incorrect": ranks_of(row, bad),
                                "margin": float(row[good] - row[bad]),
                            }
                        scores[k] = rec_s
                    results.append({"split": split, "arm": arm_name,
                                    "record_id": r["record_id"],
                                    "pair_id": r["pair_id"],
                                    "template_id": r.get("template_id"),
                                    "cell": r.get("cell"),
                                    "permuted_from": other["record_id"],
                                    "alignment_ok": align["alignment_ok"],
                                    "position_tokens": toks,
                                    "scores": scores})
                    # The model's own next-token distribution at each position,
                    # captured once (it does not depend on the lens arm).
                    if arm_name == "jlens" and model_logits is not None:
                        for k in POS:
                            p = pos[k]
                            if p is None:
                                continue
                            mrow = model_logits[want.index(p)].float()
                            shadow.append({
                                "split": split, "record_id": r["record_id"],
                                "template_id": r.get("template_id"),
                                "position": k, "token": toks[k],
                                "intermediate_margin": float(
                                    mrow[r["intermediate_id"]]
                                    - mrow[r["alt_intermediate_id"]]),
                                "answer_margin": float(
                                    mrow[r["answer_id"]] - mrow[r["alt_answer_id"]]),
                                "rank_intermediate": ranks_of(mrow, r["intermediate_id"]),
                                "rank_answer": ranks_of(mrow, r["answer_id"]),
                            })
                print(f"[stage3] {arm_name}: {split} done", flush=True)
        finally:
            if saved is not None:
                lens.jacobians = saved

    # -------------------------------------------- arm 3: fit dev, eval held-out
    arm3 = {}
    for k in POS:
        items = [(r["intermediate_id"], H[k])
                 for r, H in zip(dev, h_store["dev"]) if H[k] is not None]
        if len(items) < 2:
            arm3[k] = None
            continue
        h_bar, mu, counts = fit_centroids(items)

        def eval_on(recs, hs):
            ms = [margin_of(H[k], h_bar, mu, r["intermediate_id"],
                            r["alt_intermediate_id"])
                  if H[k] is not None else None
                  for r, H in zip(recs, hs)]
            sc = [m for m in ms if m is not None]
            return {"n": len(recs), "n_scored": len(sc),
                    "mean_margin": (sum(sc) / len(sc) if sc else None),
                    "accuracy": (sum(m > 0 for m in sc) / len(sc) if sc else None)}

        arm3[k] = {"layer": A3L, "fit_on": "dev, all records",
                   "class_counts": {str(c): n for c, n in counts.items()},
                   "dev_in_sample": eval_on(dev, h_store["dev"]),
                   "heldout": eval_on(ho, h_store["heldout"])}

    # ---------------------------------------------------------------- summaries
    def agg(split, arm_name, k):
        rows = [x for x in results
                if x["split"] == split and x["arm"] == arm_name and x["scores"].get(k)]
        if not rows:
            return None
        def frac(lbl):
            return sum(x["scores"][k][lbl]["rank_correct"]
                       < x["scores"][k][lbl]["rank_incorrect"] for x in rows) / len(rows)
        ranks = sorted(x["scores"][k]["intermediate"]["rank_correct"] for x in rows)
        return {"layer": ARM_L[arm_name][k], "n": len(rows),
                "frac": round(frac("intermediate"), 4),
                "control_frac": round(frac("control_label_permutation"), 4),
                "median_rank": ranks[len(ranks) // 2],
                "mean_margin": round(sum(x["scores"][k]["intermediate"]["margin"]
                                         for x in rows) / len(rows), 4),
                "mean_control_margin": round(
                    sum(x["scores"][k]["control_label_permutation"]["margin"]
                        for x in rows) / len(rows), 4)}

    summary = {s: {a: {k: agg(s, a, k) for k in POS}
                   for a, _, _ in ARMS} for s, _ in splits}

    by_template = {}
    for k in FREEZE["primary_positions"]:
        g = {}
        for x in results:
            if (x["split"] == "heldout" and x["arm"] == "jlens"
                    and x["scores"].get(k)):
                t = x["template_id"]
                e = g.setdefault(t, [0, 0])
                e[0] += int(x["scores"][k]["intermediate"]["rank_correct"]
                            < x["scores"][k]["intermediate"]["rank_incorrect"])
                e[1] += 1
        by_template[k] = {t: {"frac": round(a / b, 4), "n": b}
                          for t, (a, b) in sorted(g.items())}

    def shadow_agg(split, k):
        rows = [x for x in shadow if x["split"] == split and x["position"] == k]
        if not rows:
            return None
        ms = [x["intermediate_margin"] for x in rows]
        return {"n": len(rows),
                "mean_intermediate_margin": round(sum(ms) / len(ms), 4),
                "n_negative": sum(m < 0 for m in ms),
                "frac_positive": round(sum(m > 0 for m in ms) / len(ms), 4)}

    shadow_summary = {s: {k: shadow_agg(s, k) for k in POS} for s, _ in splits}

    payload = {
        "framing": "method evaluation using a narrow task as instrument; not circuit discovery",
        "claim_type": "confirmation run at frozen settings; no selection occurred in this run",
        "status": "agent-unverified",
        "freeze": FREEZE,
        "model": MODEL_ID, "model_revision": MODEL_REV,
        "lens_repo": LENS_REPO, "lens_revision": LENS_REV,
        "dev_meta": dev_meta, "heldout_meta": ho_meta,
        "anchor_failures": anchor_fail,
        "summary": summary,
        "heldout_by_template_jlens": by_template,
        "shadow_summary": shadow_summary,
        "arm3": arm3,
        "records": results,
        "shadow": shadow,
        "seconds": round(time.time() - t0, 1),
    }
    out = run.outputs / "stage3-heldout-frozen.json"
    out.write_text(json.dumps(payload, indent=1))

    print("\n" + "=" * 66)
    for s, _ in splits:
        for a, _, _ in ARMS:
            for k in POS:
                g = summary[s][a][k]
                if not g:
                    continue
                print(f"  {s:8s} {a:22s} {k:8s} L{g['layer']:<3d} "
                      f"frac={g['frac']:.3f} ctrl={g['control_frac']:.3f} "
                      f"medrank={g['median_rank']:>7d} n={g['n']}")
    print("-" * 66)
    for s, _ in splits:
        for k in POS:
            g = shadow_summary[s][k]
            if g:
                print(f"  shadow {s:8s} {k:8s} meanIntMargin={g['mean_intermediate_margin']:+.3f} "
                      f"neg={g['n_negative']}/{g['n']}")
    print("-" * 66)
    for k in POS:
        g = arm3.get(k)
        if g:
            d, h = g["dev_in_sample"], g["heldout"]
            print(f"  arm3   {k:8s} L{g['layer']} dev_acc={d['accuracy']:.3f} "
                  f"heldout_acc={h['accuracy']:.3f} heldout_scored={h['n_scored']}/{h['n']}")
    print("=" * 66)
    print(f"anchor failures: {anchor_fail}")
    print(f"wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
