#!/usr/bin/env bash
# One-shot: create the private GitHub repo, push main, instantiate the label
# taxonomy, and probe what branch protection actually enforces.
#
# Run this on your Mac (not in a Claude session — it needs your gh auth):
#   cd ~/code/mats-12-application && ./scripts/push-to-github.sh
#
# ADR-0001 accepts convention-only enforcement for this repo, so this script
# deliberately does NOT apply branch protection. It probes and reports, so the
# real answer can be recorded in docs/governance-delta.md instead of assumed.

set -euo pipefail
OWNER=djjay0131
NAME=mats-12-application

command -v gh >/dev/null || {
  echo "gh not found. Install with: brew install gh && gh auth login"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "Run: gh auth login"; exit 1; }

echo "==> creating $OWNER/$NAME (private)"
if gh repo view "$OWNER/$NAME" >/dev/null 2>&1; then
  echo "    already exists — adding remote and pushing"
  git remote get-url origin >/dev/null 2>&1 || \
    git remote add origin "https://github.com/$OWNER/$NAME.git"
  git push -u origin main
else
  gh repo create "$OWNER/$NAME" --private --source . --push \
    --description "MATS 12.0 application — Neel Nanda mech interp stream. Due 2026-09-04."
fi

echo "==> labels"
mk() { gh label create "$1" --color "$2" --description "$3" --force >/dev/null 2>&1 \
       && echo "    $1" || echo "    $1 (skipped)"; }
mk gov-L0            BFBFBF "Administrative, non-semantic"
mk gov-L1            1D76DB "Semantic, local"
mk gov-L2            D93F0B "Architectural — ADR required"
mk gov-L3            B60205 "Product / affects what we submit — ADR required"
mk phase-0-select    0E8A16 "Candidate scoping and de-risking"
mk phase-1-execute   0E8A16 "Counted experiment hours"
mk phase-2-writeup   0E8A16 "Main write-up"
mk phase-3-submit    0E8A16 "Executive summary and submission"
mk counted-time      FBCA04 "Consumes the 20-hour budget"
mk needs-baseline    E99695 "A claim without its control"
mk agent-unverified  E99695 "Agent output no human has re-derived"
mk blocker-open      B60205 "An open BLK-* requirement from the conformance register"
mk untyped-claim     E99695 "Claim not tagged existence-proof / method-claim"

echo "==> branch-protection reality probe"
code=$(gh api "repos/$OWNER/$NAME/branches/main/protection" \
       --silent -i 2>/dev/null | head -1 | awk '{print $2}' || true)
case "${code:-}" in
  200) echo "    protection IS configured — record the rules in the delta" ;;
  404) echo "    available but unconfigured (expected: ADR-0001 accepts convention-only)" ;;
  403) echo "    UNAVAILABLE — private repo on a free plan. Record this in the delta." ;;
  *)   echo "    inconclusive (HTTP ${code:-?}) — check by hand" ;;
esac

echo
echo "Now update the 'Platform Enforcement Reality' section of"
echo "docs/governance-delta.md with what you just saw — the point of that"
echo "section is that it says what is true, not what we hoped."
echo "Then: node scripts/conformance-check.mjs --gate SELECT"
