#!/usr/bin/env bash
# Install the repo's git hooks into .git/hooks. Run once per clone.
set -euo pipefail
cd "$(dirname "$0")/.."
install -m 0755 scripts/hooks/pre-commit .git/hooks/pre-commit
echo "installed .git/hooks/pre-commit  (rebuilds writeup/mats12-report.docx when the markdown changes)"
