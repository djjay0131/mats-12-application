# Contributing

This repo follows
[`agentic-governance`](https://github.com/djjay0131/agentic-governance)
**v0.2**. Policy lives there; project facts live in
[`docs/governance-delta.md`](docs/governance-delta.md). Nothing here
restates policy.

## Flow

Issue → branch → draft PR (governance level declared first) → review →
merge. No direct commits to `main`. Steward merge authority is **INACTIVE**.

## Governance levels

| Level | Meaning | Merge authority |
|---|---|---|
| L0 | Administrative, non-semantic (memory-bank notes, ADR status lines, link fixes) | Human — the fast track is not activated here |
| L1 | Semantic but local | Human review required |
| L2 | Architectural | Human review + ADR |
| L3 | Product / what we submit | Human review + ADR |

Conservative default: if unsure, escalate.

## Before opening a PR

Run the governance checks:

```
node ~/code/agentic-governance/governance/scripts/governance-checks.mjs
```

## Domain review questions

Beyond the canonical checklist, this project asks:

- Does this change consume counted hours, and is the log updated?
- Does every reported number have a control or baseline alongside it?
- Has a human read raw examples supporting this claim?
- Is any LLM-judge step validated against hand labels?
- Does the write-up state the limitation as plainly as the finding?
- Would this survive "how could this result be false?"

## Special labels

- `counted-time` — consumes the 20-hour budget
- `needs-baseline` — a claim without its control
- `agent-unverified` — agent output no human has re-derived
