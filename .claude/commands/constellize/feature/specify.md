---
description: Build a feature specification through structured phases (repo analysis, research, problem definition, adversarial interview, sample implementation, drafting, dual-persona review, final spec)
argument-hint: <one-line feature request>
---

Read `.claude/skills/constellize:feature:specify/SKILL.md` and follow its instructions exactly. The skill is rigid — execute every phase in order, do not skip the adversarial interview, and write the final spec to `llm/features/<feature-name>.md` in kebab-case with Status: SPECIFIED.

Pass the user's request through to the skill as `$ARGUMENTS`:

$ARGUMENTS
