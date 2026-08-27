# AGENTS.md

This project's agent instructions live in **[`CLAUDE.md`](CLAUDE.md)**. Read
that file first — it is authoritative for every agent, not only Claude Code.

The three things most often got wrong here:

1. **Load `context/default_600k.md`** into your context window before
   starting work (ADV-11). It is gitignored; if absent, fetch it from the
   Drive folder linked in `llm/application/mats12-instructions-raw.txt`.
2. **Use the persistent IPython kernel in the `mats-12-application` tmux
   session.** Never restart it without asking. Save every plot as a PNG.
3. **Never present your own output as a verified result.** Every number that
   reaches the write-up is re-derived by Jason via a path that does not share
   the original pipeline's code, and logged in
   `llm/application/verification-ledger.md`. Unverified agent results are
   disqualifying for this application.
