# V2 — Representation-decomposition verification: DOCUMENTED NEGATIVE

**This is a method evaluation using a narrow task as an instrument, not circuit
discovery.** The finding below is about the released artifact of a method, and
it is reported as a result rather than as a gap in this project's execution.

Run record: `results/runs/20260827T153925Z-stage1-passive-readout/` (job 550690,
step 0, node fal009). The audit script is `scripts/v2_decomposition_audit.sh`
and prints its own evidence so the answer can be checked rather than trusted.
It was run inside a Slurm job rather than a login shell, and it computes
nothing.

## The question V2 asks

> Can we operationalize "J-space versus non-J-space" without smuggling the
> desired conclusion into the decomposition?

The sprint's first required test is to *"implement or reuse the paper's sparse
non-negative J-space reconstruction"*. Blocker B2 asked whether that
reconstruction is available.

## The answer

It is not available, and not partially available. It is absent.

Vendor tree pinned at commit `581d398613e5602a5af361e1c34d3a92ea82ba8e`,
`jlens` version 0.1.0, companion code for *"Verbalizable Representations Form a
Global Workspace in Language Models"*. 1,713 lines across nine modules.

Searching for `nonneg|non_neg|non-neg|sparse|nnls|lasso|omp_|matching_pursuit|dictionary|decompos|reconstruct|j_space|jspace`, case-insensitive:

| target | matches |
|---|---|
| `jlens/` (the package, 1,713 lines) | **0** |
| `README.md` | **0** |
| `walkthrough.ipynb` | **0** |
| `tests/` | **0** |

The complete public API is:

```
ActivationRecorder, HFLensModel, JacobianLens, Layout, LensModel,
configure_logging, fit, from_hf, jacobian_for_prompt
```

Fit a lens, apply it, transport a residual, visualise the result. There is no
decomposition of any kind, so there is nothing to reuse and nothing to verify
against.

## What follows

**The causal arm (H3) is declared unavailable, not deferred.** ADR-0004 gate 2
provided for exactly this outcome ("or declare explicit passive-only scope") and
ADR-0005 already scoped the project passive-primary. H1, H2 and H4 are the
deliverable and none of them depend on the decomposition.

V2's own FAIL condition is worth quoting against the alternative that was
available:

> "J-space" is implemented as an arbitrary top-token projection with no
> correspondence to the paper's sparse construction.

Building a stand-in and calling it J-space would have satisfied the letter of
the sprint and produced numbers. It would also have meant evaluating a method
against a component this project invented, which is not an evaluation of that
method. **It was not done and will not be done.**

## Why this is a finding rather than an absence

The method's framing invites a causal claim: that a verbalizable workspace can
be separated from the rest of the residual stream and intervened on. Testing
that claim requires separating J-space from non-J-space. The released
implementation provides no way to do it.

That gap is only visible to someone who tries to use the tool for the thing its
framing implies, which is what a method evaluation is for. It is reported here
with its evidence and its command, so a reader can re-run the audit and
disagree.

## What this does NOT claim

- Not that the reconstruction does not exist. It may exist in the authors'
  internal code, in a future release, or be reconstructible from the paper's
  text. This audit covers exactly one pinned commit of one released repository,
  and says so.
- Not that the method is wrong. The passive readout it does support is measured
  in Stage 1, against its own controls.
- Not that a decomposition is impossible to write. It is that writing one here
  would make this project the author of the component under test.

## Consequences already applied

- Control 8 in the write-up is split: **8a** norm-matched random *transport*
  runs as a live passive control in Stage 1; **8b** norm-matched random
  *direction* as an intervention is unavailable along with the causal arm.
- The B3 fallback (no published shuffled-corpus lens exists) now rests on label
  permutation plus norm-matched random transport — both passive, both reachable,
  both run.
- §2.5 of `writeup/main.md` carries this finding and its FAIL-condition
  reasoning.

Status: `agent-unverified`. The grep is reproducible in seconds; that is the
point of publishing the command rather than the conclusion.
