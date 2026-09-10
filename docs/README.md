# docs/ — the data plane

This directory is the **artifacts tree** (`agentic-governance`
`llm/governance/adr/0001-llm-control-plane-docs-data-plane.md`). It holds
project deliverables, external material, and derived views of control-plane
content. **Nothing here governs how this repository is operated**, and no
source of truth lives here.

It used to hold `adr/` and `governance-delta.md`. Both were control plane in
the data plane, and both moved to `llm/governance/` — see the delta's
§Repository Layout.

## What this file projects

This page is a derived view, so it names the `llm/` documents it points at:

| Looking for | It is at |
|---|---|
| How this repo is governed | [`llm/governance/governance-delta.md`](../llm/governance/governance-delta.md) |
| Decision records | [`llm/governance/adr/`](../llm/governance/adr/) |
| The project plan, timeline and gates | [`llm/plans/PLAN.md`](../llm/plans/PLAN.md) |
| The design of record | [`llm/plans/jlens-relational-binding-experiment-design.md`](../llm/plans/jlens-relational-binding-experiment-design.md) |
| Living state, progress, the 20-hour ledger | [`llm/memory_bank/`](../llm/memory_bank/) |
| The 121 requirements and the three ledgers | [`llm/application/`](../llm/application/) |

## Where the deliverables are

They are not in here. This repo's outputs live in the directories that
produce them, which is the structure they plainly belong to rather than an
invented one:

- `writeup/` — the report and the executive summary.
- `results/` — run outputs, manifests, figures. Evidence.
- `experiments/`, `src/`, `notebooks/`, `scripts/` — the code that made them.
- `context/` — externally-sourced material (Neel's compiled context file).

## Before you add a file here

Answer Q1 then Q2 from `CLAUDE.md` §Repository layout: two planes. If what
you have governs, plans, remembers, reviews or operates this repo, it belongs
under `llm/`, not here. If you put a derived view here, name the `llm/`
document it projects — as this file does.
