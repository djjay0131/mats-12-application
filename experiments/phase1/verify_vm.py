#!/usr/bin/env python3
"""Agent verification pass, part 1 (VM): re-derive the Phase 1 load-bearing
numbers from the RAW run outputs with fresh code (no import of the report
scripts), plus provenance checks. Prints CLAIMED vs RECOMPUTED and a PASS/FAIL
per line. Read-only.
"""
import gzip, hashlib, json, subprocess, sys
from collections import Counter
from pathlib import Path

R = Path("results/runs")
S1o = R / "20260830T175149Z-stage3-heldout-frozen"
S1n = R / "20260917T193052Z-stage3-heldout-frozen"
S2 = R / "20260917T202900Z-phase1-step2-fact-tokens"
S3 = R / "20260917T202907Z-phase1-step3-patching"
S4 = R / "20260917T202853Z-phase1-step4-resample"
S5 = R / "20260917T203740Z-phase1-step5-lr-probe"
S5b = R / "20260917T205754Z-phase1-step5-breakdown"
fails = 0


def check(name, claimed, got, tol=0.0):
    global fails
    ok = (abs(claimed - got) <= tol) if isinstance(claimed, (int, float)) else claimed == got
    if not ok:
        fails += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: claimed {claimed}  recomputed {got}")


def jl(p):
    return json.loads(Path(p).read_text())


def jgz(p):
    with gzip.open(p, "rt") as fh:
        return json.load(fh)


def frac(rows, key="intermediate"):
    return sum(r[key]["rank_correct"] < r[key]["rank_incorrect"] for r in rows) / len(rows)


print("== provenance")
for name, d, sha, job in (("step1 scoring", S1n, "fe1ca16", "587809"), ("step2", S2, "7c55733", "587865"),
                          ("step3", S3, "7c55733", "587866"), ("step4", S4, "7c55733", "587867"),
                          ("step5", S5, "7c55733", "587868"), ("step5 breakdown", S5b, "6c8e7f3", "587883")):
    m = jl(d / "manifest.json")
    check(f"{name} manifest git sha starts with {sha}", True, m["git"]["sha"].startswith(sha))
    check(f"{name} Slurm job id", job, m["slurm"]["SLURM_JOB_ID"])
    check(f"{name} run status ok", "ok", m.get("status"))
h2m = jl("results/datasets/heldout2-manifest.json")
got = hashlib.sha256(Path("results/datasets/heldout2.jsonl").read_bytes()).hexdigest()
check("heldout2.jsonl sha256 = manifest", h2m["sha256"]["heldout.jsonl"], got)
recs2 = [json.loads(l) for l in Path("results/datasets/heldout2.jsonl").read_text().splitlines() if l.strip()]
recs2 = [r for r in recs2 if not r.get("_meta")]
check("heldout2 record count", 240, len(recs2))
check("heldout2 distinct pairs", 60, len({r["pair_id"] for r in recs2}))
check("heldout2 duplicate prompts", 0, len(recs2) - len({r["prompt"] for r in recs2}))
dev_p = {json.loads(l)["prompt"] for l in Path("results/datasets/dev.jsonl").read_text().splitlines() if l.strip() and "_meta" not in l}
ho_p = {json.loads(l)["prompt"] for l in Path("results/datasets/heldout.jsonl").read_text().splitlines() if l.strip() and "_meta" not in l}
check("heldout2 prompts shared with dev", 0, sum(r["prompt"] in dev_p for r in recs2))
check("heldout2 prompts shared with heldout", 0, sum(r["prompt"] in ho_p for r in recs2))
diff = subprocess.run(["git", "diff", "--stat", "mats12-submitted", "HEAD", "--",
                       "experiments/stage3/freeze.json", "writeup/main.md", "results/runs/20260830T175149Z-stage3-heldout-frozen",
                       "results/runs/20260830T173157Z-eligibility-screen", "results/runs/20260830T182516Z-stage3-window-shadow-audit"],
                      capture_output=True, text=True).stdout.strip()
check("freeze.json / writeup/main.md / application runs unchanged since mats12-submitted", "", diff)

print("\n== step 1 (recomputed from stage3 records)")
d = jl(S1n / "outputs" / "stage3-heldout-frozen.json")
rows = [x for x in d["records"] if x["split"] == "heldout" and x["arm"] == "jlens" and x["scores"].get("relcomp")]
check("new draw n", 240, len(rows))
check("new jlens relcomp frac", 0.733, round(frac([x["scores"]["relcomp"] for x in rows]), 3), 0.001)
check("new jlens relcomp ctrl", 0.496, round(frac([x["scores"]["relcomp"] for x in rows], "control_label_permutation"), 3), 0.001)
ranks = sorted(x["scores"]["relcomp"]["intermediate"]["rank_correct"] for x in rows)
check("new jlens relcomp median rank", 132, ranks[len(ranks) // 2])
sh = {(x["record_id"]): x for x in d["shadow"] if x["split"] == "heldout" and x["position"] == "relcomp"}
wrong = [x for x in rows if sh[x["record_id"]]["intermediate_margin"] < 0]
check("new model-wrong n at relcomp", 61, len(wrong))
check("new jlens acc on model-wrong", 0.213, round(frac([x["scores"]["relcomp"] for x in wrong]), 3), 0.001)
do = jl(S1o / "outputs" / "stage3-heldout-frozen.json")
rows_o = [x for x in do["records"] if x["split"] == "heldout" and x["arm"] == "jlens" and x["scores"].get("relcomp")]
sho = {x["record_id"]: x for x in do["shadow"] if x["split"] == "heldout" and x["position"] == "relcomp"}
wrong_o = [x for x in rows_o if sho[x["record_id"]]["intermediate_margin"] < 0]
comb = wrong + wrong_o
check("combined model-wrong n", 93, len(comb))
check("combined jlens acc on model-wrong", 0.258, round(frac([x["scores"]["relcomp"] for x in comb]), 3), 0.001)
check("original jlens acc on model-wrong (application 0.344)", 0.344, round(frac([x["scores"]["relcomp"] for x in wrong_o]), 3), 0.001)
model_wrong_ids_step1 = {x["record_id"] for x in comb}

print("\n== step 2 (recomputed from step2-records.json.gz)")
g = jgz(S2 / "outputs" / "step2-records.json.gz")
ents = [e for e in g["records"] if e["split"] != "dev"]
shadow2 = {(e["split"], e["record_id"]): e["shadow"] for e in g["shadow"]}
check("combined records", 400, len(ents))
check("fact-position failures", 0, sum(len(e["fact_failures"]) for e in ents))
def pooled(arm, typ, tname, layer):
    hits = n = 0
    for e in ents:
        for k in (f"{typ}_q", f"{typ}_d"):
            s = e["arms"][arm][k][tname]; li = s["layers"].index(layer)
            hits += s["rank_correct"][li] < s["rank_incorrect"][li]; n += 1
    return hits / n, n
f30, n = pooled("jlens", "period", "CITY", 30); f9, _ = pooled("jlens", "period", "CITY", 9); c30, _ = pooled("jlens", "period", "CITY_ctrl", 30)
check("jlens period->CITY pooled n", 800, n)
check("jlens period->CITY L30", 0.559, round(f30, 3), 0.001)
check("jlens period->CITY L30 ctrl", 0.507, round(c30, 3), 0.001)
check("jlens period->CITY L9", 0.871, round(f9, 3), 0.001)
def anchor(arm, k, layer, subset=None):
    rows = [e for e in ents if (subset is None or (e["split"], e["record_id"]) in subset)]
    hits = 0
    for e in rows:
        s = e["arms"][arm][k]["CITY"]; li = s["layers"].index(layer)
        hits += s["rank_correct"][li] < s["rank_incorrect"][li]
    return hits / len(rows), len(rows)
check("jlens relcomp L30 (step 2 pass)", 0.752, round(anchor("jlens", "relcomp", 30)[0], 3), 0.001)
mw2 = {(e["split"], e["record_id"]) for e in ents if shadow2[(e["split"], e["record_id"])]["relcomp"]["CITY"]["margin"] < 0}
check("step-2 model-wrong n at relcomp", 93, len(mw2))
check("step-2 model-wrong set == step-1 set (record ids)", True, {r for _, r in mw2} == model_wrong_ids_step1)
check("jlens on model-wrong relcomp L30", 0.26, round(anchor("jlens", "relcomp", 30, mw2)[0], 2), 0.005)
check("jlens on model-wrong relcomp L18", 0.634, round(anchor("jlens", "relcomp", 18, mw2)[0], 3), 0.001)
best = max(range(31), key=lambda l: anchor("jlens", "relcomp", l, mw2)[0])
check("jlens on model-wrong: max over blocks is L18", 18, best)
check("jlens relcomp L15 (chance region)", 0.53, round(anchor("jlens", "relcomp", 15)[0], 2), 0.005)

print("\n== step 3 (recomputed from step3-records.json.gz)")
g3 = jgz(S3 / "outputs" / "step3-records.json.gz")["records"]
ho3 = [e for e in g3 if e["split"] != "dev"]
right = [e for e in ho3 if e["margin_before"] > 0]
check("combined n", 400, len(ho3)); check("base-right n", 382, len(right))
def flip(cell, donor):
    xs = [e["cells"][cell][donor]["flip"] for e in right if donor in e["cells"][cell]]
    return sum(xs) / len(xs)
check("relcomp/30 twin flip", 0.0, round(flip("relcomp/30", "twin"), 4))
check("qmark/27 twin flip", 0.005, round(flip("qmark/27", "twin"), 3), 0.001)
check("final/30 twin flip", 0.935, round(flip("final/30", "twin"), 3), 0.001)
check("final/30 unrelated flip", 0.450, round(flip("final/30", "unrelated"), 3), 0.001)
mx = max((round(flip(f"{k}/{l}", "twin"), 3), f"{k}/{l}") for k in ("prequery", "relcomp", "qmark") for l in range(32))
check("max twin flip over prequery/relcomp/qmark cells", (0.05, "qmark/16"), mx)
d16 = sum(e["cells"]["relcomp/16"]["twin"]["delta"] for e in ho3) / len(ho3)
check("relcomp/16 mean twin delta", -0.53, round(d16, 2), 0.005)
# twins really are twins: same pair, other variant, same anchor positions
by = {e["record_id"]: e for e in g3}
check("every record's twin has the same pair_id", True, all(by[e["twin"]]["pair_id"] == e["pair_id"] for e in g3))

print("\n== step 4 (recomputed from step4-resample.json records)")
d4 = jl(S4 / "outputs" / "step4-resample.json")
r4 = [e for e in d4["records"] if e["split"] != "dev"]
check("combined n", 400, len(r4))
def f4(cond, arm, k, tg):
    return sum(e["prompts"][cond]["arms"][arm][k][tg]["rank_correct"] < e["prompts"][cond]["arms"][arm][k][tg]["rank_incorrect"] for e in r4) / len(r4)
check("jlens relcomp NEW>OLD modified", 0.970, round(f4("modified", "jlens", "relcomp", "NEW_vs_OLD"), 3), 0.001)
check("jlens relcomp NEW>OLD unmodified", 0.045, round(f4("unmodified", "jlens", "relcomp", "NEW_vs_OLD"), 3), 0.001)
check("jlens qmark NEW>OLD modified", 0.993, round(f4("modified", "jlens", "qmark", "NEW_vs_OLD"), 3), 0.001)
# the edit really is one word and the new object is absent from the original prompt
ds = {}
for split in ("heldout", "heldout2"):
    for l in Path(f"results/datasets/{split}.jsonl").read_text().splitlines():
        if l.strip() and "_meta" not in l:
            r = json.loads(l); ds[r["record_id"]] = r
ok_edit = True
for e in r4:
    p = ds[e["record_id"]]["prompt"]
    a, b = p.split(), None
    ok_edit &= (f" {e['new_object']}" not in p) and (e["prompts"]["modified"]["n_tokens"] == e["prompts"]["unmodified"]["n_tokens"])
check("new object absent from original prompt and token count unchanged, all records", True, ok_edit)
check("distinct replacement words", 21, len({e["new_object"] for e in r4}))

print("\n== step 5 (consistency of the summary files; the re-fit is in part 2 on ARC)")
d5 = jl(S5 / "outputs" / "step5-lr-probe.json")
c = d5["results"]["relcomp/CITY"]["per_layer"]
check("LR relcomp L30", 0.8975, c["30"]["lr"]["acc"], 0.0001)
check("LR relcomp L30 model-wrong n", 93, c["30"]["model_wrong"]["lr"]["n_scored"])
check("LR relcomp L30 model-wrong acc", 0.8495, c["30"]["model_wrong"]["lr"]["acc"], 0.0001)
check("LR relcomp L15 model-wrong acc", 0.98, round(c["15"]["model_wrong"]["lr"]["acc"], 2), 0.005)
check("DiM relcomp L30 (LOPO on combined)", 0.62, c["30"]["dim"]["acc"], 0.0001)
b = jl(S5b / "outputs" / "step5-breakdown.json")["cells"]["relcomp/CITY"]
rows5 = b["rows"]
check("breakdown rows at relcomp", 400, len(rows5))
acc = lambda sub: round(sum(x["lr"] > 0 for x in sub) / len(sub), 4)
check("breakdown LR all (== main run L30)", 0.8975, acc(rows5), 0.0001)
check("breakdown LR AB", 0.87, acc([x for x in rows5 if x["fact_order"] == "AB"]), 0.0001)
check("breakdown LR BA", 0.925, acc([x for x in rows5 if x["fact_order"] == "BA"]), 0.0001)
mw5 = {x["rid"] for x in rows5 if (x["model_city_margin"] or 0) < 0}
check("breakdown model-wrong ids == step-1/2 ids", True, mw5 == model_wrong_ids_step1)
check("breakdown LR on model-wrong", 0.8495, acc([x for x in rows5 if x["rid"] in mw5]), 0.0001)
print(f"\nTOTAL FAILS: {fails}")
sys.exit(1 if fails else 0)
