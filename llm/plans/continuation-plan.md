# Continuation plan — J-Lens binding research after MATS 12.0

Written 2026-09-16. Owner: Jason. Assumes ~5–8 hours/week alongside the
PhD, continued VT ARC access, and the existing repo/governance stack.

## The goal, stated once

Turn the application project into a public, reusable result: a cheap check
that tells whether a lens reads stored facts or predicts the upcoming output,
with J-Lens on the binding task as the worked example. The method is the part
that travels; the J-Lens finding is the case study.

Neel cannot give feedback on applications. What he did say: build on it,
write a blog post (LessWrong), join the Mech Interp Discord, apply to future
programs. So the sharing channel is public work he will see, not emails.

## Phase 0 — this week
- Tag the repo at the submitted state (mats12-submitted).
- One-page retrospective in llm/memory_bank/retrospective.md (Jason).
- Join the Mech Interp Discord; read for a week before posting.
- Start Neel's "how to become a mech interp researcher" post.

## Phase 1 — close the holes that limit what the result means (weeks 1–3)
1. Probe the fact tokens: is the pairing linearly stored where the fact is
   stated? Arm 3 at the city/person tokens with a two-way person/city target.
2. Activation patching between swapped twins at the frozen positions — the
   causal test the application could not run. Report margin change and flips.
3. The resample control ("Perth uses granite" → "basalt"): closes the
   co-occurrence door on the rank result.
4. A fresh held-out draw (new seed, 60 pairs) scored once at frozen settings.
5. A trained linear probe alongside difference-in-means.
Governance unchanged: pre-register, freeze, verification ledger.

## Phase 2 — does the audit generalize? (weeks 4–6)
- Second model with a released lens; second task family; second lens type
  (tuned lens or trained probe as the readout under audit).
- Package the audit as a script: overall accuracy, accuracy on model-wrong
  records, r(lens margin, model margin). Name it.

## Phase 3 — publish (weeks 6–8)
- LessWrong/AF post. Headline is the method; J-Lens is the case study.
  Jason's voice.
- Mech Interp Discord thread with one specific question.
- Ping the J-Lens / Neuronpedia authors.
- One-line reply to Neel with the link, once, no ask.
- Optional: workshop paper if Phase 2 generalizes.

## Phase 4 — next application
Prior work done on one's own counts as a normal project under Neel's rules.
By then: a published post, a generalization result, a reusable tool.

## What not to do
- No emails to Neel asking for feedback.
- No scope expansion before Phase 1 closes.
- Do not drop the governance.

## Checkpoints
| When | Check |
|---|---|
| End of week 1 | Retrospective; Discord joined; step 1 pre-registered and queued |
| End of week 3 | Phase 1 steps 1–4 run and logged |
| End of week 6 | Second model + task scored; audit script runs cold |
| End of week 8 | Post published; Discord thread open; authors pinged |
