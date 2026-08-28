# Cross-reference: readout success vs behavioural success — NOT COMPUTABLE

**Method evaluation using a narrow task as instrument; not circuit discovery.**

Script: `experiments/analysis/xref_readout_vs_behaviour.py`. No GPU; reads two
committed run records and the dev split. Run on the git gateway VM, not through
`src/runlog.py` — it is a static analysis of committed artifacts, and it is
recorded here rather than given a fabricated run directory.

## The question

Does the J-Lens readout recover the correct intermediate on pairs the **model
answers wrongly**? The two outcomes point opposite ways:

- readout right where behaviour is wrong → the readout sees something behaviour
  does not, a stronger claim than the current headline;
- readout fails exactly where behaviour fails → direct support for the
  answer-shadow account, i.e. the readout may be reporting the computed answer
  rather than the binding it routed through.

## The answer: it cannot be computed from committed data

```
eligibility real/zero variants : 120
stage-1 dev records (jlens)    : 40
prompts present in BOTH        :   4
selected layer                 :  27

                    readout RIGHT   readout WRONG
  model RIGHT                   4               0
  model WRONG                   0               0
```

**Zero discriminating cases.** The model answered all four shared prompts
correctly, so the comparison rules nothing in and nothing out.

## Why the overlap is 4 and not 40

The eligibility screen generated its own stimuli through
`task_templates.build_pairs(n_pairs=30)`. Stage 1 read `results/datasets/dev.jsonl`,
built separately by `src/make_dataset.py`. Same seed, different generators, so
the two prompt sets coincide only by accident — four times out of forty.

The join is on the **prompt string** precisely because the `pair_id` namespaces
are not known to agree. Joining on `pair_id` would have produced a confident
forty-row table built from mismatched stimuli. That failure would not have
announced itself.

## What this costs, and the fix

The cross-reference was proposed as the cheapest high-value next step. It is not
available, and the honest position is that the answer-shadow account in the
Hour 2 coach feedback remains untested rather than weakly supported.

**The fix is one line in the next run, not a new experiment.**
`lens.apply()` returns `(lens_logits, model_logits, input_ids)` and
`passive_readout.py` discarded `model_logits` with `_`. Keeping it records the
model's own next-token distribution at the readout position for every record, in
the same forward pass. The model's own answer-versus-alternative margin then
sits beside the lens's, per record, and the cross-reference becomes a property of
a single run rather than a join across two incompatible ones.

That change is made in `passive_readout.py` as of this commit. It costs nothing
and it should have been there from the start.

Status: `agent-unverified`. The counts above reproduce by running the script
against the two cited run records.
