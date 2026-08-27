# Note on this run

Job 550555 on fal045 (L40S). Commit 11aa27c.

## The manifest says dirty=true. It is a false positive, and here is the proof.

`git.dirty_files` in manifest.json lists exactly two paths:

    ?? results/runs/20260827T090437Z-eligibility-screen/
    ?? results/slurm-logs/gate1-550555.out

Both are this run's own output paths. `runlog.start_run()` created the run
directory and *then* read `git status`, so every run dirtied the tree with its
own artifacts before inspecting it. No source file differed from 11aa27c.

Fixed after this run: `_git()` is now called before `outputs.mkdir()`. Runs from
the next commit onward report dirty=true only when it means something. This run
and 20260827T093224Z-v1-tooling-verification predate the fix; the dirty_files
list is what makes them auditable, which is why it is recorded.

## This is the third eligibility screen. The first two were invalid.

- Run 1 (20260827T055318Z): `max_new_tokens=4`, consumed entirely by the
  `<think>` tag. Measured nothing.
- Run 2 (20260827T081208Z): token budget fixed, but scoring took the first word
  of the generation, which is "Based" (from "Based on the facts provided:").
  The number came out near-identical to run 1 by coincidence. Measured the
  parser, not the model.
- Run 3 (this one): content-based and strict-bolded-span scoring, which agree
  with each other (0.950 / 0.883 on real-zero). `first_word_accuracy` is kept
  in the output as the record of the broken rule: 0.108.

Runs 1 and 2 are kept on disk. They are not deleted, and their numbers are not
reported anywhere as results.
