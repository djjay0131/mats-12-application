# Governance Delta: mats-12-application

Status: Active
Last updated: 2026-08-22
Governance: agentic-governance v0.2

This file localizes the canonical governance in
[`agentic-governance`](https://github.com/djjay0131/agentic-governance) for
this project. This file declares project facts, never policy; changing it
is semantic (L1) and it is permanently deny-listed from the L0 fast track.

## Mission

Produce a MATS 12.0 application for Neel Nanda's stream: a ~20-hour AI
safety research project plus a write-up and executive summary, due
2026-09-04. This repo holds the plan, the source material, the experiment
code, the results, and the write-up drafts. It is **not** a long-lived
research codebase — it is a 13-day sprint with a hard external deadline,
and governance here exists to keep the sprint honest, not to slow it down.

Explicitly out of scope: publishing a paper, building reusable
infrastructure, anything that does not land in the Sept 4 submission.

## Design-Authority Document

`docs/plan/PLAN.md` — the phased plan, time budget, and gates. Candidate
selection is authorized by `docs/adr/0002-project-selection.md` once
written.

## Project Principles

1. **The 20-hour clock is a contract.** Counted time is logged. If the
   clock resets (a genuine pivot), the reset is recorded in an ADR.
2. **Every number in the write-up is re-derived by a human.** Agent output
   is a draft, never evidence. Unverified agent results are disqualifying
   per the application instructions.
3. **No claim without a baseline.** Random control, "just ask the model",
   or a linear probe — whichever is cheapest and honest.
4. **Never one metric.** Faithfulness metrics are known to perform near
   chance; report at least two and their disagreement.
5. **Look at the raw data before believing the aggregate.**
6. **Randomly selected examples, never cherry-picked.**
7. **Negative results ship.** Overclaiming does not.
8. **Simple before fancy.** Prompting and reading the CoT first; complexity
   must earn its place.

## Domain Review Questions

Added to the canonical review checklist's Alignment Review section.

- Does this change consume counted hours, and is the log updated?
- Does every reported number have a control or baseline alongside it, and
  is that control in `docs/application/controls-ledger.md` with its result?
- Is every claim typed `existence-proof` or `method-claim` in
  `docs/application/claims-register.md`? An untagged cherry-pick carrying a
  general claim is the red flag he names by name.
- Has a human **independently re-derived** every number this change adds,
  by a path that does not share the original pipeline's code, and recorded
  it in `docs/application/verification-ledger.md`?
- Has a human read raw examples supporting this claim, selected randomly
  with a recorded seed?
- Is any LLM-judge step validated against hand labels?
- Does the write-up state the limitation as plainly as the finding?
- Would this survive the question "how could this result be false?"
- Does `node scripts/conformance-check.mjs --gate <current gate>` pass?

## Memory Bank

Path: `llm/memory_bank/`

## Roadmap

Path: `docs/plan/PLAN.md`

## Governance Check Command

Two commands, both required:

```
node ~/code/agentic-governance/governance/scripts/governance-checks.mjs
node scripts/conformance-check.mjs --gate <SELECT|EXECUTE|WRITEUP|SUBMIT>
```

The first is the canonical portfolio check. The second is project-specific
and asserts the mechanically-checkable subset of the 121 requirements in
`docs/application/conformance-register.md` — the register extracted verbatim
from Neel's application doc, of which 38 are individually disqualifying.
Rationale: ADR-0003. No gate advances with an open blocker; an accepted risk
requires an ADR, not a shrug.

## L0 Path Allowlist

```l0-allowlist
allow llm/memory_bank/** path-only
allow docs/adr/README.md index-table-rows
allow docs/adr/[0-9][0-9][0-9][0-9]-*.md status-line-only
allow docs/plan/PLAN.md checkbox-only
allow docs/** link-target-only
deny src/**
deny scripts/**
deny .github/**
deny docs/adr/0000-template.md
deny docs/governance-delta.md
deny writeup/**
deny results/**
deny scripts/conformance-check.mjs
deny docs/application/**
```

## Platform Enforcement Reality

- Branch protection on `main`: **not yet configured** — no GitHub remote
  exists at time of establishment. To be recorded honestly once the remote
  is created.
- Required status checks: unavailable (no remote).
- Token/identity model: single owner (`djjay0131`); all agent sessions
  authenticate as the owner. Steward/auditor/architect are procedural
  roles, not distinct identities.
- Hardening path: create the remote, then apply
  `agentic-governance/docs/branch-protection.md`. Blocked only on the
  remote existing. **Given the 13-day deadline, convention-only enforcement
  is accepted deliberately for this repo** — the cost of a blocked merge
  during the sprint exceeds the benefit.

## Steward Activation Status

Status: INACTIVE

No activation ADR, no activation PR. Not expected to change during this
project.

## Milestone Labels

- `phase-0-select` — candidate scoping and de-risking (to Aug 24)
- `phase-1-execute` — counted experiment hours (Aug 25 – Aug 31)
- `phase-2-writeup` — main write-up (Sep 1 – Sep 2)
- `phase-3-submit` — executive summary and submission (Sep 3 – Sep 4)

## Special Labels

- `counted-time` — PR consumes hours against the 20-hour budget
- `needs-baseline` — a claim is present without its control
- `agent-unverified` — contains agent output a human has not re-derived
- `blocker-open` — an open BLK-* requirement from the conformance register
- `untyped-claim` — a claim not tagged existence-proof / method-claim

## Constitution Adjustments

None.

## Related Repos

- `agentic-governance` — canonical governance (this repo pins v0.2)
- `soa-agentic-se` — source of the paper/proposal writing agents ported here
