# Tech Context

Last updated: 2026-08-26

Durable environment and tooling facts. Transient state lives in
`activeContext.md`; how the pieces fit together lives in `systemPatterns.md`.

## Subject model and lens

| | |
|---|---|
| Model | `Qwen/Qwen3.5-4B` |
| Repo architecture | `Qwen3_5ForConditionalGeneration` (multimodal); resolves to `Qwen3_5ForCausalLM` |
| Layers / d_model / vocab | 32 / 2560 / 248320 |
| Tokenizer | `Qwen2Tokenizer`, `vocab_size` 248044, `len(tok)` 248077 |
| Precision | bfloat16 |
| Lens | `neuronpedia/jacobian-lens`, revision `qwen-n1000`, commit `16a01f3` |
| Lens provenance | fit by Neuronpedia against this exact model on `Salesforce/wikitext`, n=1000 prompts |
| Lens source layers | 0–30 (n=31), so `max(source_layers) < num_hidden_layers` |

**Do not fit a lens.** The pre-fitted public checkpoint is the substrate;
fitting one is outside the time budget.

Verified 2026-08-24, ARC job 550088: `COMPAT_ASSERTIONS: PASS`,
`LAYOUT_ASSERTIONS: PASS`, reference suite 32/32, model load 13.6 s, peak GPU
allocation 8.51 GB. Full detail:
`results/design-verification/environment-manifest.md`.

## Compute — Virginia Tech ARC

Account `agents4research`, user `djjay`, login `falcon1`. Partitions
available: `l40s`, `a30`, `v100`, `t4` (normal and preemptable).

| | |
|---|---|
| Primary | NVIDIA L40S, 47.7 GB — ample; the job peaks at 8.51 GB |
| Fallback | `a30_normal_q`, unrestricted for this association |
| Torch / CUDA | 2.13.0+cu130 / 13.0 |
| transformers | 5.16.1 |
| Scratch | `/scratch/djjay/mats12` (~15 GB staged) |

Queue latency ~23 min observed on L40S with 17 of 20 nodes draining. That is
setup time, not counted time, but it lengthens each gate's wall clock.

Neel recommends a rented cloud GPU over Colab; ARC satisfies that.

## Report toolchain

`pandoc`, `soffice` (LibreOffice), `pdftoppm`, `python3` with
`matplotlib` 3.10.9 / `numpy` 2.2.6, `node` for the checkers. All present on
the working VM.

## Known environment issues

- **B2 — no sparse non-negative J-space reconstruction** in the reference
  implementation at the pinned commit. The shipped API is
  `fit`/`apply`/`transport`/visualisation only. Load-bearing for the causal
  arm; scoped by ADR-0005 and settled at V2.
- **B3 — no published shuffled-corpus control lens.** All 40+ Neuronpedia
  lenses are fit on `Salesforce/wikitext`. The negative control falls back to
  label permutation plus norm-matched random directions.
- **B4 — tokenizer/vocab width mismatch.** `len(tokenizer)` 248077 against a
  248320-wide unembedding: ~243 ids have no tokenizer string. Rank metrics
  must state which width they rank over.
- **B5 — no Hugging Face token.** Downloads succeed unauthenticated; both
  artifacts are public and ungated. Rate-limit warnings only.
