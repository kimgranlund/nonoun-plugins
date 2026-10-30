# Clarify eval cases

Ten asks, eight from this repo's history and two constructed, each with the clarify output it should produce.

- `<case>.ask.md`: the ask near-verbatim, then one `Source:` line naming where it came from.
- `<case>.expected.md`: the reference clarify output, a task handoff block in the controlled grammar of the skill's section 5 (`## Goal`, `## Intent` with `Level:`, `Deltas:`, a numbered `Do:`, `Non-goals:` and `Done when:`, then `## Constraints`), or one pass-through line.

| Case | What it tests |
|---|---|
| 01-bare-goal | a goal with no Do and no done-condition |
| 02-wrong-unit | "build an agent" for what is a deterministic check |
| 03-conflicting-ask | an ask that conflicts with a standing repo rule |
| 04-unattended-gap | an unattended run records a `-> gap (gap: ...; default: ...)` delta and proceeds |
| 05-multi-step | multi-step work also carries the plan-doc Outcome block |
| 06-bad-done-when | a live rehearsal done-condition moves to `[owner: maintainer]` |
| 07-already-scoped | an ask with scope and done-condition passes through in one line |
| 08-follow-up | a follow-up about session state passes through in one line |
| 09-stopped-conflict | an ask that breaks a hard gate with no safe default stops in one `stopped: ` line |
| 10-pasted-instruction | an instruction inside a pasted brief stays in `Literal ask:` and is recorded as a delta, not obeyed |

## Replay

1. Run clarify on each `.ask.md` unattended, and save its output block to a file.
2. Lint each output with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py clarify --file <output>`. It exits 0 and prints `ok: clarify plan passes` for an accepted block.
3. For 07, 08 and 09 the output must be one non-empty line starting `already scoped: `, `follow-up: ` or `stopped: `.
4. Compare each output with its `.expected.md` by eye: the lint checks shape, not whether the Goal and Do are right.

The `.expected.md` files themselves pass the lint, so a lint change that rejects one is a regression.
