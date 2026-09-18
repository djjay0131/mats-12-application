# ADR-0007: Delete the vendored copies of canonical skills and role charters

Status: Accepted
Date: 2026-09-17
Deciders: Jason

## Context

This repo carried six files copied out of `agentic-governance` at
onboarding, before the governance plugin existed:

| Vendored file | Lines here | Lines in canon v0.9.0 | Drift |
|---|---|---|---|
| `.claude/skills/governance-establish/SKILL.md` | 104 | 538 | 434 lines of procedure never copied forward |
| `.claude/skills/governance-audit/SKILL.md` | 86 | 180 | 94 lines |
| `.claude/agents/repository-steward.md` | 206 | 265 | 87 changed diff lines |
| `.claude/agents/chief-architect.md` | 131 | 132 | 17 changed diff lines |
| `.claude/agents/chief-reviewer.md` | 103 | 103 | 6 changed diff lines |
| `.claude/agents/chief-product-officer.md` | 86 | 86 | **0 — byte-identical** |

Measured against the installed plugin at
`~/.claude/plugins/marketplaces/agentic-governance`, VERSION `0.9.0`, git
HEAD `851a50a0692d4409cbd255e3b3be111d863ae264` — the v0.9.0 tag commit.

The drift is not cosmetic. Every vendored charter still cites canon paths
that canon abandoned at v0.5: `docs/architecture-governance.md`,
`docs/review-checklist.md`, `docs/l0-fast-track.md`,
`docs/project-operating-system.md`, `docs/patterns/prompt-patterns.md`. Those
files live under `llm/governance/` in canon today. A charter that tells an
agent to consult `docs/review-checklist.md` is pointing at nothing. The
vendored `chief-architect.md` also still hardcodes
`~/code/agentic-governance`, which canon replaced with
`${CLAUDE_PLUGIN_ROOT}/..` and the delta's §Canon Location declaration.

**An earlier attempt to delete these was correctly refused**, because the
plugin was not actually installed at the time and deleting them would have
left the repo with no governance capability at all. That blocker is gone.
Verified before this decision:

- `~/.claude/plugins/marketplaces/agentic-governance` exists, VERSION `0.9.0`,
  git HEAD is the v0.9.0 tag commit `851a50a`.
- It provides `plugin/skills/{establish,audit,migrate}` and
  `plugin/agents/{chief-architect,chief-product-officer,chief-reviewer,repository-steward}.md`
  — every file being deleted here has a live, current counterpart.
- `governance@agentic-governance` is `true` in both `~/.claude/settings.json`
  and this repo's `.claude/settings.json`; the marketplace is registered by
  git URL, as §Canon Location declares.

## Decision

Delete the six vendored files. Resolve the governance skills and charters
through the installed plugin, under their `governance:`-qualified names.
Repoint every inbound reference in this repo to the qualified names.

**Keep**, explicitly:

- `.claude/skills/conformance-audit/` — genuinely local. It audits this
  project's 121-requirement conformance register (ADR-0003); canon has no
  such skill and no equivalent.
- The nine project agents: `paper-agent`, `neel-reviewer`, `latex-agent`,
  `position-paper-agent`, `proposal-agent`, `memory-agent`,
  `knowledge-steward`, `feature-architect`, `review-agent`.
- The seven `constellize:*` skills. Untouched.

## Rationale

**The reason is drift and unqualified-name ambiguity. It is not shadowing.**

This distinction matters enough to state plainly, because the original
justification for removing these files asserted shadowing and that assertion
was wrong. Plugin skills are namespaced — `governance:establish`,
`governance:audit`. The vendored directories were not — `governance-establish`,
`governance-audit`. They are different identifiers. Both sets were present and
addressable at the same time; neither hid the other, and nothing was
overridden.

The actual failure is narrower and quieter. An **unqualified** reference
resolves to the local copy, and unqualified is exactly how this repo's own
prose named them. `CLAUDE.md` §Agents available listed the four executives as
`chief-architect`, `chief-reviewer`, `chief-product-officer`,
`repository-steward`, and the skills as `governance-establish` /
`governance-audit` — no prefix anywhere. An agent following those instructions
reached the stale copies every time, and the fresh plugin versions sat beside
them unread. Deleting the local copies removes the ambiguity at its root:
there is one thing to resolve to, and it is current.

**`chief-product-officer.md` is the argument in miniature.** It is
byte-identical to canon today — identical md5. It is still deleted, because a
copy that happens to be correct now has to be *kept* correct forever, by
someone remembering, on every canon release, with nothing to tell them when
they forget. Its three siblings are proof of how that goes: all three started
byte-identical too, and are now 6, 17 and 87 diff lines behind. Correctness
today is not a reason to keep a duplicate; it is the state every duplicate
starts in.

Canon states the principle directly: *a prose copy of an executable procedure
is a defect* — skills are the procedure, and documentation cites them rather
than restating them (`llm/governance/architecture-governance.md`
§Documentation Standards). A vendored copy of a skill is that defect in its
most literal form.

## Alternatives Considered

### Keep the copies and sync them on each canon release

Benefit: works offline and with no plugin installed; the repo is
self-contained.

Drawback: it is precisely what was tried and failed. The copies went four
minor versions stale while canon moved its entire document tree from `docs/`
to `llm/governance/`, and nothing surfaced that. There is no check that could
have caught it — `governance-checks.mjs` validates this repo's structure, not
whether a `.claude/` copy matches an upstream file it has no reference to.
The sync is unenforceable and was never performed.

### Keep only the four charters, delete the two skills

Benefit: the charters are small and drifted least; the skills had drifted
worst (434 lines).

Drawback: it preserves exactly the ambiguity being removed, for the
references that actually appear in this repo's prose the most. And
`repository-steward.md` — a charter — is 87 diff lines behind, worse than
either of the smaller charters. Size of drift does not sort cleanly by file
type.

### Leave everything and fix only the `CLAUDE.md` references

Benefit: minimal diff, no deletions, no capability risk at all.

Drawback: the stale files remain resolvable. Anyone typing the unqualified
name at a prompt, and any future document written from the old pattern,
lands back on them. It fixes the symptom this repo happens to have written
down while leaving the mechanism intact.

### Vendor them as a git submodule or pinned subtree

Benefit: version-pinned, updatable with one command, visible in the diff.

Drawback: duplicates the plugin's job for a repo that already registers the
marketplace by git URL, and adds a second canon location to keep in step
with §Canon Location — which exists specifically so there is exactly one
machine-specific path here.

## Consequences

### Positive

- The governance skills and charters are always at the installed plugin's
  version. Drift is structurally impossible rather than merely discouraged.
- Six files, and 716 lines of stale instruction citing paths that no longer
  exist, leave the repo.
- One resolution path per name. `governance:audit` is unambiguous in a way
  `governance-audit` was not.
- `.claude/agents/` now holds exactly this project's own agents, which is
  what a tool-contract path in a project repo should contain.

### Negative / Tradeoffs

- The repo is no longer self-contained with respect to governance
  capability: without the plugin installed, `/governance:establish` and
  `/governance:audit` are unavailable and the executive charters are absent.
  §Canon Location already declares the plugin registration as a project
  fact, so this dependency is recorded rather than implicit — but it is a
  real dependency, newly load-bearing.
- Reading a charter now means looking outside the repo, at
  `${CLAUDE_PLUGIN_ROOT}/agents/`, rather than at a file in the tree.
- Git history for the four charters and two skills ends here. The deletion
  commit is the pointer; the content stays reachable in history.

### Risks

- **A future document reintroduces an unqualified reference.** Nothing
  mechanically prevents someone writing `chief-architect` again. Mitigated
  by naming the qualified form in `CLAUDE.md` and stating why, and by the
  delta's §Repository Layout note that the charters are not in this repo.
  Not eliminated.
- **A plugin uninstall silently removes governance capability.** Previously
  the vendored copies would have answered, staleness and all. Accepted:
  stale-but-present is a worse failure than absent-and-obvious, because the
  first is invisible and the second is not.
- **Canon renames a skill.** `governance:audit` becoming something else
  would dangle this repo's references. Lower risk than the converse: a
  rename is visible in canon's changelog at a pinned version, and CI now
  pins canon by SHA, so a canon change cannot reach this repo without a
  commit here.

## Impacted Areas

- [x] AI architecture
- [x] Implementation
- [x] Documentation

## Related Documents

- `llm/governance/governance-delta.md` §Canon Location, §Repository Layout
- `CLAUDE.md` §Agents available
- Canon: `llm/governance/architecture-governance.md` §Documentation Standards
- ADR-0001 (adopt agentic-governance), ADR-0003 (conformance regime — why
  `conformance-audit` is local and stays)

## Related Issues / PRs

- PR #13 — this change
- PR #12 — added CI running the canonical governance check, which pins canon
  by the same v0.9.0 SHA this decision was measured against

## Supersedes

None.

## Superseded By

None.
