# Memory Bank

Living documentation. Read `activeContext.md` first — it is the single
source of truth for where the project stands right now.

| File | Holds |
|---|---|
| `projectbrief.md` | Goal, the selected project, scope, success criteria, constraints. Changes rarely. |
| `techContext.md` | Model, lens, compute, tooling versions, known environment issues. |
| `systemPatterns.md` | Repository layout and the conventions: conformance layers, the three ledgers, the figure registry, the report build, governance flow. |
| `activeContext.md` | Current focus, next actions, open decisions, live risks. Updated every session. |
| `progress.md` | Append-only log of what happened and when. |
| `time-log.md` | The 20-hour counted-time ledger. |

Placement rule: goals and constraints → `projectbrief`; tooling and setup →
`techContext`; architecture and patterns → `systemPatterns`; current state →
`activeContext`; completed work → `progress`.

Keep every file under 150 lines. Extract detail into `details/` and leave a
one-line summary with a link.
