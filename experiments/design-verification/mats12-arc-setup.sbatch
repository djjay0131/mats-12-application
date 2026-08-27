#!/bin/bash
#SBATCH --job-name=mats12-arc-setup
#SBATCH --account=agents4research
#SBATCH --partition=l40s_normal_q
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --output=mats12-arc-setup-%j.out
#SBATCH --error=mats12-arc-setup-%j.err

# SETUP ONLY (uncounted): build the J-Lens environment on an ARC compute node,
# stage model + lens into /scratch, and verify EXACT model/tokenizer/lens match.
# Deliberately does NOT compute any J-Lens readout -- that is counted V1.

set -euo pipefail

BASE=/scratch/$USER/mats12
VENV=$BASE/venv
export HF_HOME=$BASE/hf-cache
VENDOR=$BASE/vendor
JLENS_COMMIT=581d398613e5602a5af361e1c34d3a92ea82ba8e
MODEL_ID="Qwen/Qwen3.5-4B"
MODEL_REV="851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a"
LENS_REPO="neuronpedia/jacobian-lens"
LENS_REV="qwen-n1000"
LENS_FILE="qwen3.5-4b/jlens/Salesforce-wikitext/Qwen3.5-4B_jacobian_lens_n1000.pt"

echo "=== MATS12 ARC SETUP ==="
echo "date_utc:   $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "host:       $(hostname)"
echo "job:        ${SLURM_JOB_ID:-<unset>}"
echo "account:    ${SLURM_JOB_ACCOUNT:-<unset>}"
echo "partition:  ${SLURM_JOB_PARTITION:-<unset>}"
echo "base:       $BASE"
echo "HF_HOME:    $HF_HOME"

echo "--- GPU ---"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

mkdir -p "$BASE" "$VENDOR" "$HF_HOME"

echo "--- module load ---"
# NOTE: do NOT 'module purge' -- it drops the apps/DefaultModules paths that
# provide the EasyBuild tree, making Python/* unknown on the compute node.
module reset 2>/dev/null || true
PYMOD=""
for cand in \
    Python/3.12.3-GCCcore-13.3.0 \
    Python/3.11.5-GCCcore-13.2.0 \
    Python/3.11.3-GCCcore-12.3.0 \
    Python/3.13.5-GCCcore-14.3.0 ; do
    if module load "$cand" 2>/dev/null; then PYMOD="$cand"; break; fi
done
if [ -z "$PYMOD" ]; then
    echo "BLOCKER: no EasyBuild Python module could be loaded on this node."
    module --terse avail Python 2>&1 | head -20
    exit 4
fi
echo "  loaded module: $PYMOD"
echo "  python3: $(python3 --version 2>&1) at $(command -v python3)"
python3 - <<'PYCHK'
import sys
assert sys.version_info >= (3, 10), f"jlens requires >=3.10, got {sys.version}"
print("  python_version_ok:", sys.version.split()[0])
PYCHK

echo "--- network reachability from compute node ---"
NET_OK=1
curl -sS -m 20 -o /dev/null -w "  pypi=%{http_code}\n" https://pypi.org/simple/ || NET_OK=0
curl -sS -m 20 -o /dev/null -w "  hf=%{http_code}\n"   https://huggingface.co || NET_OK=0
curl -sS -m 20 -o /dev/null -w "  gh=%{http_code}\n"   https://github.com || NET_OK=0
echo "  NET_OK=$NET_OK"
if [ "$NET_OK" -ne 1 ]; then
    echo "BLOCKER: compute node has no outbound network; staging must move to login node."
    exit 3
fi

echo "--- venv ---"
if [ ! -x "$VENV/bin/python" ]; then
    python3 -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install --quiet --upgrade pip
echo "  pip: $("$VENV/bin/python" -m pip --version)"

echo "--- install stack (CUDA torch) ---"
"$VENV/bin/python" -m pip install --quiet \
    torch "transformers>=5.5" huggingface_hub numpy safetensors scikit-learn pytest

echo "--- vendor jlens @ pinned commit ---"
if [ ! -d "$VENDOR/jacobian-lens/.git" ]; then
    git clone --quiet https://github.com/anthropics/jacobian-lens.git "$VENDOR/jacobian-lens"
fi
cd "$VENDOR/jacobian-lens"
git fetch --quiet origin || true
git checkout --quiet "$JLENS_COMMIT"
echo "  jlens HEAD: $(git rev-parse HEAD)"
"$VENV/bin/python" -m pip install --quiet -e . --no-deps

echo "--- reference test suite ---"
"$VENV/bin/python" -m pytest tests/ -q 2>&1 | tail -3

echo "--- stage model + lens into scratch ---"
"$VENV/bin/python" - <<PYEOF
import os, time
from huggingface_hub import snapshot_download
t0=time.time()
mp = snapshot_download("${MODEL_ID}", revision="${MODEL_REV}",
                       allow_patterns=["*.safetensors*","*.json","*.txt","*.jinja"])
print("  MODEL_PATH:", mp)
print("  model_stage_secs: %.1f" % (time.time()-t0))
t1=time.time()
lp = snapshot_download("${LENS_REPO}", revision="${LENS_REV}",
                       allow_patterns=["qwen3.5-4b/jlens/Salesforce-wikitext/*"])
print("  LENS_PATH:", lp)
print("  lens_stage_secs: %.1f" % (time.time()-t1))
PYEOF

echo "--- EXACT COMPATIBILITY VERIFICATION ---"
cd "$BASE"
"$VENV/bin/python" - <<PYEOF
import hashlib, json, os, torch, transformers, jlens
from jlens import JacobianLens
from huggingface_hub import snapshot_download

print("torch:            ", torch.__version__)
print("torch.version.cuda:", torch.version.cuda)
print("cuda_available:   ", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device_name:      ", torch.cuda.get_device_name(0))
    print("device_capability:", torch.cuda.get_device_capability(0))
    print("device_mem_GB:    %.1f" % (torch.cuda.get_device_properties(0).total_memory/1e9))
print("transformers:     ", transformers.__version__)

mp = snapshot_download("${MODEL_ID}", revision="${MODEL_REV}",
                       allow_patterns=["*.safetensors*","*.json","*.txt","*.jinja"])
lp = snapshot_download("${LENS_REPO}", revision="${LENS_REV}",
                       allow_patterns=["qwen3.5-4b/jlens/Salesforce-wikitext/*"])
lens_path = os.path.join(lp, "${LENS_FILE}")

# lens identity
h = hashlib.sha256(open(lens_path,'rb').read()).hexdigest()
print("lens_sha256:      ", h)
print("lens_bytes:       ", os.path.getsize(lens_path))
lens = JacobianLens.load(lens_path)
print("lens_d_model:     ", lens.d_model)
print("lens_n_prompts:   ", lens.n_prompts)
print("lens_source_layers:", lens.source_layers[0], "..", lens.source_layers[-1],
      "(n=%d)" % len(lens.source_layers))

# lens provenance
cfg_yaml = os.path.join(lp, "qwen3.5-4b/jlens/Salesforce-wikitext/config.yaml")
hf_name = None
for line in open(cfg_yaml):
    if line.startswith("hf_model_name:"):
        hf_name = line.split(":",1)[1].strip().strip('"')
print("lens_fit_against: ", hf_name)

# model identity
cfg = json.load(open(os.path.join(mp, "config.json")))
tcfg = cfg.get("text_config", cfg)
print("model_arch:       ", cfg.get("architectures"))
print("model_layers:     ", tcfg["num_hidden_layers"])
print("model_hidden:     ", tcfg["hidden_size"])
print("model_vocab:      ", tcfg["vocab_size"])

tok = transformers.AutoTokenizer.from_pretrained(mp)
print("tokenizer_class:  ", type(tok).__name__)
print("tokenizer_vocab:  ", tok.vocab_size, "len:", len(tok))

# hard assertions
assert hf_name == "${MODEL_ID}", f"lens fit against {hf_name}, not ${MODEL_ID}"
assert lens.d_model == tcfg["hidden_size"], "d_model mismatch"
assert max(lens.source_layers) < tcfg["num_hidden_layers"], "lens layers exceed model depth"
print("COMPAT_ASSERTIONS: PASS")

# layout resolution + GPU residency (NO lens readout -- that is V1)
t = __import__("time").time()
hf_model = transformers.AutoModelForCausalLM.from_pretrained(mp, dtype=torch.bfloat16).cuda()
print("model_load_secs:  %.1f" % (__import__("time").time()-t))
m = jlens.from_hf(hf_model, tok)
print("lens_model:       ", repr(m))
assert m.d_model == lens.d_model
assert m.n_layers == tcfg["num_hidden_layers"]
print("peak_gpu_alloc_GB: %.2f" % (torch.cuda.max_memory_allocated()/1e9))
print("LAYOUT_ASSERTIONS: PASS")
PYEOF

echo "--- disk usage ---"
du -sh "$BASE" "$HF_HOME" 2>/dev/null || true

echo "=== SETUP COMPLETE ==="
