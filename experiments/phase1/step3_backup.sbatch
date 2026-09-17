#!/bin/bash
# PHASE 1 / STEP 3 BACKUP -- same experiment, reduced block sweep (primary
# frozen blocks + every third block + 31), queued in parallel because the
# full-sweep job 587866 is projected to finish within ~20 minutes of its
# 4-hour limit and writes its results only at the end. Pre-registered rules
# and cells unchanged. If 587866 completes, this run is deleted and never
# reported; if 587866 times out, this run is reported with the reduced sweep
# stated (Amendment 3 in the learning log).
#SBATCH -A agents4research
#SBATCH -p l40s_normal_q
#SBATCH --gres=gpu:1
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 03:00:00
#SBATCH -J mats12-p1s3b
#SBATCH -o /scratch/djjay/mats12/repo/results/slurm-logs/phase1-step3b-%j.out
#SBATCH -e /scratch/djjay/mats12/repo/results/slurm-logs/phase1-step3b-%j.out
set -uo pipefail
module reset
source /scratch/djjay/mats12/venv/bin/activate
export HF_HOME=/scratch/djjay/mats12/hf-cache
export PYTHONPATH=/scratch/djjay/mats12/repo/src
cd /scratch/djjay/mats12/repo
echo "=== node: $(hostname)  job: ${SLURM_JOB_ID:-none}  commit: $(git rev-parse --short HEAD) ==="
nvidia-smi --query-gpu=name --format=csv,noheader
python experiments/phase1/step3_patching.py --layers 0,3,6,9,12,15,18,21,24,25,27,29,30,31
echo "exit=$?"
