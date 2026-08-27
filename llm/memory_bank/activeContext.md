# Active Context

Last updated: 2026-08-26

## Where we are

**Project selected and locked: the J-Lens relational-binding experiment**
(ADR-0005, Accepted; supersedes ADR-0002, resolves ADR-0004).

> When two prompts contain the same entities and concepts but assign them
> different relational roles, does J-Lens identify the correct hidden
> intermediate — and does changing that representation causally change the
> model's answer?

**Scope: passive-primary.** H1/H2/H4 are the deliverable. The causal arm (H3)
is contingent on V2 clearing blocker B2 — the reference implementation ships
no sparse non-negative J-space reconstruction. Do not approximate it with a
top-token projection; that is the design's own FAIL condition.

**Clock: 0.0 / 20 counted hours.** ADR-0005 §3 rules that everything through
2026-08-26 is ideation and setup, and that no reset is needed because
ADR-0002 was never executed against. V1/V2/V3 count one hour each.

**9 days to the deadline** (Fri 2026-09-04, 23:59 PT).

## Substrate — verified, not assumed

ARC job 550088, `falcon1`, NVIDIA L40S. `Qwen/Qwen3.5-4B` +
`neuronpedia/jacobian-lens` rev `qwen-n1000` (commit `16a01f3`).
`COMPAT_ASSERTIONS: PASS`, `LAYOUT_ASSERTIONS: PASS`, 32/32 reference tests,
model load 13.6 s, peak GPU 8.51 GB of 47.7 GB. Details:
`results/design-verification/environment-manifest.md`.

## Immediate next actions

1. **V1 (1 counted hour).** Reproduce an official J-Lens example and
   **exercise the logit-lens switch** — that is the one part of ADR-0004
   condition 1 setup did not close.
2. **V2 (1 counted hour).** Settle B2. Either a faithful J-space
   reconstruction is reproducible inside the hour, or causal work is declared
   unavailable and Hours 12–13 reallocate to passive controls. Do not let
   this run long.
3. **V3 (1 counted hour).** Binding-identifiability audit on 8–12 development
   pairs — does the metric test binding, or only whether the model already
   picked the right intermediate?

## Reporting is wired

- Author in `writeup/exec-summary.md` and `writeup/main.md`; build with
  `./scripts/build-report.sh [--pdf]` → `writeup/mats12-report.docx`.
- Figures go through `src/figstyle.py::save_figure`, which registers each one
  in `results/figures/FIGURE-REGISTRY.md` with a claim id, n, seed, sha and
  commit. **A figure with no claim id has no reason to be in the report.**
- Three placeholder figures exist, watermarked "NOT A RESULT". Replace them
  as real results land; the registry Notes column flags them.

## Live risks

- ⚠️ **B2** — no sparse non-negative J-space reconstruction in the reference
  code. Scoped by ADR-0005, settled at V2.
- ⚠️ **B3** — no published shuffled-corpus control lens. Negative control
  falls back to label permutation + norm-matched random directions.
- ⚠️ **B4** — `len(tokenizer)=248077` vs a 248320-wide unembedding. Rank
  metrics must state which width they rank over.
- ⚠️ **Crowding** — J-Lens was promoted with a bolded "Key resource" link.
  The relational-binding framing has to carry the differentiation, and it
  must be obvious in the first paragraph.
- Queue latency ~23 min on L40S (17/20 nodes draining); `a30_normal_q` is an
  unrestricted fallback. Setup time, not counted.

## Open

- The three ledgers still contain their example rows. Delete them before the
  first real entry — `conformance-audit` flags rows containing "example".
