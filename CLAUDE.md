# mats-12-application — Agent Instructions

## The project

**J-Lens relational binding** — ADR-0005. When two prompts contain the same
entities but swap their relational roles, does J-Lens identify the correct
hidden intermediate? Design of record:
`llm/plans/jlens-relational-binding-experiment-design.md`.

**Scope is passive-primary.** H1/H2/H4 are the deliverable. The causal arm
(H3) is contingent on V2 clearing blocker B2 — the reference implementation
ships no sparse non-negative J-space reconstruction. Do not approximate it
with a top-token projection; that is the design's own FAIL condition.

**Substrate:** `Qwen/Qwen3.5-4B` + `neuronpedia/jacobian-lens` rev
`qwen-n1000`, verified on ARC L40S (8.51 GB peak). Do not fit a lens.

## What this is

A sprint to produce a MATS 12.0 application for Neel Nanda's mech interp
stream. Hard deadline **2026-09-04 23:59 PT**. Read
`llm/plans/PLAN.md` first, then `llm/memory_bank/activeContext.md`.

## Before anything ships

```
node scripts/conformance-check.mjs --gate SELECT|EXECUTE|WRITEUP|SUBMIT
```

`llm/application/conformance-register.md` holds all 121 requirements from
Neel's doc with source quotes — **38 are individually disqualifying**. The
`conformance-audit` skill runs the checker, the 15-criterion rubric, and the
adversarial `neel-reviewer` agent, and emits GO/NO-GO. No gate advances with
an open blocker (ADR-0003).

Three ledgers are how the blockers stay closed, and they are not optional:
- `llm/application/claims-register.md` — every claim typed
  `existence-proof` vs `method-claim`. Cherry-picking is permitted **only**
  under an explicit existence-proof tag.
- `llm/application/controls-ledger.md` — the cheap control actually run,
  and its result.
- `llm/application/verification-ledger.md` — every headline number
  re-derived by a human, via a path that does **not** share the original
  pipeline's code. Re-running the same script is not verification.

## Non-negotiables

1. **The 20-hour clock.** Experiments + analysis + planning + main write-up
   all count. Only the executive summary gets a separate +2h. Setup,
   general reading, breaks, and waiting on training do not count. If you
   are about to start counted work, say so.
2. **Never present agent output as a verified result.** Anything destined
   for the write-up must be re-derived by Jason. Flag unverified numbers
   with `agent-unverified` explicitly.
3. **Never report a metric without its control.** Random vector, random
   hint, "just ask the model", linear probe.
4. **Never report a single faithfulness number.** Two metrics minimum.
5. **Look at the raw data.** Before aggregating, print examples. Randomly
   selected, never cherry-picked.
6. **Simple before fancy.** Prompting and reading the CoT beat SAEs unless
   SAEs demonstrably win.
7. **Do not write the executive summary or form answers.** Neel explicitly
   penalizes LLM-voiced applications: *"Answers that read like they were
   written by an LLM are a significant negative signal - I see hundreds of
   them, and they blur together."* Draft structure and figures; Jason writes
   the prose.
8. **Type every claim before defending it.** `existence-proof` (cherry-pick
   allowed, must say so) or `method-claim` (random sample, recorded seed,
   baseline required).
9. **Check replication first.** Never build on a phenomenon without
   confirming it exists in this model, these prompts, this dataset.

## Context to load first (ADV-11)

Neel recommends putting his compiled 600k-token mech-interp context file in
the agent's context window:

> "**Context is crucial**: LLMs are much more useful when they have the
> relevant information in the context window... By default, just **put this
> 600k token file** in the context window."

It is committed at **`context/default_600k.md`** (2.24 MB, 41,360 lines), so a
fresh clone has it. Load it before doing research work.

⚠️ It is Neel's compilation, kept here because this repository is **private**.
Do not make this repository public without removing it first.

Also load, in this order: `llm/plans/PLAN.md`,
`llm/governance/adr/0005-accept-jlens-relational-binding.md`,
`llm/plans/jlens-relational-binding-experiment-design.md`,
`results/design-verification/environment-manifest.md`.

## Persistent kernel discipline (ADV-17 / ADV-18)

Exploratory interp work wants a **persistent Python process** — load the
model once, keep weights and activations in memory while iterating. Cold-start
scripts that reload a 4B model every call waste the budget.

This project uses the tmux + IPython pattern (Neel's "simple and unbreakable"
option), across two hops. See `llm/memory_bank/techContext.md` §Topology.

- **`agents4research`** — an Ubuntu VM inside the VT network. The durable
  orchestration shell lives here, in tmux session **`mats-12-application`**.
  It survives the Mac sleeping or dropping its connection; that is the entire
  reason for the hop.
- **`djjay@falcon1.arc.vt.edu`** — the ARC login node, reached with a key
  stored on the VM. Login node only: **never run compute here.**
- **GPU compute node** — reached via `salloc`/`sbatch`. This is where the
  model and lens load. `agents4research` is *also* the Slurm account name;
  do not confuse the two.

Run the persistent IPython kernel on the compute node, in tmux, nested inside
the VM's session. Nothing long-lived runs on the Mac side.

- Send code with `tmux send-keys`, read results with `tmux capture-pane`.
- **Load models and data in dedicated cells at the top.**
- **Never restart the kernel without asking.**
- **Always save plots to disk as PNGs** as well as displaying them — you can
  read PNGs natively, and they belong in `results/figures/` via
  `src/figstyle.py::save_figure` anyway.
- **Checkpoint expensive artifacts to disk** — activations, datasets, any
  fitted object — so a crashed kernel is an annoyance, not a lost hour.
- Run anything long as a background script with a log, not a kernel cell.
- Prefer plain `.py` over `.ipynb`.

## Layout

`llm/` is the control plane — PM, research, the governance delta and the
ADRs. Execution and its outputs are at the root. `docs/` is the data plane
and holds no source of truth. Declared paths:
`llm/governance/governance-delta.md` §Repository Layout; the routing rule is
at the end of this file.

## Models

Subject model: **`Qwen/Qwen3.5-4B`** with **`neuronpedia/jacobian-lens`**
rev `qwen-n1000` (commit `16a01f3`), verified compatible on ARC L40S —
`d_model` 2560 matching on both axes, `max(source_layers)=30 < 32`, peak GPU
8.51 GB. **Do not fit a lens**; use the pre-fitted public checkpoint.

Do **not** use GPT-2, Pythia, or Gemma 2 — all read as old to this reviewer.
Neel names the Qwen 3.5/3.6 dense family (4B, 9B, 27B) as good defaults, and
`deepseek-v4-flash-0731` for a highly capable model with J-Lenses published.

⚠️ Known issue **B4**: `len(tokenizer)=248077` against a 248320-wide
unembedding — ~243 ids have no tokenizer string. Rank metrics must state
which width they rank over.

The Olmo 3 post-training lineage belonged to candidate C2, superseded by
ADR-0005. Its verified details are preserved in
`llm/plans/project-candidates.md` should the fallback ever be needed.

## Tooling

- TransformerLens: use `TransformerBridge`, **not** the deprecated
  `HookedTransformer`.
- SAELens: now `decoderesearch/SAELens`, v6 refactor.
- nnsight 0.6 / NDIF; nnsight × vLLM for scale. Note inference mode blocks
  gradients — no probe training through it.
- Do not use transformer-debugger (dead).

## Agents available

`paper-agent`, `position-paper-agent`, `proposal-agent`, `latex-agent`,
`review-agent`, `memory-agent`, `knowledge-steward`, `feature-architect`,
plus the governance executives (`chief-architect`, `chief-reviewer`,
`chief-product-officer`, `repository-steward`).

Skills: `constellize:*` for memory and feature workflows,
`governance-establish` / `governance-audit`.

## Governance

`llm/governance/governance-delta.md`, pinned to agentic-governance v0.8. Issue →
branch → PR with a governance-level declaration → review → merge. Steward
merge authority INACTIVE.

<!-- BEGIN agentic-governance: repository layout -->
## Repository layout: two planes

The source of truth for this rule is agentic-governance
`llm/governance/project-operating-system.md` §Repository Areas, and the
decision behind it is
`llm/governance/adr/0001-llm-control-plane-docs-data-plane.md`. Both are
paths **inside the canonical repo**: resolve them against the
`Canon checkout` declared in `llm/governance/governance-delta.md`
§Canon Location, or read them at
<https://github.com/djjay0131/agentic-governance>.
Where this file and §Repository Areas disagree, §Repository Areas
wins. The paths below are the ones this repo declares in
`llm/governance/governance-delta.md` §Repository Layout.

The split is by **role**, not by authorship. Who wrote a document
decides nothing; what the document *does* decides everything.

**Control plane — the `llm/` tree.** Artifacts that govern, plan,
record, review, or operate this repository: governance policy and
the governance delta, role charters, workflows, prompts and skills,
design specs acting as design authority, implementation plans,
backlog and feature specs, the memory bank, ADRs, roadmaps,
execution patterns, and review and retrospective records.
Control-plane documents are sources of truth, and nothing downstream
is authoritative over them.

**Data plane — the artifacts tree (`docs/`).** Project and
domain deliverables, external material, and derived views of
control-plane content: product and API documentation, project/domain
technical specifications and reference material, vendor and
third-party specifications, external proposals, research sources,
PDFs, diagrams, datasets, and published sites and generated views.
Nothing here governs how this repository is operated.

**No artifact that governs repository operation lives in the
artifacts tree, and any view placed there must name the `llm/`
document it projects.**

### Before you create any document: Q1, then Q2

**Q1 — Does this artifact control how the repository is governed,
planned, remembered, reviewed, or operated?** YES → control plane
(`llm/`). This is governance policy and the governance delta, role
charters, workflows, prompts and skills, design specs acting as
design authority, implementation plans, backlog and feature specs,
the memory bank, ADRs, roadmaps, execution patterns, and review and
retrospective records.

**Q2 — Otherwise: is it a project or domain deliverable, technical
reference, external source, specification, or generated project
documentation?** YES → the artifacts tree (`docs/`). This
is product and API documentation, project/domain technical
specifications and reference material, vendor and third-party
specifications, external proposals, research sources, PDFs,
diagrams, datasets, and published sites and generated views. A
derived view of a control-plane document belongs here too, and must
name the `llm/` document it projects.

**Otherwise — do not invent a location.** Use the existing structure
the artifact plainly belongs to (`src/`, `experiments/`, `results/`,
`writeup/`, `scripts/`, `.github/`), or escalate to the Repository
Steward.

If the answer to Q1 is unclear, treat the artifact as control plane.
Misfiling a source of truth as an artifact is the failure this rule
exists to prevent; the reverse is cheap to correct.

### Canonical destinations

| Content | Destination |
|---|---|
| Governance policy, the delta, patterns | `llm/governance/` |
| Architecture Decision Records | `llm/governance/adr/` |
| The phased plan, candidate scoring, the design of record | `llm/plans/` |
| Sprint plans, prompt payloads, process overlays | `llm/construction/` |
| Feature specs and backlog | `llm/features/` |
| Memory bank | `llm/memory_bank/` |
| Literature scan, positioning and discussion notes | `llm/research/` |
| Application instructions, conformance register, the three ledgers | `llm/application/` |
| Product/domain docs, external material, published views | `docs/` |

ADRs are control plane: an ADR *is* the decision, not a report of
one. A published ADR index may be generated into the artifacts tree
as a derived view.

This repo declares only the paths it uses. An absent slot is not a
violation; an undeclared path is. This repo declares **no**
constitution directory (its role charters are vendored under
`.claude/agents/`, a tool-contract path) and **no** separate spec
directory (the design of record lives in `llm/plans/`). If a document
needs a home that is not listed above, do not invent a path: use the
existing structure it plainly belongs to, or escalate to the
Repository Steward.

### Tool-contract paths

Some paths are fixed by a tool or a platform rather than chosen by
this project. They sit outside both planes and are exempt. The class
is closed:

- `.github/` — workflows, issue templates, PR templates.
- `.claude-plugin/` — the marketplace manifest.
- The plugin payload root — whatever directory a marketplace
  `source` field points at.
- Root-convention files: `README.md`, `CHANGELOG.md`, `VERSION`,
  `CONTRIBUTING.md`, `LICENSE`, `CLAUDE.md`, `AGENTS.md`.

The exemption covers **location only**. A tool default is never
design authority. Where a tool writes control-plane content into the
artifacts tree, override the tool here and relocate the output.

### Output-location preferences (these override tool defaults)

These are the repository owner's standing **user preferences for
spec and plan location**. They take precedence over any skill's,
plugin's, or tool's default output path.

**Design specs and brainstorming output.** Write every design spec
to `llm/plans/YYYY-MM-DD-<topic>-design.md`. **Never** write to
`docs/superpowers/specs/`, and never create a `docs/superpowers/`
directory.

**Implementation plans.** Write every implementation plan to
`llm/plans/YYYY-MM-DD-<feature-name>.md`. **Never** write to
`docs/superpowers/plans/`, and never create a `docs/superpowers/`
directory.

This applies to the `obra/superpowers` skills — `brainstorming`,
`writing-plans`, and anything downstream of them — and to any other
tool with a hardcoded documentation path. If a skill instructs you
to write a spec or a plan somewhere else, this preference wins:
create the document under `llm/` instead, and do not mirror or copy
it into the artifacts tree.
<!-- END agentic-governance: repository layout -->
