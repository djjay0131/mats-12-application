# Verification Ledger

One row per headline number in the write-up, recording that **a human
independently re-derived it**. Checked by `scripts/conformance-check.mjs`
(BLK-01).

This is the single most consequential blocker in the whole register:

> "**Not sanity-checking your AI agents**. Coding agents are great and you
> should use them, but if your write-up contains key results you clearly
> never verified, or don't understand that's disqualifying. I want scholars
> with value add over prompting Claude myself"

"Re-derived" means: recomputed by a path that does not share the original
pipeline's code — a separate script, a spreadsheet, a hand count on a
sample, or a different library. Re-running the same script is not
verification.

A row is only complete when it says **verified** and names who and when.

| Claim ID | Number | Produced by | Independently re-derived how | Agreed? | Who / when | Status |
|---|---|---|---|---|---|---|
| CL-01 | *(example — delete)* 34.2% → 11.8% | `src/stagewise.py` | Hand-counted 50 random rollouts per endpoint in a spreadsheet | 33.8% / 12.4% — within noise | Jason, 2026-08-30 | verified |
| | | | | | | |

## The 60-second test (BLK-02)

For every figure in the write-up, say out loud — with the code closed —
what it shows, how it was computed, and what would make it wrong. If you
cannot, the figure does not ship.

| Figure | Explained unaided | Date |
|---|---|---|
| | | |
