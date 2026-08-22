# ADR-0003: Treat Neel's instructions as a machine-checkable requirements register

Status: Accepted
Date: 2026-08-22
Deciders: Jason

## Context

The application document is 125,654 characters and states, scattered
across nine sections and two "common mistakes" lists, a large number of
things that are **individually disqualifying**. Several are easy to violate
without noticing: a results table with no baseline column, a qualitative
example that was cherry-picked without saying so, a number in the write-up
that no human re-derived, an executive summary that drifts into LLM cadence.

Reading the document once and intending to comply is not a control. Under
a 13-day clock with a 20-hour budget, the failure mode is not
disagreement — it is forgetting, at hour 19, on a Wednesday.

Meanwhile the criteria that actually earn score — clarity, taste,
skepticism, prioritisation — cannot be checked mechanically at all, and
human review time is scarce. Spending it on things a script could catch is
waste.

## Decision

Treat the instructions as a requirements specification and govern against
it in three layers.

**Layer 1 — the register.** `docs/application/conformance-register.md`
extracts all 121 requirements verbatim, each with a source quote, a class
(BLOCKER / SCORED / MECHANIC / ADVICE), a verification method, an
automatable flag, and the gate at which it must clear. 38 are blockers.
The register is the source of truth; when this repo and the register
disagree, the register wins.

**Layer 2 — the checker.** `scripts/conformance-check.mjs` asserts every
requirement that can be asserted, gated by phase
(`--gate SELECT|EXECUTE|WRITEUP|SUBMIT`), and exits non-zero on failure. It
checks banned models, dead research areas, exec-summary word count and
figure presence, LLM-voice stylometry, baseline columns in every results
table, claim typing, numeric traceability to `results/canonical.json`, the
verification ledger, replication-before-building, limitations sections,
narrative-vs-chronological structure, and the hour budget.

**Layer 3 — judgement.** `docs/application/selection-rubric.md` (15 scored
criteria, 28+/30 to submit) and the `neel-reviewer` agent, which reviews
adversarially in five passes and is instructed to reject. The
`conformance-audit` skill runs all three layers and emits a GO/NO-GO.

Three ledgers make Layer 2 possible and are themselves the discipline:
`claims-register.md` (every claim typed existence-proof vs method-claim),
`controls-ledger.md` (the cheap control actually run, and its result), and
`verification-ledger.md` (every headline number independently re-derived,
by a path not sharing the original pipeline's code).

**No gate advances with an open blocker.** An accepted risk requires an
ADR, not a shrug.

## Consequences

**Positive.** The mechanical failures become impossible rather than
unlikely, which is the only reliable state at hour 19. Human review time
goes entirely to taste and clarity. The ledgers double as the write-up's
own evidence section — the controls ledger *is* the baselines paragraph,
and the verification ledger *is* the answer to "did you check this?".
Building the register also surfaced the tensions in the doc (depth vs
breadth, cherry-picking permitted for existence proofs but not general
claims) and forced an explicit resolution rule for each.

**Negative.** The register and checker cost time that is not counted
against the 20 hours but is still real elapsed time on a 13-day clock.
The checker's stylometry and baseline-column heuristics will produce false
positives; they are advisory signals routed to a human, not verdicts. And
there is a live risk of the ledgers becoming theatre — rows marked
"verified" that were not. The 60-second unaided-explanation test in the
verification ledger exists specifically to make that harder to fake to
yourself.

**Explicit non-goal.** The checker does not and cannot judge whether the
project is interesting. Nothing here substitutes for the taste pass.

## Alternatives considered

- **A single markdown checklist.** Rejected: 121 items, read once at the
  end, when the cost of a finding is highest and there is no time to act.
- **Rely on the agent to remember the constraints.** Rejected on the
  grounds Neel himself gives — unverified agent work is the disqualifying
  failure, so the agent cannot be the control on itself.
