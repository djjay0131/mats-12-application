# Requirements Conformance Register — Neel Nanda MATS 12.0 Application

*Source: `/home/claude/out/mats12-instructions-raw.txt` (1,118 lines / 125,654 chars), read in full. Quotes are verbatim; the source is a markdown export of a Google Doc and contains escaped emphasis artifacts (`\*\*`, `\!`, `\\\!`). I have stripped only those escape artifacts for readability — no words, ordering or punctuation have been changed.*

**Counts found: 121 requirements total**
- `BLOCKER` — **38**
- `SCORED` — **33**
- `MECHANIC` — **21**
- `ADVICE` — **29**

---

## BLOCKERS

| ID | Requirement | Source quote | Class | Verification | Automatable | Gate |
|---|---|---|---|---|---|---|
| BLK-01 | Verify every key result your coding agent produced before it enters the write-up. | "**Not sanity-checking your AI agents**. Coding agents are great and you should use them, but if your write-up contains key results you clearly never verified, or don't understand that's disqualifying. I want scholars with value add over prompting Claude myself" | BLOCKER | Maintain a verification ledger: one row per headline claim in the write-up, each with (a) the code path that produced it, (b) an independent re-derivation, (c) date + who checked. Script asserts every numeric claim in the doc has a ledger row. | partial | EXECUTE→WRITEUP |
| BLK-02 | Never include a result you cannot explain from first principles. | "if your write-up contains key results you clearly never verified, or don't understand that's disqualifying" | BLOCKER | Named human must give a 60-second unaided verbal explanation of each figure/metric; record pass/fail per figure. | no | WRITEUP |
| BLK-03 | Never submit an application that reads as "an agent did a project and a human forwarded it". | "A crucial thing I am evaluating is whether you add value beyond me just prompting Fable myself. An application that is clearly \"an agent did a project and a human forwarded it to me\" will be rejected; I can get that myself, in twenty minutes, for free." | BLOCKER | Write-up must contain an explicit section naming human-owned decisions: hypothesis, experimental design, controls, interpretation. Script asserts presence of a "what I did vs what the agent did" section. | partial | WRITEUP |
| BLK-04 | Never submit raw LLM prose for the application form answers or the executive summary — write them in your own voice. | "**Please do not just submit raw LLM output for the application form or executive summary**. Write these yourself, in your own voice, even if you think an LLM will sound better. … Answers that read like they were written by an LLM are a significant negative signal - I see hundreds of them, and they blur together." | BLOCKER | Provenance rule: exec summary + form answers typed by hand, no paste from a model window; verify via editing history (Google Docs version history / git). Plus an LLM-slop lexical check (em-dash density, "delve/underscore/crucially/it's not X, it's Y", tricolon rate) against a banned-phrase list. | partial | WRITEUP/SUBMIT |
| BLK-05 | Never let the write-up read like LLM slop. | "It is your responsibility to ensure your code and writing are high quality. Well-written write-ups are welcome. Docs that read like LLM slop will be rejected." | BLOCKER | Two independent human readers score "does this read as LLM-generated?" on the exec summary; both must say no. Plus banned-phrase grep. | partial | WRITEUP |
| BLK-06 | Make the write-up understandable — if the reader cannot follow what you did, you are rejected. | "**This is not an afterthought!** People often neglect the write-up, but it's crucial. **If I don't understand what you did, I will reject your application.**" | BLOCKER | A reader with mech-interp background but zero project context reads only the doc and must correctly restate: the claim, the evidence, and one limitation. Record their restatement. | no | WRITEUP |
| BLK-07 | Ensure the application form summary and executive summary are independently comprehensible. | "Poor writing - if I can't understand your summary in the application form / executive summary, I probably won't have time to decipher your research report and figure out if there's something interesting here." | BLOCKER | Same cold-reader test run on the form answers + exec summary **alone**, with the full write-up withheld. | no | WRITEUP/SUBMIT |
| BLK-08 | Include compelling sanity checks and red-teaming of your key results. | "**Insufficient skepticism about your results**: Most research results are false, especially the exciting ones. Applications without compelling sanity checks and red-teaming of their key results rarely succeed" | BLOCKER | Every load-bearing claim has ≥1 documented sanity check and ≥1 documented red-team attempt (an actively tried alternative explanation), each with its outcome stated in the doc. | partial | EXECUTE→WRITEUP |
| BLK-09 | Never rest a conclusion only on a few cherry-picked qualitative examples. | "Crucially, **avoid relying only on a few cherry-picked qualitative examples**—this is a major red flag." | BLOCKER | For each qualitative claim, assert an accompanying quantitative measure over a defined sample, or an explicit "existence proof" label. Script flags any claim section with examples but no n. | partial | WRITEUP |
| BLK-10 | If your project rests on a dataset or on LLM judgements, look at it yourself and include randomly selected (not cherry-picked) raw examples just after the executive summary. | "If bad data would sink your project, show me the data. If everything rests on the quality of some dataset or judgement calls (e.g. you generated the dataset with an LLM, or used an LLM judge to score outputs), look at it yourself - and include some randomly selected qualitative examples in the write-up, ideally just after the executive summary. Randomly selected, not cherry-picked! A handful of raw examples is the easiest way to show me that the thing your whole project rests on is actually real." | BLOCKER | Sampling script with a recorded random seed selects the displayed examples; the seed and selection code appear in the doc/appendix. A named human has hand-labelled a stated number of judge outputs (≥30) and the agreement rate is reported. | yes | EXECUTE→WRITEUP |
| BLK-11 | Compare your key result to a baseline. | "**Failing to** **compare to baselines** (eg replace your vector with a random one, choose randomly, ask an LLM, use a linear probe)" / "And remember to compare to baselines, if applicable" / "If you want to argue that a method is useful, remember to compare to baselines!" | BLOCKER | Every metric table/figure making a method claim has an adjacent baseline column (random vector / random choice / prompt-the-model / linear probe). Script asserts each results table has ≥2 columns and one is tagged `baseline`. | yes | EXECUTE→WRITEUP |
| BLK-12 | Run the cheap control before claiming an effect. | "Skipping the cheap control: fine-tune on random data, replace your vector with a random one, compare against \"just ask the model\"." | BLOCKER | Checklist per claim: which of {random-data finetune, random vector, just-ask-the-model} applies, and its result. Must be non-empty. | partial | EXECUTE |
| BLK-13 | Never do a common/generic project type without an interesting application or twist. | "Doing a very **common/generic type of project** without an interesting application or twist (showing that a safety-related concept has a linear representation, using patching to show which heads/layers are used in a task, showing that chain of thought causally impacts the final answer)" | BLOCKER | At SELECT, write one sentence naming the twist. Grep the project one-liner against the three named generic patterns; if it matches, the twist statement must be present and reviewed by a human. | partial | SELECT |
| BLK-14 | Never work in an area he is no longer interested in. | "Working in **areas I'm no longer into** (grokking, circuit finding for its own sake, SAE hill-climbing/basic science of SAEs, toy models trained on algorithmic tasks, very theoretical work)" / "grokking, circuit finding for its own sake, SAE hill-climbing, toy models, very theoretical work" | BLOCKER | Grep the project description and write-up against a banned-topic list: grokking, circuit finding (for its own sake), SAE hill-climbing, basic science of SAEs, toy models, algorithmic tasks, purely theoretical. Any hit requires written justification. | yes | SELECT |
| BLK-15 | Never build the project only on old models. | "**Only studying old models** (GPT-2, Pythia, Gemma 2)" | BLOCKER | Grep the write-up for model names against banned list {GPT-2, Pythia, Gemma 2}; assert at least one primary subject model is current (e.g. Qwen 3.5/3.6, deepseek v4 flash, Gemma 3, Olmo 3, Nemotron 49B). | yes | SELECT |
| BLK-16 | Never use GPT-2 as your subject model. | "Related: Working with a model that's just way too dumb for the task. There's no good reason to use GPT-2 in your application at this point" | BLOCKER | Grep write-up + code for `gpt2`/`gpt-2`; must return zero hits in the subject-model role. | yes | SELECT/EXECUTE |
| BLK-17 | Never study a phenomenon in a model too weak to exhibit it. | "Trying to investigate some phenomena without checking if it's really there, e.g. theory of mind in GPT-2 … Related: Working with a model that's just way too dumb for the task." | BLOCKER | Record a capability pre-check: the subject model's baseline performance on the target behaviour, reported before any interpretability work. | partial | SELECT/EXECUTE |
| BLK-18 | Confirm the phenomenon actually exists in your setup before investigating it. | "Trying to investigate some phenomena without checking if it's really there" | BLOCKER | A "phenomenon exists" experiment with numbers must appear in the doc before any downstream analysis section. Script asserts ordering. | partial | EXECUTE |
| BLK-19 | Confirm a phenomenon replicates in your model, dataset and prompts before building on it. | "Building on a phenomenon without first checking it replicates in your setting (your model, your dataset, your prompts). If the effect isn't there for your setup, everything downstream is noise." | BLOCKER | Named replication section reporting effect size in your setting vs the original paper's, with all three of model/dataset/prompt stated. | partial | EXECUTE |
| BLK-20 | Read your actual data — datapoints, transcripts, prompts, and metric positives. | "Not looking at your data - read some data points! Talk to your model! If something seems weird, look closer! There's almost always something worthwhile to learn here, but this key step is often neglected (including by professional researchers)" / "Read the raw data. Read actual transcripts/rollouts, look at the actual prompts sent, look at datapoints the metric says are positive and check they really are." | BLOCKER | Log of manual inspection: count of transcripts read, count of metric-positive datapoints hand-checked, and the true-positive rate found. Stated in the write-up. | partial | EXECUTE |
| BLK-21 | Check a simple hypothesis (prompting, reading the CoT, a linear probe) before a complex or high-effort one. | "Overcomplicating things - eg having a super complex hypothesis about some phenomena without checking a really simple hypothesis. Or trying a really high effort method without trying something simple like prompting, reading the chain of thought, or training a linear probe" | BLOCKER | For each fancy method used, the doc must contain either its simple-method comparison or an explicit stated reason the simple method was unsuitable. | partial | EXECUTE |
| BLK-22 | Never present a negative result as positive, and never lie about outcomes. | "Not acknowledging limitations in their results (worse, trying to pretend negative results are positive - negative results are fine! Lying about them is not)" | BLOCKER | Adversarial reader compares every claim sentence to the underlying number; any directional mismatch is a hard fail. Log the claim↔number mapping. | partial | WRITEUP |
| BLK-23 | Never hype your results beyond what they show. | "Related: Trying to hype up their results and make them seem way more interesting than they are. Just be honest! I can tell" | BLOCKER | Grep for hype markers ("we show that", "proves", "definitively", "dramatic", "novel", "first ever", "striking") and require each to be justified or downgraded; hedging density check on exec summary. | partial | WRITEUP |
| BLK-24 | Never let the write-up claim anything your own numbers contradict. | "In past rounds, some otherwise-promising applications were sunk because the write-up claimed things the applicant's own numbers contradicted - I do check." | BLOCKER | Script extracts every number from the doc and diffs against the canonical results file/notebook outputs; zero mismatches allowed. | yes | WRITEUP/SUBMIT |
| BLK-25 | Acknowledge the limitations in your results. | "Not acknowledging limitations in their results" | BLOCKER | Assert a "Limitations" section exists, is non-boilerplate, and names ≥3 specific holes tied to specific claims. | partial | WRITEUP |
| BLK-26 | Never appear overconfident in shaky results; prefer plausible claims over ambitious ones. | "If you seem overconfident in shaky results, that is not. Make plausible claims over ambitious ones." | BLOCKER | Per-claim confidence label (strong / suggestive / speculative) present in the doc; human check that labels match evidence strength. | partial | WRITEUP |
| BLK-27 | Actively look for ways your results could be false and check them before he does. | "Not thinking about ways their results could be false and doing sanity checks. A really *positive* sign about an application is when I think of a way the results could be false, then discover you've already checked it!" / "Be suspicious of success. If the agent says an experiment worked, treat that as a hypothesis, not a result. Ask: what's the dumbest way this could be wrong? (Data leakage, trivial baseline matching it, the metric not measuring what you think, the model in the loop gaming your grader…) Then check." | BLOCKER | Explicit "how this could be wrong" list per key claim, each item with a check and outcome; must cover at minimum data leakage, trivial-baseline match, metric validity, grader gaming. | partial | EXECUTE→WRITEUP |
| BLK-28 | Never choose an uninteresting problem — one that is both unambitious and unrelated to his research areas. | "Choosing an uninteresting problem, eg something both fairly unambitious *and* which isn't anything to do with my research areas of interest, like an incremental improvement to sparse autoencoders, or applying IOI-style circuit finding to a random problem" | BLOCKER | SELECT-gate memo mapping the project to a named section of the Recommended Research Problems tab; reviewed by a human other than the applicant. | no | SELECT |
| BLK-29 | Never pick a problem far outside his interests — purely theoretical, or only tiny toy models. | "Choosing a problem that's really far outside my interests, e.g. something entirely theoretical, or which only involves tiny toy models" | BLOCKER | Assert the project involves empirical experiments on a real (non-toy) model; parameter-count floor check on the subject model. | partial | SELECT |
| BLK-30 | Never pick a problem that doesn't make sense. | "Choosing a problem that doesn't really make sense" | BLOCKER | Have two people independently restate the research question and the decision it would inform; disagreement or inability = fail. | no | SELECT |
| BLK-31 | Never pick a problem so ambitious or conceptually messy that you end up confused. | "Choosing a problem that's super ambitious, or conceptually messy, and getting very confused" | BLOCKER | SELECT memo must state a concrete first experiment runnable in ≤3 hours and a falsifiable claim in one sentence. | no | SELECT |
| BLK-32 | Never pick a crowded problem with nothing to differentiate you. | "Choosing a problem that lots of other people did, with nothing to differentiate you." / "Originality is a big plus. If I've seen a bunch of applications doing extremely similar things, this is less exciting." | BLOCKER | Literature + likely-applicant-pool scan; write a one-line differentiator. Search arXiv/LW/AF for near-duplicates and record hits. | partial | SELECT |
| BLK-33 | Beware a pet interest that only people who share it will find interesting. | "A warning sign is candidates with a particular pet interest. If you're e.g. really excited about medical applications of AI, you're welcome to do a project on this, but there's a good chance you do a project that *only* people interested in medical applications of AI find interesting" | BLOCKER | Ask a mech-interp-literate person with no stake in your topic: "would you find this interesting?" Record the answer at SELECT. | no | SELECT |
| BLK-34 | Pivot or abandon a project you realise is doomed — do not just keep going. | "Realising the project is probably doomed halfway through, and just continuing the project rather than trying to pivot. Knowing when to give up is a key research skill!" | BLOCKER | Scheduled kill-criteria review at fixed hour marks (e.g. h6, h12) with a written go/pivot/kill decision recorded each time. | partial | EXECUTE |
| BLK-35 | Never run many vaguely relevant experiments instead of striving for conclusive evidence, and never miss simple alternative explanations. | "**Common mistakes:** Getting too excited and missing simple alternative explanations for your results; running a bunch of experiments that are only vaguely relevant instead of striving for **conclusive evidence**." | BLOCKER | Each experiment in the log is tagged with the hypothesis it tests; assert ≥80% of logged experiments map to the ≤2 headline hypotheses. Alternative-explanations list exists per claim. | partial | EXECUTE |
| BLK-36 | Never submit an entirely LLM-written application about made-up experiments. | "Submitting an entirely LLM written application, about made up experiments (please don't do this…)" | BLOCKER | Every reported experiment maps to a committed, timestamped code artifact and its raw output file. Script asserts 1:1 coverage. | yes | SUBMIT |
| BLK-37 | Ensure your code as well as your writing is high quality — you own it, not the model. | "It is your responsibility to ensure your code and writing are high quality." | BLOCKER | Human read-through of the scripts producing each headline number, recorded as reviewed; lint/test pass on the analysis code. | partial | EXECUTE→WRITEUP |
| BLK-38 | *(Conditional — model forensics on existing transcripts)* Only study a transcript on a different model if resampling with that model recreates the weird behaviour. | "It's OK but not ideal to study a transcript on a model other than the one that made it. Only do this if resampling with the new model recreates the weird behavior" | BLOCKER | If the transcript source model ≠ subject model, a resampling reproduction experiment with a reported reproduction rate must exist before any analysis. | partial | EXECUTE |

---

## SCORED

### Clarity

| ID | Requirement | Source quote | Class | Verification | Automatable | Gate |
|---|---|---|---|---|---|---|
| SCR-01 | Make your claim, your evidence, and the link between them unmistakable. | "**Clarity**: If I understand what you're claiming, what evidence you're providing, and think that evidence supports your conclusion, that instantly puts you in the top 20% of applicants." | SCORED | For each claim, the doc contains an explicit triple: claim sentence → figure/number → one-line "why this supports it". Script asserts each claim heading has all three. | partial | WRITEUP |
| SCR-02 | Give enough methodological detail to follow along: data generation, prompt choice, metric definitions, hyperparameters. | "Show me enough detail so I can follow along: how did you generate your data or choose your prompts, how did you define your metrics, what were your hyperparameters, etc.? This can be concise if done well—bullet points and short code snippets can go a long way." | SCORED | Checklist grep for a methods block containing: data generation, prompts, metric definition, hyperparameters, n. All four present. | yes | WRITEUP |
| SCR-03 | Use bullet points, good graphs, summaries, good structure and intuitive explanations. | "I like bullet points, good graphs, summaries, good structure, and intuitive explanations to get the high-level picture across clearly" | SCORED | Structural check: heading depth ≤3, every figure has a caption, exec summary is bulleted, ≥1 intuition paragraph per key result. | partial | WRITEUP |
| SCR-04 | Write for a reader with zero context: define your terms, explain from the ground up, label your graphs. | "**Your Reader Has Zero Context.** The \"illusion of transparency\" is a huge trap. Things that feel obvious to you will be completely new to your reader. Explain everything from the ground up. Define your terms. Label your graphs clearly." | SCORED | Extract all jargon/acronyms; assert each is defined on first use. Assert every figure has labelled axes, units and a legend. | yes | WRITEUP |
| SCR-05 | Make the executive summary stand on its own, carrying the key takeaways and a sketch of the evidence. | "**Make Your Executive Summary Count.** It needs to stand on its own and convey the most important takeaways and a sketch of your key evidence. Don't make me hunt for the point or crucial details. Good graphs are a huge plus here." | SCORED | Cold reader given only the exec summary must state the takeaway and name the key evidence. Assert ≥1 graph inside the exec summary. | partial | WRITEUP |
| SCR-06 | Structure the write-up around one or two concrete insights as a narrative, not a dump of experiments. | "**Focus on a Narrative.** Don't just dump all your experiments. Structure your write-up around the one or two most interesting, concrete insights you found. What is the key story?" | SCORED | Assert the doc names ≤2 headline insights, and ≥70% of body sections are traceable to one of them. | partial | WRITEUP |
| SCR-07 | Be concrete: name the models, the key experiment, and the surprising number. | "Convey concretely what you did, what you found, why it's interesting, biggest limitations, etc. Specifics beat vibes: name the models, the key experiment, the surprising number." | SCORED | Script asserts the exec summary contains ≥1 model name, ≥1 named experiment, ≥1 numeric result, and a limitations sentence. | yes | WRITEUP |
| SCR-08 | Write it so it does not assume too much context on the reader's behalf. | "Writing was difficult to follow, and tended to assume too much context on behalf of the reader." (assessment of *What Impacts CoT Faithfulness*) | SCORED | Cold-reader annotation pass: reader marks every sentence they could not follow; target zero in the exec summary. | no | WRITEUP |

### Good Taste

| ID | Requirement | Source quote | Class | Verification | Automatable | Gate |
|---|---|---|---|---|---|---|
| SCR-09 | Choose an interesting question, get traction on it, and produce compelling results. | "**Good Taste**: You chose an interesting question, and were able to get traction on it, and produce results I find compelling. My favourite kind of application is one where I learn something from it." | SCORED | SELECT memo + a post-hoc check that the headline claim is supported and non-trivial; external reviewer rates "did I learn something?" 1–5. | no | SELECT/WRITEUP |
| SCR-10 | Align your question with his current research interests. | "Choosing a question aligned with my research interests is extremely helpful" / "Having interests aligned with my research interests is a significant plus." / "**I'm open to any application that shows strong research skill, but it helps a lot for questions to match my research interests.**" | SCORED | Map the project to a named heading in the Recommended Research Problems tab (Model Forensics, Model Biology, Reasoning Models, Circuit analysis, Objectively Measuring Interpretability, Model Diffing, Science of Model Character, Improved Interpretability Methods, Science of Post-training, Alignment Training, Science of Generalization, Applied Interpretability, Basic Science, Novelty). Assert exactly one primary mapping recorded. | partial | SELECT |
| SCR-11 | Make a claim that is not immediately obvious without evidence. | "This doesn't have to be a big, ambitious claim—just any claim that's not immediately obvious without evidence." | SCORED | Ask two people to predict the result before seeing it; if both predict correctly with high confidence, the claim is too obvious. Record predictions. | no | SELECT/EXECUTE |
| SCR-12 | Be original — differentiate from what many other applicants will do. | "Originality is a big plus. If I've seen a bunch of applications doing extremely similar things, this is less exciting." | SCORED | Recorded search for prior/parallel work; one-line novelty statement in the doc. | partial | SELECT |
| SCR-13 | Teach him something new. | "My ideal application is one that **teaches me something new**." / "I evaluate application tasks according to the criteria above, and by my intuitive sense of \"did I learn something interesting from reading this?\"" | SCORED | Write the one-sentence "thing a reader did not know before" and have a domain-literate reader confirm they did not know it. | no | WRITEUP |
| SCR-14 | Surprise him if you can — new ideas or applications he did not expect to work are strongly rewarded. | "Applications that surprise me with something new and cool are fantastic!" / "**New ideas**: For anyone feeling ambitious, I'm extremely impressed with any application showing ideas and applications of interpretability that are new to me or that I didn't expect to work" | SCORED | Record whether the finding was predicted in advance by your own pre-registration; a violated prediction is the evidence. | no | EXECUTE |

### Truth-seeking and Skepticism

| ID | Requirement | Source quote | Class | Verification | Automatable | Gate |
|---|---|---|---|---|---|---|
| SCR-15 | Constantly question your results, look for alternative explanations, and run sanity checks. | "**Truth-seeking and Skepticism**: The easiest person to fool is yourself. You constantly questioned your results, looked for alternative explanations, and did sanity checks." | SCORED | Skepticism log: per key result, ≥2 alternative explanations considered with how each was ruled out or left open. | partial | EXECUTE |
| SCR-16 | Prefer a well-analysed negative or inconclusive result over a poorly supported positive one. | "Negative or inconclusive results that are well-analysed are much better than a poorly supported positive result." | SCORED | If the headline is positive, evidence strength must clear a stated bar; otherwise reframe as a well-analysed negative. Decision recorded at WRITEUP. | no | WRITEUP |
| SCR-17 | Show self-awareness about where the holes are, which parts are speculative, and what you would investigate next. | "It's a harsh time limit, so there are going to be holes in your results. It's OK if you show self-awareness of where the holes are, which parts are speculative, what you would investigate next, etc." | SCORED | Assert three sections exist: holes/limitations, explicitly-flagged speculation, and "what I'd do next". | yes | WRITEUP |
| SCR-18 | Show attention to detail — notice subtleties and edge cases and investigate them where appropriate. | "A subskill here is **attention to detail**: Noticing subtleties and edge cases, and investigating them where appropriate" | SCORED | Doc contains ≥1 "I noticed X was odd, so I looked closer and found Y" episode. | no | EXECUTE/WRITEUP |
| SCR-19 | Document in the write-up what you verified and how. | "Document your checking in the write-up. Tell me what you verified and how - \"I read 30 transcripts and confirmed the probe's positives were real\" is strong evidence of research skill." | SCORED | Assert a "what I verified" section with countable statements (n transcripts read, n numbers re-derived, n hand-labels). | yes | WRITEUP |
| SCR-20 | Re-derive key numbers independently rather than trusting the pipeline. | "Verify the load-bearing claims. For each key result: read the code that produced it, check the numbers in the write-up against the actual outputs, re-derive at least some of them independently (e.g. recompute a headline number with a fresh one-liner, or spot check by hand)." | SCORED | Independent re-derivation script per headline number, stored separately from the main pipeline; assert agreement within tolerance. | yes | EXECUTE |
| SCR-21 | Own the experimental design, the controls and baselines, and the interpretation — not the agent. | "Design experiments yourself. Agents are great at executing experiments and terrible at noticing that the experiment doesn't test the hypothesis. The experimental design, the controls and baselines, and the interpretation of results should be yours." | SCORED | Design decisions recorded in a human-written planning doc timestamped before the agent ran the experiment. | partial | EXECUTE |
| SCR-22 | Keep track of what kind of claim you are making — existence proof (cherry-picking fine) vs method-is-right (baselines required). | "It's crucial to keep track of the kind of claim you are trying to make. Sometimes you want to give an existence proof (e.g., find an example of an interesting phenomenon), where cherry-picking is fine. Other times, you want to argue a method is the right thing to do for a task, which requires comparing to baselines." | SCORED | Each claim tagged `existence-proof` or `method-claim`; script asserts every `method-claim` has a baseline column and every `existence-proof` is labelled as such in the text. | yes | EXECUTE/WRITEUP |

### Technical Depth & Practicality

| ID | Requirement | Source quote | Class | Verification | Automatable | Gate |
|---|---|---|---|---|---|---|
| SCR-23 | Demonstrate a good handle on the relevant tools — coding, experiment design, or specific interpretability methods. | "**Technical Depth & Practicality**: You demonstrate a good handle on the relevant tools, whether that's coding, experiment design, or specific interpretability methods." | SCORED | Code artifact exists and is readable; doc explains at least one method choice at the mechanism level. | partial | EXECUTE/WRITEUP |
| SCR-24 | Show willingness to get your hands dirty writing code and running experiments. | "You show a willingness to get your hands dirty writing code and running experiments." / "Please bias towards getting your hands dirty, and focus on writing code, running experiments on the model, and getting feedback from reality." | SCORED | Time log: hours on code/experiments vs reading. Assert experiment hours ≫ reading hours. | yes | EXECUTE |
| SCR-25 | Make it clear from your writing and design decisions that you understand what you are doing, rather than following a recipe or an LLM. | "Your writing and design decisions make it clear that you understand what you are doing and it's well motivated, rather than blindly following a recipe/LLM" | SCORED | Each non-obvious method/hyperparameter choice has a one-line stated reason in the doc. | partial | WRITEUP |

### Simplicity

| ID | Requirement | Source quote | Class | Verification | Automatable | Gate |
|---|---|---|---|---|---|---|
| SCR-26 | Try the simple, obvious method first — or explain why it was unsuitable. | "**Simplicity**: Being biased towards trying the simple, obvious methods first (or explaining why they were unsuitable). It's easy to get excited by fancy techniques, but they can be a trap. Good applications are pragmatic and focused, not showing off." | SCORED | Simplicity ledger: for every technique above "prompt / read the CoT / linear probe", record either the simple-method result or the written reason it was unsuitable. | partial | EXECUTE |
| SCR-27 | Justify every piece of complexity in the project. | "Each piece of complexity in the project should be there for a reason" | SCORED | Enumerate moving parts (models, datasets, methods, metrics); each must have a one-line justification. Script asserts count of justifications == count of parts. | partial | EXECUTE/WRITEUP |
| SCR-28 | Don't reach for fancy methods (e.g. SAEs) when prompting or a linear probe would do. | "I'm agnostic about the techniques you use - start by doing the obvious thing! Fancy methods (like sparse autoencoders) are easy ways to waste effort when prompting or a linear probe would do." | SCORED | If SAEs/crosscoders/attribution graphs are used, assert a prompting and/or linear-probe comparison exists. | yes | EXECUTE |

### Prioritisation

| ID | Requirement | Source quote | Class | Verification | Automatable | Gate |
|---|---|---|---|---|---|---|
| SCR-29 | Use your time well and go deep on one or two key insights. | "**Prioritisation**: You used your time well, and went deep on one or two key insights, rather than being superficial about many things" / "**Quality over Quantity.** One interesting finding, well-explained and well-supported, is far better than ten superficial experiments." | SCORED | Assert ≤2 headline insights and ≥3 supporting experiments per insight. Time log shows majority of hours on those. | partial | EXECUTE/WRITEUP |
| SCR-30 | Avoid rabbit holes and pivot when the direction stops being interesting. | "A common mistake is getting caught in **rabbit holes** - finding one random anomaly or detail that (in my opinion) isn't very interesting, and spending the whole time zooming on that. Knowing when to pivot where appropriate is impressive" | SCORED | Hourly/two-hourly zoom-out checkpoints logged with a go/pivot decision (see ADV-19). Assert no single sub-thread exceeds a preset hour budget without a recorded decision. | yes | EXECUTE |
| SCR-31 | Avoid spreading yourself too thin across many shallow things. | "Another is spreading yourself too thin - doing lots of things superficially, but without enough depth for any one to be interesting" | SCORED | Count distinct experimental threads; assert ≤3, and that the top thread holds ≥50% of experiment hours. | yes | EXECUTE |

### Productivity

| ID | Requirement | Source quote | Class | Verification | Automatable | Gate |
|---|---|---|---|---|---|---|
| SCR-32 | Get a lot done per unit time, with fast feedback loops — without cutting corners. | "**Productivity**: While it's more important to do things well than do them fast, the ideal is both. Some researchers are a lot more productive per unit time than others, and they get a lot more done." / "This isn't about cutting corners - there's a lot of skill to having fast feedback loops, noticing and fixing inefficiency where appropriate" | SCORED | Track experiments-completed-per-hour and median iteration latency; review at h10 and fix the slowest loop. Compare final output volume against the past-example applications. | partial | EXECUTE |

### Show your work

| ID | Requirement | Source quote | Class | Verification | Automatable | Gate |
|---|---|---|---|---|---|---|
| SCR-33 | Show your thought process — explain *why* you ran each experiment, what hypothesis it tested, and what outcomes were possible. | "**Show Your Work.** Explain *why* you ran an experiment, not just *what* you did. What hypothesis were you testing? What were the possible outcomes? This reveals your thought process." / "**Show your work**: It's great to see your thought process, understand why you made the decisions you made, etc. This matters most if your results are inconclusive or key parts failed" | SCORED | Each experiment section contains a "hypothesis / possible outcomes / why now" preamble. Script asserts the three sub-fields per experiment. | yes | WRITEUP |
| SCR-34 | If you got stuck, show that you pivoted, found a new angle, or diagnosed why it failed — not that you gave up. | "The difference between \"I got stuck so I gave up\" and \"I got stuck, so I pivoted or found a new angle, or identified the reason why it didn't work\" is huge." | SCORED | Every dead end in the doc terminates in one of: pivot, new angle, or a stated diagnosis. Assert no dead end ends without one. | partial | WRITEUP |
| SCR-35 | Structure the write-up to emphasise the interesting finding — never chronological order. | "Though if you *do* have an interesting finding, please structure the write-up to emphasise it, don't do chronological order!" | SCORED | Check the section order is not the same as the experiment-log timestamp order; headline finding appears in the first section after the exec summary. | yes | WRITEUP |

### Enthusiasm & Curiosity

| ID | Requirement | Source quote | Class | Verification | Automatable | Gate |
|---|---|---|---|---|---|---|
| SCR-36 | Let genuine curiosity and enthusiasm show; make the application fun to read. | "**Enthusiasm** & **Curiosity**: Mech interp can be hard, confusing and frustrating, or it can be fascinating, exciting and tantalising. … I know this is easy to fake and hard to judge from an application, so I don't weight it highly here. But generally applications that are fun to read get bonus points!" | SCORED | A reader rates the doc for readability/enjoyment; check the write-up contains at least one genuine "this surprised me / I found this delightful" beat that is not manufactured. | no | WRITEUP |

### Holistic / beyond the task

| ID | Requirement | Source quote | Class | Verification | Automatable | Gate |
|---|---|---|---|---|---|---|
| SCR-37 | Give 1–3 strong, relevant pieces of evidence that you can do good research, including non-standard credentials. | "In the application form, I ask: \"What are 1-3 pieces of evidence that you'd be able to do good research in the program?\" This is your chance to highlight things like: Popular open-source projects you've built. Startups you've founded. Blog posts you're particularly proud of. Impactful things you did at work or in class projects. Something interesting I didn't think of when writing this list!" / "If you've done something cool, and you think a reasonable person would update positively on hearing it, please mention it and explain its relevance!" | SCORED | Assert 1–3 items present, each with (a) a verifiable link and (b) an explicit relevance sentence. | yes | SUBMIT |
| SCR-38 | Understand that insightfulness beats prestige in how prior work is weighed. | "An insightful Arxiv paper is much better evidence than a NeurIPS oral I don't find interesting." | SCORED | When choosing which credentials to list, rank by insight/relevance rather than venue; record the ranking rationale. | no | SUBMIT |

---

## MECHANIC

| ID | Requirement | Source quote | Class | Verification | Automatable | Gate |
|---|---|---|---|---|---|---|
| MEC-01 | Submit via the Airtable application form. | "**Submit** via this form, due Fri Sept 4 11:59pm PT" | MECHANIC | Confirmation email / submission receipt archived. | no | SUBMIT |
| MEC-02 | Submit by Fri Sept 4, 11:59pm PT. | "**Due Fri Sept 4th 11:59pm PT**" | MECHANIC | Calendar deadline with alarm at T-24h; assert submission timestamp < deadline (PT). | yes | SUBMIT |
| MEC-03 | If you need more time, request an extension (available until Sept 11) via the separate form. | "(extensions available until Sept 11)" | MECHANIC | Extension request submitted and confirmed before Sept 4 if needed. | no | SUBMIT |
| MEC-04 | Submit a Google doc write-up plus an executive summary, in addition to the form. | "Please submit a **write-up** and **executive summary** showing me what **progress you made** and **what you learned** about the problem." / "**Format**: An application should consist of a summary of your findings in the application form, and a google doc describing your key findings which begins with an executive summary" | MECHANIC | Assert both artifacts exist and the form has the doc link. | yes | SUBMIT |
| MEC-05 | Begin the doc with the executive summary. | "a google doc describing your key findings which begins with an executive summary" | MECHANIC | Assert the first heading of the doc is the exec summary. | yes | WRITEUP |
| MEC-06 | Keep the executive summary to ~1 page, max 3 pages, max 600 words. | "The first 1-3 pages of the google doc should be an executive summary … Something at **~1 page** (including graphs) is great, **max 3 pages** and **max 600 words**." | MECHANIC | Word-count the exec summary ≤600; page-count ≤3. | yes | WRITEUP |
| MEC-07 | Include graphs in the executive summary. | "Please **include graphs**! Bullet points can work well" | MECHANIC | Assert ≥1 image inside the exec summary page range. | yes | WRITEUP |
| MEC-08 | Use the suggested executive summary structure: problem + why interesting; high-level takeaways; one paragraph and graph per key experiment. | "One good format is to have sections for: What problem am I trying to solve? (and a bit on why you think it's interesting) … What are your high-level takeaways? What were the most interesting parts of your project? … One paragraph and graph per key experiment, giving the gist of what it was, what you found, and why this supports your key takeaways" | MECHANIC | Assert the three sections exist; assert each key experiment has exactly one paragraph and one graph. | yes | WRITEUP |
| MEC-09 | Include a bunch of graphs in the main write-up. | "a google doc describing your key findings which begins with an executive summary and ideally contains a bunch of graphs" | MECHANIC | Count figures in the doc; assert ≥1 per key experiment. | yes | WRITEUP |
| MEC-10 | Include enough detail to follow what you did without needing to read your code. | "and enough detail to follow what you did without needing to read your code" | MECHANIC | Cold reader restates the pipeline with the code withheld. | no | WRITEUP |
| MEC-11 | Optionally include code — it is encouraged but not required. | "You're encouraged to include code, but it's not required, I'll largely use it to give my agents context and ask them questions about what you actually did and I'll only read it as necessary to understand the write-up better." | MECHANIC | If included, assert the repo/link is public or link-accessible and runs. | partial | SUBMIT |
| MEC-12 | Set the Google doc so anyone with the link can access it. | "**Remember to let anyone with the link access the doc**!" | MECHANIC | Open the doc link in a logged-out incognito window and confirm it renders. Repeat for every linked artifact (code, notebooks, appendix). | yes | SUBMIT |
| MEC-13 | Answer the application form's summary questions and prioritize them — they are the preliminary filter. | "The application form has a bunch of Qs about the project and I will read these for every single app and use it as a preliminary filter - **communicating well here is important and should be prioritized**!" / "Prioritize the application form summary Qs, I read these first and use them as a preliminary filter, I don't have time to read every write-up." | MECHANIC | Assert every form field is filled; ≥2h of the writing budget logged against form answers; cold-reader test on the answers alone. | partial | SUBMIT |
| MEC-14 | Spend ~16 hours, and never more than 20, on the project. | "Spend **~16 hours (max 20) working on an interesting AI safety research problem of your choice**" / "**Application task**: Spend **~16 hours** (**max 20**)" | MECHANIC | Time-tracker total ≤20:00 on project-counted categories. | yes | EXECUTE |
| MEC-15 | Take up to 2 additional hours, beyond the 20, for the executive summary and the form questions. | "The time limit has **up to two additional hours** for the executive summary and application form Qs." / "So the executive summary doesn't get super rushed, you can take another 2 hours for it." | MECHANIC | Separate tracker category ≤2:00. | yes | WRITEUP |
| MEC-16 | Count towards the limit: writing project code, reading project-relevant papers, analysing data, thinking/planning, writing the Google doc. | "I consider any time you spend actively working towards the project goals to be within the 20 hour time limit. This includes (but is not limited to): Writing code for your project; Reading papers (chosen because they're relevant to your project); Analysing data/experimental results; Thinking and planning time; Writing up the google doc" | MECHANIC | Tracker tags map 1:1 to these five categories; assert all are inside the 20h bucket. | yes | EXECUTE |
| MEC-17 | Do not count: general prep, generic tech setup, breaks, waiting for training runs (if doing something else), or writing the MATS form answers. | "Not counted: General prep (paper reading, tutorials), that you would have done before deciding on a project … Generic tech set up, like renting and setting up a cloud GPU … Breaks … Time spent waiting for things to train (assuming you're doing something else during this time, eg training an SAE overnight) … Writing your answers to the MATS application form" | MECHANIC | Tracker has explicit excluded-category tags; audit that nothing excluded is misfiled. | yes | EXECUTE |
| MEC-18 | During the extra 2 hours, do not edit the rest of the write-up and do not write new experiment code — only new graphs/visualisations from existing data are allowed. | "I ask that you don't edit the rest of the write-up, and don't write any new experiment code, though you're welcome to write code to make new graphs/visualisations from data you already have, if it'll help present the results better" | MECHANIC | Freeze the write-up in git/Docs version history at the 20h mark; diff after the +2h window and assert changes are confined to the exec summary, form answers and figure files. | yes | WRITEUP |
| MEC-19 | If you totally change direction, you may reset the 20-hour timer. | "If you decide your project is doomed, you're welcome to give up and start a new one, and reset the timer" / "If you're totally changing directions (ie, so that your code and findings so far isn't particularly helpful for the new direction), I'm fine with you restarting the 20 hour limit." | MECHANIC | Log any reset with a dated justification that the prior code/findings do not carry over. | partial | EXECUTE |
| MEC-20 | Track your time (e.g. Toggl) and include a screenshot with the application doc. | "You're encouraged to track your time with a tool like Toggl and include a screenshot with the application doc" | MECHANIC | Assert a time-tracker screenshot image exists in the doc and its total matches the declared hours. | yes | SUBMIT |
| MEC-21 | *(Only if submitting prior work)* Include an executive summary and link, an estimate of hours the project took, a description of your specific contribution, and — if not obviously mech interp — why it shows relevant skills. | "I'm open to you writing an executive summary for that work, and linking to it, rather than doing the normal application. … **Please include an estimate of how many hours the project took you** … If other people worked on it with you, please include a description of what you specifically contributed … If it's not obviously a mech interp paper then please explain why you think it shows you have relevant skills." / "I'd prefer a standard application, and I'll judge these more harshly than normal applications" | MECHANIC | If the prior-work path is taken, assert all four elements present. | yes | SUBMIT |

---

## ADVICE

| ID | Requirement | Source quote | Class | Verification | Automatable | Gate |
|---|---|---|---|---|---|---|
| ADV-01 | Read "how my research interests have changed" before choosing a problem. | "I'm afraid my interests are somewhat vague and \"I know it when I see it\" (sorry!), so please read how my research interests have changed before choosing a problem." / "this is often misunderstood by applicants, so please read this section!" | ADVICE | Tick-box in the SELECT memo confirming the section was read, with a two-line summary of what it rules in/out. | no | SELECT |
| ADV-02 | Read the pragmatic interpretability post (or the 80,000 Hours podcast) to understand his current research approach. | "See my post on **pragmatic interpretability** (or this podcast episode) to learn about my current research approach" | ADVICE | Recorded in the prep log (does not count toward the 20h). | no | SELECT |
| ADV-03 | Riff off the suggested problems list rather than treating it as a constraint. | "Strong applications often riff off of these ideas - coming up with their own approach, but along similar themes to the below. You should not feel constrained to the problems on this list" | ADVICE | SELECT memo names the theme it riffs off and the personal twist. | no | SELECT |
| ADV-04 | Pick a problem where you know how to get started, and expect to scope the ambition down. | "**Warning**: The ideas below have **not** been filtered for \"I am confident someone could make progress on this in 20 hours\". Pick something where you have some idea of how to get started (or read around the field a bit and try to generate ideas and a sketch plan before picking a problem), and expect to need to scope the ambition down as the project goes on." | ADVICE | SELECT memo contains a concrete first-experiment sketch and a de-scoping fallback. | no | SELECT |
| ADV-05 | Do not trust LLM time estimates. | "Do not trust LLM time estimates, in my experience they're super off" | ADVICE | Compare your own estimate to any LLM estimate; plan against your own, with a 2x buffer. | no | SELECT |
| ADV-06 | Spend at most 5 of your hours reading papers and tutorials. | "**I recommend spending at most 5 of the 12-20 hours reading papers and tutorials**. You're welcome to do general reading and learning beforehand." | ADVICE | Tracker category `reading` ≤5:00. | yes | EXECUTE |
| ADV-07 | Use an agentic coding tool — Claude Code with Fable is the top recommendation (Max plan if affordable); Codex with GPT 5.6 Sol or Opus 5 in Claude Code are also solid. | "**My recommendation:** Claude Code running Fable (get the Max plan for the application period if you can - the rate limits matter for agentic research). GPT 5.6 Sol in Codex and Opus 5 in Claude Code are also solid choices." | ADVICE | Assert the tool is set up and its use is described in the write-up. | partial | SELECT/EXECUTE |
| ADV-08 | Describe your agentic LLM use in the application — it correlates with a ~3x acceptance rate. | "in the last round, applicants who described using LLMs agentically (Claude Code etc.) were accepted at ~3x the rate of those who mainly used LLMs for writing polish. The tools are a genuine edge - for the people who stay in control of them." | ADVICE | Assert the write-up/form contains an explicit paragraph on how you used agents and how you stayed in control. | yes | WRITEUP |
| ADV-09 | Practise LLM-assisted research before the 20 hours start. | "**Practice**: If you've never tried using an LLM for this kind of thing before, I recommend practicing before you start the official application - it's a skill and you improve with practice … It's much nicer if your 20 application hours are *not* your first 20 hours trying to do research with an LLM." | ADVICE | Prep log shows ≥1 practice speedrun before the clock starts. | no | SELECT |
| ADV-10 | Give the model an ambitious, open-ended task rather than over-constraining it, then analyse the output. | "**Give it free reign, then analyse**: Frontier models like Fable and Sol can be much more effective when given a more ambitious and open ended task, rather than extremely precise and constraining instructions" | ADVICE | Spot-check prompt logs for over-constrained micro-instructions. | no | EXECUTE |
| ADV-11 | Load the recommended context — by default the 600k-token file — into the model's context window. | "**Context is crucial**: LLMs are much more useful when they have the relevant information in the context window. … If you don't know what you need, just use this default file, and maybe include this activation doc." / "By default, just **put** **this 600k token file** **in the context window**" | ADVICE | Assert the context file is present in the working directory and referenced in CLAUDE.md/AGENTS.md. | yes | SELECT/EXECUTE |
| ADV-12 | Use anti-sycophancy framings to get real critical feedback. | "**Anti-sycophancy prompts:** By default, LLMs are bad at giving critical feedback. To get real feedback, open a new window and frame your request so the sycophantic thing to do is to be critical." | ADVICE | Keep the anti-sycophancy prompts used; assert ≥1 critique round per key decision and per draft. | partial | EXECUTE/WRITEUP |
| ADV-13 | Learn actively with LLMs, not passively — have them quiz you, and summarise your understanding back for critique. | "**Learn actively, not passively:** Don't just ask for an explanation. Use learning methods that forces you to be active. E.g. Have it to generate questions to test your understanding, or teach you via ask questions; Summarize your understanding/best guess back to the LLM in your own words and ask for critical feedback." / "This is not a *substitute* for understanding things yourself" | ADVICE | Prep log records self-tests taken and where you failed. | no | SELECT |
| ADV-14 | Write out why you are making each research decision and ask an LLM for critique with an anti-sycophancy prompt. | "**Research decisions:** … I highly recommend writing out why you are making these decisions and asking an LLM for thoughts, with an anti-sycophancy prompt. You shouldn't trust the LLM's judgment, but this forces you to make your thoughts explicit and often you may notice things you were missing." | ADVICE | Decision log with one entry per major pivot/design choice, each with the critique received. | partial | EXECUTE |
| ADV-15 | Use LLMs for drafting, brainstorming, several rounds of clarity/accuracy critique, and graph-making — with the paper-writing post and this application doc in context. | "I recommend having several rounds of giving it your draft (with an anti-sycophancy prompt) and asking it to critique you for clarity, find confusing sentences, and check for technical inaccuracies. … Put the application doc and my post on paper writing in the context. LLMs are fantastic at making graphs for you" | ADVICE | Assert ≥3 recorded critique rounds on the draft before submission. | partial | WRITEUP |
| ADV-16 | When learning a new technique, write it yourself first and use the LLM as tutor/reference, not as a replacement. | "**A caveat on learning:** If you are learning a new technique, first try writing things yourself, or use the LLM as a tutor/source of reference code. Use the LLM to help when you're stuck, not to replace the entire learning process - remember that you need to be able to make good research decisions and catch its mistakes." | ADVICE | For each new technique, a from-scratch attempt exists in the repo history before the agent-written version. | partial | EXECUTE |
| ADV-17 | Give your agent a persistent Python kernel (Jupyter via MCP, or IPython in tmux) instead of cold-start scripts, and instruct it accordingly. | "Best: give the agent a live Jupyter kernel via MCP. … Simple and unbreakable: a persistent IPython session in tmux. … Tell the agent (in CLAUDE.md / AGENTS.md): load models/data in dedicated cells at the top, never restart the kernel without asking, and save plots to disk as PNGs too." | ADVICE | Assert a persistent-kernel setup exists and CLAUDE.md/AGENTS.md contains the three instructions. | yes | EXECUTE |
| ADV-18 | Checkpoint expensive artifacts to disk and run long training as background scripts with logs; avoid Codex on .ipynb files. | "Either way: checkpoint expensive artifacts to disk (activations, datasets, finetuned weights) so a crashed kernel isn't a disaster, and run long training jobs as background scripts with logs, not notebook cells. … Codex is known to corrupt .ipynb files - with Codex, prefer plain .py scripts or the MCP route." | ADVICE | Assert checkpoint files exist for each expensive artifact; assert no .ipynb edited by Codex. | yes | EXECUTE |
| ADV-19 | Set a timer every hour or two to zoom out and ask whether you are making progress or in a rabbit hole; constantly ask "have I learned anything in the last 30 minutes?" | "I recommend setting a timer every hour or two to zoom out and ask if you're making progress or caught up in a rabbit hole." / "Constantly ask yourself: \"**Have I learned anything in the last 30 minutes?** Is this direction still fruitful?\"" | ADVICE | Recurring alarm + a one-line log entry per checkpoint. Script asserts checkpoint log density ≥1 per 2 hours of tracked time. | yes | EXECUTE |
| ADV-20 | Keep a running doc listing your hypotheses, and put key graphs and findings in it as you go. | "Keep a running doc with a list of your hypotheses. Alternate between designing an experiment to test one, running it, and analyzing the results. Put key graphs and findings in your doc, as you learn more about hypotheses - you don't want to forget where a key experiment is!" | ADVICE | Assert the running doc exists, is updated ≥1× per experiment, and every headline figure is indexed in it. | yes | EXECUTE |
| ADV-21 | Treat the exploration phase as information-gathering: get your hands dirty, read your data, prompt the model, and don't assume exploration ends once the problem is picked. | "**Exploration:** The goal here is simply to **gain information and build intuition**. A common mistake is thinking this stage ends once you've picked a problem … **Get your hands dirty**. Try things like reading your data, giving your model interesting prompts, or seeing what a sparse autoencoder tells you." | ADVICE | Time log shows an explicit exploration block with a written "what I learned" note. | partial | EXECUTE |
| ADV-22 | Read the research-process posts (Explore/Understand/Distill and Key Mindsets) and the ML-paper-writing post. | "My blog posts on my research process (Explore, Understand, Distill and Key Mindsets) have more detail" / "The advice in my post on writing ML papers may be helpful" | ADVICE | Prep-log tick; both linked into the LLM context for drafting. | no | SELECT/WRITEUP |
| ADV-23 | Use recommended tooling for model internals and APIs: nnsight or raw PyTorch hooks; OpenRouter for APIs; Nebius for CoT intervention; poe.com for quick model trials. | "To access a model's internals I recommend using nnsight as it's fairly performant and works well on larger models, or just asking your coding agent to use raw PyTorch hooks … If you need an LLM API, I recommend OpenRouter … If you want to intervene on the chain of thought of a reasoning model … I recommend Nebius … poe.com is a good way to try out lots of models" | ADVICE | Check dependencies in the repo match one of the recommended paths, or a reason is recorded. | partial | EXECUTE |
| ADV-24 | Pick subject models from the recommended set: Qwen 3.5/3.6 dense (4B/9B/27B) as default; deepseek v4 flash 0731 for a highly capable model; Gemma 3 + Gemma Scope 2 for SAE work. | "The Qwen 3.5 and 3.6 family are good default models, especially dense ones like 4B, 9B and 27B, they're fairly high quality. If you want to do interpretability on a highly capable model, deepseek v4 flash 0731 is a good choice … If you want to work with SAEs, use Gemma 3 and Gemma Scope 2." | ADVICE | Grep the write-up for the subject model name against this allowlist; any model outside it requires a recorded justification. | yes | SELECT |
| ADV-25 | Rent your own cloud GPU (runpod, or vast.ai if cost-constrained) rather than using Colab. | "I recommend renting and using your own cloud GPU, rather than toy coding environments like Colab … To rent GPUs, I recommend runpod.io - and vast.ai is notably cheaper if cost is a constraint" | ADVICE | Confirm a GPU pod is provisioned before the clock starts (setup time is not counted). | no | SELECT |
| ADV-26 | Use the recommended learning resources: ARENA tutorials (chapter 1.2 first 3 sections if time-constrained), the reading list, Ferrando et al., the glossary, key interp and black-box technique lists. | "The ARENA tutorials are fantastic as a practical coding intro to mech interp techniques. If you're new to mech interp and time constrained, prioritise doing the first 3 sections of chapter 1.2 to get the basics" / "Key interp techniques to focus on: Direct logit attribution, activation patching, maximum activating dataset examples, linear probes, steering vectors, sparse autoencoders. Key black box techniques: Prompting LLMs, fine-tuning (including LoRAs). Baselines are important!" | ADVICE | Prep log covers the six key interp techniques and the black-box techniques at a working level; self-test on the token-forcing question ("Good test - do you understand why token forcing is effective and hard to fix?"). | no | SELECT |
| ADV-27 | *(Conditional)* Heed the per-topic constraints in the problems list: read the model forensics paper before a forensics project; steganography work must let the model do tasks it couldn't without a CoT; avoid TDA if you have never used it; for alignment training use more than one eval and measure improvement far from the training domain. | "Please look at our paper if you want to do a project here, there's a lot of relevant advice!" / "**Note that this needs to allow the model to do tasks it couldn't do without a chain of thought to be interesting.**" / "**Warning: If you haven't played with TDA before, this may not be practical to work with in 20 hours**" / "The key metric of success is improvement on domains far from where you trained. I encourage using more than one eval!" | ADVICE | If the project falls in one of these areas, assert the corresponding condition is met and recorded (paper read; CoT-necessity check run; TDA experience declared; ≥2 evals with OOD domains). | partial | SELECT/EXECUTE |
| ADV-28 | A good title is worth having. | "(Bonus points for a great title)" | ADVICE | Assert the doc title is specific and descriptive of the finding, not generic. | no | WRITEUP |
| ADV-29 | If this material sounds boring to you, apply to a different mentor instead. | "If you hear all this and are like, \"that sounds really boring, I am no longer interested\", then great - we probably wouldn't have been a good match! It's much better to learn that now than later." | ADVICE | Honest self-check at SELECT; recorded go/no-go decision. | no | SELECT |

---

## Requirements that are automatable

Script spec — each line is one assertion the conformance checker should make.

| ID | What the script must assert |
|---|---|
| BLK-10 | The example-selection code sets and prints a random seed, and that seed string appears in the write-up; hand-label count ≥30 with an agreement rate reported. |
| BLK-11 | Every results table contains ≥2 columns, at least one tagged/named as a baseline (`random`, `baseline`, `control`, `probe`, `prompt`). |
| BLK-14 | Zero unjustified hits for the banned-topic list `{grokking, circuit finding, SAE hill-climbing, basic science of SAEs, toy model, algorithmic task, purely theoretical}` in the project one-liner and abstract. |
| BLK-15 / BLK-16 | Zero occurrences of `gpt-?2`, `pythia`, `gemma[- ]?2` in the subject-model field; ≥1 model from the current allowlist present. |
| BLK-24 | Every number appearing in the write-up matches a value in the canonical results JSON/CSV within tolerance; report every mismatch. |
| BLK-36 | Every named experiment in the doc maps to a committed script/notebook and a raw output file, with a commit timestamp inside the tracked window. |
| BLK-04 / BLK-05 | Banned-phrase and stylometric scan of the exec summary and form answers (LLM-tell lexicon, em-dash density, "not X but Y" construction rate) — flag for human adjudication. |
| BLK-09 | Any section presenting qualitative examples must also declare a sample size `n=` or be explicitly tagged `existence proof`. |
| BLK-12 | Presence check for at least one of the three cheap controls per method claim in the controls ledger. |
| BLK-18 | The "phenomenon exists in my setting" section appears in the doc before the first downstream analysis heading. |
| SCR-02 | Methods block contains all of: data generation, prompts, metric definition, hyperparameters, sample size. |
| SCR-04 | Every acronym/jargon term is defined at first use; every figure has axis labels, units and a legend. |
| SCR-07 | Exec summary contains ≥1 model name, ≥1 named experiment, ≥1 numeric result, ≥1 limitation sentence. |
| SCR-17 | Sections named `Limitations`, `Speculative`/confidence-labelled claims, and `Next steps` all exist. |
| SCR-19 | A "what I verified" section exists and contains ≥3 countable verification statements. |
| SCR-20 | An independent re-derivation script exists per headline number and agrees with the pipeline within tolerance. |
| SCR-22 | Every claim carries a `existence-proof` / `method-claim` tag; every `method-claim` has a baseline column. |
| SCR-24 | Time tracker: hours(code+experiments) > hours(reading). |
| SCR-28 | If `sae|crosscoder|attribution graph|transcoder` appears in methods, a prompting or linear-probe comparison section also exists. |
| SCR-29 / SCR-31 | Count of headline insights ≤2; count of distinct threads ≤3; top thread ≥50% of experiment hours; ≥3 supporting experiments per insight. |
| SCR-30 | No sub-thread exceeds its preset hour budget without a logged go/pivot decision. |
| SCR-33 | Every experiment section contains `hypothesis`, `possible outcomes`, `why now` sub-fields. |
| SCR-35 | Section order ≠ chronological experiment-log order; headline finding is the first post-exec-summary section. |
| SCR-37 | Form field contains 1–3 evidence items, each with a URL and a relevance sentence. |
| MEC-02 | Submission timestamp < 2026-09-04T23:59 PT. |
| MEC-04 / MEC-05 | Both artifacts exist; the doc's first heading is the executive summary; the form contains the doc URL. |
| MEC-06 | Exec summary word count ≤600 AND page count ≤3. |
| MEC-07 / MEC-09 | ≥1 image inside the exec summary page range; ≥1 figure per key experiment in the body. |
| MEC-08 | The three suggested exec-summary sections are present; one paragraph + one graph per key experiment. |
| MEC-12 | Fetch every link in the doc (and the doc itself) with no credentials; all must return 200 and render. |
| MEC-14 / MEC-15 / MEC-16 / MEC-17 | Tracker totals: counted categories ≤20:00; exec-summary/form category ≤2:00; every tracked entry carries a counted/not-counted tag. |
| MEC-18 | Git/Docs diff between the 20h freeze commit and the submitted version touches only exec summary, form answers, and figure files. |
| MEC-20 | A time-tracker screenshot image is embedded in the doc and its total matches the declared hours. |
| MEC-21 | If prior-work path: hours estimate, contribution description, relevance explanation and link all present. |
| ADV-06 | Tracker category `reading` ≤5:00. |
| ADV-08 | Write-up contains a paragraph describing agentic LLM use and human oversight. |
| ADV-11 | The 600k context file is present in the working directory and referenced from CLAUDE.md/AGENTS.md. |
| ADV-17 / ADV-18 | Persistent-kernel config exists; CLAUDE.md contains the three kernel instructions; checkpoint files exist for each expensive artifact; no Codex-edited `.ipynb`. |
| ADV-19 | Zoom-out checkpoint log density ≥1 entry per 2 hours of tracked time. |
| ADV-20 | Running hypotheses doc exists, updated ≥1× per experiment, indexes every headline figure. |
| ADV-24 | Subject model name is in the recommended allowlist, or a justification field is non-empty. |

---

## Ambiguities

**1. Depth vs breadth — he flags this tension himself.**

> "A common mistake is getting caught in **rabbit holes** - finding one random anomaly or detail that (in my opinion) isn't very interesting, and spending the whole time zooming on that."

versus

> "Another is spreading yourself too thin - doing lots of things superficially, but without enough depth for any one to be interesting"

and his own acknowledgement:

> "Yes, these tips point in opposite directions. Sorry! You need to balance between these two extremes. This is hard and I don't expect anyone to do it perfectly."

*Governance implication:* this cannot be a mechanical gate. Resolve it with the hourly zoom-out checkpoint (ADV-19) as the audit trail rather than a threshold.

**2. Cherry-picking is a red flag — except when it isn't.**

> "Crucially, **avoid relying only on a few cherry-picked qualitative examples**—this is a major red flag."

versus

> "Sometimes you want to give an existence proof (e.g., find an example of an interesting phenomenon), where cherry-picking is fine."

and, pulling a third way:

> "include some randomly selected qualitative examples in the write-up … Randomly selected, not cherry-picked!"

*Resolution rule to adopt:* tag each claim `existence-proof` (cherry-picking permitted, must be labelled as such) or `general-claim` (random sampling with a recorded seed mandatory). Never let an unlabelled cherry-pick carry a general claim.

**3. The hour budget is stated three different ways.**

> "Spend **~16 hours (max 20)**"

versus

> "**I recommend spending at most 5 of the 12-20 hours reading papers and tutorials**"

"12-20" appears nowhere else; the headline figure is "~16 (max 20)". Additionally:

> "Sanity-checking is worth a lot of your time and care - I'd guess a meaningful fraction of your 20 hours."

*Implication:* if reading can take 5h and sanity-checking "a meaningful fraction" of 20h, the residual for experiments is small. Budget explicitly: reading ≤3h, sanity-checking ~5h, experiments ~8h, write-up ~4h, and treat the 5h reading figure as a ceiling not a target.

**4. Executive summary length: 3 pages vs 600 words.**

> "The first 1-3 pages of the google doc should be an executive summary … Something at **~1 page** (including graphs) is great, **max 3 pages** and **max 600 words**."

600 words will not fill 3 pages of prose; the page allowance only makes sense if graphs consume most of it. Both limits bind independently — treat 600 words as the hard constraint and pages as the visual budget. It is also unclear whether the "randomly selected qualitative examples … ideally just after the executive summary" count inside the 3 pages; assume they sit *outside* the exec summary and outside the 600 words.

**5. Use LLMs heavily — but nothing may read as LLM-written.**

> "You are actively encouraged to use LLM assistance for your application—I want to gauge how well you'll do at research in practice, so if you'd use it there, use it here! And if you don't use LLMs as part of your research, I think you're probably making a bad decision."

versus

> "**Please do not just submit raw LLM output for the application form or executive summary**. Write these yourself, in your own voice, even if you think an LLM will sound better. … Answers that read like they were written by an LLM are a significant negative signal"

and

> "Docs that read like LLM slop will be rejected."

*Resolution rule:* LLM for code, graphs, brainstorming, and critique of your draft; zero LLM-generated sentences in the exec summary and form answers.

**6. Old models are a listed mistake — but Gemma 2 is where his own SAEs live.**

> "**Only studying old models** (GPT-2, Pythia, Gemma 2)"

versus

> "Gemma Scope, high quality open weight SAEs on every layer and sublayer of Gemma 2 that my team produced"

partially reconciled by:

> "If you want to work with SAEs, use Gemma 3 and Gemma Scope 2."

*Resolution:* Gemma Scope on Gemma 2 may be used as a supporting/reference tool, but Gemma 2 must not be the sole subject model. Prefer Gemma 3 + Gemma Scope 2.

**7. Background doesn't matter — but prior work is strong evidence.**

> "**All backgrounds & experience levels welcome** - I want to work with the most promising people, not just those with the best credentials!" / "I don't care too much about prior knowledge - if you're good enough to do a decent application task, that's good enough for me."

versus

> "Naturally, examples of good prior mech interp work are strong evidence here. … These *can* be legible credentials, but aren't always."

and the worked example where a credential flipped the decision:

> "Note: I bumped this up to an accept because I was impressed by the candidates profile … They'd further demonstrated impressive agency with some of their other achievements, like founding a start-up"

*Implication:* the task dominates, but the evidence question (SCR-37) is a real tiebreaker and should not be left thin.

**8. Prior-work submissions: discouraged and encouraged in consecutive sentences.**

> "I'd prefer a standard application, and I'll judge these more harshly than normal applications (you likely had much more time)"

versus

> "but if you otherwise won't have time to apply I'd prefer to get these!" / "If you won't even have time to write an executive summary, I'd still rather get your application than nothing, but have an extremely high bar for those."

*Implication:* only take this path if a standard application is genuinely impossible.

**9. Resetting the clock vs being judged on productivity.**

> "If you decide your project is doomed, you're welcome to give up and start a new one, and reset the timer" / "If you're totally changing directions … I'm fine with you restarting the 20 hour limit."

versus

> "**Productivity**: While it's more important to do things well than do them fast, the ideal is both. Some researchers are a lot more productive per unit time than others, and they get a lot more done."

The reset is permitted but the output is still compared against 20-hour applications that did not reset. Treat a reset as costly, not free.

**10. Code is optional — but he will run agents over it and you are accountable for its quality.**

> "You're encouraged to include code, but it's not required, I'll largely use it to give my agents context and ask them questions about what you actually did"

versus

> "It is your responsibility to ensure your code and writing are high quality."

and

> "read the code that produced it, check the numbers in the write-up against the actual outputs"

*Implication:* code is nominally optional but functionally load-bearing — omitting it removes your best defence against the "an agent did this" blocker (BLK-03). Include it, and make sure it withstands agent interrogation.

**11. The "reading papers" boundary in the time limit is fuzzy.**

Not counted: "General prep (paper reading, tutorials), that you would have done before deciding on a project". Counted: "Reading papers (chosen because they're relevant to your project)". The distinction is counterfactual and self-assessed; the stated fairness principle — "anything you could reasonably have done to learn mech interp on your own, before thinking of a problem to work on, is totally fine" — is the only tiebreaker. Log every paper with the timestamp of when the project was chosen so the split is auditable.

**12. A truncated sentence in the changes section.**

> "The application process is broadly the same, but I've emphasised"

The sentence ends mid-clause. The section is also headed "What's changed from MATS 10.0?" while the table of contents and the Key Details section reference "What's changed from MATS 9.0?" and "What's changed from MATS 8.0?" — so there may be missing text about what specifically was emphasised. The surrounding bullets suggest it is: broadened research interests, stronger agentic-tooling recommendation, and greater weight on the application form questions.agentId: a4007e46e193739dc (use SendMessage with to: 'a4007e46e193739dc', summary: '<5-10 word recap>' to continue this agent)
<usage>subagent_tokens: 123783
tool_uses: 9
duration_ms: 425103</usage>