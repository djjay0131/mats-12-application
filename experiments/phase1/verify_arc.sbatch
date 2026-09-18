#!/bin/bash
# Agent verification pass, part 2: independent re-fit from saved residuals (read-only).
#SBATCH -A agents4research
#SBATCH -p l40s_normal_q
#SBATCH --gres=gpu:1
#SBATCH -c 8
#SBATCH --mem=32G
#SBATCH -t 00:30:00
#SBATCH -J mats12-p1ver
#SBATCH -o /scratch/djjay/mats12/repo/results/slurm-logs/phase1-verify-%j.out
#SBATCH -e /scratch/djjay/mats12/repo/results/slurm-logs/phase1-verify-%j.out
set -uo pipefail
module reset
source /scratch/djjay/mats12/venv/bin/activate
export HF_HOME=/scratch/djjay/mats12/hf-cache
export OMP_NUM_THREADS=8
cd /scratch/djjay/mats12/repo
echo "=== node: $(hostname) job: ${SLURM_JOB_ID:-none} commit: $(git rev-parse --short HEAD) ==="
python experiments/phase1/verify_arc.py
echo "exit=$?"
