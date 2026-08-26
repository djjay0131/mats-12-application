# PLAN — MATS 12.0 Application (Neel Nanda stream)

Status: Active
Owner: Jason (djjay@vt.edu)
Created: 2026-08-22
Hard deadline: **Fri Sept 4, 2026, 11:59pm PT** — submit via
[Airtable form](https://airtable.com/appnMboxg76F1QIDc/pagqu7wWWrUCZkNVI/form)
Extension available to Sept 11: <https://forms.gle/gpceDYrxTUaZBoHA8>

---

## 1. Correction to the working assumption

You planned "20 hours executing + 2 hours writing." **The doc says
otherwise, and it matters.**

Neel counts *"writing up the google doc"* **inside** the 20 hours. The
extra 2 hours are for the **executive summary only**, and during those 2
hours you may not edit the rest of the write-up or write any new
experiment code — only code that makes new graphs from data you already
have.

So the real budget is:

| Bucket | Hours | Counted? |
|---|---|---|
| Experiments, code, analysis, thinking, planning | **~15** | ✅ in the 20 |
| Main write-up (Google Doc) | **~4** | ✅ in the 20 |
| Slack | **~1** | ✅ in the 20 |
| **Executive summary** | **2** | ➕ separate |
| Reading papers *for the project* | ≤5 of the above | ✅ counted |
| General prep, tutorials, GPU/env setup, breaks, waiting on training | ∞ | ❌ not counted |
| Filling in the application form | ∞ | ❌ not counted |

Two rules worth knowing:

- **You may reset the clock.** *"If you decide your project is doomed,
  you're welcome to give up and start a new one, and reset the timer"* —
  as long as the pivot is genuine (old code/findings don't carry over).
  This is what makes the Aug 24 de-risk gate cheap.
- **Track your time.** He encourages Toggl and says you can include a
  screenshot. Do it — it's free credibility on a rule-bound task.

---

## 2. Phases

```
Aug 22 ── Aug 24   SELECT & DE-RISK      (mostly uncounted)
Aug 24             ▲ GATE 1: lock the project (ADR-0002)
Aug 25 ── Aug 31   EXECUTE ~15h          (counted h1–h15)
Aug 28             ▲ GATE 2: weekly review / pivot-or-commit
Sep  1 ── Sep  2   WRITE-UP ~4h          (counted h16–h20)
Sep  2             ▲ CLOCK STOPS
Sep  3             EXEC SUMMARY 2h       (+2h budget)
Sep  4             SUBMIT (target: noon ET, not 11:59pm PT)
```

---

## 2b. Go/no-go verified — C2 is live

The gating fact for candidate C2 was checked against the HuggingFace Hub
on 2026-08-22. **GO, and better than hoped.**

All four Think-branch stage endpoints are separate public repos, Apache-2.0,
~14.6 GB each:

| # | Stage | Repo |
|---|---|---|
| 0 | Base | `allenai/Olmo-3-1025-7B` |
| 1 | SFT | `allenai/Olmo-3-7B-Think-SFT` |
| 2 | DPO | `allenai/Olmo-3-7B-Think-DPO` |
| 3 | RLVR (final) | `allenai/Olmo-3-7B-Think` |

**The upgrade:** intermediate checkpoints exist as git *branches*, not just
endpoints — 55 RL checkpoints on `Olmo-3-7B-Think` (`step_0025` …
`step_1375`, every 25 steps) and 43 SFT checkpoints on `Think-SFT`
(`step1000` … `step43000`). Load with
`from_pretrained(..., revision="step_0700")`. That turns the headline
figure from a four-point bar chart into **a continuous faithfulness curve
across RLVR training** — which is a far better executive-summary graph.

The Dolci post-training datasets are all public (SFT 2.3M rows, DPO 150k
pairs, RLVR 102k prompts), plus pre-computed completion sets at the SFT and
DPO checkpoints over the RL prompts — that may save a large slice of
inference budget.

Three gotchas, all recorded before they cost time:

1. **`Think-SFT` ships a different tokenizer** (4.8 MB vs 7.1 MB
   `tokenizer.json`) and **no chat template** — it ships a `fix_tokens.py`
   repair script instead. Verify `<think>` / `</think>` tokenize identically
   at all four stages *before* comparing anything.
2. **Branch naming is inconsistent** — RL uses `step_0700`, SFT uses
   `step20000`. The SFT model card's own example (`step_11000`) 404s.
3. **`Think-DPO` duplicates weights as `.bin`** — naive `snapshot_download`
   pulls 29 GB instead of 14.6. Use
   `allow_patterns=["*.safetensors*","*.json","*.txt","*.jinja"]`.

**Do not make OlmoTrace load-bearing.** It is hosted-only, attached to the
32B, and the public infini-gram index list tops out at OLMo-2 / Dolma-v1.7.
Use the Dolci datasets for the "which data caused it" follow-up instead.

Also available if wanted: the full Instruct lineage at the same four stages
as a control arm, and six `Olmo-3-7B-RL-Zero-*` models trained straight
from base with no SFT/DPO — a clean "does the SFT stage matter" ablation
Ai2 has already run.

⚠️ There is **no** `Olmo-3.1-7B-Think`. The Dec 2025 refresh covers 32B
only; the 7B Think lineage is the original Nov 2025 line.

---

## 3. Day by day

| Date | Day | Work | Hours | Counted |
|---|---|---|---|---|
| **Aug 22** | Sat | Repo + governance up. Read Model Forensics (2606.26071), Thought Branches, BONAFIDE, the Goodfire eval-awareness post. Skim the candidate list. | — | ❌ prep |
| **Aug 23** | Sun | ~~Verify Olmo 3 lineage~~ ✅ **done, GO**. ARC allocation + env: TransformerBridge, vLLM/nnsight, pull the 4 stage checkpoints (~58 GB), verify `<think>` tokenizes identically at all four, smoke test one prompt. | — | ❌ setup |
| **Aug 24** | Mon | **2h de-risk pilot** on the top candidate: does the phenomenon replicate in *my* model, *my* dataset, *my* prompts? **▲ GATE 1.** Write ADR-0002. | 2 | ✅ h1–2 |
| **Aug 25** | Tue | Build the experimental harness. Generation + logging + one metric end-to-end on 20 examples. | 3 | ✅ h3–5 |
| **Aug 26** | Wed | Main run #1. **Then stop and read 30 raw rollouts by hand.** Hand-label a validation subset for any LLM-judge step. | 3 | ✅ h6–8 |
| **Aug 27** | Thu | Baselines and controls: random-vector / random-hint control, "just ask the model", second faithfulness metric. | 3 | ✅ h9–11 |
| **Aug 28** | Fri | **▲ GATE 2 — weekly review.** No new experiments. What's the claim? What's the evidence? What would make it false? Commit or pivot. (Pivot here = clock reset, still 7 days left.) | 0.5 | ✅ h11.5 |
| **Aug 29** | Sat | Main run #2 — second model / second condition. The single-model claim is the #1 weakness in the 2026 literature; not having it is the cheapest differentiator. | 3 | ✅ h12–14 |
| **Aug 30** | Sun | Red-team your own result. List 3 ways it could be false; test the cheapest 2. Freeze data. | 1.5 | ✅ h15–16 |
| **Aug 31** | Mon | Figures only. One graph per claim. Nothing new. | 1 | ✅ h17 |
| **Sep 1** | Tue | Write-up draft: narrative first, then evidence. Not chronological. | 2 | ✅ h18–19 |
| **Sep 2** | Wed | Write-up finish + randomly-selected raw examples appendix. Run `--gate WRITEUP`. **CLOCK STOPS AT h20.** | 1 | ✅ h20 |
| **Sep 3** | Thu | **Executive summary, 2h.** ≤600 words, ≤3 pages, graphs included. Then the Airtable form (uncounted). | +2 | ➕ |
| **Sep 4** | Fri | **Run `conformance-audit --gate SUBMIT`.** All three layers: checker, rubric ≥28/30, neel-reviewer. Link sharing set to *anyone with the link*, Toggl screenshot attached, form answers in your own voice. **Submit by noon ET.** | — | ❌ |

**Total counted: 20.0h. Total elapsed: 13 days.** Aug 28 and the Sep 4
morning are deliberate slack.

---

## 4. Gates

Every gate runs the conformance audit before anything else:

```
node scripts/conformance-check.mjs --gate <SELECT|EXECUTE|WRITEUP|SUBMIT>
```

or, for all three layers (checker + 15-criterion rubric + adversarial
`neel-reviewer` read), invoke the `conformance-audit` skill. **No gate
advances with an open blocker.** Requirements and their source quotes:
`llm/application/conformance-register.md` — 121 requirements, 38 of them
individually disqualifying. Rationale: ADR-0003.

### GATE 1 — Aug 24, end of the 2h pilot
Proceed only if **all** are true:
- The phenomenon replicates in my setup (my model, my prompts, my data).
- I can state the claim in one sentence.
- I can name the graph that would carry the executive summary.

If not → switch to the backup candidate and **reset the clock**. There are
still 10 days.

Plus, mechanically: `--gate SELECT` green (subject model is current, project
is not in an area he has left) and ADR-0002 moved to **Accepted**. The
checker refuses to pass `--gate EXECUTE` while ADR-0002 is still Proposed —
that is deliberate. Counted hours do not start against an unlocked project.

### GATE 2 — Aug 28, weekly review
Neel's own prompts:
- What is my goal right now? What progress have I made toward it?
- What's consumed the most time? What's blocked me?
- What am I currently confused about? Am I missing something?
- **Have I learned anything in the last 30 minutes?**

Plus, mechanically: `--gate EXECUTE` green — hours ledger current, reading
≤5h, and every result so far has a row in the controls ledger.

Pivot here is still survivable. After Aug 29, it is not.

### GATE 3 — Sep 2, clock stop
`--gate WRITEUP` green: every number traces to `results/canonical.json`,
every results table has a baseline column, every claim is typed, the
structure is narrative rather than chronological, and the limitations
section exists.

### GATE 4 — Sep 4, before submitting
Full `conformance-audit --gate SUBMIT`. Rubric ≥28/30 with no zeros.
`neel-reviewer` verdict recorded. Exec summary ≤600 words with graphs,
sharing set to *anyone with the link*, time screenshot attached.

---

## 5. Standing rules for the execution phase

Drawn from the doc's "Common Mistakes" — these are the failure modes to
actively defend against.

1. **Look at your data.** Read raw rollouts. Talk to the model. If
   something is weird, look closer. He calls this out as neglected even by
   professional researchers.
2. **Check the phenomenon replicates before building on it.** If the
   effect isn't there in your setup, everything downstream is noise.
3. **Take the cheap control every time.** Random vector, random hint,
   "just ask the model", a linear probe. He lists "failing to compare to
   baselines" as disqualifying.
4. **Never report one faithfulness number.** BONAFIDE showed most metrics
   perform near chance. Two metrics and their disagreement is the honest
   unit.
5. **Simple first.** Prompting and reading the CoT before anything fancy.
   His own team's example: *"we started with the obvious things ... and,
   er, it just worked, and we stopped there."*
6. **Verify every agent-produced result.** *"if your write-up contains key
   results you clearly never verified, or don't understand, that's
   disqualifying."* Use Claude Code aggressively; re-derive every number
   that goes in the write-up.
7. **Timer every 1–2 hours.** Zoom out: rabbit hole, or progress?
8. **Negative results are fine. Overclaiming is not.** Plausible over
   ambitious.
9. **Randomly selected examples, never cherry-picked.** He names
   cherry-picking as a major red flag.
10. **Write the summary in your own voice.** *"Answers that read like they
    were written by an LLM are a significant negative signal — I see
    hundreds of them, and they blur together."*

---

## 6. Deliverables

| Artifact | Where | Due |
|---|---|---|
| ADR-0002: project selection | `docs/adr/0002-*.md` | Aug 24 |
| Experiment code | `src/`, `notebooks/` | rolling |
| Raw results + figures | `results/` | Aug 30 |
| Main write-up (Google Doc, link-shareable) | `writeup/main.md` → GDoc | Sep 2 |
| Executive summary (≤600 words, ≤3pp, with graphs) | first 1–3 pp of the same GDoc | Sep 3 |
| Toggl time screenshot | attach to GDoc | Sep 3 |
| Airtable form answers | — | Sep 4 |

**Form answers are read first and used as a preliminary filter.** He does
not read every write-up. Budget real care there even though it's
uncounted — including the named question: *"What are 1-3 pieces of
evidence that you'd be able to do good research in the program?"*

---

## 7. What success looks like

His own bar: *"My ideal application is one that teaches me something new."*
And: *"If I understand what you're claiming, what evidence you're
providing, and think that evidence supports your conclusion, that instantly
puts you in the top 20% of applicants."*

Not a big claim. One claim, defended, with the holes named.
