#!/bin/bash
# Stage 2: behavioural labels and lens readouts over THE SAME STIMULI.
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
#SBATCH -p a30_normal_q,l40s_normal_q,a30_preemptable_q,l40s_preemptable_q
#SBATCH --gres=gpu:1
#SBATCH -c 2
#SBATCH --mem=24G
#SBATCH -t 00:20:00
#SBATCH -J mats12-stage2
#SBATCH -o /scratch/djjay/mats12/repo/results/slurm-logs/stage2-%j.out
#SBATCH -e /scratch/djjay/mats12/repo/results/slurm-logs/stage2-%j.out
set -uo pipefail
module reset
source /scratch/djjay/mats12/venv/bin/activate
export HF_HOME=/scratch/djjay/mats12/hf-cache
export PYTHONPATH=/scratch/djjay/mats12/repo/src
cd /scratch/djjay/mats12/repo

echo "=== node: $(hostname)  job: ${SLURM_JOB_ID:-none} ==="
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
echo "dataset: $(wc -l < results/datasets/dev.jsonl) lines in results/datasets/dev.jsonl"

echo
echo "=== STEP 0/2: behavioural eligibility screen on results/datasets/dev.jsonl ==="
echo "    behavioural labels for EXACTLY the stimuli steps 1 and 2 read"
python experiments/design-verification/eligibility_screen.py \
    --dataset results/datasets/dev.jsonl
rc0=$?
echo "screen exit=$rc0"

echo
echo "=== STEP 1/2: passive J-Lens readout, full dev split ==="
echo "    keeps model_logits, so the readout-vs-behaviour margin is per record"
python experiments/stage1/passive_readout.py
rc1=$?
echo "readout exit=$rc1"

echo
echo "=== STEP 2/2: arm 3, supervised difference-in-means reference ==="
echo "    now with class support outside every held-out pair"
python experiments/stage1/supervised_reference.py
rc2=$?
echo "arm3 exit=$rc2"

echo
echo "=== STAGE 2 COMPLETE (screen rc=$rc0, readout rc=$rc1, arm3 rc=$rc2) ==="
ls -d results/runs/*/ 2>/dev/null | tail -4
