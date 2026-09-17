#!/bin/bash
# PHASE 1 / STEP 5 addendum -- per-record breakdown at the frozen block (reporting only, no rule).
#SBATCH -A agents4research
#SBATCH -p l40s_normal_q
#SBATCH --gres=gpu:1
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:40:00
#SBATCH -J mats12-p1s5b
#SBATCH -o /scratch/djjay/mats12/repo/results/slurm-logs/phase1-step5b-%j.out
#SBATCH -e /scratch/djjay/mats12/repo/results/slurm-logs/phase1-step5b-%j.out
set -uo pipefail
module reset
source /scratch/djjay/mats12/venv/bin/activate
export HF_HOME=/scratch/djjay/mats12/hf-cache
export PYTHONPATH=/scratch/djjay/mats12/repo/src
export OMP_NUM_THREADS=4
cd /scratch/djjay/mats12/repo
S2=$(ls -td results/runs/*phase1-step2-fact-tokens | head -1)
echo "=== node: $(hostname) job: ${SLURM_JOB_ID:-none} commit: $(git rev-parse --short HEAD) step2: $S2 ==="
python experiments/phase1/step5_breakdown.py --residual-dir /scratch/djjay/mats12/phase1/residuals --step2-run "$S2"
echo "exit=$?"
