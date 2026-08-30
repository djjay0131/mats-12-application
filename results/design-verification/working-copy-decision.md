# Working-copy location decision

Date: 2026-08-26
Decided by: agent, during execution setup (uncounted)
Status: Active
Related: `llm/memory_bank/techContext.md` §Topology, `results/design-verification/environment-manifest.md`

> This is a setup/logistics record, not a research result. It contains no
> measurements.

## Decision

**The working copy lives on ARC, at `/scratch/djjay/mats12/repo`.**

The VM clone at `/home/djjay/code/mats-12-application` is retained as the
**git gateway only** — it is where `git commit` / `git push` run, because that
is where the GitHub credential lives. It is not edited by hand.

Single-authority rule, to avoid the two-clone collision the brief warns about:

| Direction | What moves | Mechanism |
|---|---|---|
| VM → ARC | initial seed only | `rsync -az` (done once, this file's commit) |
| ARC → VM | all code, results, writeup edits | `rsync -az` before each commit |
| VM → GitHub | commits | `git push` from the VM |

At no point are the same paths edited in both places. ARC is authoritative for
content; the VM is authoritative for history.

## Why ARC rather than the VM

1. **The GPU is there and nothing else is.** The model and lens only load on an
   ARC compute node. The VM has no CUDA device (blocker B1). Code that is
   edited on the VM has to cross to ARC before it can be run at all, so every
   edit-run cycle would pay a transfer.
2. **The staged data is already there and is large.** `/scratch/djjay/mats12`
   holds a 9.5 GB HF cache, a 5.0 GB venv, and the vendored reference
   implementation. Moving the code to the data is cheap; the reverse is not
   possible.
3. **`/scratch` has room.** 720 T available; the repo is 5.7 MB.
4. **The VM clone is not idle.** A separate agent session is live in tmux
   window `0:claude` with that clone as its working directory. Editing the same
   paths from a second process is exactly the collision to avoid.

## Why not clone directly from GitHub onto ARC

The repository is private. Cloning on ARC would mean placing a GitHub
credential on a shared university cluster. `rsync` over the existing
agent-forwarded SSH hop achieves the same result and puts no secret on ARC.
This was a deliberate choice, not an oversight.

## Caveats carried forward

- **`/scratch` is not backed up and may be subject to purge policy.** GitHub
  plus the VM clone are the durable copies. Nothing may exist only on
  `/scratch`.
- The SSH agent that authorises the VM → ARC hop is a socket at
  `~/.ssh/agent.sock` on the VM. It does not survive a VM reboot; the key must
  be re-added if the hop starts refusing.

## Branch correction made at the same time

The VM clone was checked out on `exp/jlens-design-verification`, which is
**9 commits behind `main`** and predates ADR-0005, the context audit,
`llm/memory_bank/techContext.md`, `context/default_600k.md`, `AGENTS.md` and
`scripts/build-report.sh`. Every path named in the execution brief resolves on
`main` and none of the moved ones resolved on the exp branch.

`git merge-base --is-ancestor HEAD origin/main` confirmed the exp branch had
**zero unique commits** and was a strict ancestor, and the tree was clean, so
fast-forwarding to `main` was lossless. Both copies are now on `main` at
`b138b88`.

Note that the open draft PR #4 (from the other agent session) is based on the
older branch point.
