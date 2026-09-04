#!/usr/bin/env bash
# Assemble the MATS write-up into Word format, then check it against the rules.
#
#   ./scripts/build-report.sh            build + check
#   ./scripts/build-report.sh --pdf      also render a PDF and page images
#
# The report is authored as markdown (writeup/exec-summary.md, writeup/main.md)
# and compiled to .docx. That is deliberate: the source stays diffable and
# reviewable in git, figures are picked up from results/figures/ on every
# build, and scripts/conformance-check.mjs reads the same two files it reads
# for the gates. Do not hand-edit the .docx — it is a build artifact and the
# next build overwrites it.

set -euo pipefail
cd "$(dirname "$0")/.."
OUT=writeup/mats12-report.docx
BUILD=writeup/.build
mkdir -p "$BUILD"

command -v pandoc >/dev/null || { echo "pandoc not found"; exit 1; }

# --- 1. missing figures are a warning, not a failure: the report is built
#        repeatedly while results are still arriving.
missing=0
while read -r f; do
  [ -z "$f" ] && continue
  [ -f "$f" ] || { echo "  missing figure: $f"; missing=$((missing+1)); }
done < <(grep -ho '!\[[^]]*\](\([^)]*\))' writeup/*.md 2>/dev/null | sed 's/.*(\(.*\))/\1/' || true)
[ "$missing" -gt 0 ] && echo "==> $missing figure(s) not yet generated (expected mid-sprint)"

# --- 2. assemble: exec summary first, per the submission format
cat writeup/exec-summary.md > "$BUILD/report.md"
printf '\n\n\\newpage\n\n' >> "$BUILD/report.md"
cat writeup/main.md >> "$BUILD/report.md"

# --- 3. strip the authoring comments so they never reach the reader
python3 - "$BUILD/report.md" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p).read()
s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
s = re.sub(r'\n{3,}', '\n\n', s)
open(p, 'w').write(s)
PY

pandoc "$BUILD/report.md" \
  --from=markdown+yaml_metadata_block+pipe_tables \
  --to=docx \
  --resource-path=.:writeup \
  --reference-doc=writeup/reference.docx \
  --output="$OUT"
echo "==> $OUT"

# --- 4. the two hard mechanical limits on the executive summary
python3 - <<'PY'
import re, pathlib
s = pathlib.Path('writeup/exec-summary.md').read_text()
s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
s = re.sub(r'^---.*?^---', '', s, flags=re.S | re.M)      # yaml block
s = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', s)                 # images
n = len(re.findall(r"\b[\w'’-]+\b", s))
imgs = len(re.findall(r'!\[', pathlib.Path('writeup/exec-summary.md').read_text()))
print(f"==> exec summary: {n} words (limit 600), {imgs} figure reference(s)")
if n > 600: print("    FAIL MEC-06 — over the 600-word limit")
if imgs == 0: print("    FAIL MEC-07 — no graphs; he asks for them explicitly")
PY

# --- 5. optional visual check: render and look at it
if [ "${1:-}" = "--pdf" ]; then
  soffice --headless --convert-to pdf --outdir "$BUILD" "$OUT" >/dev/null 2>&1
  pdftoppm -jpeg -r 100 "$BUILD/$(basename "${OUT%.docx}").pdf" "$BUILD/page" 2>/dev/null || true
  echo "==> page images: $BUILD/page-*.jpg   (exec summary must fit in 3)"
  ls "$BUILD"/page-*.jpg 2>/dev/null | wc -l | xargs echo "    total pages:"
fi

# --- 6. the rest of the rules
echo
node scripts/conformance-check.mjs --gate WRITEUP 2>&1 | tail -20
