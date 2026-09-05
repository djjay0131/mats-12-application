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
- **Time ledger** brought current: 19.8 / 20 counted (7.1 verified,
  12.7 estimated). Executive-summary hours are Jason's to enter.

**Counted hours: 19.8 / 20.**
