# Workflow-stage pilot observation, 2026-09-28

This is an author-written manual exercise record for the original `cce84c8` pilot. It is not a planner, builder, or verifier role result. No model runner was launched, and there is no `runs.jsonl` row or role verdict. The original checked material included the edited skill and references, the SDLC Lite handoff format, and this task's handoffs at that revision. The illustration now lives under `docs/validation/`, outside the live `.sdlc/` task root; the SDLC Lite handoff-format addition was removed after review.

| Reusable stage | Actual input at this boundary | Actual output and observation |
| --- | --- | --- |
| [Frame the change](../../../plugins/progressive-context/skills/progressive-context/references/examples/small-repository-change.md#frame-the-change) | Approved pilot scope; repository and plugin guidance; base `a4404cb` | [Task handoff](handoff.md) names the goal, source context, constraints, current stage, and unresolved limits. [Exercise plan](exercise-plan.md) is author-written and identifies two concrete steps. |
| [Make the change](../../../plugins/progressive-context/skills/progressive-context/references/examples/small-repository-change.md#make-the-change) | Task handoff and the generated [step 1](step-1/handoff.md) and [step 2](step-2/handoff.md) handoffs | [Stage guidance](../../../plugins/progressive-context/skills/progressive-context/references/workflow-stages.md), [reusable example](../../../plugins/progressive-context/skills/progressive-context/references/examples/small-repository-change.md), and the original optional links in two plugin skills. Those files were the original implementation; no builder report was produced. |
| [Check and hand off](../../../plugins/progressive-context/skills/progressive-context/references/examples/small-repository-change.md#check-and-hand-off) | Changed files and task criteria | Command observations below. There is no independent verifier report, and this exercise makes no capability reuse claim. |

Commands run from the repository root during the original `cce84c8` exercise and observed results (paths are historical and refer to the layout at that revision):

| Command | Observation |
| --- | --- |
| `python3 plugins/sdlc-lite/scripts/steps.py lint .sdlc/workflow-stage-pilot/exercise-plan.md` | `steps lint: ok` |
| `python3 plugins/sdlc-lite/scripts/steps.py split .sdlc/workflow-stage-pilot/exercise-plan.md` | Wrote the two linked step handoffs above from the author-written plan. |
| `python3 plugins/sdlc-lite/scripts/steps.py next .sdlc/workflow-stage-pilot/step-1` | `build L1`, reason: no builder result. This is the existing next-action tool's output, not a stage status. |
| `python3 scripts/check-packaging.py` | Passed catalog parity, identity, skill routes, hook isolation, and context links. |
| `python3 plugins/sdlc-lite/scripts/check.py` | Passed 18 role levels and 8 agents checked. |
| `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` | Generated Codex agent definitions verified; no definitions changed. |
| `python3 /Users/kimba/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/progressive-context/skills/progressive-context` | Skill valid. |
| `python3 /Users/kimba/.claude/skills/author-cross-harness-plugins/scripts/validate_cross_harness.py plugins/progressive-context` | Clean, zero errors and warnings. |

The generic Codex `quick_validate.py` rejects the unchanged `user-invocable: false` key in SDLC Lite's `handoff-format` frontmatter. The cross-harness validator also rejects many existing Claude tokens throughout SDLC Lite. These are validator compatibility limits, not new findings in the stage pilot. The repository's packaging and SDLC contract checks passed.

The stage contracts guided which saved inputs to load and which outputs to inspect. `steps.py` parsed the plan and supplied the next action. No tool reads these stage headings as executable gates, no fresh-context model run was made, and task checks do not establish qualification for capability reuse.

## Review cleanup, 2026-09-28

After review, this author-written illustration moved from `.sdlc/` to `docs/validation/`, and the Progressive Context sentence was removed from SDLC Lite's handoff-format skill. The author-written plan gained runnable criteria, and `steps.py split` regenerated both illustrative step handoffs. These are documentation examples, not open SDLC tasks or role runs.

The revised plan passed `steps.py lint`; all six command criteria passed against the repository. A temporary copy of `workflow-stages.md` with Review changed to unconditional failed the first criterion (exit 1); the shipped source was not changed for that control. Packaging, SDLC role contracts, generated Codex agent parity, and the Progressive Context skill validator passed. The board rendered with `--root .sdlc --summary` included the open ticket only and no workflow-stage pilot. Local links and `git diff --check` passed. The earlier command table remains the historical observation at `cce84c8`, including its then-valid `.sdlc/` paths.
