#!/bin/bash
#SBATCH --job-name=mats12-arc-smoke
#SBATCH --account=agents4research
#SBATCH --partition=l40s_normal_q
#SBATCH --time=00:10:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:1
#SBATCH --mem=8G
#SBATCH --output=mats12-arc-smoke-%j.out
#SBATCH --error=mats12-arc-smoke-%j.err

# ARC GPU infrastructure smoke test for the MATS 12.0 J-Lens project.
# Scope: prove a GPU job can be scheduled and can see a GPU.
# Deliberately does NOT: download models, install packages, or validate
# J-Lens/model/lens compatibility.

set -euo pipefail

echo "=== ARC GPU SMOKE TEST ==="
echo "date_utc:            $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# 1. hostname
echo "hostname:            $(hostname)"

# 2. job id
echo "SLURM_JOB_ID:        ${SLURM_JOB_ID:-<unset>}"
echo "SLURM_JOB_ACCOUNT:   ${SLURM_JOB_ACCOUNT:-<unset>}"
echo "SLURM_JOB_PARTITION: ${SLURM_JOB_PARTITION:-<unset>}"

# 3. visible devices
echo "CUDA_VISIBLE_DEVICES: ${CUDA_VISIBLE_DEVICES:-<unset>}"

# 4. GPU identity
echo "--- nvidia-smi ---"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

# 5. system python
echo "--- python ---"
if command -v python3 >/dev/null 2>&1; then
    echo "python3:             $(python3 --version 2>&1)"
    echo "python3_path:        $(command -v python3)"
else
    echo "python3:             not available"
fi

# 6/7/8. Optional PyTorch probe. Must never fail the job:
# disable errexit around it and swallow a non-zero exit.
echo "--- pytorch probe ---"
if command -v python3 >/dev/null 2>&1; then
    set +e
    python3 - <<'PYEOF'
try:
    import torch
except Exception:
    print("PyTorch not installed; environment setup required")
else:
    print(f"torch.__version__:        {torch.__version__}")
    print(f"torch.version.cuda:       {torch.version.cuda}")
    avail = torch.cuda.is_available()
    print(f"torch.cuda.is_available(): {avail}")
    if avail:
        print(f"torch.cuda.get_device_name(0): {torch.cuda.get_device_name(0)}")
PYEOF
    rc=$?
    set -e
    if [ "$rc" -ne 0 ]; then
        echo "PyTorch not installed; environment setup required"
    fi
else
    echo "PyTorch not installed; environment setup required"
fi

echo "=== SMOKE TEST COMPLETE ==="
exit 0
