# Backlog

Project: J-Lens relational binding (ADR-0005). Passive-primary scope.

| # | Item | Phase | Status |
|---|---|---|---|
| 1 | ~~Verify a public J-Lens checkpoint works on a current model~~ | phase-0-select | **Done — ARC job 550088, COMPAT PASS** |
| 2 | ~~Score C6 and decide between candidates~~ | phase-0-select | **Done — ADR-0005** |
| 3 | V1: reproduce an official example; **exercise the logit-lens switch** | phase-1-execute | Open (1 counted hour) |
| 4 | V2: settle B2 — faithful J-space reconstruction, or declare causal unavailable | phase-1-execute | Blocked on 3 (1 counted hour) |
| 5 | V3: binding-identifiability audit on 8–12 dev pairs | phase-1-execute | Blocked on 4 (1 counted hour) |
| 6 | Build 4–5 relational templates; 10 dev pairs | phase-1-execute | Blocked on 5 |
| 7 | Generate 50 pairs, seeded; tokenize targets; measure eligibility (≥80%) | phase-1-execute | Blocked on 6 |
| 8 | Instrument readout at final prompt token over the fixed layer band | phase-1-execute | Blocked on 7 |
| 9 | Development controls; complete rival-hypothesis table | phase-1-execute | Blocked on 8 |
| 10 | **Hour 7 gate: freeze hypotheses and metrics** before any held-out result | phase-1-execute | Blocked on 9 |
| 11 | Held-out passive run; no per-example inspection during the run | phase-1-execute | Blocked on 10 |
| 12 | Primary result + CIs → `fig_binding_accuracy`, `fig_layerwise_margin` | phase-1-execute | Blocked on 11 |
| 13 | Falsification controls across held-out → `fig_controls_panel` | phase-1-execute | Blocked on 12 |
| 14 | Causal arm, **only if V2 cleared** | phase-1-execute | Contingent |
| 15 | Robustness and seeded error analysis | phase-1-execute | Blocked on 13 |
| 16 | Delete example rows from the three ledgers; fill with real entries | phase-1-execute | Open |
| 17 | Write-up: methods and results first, negatives included | phase-2-writeup | Blocked on 15 |
| 18 | Introduction, discussion, limitations; audit against preregistration | phase-2-writeup | Blocked on 17 |
| 19 | Executive summary (+2h budget) — **Jason writes the prose** | phase-3-submit | Blocked on 18 |
| 20 | Airtable form answers — **Jason writes these** | phase-3-submit | Blocked on 19 |
| 21 | `conformance-audit --gate SUBMIT`: checker + rubric ≥28/30 + neel-reviewer | phase-3-submit | Blocked on 20 |
| 22 | Submit | phase-3-submit | Blocked on 21 |
