# Progress

## 2026-08-22 — Repo established

- `mats-12-application` created; governance adopted from
  `agentic-governance` v0.2 (ADR-0001, convention-only enforcement).
- Paper/proposal agents ported from `soa-agentic-se`: `paper-agent`,
  `position-paper-agent`, `proposal-agent`, `latex-agent`, `review-agent`,
  `memory-agent`, `knowledge-steward`, `feature-architect`; plus the
  `constellize:*` skills and commands.
- Neel's application doc retrieved in full (125k chars) and distilled into
  `docs/application/`.
- Literature scan completed — `docs/research/literature-scan-2026-08-22.md`.
- Five candidates scored — `docs/plan/project-candidates.md`.
- Day-by-day plan to Sept 4 — `docs/plan/PLAN.md`.

**Correction captured:** the main write-up counts *inside* the 20 hours;
only the executive summary gets the separate +2h. Plan rebalanced to ~15h
experiments / ~4h write-up / ~1h slack.

**Counted hours: 0 / 20.**

## Next

Gate 1, Aug 24.

## 2026-08-22 (later) — Conformance regime + C2 unblocked

- Extracted **121 requirements** from Neel's doc into
  `docs/application/conformance-register.md` — 38 BLOCKER, 33 SCORED,
  21 MECHANIC, 29 ADVICE — each with source quote, verification method,
  automatable flag, and gate. Includes a resolution rule for the three
  places the doc contradicts itself.
- Built `scripts/conformance-check.mjs` — gated assertions
  (`--gate SELECT|EXECUTE|WRITEUP|SUBMIT`), exits non-zero on failure.
  `--gate SELECT` currently green.
- Added the three ledgers: claims register (claim typing), controls ledger
  (cheap control + result), verification ledger (independent re-derivation
  + the 60-second unaided-explanation test).
- Added the `neel-reviewer` agent (five adversarial passes, instructed to
  reject) and the `conformance-audit` skill (runs all three layers,
  emits GO/NO-GO).
- ADR-0003 records the regime.
- **Olmo 3 Think lineage verified GO.** Four public stage endpoints plus
  55 RL / 43 SFT intermediate checkpoints as git branches. C2 unblocked and
  upgraded — continuous curve rather than four points.

**Counted hours: 0 / 20.**
