# mats-12-application — Agent Instructions

## What this is

A 13-day sprint to produce a MATS 12.0 application for Neel Nanda's mech
interp stream. Hard deadline **2026-09-04 23:59 PT**. Read
`docs/plan/PLAN.md` first, then `llm/memory_bank/activeContext.md`.

## Before anything ships

```
node scripts/conformance-check.mjs --gate SELECT|EXECUTE|WRITEUP|SUBMIT
```

`docs/application/conformance-register.md` holds all 121 requirements from
Neel's doc with source quotes — **38 are individually disqualifying**. The
`conformance-audit` skill runs the checker, the 15-criterion rubric, and the
adversarial `neel-reviewer` agent, and emits GO/NO-GO. No gate advances with
an open blocker (ADR-0003).

Three ledgers are how the blockers stay closed, and they are not optional:
- `docs/application/claims-register.md` — every claim typed
  `existence-proof` vs `method-claim`. Cherry-picking is permitted **only**
  under an explicit existence-proof tag.
- `docs/application/controls-ledger.md` — the cheap control actually run,
  and its result.
- `docs/application/verification-ledger.md` — every headline number
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

## Models

Do **not** use GPT-2, Pythia, Gemma 2, and prefer not to use Qwen2.5 or
Llama-3 as the primary model — all read as "old" to this reviewer. Current
substrates: `allenai/Olmo-3-7B-Think` (best interp tractability, full
post-training lineage), `openai/gpt-oss-20b`, `Qwen/Qwen3.5-9B` (⚠️ hybrid
linear attention — residual-stream methods fine, attention-head analysis
not). See the literature scan for the verified table.

### Olmo 3 Think lineage — verified 2026-08-22
`allenai/Olmo-3-1025-7B` (base) → `allenai/Olmo-3-7B-Think-SFT` →
`allenai/Olmo-3-7B-Think-DPO` → `allenai/Olmo-3-7B-Think` (RLVR).
Intermediate checkpoints are **git branches**: 55 on Think
(`step_0025`…`step_1375`), 43 on Think-SFT (`step1000`…`step43000`).
`from_pretrained(..., revision="step_0700")`.

Three traps: (1) `Think-SFT` has a **different tokenizer and no chat
template** — verify `<think>` tokenizes identically at all four stages
before comparing anything; (2) branch naming differs between repos
(`step_0700` vs `step20000`) and the SFT card's own example 404s;
(3) `Think-DPO` duplicates weights as `.bin` — pass
`allow_patterns=["*.safetensors*","*.json","*.txt","*.jinja"]` or you pull
29 GB instead of 14.6. OlmoTrace is hosted-only on the 32B — do not make it
load-bearing.

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
