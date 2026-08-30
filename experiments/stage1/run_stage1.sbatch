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
# Step 3 runs arm 3, the supervised difference-in-means reference, inside this
# same allocation because section 2.5 declares that arm NOT OPTIONAL: if both
# lenses sit at floor, "J-Lens cannot read binding" and "binding is not linearly
# present in this residual at all" produce identical numbers, so a floor result
# from the passive readout cannot be interpreted without it. Running it here
# costs one queue wait instead of two.
#
# `set -e` is deliberately NOT used: the audit must not be able to stop the
# readout, and the readout's own exit code is reported explicitly.
#SBATCH -A agents4research
#SBATCH -p a30_normal_q,l40s_normal_q
#SBATCH --gres=gpu:1
#SBATCH -c 2
#SBATCH --mem=24G
#SBATCH -t 00:25:00
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
echo "=== STEP 0/3: V2 decomposition audit (static, no GPU) ==="
bash scripts/v2_decomposition_audit.sh
echo "audit exit=$?"

echo
echo "=== STEP 1/3: dry run, 4 records, position alignment check ==="
python experiments/stage1/passive_readout.py --max-records 4
echo "dry run exit=$?"

echo
echo "=== STEP 2/3: full dev split ==="
python experiments/stage1/passive_readout.py
rc=$?
echo "stage1 exit=$rc"

echo
echo "=== STEP 3/3: arm 3, supervised difference-in-means reference ==="
python experiments/stage1/supervised_reference.py
rc3=$?
echo "arm3 exit=$rc3"

echo
echo "=== STAGE 1 COMPLETE (stage1 rc=$rc, arm3 rc=$rc3) ==="
ls -d results/runs/*/ 2>/dev/null | tail -4
