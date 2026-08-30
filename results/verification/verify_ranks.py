#!/usr/bin/env python
"""Check 4 (+7), v2.
Fixes vs v1: (a) logit-lens sanity now reports max|diff| / top-token / rank
agreement instead of a bf16-hostile allclose; (b) J-Lens jacobians[L] is a
d_model x d_model residual->residual map, so the readout must compose with the
unembedding — we compute all four candidate compositions and also print the
pipeline's recorded scores for the same records so the right convention
identifies itself.
"""
import json, os, glob, torch
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "Qwen/Qwen3.5-4B"
MODEL_REV = "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a"
LENS_REPO, LENS_REV = "neuronpedia/jacobian-lens", "qwen-n1000"
LENS_FILE = "qwen3.5-4b/jlens/Salesforce-wikitext/Qwen3.5-4B_jacobian_lens_n1000.pt"
DEV = "results/datasets/dev.jsonl"
N_SPOT = 5

lines = [json.loads(l) for l in open(DEV) if l.strip()]
recs = [d for d in lines if isinstance(d, dict) and not d.get("_meta")]
spot = recs[:N_SPOT]
K_ID, K_PROM, K_CORR, K_TWIN = "record_id", "prompt", "intermediate", "alt_intermediate"

tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REV,
        dtype=torch.bfloat16).to("cuda").eval()

def tid(w):
    ids = tok(" " + str(w), add_special_tokens=False)["input_ids"]
    assert len(ids) == 1, (w, ids)
    return ids[0]

def rank_of(scores, token_id):
    return int((scores > scores[token_id]).sum().item())

def unembed(v):
    return model.lm_head(v.to(torch.bfloat16)).float()

lp = snapshot_download(LENS_REPO, revision=LENS_REV,
                       allow_patterns=["qwen3.5-4b/jlens/Salesforce-wikitext/*"])
from jlens import JacobianLens
lens = JacobianLens.load(os.path.join(lp, LENS_FILE))
print("lens: d_model", lens.d_model, "layers", lens.source_layers[0], "..", lens.source_layers[-1])

# pipeline's recorded scores for these record ids, for convention matching
recorded = {}
for p in sorted(glob.glob("results/runs/*stage1-passive-readout/outputs/*.json"))[-1:]:
    for r in json.load(open(p)).get("records", []):
        if r.get("arm") == "jlens" and r.get("record_id") in {s[K_ID] for s in spot}:
            recorded[r["record_id"]] = r.get("scores")
    print(f"recorded jlens scores pulled from {p} for {len(recorded)} records")
if recorded:
    rid0 = next(iter(recorded))
    print(f"structure of recorded scores for {rid0} (first 500 chars):")
    print(json.dumps(recorded[rid0])[:500])

print(f"\n--- logit lens (own matmul) ---")
print(f"{'id':<18} {'pos':>8} {'L':>3} {'corr_rank':>9} {'twin_rank':>9}  sanity(final L30 only)")
hs_cache = {}
for i, r in enumerate(spot):
    rid = r[K_ID]
    enc = tok(r[K_PROM], return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model(**enc, output_hidden_states=True)
    hs_cache[rid] = (out, tid(r[K_CORR]), tid(r[K_TWIN]))
    ci, ti = hs_cache[rid][1], hs_cache[rid][2]
    positions = [("final", -1, 30)] + ([("prequery", 20, 24)] if i < 2 else [])
    for pname, p, L in positions:
        h = out.hidden_states[L][0, p]
        ll = unembed(model.model.norm(h))
        sanity = ""
        if pname == "final" and L == 30:
            real = out.logits[0, -1].float()
            sanity = (f"max|d|={float((ll-real).abs().max()):.3f} "
                      f"top1={'SAME' if int(ll.argmax())==int(real.argmax()) else 'DIFF'} "
                      f"rank(corr) {rank_of(ll,ci)} vs real {rank_of(real,ci)}")
        print(f"{rid:<18} {pname:>8} {L:>3} {rank_of(ll,ci):>9} {rank_of(ll,ti):>9}  {sanity}")

print(f"\n--- J-Lens: four candidate compositions of jacobians[L] with the unembedding ---")
print("variant key: Jh = J@h, JTh = J.T@h; +n = final norm applied before lm_head")
print(f"{'id':<18} {'pos':>8} {'L':>3} {'Jh':>9} {'Jh+n':>9} {'JTh':>9} {'JTh+n':>9}   (rank of correct intermediate)")
for i, r in enumerate(spot):
    rid = r[K_ID]
    out, ci, ti = hs_cache[rid]
    positions = [("final", -1, 27)] + ([("prequery", 20, 25)] if i < 2 else [])
    for pname, p, L in positions:
        h = out.hidden_states[L][0, p].float()
        J = lens.jacobians[L].to(h.device).float()
        variants = {
            "Jh":    unembed(J @ h),
            "Jh+n":  unembed(model.model.norm((J @ h).to(torch.bfloat16)).float()),
            "JTh":   unembed(J.T @ h),
            "JTh+n": unembed(model.model.norm((J.T @ h).to(torch.bfloat16)).float()),
        }
        row = "  ".join(f"{rank_of(v, ci):>8}" for v in variants.values())
        print(f"{rid:<18} {pname:>8} {L:>3} {row}")

print("\nread-off: the variant whose final-position ranks sit near the recorded values")
print("(median ~35 at L27; compare per-record against the recorded scores above)")
print("is the pipeline's convention. Note which one in the log; the other columns")
print("are the evidence you checked rather than assumed.")
