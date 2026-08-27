#!/usr/bin/env bash
# Regenerate every number and figure in the write-up, from a clean checkout,
# in dependency order.
#
# This doubles as proof that the repository actually runs on a fresh machine.
# Steps are added AS THEY ARE CREATED, never retrofitted at the end -- a
# reproduce script written the night before submission is a script nobody has
# ever run.
#
#   ./scripts/reproduce.sh            # run everything that can run here
#   ./scripts/reproduce.sh --list     # show the dependency order and exit
#
# GPU steps refuse to run on a login node. On ARC, run this inside an
# allocation or via sbatch -- never on falcon1, where Python is prohibited.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VENV="${MATS_VENV:-/scratch/$USER/mats12/venv}"
export HF_HOME="${HF_HOME:-/scratch/$USER/mats12/hf-cache}"
export PYTHONPATH="$ROOT/src:${PYTHONPATH:-}"

# step id | needs GPU | description | command
STEPS=(
  "01-dataset|no|Generate dev + held-out paired datasets (deterministic, seeded)|python src/make_dataset.py"
  "02-eligibility|yes|Behavioural eligibility screen on the unmodified model|python experiments/design-verification/eligibility_screen.py --n-pairs 30"
  "03-v1-tooling|yes|V1 tooling verification: official positive control, logit-lens switch, coverage control|python experiments/design-verification/v1_tooling_verification.py"
)

if [[ "${1:-}" == "--list" ]]; then
  printf '%-16s %-4s %s\n' "STEP" "GPU" "DESCRIPTION"
  for s in "${STEPS[@]}"; do
    IFS='|' read -r id gpu desc _cmd <<< "$s"
    printf '%-16s %-4s %s\n' "$id" "$gpu" "$desc"
  done
  exit 0
fi

have_gpu() { python -c 'import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)' 2>/dev/null; }

if [[ -f "$VENV/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
else
  echo "WARN: venv not found at $VENV -- using whatever python is on PATH" >&2
fi

if [[ "$(hostname)" == falcon* ]]; then
  echo "REFUSING: this is an ARC login node. Python is prohibited here." >&2
  echo "Run inside an salloc allocation, or submit with sbatch." >&2
  exit 2
fi

for s in "${STEPS[@]}"; do
  IFS='|' read -r id gpu desc cmd <<< "$s"
  if [[ "$gpu" == "yes" ]] && ! have_gpu; then
    echo "SKIP  $id  ($desc) -- no CUDA device visible" >&2
    continue
  fi
  echo "=== $id : $desc"
  echo "    \$ $cmd"
  eval "$cmd"
done

echo
echo "Done. Provenance for each run is under results/runs/."
