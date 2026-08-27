# Project Brief

Last updated: 2026-08-26

## Goal

Win a place in MATS 12.0, Neel Nanda's mech interp stream (Winter 2026–27).
The gate is one deliverable: ~16–20 hours of research progress on an AI
safety problem, written up, with a 1–3 page executive summary. Due
**2026-09-04 23:59 PT**.

## The project

**J-Lens relational binding** (ADR-0005):

> When two prompts contain the same entities and concepts but assign them
> different relational roles, does J-Lens identify the correct hidden
> intermediate — and does changing that representation causally change the
> model's answer?

Primarily a red-team evaluation of J-Lens, with a model-biology question as
the test case. It targets a limitation the J-Lens paper names itself: a
readout can list the right concepts without showing which entity fills which
role.

## Scope

**Passive-primary.** H1, H2 and H4 are the deliverable. The causal arm (H3)
is contingent on V2 clearing blocker B2. Declared in advance rather than
discovered mid-sprint.

Claims are bounded to a specified layer band and token position in a
controlled two-hop task. This is **not** a claim about reading the model's
thoughts; language to that effect is a write-up defect.

Out of scope: fitting a lens, SAE research, publishing a paper, reusable
infrastructure — anything that does not land in the Sept 4 submission.

## Success criteria

His stated bar, which is lower and more specific than it first appears:

> "If I understand what you're claiming, what evidence you're providing, and
> think that evidence supports your conclusion, that instantly puts you in
> the top 20% of applicants."

One claim, defended, with the holes named. A clean null on H2 is a result: it
would quantify the paper's own stated limitation. The project fails only if
the pipeline is never validated and no interpretable comparison is produced.

## Constraints

- **20 counted hours** plus 2 for the executive summary. The main write-up
  counts inside the 20.
- **9 days elapsed** as of 2026-08-26.
- Compute is not binding — the job peaks at 8.51 GB on a 47.7 GB L40S. The
  binding constraints are hours and taste.
- J-Lens is a crowded field this cycle; the relational-binding framing has to
  carry the differentiation, and it must be obvious in the first paragraph.

## The program

Exploration phase Sept 28 – Oct 30 (online, ~34 scholars, $4.2K). Research
phase Jan 19 – Apr 10 2027 (Berkeley, in-person, ~8 scholars, $19.2K plus
housing). Most research-phase scholars publish co-first-author papers.
