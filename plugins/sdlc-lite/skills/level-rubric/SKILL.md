---
name: level-rubric
description: "Level tables and routing rubrics for every sdlc-lite role (model and effort per level, and how to pick a level). Reference for the launcher skills; not a command."
user-invocable: false
---

**Codex host:** Before following this workflow, read [the Codex adapter](../sdlc-lite/SKILL.md) and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

The tables below describe the Claude backend. For Codex, model and effort are defined in `adapters/codex/models.json`; the level scope and escalation rules below still apply. The Codex runner records its selected model. When the builder and verifier models match, the Codex verifier switches to the model that `verifier_alternates` in `adapters/codex/models.json` maps the builder's model to. With no alternate configured, the verifier keeps the builder's model and the runner records `shared_with_builder` in the result header and `runs.jsonl`.

The Claude model and effort per level live in `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh`. This file says how to pick a level. Keep the two in sync.

## How to resolve a level

Use the first source that gives one:
1. A level in the user's arguments.
2. A `level: Lx` line in the handoff (set by the planner, per step).
3. The role's rule below. Pick the **lowest** level whose row fits every signal, then state the level and a one-line reason before running.

## builder (L1 to L5)

| Level | Model / effort | Fits when |
|---|---|---|
| L1 | Sonnet low | Mechanical: rename, boilerplate, config, one file, spec fully given |
| L2 | Opus low | Small change in a known pattern, 1 to 3 files, tests exist |
| L3 | Opus high | New feature inside the existing architecture |
| L4 | Opus xhigh | Crosses modules, unclear edges, concurrency or state |
| L5 | Fable xhigh | Earlier attempt failed, root cause unknown, or high blast radius |

Bump one level for each earlier `builder-*.md` in the step dir with Status blocked, and after a verifier fail on the same step twice. A builder blocked tagged `plan defect:` goes to replan. A verifier fail tagged `plan defect:` goes to replan, or to a criterion swap and a rebuild at the same level when `steps.py swap` accepts the verifier's `swap old:`/`swap new:` proposal. Neither counts toward a bump. A builder block resolved by `steps.py widen` (a conductor scope decision, /chain 4.9) never counts toward a bump either. A recurring finding (a verifier fail or builder block that repeats an earlier attempt's finding on the same step: same criterion, same root cause, after a rebuild or replan addressed it) also goes to a planner L3 replan, like `plan defect:`; it never bumps a level and never counts toward a bump. Most fails are ordinary: the test fires only on a recurrence. L5 failed means stop and ask the user. There is no L6.

### Loose ends step

/chain 5's `Loose ends` step runs the builder at the lowest fitting level (L1 or L2 as a rule) and the verifier per the table below. A fail or block there is reported once and never rebuilt, bumped, or replanned.

The `/fix` fast lane runs builder L1 or L2 (never higher) and verifier L1. A fail gets one rebuild at the same level, with no bump; a second fail hands the item to /chain.

## verifier (L1 to L3)

Follows the newest build level in the step dir: builder L1 or L2 → L1, L3 → L2, L4 or L5 → L3. `run.sh` never lets a verifier run on the build's model family: after a Fable or Sonnet build, a verifier on that family becomes Opus at the same effort.

| Level | Model / effort | Fits when |
|---|---|---|
| L1 | Sonnet medium | Criteria are commands to run |
| L2 | Sonnet high | Judgment on behavior and edge cases |
| L3 | Fable xhigh | Subtle correctness: concurrency, security, data |

## planner (L1 to L3)

| Level | Model / effort | Fits when |
|---|---|---|
| L1 | Sonnet medium | 1 to 3 obvious steps |
| L2 | Opus medium | A normal feature |
| L3 | Fable xhigh | Cross-cutting or risky, or any replan (a builder blocked, or a verifier or `steps.py split` tagged `plan defect:`) |

## researcher (L1 to L3)

| Level | Model / effort | Fits when |
|---|---|---|
| L1 | Sonnet medium | One known source, a single fact |
| L2 | Opus medium | Several sources, some conflicting |
| L3 | Opus high | New territory, and the synthesis drives a decision |

## Single-level roles

| Role | Level | Model / effort |
|---|---|---|
| architect | L1 | Fable high |
| scout | L1 | Haiku low |
| archaeologist | L1 | Sonnet medium |
| filer | L1 | Sonnet medium |

## Agent-tool spawns (outside run.sh)

This section applies to any in-session Agent-tool spawn that has no run.sh role: `general-purpose`, `Explore`, `Plan`, or any spawn that names no agent file. Work that has a run.sh role goes through run.sh, not the Agent tool.

Every such spawn states `model` explicitly. An unset `model` inherits the session's top model. Pick the seat by class of work:

- Mechanical or gather-only work: `haiku`.
- Search, review, and routine coding: `sonnet`, the default.
- Judgment-heavy synthesis: `opus`.

A plain Agent spawn cannot set effort. A `context: fork` or `subagent_type: "fork"` spawn always prices at the parent model, so it is never a step-down.

Evidence: 62 inherited general-purpose builders cost $7.13 each, against $1.82 for an L3 run.sh builder.
