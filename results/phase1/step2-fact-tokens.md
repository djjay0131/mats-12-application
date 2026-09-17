# Phase 1, step 2 — fact-token probes

Status: **agent-unverified**. Numbers only; interpretation is Jason's.
Pre-registration: `llm/memory_bank/research-learning-log.md`, entry "Phase 1,
steps 2–5" (commit `7c55733`), committed before the job was queued.

## Provenance

| item | value |
|---|---|
| job | Falcon **587865**, commit `7c55733`, NVIDIA L40S; smoke pass (2 records/split) deleted; full run exit 0; log `results/slurm-logs/phase1-step2-587865.out` |
| run | `results/runs/20260917T202900Z-phase1-step2-fact-tokens` (`experiments/phase1/step2_fact_tokens.py --residual-dir /scratch/djjay/mats12/phase1/residuals`) |
| outputs | `outputs/step2-fact-tokens.json` (summaries, arm 3 per layer), `outputs/step2-records.json.gz` (per-record two-way scores at every lens layer, model preference per position) |
| residuals (outside repo) | `/scratch/djjay/mats12/phase1/residuals/{dev,heldout,heldout2}.pt` — [n, 10 positions, 32 blocks, 2560] fp16; read by step 5 |
| tables / figure | `experiments/phase1/step2_report.py`; `results/figures/phase1-step2-fact-tokens.png` via `figstyle.save_figure` (rendered, not visually inspected by the agent) |
| data | dev 40, heldout 160, heldout2 240 records; combined held-out = 400 records = 800 fact tokens per token type |

Fact-token resolution failures: **0 / 440 records** (also checked with the tokenizer alone before queueing). Positions per record: prequery, relcomp, qmark, final, person_q, city_q, period_q, person_d, city_d, period_d; all distinct in every record.

Example (dev `real-zero-000-AAB`, T1, 30 tokens): `person_q`=3 " Helen", `city_q`=6 " Prague", `period_q`=7 ".", `person_d`=8 " Laura", `city_d`=11 " Athens", `period_d`=12 ".", `prequery`=20 ".", `relcomp`=26 " lives", `qmark`=27, `final`=29 ":".

## Arm 3 (difference-in-means; fit on all of dev, pooled over sentence roles; applied unchanged)

Two-way accuracy (correct class centroid vs alternative) on the combined held-out. `n_sc` = records scorable (both classes present in the dev fit); PERSON classes are name tokens and dev covers only some of the 24 names, so PERSON cells are scorable on 352/800 tokens. ctrl = label-permutation control. Chance = 0.5.

| cell (token → target) | L30 acc | L30 ctrl | n_sc | dev-selected layer | acc there | max over blocks | dev LOPO at L30 (n) | R2.1 |
|---|---|---|---|---|---|---|---|---|
| prequery → CITY | 0.495 | 0.537 | 400 | L30 | 0.495 | L23 0.525 | 0.525 (40) | no |
| relcomp → CITY | 0.515 | 0.520 | 400 | L31 | 0.537 | L16 0.542 | 0.500 (40) | no |
| qmark → CITY | **0.725** | 0.492 | 400 | L31 | 0.725 | L29 0.725 | 0.700 (40) | readable |
| final → CITY | **0.660** | 0.507 | 400 | L31 | 0.682 | L31 0.682 | 0.625 (40) | readable (gap 0.153) |
| city → PERSON | 0.528 | 0.477 | 352 | L31 | 0.517 | L18 0.537 | 0.531 (32) | no |
| person → CITY | 0.502 | 0.476 | 800 | L29 | 0.506 | L4 0.526 | 0.512 (80) | no (predicted: causal order) |
| period → PERSON | 0.608 | 0.474 | 352 | L31 | 0.642 | L24 0.679 | 0.594 (32) | no (gap 0.134, acc < 0.65) |
| period → CITY | **0.664** | 0.502 | 800 | L31 | 0.644 | **L0 0.994** | 0.700 (80) | readable (gap 0.162) |

Per split at L30: qmark → CITY heldout 0.731 / heldout2 0.721 (ctrl 0.506 / 0.483); period → CITY 0.653 / 0.671 (ctrl 0.509 / 0.498); period → PERSON 0.606 / 0.609 (n 160/320, 192/480); city → PERSON 0.531 / 0.526; person → CITY 0.500 / 0.504; relcomp → CITY 0.525 / 0.508; final → CITY 0.725 / 0.617. Application values reproduced: relcomp 0.525, qmark 0.731 on the original held-out.

Layer curve for period → CITY (combined, arm 3): 0.994 at L0, falling through the blocks to 0.664 at L30 (full curve in the JSON and the figure).

## J-Lens and logit lens at the fact tokens (pooled over roles; combined held-out, n = 800)

Direction frac = correct entity ranked above the alternative in the lens logits. L30 is the frozen reporting layer; the max over lens layers 0..30 is reported as a curve, not selected on.

| arm | token → target | L30 frac | L30 ctrl | R2.2 at L30 | max over layers (ctrl there) |
|---|---|---|---|---|---|
| J-Lens | city → PERSON | 0.537 | 0.500 | — (R2.1 not cleared) | L27 0.625 (0.525) |
| J-Lens | person → CITY | 0.295 | 0.520 | — | L2 0.499 (0.487) |
| J-Lens | period → PERSON | 0.501 | 0.511 | — | L10 0.729 (0.507) |
| J-Lens | period → CITY | 0.559 | 0.507 | **does not read (gap 0.05)** | **L9 0.871** (0.512) |
| logit lens | city → PERSON | 0.519 | 0.492 | — | L27 0.585 (0.495) |
| logit lens | person → CITY | 0.341 | 0.491 | — | L2 0.491 (0.479) |
| logit lens | period → PERSON | 0.551 | 0.506 | — | L26 0.579 (0.510) |
| logit lens | period → CITY | 0.588 | 0.517 | does not read (gap 0.07) | L25 0.704 (0.491) |

By sentence role at L30 (J-Lens): city_q → PERSON 0.540 (median rank of the correct name 2,591), city_d 0.535 (2,499); period_q → PERSON 0.502 (median rank **1**), period_d 0.500 (1); period_q → CITY 0.557 (13), period_d 0.560 (13); person_q → CITY 0.287 (16,191), person_d 0.302 (15,535). Logit lens: period → PERSON median rank 7–8, period → CITY 31–35; person → CITY 0.335–0.347.

Raw-data observation, no interpretation: at a period token the next prompt token is a name (after the first person sentence) or a city (after the second), and both names / both cities sit at ranks 0–1 / 13 in the J-Lens readout there; at a person token the readout ranks the other city above this sentence's city in ~70% of records (the sentence's own city is to the right of the token).

## Query anchors (combined held-out, frozen layers) — consistency with step 1

J-Lens: prequery 0.500 / ctrl 0.522 / rank 382; relcomp **0.752** / 0.507 / 129; qmark 0.665 / 0.497 / 93; final 0.948 / 0.520 / 21. Logit lens: relcomp 0.693 / 0.510 / 380; qmark 0.743 / 0.495 / 99. Step 1 combined values were 0.752 / 0.505 / 129 and 0.667 / 0.495 / 93: identical to one record (bf16 run-to-run; the lens logits here are computed from one recorded forward pass rather than through `lens.apply`, same transport and unembed).

## Pre-registered rules — which branch fired

- **R2.1 (linearly readable: arm 3 at L30 ≥ 0.65 and ≥ control + 0.15, combined held-out):** cleared by **period → CITY** (0.664 vs 0.502), by qmark → CITY (0.725 vs 0.492) and by final → CITY (0.660 vs 0.507, gap 0.153). Not cleared by city → PERSON (0.528), period → PERSON (0.608, gap 0.134), person → CITY (0.502, as predicted from causal order), relcomp → CITY (0.515) or prequery → CITY (0.495). So the branch "not linearly readable at any position we probed" did **not** fire; the pairing's city side is linearly present at the period of the person sentence (strongly at early blocks, weakly by L30).
- **R2.2 (J-Lens reads it there, at L30, gap ≥ 0.15):** at the period, J-Lens 0.559 vs 0.507 → **does not read it at L30**; logit lens 0.588 vs 0.517 → does not. The layer curve, reported not selected: J-Lens reaches 0.871 at L9 (control 0.512) at the period → CITY cell.
- Causal-order note held: person → CITY at chance (arm 3 0.502) and below chance for the lenses (0.29–0.34).

## Predictions (agent's) — scored

| prediction | observed | hit? |
|---|---|---|
| city → PERSON readable ≥ 0.85 at most layers | arm 3 0.528 at L30, max 0.537 (n_sc 352) | **no** |
| period → CITY ≥ 0.9 | 0.664 at L30; 0.994 at L0 | no at L30, yes at L0 |
| period → PERSON ≥ 0.8 | 0.608 (n_sc 352) | **no** |
| person → CITY at chance | 0.502 | yes |
| J-Lens at period reads CITY above control | 0.559 vs 0.507 at L30 (0.871 at L9) | no at L30 |
| J-Lens PERSON above control at city token | 0.537 vs 0.500 | no |

## Deviations / caveats

1. PERSON-target arm 3 cells are scorable on 352/800 tokens (dev's 10 pairs use 15 of the 24 names); their accuracies are on the scorable subset. Step 5 (fit on the combined held-out, LOPO) does not have this limit.
2. Arm 3's dev-selected layer is L31 (the last block) for most cells; L30 is the frozen reporting layer and both are given.
3. The lens logits were computed from one recorded forward pass per record (`lens.transport` + `lm.unembed` on stored block outputs) rather than through `lens.apply`; the query-anchor numbers match step 1 to one record.

## Three numbers for Jason to hand-check

1. arm 3 period → CITY combined at L30 = **0.664**, ctrl 0.502, n_scored 800 — `outputs/step2-fact-tokens.json`, `arm3["period/CITY"].per_layer["30"].combined.acc` / `.ctrl_acc`.
2. J-Lens period → CITY pooled at L30 = **0.559** (ctrl 0.507) and at L9 = **0.871** — same file, `lens_summary_pooled["combined/jlens/period/CITY"][30]` and `[9]`.
3. arm 3 period → CITY at L0 = **0.994** — `arm3["period/CITY"].per_layer["0"].combined.acc`.
