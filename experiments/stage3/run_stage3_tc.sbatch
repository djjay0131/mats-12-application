#!/bin/bash
# STAGE 3 -- held-out at FROZEN settings. Header and environment inherited
# from the stage-2 job of this cluster; the stage-2 prose comment below
# describes THAT job and is kept for provenance only. Authoritative docs:
# results/stage2/FREEZE.md and experiments/stage3/heldout_frozen.py.
# Stage 2 on TINKERCLIFFS -- INDEPENDENT REBUILD ON DIFFERENT HARDWARE.
#
# WHAT THIS FILE IS FOR
# ---------------------
# This is not a second copy of the Falcon job for convenience. The environment
# under /home/djjay/mats12-tc was rebuilt from scratch on TinkerCliffs -- its own
# venv, its own HF cache, its own pip resolution -- and it runs on different
# GPUs (an A100 here, an A30 or L40S on Falcon). The repo commit and the vendored
# jacobian-lens commit are pinned to the SAME revisions as the Falcon run, and
# the package versions were pinned from `pip freeze` of the Falcon venv, so the
# only intended differences are the machine and the CUDA device.
#
# Therefore: if this job's numbers match the Falcon run's numbers, that is a
# CROSS-PLATFORM REPLICATION CHECK -- evidence the Stage 2 result is a property
# of the method and not of one node, one driver, or one set of wheels. If the
# numbers differ, that difference is itself the finding and must be reported,
# not silently reconciled. Do not "fix" a mismatch by editing this file.
#
# WHY ONE ALLOCATION FOR ALL THREE STEPS
# --------------------------------------
# Not to save queue time -- although it does, three waits become one. The
# binding reason is that step 0 and steps 1-2 must see the same prompts. Stage 1
# already produced a readout and a behavioural screen that could not be joined:
# the screen generated its own pairs through task_templates.build_pairs while
# the readout read results/datasets/dev.jsonl, so the two prompt sets coincided
# 4 times out of 40 and the cross-reference "does the readout recover the
# intermediate where the model answers wrongly" was NOT COMPUTABLE
# (results/design-verification/xref-readout-vs-behaviour.md). Running the screen
# with --dataset results/datasets/dev.jsonl, in the same job, against the same
# committed file the two readout steps read, makes the join exact: every row
# carries the dataset's own record_id and no prompt-string matching is involved.
# Splitting the steps across jobs would let the dataset file change between
# them, which is precisely the failure this job exists to remove.
#
# WHY THE DATASET CHANGED
# -----------------------
# results/datasets/dev.jsonl and heldout.jsonl were regenerated with
# `--vocab-pool 6`: intermediates and their paired objects for every pair are
# now drawn from one shared 6-word pool. Arm 3 (step 2) is the supervised
# difference-in-means reference that section 2.5 of the write-up declares NOT
# OPTIONAL -- without it, "J-Lens cannot read binding" and "binding is not
# linearly present in this residual at all" produce identical numbers. In the
# stage-1 run it failed to produce an interpretable number: leave-one-pair-out
# scored 12 of 40 records and returned class_unseen_in_fit for the other 28,
# because 14 intermediate classes fell across 10 pairs and 9 of them appeared in
# exactly one pair, so holding a pair out deleted the only support for its
# classes. The shared pool gives every class at least 3 pairs of support, and it
# also makes the section-2.5 promise "fit h_bar and mu on dev, apply unchanged
# to held-out" meaningful, since the two splits now share a class vocabulary.
# src/make_dataset.py refuses to write a dataset that fails that self-check.
#
# `set -e` is deliberately NOT used: no step may silently prevent a later one
# from running, and each step's own exit code is reported explicitly.
#SBATCH -A agents4research
# ONE partition, not four. TinkerCliffs rejects a multi-partition request from
# this account with Invalid qos specification: each partition carries its own
# default QOS and agents4research has no shared one. a100_preemptable_q is the
# choice because the A100 is sm_80, the same compute capability as the A30 the
# Falcon run used, so architecture is held fixed. An H200 is sm_90 and would add
# an architecture difference to a comparison meant to vary only the machine.
#SBATCH -p a100_preemptable_q
#SBATCH --gres=gpu:1
#SBATCH -c 2
#SBATCH --mem=24G
#SBATCH -t 00:45:00
#SBATCH -J mats12-stage3-tc
#SBATCH -o /home/djjay/mats12-tc/repo/results/slurm-logs/stage3tc-%j.out
#SBATCH -e /home/djjay/mats12-tc/repo/results/slurm-logs/stage3tc-%j.out
set -uo pipefail
module reset
source /home/djjay/mats12-tc/venv/bin/activate
export HF_HOME=/home/djjay/mats12-tc/hf-cache
export PYTHONPATH=/home/djjay/mats12-tc/repo/src
cd /home/djjay/mats12-tc/repo

echo "=== node: $(hostname)  job: ${SLURM_JOB_ID:-none} ==="
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
echo "dataset: $(wc -l < results/datasets/dev.jsonl) lines in results/datasets/dev.jsonl"

echo
echo "=== STEP 0/1: behavioural eligibility screen on results/datasets/heldout.jsonl ==="
echo "    first read of held-out; the freeze (results/stage2/FREEZE.md) is already committed"
python experiments/design-verification/eligibility_screen.py \
    --dataset results/datasets/heldout.jsonl --frozen-eval
rc0=$?
echo "screen exit=$rc0"

echo
echo "=== STEP 1/1: Stage 3 frozen evaluation (dev shadow reference + held-out) ==="
python experiments/stage3/heldout_frozen.py
rc1=$?
echo "frozen-eval exit=$rc1"

echo
echo "=== STAGE 3 COMPLETE (screen rc=$rc0, eval rc=$rc1) ==="
ls -d results/runs/*/ 2>/dev/null | tail -3
