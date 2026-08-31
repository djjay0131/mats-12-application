# Figure Registry

Every figure in the write-up, written by `src/figstyle.py::save_figure`.
Rows are rewritten in place when a figure is regenerated, so the sha and
commit always describe the file currently on disk.

A figure with no claim id has no reason to be in the report. A number in
the report that traces to no figure or table is caught separately by
`scripts/conformance-check.mjs` (BLK-24).

| Slug | Caption | Claim | n | Seed | SHA-256 (12) | Commit | Date | Notes |
|---|---|---|---|---|---|---|---|---|
| `binding-accuracy-by-method` | Pairwise binding accuracy by method, bootstrap 95% CIs. Chance 50%. | CL-02 | 40 held-out pairs | 1337 | `c7ae75133c6c` | 7d250c2 | 2026-08-26 | PLACEHOLDER DATA |
| `layerwise-margin` | Correct-minus-alternative margin across the layer band. | CL-03 | 40 held-out pairs | 1337 | `85af96c2f933` | 7d250c2 | 2026-08-26 | PLACEHOLDER DATA |
| `controls-panel` | Binding accuracy under relation deletion, truncation, and label permutation. | CL-04 | 40 held-out pairs | 1337 | `430d1219fed5` | 7d250c2 | 2026-08-26 | PLACEHOLDER DATA |
| `stage3-frac-by-position` | Direction score by position on frozen held-out; both lenses rise with, and to, the model's own next-token preference; random transport stays at chance. | CL-02, CL-03 | 160 | 20260827 | `ccdc19c7418a` | ded549f | 2026-08-31 | job 554591; freeze c5e9a5a |
| `stage3-discriminating-set` | Lens accuracy split by the sign of the model's own next-token preference at the same position; below chance on every preference-wrong cell. | CL-03 | 160 | 20260827 | `64ac0af2b6cd` | ded549f | 2026-08-31 | job 554591 + window_shadow_audit |
