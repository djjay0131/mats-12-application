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
