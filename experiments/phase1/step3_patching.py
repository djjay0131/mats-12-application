#!/usr/bin/env python3
"""Phase 1, step 3 -- activation patching between swapped twins.

Pre-registered in llm/memory_bank/research-learning-log.md ("Phase 1, step 3")
before this job is queued.

For every record X and its swapped twin Y (same pair, same fact order, other
binding variant; the prompts differ only in which city sits in each
person->place sentence), the residual at ONE (position, block) of X's forward
pass is replaced by Y's residual at the same (position, block) and the
model's answer margin at the final position is re-read:

    margin = logit[X's correct answer] - logit[Y's answer]   (Y's answer is
             exactly X's alternative answer, so this is the application's
             "answer_margin" at `final`)

Reported per cell: mean change in margin, two-way flip rate (margin > 0 before
and < 0 after, over records whose unpatched margin is > 0), and full-vocab
argmax changes. Cells: the four frozen anchors x every block output 0..31;
the FROZEN cells (freeze.json layers) are primary, the sweep is reported as a
curve. Controls: (a) the same patch from an UNRELATED record of the same
template / fact order / variant (norm-matched to X's own residual);
(b) patching the prequery period at the same block, which is the prequery
row of the same table. Dev is processed and printed first; the held-out sets
are then processed once. Every number agent-unverified.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (QPOS, FREEZE, load_all, load_model_and_lens,  # noqa: E402
                    anchored_positions, MODEL_ID, MODEL_REV)
from jlens.hooks import ActivationRecorder                    # noqa: E402
from runlog import start_run                                   # noqa: E402

PRIMARY = {}   # position -> sorted set of frozen layers (jlens, logitlens, arm3)
for k in QPOS:
    PRIMARY[k] = sorted({int(FREEZE["layers"]["jlens"][k]),
                         int(FREEZE["layers"]["logitlens"][k]),
                         int(FREEZE["layers"]["arm3"])})


class Patch:
    """Replace block output at one position with a given vector."""

    def __init__(self, blocks, layer, pos, vec):
        self.block, self.pos, self.vec = blocks[layer], pos, vec
        self.h = None

    def __enter__(self):
        def hook(module, inputs, output):
            out = output if torch.is_tensor(output) else output[0]
            out[:, self.pos, :] = self.vec.to(out.dtype).to(out.device)
        self.h = self.block.register_forward_hook(hook)
        return self

    def __exit__(self, *exc):
        self.h.remove()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260827)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--layers", default="all", help="'all' or comma list")
    ap.add_argument("--max-records", type=int, default=0, help="smoke test only")
    args = ap.parse_args()

    splits = load_all()
    if args.max_records:
        splits = [(s, r[:args.max_records]) for s, r in splits]
    run = start_run("phase1-step3-patching", seed=args.seed,
                    model_repo=MODEL_ID, model_revision=MODEL_REV,
                    freeze="experiments/stage3/freeze.json",
                    note="twin activation patching at frozen anchors, all blocks; unrelated-donor control")
    t0 = time.time()
    tok, hf, lm, lens = load_model_and_lens(args.device)
    n_layers = lm.n_layers
    layers = (list(range(n_layers)) if args.layers == "all"
              else [int(x) for x in args.layers.split(",")])
    final_block = n_layers - 1
    print(f"[step3] n_layers={n_layers} sweep={len(layers)} blocks load={time.time()-t0:.1f}s",
          flush=True)
    rng = random.Random(args.seed)

    def forward_final(ids, patch=None):
        with ActivationRecorder(lm.layers, at=[final_block]) as rec:
            with torch.no_grad():
                if patch is None:
                    lm.forward(ids)
                else:
                    with patch:
                        lm.forward(ids)
            act = rec.activations[final_block][0, -1].float()
        return lm.unembed(act).float().cpu()

    results = []
    skipped = defaultdict(int)
    for split, recs in splits:
        by_key = defaultdict(dict)
        for r in recs:
            by_key[(r["pair_id"], r["fact_order"])][r["variant"]] = r
        # cache: record_id -> (ids, positions, residuals[pos][layer])
        cache = {}
        for r in recs:
            ids = lm.encode(r["prompt"])
            pos, toks, align = anchored_positions(tok, r["prompt"], ids)
            with ActivationRecorder(lm.layers, at=layers) as rec:
                with torch.no_grad():
                    lm.forward(ids)
                res = {k: {l: rec.activations[l][0, pos[k]].detach().clone()
                           for l in layers} for k in QPOS if pos[k] is not None}
            cache[r["record_id"]] = (ids, pos, res, int(ids.shape[1]))
        print(f"[step3] {split}: cached {len(cache)} records  {time.time()-t0:.0f}s", flush=True)
        # unrelated donors: same template, fact_order, variant, different pair,
        # same token length; deterministic choice
        for i, r in enumerate(recs):
            ids, pos, own, n_tok = cache[r["record_id"]]
            twin = by_key[(r["pair_id"], r["fact_order"])].get("B" if r["variant"] == "A" else "A")
            if twin is None or any(pos[k] is None for k in QPOS):
                skipped[f"{split}:no-twin-or-anchor"] += 1
                continue
            _, tpos, tres, tn = cache[twin["record_id"]]
            if tpos != pos or tn != n_tok:
                skipped[f"{split}:twin-position-mismatch"] += 1
                continue
            cands = [c for c in recs if c["pair_id"] != r["pair_id"]
                     and c["template_id"] == r["template_id"]
                     and c["fact_order"] == r["fact_order"] and c["variant"] == r["variant"]
                     and cache[c["record_id"]][1] == pos and cache[c["record_id"]][3] == n_tok]
            unrel = rng.choice(cands) if cands else None
            if unrel is None:
                skipped[f"{split}:no-unrelated-donor"] += 1
            ures = cache[unrel["record_id"]][2] if unrel else None

            base = forward_final(ids)
            good, bad = r["answer_id"], r["alt_answer_id"]
            assert bad == twin["answer_id"], (r["record_id"], twin["record_id"])
            m0 = float(base[good] - base[bad])
            am0 = int(base.argmax())
            entry = {"split": split, "record_id": r["record_id"], "pair_id": r["pair_id"],
                     "template_id": r["template_id"], "twin": twin["record_id"],
                     "unrelated": (unrel["record_id"] if unrel else None),
                     "margin_before": round(m0, 4), "argmax_before": am0,
                     "argmax_before_tok": tok.convert_ids_to_tokens(am0),
                     "cells": {}}
            for k in QPOS:
                p = pos[k]
                for l in layers:
                    cell = {}
                    vx, vy = own[k][l].float(), tres[k][l].float()
                    cell["cos_twin"] = round(float(torch.nn.functional.cosine_similarity(
                        vx, vy, dim=0)), 4)
                    lg = forward_final(ids, Patch(lm.layers, l, p, tres[k][l]))
                    m1 = float(lg[good] - lg[bad]); am1 = int(lg.argmax())
                    cell["twin"] = {"margin_after": round(m1, 4), "delta": round(m1 - m0, 4),
                                    "flip": bool(m0 > 0 and m1 < 0),
                                    "argmax_changed": bool(am1 != am0),
                                    "argmax_after_tok": tok.convert_ids_to_tokens(am1)}
                    if ures is not None:
                        vu = ures[k][l].float()
                        vu = vu * (vx.norm() / (vu.norm() + 1e-6))
                        lg = forward_final(ids, Patch(lm.layers, l, p, vu))
                        m1 = float(lg[good] - lg[bad]); am1 = int(lg.argmax())
                        cell["unrelated"] = {"margin_after": round(m1, 4),
                                             "delta": round(m1 - m0, 4),
                                             "flip": bool(m0 > 0 and m1 < 0),
                                             "argmax_changed": bool(am1 != am0)}
                    entry["cells"][f"{k}/{l}"] = cell
            results.append(entry)
            if (i + 1) % 20 == 0:
                print(f"[step3] {split} {i+1}/{len(recs)}  {time.time()-t0:.0f}s", flush=True)
        # ---- per-split summary printed as soon as the split is done (dev first)
        print_summary(split, results, layers)

    summary = {s: summarise([e for e in results if e["split"] == s], layers)
               for s in ("dev", "heldout", "heldout2")}
    summary["combined"] = summarise([e for e in results if e["split"] != "dev"], layers)
    payload = {"framing": "method evaluation using a narrow task as instrument; not circuit discovery",
               "status": "agent-unverified", "freeze": FREEZE, "primary_cells": PRIMARY,
               "layers": layers, "skipped": dict(skipped),
               "summary": summary, "records_file": "step3-records.json.gz",
               "seconds": round(time.time() - t0, 1)}
    out = run.outputs / "step3-patching.json"
    out.write_text(json.dumps(payload, indent=1))
    import gzip
    with gzip.open(run.outputs / "step3-records.json.gz", "wt") as fh:
        json.dump({"records": results}, fh)
    print(f"skipped: {dict(skipped)}")
    print(f"wrote {out}", flush=True)
    return 0


def summarise(ents, layers):
    out = {}
    for k in QPOS:
        for l in layers:
            key = f"{k}/{l}"
            rows = [e for e in ents if key in e["cells"]]
            if not rows:
                continue
            right = [e for e in rows if e["margin_before"] > 0]
            wrong = [e for e in rows if e["margin_before"] < 0]
            def stat(which, sub):
                xs = [e["cells"][key][which] for e in sub if which in e["cells"][key]]
                if not xs:
                    return None
                return {"n": len(xs),
                        "flip_rate": round(sum(x["flip"] for x in xs) / len(xs), 4),
                        "mean_delta": round(sum(x["delta"] for x in xs) / len(xs), 4),
                        "argmax_changed_rate": round(sum(x["argmax_changed"] for x in xs) / len(xs), 4)}
            def stat_all(which):
                xs = [e["cells"][key][which] for e in rows if which in e["cells"][key]]
                return (round(sum(x["delta"] for x in xs) / len(xs), 4) if xs else None)
            rev = [e for e in wrong if e["cells"][key]["twin"]["margin_after"] > 0]
            out[key] = {"n": len(rows), "n_base_right": len(right), "n_base_wrong": len(wrong),
                        "twin": stat("twin", right), "unrelated": stat("unrelated", right),
                        "twin_mean_delta_all": stat_all("twin"),
                        "unrelated_mean_delta_all": stat_all("unrelated"),
                        "reverse_flip_rate_on_base_wrong": (round(len(rev) / len(wrong), 4)
                                                            if wrong else None),
                        "mean_cos_twin": round(sum(e["cells"][key]["cos_twin"] for e in rows) / len(rows), 4)}
    return out


def print_summary(split, results, layers):
    ents = [e for e in results if e["split"] == split]
    s = summarise(ents, layers)
    print(f"== {split}: n={len(ents)}")
    for k in QPOS:
        for l in PRIMARY[k]:
            g = s.get(f"{k}/{l}")
            if not g or not g["twin"]:
                continue
            u = g["unrelated"] or {}
            print(f"  {k:8s} L{l:<2d} baseRight={g['n_base_right']:3d}/{g['n']:3d} "
                  f"twin flip={g['twin']['flip_rate']:.3f} d={g['twin']['mean_delta']:+.2f} "
                  f"argmaxChg={g['twin']['argmax_changed_rate']:.2f} | unrelated flip="
                  f"{u.get('flip_rate', float('nan')):.3f} d={u.get('mean_delta', float('nan')):+.2f} "
                  f"| cos={g['mean_cos_twin']:.3f}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
