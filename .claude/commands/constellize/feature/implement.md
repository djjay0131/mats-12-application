---
description: Implement a SPECIFIED feature through structured phases (context loading, star identification, gap analysis, test-first generation, adversarial test review, integration validation)
argument-hint: <feature-name from llm/features/ — e.g. "final-project-reframe">
---

Read `.claude/skills/constellize:feature:implement/SKILL.md` and follow its instructions exactly. The skill expects `llm/features/<feature-name>.md` to exist with Status: SPECIFIED — if not, stop and tell the user to run `/constellize:feature:specify` first.

Adapt phase 4–6 conventions (test framework, build commands) to the actual project: not every project is Python+pytest+uv. The phase structure is rigid; the tooling is whatever the project uses (e.g., LaTeX projects verify by building the PDF and running spec-defined verification scripts).

Pass the user's request through to the skill as `$ARGUMENTS`:

$ARGUMENTS
