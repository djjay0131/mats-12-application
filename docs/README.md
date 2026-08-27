# docs/

This directory is deliberately small. It holds **only** what
`agentic-governance` fixes at a known path:

| Path | Why it must live here |
|---|---|
| `adr/` | Decision records. `governance-checks.mjs` reads `docs/adr/README.md` and `docs/adr/NNNN-*.md` directly. |
| `governance-delta.md` | The project's local governance facts. The canonical docs and the `governance:establish` skill both expect this exact path. |

Everything else that would conventionally sit in a `docs/` folder — the plan,
the research, the application material, the construction workspace — lives
under `llm/`, per `governance-delta.md` §Repository Layout. That is the
portfolio convention, matching `soa-agentic-se` and `reliable-trustworthy-se`.

If you landed here looking for the project plan, it is
[`llm/plan/PLAN.md`](../llm/plan/PLAN.md).
