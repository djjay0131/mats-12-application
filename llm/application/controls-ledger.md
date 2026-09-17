# Controls Ledger

One row per claim, naming the cheap control that was actually run.
Checked by `scripts/conformance-check.mjs` (BLK-12).

Neel lists **"Failing to compare to baselines"** among the disqualifying
mistakes, and names the cheap ones directly:

> "eg replace your vector with a random one, choose randomly, ask an LLM,
> use a linear probe"

| Claim ID | Claim | Control run | What it would have shown if spurious | Result | Where |
|---|---|---|---|---|---|
| CL-01 | J-Lens recovers the intermediate at the final token | Output-shadow control: captured the model's own next-token distribution (the baseline the apparent recovery is compared against) in the same forward pass; plus independent hand re-derivation | The "recovery" is the output forming | Spurious as a binding claim: model already prefers it 37/40, r=0.77 vs 0.81 anchor. Headline retired | writeup §4.2a; `results/verification/verify-shadow-554518.out` |
| CL-02 | Direction resolves at the relation-completing token and question mark | Label permutation per position; norm-matched random transport; anchors+layers frozen pre-read; held-out read once | Forking paths from the position sweep | Real: 0.781/0.669 vs 0.519/0.556 control on 160 unseen records, all six templates | writeup §4.2c; `results/stage2/FREEZE.md` |
| CL-03 | The window signal is latent binding | Measured the model's own preference AT those positions; scored lenses on the 32-40 records where it points wrong | Lens beats the preference where they disagree | It does not: 0.125-0.344, below chance. Signal is the developing output preference | writeup §4.2c; `experiments/analysis/window_shadow_audit.py` |
| CL-04 | J-Lens localizes concepts far above the logit lens (rank) | Random transport (rank ~150k); label permutation; coverage positive control (reference eval pass@10 0.350 vs 0.200) | A pipeline or coverage artifact | Stands, with the six-city collision caveat attached to held-out controls | writeup §4.4 |
| CL-05 | Binding is not linearly present beyond the preference at these positions | Supervised difference-in-means probe (the linear-probe control Neel names), fit on dev, applied unchanged to held-out | Lenses merely weak, signal present | Probe = preference rate at qmark (0.725→0.731); reads nothing at relcomp (0.525) | writeup §2.5, §4.2c |
| CL-06 | "Just ask the model" bound | Direct prompting = the eligibility screen itself | Task illegible without internals | 90-100% by architecture; prompting dominates every internal readout on this task | writeup §4.1 |

Cut controls (10, 11) and the unrun resample variant are documented with
reasons and the standing objection in writeup §2.5 — cut before results, not
after.
