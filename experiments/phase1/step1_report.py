#!/usr/bin/env python3
"""Phase 1, step 1 -- fresh held-out draw scored once at frozen settings.

Reads TWO stage3-heldout-frozen runs -- the application's original held-out
run (160 records) and the heldout2 run (240 records) -- and reports, for
each of `original`, `new`, `combined`, the same quantities the application
reported: direction fraction vs its label-permutation control, median rank of
the correct intermediate, the output-shadow fraction, lens accuracy on the
records where the model's own next-token preference is wrong (with n), and
r(lens margin, model margin). Arm 3 (difference-in-means, fit on dev) is
reported per run and pooled by count.

Nothing here selects anything: positions, layers and arms are whatever the
two runs already scored. The pre-registered decision rule is evaluated at the
end and printed with the branch that fired. Interpretation is Jason's.

METHOD EVALUATION, not circuit discovery. Output is agent-unverified.
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
ARMS = ["jlens", "logitlens", "jlens_random_transport"]
BAND = (0.25, 0.45)          # pre-registered flag band, combined jlens/relcomp
REPLICATE_GAP = 0.10         # pre-registered: jlens frac - control frac at relcomp


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


def load_run(run_dir: str, tag: str):
    src = Path(run_dir) / "outputs" / "stage3-heldout-frozen.json"
    d = json.loads(src.read_text())
    recs = [dict(x, source=tag) for x in d["records"] if x["split"] == "heldout"]
    shadow = {(tag, x["record_id"], x["position"]): x
              for x in d["shadow"] if x["split"] == "heldout"}
    return d, recs, shadow


def prompts_of(path: str) -> dict[str, str]:
    out = {}
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if not r.get("_meta"):
            out[r["record_id"]] = r["prompt"]
    return out


def right(x, k):
    s = x["scores"][k]["intermediate"]
    return s["rank_correct"] < s["rank_incorrect"]


def ctrl_right(x, k):
    s = x["scores"][k]["control_label_permutation"]
    return s["rank_correct"] < s["rank_incorrect"]


def tally(recs, shadow, arm, k):
    rows = [x for x in recs if x["arm"] == arm and x["scores"].get(k)]
    if not rows:
        return None
    ranks = sorted(x["scores"][k]["intermediate"]["rank_correct"] for x in rows)
    out = {"n": len(rows),
           "frac": round(sum(right(x, k) for x in rows) / len(rows), 4),
           "control_frac": round(sum(ctrl_right(x, k) for x in rows) / len(rows), 4),
           "median_rank": ranks[len(ranks) // 2]}
    sh = [x for x in rows if (x["source"], x["record_id"], k) in shadow]
    if sh:
        sm = [shadow[(x["source"], x["record_id"], k)]["intermediate_margin"] for x in sh]
        lm = [x["scores"][k]["intermediate"]["margin"] for x in sh]
        wrong = [x for x, m in zip(sh, sm) if m < 0]
        ok = [x for x, m in zip(sh, sm) if m > 0]
        r = pearson(lm, sm)
        out.update({
            "shadow_frac": round(sum(m > 0 for m in sm) / len(sm), 4),
            "n_shadow": len(sh),
            "n_model_wrong": len(wrong),
            "acc_model_wrong": (round(sum(right(x, k) for x in wrong) / len(wrong), 4)
                                if wrong else None),
            "n_model_right": len(ok),
            "acc_model_right": (round(sum(right(x, k) for x in ok) / len(ok), 4)
                                if ok else None),
            "r_lens_vs_model": (round(r, 4) if r is not None else None),
        })
    return out


def arm3_pool(d_list):
    out = {}
    for k in POS:
        n_sc = n_ok = 0
        n_tot = 0
        for d in d_list:
            g = (d.get("arm3") or {}).get(k)
            if not g:
                continue
            h = g["heldout"]
            if h["n_scored"] and h["accuracy"] is not None:
                n_sc += h["n_scored"]
                n_ok += round(h["accuracy"] * h["n_scored"])
                n_tot += h["n"]
        if n_sc:
            out[k] = {"n": n_tot, "n_scored": n_sc,
                      "accuracy": round(n_ok / n_sc, 4),
                      "layer": d_list[0]["arm3"][k]["layer"]}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--original", required=True, help="application stage3 run dir")
    ap.add_argument("--new", required=True, help="heldout2 stage3 run dir")
    ap.add_argument("--dev", default="results/datasets/dev.jsonl")
    ap.add_argument("--heldout", default="results/datasets/heldout.jsonl")
    ap.add_argument("--heldout2", default="results/datasets/heldout2.jsonl")
    args = ap.parse_args()

    d1, r1, s1 = load_run(args.original, "original")
    d2, r2, s2 = load_run(args.new, "new")

    # ---- duplicate-prompt screen (pre-registered handling) ----------------
    dev_p = set(prompts_of(args.dev).values())
    ho_p = set(prompts_of(args.heldout).values())
    h2 = prompts_of(args.heldout2)
    dup_dev = sorted(rid for rid, p in h2.items() if p in dev_p)
    dup_ho = sorted(rid for rid, p in h2.items() if p in ho_p)
    # records whose prompt appears in DEV are excluded from every heldout2
    # tally (arm 3's mu was fit on dev; the label-permutation seed is shared).
    r2 = [x for x in r2 if x["record_id"] not in set(dup_dev)]
    # records whose prompt appears in the ORIGINAL held-out set stay in
    # `new` but are dropped from `combined` so no prompt is counted twice.
    r2_comb = [x for x in r2 if x["record_id"] not in set(dup_ho)]

    run = start_run("phase1-step1-report",
                    original_run=args.original, new_run=args.new,
                    heldout2=args.heldout2,
                    note="original / new / combined at frozen settings; no selection")

    sets = {"original": (r1, s1), "new": (r2, s2),
            "combined": (r1 + r2_comb, {**s1, **s2})}
    table = {name: {arm: {k: tally(recs, sh, arm, k) for k in POS} for arm in ARMS}
             for name, (recs, sh) in sets.items()}
    arm3 = {"original": arm3_pool([d1]), "new": arm3_pool([d2]),
            "combined": arm3_pool([d1, d2])}

    print(f"original run: {args.original}")
    print(f"new run:      {args.new}")
    print(f"heldout2 records: {len(h2)}  dup-with-dev (excluded): {len(dup_dev)}  "
          f"dup-with-heldout (kept in new, dropped from combined): {len(dup_ho)}")
    print(f"n scored: original={len({x['record_id'] for x in r1})} "
          f"new={len({x['record_id'] for x in r2})} "
          f"combined={len({(x['source'], x['record_id']) for x in r1 + r2_comb})}")
    print()
    for name in sets:
        print(f"== {name}")
        for arm in ARMS:
            for k in POS:
                g = table[name][arm][k]
                if not g:
                    continue
                line = (f"  {arm:22s} {k:8s} frac={g['frac']:.3f} "
                        f"ctrl={g['control_frac']:.3f} medrank={g['median_rank']:>7d} "
                        f"n={g['n']}")
                if "shadow_frac" in g:
                    aw = g["acc_model_wrong"]
                    line += (f"  shadow={g['shadow_frac']:.3f} "
                             f"modelWRONG n={g['n_model_wrong']:3d} "
                             f"acc={'--' if aw is None else f'{aw:.3f}'} "
                             f"r={g['r_lens_vs_model']:+.3f}")
                print(line)
        for k, g in arm3[name].items():
            print(f"  {'arm3 (diff-in-means)':22s} {k:8s} acc={g['accuracy']:.3f} "
                  f"scored={g['n_scored']}/{g['n']} L{g['layer']}")
        print()

    # ---- pre-registered decision rules --------------------------------------
    verdict = {}
    g_new = table["new"]["jlens"]["relcomp"]
    gap = g_new["frac"] - g_new["control_frac"] if g_new else None
    verdict["replicates_at_relcomp"] = (gap is not None and gap >= REPLICATE_GAP)
    verdict["relcomp_gap_new"] = None if gap is None else round(gap, 4)
    g_q = table["new"]["jlens"]["qmark"]
    verdict["qmark_gap_new"] = (None if not g_q
                                else round(g_q["frac"] - g_q["control_frac"], 4))
    g_c = table["combined"]["jlens"]["relcomp"]
    aw = g_c.get("acc_model_wrong") if g_c else None
    verdict["combined_relcomp_acc_model_wrong"] = aw
    verdict["combined_relcomp_n_model_wrong"] = g_c.get("n_model_wrong") if g_c else None
    verdict["flag_outside_band"] = (aw is None or not (BAND[0] <= aw <= BAND[1]))
    print("== pre-registered rules")
    print(f"  R1 replicate: jlens frac - ctrl at relcomp (new) = "
          f"{verdict['relcomp_gap_new']}  (>= {REPLICATE_GAP} required)  -> "
          f"{'REPLICATES' if verdict['replicates_at_relcomp'] else 'DOES NOT REPLICATE'}")
    print(f"  R2 band: combined jlens acc on model-wrong records at relcomp = {aw} "
          f"(n={verdict['combined_relcomp_n_model_wrong']}); band {BAND} -> "
          f"{'FLAG: outside band' if verdict['flag_outside_band'] else 'inside band'}")

    out = {"framing": "method evaluation using a narrow task as instrument; not circuit discovery",
           "status": "agent-unverified",
           "original_run": args.original, "new_run": args.new,
           "duplicates": {"heldout2_vs_dev_excluded": dup_dev,
                          "heldout2_vs_heldout_dropped_from_combined": dup_ho},
           "table": table, "arm3": arm3, "verdict": verdict,
           "rules": {"replicate_gap": REPLICATE_GAP, "band": BAND}}
    (run.outputs / "step1-report.json").write_text(json.dumps(out, indent=1))
    print(f"\nwrote {run.outputs / 'step1-report.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
