# Note on this run

Job 550555 on fal045 (L40S), same allocation as the eligibility screen that
precedes it. Commit 11aa27c.

`git.dirty=true` in manifest.json is a false positive of the same kind
described in results/runs/20260827T090437Z-eligibility-screen/NOTE.md: the run
directory was created before `git status` was read. `git.dirty_files` lists only
this run's own output paths.

V1 had already returned PASS on the same commit in the previous allocation
(20260827T082947Z). This execution is the one that ran alongside the valid
eligibility screen, and is the one cited.
