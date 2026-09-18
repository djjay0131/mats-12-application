# Progress

## 2026-08-22 — Repo established

- `mats-12-application` created; governance adopted from
  `agentic-governance` v0.2 (ADR-0001, convention-only enforcement).
- Paper/proposal agents ported from `soa-agentic-se`: `paper-agent`,
  `position-paper-agent`, `proposal-agent`, `latex-agent`, `review-agent`,
  `memory-agent`, `knowledge-steward`, `feature-architect`; plus the
  `constellize:*` skills and commands.
- Neel's application doc retrieved in full (125k chars) and distilled into
  `llm/application/`.
- Literature scan completed — `llm/research/literature-scan-2026-08-22.md`.
- Five candidates scored — `llm/plan/project-candidates.md`.
- Day-by-day plan to Sept 4 — `llm/plan/PLAN.md`.

**Correction captured:** the main write-up counts *inside* the 20 hours;
only the executive summary gets the separate +2h. Plan rebalanced to ~15h
experiments / ~4h write-up / ~1h slack.

**Counted hours: 0 / 20.**

## Next

Gate 1, Aug 24.

## 2026-08-22 (later) — Conformance regime + C2 unblocked

- Extracted **121 requirements** from Neel's doc into
  `llm/application/conformance-register.md` — 38 BLOCKER, 33 SCORED,
  21 MECHANIC, 29 ADVICE — each with source quote, verification method,
  automatable flag, and gate. Includes a resolution rule for the three
  places the doc contradicts itself.
- Built `scripts/conformance-check.mjs` — gated assertions
  (`--gate SELECT|EXECUTE|WRITEUP|SUBMIT`), exits non-zero on failure.
  `--gate SELECT` currently green.
- Added the three ledgers: claims register (claim typing), controls ledger
  (cheap control + result), verification ledger (independent re-derivation
  + the 60-second unaided-explanation test).
- Added the `neel-reviewer` agent (five adversarial passes, instructed to
  reject) and the `conformance-audit` skill (runs all three layers,
  emits GO/NO-GO).
- ADR-0003 records the regime.
- **Olmo 3 Think lineage verified GO.** Four public stage endpoints plus
  55 RL / 43 SFT intermediate checkpoints as git branches. C2 unblocked and
  upgraded — continuous curve rather than four points.

**Counted hours: 0 / 20.**

## 2026-08-26 — Project locked; repo reorganised; report wired

- **ADR-0005 accepted.** J-Lens relational binding is the project. ADR-0002
  superseded, ADR-0004 resolved. Tie between C6 and C2 (both 24/25) broken on
  the uncounted ARC head start and the graceful-degradation asymmetry: B2
  threatens only C6's causal arm, while C2's tokenizer risk threatens its
  primary comparison. Scope declared passive-primary. Clock ruled: nothing
  counted yet, no reset needed.
- **C6 scored into `llm/plan/project-candidates.md`** on the same five
  dimensions as C1–C5, with the case for C2 stated rather than buried.
- **Repo reorganised** to the portfolio convention: all planning and research
  material under `llm/`; `docs/` keeps only ADRs and the governance delta.
  Layout documented in the delta. All cross-references updated;
  `governance-links` and `adr-index` pass.
- **Conformance checker fixed twice by its own findings:** GATE-1 still
  pointed at the superseded ADR-0002, and BLK-11 treated every markdown table
  as a results table. Both corrected.
- **Report pipeline built.** `writeup/{exec-summary,main}.md` →
  `scripts/build-report.sh` → `writeup/mats12-report.docx` (pandoc), with
  exec-summary word-count and figure-presence gates in the build. Figures go
  through `src/figstyle.py` onto a validated 3-slot palette and register
  themselves in `results/figures/FIGURE-REGISTRY.md`. Three watermarked
  placeholders prove the pipeline end to end.

**Counted hours: 0 / 20.**

## 2026-08-26 (later) — Merge, cleanup, memory bank restructured

- **Merged to main** (`13734ec`) — server-side via the GitHub API, because
  local git deadlocked: every write leaves a `.lock` the bridge cannot
  unlink, and each leftover blocks the next command. Verified by cloning main
  fresh: governance checks green, conformance clean, report builds.
- **Finished the cleanup the reorg had left half-done** (`e65fed0`).
  `llm/plan/PLAN.md` still described the superseded C2/Olmo project — and it
  is the roadmap path declared in the governance delta, so a stale one broke
  the design-authority chain. Rewritten around the J-Lens experiment, the
  passive-primary scope, the nine-day schedule and the V1/V2/V3 gates.
  `CLAUDE.md` carried both substrates at once; replaced with Qwen3.5-4B plus
  the pinned lens. Dropped three redundant `.gitkeep` files.
- Deleted the merged `docs/candidate-c6-scoring` branch. Kept
  `docs/jlens-relational-binding-history` and `exp/jlens-design-verification`
  as work history, by decision.
- **Memory bank restructured** (`memory:revise`). Created the two canonical
  files that never existed — `techContext.md` and `systemPatterns.md` — and
  moved the environment and convention material out of `activeContext.md`,
  which had been carrying durable facts in a transient file. Relocated the
  discussion history to `llm/research/` and the learning-log template to
  `llm/construction/`; neither is living memory. Rewrote `projectbrief.md`,
  which still described the project generically. Added `docs/README.md` to
  explain why that directory holds only ADRs and the delta.

**Counted hours: 0 / 20.**

## 2026-09-03 → 09-05 — Write-up assembled, condensed, and mirrored to a Google Doc

- **Executive summary** written by Jason in the repo (`0bdb1ad` … `ffb4837`),
  then edited directly in the Google Doc; split into methodology and results
  per experiment with one figure each; ranks reported for both dev (35 vs
  ~1,000) and held-out (128 vs 393). Cut to ~800 words / 3 pages on 09-05.
- **Experiment 2 controls figure** `results/figures/stage3-controls.png`
  added and registered (CL-02, CL-04).
- **Main body condensed** 6.5k → 3.6k → 3.2k words (`4116910` and after);
  unabridged text preserved as `writeup/main-full.md`; run-id citations
  restored so BLK-36b resolves.
- **Google Doc** carries the executive summary and body with figures
  embedded from the public repo; 16 pages after the 09-05 pass.
- **Repository made public** for submission.
- **Time ledger** brought current: 19.3 / 20 counted (7.1 verified,
  8.2 estimated, 4.0 Jason-stated for the write-up). Executive summary
  2.0 / 2.0, Jason-stated.

**Counted hours: 19.3 / 20.**

## 2026-09-10 — Migrated to the agentic-governance v0.5 two-plane layout

- Pin moved **v0.2 -> v0.5**. `llm/` is the control plane, `docs/` the data
  plane (canonical
  `llm/governance/adr/0001-llm-control-plane-docs-data-plane.md`).
- Moved, all `git mv` so history follows: `docs/adr/` ->
  `llm/governance/adr/`, `docs/governance-delta.md` ->
  `llm/governance/governance-delta.md`, `llm/plan/` -> `llm/plans/`.
- The belief that `governance-checks.mjs` hard-coded `docs/adr/` and
  `docs/governance-delta.md` was **wrong** — it reads both from the delta's
  `## Repository Layout` block, and its built-in defaults were the `llm/`
  paths all along. That belief is why the delta and every ADR spent three
  weeks in the data plane. Recorded in the delta's layout section so it is
  not re-derived.
- The delta now binds every slot this repo uses, including the two the canon
  has no slot for (`llm/research/`, `llm/application/`) and the
  non-canonical `llm/construction/`, bound to the sprints slot.
- `llm/plan/` renamed to the canonical `llm/plans/`; `llm/construction/`
  deliberately **not** renamed to `llm/sprints/`.
- `experiments/`, `results/`, `writeup/`, `src/`, `notebooks/`, `scripts/`
  and `context/` are data plane and stay where they are — declared in the
  delta rather than relocated. `docs/README.md` is now the data-plane index.
- The two-plane routing rule is installed in `CLAUDE.md` and `AGENTS.md`.
- Verification: `governance-checks.mjs --layout` — 4 of 4 passed, `--layout`
  a real PASS rather than a SKIP. PR #7.

**Counted hours: unchanged — governance housekeeping, not research.**

## 2026-09-17 — The governance check now runs itself, and the stale v0.5 claims are corrected

- **`.github/workflows/ci.yml` added.** Job `governance` runs
  `governance-checks.mjs --layout` on every pull request and every push to
  `main`, with canon cloned into `$RUNNER_TEMP` pinned to agentic-governance
  v0.9.0 (`851a50a0692d4409cbd255e3b3be111d863ae264`). Modelled on
  `agentic-kgcs/.github/workflows/governance-checks.yml`.
- **This was the root finding of the audit.** The delta has declared a
  governance check command since onboarding and nothing ever ran it, so
  "no direct commits to `main`" had no mechanism behind it — and most of the
  recent history on `main` arrived as direct pushes. Canon is cloned
  *outside* the workspace because the checker roots its file scan at
  `git rev-parse --show-toplevel` and would otherwise walk canon's own tree
  as this repo's content; `fetch-depth: 0` because `adr-status` diffs
  against the base ref.
- **`conformance-check.mjs` deliberately left out of CI.** It is a
  submission gate over application content, not repository hygiene, and its
  open failures are content facts — including MEC-02 *Before the deadline*,
  which can never pass again. Requiring it would hold `main` red for reasons
  no commit can fix. Recorded in the delta §Governance Check Command.
- **Stale version claims corrected** — `README.md`, `CONTRIBUTING.md`,
  `activeContext.md` and `systemPatterns.md` each asserted in the present
  tense that this repo is on v0.5. The pin moved to v0.8 in PR #10 and v0.9
  in PR #11; only the delta and `CLAUDE.md` had been updated. Dated history
  (the 2026-09-10 entry above, ADR-0001's v0.2 references, the delta's
  "Revised 2026-09-10 for v0.5") is left exactly as written.
- **`Status:` / `Last updated:` headers added** to `README.md` and
  `CONTRIBUTING.md`, which canon's documentation standards
  (`llm/governance/architecture-governance.md` §Documentation Standards)
  require of every major document.
- `systemPatterns.md` also still claimed branch protection was unavailable
  on this plan "(verified 403)". The repo is public now and the delta had
  already corrected that reading on 2026-09-16; the memory bank had not.
- Verification: `governance-checks.mjs --layout` at the pinned v0.9.0 SHA —
  4 of 4 passed. PR #12.

**Counted hours: unchanged — governance housekeeping, not research.**

## 2026-09-17 (later) — The vendored canon copies are gone (ADR-0007)

- **Deleted six files** that duplicated what the installed
  `governance@agentic-governance` plugin provides:
  `.claude/skills/governance-establish/SKILL.md` (104 lines here vs 538 in
  canon), `.claude/skills/governance-audit/SKILL.md` (86 vs 180), and the
  four executive charters `chief-architect.md` (17 diff lines behind),
  `chief-reviewer.md` (6), `chief-product-officer.md` (**0** — byte-identical)
  and `repository-steward.md` (87).
- **Plugin install verified first.** An earlier attempt to delete these was
  correctly refused because the plugin was not installed. It is now:
  `~/.claude/plugins/marketplaces/agentic-governance`, VERSION `0.9.0`, git
  HEAD `851a50a` (the v0.9.0 tag), providing
  `plugin/skills/{establish,audit,migrate}` and all four charters, with
  `governance@agentic-governance: true` in both the user and the repo
  settings.
- **The reason is drift and unqualified-name ambiguity, not shadowing.** The
  earlier justification claimed shadowing and was wrong: plugin skills are
  namespaced (`governance:establish`), the vendored ones were not
  (`governance-establish`), and both were addressable at once. The real
  problem was that an *unqualified* name resolved to the stale local copy —
  and unqualified is how `CLAUDE.md` named every one of them.
- **The drift was load-bearing, not cosmetic.** Every vendored charter still
  cited `docs/architecture-governance.md`, `docs/review-checklist.md`,
  `docs/l0-fast-track.md` — paths canon abandoned at v0.5. They pointed at
  nothing.
- **Kept:** `.claude/skills/conformance-audit/` (genuinely local, ADR-0003),
  the nine project agents (`paper-agent`, `neel-reviewer`, `latex-agent`,
  `position-paper-agent`, `proposal-agent`, `memory-agent`,
  `knowledge-steward`, `feature-architect`, `review-agent`) and the seven
  `constellize:*` skills.
- **References repointed** — all three inbound references were in
  `CLAUDE.md` (§Agents available, lines 164–170), plus two claims that the
  role charters are "vendored under `.claude/agents/`" in `CLAUDE.md` and the
  delta §Repository Layout, which the deletion makes false. Grepped the
  whole tree; nothing else referred to them.
- Verification: `governance-checks.mjs --layout` at the pinned v0.9.0 SHA —
  4 of 4 passed. ADR-0007. PR #13.

**Counted hours: unchanged — governance housekeeping, not research.**
