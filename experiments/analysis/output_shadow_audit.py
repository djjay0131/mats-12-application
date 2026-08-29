"""Output-shadow audit: is the readout reading a latent, or a token about to be said?

METHOD EVALUATION using a narrow task as instrument; not circuit discovery.

WHY THIS EXISTS
---------------
The Stage 2 readout looks strong at the final position: at its pre-registered
layer J-Lens prefers the correct intermediate over its role-swapped twin on 39
of 40 dev records. That number is only interesting if the intermediate is
HIDDEN at that position. This script tests whether it is.

It asks three things of the same 40 records, joined on record_id:

  1. SURFACE. Does the model's own generation name the intermediate in plain
     text? If it does, the intermediate is not a latent at the readout position
     -- it is a token the model is about to emit, and reading it out of the
     residual is not evidence of recovered binding.
  2. SHADOW. Does the model's own final-layer logit distribution already prefer
     the correct intermediate? How strongly, and on how many records does it
     prefer the WRONG one? Those records are the only ones where the shadow and
     the truth come apart, and they are therefore the only ones on which the
     project's question is answerable by a passive readout at this position.
  3. COUPLING. How tightly does the lens readout track that output preference,
     against an anchor: the last-layer logit lens, which is about as close to
     "just reading the output" as a lens gets. A lens scoring near the anchor is
     reporting the output, whatever else it may also be doing.

It also breaks the shadow strength down by cell and by pair, because if the
small discriminating set were an artifact of particular items or of the AB/BA
role-swap structure it would show up there. (It does not.)

NO GPU, NO MODEL LOAD. Reads two committed run records and the dev split.
Intended to run on the agents4research VM, not on an ARC login node.

The join is on record_id, which is exact: the eligibility screen was run with
--dataset against the same committed file the readout read, in the same
allocation. This is the join Stage 1 could not do.

Every number `agent-unverified`.
"""
from __future__ import annotations

import argparse
import json
import sys
from math import sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from runlog import start_run  # noqa: E402


def pearson(xs, ys):
    """Pearson r, or None when it is undefined rather than a misleading 0.0."""
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / sqrt(sxx * syy)


def wilson(k, n, z=1.96):
    """Wilson score interval. A bare 3/40 invites over-reading; this is the range."""
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d, 4), round((c + h) / d, 4)]


ap = argparse.ArgumentParser()
ap.add_argument("--elig", required=True, help="eligibility-screen run directory")
ap.add_argument("--readout", required=True, help="stage1-passive-readout run directory")
ap.add_argument("--dataset", default="results/datasets/dev.jsonl")
ap.add_argument("--label", required=True, help="short name for this cluster/job, e.g. tinkercliffs-7298944")
args = ap.parse_args()

elig_p = Path(args.elig) / "outputs" / "eligibility-screen.json"
read_p = Path(args.readout) / "outputs" / "stage1-passive-readout.json"
dev_p = Path(args.dataset)
for p in (elig_p, read_p, dev_p):
    if not p.exists():
        sys.exit(f"missing input: {p}")

dev = {}
meta = None
for line in dev_p.read_text().splitlines():
    if not line.strip():
        continue
    r = json.loads(line)
    if r.get("_meta"):
        meta = r
        continue
    dev[r["record_id"]] = r
if meta is None or meta.get("split") != "dev":
    sys.exit("dataset is not the dev split; refusing (this script tunes nothing, but the rule is the rule)")

elig = json.loads(elig_p.read_text())
readout = json.loads(read_p.read_text())

# The two records must describe the same stimuli, or the join is meaningless.
if readout.get("dataset") and Path(str(readout["dataset"])).name != dev_p.name:
    sys.exit(f"readout ran against {readout['dataset']}, not {dev_p}")

behaviour = {}
for cell in elig["cells"]:
    for v in cell.get("per_variant", []):
        behaviour[v["record_id"]] = v

sel_final = readout["summary"]["jlens"]["final"]["selected_layer"]
sel_pre = readout["summary"]["jlens"]["prequery"]["selected_layer"]
ll_final = readout["summary"]["logitlens"]["final"]["selected_layer"]

rows = []
for rec in readout["records"]:
    if rec["arm"] != "jlens":
        continue
    rid = rec["record_id"]
    d, b = dev.get(rid), behaviour.get(rid)
    if d is None or b is None:
        sys.exit(f"record {rid} present in the readout but not in both the dataset and the screen")
    mb = rec.get("model_behaviour")
    if mb is None:
        sys.exit(f"record {rid} has no model_behaviour; this run predates the capture and cannot be audited")
    gen = b.get("generated") or ""
    rows.append({
        "record_id": rid,
        "pair_id": rec["pair_id"],
        "cell": rec["cell"],
        "template_id": rec.get("template_id"),
        "intermediate": d["intermediate"],
        "alt_intermediate": d["alt_intermediate"],
        "answer": d["answer"],
        # surface
        "gen_names_intermediate": d["intermediate"] in gen,
        "gen_names_alt_intermediate": d["alt_intermediate"] in gen,
        "gen_names_answer": d["answer"] in gen,
        "text_match": bool(b["text_match"]),
        # shadow
        "model_intermediate_margin": mb["intermediate_margin"],
        "model_answer_margin": mb["answer_margin"],
        # readout
        "jlens_final_margin": rec["scores"]["final"][str(sel_final)]["intermediate"]["margin"],
        "jlens_final_correct": (rec["scores"]["final"][str(sel_final)]["intermediate"]["rank_correct"]
                                < rec["scores"]["final"][str(sel_final)]["intermediate"]["rank_incorrect"]),
        "jlens_prequery_margin": rec["scores"]["prequery"][str(sel_pre)]["intermediate"]["margin"],
        "jlens_prequery_correct": (rec["scores"]["prequery"][str(sel_pre)]["intermediate"]["rank_correct"]
                                   < rec["scores"]["prequery"][str(sel_pre)]["intermediate"]["rank_incorrect"]),
    })

ll_margin = {r["record_id"]: r["scores"]["final"][str(ll_final)]["intermediate"]["margin"]
             for r in readout["records"] if r["arm"] == "logitlens"}

n = len(rows)
if n == 0:
    sys.exit("no jlens records found")

run = start_run("output-shadow-audit",
                seed=meta.get("seed"),
                model_repo=readout.get("model"),
                model_revision=readout.get("model_revision"))

names_int = sum(r["gen_names_intermediate"] for r in rows)
neg = [r for r in rows if r["model_intermediate_margin"] < 0]
margins = sorted(r["model_intermediate_margin"] for r in rows)

by = {}
for key in ("cell", "pair_id"):
    g = {}
    for r in rows:
        k = r[key]
        e = g.setdefault(k, {"n": 0, "sum": 0.0, "n_negative": 0})
        e["n"] += 1
        e["sum"] += r["model_intermediate_margin"]
        e["n_negative"] += int(r["model_intermediate_margin"] < 0)
    for k, e in g.items():
        e["mean_model_intermediate_margin"] = round(e.pop("sum") / e["n"], 4)
    by[key] = dict(sorted(g.items()))

jf = [r["jlens_final_margin"] for r in rows]
jp = [r["jlens_prequery_margin"] for r in rows]
mi = [r["model_intermediate_margin"] for r in rows]
ma = [r["model_answer_margin"] for r in rows]
lf = [ll_margin[r["record_id"]] for r in rows]

ct = {"model_correct": {"readout_correct": 0, "readout_wrong": 0},
      "model_wrong": {"readout_correct": 0, "readout_wrong": 0}}
for r in rows:
    ct["model_correct" if r["text_match"] else "model_wrong"][
        "readout_correct" if r["jlens_final_correct"] else "readout_wrong"] += 1

payload = {
    "framing": "method evaluation using a narrow task as instrument; not circuit discovery",
    "claim_type": "method-claim: what a passive readout at this position can and cannot be credited with",
    "status": "agent-unverified",
    "label": args.label,
    "inputs": {"eligibility_run": args.elig, "readout_run": args.readout, "dataset": str(dev_p)},
    "dataset_meta": meta,
    "selected_layers": {"jlens_final": sel_final, "jlens_prequery": sel_pre, "logitlens_final": ll_final},
    "n_records": n,

    "surface": {
        "note": ("Whether the model's own generated text names the intermediate. If it does, "
                 "the intermediate is not latent at the final readout position -- it is a token "
                 "the model is about to emit."),
        "generation_names_intermediate": names_int,
        "rate": round(names_int / n, 4),
        "wilson95": wilson(names_int, n),
        "generation_names_alt_intermediate": sum(r["gen_names_alt_intermediate"] for r in rows),
        "generation_names_answer": sum(r["gen_names_answer"] for r in rows),
    },

    "shadow": {
        "note": ("The model's own final-layer logits. n_negative is the DISCRIMINATING SET: the "
                 "only records where the output preference and the correct intermediate disagree, "
                 "and therefore the only ones on which a passive readout at this position can be "
                 "distinguished from an output shadow."),
        "mean_model_intermediate_margin": round(sum(mi) / n, 4),
        "margin_quantiles": {"min": margins[0], "p25": margins[n // 4], "median": margins[n // 2],
                             "p75": margins[(3 * n) // 4], "max": margins[-1]},
        "n_below_0": len(neg),
        "n_below_0.5": sum(m < 0.5 for m in margins),
        "n_below_1.0": sum(m < 1.0 for m in margins),
        "n_below_2.0": sum(m < 2.0 for m in margins),
        "discriminating_rate": round(len(neg) / n, 4),
        "discriminating_wilson95": wilson(len(neg), n),
        "discriminating_records": [
            {"record_id": r["record_id"], "text_match": r["text_match"],
             "model_intermediate_margin": r["model_intermediate_margin"],
             "jlens_final_margin": r["jlens_final_margin"],
             "jlens_final_correct": r["jlens_final_correct"],
             "jlens_prequery_correct": r["jlens_prequery_correct"]} for r in neg],
    },

    "coupling": {
        "note": ("logitlens_final_vs_model_intermediate is the ANCHOR: the last-layer logit lens is "
                 "about as close to reading the output as a lens gets, so it is roughly what a pure "
                 "shadow scores on this data. It is not 1.0 because the lens reads the residual "
                 "through its own path."),
        "jlens_final_vs_model_intermediate": round(pearson(jf, mi), 4),
        "jlens_final_vs_model_answer": round(pearson(jf, ma), 4),
        "logitlens_final_vs_model_intermediate": round(pearson(lf, mi), 4),
        "jlens_prequery_vs_model_intermediate": round(pearson(jp, mi), 4),
    },

    "breakdown": by,
    "contingency_final": ct,
    "contingency_note": ("Rows are the model's text_match, columns the readout at the selected final "
                         "layer. Cells in the model_wrong row are the only discriminating ones. See "
                         "shadow.n_below_0 for why this table is not a usable instrument on this split."),
    "records": rows,
}

out = run.outputs / "output-shadow-audit.json"
out.write_text(json.dumps(payload, indent=2))

print()
print("=" * 62)
print(f"  label                       {args.label}   n={n}")
verdict = "the intermediate is NOT latent here" if names_int > 0.8 * n else "mostly latent"
print(f"  generation NAMES the intermediate   {names_int}/{n}   -> {verdict}")
print(f"  model's own intermediate margin     mean {sum(mi)/n:+.3f}"
      f"   median {margins[n//2]:+.3f}   min {margins[0]:+.3f}")
print(f"  DISCRIMINATING SET (margin < 0)     {len(neg)}/{n}"
      f"   95% CI {wilson(len(neg), n)}")
print(f"  coupling: jlens final vs model      r={pearson(jf, mi):+.3f}"
      f"   (shadow anchor: logit lens L{ll_final} r={pearson(lf, mi):+.3f})")
print(f"  coupling: jlens final vs ANSWER     r={pearson(jf, ma):+.3f}")
print(f"  coupling: jlens prequery vs model   r={pearson(jp, mi):+.3f}")
print("=" * 62)
print(f"wrote {out}")
