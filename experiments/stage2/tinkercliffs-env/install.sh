#!/bin/bash
set -uo pipefail
source /etc/profile.d/modules.sh 2>/dev/null
module reset >/dev/null 2>&1
module load Python/3.12.3-GCCcore-13.3.0
PY=/home/djjay/mats12-tc/venv/bin/python
BASE=/home/djjay/mats12-tc
"$PY" -m pip install --upgrade pip
echo "=== STEP1_RC=$? ==="
"$PY" -m pip install -r "$BASE/requirements-from-falcon.txt"
echo "=== STEP2_RC=$? ==="
"$PY" -m pip install -e "$BASE/vendor/jacobian-lens" --no-deps
echo "=== STEP3_RC=$? ==="
"$PY" -m pip check
echo "=== PIPCHECK_RC=$? ==="
echo "=== ALL_DONE ==="
