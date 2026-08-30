# Slurm logs — which blocks are valid

Written 2026-08-27. Read this before citing anything from a log in this
directory.

Each `gate1-*.out` file contains **two independent steps in one allocation**: a
behavioural eligibility screen and a V1 tooling verification. In two of the
three gate1 allocations the eligibility block is invalid and the V1 block is
valid. A reader opening a raw log will not see that from the log alone, which is
why this file exists.

| job | log | eligibility block | V1 / stage-1 block |
|---|---|---|---|
| 550510 | `gate1-550510.out` | **INVALID** — `max_new_tokens=4`, budget eaten by the `<think>` tag | **VALID** — PASS 8/8 |
| 550548 | `gate1-550548.out` | **INVALID** — first-word scorer returned `"Based"` | **VALID** — PASS 8/8 |
| 550555 | `gate1-550555.out` | **VALID** — real/zero AB = 0.900, PASS | **VALID** — PASS 8/8 |
| 550627 | *(none)* | cancelled before starting, to add arm 3 | — |
| 550652 | *(none)* | cancelled after 90 min pending; widened to two partitions | — |
| 550690 | `stage1-550690.out` | — | **VALID** — vendor audit, passive readout, arm 3 |

## The trap in 550510 and 550548

Both invalid screens report zero-shot near floor and few-shot near ceiling. The
valid screen inverts this: **real/zero = 0.900 PASS, real/few = 0.667
MARGINAL**. Few-shot only ever looked better because demonstrations make the
model terse, which flattered two broken scoring rules. The operating point for
the project is **real lexicon, zero-shot**.

## Caveat on 550690

Arm 3 in `stage1-550690.out` reports a leave-one-pair-out accuracy of 0.583,
but it scored only **12 of 40 records** — the other 28 were unscorable
(`class_unseen_in_fit`). It is **uninformative, not at floor**, and the
pre-registered rule about a floor-level arm 3 does not apply to it. See
`results/runs/20260827T154143Z-stage1-supervised-reference/`.

## Provenance

Every number in every log traces to a run directory under `results/runs/` with
its own `manifest.json`, `command.txt` and `outputs/`. The runs are the record;
the logs are the transcript. Where they disagree, the run directory wins.

All numbers are `agent-unverified`: they come from this pipeline and share its
code.

---

# Stage 2, 2026-08-28 — added after the file above was written

Three more allocations. These are `stage2-*.out` and `stage2tc-*.out`, and they
have a different shape from the `gate1-*` logs: each one is **three steps in one
allocation** — behavioural eligibility screen, passive J-Lens readout, arm 3 —
run against the same `results/datasets/dev.jsonl` in the same job so that the
screen and the readout see identical stimuli and join exactly on `record_id`.
That was the point: Stage 1's screen and readout could not be joined at all.

| job | cluster / GPU | log | screen | readout | arm 3 |
|---|---|---|---|---|---|
| 551581 | Falcon / A30 | `stage2-551581.out` | **VALID** — AB = 1.000 | **INVALID** — crashed, `model_logits` indexed as `[batch, seq, vocab]` when `apply()` returns `[n_positions, vocab]` | **VALID** — LOO 40/40 scored |
| 551834 | Falcon / L40S | `stage2-551834.out` | **VALID** — AB = 1.000 | **VALID** | **VALID** |
| 7298944 | TinkerCliffs / A100 | `stage2tc-7298944.out` | **VALID** — AB = 0.900 | **VALID** | **VALID** |

The 551581 readout crash is fixed in `06ef3a5`. It is worth naming precisely
because the line that crashed was the line added specifically to enable the
answer-shadow test — the instrument broke on its first use, for the third time
in this project.

## 551834 and 7298944 are a replication pair

Same commit `06ef3a5`, same dataset, same lens revision, same model revision,
same 61 pip packages, different cluster and different GPU. Read them together or
not at all.

**The readout replicates.** Both jobs select the same layers (J-Lens final 27,
J-Lens prequery 25, logit lens final 30, logit lens prequery 24), report the same
`frac_correct_outranks_incorrect` at every one of them, and give median ranks
within about 5% (J-Lens final 37 vs 35; prequery 357 vs 346; logit lens final
20 vs 19; random-transport control 128,589 vs 128,084). Arm 3 agrees to
+24.199 / 0.625 against +24.717 / 0.650.

**The screen does not.** Eligibility AB is 1.000 on the L40S and 0.900 on the
A100, and the screen's own padding control moves from 0/8 mismatched to 2/8.
This is the expected failure mode rather than a mystery: the screen decodes
greedily, and greedy decoding turns last-bit floating-point differences into
different tokens. One prompt in ten flips its behavioural label between two GPUs.

Consequences, both of which bind:

1. **Quote the eligibility percentage with that instability attached.** It is not
   a stable property of the stimuli; it is a property of the stimuli and the
   card.
2. **The binary readout-vs-behaviour contingency table is not usable on this
   split.** On 7298944 it has exactly one discriminating case; on 551834 it has
   zero, because the model is behaviourally correct on all 40 records. Any
   readout-versus-behaviour claim has to come from the graded per-record
   `model_behaviour` field, not from the 2x2.

## Provenance for these three

`results/runs/20260828T2040*` and `20260828T2045*` are 7298944 (TinkerCliffs);
`20260828T2051*` through `20260828T2054*` are 551834 (Falcon). Their manifests
report `dirty=true`: the earlier steps of the same allocation write their own run
directories into the tree before the later steps snapshot git state. That is the
known and expected form of the flag in a multi-step job, not an uncommitted
source change — `git=06ef3a5…` is the same in all six.

All numbers `agent-unverified`.
