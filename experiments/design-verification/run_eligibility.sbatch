#!/bin/bash
#SBATCH -A agents4research
#SBATCH -p a30_normal_q
#SBATCH --gres=gpu:1
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:30:00
#SBATCH -J mats12-elig
#SBATCH -o /scratch/djjay/mats12/repo/results/slurm-logs/elig-%j.out
#SBATCH -e /scratch/djjay/mats12/repo/results/slurm-logs/elig-%j.out
set -euo pipefail
module reset
source /scratch/djjay/mats12/venv/bin/activate
export HF_HOME=/scratch/djjay/mats12/hf-cache
export HF_HUB_OFFLINE=1
export PYTHONPATH=/scratch/djjay/mats12/repo/src
cd /scratch/djjay/mats12/repo
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
python experiments/design-verification/eligibility_screen.py --n-pairs 30
