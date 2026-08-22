# Self-Review Rubric

Score the application against this before submitting. Derived verbatim
from Neel's evaluation criteria and common-mistakes lists — the full
source is in `mats12-application-instructions-distilled.md`.

## The bar he states

> "If I understand what you're claiming, what evidence you're providing,
> and think that evidence supports your conclusion, that instantly puts you
> in the top 20% of applicants."

> "My ideal application is one that teaches me something new."

## Green flags — score each 0/1/2

| # | Criterion | Score |
|---|---|---|
| 1 | **Clarity.** A reader with mech interp experience and zero context can follow what I did — data generation, prompt choice, metric definitions, hyperparameters. | |
| 2 | **Good taste.** The question is interesting and sits inside a direction he names in the doc. Not obvious without evidence. | |
| 3 | **Originality.** He will not have seen twenty of these. | |
| 4 | **Skepticism.** I questioned my own results, looked for alternative explanations, and ran sanity checks. | |
| 5 | **Anticipated red-team.** He thinks of a way the result could be false, then finds I already checked it. *(He names this as "a really positive sign.")* | |
| 6 | **Technical depth.** The design decisions show I understand why, not that I followed a recipe. | |
| 7 | **Simplicity.** I tried the obvious thing first, or explained why it was unsuitable. Every piece of complexity earns its place. | |
| 8 | **Prioritisation.** I went deep on one or two insights rather than being superficial about many. | |
| 9 | **Showed my work.** The thought process is visible — especially where things failed. "I got stuck so I pivoted / found the reason" beats "I got stuck so I gave up." | |
| 10 | **Baselines.** Every claim has a control: random vector, random choice, "just ask the model", a linear probe. | |
| 11 | **Raw examples.** Randomly selected qualitative examples appear just after the executive summary — especially for any LLM-judge or LLM-generated dataset. | |
| 12 | **Limitations named.** The holes are stated as plainly as the finding. Plausible claims over ambitious ones. | |
| 13 | **Own voice.** The exec summary and form answers are mine, not an LLM's. | |
| 14 | **Executive summary stands alone.** ≤600 words, ≤3 pages, graphs included, point not buried. | |
| 15 | **Narrative, not chronology.** Structured to emphasise the finding. | |

**28+/30 before submitting.** Anything scoring 0 is a blocker.

## Red flags — every one of these must be NO

- [ ] Contains a key result I never verified or don't fully understand
- [ ] Generic project type: "safety concept has a linear representation",
      "patching shows which heads matter", "CoT causally affects the answer"
- [ ] Sits in an area he's out of: grokking, circuit-finding for its own
      sake, SAE hill-climbing, toy models on algorithmic tasks, theory
- [ ] Primary model is GPT-2, Pythia, or Gemma 2
- [ ] A claim without a baseline
- [ ] Cherry-picked qualitative examples
- [ ] A negative result dressed up as positive
- [ ] Results hyped beyond what the evidence carries
- [ ] Built on a phenomenon I never checked replicates in my setup
- [ ] A single faithfulness metric reported as if it means something
- [ ] A single-model claim with no second model
- [ ] Reads like LLM output
- [ ] Google Doc sharing not set to "anyone with the link"

## Mechanics checklist

- [ ] Exec summary is the first 1–3 pages of the Google Doc
- [ ] ≤600 words, graphs included, bullet points fine
- [ ] Sections: *What problem / why interesting* · *High-level takeaways* ·
      *One paragraph + graph per key experiment*
- [ ] Randomly selected raw examples immediately after the exec summary
- [ ] Toggl (or equivalent) time screenshot attached
- [ ] Code linked (optional but encouraged — he feeds it to his agents)
- [ ] Airtable form answers written with care; they are the first filter
- [ ] Answered: *"What are 1-3 pieces of evidence that you'd be able to do
      good research in the program?"*
- [ ] Submitted before Fri Sept 4, 11:59pm PT
