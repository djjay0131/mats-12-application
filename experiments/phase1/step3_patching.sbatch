#!/bin/bash
# PHASE 1 / STEP 3 -- activation patching between swapped twins at the frozen
# anchors, every block output; unrelated-donor (norm-matched) control and the
# prequery-period position control. Dev first, then held-out once.
# Pre-registered in llm/memory_bank/research-learning-log.md ("Phase 1, step 3")
# and committed before this job is queued.
#
# A 2-record smoke run (blocks 30,31 only) is executed first and its run
# directory DELETED; it is never reported.
#
#SBATCH -A agents4research
#SBATCH -p l40s_normal_q
#SBATCH --gres=gpu:1
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 04:00:00
#SBATCH -J mats12-p1s3
#SBATCH -o /scratch/djjay/mats12/repo/results/slurm-logs/phase1-step3-%j.out
#SBATCH -e /scratch/djjay/mats12/repo/results/slurm-logs/phase1-step3-%j.out
set -uo pipefail
module reset
source /scratch/djjay/mats12/venv/bin/activate
export HF_HOME=/scratch/djjay/mats12/hf-cache
export PYTHONPATH=/scratch/djjay/mats12/repo/src
cd /scratch/djjay/mats12/repo
echo "=== node: $(hostname)  job: ${SLURM_JOB_ID:-none}  commit: $(git rev-parse --short HEAD) ==="
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

echo "=== smoke (4 records/split, blocks 30,31; run dir deleted) ==="
python experiments/phase1/step3_patching.py --max-records 4 --layers 30,31
rc=$?
d=$(ls -td results/runs/*phase1-step3-patching 2>/dev/null | head -1)
echo "smoke exit=$rc dir=$d"; rm -rf "$d"
if [ "$rc" != "0" ]; then echo "=== STOP: smoke failed ==="; exit 5; fi

echo "=== STEP 3: full run (dev first, then heldout, heldout2) ==="
python experiments/phase1/step3_patching.py
rc=$?
echo "step3 exit=$rc"
echo "=== PHASE 1 STEP 3 COMPLETE rc=$rc ==="
