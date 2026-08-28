"""Cross-reference: does the J-Lens readout succeed where the MODEL fails?

METHOD EVALUATION using a narrow task as instrument; not circuit discovery.

Two outcomes are sharply diagnostic, and they point opposite ways:

  readout right where the model is WRONG  -> the readout sees something the
      behaviour does not. A stronger claim than the current headline.
  readout fails exactly where the model fails -> direct support for the
      answer-shadow account: the readout may be reporting the computed answer
      rather than the binding it routed through.

No GPU. Reads two committed run records and the dev split. The join is on the
PROMPT STRING, because the eligibility screen generated its own pairs via
build_pairs() while Stage 1 read dev.jsonl, and the pair_id namespaces are not
known to agree. If the prompts do not overlap, that is reported and nothing is
computed -- a join on mismatched stimuli would be worse than no answer.

Every number `agent-unverified`.
"""
import json, sys
from pathlib import Path

ELIG = Path("results/runs/20260827T090437Z-eligibility-screen/outputs/eligibility-screen.json")
PASS = Path("results/runs/20260827T154016Z-stage1-passive-readout/outputs/stage1-passive-readout.json")
DEV  = Path("results/datasets/dev.jsonl")

def norm(p):
    return " ".join(p.split())

elig = json.loads(ELIG.read_text())
cell = next((c for c in elig["cells"]
             if c["lexicon"] == "real" and c["shot"] == "zero"), None)
if cell is None:
    sys.exit("no real/zero cell in the eligibility record")

model = {}          # prompt -> behaviourally correct?
for v in cell["per_variant"]:
    model[norm(v["prompt"])] = bool(v["text_match"])

pas = json.loads(PASS.read_text())
sel = pas["summary"]["jlens"]["final"]["selected_layer"]
readout = {}        # prompt -> readout correct?
dev = {}
for line in DEV.read_text().splitlines():
    r = json.loads(line)
    if not r.get("_meta"):
        dev[r["record_id"]] = r
for rec in pas["records"]:
    if rec["arm"] != "jlens":
        continue
    d = dev.get(rec["record_id"])
    if d is None:
        continue
    c = rec["scores"]["final"][str(sel)]["intermediate"]
    readout[norm(d["prompt"])] = c["rank_correct"] < c["rank_incorrect"]

shared = sorted(set(model) & set(readout))
print(f"eligibility real/zero variants : {len(model)}")
print(f"stage-1 dev records (jlens)    : {len(readout)}")
print(f"prompts present in BOTH        : {len(shared)}")
print(f"selected layer                 : {sel}")

if not shared:
    print()
    print("NO OVERLAP. The eligibility screen and the dev split do not share")
    print("stimuli, so this cross-reference cannot be computed from committed")
    print("data. Behavioural labels for the dev prompts would have to be")
    print("generated -- that needs the GPU, and it is a new run, not an")
    print("analysis. Reported rather than forced.")
    sys.exit(0)

a = b = c = d = 0          # model x readout
for p in shared:
    m, r = model[p], readout[p]
    if m and r: a += 1
    elif m and not r: b += 1
    elif not m and r: c += 1
    else: d += 1

print()
print("                    readout RIGHT   readout WRONG")
print(f"  model RIGHT       {a:>13}   {b:>13}")
print(f"  model WRONG       {c:>13}   {d:>13}")
print()
n_wrong = c + d
print(f"n = {len(shared)}; model wrong on {n_wrong}")
if n_wrong:
    print(f"readout accuracy WHERE THE MODEL FAILS : {c}/{n_wrong} = {c/n_wrong:.3f}")
if a + b:
    print(f"readout accuracy where the model succeeds: {a}/{a+b} = {a/(a+b):.3f}")
print()
if n_wrong == 0:
    print("The model got every shared prompt right, so this comparison has no")
    print("discriminating cases. It rules nothing in or out.")
elif n_wrong < 5:
    print(f"Only {n_wrong} discriminating case(s). Too few to read either way;")
    print("report the counts, draw no conclusion.")
json.dump({"n_shared": len(shared), "selected_layer": sel,
           "model_right_readout_right": a, "model_right_readout_wrong": b,
           "model_wrong_readout_right": c, "model_wrong_readout_wrong": d,
           "status": "agent-unverified"},
          open("/tmp/xref-result.json", "w"), indent=2)
print("wrote /tmp/xref-result.json")
