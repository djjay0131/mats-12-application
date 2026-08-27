#!/bin/bash
# Stage 1: passive J-Lens readout on role-swapped pairs, DEV SPLIT ONLY.
#
# Two readout positions in the same forward pass (final = post-selection,
# prequery = before the query names a subject), three arms (J-Lens, logit lens
# through the identical path, norm-matched random transport), and a label
# permutation control scored alongside every record.
#
# Step 0 is a static audit of the vendor package, run here rather than on the
# login node so it lands inside a job with a log. It is grep, not compute; it
# costs seconds and it is the evidence behind the V2 decision.
#
# `set -e` is deliberately NOT used: the audit must not be able to stop the
# readout, and the readout's own exit code is reported explicitly.
#SBATCH -A agents4research
#SBATCH -p a30_normal_q
#SBATCH --gres=gpu:1
#SBATCH -c 2
#SBATCH --mem=24G
#SBATCH -t 00:45:00
#SBATCH -J mats12-stage1
#SBATCH -o /scratch/djjay/mats12/repo/results/slurm-logs/stage1-%j.out
#SBATCH -e /scratch/djjay/mats12/repo/results/slurm-logs/stage1-%j.out
set -uo pipefail
module reset
source /scratch/djjay/mats12/venv/bin/activate
export HF_HOME=/scratch/djjay/mats12/hf-cache
export PYTHONPATH=/scratch/djjay/mats12/repo/src
cd /scratch/djjay/mats12/repo

echo "=== node: $(hostname)  job: ${SLURM_JOB_ID:-none} ==="
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

echo
echo "=== STEP 0/2: V2 decomposition audit (static, no GPU) ==="
bash scripts/v2_decomposition_audit.sh
echo "audit exit=$?"

echo
echo "=== STEP 1/2: dry run, 4 records, position alignment check ==="
python experiments/stage1/passive_readout.py --max-records 4
echo "dry run exit=$?"

echo
echo "=== STEP 2/2: full dev split ==="
python experiments/stage1/passive_readout.py
rc=$?
echo "stage1 exit=$rc"

echo
echo "=== STAGE 1 COMPLETE (rc=$rc) ==="
ls -d results/runs/*/ 2>/dev/null | tail -4
