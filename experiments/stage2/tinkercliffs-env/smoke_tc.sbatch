#!/bin/bash
# Environment smoke test for the TinkerCliffs independent rebuild.
# Loads torch/transformers/jlens on a real GPU node -- NOT on the login node --
# and reports versions plus the CUDA device, so the rebuilt venv is confirmed
# importable and GPU-capable before any Stage 2 compute is submitted.
#SBATCH -A agents4research
#SBATCH -p a100_preemptable_q
#SBATCH --gres=gpu:1
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -t 00:05:00
#SBATCH -J mats12-smoke-tc
#SBATCH -o /home/djjay/mats12-tc/repo/results/slurm-logs/smoketc-%j.out
#SBATCH -e /home/djjay/mats12-tc/repo/results/slurm-logs/smoketc-%j.out
set -uo pipefail
module reset
source /home/djjay/mats12-tc/venv/bin/activate
export HF_HOME=/home/djjay/mats12-tc/hf-cache
export PYTHONPATH=/home/djjay/mats12-tc/repo/src

echo "=== node: $(hostname)  job: ${SLURM_JOB_ID:-none} ==="
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
echo
python - <<'PY'
import importlib.metadata as md
import torch, transformers, jlens
print("python        :", __import__("sys").version.split()[0])
print("torch         :", torch.__version__)
print("torch.cuda    :", torch.version.cuda)
print("cuda available:", torch.cuda.is_available())
print("device 0      :", torch.cuda.get_device_name(0))
print("capability    :", torch.cuda.get_device_capability(0))
print("transformers  :", transformers.__version__)
print("jlens version :", md.version("jlens"))
print("jlens path    :", jlens.__file__)
x = torch.randn(2048, 2048, device="cuda")
print("matmul ok     :", bool(torch.isfinite(x @ x).all().item()))
PY
echo "=== SMOKE_RC=$? ==="
