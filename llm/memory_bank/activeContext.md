# Active Context

Last updated: 2026-08-22

## Where we are

**Phase 0 — Select & De-risk.** Repo established, governance adopted
(ADR-0001), paper/proposal agents ported from `soa-agentic-se`.
Neel's application doc retrieved in full and distilled. Literature scan
complete. Five candidates scored.

**Clock: 0 / 20 counted hours.** Nothing counted yet — all work so far is
prep and setup, which the instructions explicitly exclude.

**Conformance regime live** (ADR-0003): 121 requirements extracted from
Neel's doc into `docs/application/conformance-register.md`, 38 of them
disqualifying; `scripts/conformance-check.mjs` asserts the automatable
subset per gate; `neel-reviewer` agent and `conformance-audit` skill handle
the judgement layer. `--gate SELECT` is currently green.

## Resolved since last update

**Olmo 3 Think lineage: GO.** All four stage endpoints are public
Apache-2.0 repos (~14.6 GB each, ~58 GB total). Better than hoped —
intermediate checkpoints exist as git branches: 55 RL steps on
`Olmo-3-7B-Think`, 43 SFT steps on `Think-SFT`. That converts the headline
figure from a 4-point bar chart into a continuous faithfulness curve across
RLVR. Dolci SFT/DPO/RL datasets all public, plus pre-computed completion
sets at the SFT and DPO checkpoints. **C2 is unblocked.**

## Immediate next actions

1. **Aug 23 — env setup on ARC** (uncounted): TransformerBridge, vLLM /
   nnsight, pull the four stage checkpoints, one-prompt smoke test.
2. **Aug 23 — verify `<think>`/`</think>` tokenize identically at all four
   stages.** `Think-SFT` ships a different tokenizer and no chat template.
   If they differ, every cross-stage comparison is confounded — this is now
   the top de-risk item.
3. **Aug 24 — 2h de-risk pilot, then Gate 1.** Run
   `conformance-check --gate SELECT`, write ADR-0002, move it to Accepted.
   The checker refuses `--gate EXECUTE` while ADR-0002 is Proposed.

## Open decisions

- **ADR-0002: which candidate.** Recommendation: C2 primary (Olmo 3
  post-training lineage — Neel names the model), C1 backup (eval-awareness
  contaminating faithfulness measurement — Neel names the question), C4
  fallback. C3 excluded on schedule risk.
- Whether to combine C1+C2. Tempting and original; doubles scope. Decide
  only at Gate 1, and only if the harness comes up fast.

## Live risks

- ⚠️ **`Think-SFT` tokenizer differs from the other three stages** and it
  ships no chat template (a `fix_tokens.py` repair script instead). Top
  de-risk item — check before any cross-stage comparison.
- ⚠️ Branch naming is inconsistent between repos; the SFT model card's own
  revision example 404s.
- ⚠️ `Think-DPO` duplicates weights as `.bin` — 29 GB on a naive download.
- ⚠️ OlmoTrace is hosted-only on the 32B; public infini-gram indexes stop
  at OLMo-2. Use the Dolci datasets for "which data caused it".
- ⚠️ Qwen3.5 hybrid linear attention breaks attention-head analysis
  (inferred from spec, unverified).
- ⚠️ Any LLM-judge step is the load-bearing weakness — BONAFIDE showed
  most faithfulness metrics perform near chance.
- Schedule: a pivot after Aug 29 is not survivable.
