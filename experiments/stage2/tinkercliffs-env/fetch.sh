#!/bin/bash
set -uo pipefail
export HF_HOME=/home/djjay/mats12-tc/hf-cache
BIN=/home/djjay/mats12-tc/venv/bin/hf
mkdir -p "$HF_HOME"
echo "=== MODEL ==="
"$BIN" download Qwen/Qwen3.5-4B \
  --revision 851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a
echo "=== MODEL_RC=$? ==="
echo "=== LENS ==="
"$BIN" download neuronpedia/jacobian-lens \
  --revision qwen-n1000 \
  qwen3.5-4b/jlens/Salesforce-wikitext/Qwen3.5-4B_jacobian_lens_n1000.pt
echo "=== LENS_RC=$? ==="
echo "=== FETCH_ALL_DONE ==="
