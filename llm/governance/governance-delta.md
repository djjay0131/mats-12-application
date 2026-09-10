# Governance Delta: mats-12-application

Status: Active
Last updated: 2026-09-10
Governance: agentic-governance v0.5

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

`llm/plans/PLAN.md` — the phased plan, time budget, and gates. Candidate
selection is authorized by `llm/governance/adr/0002-project-selection.md`,
and the accepted project by
`llm/governance/adr/0005-accept-jlens-relational-binding.md`.

This repo declares no separate spec directory, so the design of record
(`llm/plans/jlens-relational-binding-experiment-design.md`) sits in the plans
directory alongside the plan it drives. See §Repository Layout.

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
  is that control in `llm/application/controls-ledger.md` with its result?
- Is every claim typed `existence-proof` or `method-claim` in
  `llm/application/claims-register.md`? An untagged cherry-pick carrying a
  general claim is the red flag he names by name.
- Has a human **independently re-derived** every number this change adds,
  by a path that does not share the original pipeline's code, and recorded
  it in `llm/application/verification-ledger.md`?
- Has a human read raw examples supporting this claim, selected randomly
  with a recorded seed?
- Is any LLM-judge step validated against hand labels?
- Does the write-up state the limitation as plainly as the finding?
- Would this survive the question "how could this result be false?"
- Does `node scripts/conformance-check.mjs --gate <current gate>` pass?

## Memory Bank

Path: `llm/memory_bank/`

## Roadmap

Path: `llm/plans/PLAN.md`

## Governance Check Command

Two commands, both required:

```
node ~/code/agentic-governance/plugin/scripts/governance-checks.mjs --layout
node scripts/conformance-check.mjs --gate <SELECT|EXECUTE|WRITEUP|SUBMIT>
```

`--layout` is required, not optional: it asserts that every path declared in
§Repository Layout exists and that no source of truth sits under the declared
artifacts directory. Without it the two-plane rule is enforced only at
onboarding, which is how this repo kept its delta and its ADRs in the data
plane for three weeks.

The first is the canonical portfolio check. The second is project-specific
and asserts the mechanically-checkable subset of the 121 requirements in
`llm/application/conformance-register.md` — the register extracted verbatim
from Neel's application doc, of which 38 are individually disqualifying.
Rationale: ADR-0003. No gate advances with an open blocker; an accepted risk
requires an ADR, not a shrug.

## L0 Path Allowlist

The fenced block below is an instance of the canonical rule set in
agentic-governance `llm/governance/l0-fast-track.md` §Template Allowlist,
which defines the grammar and the diff shapes. Deny rules are checked first;
every path is bound to §Repository Layout below. The self-referential rules —
the delta's own path and the ADR template — moved with everything else, and a
stale one there silently stops the fast track matching anything.

```l0-allowlist
# Instance of agentic-governance `llm/governance/l0-fast-track.md`
# §Template Allowlist — the source of this rule set and its grammar.
allow llm/memory_bank/** path-only
allow llm/governance/adr/README.md index-table-rows
allow llm/governance/adr/[0-9][0-9][0-9][0-9]-*.md status-line-only
allow llm/plans/PLAN.md checkbox-only
allow llm/** link-target-only
allow docs/** link-target-only
deny src/**
deny scripts/**
deny .github/**
deny llm/governance/adr/0000-template.md
deny llm/governance/governance-delta.md
deny writeup/**
deny results/**
deny scripts/conformance-check.mjs
deny llm/application/**
deny llm/plans/jlens-relational-binding-experiment-design.md
deny experiments/**
```


## Repository Layout

The paths this repo binds. The canon prescribes the shape (agentic-governance
`llm/governance/project-operating-system.md` §Repository Areas, ratified by
`llm/governance/adr/0001-llm-control-plane-docs-data-plane.md`); this block
binds it here, so nothing downstream hardcodes a path. Declare only the slots
this repo uses — an absent slot is not a violation, an undeclared path is.

Revised 2026-09-10 for agentic-governance v0.5. Before that, this repo kept
its delta and its ADRs under `docs/` on the belief that
`governance-checks.mjs` hard-coded those paths. It does not: it reads them
from this block, and the canonical defaults were the other way round the whole
time.

- Governance directory: `llm/governance/`
- ADR directory: `llm/governance/adr/`
- Sprints directory: `llm/construction/`
- Plans directory: `llm/plans/`
- Features directory: `llm/features/`
- Memory-bank path: `llm/memory_bank/`
- Artifacts directory: `docs/`

Two further control-plane directories this repo uses, for which the canon
defines no slot. They are declared here because an undeclared path is the
violation:

- Research material: `llm/research/`
- Application material: `llm/application/`

**Not declared, deliberately.** No constitution directory — the role charters
are vendored under `.claude/agents/`, a tool-contract path. No spec directory
— the design of record lives in the plans directory (§Design-Authority
Document).

**`llm/plans/`, not `llm/plan/`.** The slot could have been bound to the
singular path; the canonical name was adopted instead, because the local name
carried no meaning, is not a published URL or an import path, and diverging
from every canonical table and tool default costs a lookup on every future
edit for no benefit.

**`llm/construction/`, not `llm/sprints/`.** Bound rather than renamed. It
holds the verification sprint plan, its prompt payloads, the process overlay
and the spec builder — `sprints/` would name a third of it.

### The data plane, and the work itself

`docs/` is the artifacts tree and holds no source of truth. It currently
carries one derived index (`docs/README.md`), which names the `llm/`
documents it projects, as a derived view must.

Everything below is **deliverables, evidence, and the code that produced
them** — data plane by Q2, kept in the structure it plainly belongs to rather
than moved under `docs/`. Q1 is NO for every one of them: none governs, plans,
remembers, reviews or operates this repo.

| Path | Holds | Plane |
|---|---|---|
| `experiments/` | Slurm batch scripts, run definitions, analysis entry points | Execution |
| `results/` | Run outputs, manifests, figures, frozen held-out numbers | Evidence |
| `writeup/` | The report and the executive summary — the submission | Deliverable |
| `src/`, `notebooks/` | Experiment and figure code | Execution |
| `scripts/` | `conformance-check.mjs` and repo tooling | Tooling |
| `context/` | Neel's compiled 600k-token mech-interp context file | External source material |

These are **not** relocated under `docs/`. `results/` alone is 189 tracked
files of evidence whose paths are cited by name in the write-up, the
environment manifest and the reproduce script; moving it would break the
audit trail of a submitted application to satisfy a directory name. The canon
provides for this directly: where an artifact is neither control plane nor a
document, use the existing structure it plainly belongs to rather than
inventing a location.

Rule of thumb: if it describes **what we will do or why**, it belongs under
`llm/`. If it **is the work or its output**, it belongs at the root. If it is
a derived view of something under `llm/`, it belongs in `docs/` and must say
what it projects.


## Platform Enforcement Reality

Verified against the live API on 2026-08-24, not assumed.

- **Branch protection on `main`: UNAVAILABLE.**
  `GET /repos/djjay0131/mats-12-application/branches/main/protection` returns
  **403** — *"Upgrade to GitHub Pro or make this repository public to enable
  this feature."* Branch protection cannot be configured on a private repo
  on this plan. This is the case ADR-0001 anticipated, and it is recorded
  here rather than left aspirational.
- **Required status checks: UNAVAILABLE** — same 403, same cause.
- **Token/identity model:** single owner (`djjay0131`). Pushes during this
  project may originate from a fine-grained PAT scoped to this repo alone.
  Chief Architect, Chief Reviewer, Repository Steward and Chief Product
  Officer are **procedural roles, not distinct identities** — nothing at the
  platform layer distinguishes them.
- **What is actually enforced:** nothing. Every control in this repo is
  convention, held by the operator and by `scripts/conformance-check.mjs`.
  The Issue → branch → PR → review → merge flow is honoured, not imposed.
- **Hardening path:** make the repo public, or upgrade to GitHub Pro. Both
  are rejected for this project — public would expose an in-flight
  application in a process where originality is graded, and a paid upgrade
  buys enforcement that is theatre on a single-reviewer repo. Revisit after
  2026-09-04.

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

- `agentic-governance` — canonical governance (this repo pins v0.5)
- `soa-agentic-se` — source of the paper/proposal writing agents ported here
