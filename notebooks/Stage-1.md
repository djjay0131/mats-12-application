[djjay@fal015 repo]$ # (a) the exact model id + revision the pipeline used
grep -ri "qwen\|model" results/runs/20260827T154016Z-stage1-passive-readout/*manifest* | head
# expect a Qwen3.5 id and revision starting 851bf6e

# (b) the dev split file and its schema
find results -iname "*dev*" -o -iname "*split*" | grep -iv slurm
python3 - <<'EOF'
import json,glob
p = sorted(glob.glob("results/datasets/*dev*"))[0]; print(p)
recs = [json.loads(l) for l in open(p)] if p.endswith("jsonl") else json.load(open(p))
print(len(recs)); print(json.dumps(recs[0], indent=2)[:1500])
EOF
# note the field names for: record_id, prompt text, correct intermediate,
# role-swapped twin, correct answer. Fix FIELD_* in the scripts below.

# (c) the per-record stage-2 analysis table (for checks 3 and 4)
ls results/stage2/ results/runs/ | grep -i "join\|record\|csv\|analysis"
    "model_repo": "Qwen/Qwen3.5-4B",
    "model_revision": "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a",
    "lens_revision": "qwen-n1000",
    "lens_file": "qwen3.5-4b/jlens/Salesforce-wikitext/Qwen3.5-4B_jacobian_lens_n1000.pt",
results/datasets/dev.jsonl
results/runs/20260827T154143Z-stage1-supervised-reference/outputs/centroids-dev.pt
results/runs/20260828T164704Z-stage1-supervised-reference/outputs/centroids-dev.pt
results/datasets/dev.jsonl
41
{
  "_meta": true,
  "header": "DEV split. Method evaluation, not circuit discovery. Develop, tune and debug against this file only.",
  "seed": 20260827,
  "model": "Qwen/Qwen3.5-4B",
  "revision": "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a",
  "lexicons": [
    "real"
  ],
  "shot": "zero",
  "vocab_pool": 6,
  "framing": "method evaluation, not circuit discovery",
  "split": "dev",
  "n_pairs": 10
}

import json, sys, glob, torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL   = "FIXQwen/Qwen3.5-4B"      # exact id from the manifest
REV     = "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a"           # revision from the manifest
DEVPATH = "/results/runs/20260827T154016Z-stage1-passive-readout/outputs/stage1-passive-readout.json"
F_ID, F_PROMPT, F_CORR, F_TWIN = "record_id", "prompt", "intermediate", "intermediate_alt"  # fix to real names

recs = [json.loads(l) for l in open(DEVPATH)] if DEVPATH.endswith("jsonl") else json.load(open(DEVPATH))
assert len(recs) == 40, len(recs)

tok = AutoTokenizer.from_pretrained(MODEL, revision=REV)
model = AutoModelForCausalLM.from_pretrained(MODEL, revision=REV,
        torch_dtype=torch.bfloat16, device_map="auto").eval()

def tid(w):
    ids = tok(" " + w, add_special_tokens=False)["input_ids"]
    assert len(ids) == 1, (w, ids)      # single-token by construction
    return ids[0]

wins, margins = 0, []
for r in recs:
    enc = tok(r[F_PROMPT], return_tensors="pt")
    toks = tok.convert_ids_to_tokens(enc["input_ids"][0])
    # CHECK 5 rides along: alignment, per record
    assert len(toks) == 30 and "." in toks[20] and ":" in toks[29], (r[F_ID], len(toks), toks[20], toks[29])
    with torch.no_grad():
        logits = model(**enc.to(model.device)).logits[0, -1].float()
    m = (logits[tid(r[F_CORR])] - logits[tid(r[F_TWIN])]).item()
    margins.append(m); wins += m > 0
    print(f"{r[F_ID]}  margin={m:+.3f}  {'WIN' if m>0 else 'LOSS'}")
print(f"\nwins {wins}/40   mean margin {sum(margins)/40:+.3f}")



