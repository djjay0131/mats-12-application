---
name: conformance-audit
description: Run the full MATS application conformance gate - the mechanical checker, the human rubric, and an adversarial Neel review - and produce a go/no-go with a blocker list. Use before advancing a project gate (SELECT, EXECUTE, WRITEUP, SUBMIT) and always before submitting.
argument-hint: "[gate: SELECT|EXECUTE|WRITEUP|SUBMIT]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

# conformance-audit

Gate the MATS 12.0 application. Nothing advances past a gate with an open
blocker.

The requirement source of truth is
`docs/application/conformance-register.md` — 121 requirements extracted
verbatim from Neel's instructions, classed BLOCKER / SCORED / MECHANIC /
ADVICE. This skill checks them in three layers because no single layer can
cover them all.

## Steps

1. **Mechanical layer.** Run:
   ```
   node scripts/conformance-check.mjs --gate <GATE>
   ```
   Report every FAIL and WARN with its requirement ID. FAILs at or before
   the named gate are blocking. Do not proceed past this step with an open
   FAIL — fix, or record an explicit accepted-risk in an ADR.

2. **Ledger integrity.** Confirm the three ledgers are real, not
   aspirational:
   - `docs/application/claims-register.md` — every claim typed; no
     `existence-proof` tag carrying a general claim
   - `docs/application/controls-ledger.md` — a control actually *run* per
     claim, with its result
   - `docs/application/verification-ledger.md` — every headline number
     independently re-derived, by a path that does not share the original
     pipeline's code, with a name and a date
   Example rows shipped with the templates must be deleted, not edited
   around. Flag any row containing "TODO", "pending", or the word
   "example".

3. **Human rubric.** Walk `docs/application/selection-rubric.md`. Score
   each of the 15 green-flag criteria 0/1/2 and confirm every red flag is
   NO. **28+/30 before submitting; any 0 is a blocker.** These are the
   judgement criteria the script cannot reach — clarity, taste, skepticism,
   prioritisation. Do not let the script's green tick substitute for them.

4. **Adversarial read.** Launch the `neel-reviewer` agent over
   `writeup/exec-summary.md` and `writeup/main.md`. Its five passes
   (exclusion, illusion-of-transparency, red-team, simplicity, taste) are
   the closest thing available to the real review. Treat its
   UNADDRESSED FAILURE MODES list as work, not commentary — Neel says
   discovering you already checked his objection is "a really positive
   sign".

5. **Gate-specific extras.**
   - `SELECT` — is ADR-0002 Accepted? Did the de-risk pilot show the
     phenomenon replicates *in this setup*? Can the claim be said in one
     sentence, and can you name the graph that carries the exec summary?
   - `EXECUTE` — hours ledger current; reading ≤5h; every new result has a
     control logged the same day.
   - `WRITEUP` — every number traces to `results/canonical.json`;
     structure is narrative, not chronological; limitations section exists
     and is honest.
   - `SUBMIT` — exec summary ≤600 words with graphs; doc sharing set to
     *anyone with the link*; time screenshot attached; form answers written
     in Jason's own voice, **not drafted by an agent**.

6. **Report.** Emit:
   ```
   GATE: <name>   GO / NO-GO
   Blockers open: n     Warnings: n     Rubric: nn/30
   [blocker list with requirement IDs]
   [the single highest-value fix]
   ```

## Standing rule

Never write the executive summary or the application-form answers.

> "Please do not just submit raw LLM output for the application form or
> executive summary. Write these yourself, in your own voice … Answers that
> read like they were written by an LLM are a significant negative signal —
> I see hundreds of them, and they blur together."

Diagnose, structure, make figures. The prose in those two artifacts is
Jason's.
