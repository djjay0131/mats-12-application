# Environment Manifest — J-Lens Design-Verification Sprint

Status: **Setup complete (local + ARC). No counted work performed.**
Date: 2026-08-26
Issue: #3 · Branch: `exp/jlens-design-verification` · Governance level: **L1**
Authoritative spec: `llm/construction/jlens-design-verification-sprint.md`

> **All measurements in this file are `agent-unverified`.** No number here has been
> independently re-derived by a human. Nothing in this file is a research result;
> it records environment facts, pinned identifiers, and blockers only.

## 0. Time accounting

| Window | Activity | Counted? |
|---|---|---|
| Setup | Install, download, ARC connectivity, GPU smoke test, environment build, queue time, passive waiting | ❌ **not counted** |
| V1 / V2 / V3 | Project-specific verification work | ✅ 1 counted hour each (conservative) |

**Counted time consumed so far: 0.0 h.** `llm/memory_bank/time-log.md` is
deliberately **not** updated — it records only time Jason explicitly confirms.

## 1. Topology

| Role | Machine |
|---|---|
| **Control machine** | `agents4research` (Ubuntu, Linux 6.8.0-138) — orchestration, git, job submission. **No GPU** |
| **Execution** | Virginia Tech ARC **Falcon**, compute nodes via Slurm. All computation, package installation, model loading, and J-Lens execution happen here |

Login node is used **only** for lightweight diagnostics, file staging, and
`sbatch`, per ARC's Acceptable Use Policy.

## 2. ARC execution environment (required record)

| Field | Value |
|---|---|
| **Slurm account** | `agents4research` (untruncated; `sacctmgr`-discovered, confirmed by `SLURM_JOB_ACCOUNT`) |
| **Cluster** | `falcon` (login `falcon1.arc.vt.edu`, user `djjay`) |
| **Partition** | `l40s_normal_q` |
| **QoS available** | `fal_l40s_normal_base`, `_int`, `_long`, `_short`, `fal_l40s_preemptable_base` (also full a30/v100/t4 sets; **no partition restriction** on the association) |
| **Allocation** | 2,000,000 hrs, Active |
| **GPU type** | NVIDIA **L40S**, compute capability (8, 9) |
| **GPU memory** | 46068 MiB (`nvidia-smi`) / 47.7 GB (`torch`) |
| **Driver** | **595.71.05** |
| **CUDA (torch)** | **13.0** |
| **PyTorch** | **2.13.0+cu130**, `torch.cuda.is_available() == True` |
| **transformers** | 5.16.1 |
| **Python** | 3.12.3 via module `Python/3.12.3-GCCcore-13.3.0` |
| **Environment path** | `/scratch/djjay/mats12/venv` |
| **Cache path** | `/scratch/djjay/mats12/hf-cache` (`HF_HOME`) |
| **Vendor path** | `/scratch/djjay/mats12/vendor/jacobian-lens` |
| **Scratch capacity** | `/scratch` 910T total, 721T available |
| **Disk used** | 15G under `/scratch/djjay/mats12` |

Model weights and HF caches are on **`/scratch`**, never the ARC home directory.

### Job record

| Job ID | Purpose | Queue time | Runtime | State | Node |
|---|---|---|---|---|---|
| **550057** | GPU smoke test | short | 00:00:01 | COMPLETED (0:0) | fal033 |
| **550077** | Environment build (1st attempt) | ~23 min | 00:00:02 | **FAILED (1:0)** | fal043 |
| **550088** | Environment build (2nd attempt) | **22 m 55 s** | **06 m 28 s** | COMPLETED (0:0) | fal045 |

Job 550088 TRES: `cpu=8, gres/gpu=1, mem=64G, node=1, billing=91`.
Submit `15:25:44` → Start `15:48:39` → End `15:55:07` (ARC local).

**550077 failure, recorded rather than hidden:** `module purge` dropped the
`apps` / `DefaultModules` paths that provide ARC's EasyBuild tree, so
`Python/3.12.3-GCCcore-13.3.0` was unknown on the compute node although it
resolves on the login node. Fixed by using `module reset`, a fallback list of
Python modules, and an explicit `sys.version_info >= (3,10)` assertion. Cost:
one queue wait, no downloads.

**Compute-node network:** verified reachable — `pypi=200`, `hf=200`, `gh=200`.
Package installation and model staging therefore run on the compute node as
required, not on the login node.

## 3. Reference implementation — pinned

| Item | Value |
|---|---|
| Repository | `anthropics/jacobian-lens` |
| **Pinned commit** | **`581d398613e5602a5af361e1c34d3a92ea82ba8e`** ("Initial release", 2026-07-02) |
| License | Apache-2.0 |
| Reference test suite | **32 passed** on ARC (and 32 passed locally) |

Companion code to *Verbalizable Representations Form a Global Workspace in
Language Models*. Repo is explicitly *"not maintained and not accepting
contributions."*

### API facts relevant to the gates
- `JacobianLens.apply(..., use_jacobian=False)` yields the **vanilla logit lens
  through the identical extraction path** — satisfies the V1 baseline requirement
  and the design's Control 1.
- `JacobianLens.transport(h, layer)` exposes the bare `J_l @ h`.
- `lens.apply()` runs **one forward pass per call**, so a J-lens plus logit-lens
  readout costs two forwards unless extraction is refactored.

## 4. Model and lens — exact identifier match (verified on ARC GPU)

| Item | Value |
|---|---|
| **Primary model** | `Qwen/Qwen3.5-4B` |
| Model revision (pinned) | `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a` |
| Repo architecture | `Qwen3_5ForConditionalGeneration` (multimodal) |
| Resolved class | `Qwen3_5ForCausalLM` (text tower) |
| Layers / d_model / vocab | **32 / 2560 / 248320** |
| Tokenizer | `Qwen2Tokenizer`, `vocab_size=248044`, `len(tok)=248077` |
| dtype | `torch.bfloat16` |
| **Lens repo** | `neuronpedia/jacobian-lens` |
| Lens revision | `qwen-n1000` → commit `16a01f309fcec900fdcec3f4cd5b64f3d00e4d5a` |
| **Lens file** | `qwen3.5-4b/jlens/Salesforce-wikitext/Qwen3.5-4B_jacobian_lens_n1000.pt` |
| Lens sha256 | `1f9a8f8fd593f0ffec1a9640993257ca4560f8ae3e5602315643d5cc6818534e` |
| Lens bytes | 406,332,644 |
| Lens `d_model` / `n_prompts` | **2560 / 1000** |
| Lens `source_layers` | `0..30` (31 layers); model layer 31 is the output row |

### Assertions executed on the GPU (`COMPAT_ASSERTIONS: PASS`, `LAYOUT_ASSERTIONS: PASS`)
1. `config.yaml → hf_model_name == "Qwen/Qwen3.5-4B"` — the lens was fit against
   **this exact model ID**, not a sibling.
2. `lens.d_model == model.hidden_size` (2560 == 2560).
3. `max(lens.source_layers) < num_hidden_layers` (30 < 32).
4. `jlens.from_hf` resolves the layout: `HFLensModel(Qwen3_5ForCausalLM,
   n_layers=32, d_model=2560)`, matching the lens on both axes.
5. Model loads to GPU: `model_load_secs 13.6`, `peak_gpu_alloc 8.51 GB` of 47.7 GB.

### Lens provenance
Fit by Neuronpedia (`fit_lens.py Qwen/Qwen3.5-4B`) on `Salesforce/wikitext`
(`wikitext-103-raw-v1`, train), `max_seq_len=128`, `dim_batch=64`,
`dtype=bfloat16`, on an NVIDIA B200.

**Resolved ambiguity:** the directory holds two lenses but one `config.yaml`
(reporting `prompts_fitted: 417`). The loaded `_n1000.pt` reports
`n_prompts=1000`, so that `config.yaml` describes the *other* file
(`Qwen3.5-4B_jacobian_lens.pt`). The n1000 lens — the one the official
`walkthrough.ipynb` selects — is the genuine 1000-prompt fit.

### Model-allowlist compliance
`Qwen/Qwen3.5-4B` is **not** GPT-2, Pythia, Gemma 2, Qwen2.5, or Llama 3. It is a
current-generation Qwen3.5 model and the substrate the official
`walkthrough.ipynb` itself uses. Satisfies the sprint's candidate priority #1.

## 5. `/common/data/models` check — no reusable copy

Checked before downloading, as required.

- **`unsloth--Qwen3.5-4B-GGUF--BF16` exists but is NOT usable.** Contents verified,
  not assumed: only `Qwen3.5-4B-BF16.gguf` (8.4 GB) and `mmproj-BF16.gguf`.
  **GGUF is a llama.cpp serialization; the official J-Lens is a PyTorch/HF
  implementation** that hooks residual streams via `transformers` modules and
  decodes with the model's own unembedding. No lens checkpoint corresponds to a
  GGUF quantization, and the tokenizer/architecture/revision cannot be
  established to match. It is therefore **rejected as incompatible**, not merely
  inconvenient. Same reasoning applies to `unsloth--Qwen3.5-9B-GGUF--BF16`.
- **No safetensors Qwen3.5-4B exists on ARC.** The model was staged from the Hub
  at its pinned revision into `/scratch`.
- **`Qwen--Qwen3.5-27B` (safetensors) exists** and a `Qwen3.5-27B` lens exists,
  but ~27B in bf16 is ≈54 GB against 47.7 GB of L40S memory — it does not fit the
  single-GPU scope. Not used.

## 6. Other lenses in the same repo (context)

The repo hosts 40+ lenses, all fit on `Salesforce/wikitext`. Also present:
`qwen3.5-9b-pt` (fit against `Qwen/Qwen3.5-9B-Base`), `qwen3.6-27b` (with an
n1000 lens), and `olmo-3-1025-7b`. **Prohibited as primary but present**:
`gpt2-small`, `pythia-70m-deduped`, `gemma-2-*`, `qwen2.5-7b-it`, `llama3.1-8b`,
`llama3.3-70b-it` — appendix/contrast use only, never primary.

## 7. Official positive control for V1 — located

`data/evaluations/lens-eval-multihop.json` (Apache-2.0, authored by Anthropic) is
a purpose-built lens-quality eval and is the correct V1 positive control:

- `items[*]` provide `prompt`, `target`, and **`intermediates`** — the unspoken
  concept that should surface in the readout.
- Documented readout position: **the single token immediately preceding `target`**.
- Documented metric: `pass@k` = mean fraction of `intermediates` whose
  **min-over-layers** lens rank ≤ k.
- `target` defines the readout position only and **is not itself scored**.

Example item: `{"name": "spider-legs", "prompt": "Fact: The number of legs on the
animal that spins webs is ", "target": "8", "intermediates": ["spider"]}`.

`jlens.examples.EXAMPLES` additionally ships a `multihop` slice example, plus five
other evaluation distributions (`association`, `multilingual`, `order-ops`,
`poetry`, `typo`).

This is **stronger** than the sprint minimum: it supplies an official metric and
an official scoring position rather than requiring a subjective read of a token
list.

## 8. Feasibility (`agent-unverified`)

On ARC L40S: model load 13.6 s, peak GPU allocation 8.51 GB of 47.7 GB. Ample
headroom for the V1 PASS criterion ("at least 20 paired examples plus controls")
and for V2 interventions.

For contrast, the control machine (CPU-only, 2 cores, bf16) measured ~18.9 s per
forward pass at 21 tokens with 9.23 GB peak RSS — usable as a fallback for a
single positive control, but not for the sprint. **ARC is the execution target.**

### Contingency only — bounded fitting pilot (not required, not run)
A pre-fitted lens exists, so no fit is needed. If V1 were to invalidate the
pairing, the bounded pilot would be `jlens.fit(model, prompts=wikitext[:4],
dim_batch=32, max_seq_len=128)`, timed and extrapolated to the ~100-prompt
minimum the README calls usable, reported as a cost estimate. Per the spec, a
usable lens requiring an open-ended fitting project is a **V1 FAIL**, not a
rescue path.

## 9. Unresolved blockers

### B1 — No local GPU. **RESOLVED for the sprint.**
The control machine has no CUDA device, but ARC Falcon L40S access is verified
end to end (SSH → account → QoS → scheduling → GPU → torch CUDA → model on GPU).
Execution moves to ARC. Residual risk is only queue latency, which is setup time.

### B2 — No sparse non-negative J-space reconstruction in the reference code. **OPEN. Load-bearing for V2.**
V2 requires *"the paper's sparse non-negative J-space reconstruction."* A search
of the pinned commit finds **no** sparse coding, NNLS, non-negative solver,
dictionary, or reconstruction routine — the shipped API is
`fit`/`apply`/`transport`/visualisation only. V2 would have to implement the
decomposition from the paper, which is the kind of open-ended work the sprint
forbids, and it invites V2's own FAIL condition: *"'J-space' is implemented as an
arbitrary top-token projection with no correspondence to the paper's sparse
construction."* **This remains the single most likely cause of a NO-GO.**

### B3 — No published shuffled-corpus / control lens exists. **OPEN, workaround available.**
All 40+ lenses in `neuronpedia/jacobian-lens` are fit on `Salesforce/wikitext`;
none is a shuffled-corpus or control lens. V1's negative-control requirement
resolves to the **third option only**: label-permutation plus norm-matched random
directions, implemented locally. Defensible, and matches design Controls 6 and 7,
but the stronger published control the design hoped for is **not available**.

### B4 — Tokenizer/vocab width mismatch. **OPEN, minor, must be handled in scoring.**
`len(tokenizer) = 248077` but the unembedding is `248320` wide. Ranks over the
full logit vector include ~243 ids with no tokenizer string. V1/V3 rank metrics
must state which width they rank over.

### B5 — No Hugging Face token. **OPEN, non-blocking.**
Downloads succeeded unauthenticated (rate-limit warning only); both artifacts are
public and ungated.

### B6 — ARC L40S queue latency. **OPEN, setup-time only.**
Observed queue waits of ~23 minutes with 17 of 20 L40S nodes in `mix-` (draining)
state. Not counted time, but it lengthens the wall-clock of each gate. The
association has no partition restriction, so `a30_normal_q` is an available
fallback if L40S congests.

## 10. Artifact locations

| Artifact | Path |
|---|---|
| Raw machine-readable outputs | `results/design-verification/raw/v{1,2,3}-*.json` |
| Verification reports | `results/design-verification/v{1,2,3}-*.md` |
| This manifest | `results/design-verification/environment-manifest.md` |
| Scripts and unit tests | `experiments/design-verification/` |
| Dev binding pairs (V3) | `experiments/design-verification/dev-binding-pairs.jsonl` |
| Decision record (V3) | `llm/plan/jlens-design-verification-decision.md` |
| ARC job scripts / logs | `~/mats12-arc-smoke/` on ARC; transcripts staged back into `results/design-verification/raw/` |

`.gitignore` excludes `results/raw/**` and `*.pt`, but **not**
`results/design-verification/raw/**` — JSON raw outputs under this sprint's path
are tracked, as the spec requires. Model and lens weights live on ARC `/scratch`
and are never committed.

## 11. Setup checklist

| # | Requirement | Status |
|---|---|---|
| 1 | GPU / CUDA / PyTorch / Transformers / storage / HF access inspected | ✅ |
| 2 | Official implementation inspected and commit pinned | ✅ `581d3986…` |
| 3 | Pre-fitted lens for a current allowed model located | ✅ Qwen3.5-4B |
| 4 | Model / tokenizer / lens identifiers verified to match exactly | ✅ asserted on GPU |
| 5 | Pre-fitted lens preferred | ✅ |
| 6 | No full lens-fitting run started | ✅ none started |
| 7 | Bounded fitting pilot designed if needed | ✅ not needed; §8 |
| 8 | Raw-output and script locations identified | ✅ §10 |
| 9 | `environment-manifest.md` created | ✅ this file |
| 10 | Unresolved blockers recorded plainly | ✅ §9 (B1–B6) |
| 11 | ARC connectivity + GPU smoke test | ✅ job 550057 |
| 12 | ARC environment built on compute node | ✅ job 550088 |
| 13 | `/common/data/models` checked before download | ✅ §5 (GGUF rejected) |
| 14 | Caches on scratch, not home | ✅ `/scratch/djjay/mats12` |

**Environment is usable. The setup stop rule was not triggered.**

## 12. What has explicitly NOT been done

- No positive-control experiment (that is counted V1).
- **No J-Lens readout of any kind has been computed.**
- No lens fitting.
- No dataset construction, no probe, no intervention.
- `docs/adr/0002-project-selection.md` untouched; ADR-0004 remains **Proposed**.
- `llm/memory_bank/time-log.md` not updated.
- No existing job cancelled or deleted.
