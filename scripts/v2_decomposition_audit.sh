#!/bin/bash
# V2 -- can "J-space versus non-J-space" be operationalised with what ships?
#
# Blocker B2 asks whether the released implementation provides the sparse
# non-negative J-space reconstruction the method's framing depends on. This
# script answers it by looking, and prints its own evidence so the answer can
# be checked rather than taken on trust. It is grep over a pinned vendor tree;
# it computes nothing and it decides nothing.
#
# The FAIL condition V2 declares for itself is implementing "J-space" as an
# arbitrary top-token projection with no correspondence to the paper's sparse
# construction. This audit exists so that condition is never reached by
# accident.
set -uo pipefail
VENDOR=${VENDOR:-/scratch/djjay/mats12/vendor/jacobian-lens}

echo "vendor: $VENDOR"
echo "commit: $(cd "$VENDOR" && git rev-parse HEAD 2>/dev/null || echo unknown)"
echo "version: $(grep -m1 '^Version:' "$VENDOR"/jlens.egg-info/PKG-INFO 2>/dev/null || echo unknown)"
echo "modules:"
wc -l "$VENDOR"/jlens/*.py

PATTERN='nonneg|non_neg|non-neg|sparse|nnls|lasso|omp_|matching_pursuit|dictionary|decompos|reconstruct|j_space|jspace'

for target in "$VENDOR/jlens" "$VENDOR/README.md" "$VENDOR/walkthrough.ipynb" "$VENDOR/tests"; do
  echo
  echo "--- grep -rniE '$PATTERN' $(basename "$target")"
  n=$(grep -rniE "$PATTERN" "$target" 2>/dev/null | wc -l)
  grep -rniE "$PATTERN" "$target" 2>/dev/null | head -20
  echo "matches: $n"
done

echo
echo "--- public API"
grep -n '__all__' -A 20 "$VENDOR/jlens/__init__.py" 2>/dev/null
