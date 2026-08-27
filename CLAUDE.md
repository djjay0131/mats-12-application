# mats-12-application — Agent Instructions

## The project

**J-Lens relational binding** — ADR-0005. When two prompts contain the same
entities but swap their relational roles, does J-Lens identify the correct
hidden intermediate? Design of record:
`llm/plan/jlens-relational-binding-experiment-design.md`.

**Scope is passive-primary.** H1/H2/H4 are the deliverable. The causal arm
(H3) is contingent on V2 clearing blocker B2 — the reference implementation
ships no sparse non-negative J-space reconstruction. Do not approximate it
with a top-token projection; that is the design's own FAIL condition.

**Substrate:** `Qwen/Qwen3.5-4B` + `neuronpedia/jacobian-lens` rev
`qwen-n1000`, verified on ARC L40S (8.51 GB peak). Do not fit a lens.

## What this is

A sprint to produce a MATS 12.0 application for Neel Nanda's mech interp
stream. Hard deadline **2026-09-04 23:59 PT**. Read
`llm/plan/PLAN.md` first, then `llm/memory_bank/activeContext.md`.

## Before anything ships

```
node scripts/conformance-check.mjs --gate SELECT|EXECUTE|WRITEUP|SUBMIT
```

`llm/application/conformance-register.md` holds all 121 requirements from
Neel's doc with source quotes — **38 are individually disqualifying**. The
`conformance-audit` skill runs the checker, the 15-criterion rubric, and the
adversarial `neel-reviewer` agent, and emits GO/NO-GO. No gate advances with
an open blocker (ADR-0003).

Three ledgers are how the blockers stay closed, and they are not optional:
- `llm/application/claims-register.md` — every claim typed
  `existence-proof` vs `method-claim`. Cherry-picking is permitted **only**
  under an explicit existence-proof tag.
- `llm/application/controls-ledger.md` — the cheap control actually run,
  and its result.
- `llm/application/verification-ledger.md` — every headline number
  re-derived by a human, via a path that does **not** share the original
  pipeline's code. Re-running the same script is not verification.

## Non-negotiables

1. **The 20-hour clock.** Experiments + analysis + planning + main write-up
   all count. Only the executive summary gets a separate +2h. Setup,
   general reading, breaks, and waiting on training do not count. If you
   are about to start counted work, say so.
2. **Never present agent output as a verified result.** Anything destined
   for the write-up must be re-derived by Jason. Flag unverified numbers
   with `agent-unverified` explicitly.
3. **Never report a metric without its control.** Random vector, random
   hint, "just ask the model", linear probe.
4. **Never report a single faithfulness number.** Two metrics minimum.
5. **Look at the raw data.** Before aggregating, print examples. Randomly
   selected, never cherry-picked.
6. **Simple before fancy.** Prompting and reading the CoT beat SAEs unless
   SAEs demonstrably win.
7. **Do not write the executive summary or form answers.** Neel explicitly
   penalizes LLM-voiced applications: *"Answers that read like they were
   written by an LLM are a significant negative signal - I see hundreds of
   them, and they blur together."* Draft structure and figures; Jason writes
   the prose.
8. **Type every claim before defending it.** `existence-proof` (cherry-pick
   allowed, must say so) or `method-claim` (random sample, recorded seed,
   baseline required).
9. **Check replication first.** Never build on a phenomenon without
   confirming it exists in this model, these prompts, this dataset.

## Context to load first (ADV-11)

Neel recommends putting his compiled 600k-token mech-interp context file in
the agent's context window:

> "**Context is crucial**: LLMs are much more useful when they have the
> relevant information in the context window... By default, just **put this
> 600k token file** in the context window."

It lives at **`context/default_600k.md`** (gitignored — 637 KB, not ours to
redistribute). If it is missing, get it from the Drive folder linked in
`llm/application/mats12-instructions-raw.txt` before starting work.

Also load, in this order: `llm/plan/PLAN.md`,
`docs/adr/0005-accept-jlens-relational-binding.md`,
`llm/plan/jlens-relational-binding-experiment-design.md`,
`results/design-verification/environment-manifest.md`.

## Persistent kernel discipline (ADV-17 / ADV-18)

Exploratory interp work wants a **persistent Python process** — load the
model once, keep weights and activations in memory while iterating. Cold-start
scripts that reload a 4B model every call waste the budget.

This project uses the tmux + IPython pattern (Neel's "simple and unbreakable"
option). Session name: **`mats-12-application`**.

- Send code with `tmux send-keys`, read results with `tmux capture-pane`.
- **Load models and data in dedicated cells at the top.**
- **Never restart the kernel without asking.**
- **Always save plots to disk as PNGs** as well as displaying them — you can
  read PNGs natively, and they belong in `results/figures/` via
  `src/figstyle.py::save_figure` anyway.
- **Checkpoint expensive artifacts to disk** — activations, datasets, any
  fitted object — so a crashed kernel is an annoyance, not a lost hour.
- Run anything long as a background script with a log, not a kernel cell.
- Prefer plain `.py` over `.ipynb`.

## Layout

PM and research material under `llm/`; execution and outputs at the root.
`docs/` holds only ADRs and the governance delta. See
`docs/governance-delta.md` §Repository Layout.

## Models

Subject model: **`Qwen/Qwen3.5-4B`** with **`neuronpedia/jacobian-lens`**
rev `qwen-n1000` (commit `16a01f3`), verified compatible on ARC L40S —
`d_model` 2560 matching on both axes, `max(source_layers)=30 < 32`, peak GPU
8.51 GB. **Do not fit a lens**; use the pre-fitted public checkpoint.

Do **not** use GPT-2, Pythia, or Gemma 2 — all read as old to this reviewer.
Neel names the Qwen 3.5/3.6 dense family (4B, 9B, 27B) as good defaults, and
`deepseek-v4-flash-0731` for a highly capable model with J-Lenses published.

⚠️ Known issue **B4**: `len(tokenizer)=248077` against a 248320-wide
unembedding — ~243 ids have no tokenizer string. Rank metrics must state
which width they rank over.

The Olmo 3 post-training lineage belonged to candidate C2, superseded by
ADR-0005. Its verified details are preserved in
`llm/plan/project-candidates.md` should the fallback ever be needed.

## Tooling

- TransformerLens: use `TransformerBridge`, **not** the deprecated
  `HookedTransformer`.
- SAELens: now `decoderesearch/SAELens`, v6 refactor.
- nnsight 0.6 / NDIF; nnsight × vLLM for scale. Note inference mode blocks
  gradients — no probe training through it.
- Do not use transformer-debugger (dead).

## Agents available

`paper-agent`, `position-paper-agent`, `proposal-agent`, `latex-agent`,
`review-agent`, `memory-agent`, `knowledge-steward`, `feature-architect`,
plus the governance executives (`chief-architect`, `chief-reviewer`,
`chief-product-officer`, `repository-steward`).

Skills: `constellize:*` for memory and feature workflows,
`governance-establish` / `governance-audit`.

## Governance

`docs/governance-delta.md`, pinned to agentic-governance v0.2. Issue →
branch → PR with a governance-level declaration → review → merge. Steward
merge authority INACTIVE.
