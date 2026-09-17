#!/bin/bash
# PHASE 1 / STEP 1 -- fresh held-out draw, scored ONCE at the frozen settings.
#
# Pre-registered in llm/memory_bank/research-learning-log.md ("Phase 1, step 1")
# and committed BEFORE this job is queued. Nothing in this job selects anything:
# positions, layers, arms and controls are whatever experiments/stage3/freeze.json
# already says. The only new inputs are the seed (20260917) and the pair count
# (60 pairs = 240 records).
#
# Steps
#   0. Regression: regenerate the ORIGINAL dev/heldout files with default
#      arguments into a scratch dir and require byte-identical sha256 against
#      results/datasets/dataset-manifest.json. This proves the two flags added
#      to src/make_dataset.py for this step (--pool-seed, --id-prefix) leave
#      the original draw untouched. If it fails, the job stops here.
#      (Job 587798 passed this check and then stopped at step 1: the
#      generator's own self-check refused a 60-pair draw with 4 duplicate
#      prompt strings. Nothing was written. Amendment: --dedupe-prompts,
#      pre-registered in the learning log before this resubmission.)
#   1. Fresh draw: --seed 20260917 --pool-seed 20260827 (same six-city pool)
#      --n-dev 0 --n-heldout 60 --id-prefix h2- --dedupe-prompts. Written ONLY to
#      results/datasets/heldout2.jsonl (+ heldout2-manifest.json,
#      heldout2-tokenization_report.json). heldout.jsonl is not touched.
#   2. Behavioural eligibility screen on heldout2 (same script, same
#      thresholds, --frozen-eval). GPU architecture is printed by nvidia-smi
#      and recorded in the run manifest.
#   3. experiments/stage3/heldout_frozen.py --heldout results/datasets/heldout2.jsonl
#      (all three arms, label-permutation + random-transport controls, output
#      shadow at every position; dev is re-scored only because arm 3's mu is
#      fit on dev inside that script, exactly as in the application run).
#
#SBATCH -A agents4research
#SBATCH -p l40s_normal_q
#SBATCH --gres=gpu:1
#SBATCH -c 2
#SBATCH --mem=24G
#SBATCH -t 01:30:00
#SBATCH -J mats12-p1s1
#SBATCH -o /scratch/djjay/mats12/repo/results/slurm-logs/phase1-step1-%j.out
#SBATCH -e /scratch/djjay/mats12/repo/results/slurm-logs/phase1-step1-%j.out
set -uo pipefail
module reset
source /scratch/djjay/mats12/venv/bin/activate
export HF_HOME=/scratch/djjay/mats12/hf-cache
export PYTHONPATH=/scratch/djjay/mats12/repo/src
cd /scratch/djjay/mats12/repo

echo "=== node: $(hostname)  job: ${SLURM_JOB_ID:-none}  commit: $(git rev-parse --short HEAD) ==="
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
if [ -e results/datasets/heldout2.jsonl ]; then
    echo "REFUSING: results/datasets/heldout2.jsonl already exists; this draw happens once."
    exit 4
fi
TMP=$(mktemp -d /scratch/djjay/mats12/tmp-phase1-step1-XXXXXX)
echo "scratch: $TMP"

echo
echo "=== STEP 0/3: regression -- regenerate the original draw, require identical sha256 ==="
python src/make_dataset.py --out "$TMP/orig"
rc0=$?
python - "$TMP/orig" <<'EOF'
import hashlib, json, sys
tmp = sys.argv[1]
want = json.load(open("results/datasets/dataset-manifest.json"))["sha256"]
ok = True
for name in ("dev.jsonl", "heldout.jsonl"):
    got = hashlib.sha256(open(f"{tmp}/{name}", "rb").read()).hexdigest()
    same = got == want[name]
    ok &= same
    print(f"  {name:14s} regenerated={got[:16]} manifest={want[name][:16]} {'IDENTICAL' if same else 'DIFFERENT'}")
    # and against the committed file itself
    cur = hashlib.sha256(open(f"results/datasets/{name}", "rb").read()).hexdigest()
    print(f"  {name:14s} committed  ={cur[:16]} {'matches manifest' if cur == want[name] else 'DOES NOT MATCH MANIFEST'}")
sys.exit(0 if ok else 5)
EOF
rcr=$?
echo "regression exit=$rc0/$rcr"
if [ "$rc0" != "0" ] || [ "$rcr" != "0" ]; then
    echo "=== STOP: generator regression failed; nothing drawn, nothing scored ==="
    exit 5
fi

echo
echo "=== STEP 1/3: fresh draw seed=20260917 pool_seed=20260827 n_heldout=60 ==="
python src/make_dataset.py --out "$TMP/h2" --seed 20260917 --pool-seed 20260827 \
    --n-dev 0 --n-heldout 60 --id-prefix h2- --dedupe-prompts
rc1=$?
echo "draw exit=$rc1"
if [ "$rc1" != "0" ]; then
    echo "=== STOP: draw failed (self-check or tokenizer); nothing scored ==="
    exit 6
fi
cp "$TMP/h2/heldout.jsonl" results/datasets/heldout2.jsonl
cp "$TMP/h2/manifest.json" results/datasets/heldout2-manifest.json
cp "$TMP/h2/tokenization_report.json" results/datasets/heldout2-tokenization_report.json
sha256sum results/datasets/heldout2.jsonl results/datasets/heldout.jsonl results/datasets/dev.jsonl
echo "heldout2: $(grep -vc '\"_meta\"' results/datasets/heldout2.jsonl) records"

echo
echo "=== STEP 2/3: behavioural eligibility screen on results/datasets/heldout2.jsonl ==="
python experiments/design-verification/eligibility_screen.py \
    --dataset results/datasets/heldout2.jsonl --frozen-eval
rc2=$?
echo "screen exit=$rc2"

echo
echo "=== STEP 3/3: frozen evaluation on heldout2 (dev re-scored for arm 3 mu only) ==="
python experiments/stage3/heldout_frozen.py --heldout results/datasets/heldout2.jsonl
rc3=$?
echo "frozen-eval exit=$rc3"

echo
echo "=== PHASE 1 STEP 1 COMPLETE (regression rc=$rcr, draw rc=$rc1, screen rc=$rc2, eval rc=$rc3) ==="
ls -d results/runs/*/ 2>/dev/null | tail -3
