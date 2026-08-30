#!/bin/bash
#SBATCH --account=agents4research
#SBATCH --partition=a30_normal_q,l40s_normal_q
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=00:40:00
#SBATCH --job-name=verify-shadow
#SBATCH --output=/scratch/djjay/mats12/repo/results/verification/verify-shadow-%j.out
#SBATCH --error=/scratch/djjay/mats12/repo/results/verification/verify-shadow-%j.err

set -euo pipefail
cd /scratch/djjay/mats12/repo
source /scratch/djjay/mats12/venv/bin/activate
python results/verification/verify_shadow.py
