# ADR-0001: Adopt agentic-governance v0.2 with convention-only enforcement

Status: Accepted
Date: 2026-08-22
Deciders: Jason

## Context

This repo carries a 13-day sprint against a hard external deadline
(MATS 12.0 application, due 2026-09-04). The portfolio standard is
`agentic-governance` v0.2: governance delta, ADRs, PR/issue templates,
gov-level labels, branch protection, and the governance-checks script.

Two things pull against each other. The application is graded partly on
*truth-seeking and skepticism* — exactly what governance encodes — so
having the discipline is directly valuable. But full platform enforcement
(branch protection, required approvals on a single-person repo, required
status checks) would add merge latency to a sprint measured in hours, with
no second reviewer to make the approval meaningful.

## Decision

Adopt agentic-governance v0.2 in full at the **document** layer: governance
delta, ADR system, PR and issue templates, CONTRIBUTING, label taxonomy,
domain review questions, and the L0 allowlist.

Accept **convention-only enforcement** at the platform layer for the
duration of this project: no branch protection, no required approvals, no
required status checks. Record this honestly in the delta's Platform
Enforcement Reality section rather than leaving it aspirational.

Steward merge authority remains **INACTIVE**. No activation ADR will be
filed for this repo.

## Consequences

**Positive.** The review checklist and domain review questions do the work
that actually matters here — forcing a baseline next to every claim, a
human re-derivation of every agent-produced number, and a stated limitation
next to every finding. These map directly onto the application's grading
criteria.

**Negative.** Nothing prevents a direct commit to `main`. The discipline is
self-imposed and will hold only as well as the operator holds it. The delta
says so plainly.

**Follow-up.** If a GitHub remote is created, record what the platform
actually enforces (a 403 on `gh api .../branches/main/protection` on a
private free-plan repo means unavailable) rather than assuming.

## Alternatives considered

- **Full enforcement including branch protection.** Rejected: adds merge
  latency during counted hours, and single-owner approval is theater.
- **No governance at all.** Rejected: the review questions are the part
  that improves the deliverable, and they cost nothing.
