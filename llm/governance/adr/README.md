# Architecture Decision Records

Durable decisions for this project. One decision per file, numbered
sequentially. Template: `0000-template.md`.

Lifecycle: **Proposed** → **Accepted** → (**Superseded by NNNN** |
**Deprecated**). A decision that changes how the project spends its
counted hours, what it claims, or what it submits belongs here — not in a
commit message.

| # | Title | Status | Date |
|---|---|---|---|
| [0001](0001-adopt-agentic-governance.md) | Adopt agentic-governance v0.2, convention-only enforcement | Accepted | 2026-08-22 |
| [0002](0002-project-selection.md) | Project selection for the 20-hour application task | Superseded | 2026-08-24 |
| [0003](0003-conformance-regime.md) | Treat Neel's instructions as a machine-checkable requirements register | Accepted | 2026-08-22 |
| [0004](0004-proposed-jlens-relational-binding-candidate.md) | Consider J-Lens relational-binding evaluation | Superseded | 2026-08-24 |
| [0005](0005-accept-jlens-relational-binding.md) | Accept the J-Lens relational-binding project; supersede ADR-0002 | Accepted | 2026-08-26 |
| [0006](0006-proposed-suppress-generation-restatement.md) | Suppress the model restatement of the intermediate before the held-out freeze | Proposed | 2026-08-29 |

ADR-0006 is **Proposed and parked**: the post-query sweep made it unnecessary
for the primary claim, and Jason ruled on 2026-08-29 not to action it. It is
kept rather than rejected, so it is not Deprecated. It previously carried
`Status: Deferred`, which is not in the lifecycle above and which
`governance-checks.mjs --layout` had never seen, because before the v0.5
migration the checker was looking for ADRs at `llm/governance/adr/` — a
directory that did not yet exist — and passing on an empty set.
