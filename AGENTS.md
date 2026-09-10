# AGENTS.md

This project's agent instructions live in **[`CLAUDE.md`](CLAUDE.md)**. Read
that file first — it is authoritative for every agent, not only Claude Code.

The three things most often got wrong here:

1. **Load `context/default_600k.md`** into your context window before
   starting work (ADV-11). It is committed, so a fresh clone has it.
2. **Use the persistent IPython kernel in the `mats-12-application` tmux
   session on the `agents4research` VM** — not on the Mac, and not on the ARC
   login node. Never restart it without asking. Save every plot as a PNG.
   Topology: `llm/memory_bank/techContext.md` §Topology.
3. **Never present your own output as a verified result.** Every number that
   reaches the write-up is re-derived by Jason via a path that does not share
   the original pipeline's code, and logged in
   `llm/application/verification-ledger.md`. Unverified agent results are
   disqualifying for this application.

<!-- BEGIN agentic-governance: repository layout -->
See `CLAUDE.md`. It carries this repository's agent instructions —
the two-plane rule (`llm/` control plane, `docs/` data
plane), the Q1/Q2 pre-write decision procedure, the tool-contract
exemption class, and the output-location preferences for design
specs and implementation plans.

This file exists because some tools read `AGENTS.md` rather than
`CLAUDE.md` (`obra/superpowers` `using-superpowers/SKILL.md` names
both). It restates no policy of its own; `CLAUDE.md` is the only
copy.
<!-- END agentic-governance: repository layout -->
