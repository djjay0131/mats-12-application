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
| `localization-by-position` | Median rank of the correct intermediate over the full vocabulary, J-Lens vs logit lens, at each readout position on the frozen held-out split. Lower is better. J-Lens's advantage is largest before the query (373 vs 76,276) and narrows as the model's own output preference arrives. | CL-02 | 160 | 20260827 | `2c04cac338c1` | b11ec5e | 2026-09-03 |  |
| `direction-vs-shadow` | Direction score (correct intermediate outranks its role-swapped twin) by position, held-out n=160. J-Lens and the logit lens both rise with, and to, the model's own next-token preference (dashed); the norm-matched random transport stays at chance. The apparent binding signal is an output shadow, not recovered binding. | CL-03 | 160 | 20260827 | `082c8f177ee1` | b11ec5e | 2026-09-03 |  |
| `supervised-ceiling` | Difference-in-means supervised probe (arm 3), fit on all dev records with labels in hand and applied unchanged to held-out (n=160). At the relation-completing token it reaches only 0.525 — chance — so binding is not linearly decodable there by any method; the accuracy it gains toward the final token is the same output shadow the passive readouts see. | CL-03 | 160 | 20260827 | `fb910dd6f255` | b11ec5e | 2026-09-03 |  |
| `stage3-controls` | Experiment 2 controls on frozen held-out data (n=160). Shuffling the answer key drops J-Lens to chance; replacing the trained matrix with a random one drops both the direction score to chance and the median rank of the correct city from tens to over a hundred thousand. | CL-02, CL-04 | 160 | 20260827 | `a3cf394362b5` | 1b3da50 | 2026-09-05 | job 554591; label-permutation control and norm-matched random transport |
