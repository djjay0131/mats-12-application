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
