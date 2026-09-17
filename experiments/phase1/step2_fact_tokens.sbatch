#!/bin/bash
# PHASE 1 / STEP 2 -- probe the fact tokens (arm 3 at every layer, dev-fit,
# leave-one-pair-out on dev, applied unchanged to heldout + heldout2; J-Lens
# and logit lens at the same positions; label-permutation control).
# Pre-registered in llm/memory_bank/research-learning-log.md ("Phase 1, step 2")
# and committed before this job is queued. Also saves residuals (outside the
# repo) that step 5 reads.
#
# A 2-record smoke run is executed first and its run directory DELETED; it is
# never reported. If the smoke run fails, the main run does not start.
#
#SBATCH -A agents4research
#SBATCH -p l40s_normal_q
#SBATCH --gres=gpu:1
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 02:00:00
#SBATCH -J mats12-p1s2
#SBATCH -o /scratch/djjay/mats12/repo/results/slurm-logs/phase1-step2-%j.out
#SBATCH -e /scratch/djjay/mats12/repo/results/slurm-logs/phase1-step2-%j.out
set -uo pipefail
module reset
source /scratch/djjay/mats12/venv/bin/activate
export HF_HOME=/scratch/djjay/mats12/hf-cache
export PYTHONPATH=/scratch/djjay/mats12/repo/src
cd /scratch/djjay/mats12/repo
RES=/scratch/djjay/mats12/phase1/residuals
echo "=== node: $(hostname)  job: ${SLURM_JOB_ID:-none}  commit: $(git rev-parse --short HEAD) ==="
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

echo "=== smoke (2 records/split; run dir deleted) ==="
python experiments/phase1/step2_fact_tokens.py --residual-dir "$RES-smoke" --max-records 2
rc=$?
d=$(ls -td results/runs/*phase1-step2-fact-tokens 2>/dev/null | head -1)
echo "smoke exit=$rc dir=$d"; rm -rf "$d" "$RES-smoke"
if [ "$rc" != "0" ]; then echo "=== STOP: smoke failed ==="; exit 5; fi

echo "=== STEP 2: full run ==="
python experiments/phase1/step2_fact_tokens.py --residual-dir "$RES"
rc=$?
echo "step2 exit=$rc"
ls -la "$RES" 2>/dev/null
echo "=== PHASE 1 STEP 2 COMPLETE rc=$rc ==="
