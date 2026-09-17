#!/bin/bash
# PHASE 1 / STEP 4 -- resample control: the correct intermediate's object fact
# is rewritten with a fresh pool object; J-Lens / logit lens re-read at the
# frozen positions and layers; unmodified-prompt control.
# Pre-registered in llm/memory_bank/research-learning-log.md ("Phase 1, step 4")
# and committed before this job is queued.
#
# A 2-record smoke run is executed first and its run directory DELETED.
#
#SBATCH -A agents4research
#SBATCH -p l40s_normal_q
#SBATCH --gres=gpu:1
#SBATCH -c 2
#SBATCH --mem=24G
#SBATCH -t 01:30:00
#SBATCH -J mats12-p1s4
#SBATCH -o /scratch/djjay/mats12/repo/results/slurm-logs/phase1-step4-%j.out
#SBATCH -e /scratch/djjay/mats12/repo/results/slurm-logs/phase1-step4-%j.out
set -uo pipefail
module reset
source /scratch/djjay/mats12/venv/bin/activate
export HF_HOME=/scratch/djjay/mats12/hf-cache
export PYTHONPATH=/scratch/djjay/mats12/repo/src
cd /scratch/djjay/mats12/repo
echo "=== node: $(hostname)  job: ${SLURM_JOB_ID:-none}  commit: $(git rev-parse --short HEAD) ==="
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

echo "=== smoke (2 records/split; run dir deleted) ==="
python experiments/phase1/step4_resample.py --max-records 2
rc=$?
d=$(ls -td results/runs/*phase1-step4-resample 2>/dev/null | head -1)
echo "smoke exit=$rc dir=$d"; rm -rf "$d"
if [ "$rc" != "0" ]; then echo "=== STOP: smoke failed ==="; exit 5; fi

echo "=== STEP 4: full run ==="
python experiments/phase1/step4_resample.py
rc=$?
echo "step4 exit=$rc"
echo "=== PHASE 1 STEP 4 COMPLETE rc=$rc ==="
