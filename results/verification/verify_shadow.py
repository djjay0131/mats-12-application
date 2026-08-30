#!/usr/bin/env python
"""Check 1: independent re-derivation of the 37/40 output shadow.
Self-configuring: model id comes from the run manifest, dataset field names
are auto-detected and printed. Override with env vars MODEL= and REV= if the
auto-detection picks wrong. No pipeline code is imported.
"""
import json, os
from pathlib import Path

REPO = Path("/scratch/djjay/mats12/repo")
DEV = REPO / "results/datasets/dev.jsonl"
MANIFEST = REPO / "results/runs/20260827T154016Z-stage1-passive-readout/manifest.json"

# ---- model id / revision: env override, else walk the manifest -------------
model_id, rev = os.environ.get("MODEL"), os.environ.get("REV")
pairs = []
def walk(o, prefix=""):
    if isinstance(o, dict):
        for k, v in o.items(): walk(v, prefix + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, prefix + f"[{i}]")
    else:
        pairs.append((prefix.lower(), o))
walk(json.load(open(MANIFEST)))
if not model_id:
    for k, v in pairs:
        if isinstance(v, str) and "model" in k and ("/" in v or "qwen" in v.lower()) and not v.endswith((".json", ".jsonl", ".py")):
            model_id = v; break
if not rev:
    for k, v in pairs:
        if isinstance(v, str) and k.rsplit("/", 1)[-1] in ("revision", "rev", "model_revision"):
            rev = v; break
print(f"MODEL = {model_id}\nREV   = {rev}")
assert model_id, "no model found in manifest — rerun as: MODEL=<id> python verify_shadow.py"

# ---- dataset: split records from metadata, auto-detect field names ---------
lines = [json.loads(l) for l in open(DEV) if l.strip()]
recs  = [d for d in lines if isinstance(d, dict) and not d.get("_meta")]
meta  = [d for d in lines if isinstance(d, dict) and d.get("_meta")]
print(f"\nlines={len(lines)}  records={len(recs)}  metadata_lines={len(meta)}")
for m in meta:
    print("META:", str(m)[:300])
if len(recs) != 40:
    print(f"*** NOTE: {len(recs)} records, expected 40 ***")

def pick(d, names, pred=None):
    low = {k.lower(): k for k in d}
    for n in names:
        if n in low: return low[n]
    if pred:
        for k, v in d.items():
            if pred(k, v): return k
    return None

r0 = recs[0]
K_PROMPT = pick(r0, ["prompt", "text", "input", "question"], lambda k, v: isinstance(v, str) and len(v) > 40)
K_ID     = pick(r0, ["record_id", "id", "uid", "name", "pair_id"])
K_CORR   = pick(r0, ["intermediate", "correct_intermediate", "intermediate_correct", "target_intermediate", "intermediate_true"])
K_TWIN   = pick(r0, ["intermediate_alt", "alt_intermediate", "twin", "incorrect_intermediate", "intermediate_incorrect", "distractor", "counterfactual_intermediate", "intermediate_cf", "intermediate_other"])
print(f"\nfield mapping: id={K_ID}  prompt={K_PROMPT}  correct={K_CORR}  twin={K_TWIN}")
print("first record for eyeball check:")
print(json.dumps(r0, indent=2)[:900])
assert K_PROMPT and K_CORR and K_TWIN, \
    "auto-detect failed — read the record above and hardcode the three keys near the top of the loop"

# ---- model ------------------------------------------------------------------
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
tok = AutoTokenizer.from_pretrained(model_id, revision=rev)
model = AutoModelForCausalLM.from_pretrained(model_id, revision=rev, dtype=torch.bfloat16).to("cuda").eval()

def tid(w):
    ids = tok(" " + str(w), add_special_tokens=False)["input_ids"]
    return ids[0] if len(ids) == 1 else None

# ---- one row per record: hand-count the WIN column --------------------------
print(f"\n{'id':<14} {'ntok':>4} {'tok20':>7} {'tok29':>7} {'correct':>10} {'twin':>10} {'margin':>8}  result")
wins = losses = skips = 0
margins = []
for i, r in enumerate(recs):
    rid = str(r.get(K_ID, i))
    enc = tok(r[K_PROMPT], return_tensors="pt")
    toks = tok.convert_ids_to_tokens(enc["input_ids"][0])
    n = len(toks)
    t20 = toks[20] if n > 20 else "-"
    t29 = toks[29] if n > 29 else "-"
    ci, ti = tid(r[K_CORR]), tid(r[K_TWIN])
    if ci is None or ti is None:
        print(f"{rid:<14} {n:>4} {t20:>7} {t29:>7} {str(r[K_CORR]):>10} {str(r[K_TWIN]):>10} {'—':>8}  SKIP (multi-token)")
        skips += 1; continue
    with torch.no_grad():
        logits = model(**enc.to(model.device)).logits[0, -1].float()
    m = (logits[ci] - logits[ti]).item()
    margins.append(m)
    res = "WIN" if m > 0 else "LOSS"
    wins += m > 0; losses += m <= 0
    flag = "" if (n == 30 and "." in t20 and ":" in t29) else "   <-- ALIGNMENT ODD"
    print(f"{rid:<14} {n:>4} {t20:>7} {t29:>7} {str(r[K_CORR]):>10} {str(r[K_TWIN]):>10} {m:>+8.3f}  {res}{flag}")

print(f"\nscript totals (confirm by hand-counting rows): WIN {wins}  LOSS {losses}  SKIP {skips}")
if margins:
    print(f"mean margin {sum(margins)/len(margins):+.3f}")
print("expected: 37 WIN / 3 LOSS, mean ~ +2.766, ntok 30, tok20 '.', tok29 ':'")
