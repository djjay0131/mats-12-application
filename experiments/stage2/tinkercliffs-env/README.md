# TinkerCliffs environment: what it is and what was verified

This directory holds the scripts that built the second execution environment for
Stage 2, under `/home/djjay/mats12-tc` on TinkerCliffs, together with the smoke
job that proved it works. The Falcon environment lives at
`/scratch/djjay/mats12`; nothing is shared between them except `/home`, which is
the same filesystem on both clusters (`qc72.arc.vt.edu:/home`). `/scratch` is
not shared.

## Why a second environment exists

Not as a backup. `experiments/stage2/run_stage2_tc.sbatch` runs the same three
steps as `experiments/stage2/run_stage2.sbatch` against the same repo commit,
the same vendored `jacobian-lens` commit, the same model revision and the same
lens revision, on a different cluster, a different GPU, a different venv and a
different Hugging Face cache. If the two jobs produce the same numbers, that is
a cross-platform replication check: evidence the Stage 2 result is a property of
the method rather than of one node, one driver, or one set of wheels. If they
differ, the difference is the finding and gets reported as such -- it does not
get reconciled by editing either job file.

## What was pinned, and what was checked

Checked on 2026-08-28 by reading both environments, not by assuming:

| Thing | Falcon | TinkerCliffs | Same? |
|---|---|---|---|
| repo commit | `06ef3a5` | `06ef3a5` | yes, tree-identical |
| vendored `jacobian-lens` | `581d398` | `581d398` | yes, diff-identical |
| lens snapshot `neuronpedia/jacobian-lens` | `16a01f309fcec900fdcec3f4cd5b64f3d00e4d5a` | `16a01f309fcec900fdcec3f4cd5b64f3d00e4d5a` | yes |
| model snapshot `Qwen/Qwen3.5-4B` | `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a` | `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a` | yes |
| Python module | `Python/3.12.3-GCCcore-13.3.0` | same | yes |
| pip packages | 61 | 61 | yes, versions match exactly |
| GPU | A30 or L40S | A100-SXM4-80GB | NO -- see below |

The lens revision `qwen-n1000` is a *branch*, not a tag, so it can move. It was
resolved on both sides and the resolved commits are recorded above precisely
because a silent branch move would invalidate the comparison. They match.

`accelerate` is absent from both environments. `requirements-from-falcon.txt` is
`pip freeze` of the Falcon venv, used verbatim to build the TinkerCliffs one.

## The one intended difference

The GPU. The TinkerCliffs job requests `a100_preemptable_q` only. The A100 is
compute capability 8.0, the same as Falcon's A30, so the architecture is held
fixed and the difference is the specific card, its memory and its driver. The
H200 partitions were deliberately not requested: sm_90 would add an architecture
change to a comparison meant to vary only the machine.

A single partition is also a hard requirement here, not a preference.
TinkerCliffs rejects a multi-partition request from the `agents4research`
account with `Invalid qos specification`, because each partition carries its own
default QOS and the account has no shared one. The four-partition line that
works on Falcon does not work here.

## Smoke test

Job 7298891, `smoketc-7298891.out` in `results/slurm-logs/`, COMPLETED in 41 s
with exit 0 on node `tc-dgx008`:

    NVIDIA A100-SXM4-80GB, 81920 MiB, 595.71.05
    python 3.12.3 / torch 2.13.0+cu130 / cuda 13.0 / capability (8, 0)
    transformers 5.16.1 / jlens 0.1.0
    matmul ok: True

It imports `jlens` and does a CUDA matmul. It does not load the model or the
lens, so it is a proof the environment starts, not a proof the science runs.

## Files here

- `install.sh` -- module load, venv creation, `pip install -r requirements-from-falcon.txt`
- `fetch.sh` -- `hf download` of the model and lens at the pinned revisions.
  Note `huggingface-cli` is a dead stub in `huggingface_hub` 1.x: it prints a
  deprecation notice, exits 1 and downloads nothing. `hf download` is the
  working command.
- `requirements-from-falcon.txt` -- the pin source
- `smoke_tc.sbatch` -- the smoke job

Build logs (`pip-install.log`, `fetch.log`) were left on TinkerCliffs at
`/home/djjay/mats12-tc/` rather than committed; they are machine-local install
noise, and the versions they produced are recorded in the table above.

## Honest note on why this environment was built

The trigger was a claim I made that TinkerCliffs and Owl had no queued work and
would therefore start sooner than Falcon. That claim was wrong: `squeue` on ARC
shows only your own jobs, so the queue looked empty because it was empty *of
mine*. `sinfo` and `sbatch --test-only` tell the real story, and TinkerCliffs is
not obviously faster. The environment was built on a mistaken premise. It is
kept because the cross-platform replication check is worth having on its own
terms, which is the reason recorded at the top of this file -- but the record
should not pretend that was the reason it started.
