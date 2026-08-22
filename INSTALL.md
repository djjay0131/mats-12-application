# Dropping this into ~/code/mats-12-application

The directory scaffold and the ported agents/skills are already on your Mac
from the earlier setup pass. This bundle carries the document layer.

```bash
cd ~/code/mats-12-application
tar xzf ~/Downloads/mats-12-application-docs.tar.gz --strip-components=0
```

Then verify and commit:

```bash
node ~/code/agentic-governance/governance/scripts/governance-checks.mjs
git add -A
git commit -m "Establish repo: governance v0.2, paper agents, plan, literature scan"
```

To create the remote (I have no GitHub auth from the cloud session):

```bash
gh repo create djjay0131/mats-12-application --private --source . --push
gh label create gov-L0 --color BFBFBF --description "Administrative, non-semantic"
gh label create gov-L1 --color 1D76DB --description "Semantic, local"
gh label create gov-L2 --color D93F0B --description "Architectural"
gh label create gov-L3 --color B60205 --description "Product / affects submission"
gh label create phase-0-select --color 0E8A16
gh label create phase-1-execute --color 0E8A16
gh label create phase-2-writeup --color 0E8A16
gh label create phase-3-submit --color 0E8A16
gh label create counted-time --color FBCA04 --description "Consumes the 20-hour budget"
gh label create needs-baseline --color E99695 --description "Claim without its control"
gh label create agent-unverified --color E99695 --description "Agent output no human re-derived"
```

Then record what branch protection actually enforces in
`docs/governance-delta.md` — run
`gh api repos/djjay0131/mats-12-application/branches/main/protection` and
write down the real answer (a 403 on a private free-plan repo means
unavailable). ADR-0001 accepts convention-only enforcement for this repo,
so a 403 is a fine outcome — just record it rather than leaving the
section aspirational.
