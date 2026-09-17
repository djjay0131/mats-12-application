#!/bin/bash
# PHASE 1 / STEP 5 -- logistic-regression probe beside difference-in-means,
# leave-one-pair-out on the combined held-out set, at every block; reads the
# residuals step 2 saved. CPU work; queued with --dependency=afterok:<step2>.
# Pre-registered in llm/memory_bank/research-learning-log.md ("Phase 1, step 5")
# and committed before this job is queued.
#
#SBATCH -A agents4research
#SBATCH -p l40s_normal_q
#SBATCH --gres=gpu:1
#SBATCH -c 16
#SBATCH --mem=64G
#SBATCH -t 03:00:00
#SBATCH -J mats12-p1s5
#SBATCH -o /scratch/djjay/mats12/repo/results/slurm-logs/phase1-step5-%j.out
#SBATCH -e /scratch/djjay/mats12/repo/results/slurm-logs/phase1-step5-%j.out
set -uo pipefail
module reset
source /scratch/djjay/mats12/venv/bin/activate
export HF_HOME=/scratch/djjay/mats12/hf-cache
export PYTHONPATH=/scratch/djjay/mats12/repo/src
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /scratch/djjay/mats12/repo
RES=/scratch/djjay/mats12/phase1/residuals
echo "=== node: $(hostname)  job: ${SLURM_JOB_ID:-none}  commit: $(git rev-parse --short HEAD) ==="
S2=$(ls -td results/runs/*phase1-step2-fact-tokens 2>/dev/null | head -1)
echo "step2 run: $S2"
if [ -z "$S2" ] || [ ! -f "$S2/outputs/step2-records.json.gz" ] || [ ! -f "$RES/heldout2.pt" ]; then
    echo "=== STOP: step 2 outputs not found ==="; exit 5
fi

echo "=== smoke (blocks 30,31; run dir deleted) ==="
python experiments/phase1/step5_lr_probe.py --residual-dir "$RES" --step2-run "$S2" --layers 30,31 --jobs 2
rc=$?
d=$(ls -td results/runs/*phase1-step5-lr-probe 2>/dev/null | head -1)
echo "smoke exit=$rc dir=$d"; rm -rf "$d"
if [ "$rc" != "0" ]; then echo "=== STOP: smoke failed ==="; exit 5; fi

echo "=== STEP 5: full run ==="
python experiments/phase1/step5_lr_probe.py --residual-dir "$RES" --step2-run "$S2" --jobs 16
rc=$?
echo "step5 exit=$rc"
echo "=== PHASE 1 STEP 5 COMPLETE rc=$rc ==="
