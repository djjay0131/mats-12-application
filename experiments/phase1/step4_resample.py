#!/usr/bin/env python3
"""Phase 1, step 4 -- the resample control.

Pre-registered in llm/memory_bank/research-learning-log.md ("Phase 1, step 4")
before this job is queued.

For every record, the correct intermediate's object fact is rewritten with a
fresh single-token object from the same pool that appears nowhere in the
prompt ("Prague uses wool." -> "Prague uses basalt."-style, but drawn from
task_templates.REAL_OBJECTS so it is single-token by construction). Nothing
else changes. J-Lens and the logit lens are then re-read at the FROZEN
positions and layers (freeze.json) and the ANSWER target is read as
(new object, old object): "the readout follows the stated fact" means the
new object outranks the old one. Also reported: (new object, alternative
object) on the modified prompt (both present, so co-occurrence cannot decide
it), the CITY target on the modified prompt (the application's rank result,
which should not move), the same targets on the UNMODIFIED prompt (control:
how often a fresh pool word outranks the stated answer anyway), and the
model's own next-token preference for new vs old. Every number
agent-unverified.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
import zlib
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (QPOS, FREEZE, TEMPLATES, load_all, load_model_and_lens,  # noqa: E402
                    anchored_positions, two_way, MODEL_ID, MODEL_REV,
                    LENS_REPO, LENS_REV)
import task_templates as tt                                    # noqa: E402
from runlog import start_run                                   # noqa: E402

ARMS = [("jlens", True), ("logitlens", False)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260917)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--max-records", type=int, default=0, help="smoke test only")
    args = ap.parse_args()

    splits = load_all()
    if args.max_records:
        splits = [(s, r[:args.max_records]) for s, r in splits]
    run = start_run("phase1-step4-resample", seed=args.seed,
                    model_repo=MODEL_ID, model_revision=MODEL_REV,
                    lens_repo=LENS_REPO, lens_revision=LENS_REV,
                    freeze="experiments/stage3/freeze.json",
                    note="resample control: correct object fact rewritten; frozen positions/layers")
    t0 = time.time()
    tok, hf, lm, lens = load_model_and_lens(args.device)
    pool = tt.filter_single_token(tok, tt.REAL_OBJECTS)
    JL = {k: int(v) for k, v in FREEZE["layers"]["jlens"].items()}
    LL = {k: int(v) for k, v in FREEZE["layers"]["logitlens"].items()}
    ARM_L = {"jlens": JL, "logitlens": LL}
    print(f"[step4] pool={len(pool)} single-token objects  load={time.time()-t0:.1f}s", flush=True)

    results, fails = [], 0
    for split, recs in splits:
        for i, r in enumerate(recs):
            rng = random.Random(args.seed * 1000003 + zlib.crc32(r["record_id"].encode()))
            cands = [w for w in pool if w not in (r["answer"], r["alt_answer"])
                     and f" {w}" not in r["prompt"]]
            new = rng.choice(cands)
            new_id = tt.single_token_id(tok, new)
            t = TEMPLATES[r["template_id"]]
            old_fact = t.place_rel.format(place=r["intermediate"], obj=r["answer"])
            new_fact = t.place_rel.format(place=r["intermediate"], obj=new)
            if r["prompt"].count(old_fact) != 1:
                fails += 1
                continue
            mod = r["prompt"].replace(old_fact, new_fact)
            entry = {"split": split, "record_id": r["record_id"], "pair_id": r["pair_id"],
                     "template_id": r["template_id"], "new_object": new, "new_id": new_id,
                     "old_object": r["answer"], "prompts": {}}
            for cond, prompt in (("modified", mod), ("unmodified", r["prompt"])):
                ids = lm.encode(prompt)
                pos, toks, align = anchored_positions(tok, prompt, ids)
                want = [pos[k] for k in QPOS]
                if any(p is None for p in want):
                    fails += 1
                    continue
                per_arm = {}
                model_logits = None
                for arm, use_j in ARMS:
                    with torch.no_grad():
                        ll, ml, _ = lens.apply(lm, prompt, positions=want, use_jacobian=use_j)
                    model_logits = ml
                    ll = {int(l): v for l, v in ll.items()}
                    sc = {}
                    for ki, k in enumerate(QPOS):
                        row = ll[ARM_L[arm][k]][ki]
                        sc[k] = {"layer": ARM_L[arm][k],
                                 "NEW_vs_OLD": two_way(row, new_id, r["answer_id"]),
                                 "NEW_vs_ALT": two_way(row, new_id, r["alt_answer_id"]),
                                 "OLD_vs_ALT": two_way(row, r["answer_id"], r["alt_answer_id"]),
                                 "CITY": two_way(row, r["intermediate_id"], r["alt_intermediate_id"])}
                    per_arm[arm] = sc
                sh = {}
                for ki, k in enumerate(QPOS):
                    row = model_logits[ki].float()
                    sh[k] = {"NEW_vs_OLD": two_way(row, new_id, r["answer_id"]),
                             "NEW_vs_ALT": two_way(row, new_id, r["alt_answer_id"]),
                             "OLD_vs_ALT": two_way(row, r["answer_id"], r["alt_answer_id"])}
                entry["prompts"][cond] = {"n_tokens": int(ids.shape[1]), "position_tokens": toks,
                                          "arms": per_arm, "model": sh}
            results.append(entry)
            if (i + 1) % 40 == 0:
                print(f"[step4] {split} {i+1}/{len(recs)}  {time.time()-t0:.0f}s", flush=True)

    def summarise(ents):
        out = {}
        for cond in ("modified", "unmodified"):
            for arm, _ in ARMS + [("model", None)]:
                for k in QPOS:
                    for tg in ("NEW_vs_OLD", "NEW_vs_ALT", "OLD_vs_ALT", "CITY"):
                        rows = []
                        for e in ents:
                            pr = e["prompts"].get(cond)
                            if not pr:
                                continue
                            src = pr["model"] if arm == "model" else pr["arms"][arm]
                            if k in src and tg in src[k]:
                                rows.append(src[k][tg])
                        if not rows:
                            continue
                        n = len(rows)
                        ranks = sorted(x["rank_correct"] for x in rows)
                        out[f"{cond}/{arm}/{k}/{tg}"] = {
                            "n": n,
                            "frac": round(sum(x["rank_correct"] < x["rank_incorrect"] for x in rows) / n, 4),
                            "median_rank_first": ranks[n // 2],
                            "mean_margin": round(sum(x["margin"] for x in rows) / n, 4)}
        return out

    summary = {s: summarise([e for e in results if e["split"] == s])
               for s in ("dev", "heldout", "heldout2")}
    summary["combined"] = summarise([e for e in results if e["split"] != "dev"])
    payload = {"framing": "method evaluation using a narrow task as instrument; not circuit discovery",
               "status": "agent-unverified", "freeze": FREEZE, "pool": pool,
               "n_failed": fails, "summary": summary, "records": results,
               "seconds": round(time.time() - t0, 1)}
    out = run.outputs / "step4-resample.json"
    out.write_text(json.dumps(payload, indent=1))
    print("=" * 70)
    for arm, _ in ARMS + [("model", None)]:
        for k in QPOS:
            m = summary["combined"].get(f"modified/{arm}/{k}/NEW_vs_OLD")
            u = summary["combined"].get(f"unmodified/{arm}/{k}/NEW_vs_OLD")
            a = summary["combined"].get(f"modified/{arm}/{k}/NEW_vs_ALT")
            c = summary["combined"].get(f"modified/{arm}/{k}/CITY")
            if m:
                print(f"  combined {arm:9s} {k:8s} NEWvsOLD mod={m['frac']:.3f} (medrank new {m['median_rank_first']}) "
                      f"unmod={u['frac']:.3f} | NEWvsALT mod={a['frac']:.3f} | "
                      f"CITY mod={c['frac']:.3f} n={m['n']}" if c else
                      f"  combined {arm:9s} {k:8s} NEWvsOLD mod={m['frac']:.3f} unmod={u['frac']:.3f} n={m['n']}")
    print(f"failed records: {fails}")
    print(f"wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
