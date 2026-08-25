# Environment Manifest — J-Lens Design-Verification Sprint

Status: **Setup complete. No counted work performed.**
Date: 2026-08-25
Issue: #3 · Branch: `exp/jlens-design-verification` · Governance level: **L1**
Authoritative spec: `construction/jlens-design-verification-sprint.md`

> **All measurements in this file are `agent-unverified`.** No number here has been
> independently re-derived by a human. Nothing in this file is a research result;
> it records environment facts, pinned identifiers, and blockers only.

## 0. Time accounting

| Window | Activity | Counted? |
|---|---|---|
| Setup | Install, download, hardware/dependency checks, passive waiting | ❌ **not counted** |
| V1 / V2 / V3 | Project-specific verification work | ✅ 1 counted hour each (conservative) |

Setup window opened `2026-08-25T18:06:23Z`. Bounded to 60 elapsed minutes.
**Counted time consumed so far: 0.0 h.** `llm/memory_bank/time-log.md` is
deliberately **not** updated — it records only time Jason explicitly confirms.

## 1. Hardware

| Item | Value |
|---|---|
| Host | `agents4research`, Linux 6.8.0-138-generic, x86_64 |
| CPU | **2 cores** |
| RAM | 31 GB total / ~28 GB available |
| **GPU** | **NONE.** `nvidia-smi` not found; `nvcc` not found |
| `torch.cuda.is_available()` | **`False`** |
| Disk | `/home` 96 GB free; `/` 79 GB free |

**This is a CPU-only, 2-core host.** See §7, Blocker B1.

## 2. Software stack

Bootstrapped into `/home/djjay/.venvs/jlens` (system Python had no `pip` and no
`ensurepip`; pip was installed via `get-pip.py`).

| Package | Version |
|---|---|
| Python | 3.12.3 |
| torch | **2.13.0+cpu** (CPU wheel, pinned) |
| transformers | 5.15.1 (spec requires ≥5.5 ✓) |
| huggingface_hub | 1.28.0 |
| tokenizers | 0.22.2 |
| numpy | 2.5.2 |
| safetensors | 0.8.0 |
| scikit-learn | 1.9.0 (for the V3 linear probe) |
| pytest | 9.1.1 |
| jlens | 0.1.0 (editable, from pinned commit below) |

## 3. Reference implementation — pinned

| Item | Value |
|---|---|
| Repository | `anthropics/jacobian-lens` |
| **Pinned commit** | **`581d398613e5602a5af361e1c34d3a92ea82ba8e`** |
| Commit date | 2026-07-02T09:07:51+00:00 ("Initial release") |
| License | Apache-2.0 |
| Local checkout | `<scratchpad>/vendor/jacobian-lens` |
| Reference test suite | **32 passed** (`pytest tests/ -q`) |

Repository status is *"Reference implementation. Not maintained and not accepting
contributions."* Companion code to *Verbalizable Representations Form a Global
Workspace in Language Models* (transformer-circuits.pub/2026/workspace).

### API facts relevant to the gates
- `JacobianLens.apply(..., use_jacobian=False)` yields the **vanilla logit lens
  through the identical extraction path** — satisfies the V1 baseline requirement
  and the design's Control 1.
- `JacobianLens.transport(h, layer)` exposes the bare `J_l @ h`.
- `lens.apply()` runs **one forward pass per call**, so J-lens and logit-lens
  readouts cost two forwards unless the extraction is refactored.

## 4. Model and lens — exact identifier match

Setup requirement #4 was to verify that model, tokenizer, and lens identifiers
match **exactly**. They do:

| Item | Value |
|---|---|
| **Primary model** | `Qwen/Qwen3.5-4B` |
| Model commit (SHA) | `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a` |
| Gated / private | No / No (Apache-style public) |
| Resolved class | `Qwen3_5ForCausalLM` (text tower; the repo config is multimodal `Qwen3_5ForConditionalGeneration`) |
| Layers / d_model | **32 / 2560** |
| Config vocab_size | 248320 |
| Tokenizer | `Qwen2Tokenizer`, `vocab_size=248044`, `len(tok)=248077` |
| dtype used | `torch.bfloat16` |
| **Lens repo** | `neuronpedia/jacobian-lens` |
| Lens revision | `qwen-n1000` |
| Lens commit (SHA) | `16a01f309fcec900fdcec3f4cd5b64f3d00e4d5a` |
| **Lens file** | `qwen3.5-4b/jlens/Salesforce-wikitext/Qwen3.5-4B_jacobian_lens_n1000.pt` |
| Lens sha256 | `1f9a8f8fd593f0ffec1a9640993257ca4560f8ae3e5602315643d5cc6818534e` |
| Lens size | 406,332,644 bytes |
| Lens `d_model` | **2560 — matches the model ✓** |
| Lens `n_prompts` | **1000** |
| Lens `source_layers` | `0..30` (31 layers); model layer 31 is the output row |
| Stored J dtype | fp16 on disk, loaded as fp32; each `J_l` is `[2560, 2560]` |

### Lens provenance (from the repo's own `config.yaml`)
The lens was fit by Neuronpedia with `fit_lens.py Qwen/Qwen3.5-4B`, i.e. **against
this exact model ID** — `hf_model_name: "Qwen/Qwen3.5-4B"`. Corpus
`Salesforce/wikitext` (`wikitext-103-raw-v1`, train), `max_seq_len=128`,
`dim_batch=64`, `dtype=bfloat16`, fit on an NVIDIA B200.

**Resolved ambiguity:** the directory holds *two* lenses but only one
`config.yaml` (which reports `prompts_fitted: 417`, early-stopped at
`stop_at_delta=0.002`). Loading the file confirms
`Qwen3.5-4B_jacobian_lens_n1000.pt` reports `n_prompts=1000`, so the `config.yaml`
describes the **other** file (`Qwen3.5-4B_jacobian_lens.pt`). The n1000 lens — the
one the official `walkthrough.ipynb` selects — is the genuine 1000-prompt fit.

### Model-allowlist compliance
`Qwen/Qwen3.5-4B` is **not** GPT-2, Pythia, Gemma 2, Qwen2.5, or Llama 3. It is a
current-generation Qwen3.5 model, and it is the substrate the official
`walkthrough.ipynb` itself uses. This satisfies the sprint's candidate priority #1
("Qwen3.5 model with a matching published lens").

### Pre-fitted lens: available — no fitting required
Setup requirements #3 and #5 (prefer a pre-fitted lens) are **satisfied**. No lens
fitting is required and none was started (requirement #6). The bounded
cost-estimation pilot (requirement #7) is therefore **not needed**; its
contingency design is recorded in §6 only in case V1 invalidates this pairing.

### Other lenses in the same repo (context)
The repo hosts 40+ lenses. Notable: `qwen3.5-9b-pt` (fit against
`Qwen/Qwen3.5-9B-Base`) also exists, and `olmo-3-1025-7b` exists. **Prohibited as
primary but present**: `gpt2-small`, `pythia-70m-deduped`, `gemma-2-*`,
`qwen2.5-7b-it`, `llama3.1-8b`, `llama3.3-70b-it`. These may only ever serve as
contrast/appendix material, never as the primary substrate.

## 5. Official positive control for V1 — located

`data/evaluations/lens-eval-multihop.json` (Apache-2.0, authored by Anthropic) is a
purpose-built lens-quality eval and is the correct V1 positive control:

- `items[*]` provide `prompt`, `target`, and **`intermediates`** — the unspoken
  concept that should surface in the readout.
- Documented readout position: **the single token immediately preceding `target`**.
- Documented metric: `pass@k` = mean fraction of `intermediates` whose
  **min-over-layers** lens rank ≤ k.
- `target` defines the readout position only and **is not itself scored**.

Example item: `{"name": "spider-legs", "prompt": "Fact: The number of legs on the
animal that spins webs is ", "target": "8", "intermediates": ["spider"]}`.

`jlens.examples.EXAMPLES` additionally ships a `multihop` slice example
(*"Fact: The capital of Japan is Tokyo.\nFact: The currency used in the country
shaped like a boot is"*), plus five other evaluation distributions
(`association`, `multilingual`, `order-ops`, `poetry`, `typo`).

This is a **stronger** positive control than the sprint minimum, because it
supplies an official metric and an official scoring position rather than requiring
a subjective read of a token list.

## 6. Feasibility measurements (`agent-unverified`)

Measured on neutral filler text (`"The quick brown fox…"`, 21 tokens) — **not** an
evaluation item. No J-Lens readout was computed; this is a hardware timing check.

| dtype | Load | Forward pass | Peak RSS | Verdict |
|---|---|---|---|---|
| `bfloat16` | 0.9 s (warm mmap) | **18.9 s** | **9.23 GB** | ✅ selected |
| `float32` | 34.8 s | 22.2 s | **25.62 GB** | ❌ rejected — 25.6/31 GB is too tight |

**Operating decision: bfloat16 on CPU, `torch.set_num_threads(2)`.**

Derived budget (order-of-magnitude, unverified): one full 31-layer readout at a
single position ≈ one forward (~19 s) plus ~31 unembed projections. J-lens plus
logit-lens for one prompt ≈ **two** forwards under the current API. A 20-pair
experiment (40 prompts × 2 methods) is therefore on the order of tens of minutes
per full sweep — feasible but slow, and it constrains how many layers, pairs, and
control arms V3 can afford.

### Contingency only — bounded fitting pilot (not required, not run)
If V1 invalidates the Qwen3.5-4B pairing, a fit is **not** attempted on this host:
`jlens.fit` is dominated by the model's own backward pass and the released lenses
were fit on a B200. The bounded pilot would instead be `jlens.fit(model,
prompts=wikitext[:4], dim_batch=32, max_seq_len=128)`, timed, and linearly
extrapolated to the ~100-prompt minimum the README calls usable — reported as a
cost estimate to Jason, with the sprint stopping there. Per the spec, a usable lens
that requires an open-ended fitting project is a **V1 FAIL**, not a rescue path.

## 7. Unresolved blockers

Recorded plainly, per setup requirement #10.

### B1 — No GPU; CPU-only, 2 cores. **Open, mitigated, not resolved.**
The environment has no CUDA device. The lens itself was fit on a B200. Mitigation:
Qwen3.5-4B in bf16 fits in RAM and runs at ~19 s/forward, so V1's positive control
is affordable. **Risk:** this materially constrains V2's intervention sweeps and
V3's probe work, and it makes any scale-up (the 40 held-out pairs in the 16-hour
design) impractical on this host. If the sprint returns GO, real compute must be
secured before the main experiment. No ARC/remote-compute access is configured on
this host (`~/.ssh` has no cluster entry).

### B2 — No sparse non-negative J-space reconstruction in the reference code. **Open. Load-bearing for V2.**
V2 requires *"the paper's sparse non-negative J-space reconstruction."* A search of
the pinned commit (`jlens/*.py`) finds **no** sparse coding, NNLS, non-negative
solver, dictionary, or reconstruction routine — the shipped API is
`fit` / `apply` / `transport` / visualisation only. V2 would therefore have to
**implement the decomposition from the paper**, which is exactly the kind of
open-ended work the sprint forbids, and it directly invites the V2 FAIL condition
*"'J-space' is implemented as an arbitrary top-token projection with no
correspondence to the paper's sparse construction."* This is the single most
likely cause of a NO-GO and should be treated as such when V2 is scoped.

### B3 — No published shuffled-corpus / control lens exists. **Open, workaround available.**
All 40+ lenses in `neuronpedia/jacobian-lens` are fit on `Salesforce/wikitext`;
none is a shuffled-corpus or control lens. The V1 requirement *"determine whether a
shuffled-corpus lens, published control lens, or defensible label/permutation
control can be run"* therefore resolves to the **third option only**: a
label-permutation control and norm-matched random directions, implemented locally.
That is defensible and matches design Controls 6 and 7, but the stronger negative
control the design hoped for ("if a published shuffled-corpus J-Lens checkpoint is
readily available") is **not available**.

### B4 — Tokenizer/vocab width mismatch. **Open, minor, must be handled in scoring.**
`len(tokenizer) = 248077` but the unembedding is `248320` wide (padded). Ranks
computed over the full logit vector include ~243 ids with no tokenizer string.
Rank-based metrics in V1/V3 must state whether they rank over the padded width or
the tokenizer width. Untracked, this is a small but real source of
non-reproducibility between implementations.

### B5 — No Hugging Face token configured. **Open, non-blocking.**
No `HF_TOKEN`. Downloads succeeded unauthenticated (rate-limit warning only); both
required artifacts are public and ungated. Only a risk if rate limits bite on a
re-download.

## 8. Artifact locations

Fixed now so raw output always precedes summaries (setup requirement #8):

| Artifact | Path |
|---|---|
| Raw machine-readable outputs | `results/design-verification/raw/v{1,2,3}-*.json` |
| Verification reports | `results/design-verification/v{1,2,3}-*.md` |
| This manifest | `results/design-verification/environment-manifest.md` |
| Scripts and unit tests | `experiments/design-verification/` |
| Dev binding pairs (V3) | `experiments/design-verification/dev-binding-pairs.jsonl` |
| Decision record (V3) | `docs/plan/jlens-design-verification-decision.md` |
| Human-verification handoff | `results/design-verification/human-verification-pending.md` |

`.gitignore` excludes `results/raw/**` and `*.pt`, but **not**
`results/design-verification/raw/**` — JSON raw outputs under this sprint's path
are tracked, as the spec requires. Model and lens weights stay in
`~/.cache/huggingface` and are never committed.

## 9. Setup checklist

| # | Requirement | Status |
|---|---|---|
| 1 | GPU / CUDA / PyTorch / Transformers / storage / HF access inspected | ✅ (GPU absent — B1) |
| 2 | Official implementation inspected and commit pinned | ✅ `581d3986…` |
| 3 | Pre-fitted lens for a current allowed model located | ✅ Qwen3.5-4B |
| 4 | Model / tokenizer / lens identifiers verified to match exactly | ✅ §4 |
| 5 | Pre-fitted lens preferred | ✅ |
| 6 | No full lens-fitting run started | ✅ none started |
| 7 | Bounded fitting pilot designed if needed | ✅ not needed; contingency in §6 |
| 8 | Raw-output and script locations identified | ✅ §8 |
| 9 | `environment-manifest.md` created | ✅ this file |
| 10 | Unresolved blockers recorded plainly | ✅ §7 (B1–B5) |

**Environment is usable. The setup stop rule was not triggered.**

## 10. What has explicitly NOT been done

- No positive-control experiment (that is counted V1).
- No J-Lens readout of any kind has been computed.
- No lens fitting.
- No dataset construction, no probe, no intervention.
- `docs/adr/0002-project-selection.md` untouched; ADR-0004 remains **Proposed**.
- `llm/memory_bank/time-log.md` not updated.
