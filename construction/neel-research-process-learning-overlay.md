# Neel Research-Process Learning Overlay

Status: Operative process overlay for the J-Lens candidate
Applies to: the design-verification sprint and, if selected, the 16-hour main experiment
Purpose: make the project follow Ideation → Exploration → Understanding → Distillation while teaching Jason how to make the research decisions himself

## Core correction

The earlier plan treated a crisp hypothesis and an early preregistration as the starting point. That is too early for this project. We still have load-bearing uncertainty about what a J-Lens readout means, which model/lens pairing is usable, and whether a single activation can identify a binding. We are therefore in **Exploration**, not yet **Understanding**.

The design-verification sprint is best understood as an **Explore → Understand transition sprint**:

- V1 gains surface area on the tool and its failure modes.
- V2 gains surface area on what “J-space” operationally means and generates rival explanations.
- V3 converts what we learned into explicit hypotheses and a discriminating experiment.
- A GO means “ready to enter Understanding.” It does not mean the scientific hypothesis is verified.

## The four stages and their gates

| Stage | North star | This project | Exit gate |
|---|---|---|---|
| Ideation | Choose a fruitful problem | Establish the J-Lens bag-of-concepts gap, relation to prior work, importance, tractability, and fit with Neel's interests. | Jason can explain in his own words what is known, what remains open, why the answer matters, and why this is feasible now. |
| Exploration | Gain information and surface area | Run small positive controls, visualize readouts, inspect anomalies, compare observation positions, and identify shortcuts. | We can state one key hypothesis, at least two plausible alternatives (including “something else”), their differing predictions, and the smallest experiment that separates them. |
| Understanding | Convince ourselves for or against a key hypothesis | Freeze the dataset split, metric, controls, and claim; then run held-out passive and causal tests. | Evidence survives strong baselines, shortcut checks, bug checks, and at least one serious alternative explanation. |
| Distillation | Compress into concise, rigorous truth | Write the result and limitations from frozen evidence, including a clean null if that is what happened. | A skeptical reader can trace every claim to an artifact and restate what remains unknown. |

Moving backward is allowed. An anomaly during Understanding can send us briefly back to Exploration. This is an evidence-driven stage change, not failure or wheel-spinning.

## The 60-minute apprenticeship loop

Each counted hour uses separate execution and reflection modes.

### Minutes 0–5 — Jason predicts

Before the agent reveals its judgment, Jason writes:

1. What stage are we in, and what is that stage's north star?
2. What do I expect to observe, and why?
3. What would I observe under the strongest alternative explanation?
4. What result would most change my mind?
5. Why is this the highest-information action available this hour?

### Minutes 5–45 — Execute one fast feedback loop

- Run the smallest experiment that can teach us something.
- Save raw output before interpretation.
- Keep a highlights/anomalies note, including ugly or confusing results.
- If blocked for 20 minutes, use the registered fallback and preserve the question.
- Do not silently turn debugging observations into scientific evidence.

### Minutes 45–55 — Jason interprets first

Jason writes, before seeing the agent's interpretation:

- What happened?
- Which prediction was wrong or right?
- Is the observation more likely under one hypothesis than another?
- What is the simplest boring explanation?
- What remains unexplained?

### Minutes 55–60 — Coach feedback and decision

The agent then:

1. Critiques Jason's reasoning, not merely the result.
2. Names one good research-taste move and one missed consideration.
3. Separates fact, inference, and speculation.
4. Recommends exactly one next action and estimates its information gain per unit time.

Record one decision:

- **CONTINUE:** next planned loop remains highest value.
- **CHANGE LOOP:** stay in the same stage but try a more informative experiment or representation.
- **RETURN TO EXPLORE:** the hypothesis/experiment was ill-posed or an anomaly is load-bearing.
- **PIVOT CANDIDATE:** only a load-bearing assumption failed and no bounded same-question fallback remains.

The first three are normal progress. Do not use PIVOT merely because a hypothesis was false or a result was messy.

## Required hypothesis table before Understanding

V3 cannot return GO until Jason completes this table in his own words.

| Hypothesis | Gears-level story | Distinctive prediction | Cheapest discriminating test | What would falsify it? |
|---|---|---|---|---|
| H-J | Binding information is captured in the J-space component. | J-space beats matched controls and non-J-space on template-held-out binding, with targeted causal effects. | To be filled after V1–V2. | To be filled. |
| H-N | Binding information is primarily outside the reconstructed J-space. | Non-J-space retains binding performance while J-space retains entities but loses role selectivity. | To be filled after V1–V2. | To be filled. |
| H-R | Binding is distributed across positions or only appears after role-conditioned retrieval. | Pre-query single-vector decoding fails while pooled or role-conditioned states succeed. | To be filled after V1–V2. | To be filled. |
| H-S | Apparent success is a shortcut or readout artifact. | Lexical/template/permutation baselines match the method or success vanishes under counterfactual controls. | To be filled after V1–V2. | To be filled. |
| H-? | An explanation we have not thought of yet. | Unexplained anomalies remain after the named hypotheses. | Ask what observation none of H-J/H-N/H-R/H-S predicts. | Retire only after broad surface-area checks. |

## Main 16-hour stage map

If the candidate is selected, the existing hour rows are retained but interpreted as follows:

- **Hour 1 — Ideation exit:** source memo and gap check.
- **Hours 2–6 — Exploration:** hypotheses are provisional; generate examples, reproduce the method, visualize results, and collect anomalies. Do not inspect held-out data.
- **Hour 7 — Explore → Understand gate:** run development controls, complete the hypothesis table, predict outcomes, and only then freeze the analysis and claim boundaries.
- **Hours 8–14 — Understanding:** run frozen held-out tests, causal checks, alternatives, and robustness. Dip back into bounded exploration only for a load-bearing anomaly; document why.
- **Hours 15–16 — Distillation:** methods/results first, then introduction/discussion. Red-team every claim and report negative evidence and limitations.

This changes Hour 2 from a final preregistration to a **provisional hypothesis-and-prediction memo**. The actual preregistration occurs at the end of Hour 7, after exploration has taught us what question and experiment are defensible.

## How the AI helps Jason learn instead of replacing him

The agent must not provide the interpretation before Jason records a prediction and update. Its role is:

- prompt Jason for a stage diagnosis and prediction;
- offer tools, implementation help, literature retrieval, and alternative hypotheses;
- ask for Jason's interpretation before giving its own;
- compare Jason's reasoning with the evidence;
- explain why an experiment is or is not discriminating;
- maintain the log and point out recurring judgment errors;
- invite Jason to paraphrase the lesson in his own words.

At the end of each stage, Jason writes a five-sentence teach-back:

1. What was the stage's north star?
2. What did I initially believe?
3. What evidence changed my mind?
4. What research decision would I make differently next time?
5. What reusable heuristic did I learn?

## Process metrics

Track these alongside scientific metrics:

- experiment idea → saved result latency;
- number of substantive observations per hour;
- prediction accuracy and calibration;
- number of alternative hypotheses considered before commitment;
- anomalies left unexplained;
- time spent on the largest blocker;
- decisions where mentor/agent feedback differed from Jason's prior prediction.

These are diagnostic, not performance targets. The goal is to notice and improve the process without creating incentives to manufacture activity.

## Sources

- Neel Nanda, *How I Think About My Research Process: Explore, Understand, Distill*: https://www.alignmentforum.org/posts/hjMy4ZxS5ogA9cTYK/how-i-think-about-my-research-process-explore-understand
- Neel Nanda, *My Research Process: Key Mindsets — Truth-Seeking, Prioritisation, Moving Fast*: https://www.alignmentforum.org/s/5GT3yoYM9gRmMEKqL/p/cbBwwm4jW6AZctymL
- Neel Nanda, *My Research Process: Understanding and Cultivating Research Taste*: https://www.alignmentforum.org/posts/Ldrss6o3tiKT6NdMm/my-research-process-understanding-and-cultivating-research
