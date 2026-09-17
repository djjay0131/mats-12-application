# Verification log — Jason, hand-verified results

Rule: every entry = what I checked, how, expected vs got, matched or not.
Numbers verified here get flipped from `agent-unverified` to `jason-verified`
in the write-up.

## 2026-08-29

- Step 0 facts: MODEL = Qwen/Qwen3.5-4B  REV = '851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a',
  DEVPATH = results/datasets/dev.jsonl  fields = {"pair_id","record_id","template_id","lexicon","fact_order","variant","cell":,"shot","seed","prompt","prompt_n_tokens","person_q","person_d","intermediate","answer","alt_intermediate","alt_answer","intermediate_id","answer_id","alt_intermediate_id","alt_answer_id"}

- dev.jsonl structure: 1 header line + 40 records. Hand-counted 40; parser
  initially reported 41; discrepancy explained by the header.

- Header contents (seed / vocab_pool / etc.): {"_meta":true,"header":"DEV split. Method evaluation, not circuit discovery. Develop, tune and debug against this file only.","seed":20260827,"model":"Qwen/Qwen3.5-4B","revision":"851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a","lexicons":["real"],"shot":"zero","vocab_pool":6,"framing":"method evaluation, not circuit discovery","split":"dev","n_pairs":10}

## Check 1 — output shadow (37/40)
- Method: verify_shadow.py v2, independent path (plain transformers,
  single-prompt, greedy-free logit read at final position).
- Expected: 37 WIN / 3 LOSS, mean margin ≈ +2.766.
- Got: Hand counted 40, 3 LOSS, no anomolies.
- LOSS record ids: real-zero-002-BAB, real-zero-004-BBA, real-zero-009-BAB
- Alignment: ntok=30, tok20='.', tok29=':' on all rows? yes

## Check 2 — the 3 discriminating records, read by hand
- {"pair_id":"real-zero-002","record_id":"real-zero-002-BBA","template_id":"T3","lexicon":"real","fact_order":"BA","variant":"B","cell":"B/BA","shot":"zero","seed":20260829,"prompt":"Facts: Simon studies at Seattle. Victor studies at Dublin. Seattle teaches bronze. Dublin teaches rubber. What is taught where Victor studies? Answer:","prompt_n_tokens":30,"person_q":"Victor","person_d":"Simon","intermediate":"Dublin","answer":"rubber","alt_intermediate":"Seattle","alt_answer":"bronze","intermediate_id":31785,"answer_id":21970,"alt_intermediate_id":15875,"alt_answer_id":38486}
- Prompt looks good, values are present and opposite.  One thing that could be odd is a City is Teaching?

- {"pair_id":"real-zero-004","record_id":"real-zero-004-BBA","template_id":"T5","lexicon":"real","fact_order":"BA","variant":"B","cell":"B/BA","shot":"zero","seed":20260831,"prompt":"Facts: Helen trains at Dublin. Emma trains at Athens. Dublin offers bronze. Athens offers timber. What is offered where Emma trains? Answer:","prompt_n_tokens":30,"person_q":"Emma","person_d":"Helen","intermediate":"Athens","answer":"timber","alt_intermediate":"Dublin","alt_answer":"bronze","intermediate_id":44299,"answer_id":43299,"alt_intermediate_id":31785,"alt_answer_id":38486}
- Prompt looks good and balanced.  Not sure if traning and a city offering timber or bronze makes sense or matters.

- {"pair_id":"real-zero-009","record_id":"real-zero-009-BAB","template_id":"T4","lexicon":"real","fact_order":"AB","variant":"B","cell":"B/AB","shot":"zero","seed":20260836,"prompt":"Facts: Robert shops at Seattle. Grace shops at Prague. Prague sells bronze. Seattle sells timber. What is sold where Robert shops? Answer:","prompt_n_tokens":30,"person_q":"Robert","person_d":"Grace","intermediate":"Seattle","answer":"timber","alt_intermediate":"Prague","alt_answer":"bronze","intermediate_id":15875,"answer_id":43299,"alt_intermediate_id":65019,"alt_answer_id":38486}
- Prompt looks good and balanced, and htis time the prompt makes senese on both ends.  


## Check 3 — correlations recomputed
- Source table: results/runs/20260829T033509Z-output-shadow-audit/outputs/output-shadow-audit.json
- Expected 0.771 / 0.811 / -0.016 / 0.445 — got: same

## Check 4 / 7 — rank spot checks
- Records checked: real-zero-002-BAB, real-zero-004-BBA, real-zero-009-BAB
, layer/position, my rank vs recorded rank: <fill in>

## Check 6 — behavioural labels & padding control (hand-checked 2026-08-30)
- Source: results/runs/20260829T205245Z-eligibility-screen/outputs/eligibility-screen.json (Falcon).
- Per-pair table read by hand: 40 variant-cells, 39 true / 1 false; failing cell
  real-zero-009 A/AB. Matches the 39/1 shape.
- pair_eligibility_AB = 0.900 on this Falcon run vs 1.000 on Falcon job 551581
  (Aug 28): the eligibility number is unstable run-to-run on the SAME cluster,
  not only across GPU architectures. [Pending: confirm the Aug 29 run's config
  matches 551581 before quoting this — see command.txt/manifest.]
- Padding control mismatches (both read in full): batched vs unbatched outputs
  differ only in phrasing; final answers identical and correct in both
  (Athens→granite, Bristol→linen). On this run the 2/8-style mismatch is
  surface wording, not an answer flip.
- Not verified from raw text: the one false label (009 A/AB) — boolean only;
  raw generation not stored in this output file.
