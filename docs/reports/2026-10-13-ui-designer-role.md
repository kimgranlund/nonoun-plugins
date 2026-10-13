# ui-designer role: level rows and wiring

Recorded: 2026-10-13

Ticket: T-0520. This records a user decision and how the role is wired. No experiment was run.

## Decision

The four rows are the user's stated choices of 2026-10-13 in T-0520. No model or effort was compared.

| Host | Level | Model | Effort |
|---|---|---|---|
| Claude | L1 | opus | medium |
| Claude | L2 | opus | high |
| Codex | L1 | gpt-6.1-sol | medium |
| Codex | L2 | gpt-6.1-sol | high |

The Claude rows live in `plugins/sdlc-lite/adapters/claude/levels.json` and are mirrored by the `ui-designer:L<n>)` case rows of `plugins/sdlc-lite/scripts/run.sh`. The Codex rows live in `plugins/sdlc-lite/adapters/codex/models.json`. The eval that cites this report locks the table. Its date is 2026-10-14 because the eval it replaces, `.sdlc/evals/0009-model-batch-roles.md`, is dated 2026-10-14 and a replacement must not be earlier.

## Wiring

`ui-designer` is one role with three modes (`mode: plan`, `mode: review`, `mode: generate`, one line in the handoff). It holds the builder's write allowances.

Why one role and no gate per mode: every write gate keys on the role name, never on a handoff line.

- `plugins/sdlc-lite/hooks/_role.sh`: `SDLC_READONLY_ROLES` is a list of role names.
- `plugins/sdlc-lite/hooks/block-role-write.sh`: acts only when the resolved role is in that list.
- `plugins/sdlc-lite/scripts/claude_roles.py`: `WRITERS` decides which generated definitions get `disallowedTools`.
- `plugins/sdlc-lite/scripts/run.sh`: the `read_only` case lists role names.
- `plugins/sdlc-lite/scripts/codex_roles.py`: `sandbox_mode` is picked by role name.

A gate per mode would need a new mechanism the ticket does not ask for. So the rule that plan and review never edit is held by the role contract (`plugins/sdlc-lite/agents/ui-designer.md`: "Generate is the only mode that edits.") and by `check.py` item 61, which requires that sentence, the three mode lines and both pass names in the role file, and requires the role to be a writer on both sides (`claude_roles.WRITERS`, and absent from `SDLC_READONLY_ROLES`). No hook enforces it.

Other wiring:

- Result schema in `plugins/sdlc-lite/scripts/results.py`: key section `Mode` with first line `plan`, `review`, `generate`, or `blocked: <question>`; sections `Mode`, `Decisions`, `Findings`, `Changes`, `Context used`, `Carry forward`.
- One-shot role: `ui-designer` is in `PRUNE_ROLES` of `plugins/sdlc-lite/scripts/dispatch.py`. A failed generate run is dispatched again, not resumed.
- A conductor session cannot spawn the bare name (`plugins/sdlc-lite/hooks/block-role-spawn.sh`).
- Start path: the `ui-designer` row of `plugins/sdlc-lite/skills/agent/SKILL.md`. No new skill and no `/chain` route.

## Not proven

- Live behavior. No plan, review, or generate run of the role has been made on either host. The live-run report lands in step 2 of T-0520.
- That a plan or review run leaves the tree unchanged. The contract says so and nothing enforces it.
- The level rows. They are a user decision with no pass rate or cost behind them.
- Planner intake of a ui-designer result. The planner does not read one yet.
