# Controls Ledger

One row per claim, naming the cheap control that was actually run.
Checked by `scripts/conformance-check.mjs` (BLK-12).

Neel lists **"Failing to compare to baselines"** among the disqualifying
mistakes, and names the cheap ones directly:

> "eg replace your vector with a random one, choose randomly, ask an LLM,
> use a linear probe"

> "Skipping the cheap control: fine-tune on random data, replace your
> vector with a random one, compare against 'just ask the model'."

| Claim ID | Control run | What it would have shown if the result were spurious | Result | Where |
|---|---|---|---|---|
| CL-01 | *(example — delete)* Random-hint control: same pipeline, hint replaced with an irrelevant token | Stage-wise "faithfulness" curve would appear even with no real hint influence | Flat, 2.1% ± 0.8 across all stages | `results/canonical.json#random_hint` |
| | | | | |

Standard cheap controls to reach for first:
- random vector in place of the steering vector
- random / shuffled labels
- "just ask the model" — prompting baseline
- a linear probe
- an unrelated model at matched scale
