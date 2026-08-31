# The pipeline's readout convention, read from vendor source

Written 2026-08-30 in response to the open read-off in `verify_ranks.py`
("note which one in the log"). This is a SOURCE READING, not a run: every line
below cites `vendor/jacobian-lens/jlens/` at the pinned commit `581d398`.

## The convention

1. **Layer index = block output.** `ActivationRecorder` registers
   `register_forward_hook` on `model.layers[i]` (`hooks.py:62`), so
   **jlens `L_i` is the residual AFTER block `i`**. In HF
   `output_hidden_states` terms: jlens `L_i` = `hidden_states[i+1]`
   (`hidden_states[0]` is the embedding output). This is the off-by-one the
   verify-ranks commit identified.

2. **The unembedding includes the final norm.** `unembed(residual)` =
   `lm_head(final_norm(residual))`, plus a tanh softcap only when the config
   sets `final_logit_softcapping` (`hf.py:166-174`). A bare
   `residual @ W_U` reproduces nothing.

3. **J-Lens composition = `Jh+n`** in verify_ranks' terms: `transport()`
   computes `residual @ J.T` (= `J @ h`, `lens.py:143`) and `apply()` then
   calls `unembed` on it (`lens.py:210-213`) — so J transport, THEN final
   norm, THEN `lm_head`.

4. **`model_logits` is the true model output.** `final_layer = n_layers - 1`
   with `n_layers = config.num_hidden_layers = 32` for this model
   (`hf.py:126`, checked against the pinned snapshot's config), so
   `model_logits = unembed(residual after block 31)` — the model's real
   next-token distribution. This is why the independent shadow re-derivation
   (`verify-shadow-554518.out`) matches the pipeline's `model_behaviour`
   numbers exactly.

5. **Therefore L30 is the PENULTIMATE block, not the last layer.** The lens
   is fitted on source layers 0..30 of a 32-block model; block 31 has no
   jacobian and is never read by either lens arm.

## What this changes, and what it does not

- Every earlier description of "L30, the last layer, both approximately the
  model's output" was **wrong**: L30 is one block short of the output, read
  through the final norm. Corrected where it appears
  (`results/stage2/answer-shadow-and-replication.md`).
- The **shadow result is untouched**: it rests on `model_logits` (the true
  block-31 output), independently re-derived at 37/3/0, mean +2.767.
- The **anchor interpretation shifts**: r=0.811 for "logit lens L30 vs the
  model's own margin" is now "a passive linear readout one block below the
  output couples to the output at 0.811" — an empirical anchor still, just
  not a tautological one. J-Lens's 0.771 against it reads the same way.
- For `verify_ranks.py` to land on the recorded values it needs
  `hidden_states[i+1]` for jlens `L_i` and the `Jh+n` composition. That
  re-run is deliberately left to Jason — the point of that script is
  independence from the pipeline and from the agent.

`agent-unverified` (a source reading; the file/line cites are the check).
