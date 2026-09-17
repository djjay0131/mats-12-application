# NOTE — crashed attempt, no outputs

This run produced no `outputs/` because the script raised an exception before
writing any results. It is recorded here honestly rather than deleted or
back-filled.

- Job 551581 (A30, node fal022), commit 23a8391 (dirty), 2026-08-28.
- `experiments/stage1/passive_readout.py` crashed at line 280 with
  `IndexError: index 37260 is out of bounds for dimension 0 with size 0` —
  it indexed `row[answer_id]` into an empty logit row. See `stdout.log`.
- No records file was produced. Nothing from this directory is reported as a
  result anywhere in the write-up.
- The passive readout was re-run successfully later the same evening; the
  Stage 1 numbers derive from those successful runs, not this one.

Kept as an honest gap in the record. No manifest field, output, or metric has
been manufactured for it.
