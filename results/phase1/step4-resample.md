# Phase 1, step 4 — resample control

Status: **agent-unverified**. Numbers only; interpretation is Jason's.
Pre-registration: `llm/memory_bank/research-learning-log.md`, entry "Phase 1,
steps 2–5" (commit `7c55733`), committed before the job was queued.

## Provenance

| item | value |
|---|---|
| job | Falcon **587867**, commit `7c55733`, NVIDIA L40S; smoke pass deleted; full run exit 0; log `results/slurm-logs/phase1-step4-587867.out` |
| run | `results/runs/20260917T202853Z-phase1-step4-resample` (`experiments/phase1/step4_resample.py`, seed 20260917) |
| output | `outputs/step4-resample.json` (summary per split/condition/arm/anchor/target; every record's modified and unmodified readouts) |
| edit | the correct intermediate's object fact `"{city} uses {answer}."` → `"{city} uses {new}."`, `new` drawn per record (seed 20260917 + crc32(record_id)) from the 21 single-token `REAL_OBJECTS` excluding the prompt's two objects and any word already in the prompt; 21 distinct replacements used across the 400 held-out records (most frequent: jade 32, paper 32); 0 failed edits; token count unchanged (e.g. `real-zero-010-AAB` rubber → bronze, 30 → 30 tokens) |
| readout | `lens.apply` at the frozen anchors and layers (jlens relcomp L30 / qmark L27 / prequery L25 / final L27; logitlens L30 / L29 / L24 / L30), targets NEW vs OLD, NEW vs ALT, OLD vs ALT, CITY; model's own next-token logits at the same anchors |

## Results — combined held-out (n = 400; heldout 160 + heldout2 240)

"frac" = first-named token ranked above the second in the lens logits. `mod` = modified prompt, `unmod` = unmodified prompt (control: how often the fresh word outranks the stated answer when it is not in the prompt).

### NEW vs OLD (primary: does the readout follow the stated fact?)

| arm | anchor | mod frac | median rank of NEW (mod) | unmod frac | median rank of NEW (unmod) |
|---|---|---|---|---|---|
| J-Lens | prequery L25 | 0.900 | 9,103 | 0.035 | — |
| J-Lens | relcomp L30 | **0.970** | 618 | 0.045 | 23,764 |
| J-Lens | qmark L27 | **0.993** | 99 | 0.000 | 59,124 |
| J-Lens | final L27 | 1.000 | 0 | 0.000 | — |
| logit lens | prequery L24 | 0.670 | 87,308 | 0.035 | — |
| logit lens | relcomp L30 | 0.963 | 1,898 | 0.053 | 97,753 |
| logit lens | qmark L29 | 0.978 | 67 | 0.000 | 144,621 |
| logit lens | final L30 | 1.000 | 0 | 0.000 | — |
| model (own logits) | prequery | 1.000 | 116 | 0.005 | — |
| model | relcomp | 0.983 | 587 | 0.045 | — |
| model | qmark | 1.000 | 34 | 0.000 | — |
| model | final | 1.000 | 1 | 0.000 | — |

Per split, J-Lens NEW vs OLD (mod / unmod): heldout relcomp 0.969 / 0.031, qmark 0.994 / 0.000; heldout2 relcomp 0.971 / 0.054, qmark 0.992 / 0.000. Logit lens: heldout 0.956 / 0.044 and 0.988 / 0.000; heldout2 0.967 / 0.058 and 0.971 / 0.000.

### The same prompts, other targets (combined)

| arm | anchor | NEW vs ALT (mod) | OLD vs ALT (mod) | OLD vs ALT (unmod) = application's ANSWER target | CITY (mod) | CITY (unmod) |
|---|---|---|---|---|---|---|
| J-Lens | relcomp | 0.633 | 0.065 | 0.603 | 0.740 | 0.753 |
| J-Lens | qmark | 0.768 | 0.065 | 0.808 | 0.678 | 0.665 |
| logit lens | relcomp | 0.643 | 0.090 | 0.615 | 0.690 | 0.693 |
| logit lens | qmark | 0.650 | 0.050 | 0.760 | 0.738 | 0.743 |
| model | relcomp | 0.700 | — | — | — | — |
| model | qmark | 0.748 | — | — | — | — |

CITY on the unmodified prompt reproduces step 1's combined values (0.752 / 0.667 J-Lens; 0.690 / 0.745 logit lens) to within one record; CITY on the modified prompt moves by −0.013 / +0.013 (J-Lens) and −0.003 / −0.005 (logit lens).

## Pre-registered rule — which branch fired

**Rule (agent's):** J-Lens NEW-vs-OLD ≥ 0.75 and ≥ unmodified control + 0.30 at relcomp (L30) and qmark (L27) on the combined held-out → "readout follows the stated fact; the co-occurrence door is closed at that position"; ≤ 0.55 → soften §4.2.

- relcomp: 0.970 vs control 0.045 → **follows**.
- qmark: 0.993 vs 0.000 → **follows**.
- Logit lens, reported alongside: 0.963 / 0.978 → follows.
- The branch "does not follow; soften §4.2" did **not** fire.
- Reported beside it, no rule attached: the model's own logits at relcomp already prefer NEW over OLD in 0.983 of records; NEW vs ALT (both in the prompt) is 0.633 at relcomp and 0.768 at qmark for J-Lens, against 0.603 / 0.808 for OLD vs ALT on the original prompt.

## Predictions (agent's) — scored

| prediction | observed | hit? |
|---|---|---|
| final NEW-vs-OLD ≥ 0.9 | 1.000 | yes |
| relcomp 0.55–0.80 | 0.970 | **no** (higher) |
| qmark 0.60–0.85 | 0.993 | **no** (higher) |
| unmodified control ≤ 0.3 at relcomp/qmark | 0.045 / 0.000 | yes |
| CITY frac within ±0.05 of step 1 | −0.013 / +0.013 | yes |

## Three numbers for Jason to hand-check

1. J-Lens relcomp NEW vs OLD, modified, combined = **0.970**, n = 400 — `outputs/step4-resample.json`, `summary.combined["modified/jlens/relcomp/NEW_vs_OLD"].frac`.
2. The unmodified control at the same cell = **0.045** — `summary.combined["unmodified/jlens/relcomp/NEW_vs_OLD"].frac`.
3. One raw record: `real-zero-010-AAB`, rubber → bronze, J-Lens relcomp modified: rank(bronze) 2,807, rank(rubber) 23,918, margin +2.03 — `records[i].prompts.modified.arms.jlens.relcomp.NEW_vs_OLD` for that record_id (first held-out record in the file).
