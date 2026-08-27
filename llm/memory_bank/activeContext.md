# Active Context

Last updated: 2026-08-26

Current focus, next actions and live risks only. Durable environment facts
are in `techContext.md`; conventions in `systemPatterns.md`; scope in
`projectbrief.md`.

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

## Live risks

- ⚠️ **B2** — no sparse non-negative J-space reconstruction in the reference
  code. Scoped by ADR-0005, settled at V2.
- ⚠️ **Crowding** — J-Lens was promoted with a bolded "Key resource" link.
  The relational-binding framing has to carry the differentiation, and it
  must be obvious in the first paragraph.
- Schedule — 20 counted hours across 9 days with no slack for a second false
  start. A V2 that runs long is the most likely way to lose a day.

B3, B4 and queue latency are environment facts, not live decisions:
`techContext.md` §Known environment issues.

## Where the work runs

Mac → `agents4research` (Ubuntu VM, durable tmux `mats-12-application`) →
`djjay@falcon1.arc.vt.edu` (ARC login) → `salloc` GPU node. The VM hop exists
so the session survives the Mac sleeping. `agents4research` is also the Slurm
account name — do not conflate. Detail: `techContext.md` §Topology.

**Open question for V1:** where the repo working copy lives. Options are a
clone on the VM with results pulled back, or a clone on ARC with the VM as a
pure orchestration shell. The second is simpler — jobs and data are already
on ARC at `/scratch/$USER/mats12` — but confirm before building on it.

## Design deltas from the 600k audit

`llm/research/context-audit-2026-08-26.md`. Eight changes folded into the
execution prompt; two are Jason's call:

- **Open — promote H3 out of contingency.** ADR-0005 §2 deferred the causal arm
  because the reference implementation has no J-space reconstruction. The audit
  shows causal validity does not require intervening *in J-space*: a 1-D
  activation-space intervention on a difference-in-means direction, patched on
  the residual stream, is a few lines. That converts a predicted negative from
  a number into a mechanism, which is what the novelty squeeze (L764) demands.
  Would need an ADR-0006.
- **Open — cut two redundant controls** (pair-alternative / relation deletion /
  question truncation are mutually predictive) to pay for the coverage control,
  the supervised ceiling and the order-reversed variant.

**Headline:** the 600k file predates J-Lens — zero mentions. It is background,
not requirements, and the write-up must define J-Lens from first principles.

## Open

- The three ledgers still carry their example rows. Delete them before the
  first real entry — `conformance-audit` flags any row containing "example".
- Local git is deadlocked on lock files the bridge cannot unlink; commits are
  going in server-side via the GitHub API. Jason clears it with
  `rm -f .git/*.lock && git fetch && git reset --hard origin/main && git gc --prune=now`.
- `origin/docs/jlens-relational-binding-history` and
  `origin/exp/jlens-design-verification` are kept deliberately as work history.
- `latex-agent`, `proposal-agent` and `position-paper-agent` are dead weight
  for a pandoc/Word project. Kept for now by decision.
