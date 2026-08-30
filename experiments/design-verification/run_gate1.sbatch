#!/bin/bash
# Gate 1: the eligibility kill-shot, then V1 tooling verification.
#
# Both run in ONE allocation because ARC queue latency is measured in hours,
# so a second queue wait costs more than a second model load. They are separate
# processes on purpose: each gets its own clean run record under results/runs/,
# and a failure in one does not contaminate the other's provenance.
#
# `set -e` is deliberately NOT used. If the eligibility screen fails or STOPs,
# V1 still runs -- V1 verifies the tooling against the OFFICIAL evaluation and
# is independent of whether our own stimuli turn out to be usable.
#SBATCH -A agents4research
#SBATCH -p a30_normal_q
#SBATCH --gres=gpu:1
#SBATCH -c 2
#SBATCH --mem=24G
#SBATCH -t 00:45:00
#SBATCH -J mats12-gate1
#SBATCH -o /scratch/djjay/mats12/repo/results/slurm-logs/gate1-%j.out
#SBATCH -e /scratch/djjay/mats12/repo/results/slurm-logs/gate1-%j.out
set -uo pipefail
module reset
source /scratch/djjay/mats12/venv/bin/activate
export HF_HOME=/scratch/djjay/mats12/hf-cache
export PYTHONPATH=/scratch/djjay/mats12/repo/src
cd /scratch/djjay/mats12/repo

echo "=== node: $(hostname)  job: ${SLURM_JOB_ID:-none} ==="
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

echo
echo "=== STEP 1/2: behavioural eligibility screen (the kill-shot) ==="
python experiments/design-verification/eligibility_screen.py --n-pairs 30
rc1=$?
echo "eligibility screen exit=$rc1"

echo
echo "=== STEP 2/2: V1 tooling and positive-control verification ==="
python experiments/design-verification/v1_tooling_verification.py
rc2=$?
echo "v1 exit=$rc2"

echo
echo "=== GATE 1 COMPLETE (eligibility rc=$rc1, v1 rc=$rc2) ==="
ls -d results/runs/*/ 2>/dev/null | tail -5
