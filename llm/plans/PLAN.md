# PLAN — MATS 12.0 Application (Neel Nanda stream)

Status: Active
Owner: Jason (djjay@vt.edu)
Last updated: 2026-08-26
Project: **J-Lens relational binding** (ADR-0005)
Hard deadline: **Fri Sept 4, 2026, 11:59pm PT** —
[Airtable form](https://airtable.com/appnMboxg76F1QIDc/pagqu7wWWrUCZkNVI/form)
Extension available to Sept 11: <https://forms.gle/gpceDYrxTUaZBoHA8>

---

## 1. The project

> When two prompts contain the same entities and concepts but assign them
> different relational roles, does J-Lens identify the correct hidden
> intermediate — and does changing that representation causally change the
> model's answer?

Design of record: `llm/plan/jlens-relational-binding-experiment-design.md`.
Selection and scope: `docs/adr/0005-accept-jlens-relational-binding.md`.
Why this over the alternatives: `llm/plan/project-candidates.md` (C6, 24/25).

**Scope is passive-primary.** H1, H2 and H4 are the deliverable. The causal
arm (H3) is contingent on V2 clearing blocker B2 — the reference
implementation ships no sparse non-negative J-space reconstruction. Do not
approximate it with a top-token projection; that is the design's own FAIL
condition.

**Substrate, verified on ARC (job 550088, L40S):** `Qwen/Qwen3.5-4B` plus
`neuronpedia/jacobian-lens` rev `qwen-n1000`, commit `16a01f3`.
`COMPAT_ASSERTIONS: PASS`, 32/32 reference tests, peak GPU 8.51 GB of 47.7.
Full detail: `results/design-verification/environment-manifest.md`.

---

## 2. The time budget

The write-up counts **inside** the 20 hours. The extra 2 hours are for the
executive summary only, and during them you may not edit the rest of the
write-up or write new experiment code — only code that makes new graphs from
data you already have.

| Bucket | Hours | Counted? |
|---|---|---|
| Experiments, code, analysis, thinking, planning | ~16 | ✅ in the 20 |
| Main write-up | ~4 | ✅ in the 20 |
| **Executive summary** | **2** | ➕ separate |
| Project-specific reading | ≤5 of the above | ✅ counted |
| Setup, general prep, GPU/env build, queue waits, breaks | ∞ | ❌ not counted |
| Filling in the application form | ∞ | ❌ not counted |

**Clock state: 0.0 / 20.** ADR-0005 §3 rules that everything through
2026-08-26 — ARC access, environment build, model and lens staging,
compatibility assertions, and the design documents — is ideation and setup.
No reset is needed because ADR-0002 was never executed against. Log hours in
`llm/memory_bank/time-log.md`; track with Toggl and attach the screenshot.

---

## 3. Schedule — 9 days

| Date | Day | Work | Hrs | Cum |
|---|---|---|---|---|
| **Aug 26** | Wed | **V1** — reproduce an official J-Lens example and **exercise the logit-lens switch** (the one part of ADR-0004 condition 1 setup did not close) | 1 | 1 |
| **Aug 27** | Thu | **V2** — settle B2: is a faithful J-space reconstruction reproducible inside the hour, or is causal work declared unavailable? **V3** — binding-identifiability audit on 8–12 dev pairs | 2 | 3 |
| **Aug 28** | Fri | 4–5 relational templates; 10 dev pairs by hand; generate 50 seeded pairs; tokenize targets; measure behavioural eligibility (target ≥80%) | 3 | 6 |
| **Aug 29** | Sat | Instrument activation capture at the final prompt token across the fixed layer band; run dev pairs through J-Lens and logit lens; verify token/position alignment on three examples by hand | 3 | 9 |
| **Aug 30** | Sun | Development controls (deletion, truncation, permutation); complete the rival-hypothesis table; **▲ Hour-7 gate: freeze hypotheses, metrics and claim boundaries** | 2 | 11 |
| **Aug 31** | Mon | Held-out run on all eligible pairs — no per-example inspection during the run. Primary result plus bootstrap CIs; figures 1 and 2 | 3 | 14 |
| **Sep 1** | Tue | Falsification controls across held-out; robustness by template; seeded error taxonomy | 2 | 16 |
| **Sep 2** | Wed | Write-up: methods and results first, negatives included | 3 | 19 |
| **Sep 3** | Thu | Finish write-up — **▲ clock stops at h20**. Then executive summary (+2h budget). Airtable answers (uncounted) | 1 | 20 |
| **Sep 4** | Fri | `conformance-audit --gate SUBMIT`; sharing set to *anyone with the link*; Toggl screenshot attached. **Submit by noon ET** | — | — |

**Counted total: 20.0.** There is no slack for a second false start. The two
hard edges are Sunday's freeze — after it the held-out analysis does not
change — and Thursday's clock stop, which is what makes the +2 exec-summary
hours legitimate.

---

## 4. Gates

Every gate runs the conformance audit first:

```
node scripts/conformance-check.mjs --gate <SELECT|EXECUTE|WRITEUP|SUBMIT>
```

or the `conformance-audit` skill for all three layers (checker, the
15-criterion rubric, and the adversarial `neel-reviewer` read). **No gate
advances with an open blocker.** Requirements and their source quotes:
`llm/application/conformance-register.md` — 121 requirements, 38 of them
individually disqualifying. Rationale: ADR-0003.

- **V1 (Aug 26)** — an official example reproduces; the logit-lens switch
  produces different, reproducible output. If not, the pipeline is not
  validated and nothing downstream means anything.
- **V2 (Aug 27)** — B2 settled either way, in one hour. Box it. Taking the
  passive-only path is a scope reduction, not a failure.
- **V3 (Aug 27)** — the metric tests *binding*, not merely whether the model
  already selected the correct intermediate. If it cannot distinguish those,
  the dataset design changes before any held-out work.
- **Hour-7 freeze (Aug 30)** — hypotheses, primary metric and layer band
  frozen before any held-out result is examined. Development pairs are for
  debugging and layer selection; the 40 held-out pairs are never tuned on.
- **Clock stop (Sep 3)** — `--gate WRITEUP` green: every number traces to
  `results/canonical.json`, every results table carries a baseline column,
  every claim is typed, structure is narrative rather than chronological.
- **Submit (Sep 4)** — full audit, rubric ≥28/30 with no zeros,
  `neel-reviewer` verdict recorded.

---

## 5. Standing rules

From the doc's "Common Mistakes" — the failure modes to actively defend
against.

1. **Look at your data.** Read raw rollouts. If something is weird, look
   closer. He names this as neglected even by professional researchers.
2. **Check the phenomenon replicates before building on it.** If the effect
   is not there in your setup, everything downstream is noise.
3. **Take the cheap control every time.** Eight are specified in the design;
   log each in `llm/application/controls-ledger.md` with its result.
4. **Simple first.** Prompting and reading the output before anything fancy.
5. **Verify every agent-produced result.** Re-derive by a path that does not
   share the original pipeline's code, and record it in
   `llm/application/verification-ledger.md`. Unverified agent results are
   disqualifying.
6. **Timer every 1–2 hours.** Rabbit hole, or progress?
7. **Negative results are fine. Overclaiming is not.** A clean null on H2
   substantiates the paper's own stated limitation.
8. **Randomly selected examples with a recorded seed** — never cherry-picked,
   unless the claim is explicitly typed `existence-proof`.
9. **Write the exec summary and form answers in your own voice.** LLM-voiced
   applications are a stated negative signal.
10. **Claim only what was measured** — a specified layer band and token
    position in a controlled two-hop task. Not "reading the model's thoughts."

---

## 6. Deliverables

| Artifact | Where | Due |
|---|---|---|
| V1/V2/V3 outcomes | `results/design-verification/` | Aug 27 |
| Dataset (dev + held-out, seeded) | `results/` | Aug 28 |
| Experiment code | `src/`, `notebooks/` | rolling |
| Figures, registered with claim ids | `results/figures/` + `FIGURE-REGISTRY.md` | rolling |
| Main write-up | `writeup/main.md` → `writeup/mats12-report.docx` | Sep 2 |
| Executive summary (≤600 words, ≤3pp, graphs) | `writeup/exec-summary.md`, first in the doc | Sep 3 |
| Toggl screenshot | attached to the doc | Sep 3 |
| Airtable form answers | — | Sep 4 |

Build the report with `./scripts/build-report.sh [--pdf]`. Author the
markdown; the `.docx` is a build artifact and the next build overwrites it.

**The form answers are read first and used as a preliminary filter.** He
does not read every write-up. Budget real care there even though it is
uncounted.

---

## 7. What success looks like

> "If I understand what you're claiming, what evidence you're providing, and
> think that evidence supports your conclusion, that instantly puts you in
> the top 20% of applicants."

One claim, defended, with the holes named.
