# Hand-verification instructions — 2026-08-29

Purpose: re-derive every load-bearing number in the write-up **by a path that
does not share the pipeline's code**, per the Stage 2 doc's own rule and
Neel's "unverified key results are disqualifying."

Where: **Falcon**, `/scratch/djjay/mats12/repo`, on the `exp/v1-v3-verification`
checkout at commit `06ef3a5` or later. Get a GPU shell first:

```bash
cd /scratch/djjay/mats12/repo
srun --account=agents4research -p a30_normal_q,l40s_normal_q --gres=gpu:1 -t 01:30:00 --mem=64G --pty bash
source <your stage-2 venv>   # only for torch/transformers, NOT the pipeline
```

Log every check as you finish it in `results/verification-log.md`:
date, check, expected value, what you got, matched or not. Flip the
corresponding write-up numbers from `agent-unverified` to `jason-verified`.

---

## STEP 0 — Discovery (10 min, no GPU needed)

The scripts below need three facts. Find them once, write them down:

```bash
# (a) the exact model id + revision the pipeline used
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
```

---

## CHECK 1 — The 37/40 output shadow  ⟵ mandatory
**Expected: 37/40 wins, mean intermediate margin ≈ +2.766**
(also: answer beats alt-answer 40/40, mean ≈ +2.442; rank_answer==1 on 30/40)

This is "run the 40 dev prompts": the 40 records in the dev split from step
0(b), fed one at a time to the plain HuggingFace model — no pipeline imports,
no batching (single-prompt is the clean reference; batching is what flips
2/8 on the A100).

Save as `results/verification/verify_shadow.py` (new dir, yours):

v2 — hand-count edition. Nothing is dropped silently, nothing asserts mid-run;
every record prints one row and YOUR count of the WIN column is the result.
The script's totals at the bottom are a convenience, not the verification.

```python
import json, torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL   = "FIXME-from-manifest"     # exact id from manifest.json
REV     = None                       # or the revision hash from manifest.json
DEVPATH = "results/datasets/dev.jsonl"
F_ID, F_PROMPT, F_CORR, F_TWIN = "record_id", "prompt", "intermediate", "intermediate_alt"  # fix to real names

# --- load: show everything, drop nothing silently -------------------------
parsed = [json.loads(l) for l in open(DEVPATH) if l.strip()]
recs, other = [], []
for d in parsed:
    (recs if isinstance(d, dict) and F_PROMPT in d and F_CORR in d else other).append(d)
print(f"non-empty lines parsed: {len(parsed)}   records: {len(recs)}   non-record lines: {len(other)}")
for d in other:
    print("  NON-RECORD LINE (first 200 chars):", str(d)[:200])
if len(recs) != 40:
    print(f"*** NOTE: {len(recs)} records, expected 40 — eyeball the list before trusting totals ***")

# --- model ----------------------------------------------------------------
tok = AutoTokenizer.from_pretrained(MODEL, revision=REV)
model = AutoModelForCausalLM.from_pretrained(MODEL, revision=REV,
        torch_dtype=torch.bfloat16, device_map="auto").eval()

def tid(w):
    ids = tok(" " + w, add_special_tokens=False)["input_ids"]
    return ids[0] if len(ids) == 1 else None   # None = not single-token

# --- one row per record; count the WIN column by hand ---------------------
print(f"\n{'id':<12} {'ntok':>4} {'tok20':>6} {'tok29':>6} {'correct':>10} {'twin':>10} {'margin':>8}  result")
wins = losses = skips = 0
margins = []
for r in recs:
    enc = tok(r[F_PROMPT], return_tensors="pt")
    toks = tok.convert_ids_to_tokens(enc["input_ids"][0])
    n = len(toks)
    t20 = toks[20] if n > 20 else "-"
    t29 = toks[29] if n > 29 else "-"
    ci, ti = tid(r[F_CORR]), tid(r[F_TWIN])
    if ci is None or ti is None:
        print(f"{str(r[F_ID]):<12} {n:>4} {t20:>6} {t29:>6} {r[F_CORR]:>10} {r[F_TWIN]:>10} {'—':>8}  SKIP (multi-token word)")
        skips += 1; continue
    with torch.no_grad():
        logits = model(**enc.to(model.device)).logits[0, -1].float()
    m = (logits[ci] - logits[ti]).item()
    margins.append(m)
    res = "WIN" if m > 0 else "LOSS"
    wins += m > 0; losses += m <= 0
    flag = "" if (n == 30 and "." in t20 and ":" in t29) else "   <-- ALIGNMENT ODD, note it"
    print(f"{str(r[F_ID]):<12} {n:>4} {t20:>6} {t29:>6} {r[F_CORR]:>10} {r[F_TWIN]:>10} {m:>+8.3f}  {res}{flag}")

print(f"\nscript totals (confirm by hand-counting the rows above):")
print(f"  WIN {wins}   LOSS {losses}   SKIP {skips}   mean margin {sum(margins)/max(len(margins),1):+.3f}")
print("expected: 37 WIN / 3 LOSS, mean about +2.766, ntok 30, tok20 '.', tok29 ':' on every row")
```

Run: `python results/verification/verify_shadow.py | tee results/verification/shadow-check.txt`

How to read it, by hand:
- Count the WIN rows yourself → that is your verified 37 (or not).
- The 3 LOSS row ids → your Check 2 reading list.
- Any ALIGNMENT ODD flag or SKIP row → copy that record id into the log and
  look at it before anything else; do not average over it.
- Any NON-RECORD LINE printed at the top → that is the 41st line mystery;
  paste it into the log (it is probably dataset metadata, which also settles
  the vocab_pool/seed provenance question).

- 37/40 and ≈+2.766 → the shadow claim is verified.
- The 3 LOSS record ids are your input to CHECK 2. If you get 36 or 38, note
  it — that's the padding/greedy fp sensitivity, and it belongs in the
  write-up next to the eligibility instability, not silently reconciled.
- If the position assert fires: STOP. That is a real finding about alignment.

## CHECK 2 — Read the 3 discriminating records by eye
**Expected ids: the 3 with model margin < 0 in Check 1 (Stage 2: J-Lens right on 2, wrong on the one with model margin −1.19).**

For each of the 3: print the full prompt, then generate:

```python
out = model.generate(**tok(r[F_PROMPT], return_tensors="pt").to(model.device),
                     max_new_tokens=12, do_sample=False)
print(tok.decode(out[0]))
```

Read them. Confirm the prompt is well-formed, the model's continuation is what
`text_match` says it is, and the "wrong intermediate preferred" is real, not a
tokenization artifact (e.g. the twin appearing in a different surface form).
Write two sentences per record in the log.

## CHECK 3 — Recompute r = 0.771 and the 0.811 anchor yourself
**Expected: J-Lens L27 final margin vs model intermediate margin r ≈ +0.771;
logit-lens L30 vs same ≈ +0.811; J-Lens vs model ANSWER margin ≈ −0.016;
J-Lens L25 prequery vs model intermediate ≈ +0.445.**

From the per-record table found in step 0(c) — do NOT rerun the pipeline,
just recompute the statistic from its logged per-record numbers:

```python
import numpy as np
# x, y = the two margin columns, loaded with json/csv by hand
r = np.corrcoef(x, y)[0, 1]
```

Four correlations, four lines in the log. If a column you need isn't in the
table, that's a bookkeeping gap to record — not something to regenerate.

## CHECK 4 — Spot-check ranks at L27 (J-Lens) and L30 (logit lens), 5 records
**Expected: J-Lens L27 final, median rank ≈ 35 across all 40 (frac 0.975);
logit lens L30 ≈ 19. Your 5 records should be consistent with the recorded
per-record ranks, not just the median.**

Independent path = your own matmul on hidden states from plain transformers:

```python
with torch.no_grad():
    out = model(**enc.to(model.device), output_hidden_states=True)
h30 = out.hidden_states[30][0, -1]          # hidden_states[k] = after block k; [0] = embeddings
# logit lens at the last layer == model output (built-in sanity check):
ll  = model.lm_head(model.model.norm(h30)).float()
assert torch.allclose(ll, out.logits[0, -1].float(), atol=1e-2)
rank = int((ll > ll[tid(r[F_CORR])]).sum())  # 0-based rank over the full 248,320 vocab
```

For J-Lens: load the pre-fitted lens artifact (vendor
`/scratch/djjay/mats12/vendor/jacobian-lens`, or the published checkpoint the
manifest names), extract the layer-27 matrix and apply it to
`out.hidden_states[27][0,-1]` with your own matmul. Discover the attribute
names with `print(vars(lens).keys())`. Using the vendor lib only to LOAD the
weights is fine; the multiplication and ranking must be your code.

Compare your 5 ranks to the same records' ranks in the run record. Watch for
the classic failure this check exists to catch: an off-by-one on
`hidden_states` indexing or a missing final-norm producing plausible-looking
but wrong ranks. Do 2 of the 5 at the prequery position (index 20), L25:
**expected neighborhood ≈ 346 (J-Lens) vs ≈ 78,500 (logit lens)** — CHECK 7
rides along here.

## CHECK 6 — Behavioural labels and the padding flip
**Expected: text_match 39/40 correct on TinkerCliffs join (40/40 eligibility
screen on Falcon, 36/40→AB 0.900 on TC); padding control 2/8 mismatched on
both Stage-2 screens.**

- Read all 40 generated outputs in the run record (or regenerate with the
  Check 2 snippet) and count correct answers by eye.
- Pull the ids of the 2/8 padding-mismatched prompts from the screen's log,
  generate each one-at-a-time greedy, and compare to the batched output
  recorded. Seeing one flip with your own eyes is the point.

## Optional — arm 3 LOO 0.650
Only if arm 3 stays load-bearing in §2.5: re-derive with sklearn
NearestCentroid you configure yourself, leave-one-PAIR-out (not one record),
on the cached L30 final-position residuals. Expected 0.650 (TC) / 0.625
(Falcon), 0 unscorable.

---

## What each expected number is anchored to
37/40, +2.766, 40/40, +2.442, 30/40 — `claude/answer-shadow-result-2026-08-28.md` §"The answer".
r values — same doc, "the graded measure" table.
Median ranks 35/19, prequery 346/78,525 — same doc, rank tables.
Alignment idx 20 `'.'` / idx 29 `':'` — `claude/stage1-results-2026-08-27.md`.
AB 1.000/0.900, 2/8 padding — same Stage 2 doc, replication addendum.

Total ≈ 2.5 h GPU-attached. Checks 1+2+3 are non-negotiable; 4 is strongly
recommended; 6–7 are cheap. Every mismatch found is a result, not a setback —
record it, don't reconcile it.
